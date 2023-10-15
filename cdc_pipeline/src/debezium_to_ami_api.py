from kafka import KafkaConsumer
import requests
import json
import time

class consumer_to_api:

    def __init__(self, kafka_bootstrap_servers, kafka_topic, api_endpoint):
        self.consumer = KafkaConsumer(
            kafka_topic,
            bootstrap_servers=kafka_bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='ami_api'
        )
        self.api_endpoint = api_endpoint
        self.backoff_times = [0, 3, 30, 60, 720, 3600]

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
        return extracted

    def push_to_api(self, message):
        extracted_message = self.extract_message(message)
        #print(f'extracted {extracted_message}')
        for backoff in self.backoff_times:
            try:
                response = requests.post(self.api_endpoint, json=extracted_message, timeout=30)
                response.raise_for_status()
                return True, print('writing to amiSQL api')
            except requests.HTTPError as err:
                print(f"Failed to push message to API due to an HTTP error: {err}. Retrying in {backoff} seconds...")
                print(response.json())
            except requests.RequestException as err:
                print(f"Failed to push message to API due to a general request error: {err}. Retrying in {backoff} seconds...")
            time.sleep(backoff)
        return False

    def consume_and_push(self):
        print('Consumer to AMISQL api up...')
        for message in self.consumer:
            success = self.push_to_api(message.value)
            if not success:
                print(f"Failed to push message {message.value} after all retries")


kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'api.AMI_MSSQL.dbo.CUSTOMER_READS' 
api_endpoint = 'https://meterapi.ylu.agency/api/AMISQL/KafkaSink'

pusher = consumer_to_api(kafka_bootstrap_servers, kafka_topic, api_endpoint)
pusher.consume_and_push()