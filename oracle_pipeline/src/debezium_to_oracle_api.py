from kafka import KafkaConsumer
import requests
import json
import time
import base64
import uuid




class consumer_to_api:

    def __init__(self, kafka_bootstrap_servers, kafka_topic, api_endpoint):
        self.consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.api_endpoint = api_endpoint
        self.backoff_times = [0, 3, 30, 60, 720, 3600]

    def convert_rowno_to_uuid(self, rowno):
        """Convert Base64 encoded rowno to UUID string."""
        # Decode Base64 value
        decoded_bytes = base64.b64decode(rowno)

        # Convert bytes to UUID and return as string
        return str(uuid.UUID(bytes=decoded_bytes))



    def extract_message(self, message):
        """Extract only the needed fields from the Kafka message."""
        extracted = {
            'before': message.get('before', {}),
            'after': message.get('after', {}),
            'source.db': message.get('source', {}).get('db', ''),
            'source.table': message.get('source', {}).get('table', ''),
            'op': message.get('op', ''),
            'ts_ms': message.get('ts_ms', None)
        }

        # Add converted UUIDs if 'after' field exists and contains 'ROWNO'
        if message.get('after') and 'ROWNO' in message['after']:
            extracted['after']['ROWNO'] = self.convert_rowno_to_uuid(message['after']['ROWNO'])
        
        # Add converted UUIDs if 'before' field exists and contains 'ROWNO'
        if message.get('before') and 'ROWNO' in message['before']:
            extracted['before']['ROWNO'] = self.convert_rowno_to_uuid(message['before']['ROWNO'])

        # Convert all keys in 'extracted' to lowercase
        extracted = {k.lower(): v for k, v in extracted.items()}

        # Convert all keys in nested dictionaries to lowercase, if they are not None
        if extracted['before'] is not None:
            extracted['before'] = {k.lower(): v for k, v in extracted['before'].items()}

            # Divide 'consumdt' by 1000000 if it exists in 'before'
            if 'consumdt' in extracted['before']:
                extracted['before']['consumdt'] = int(extracted['before']['consumdt']) / 1000

        if extracted['after'] is not None:
            extracted['after'] = {k.lower(): v for k, v in extracted['after'].items()}

            # Divide 'consumdt' by 1000000 if it exists in 'after'
            if 'consumdt' in extracted['after']:
                extracted['after']['consumdt'] = int(extracted['after']['consumdt'] / 1000)


        return extracted

    def push_to_api(self, message):
        extracted_message = self.extract_message(message)
        print(f'extracted {extracted_message}')
        for backoff in self.backoff_times:
            try:
                response = requests.post(self.api_endpoint, json=extracted_message, timeout=30)
                response.raise_for_status()
                return True, print('writing to oracle api')
            except requests.HTTPError as err:
                print(f"Failed to push message to API due to an HTTP error: {err}. Retrying in {backoff} seconds...")
            except requests.RequestException as err:
                print(f"Failed to push message to API due to a general request error: {err}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
        return False

    def consume_and_push(self):
        print('Consumer to ORACLE api up...')
        for message in self.consumer:
            if message.value["op"] == "d":
                print('Deleted op skipping...')
            else:

                success = self.push_to_api(message.value)
                if not success:
                    print(f"Failed to push message {message.value} after all retries")


kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'oracle1.DEBEZIUM.CUSREADS' 
api_endpoint = 'https://meterapi.ylu.agency/api/OracleAMI/KafkaSink'

pusher = consumer_to_api(kafka_bootstrap_servers, kafka_topic, api_endpoint)
pusher.consume_and_push()