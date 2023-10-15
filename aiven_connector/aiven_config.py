import re
import requests
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    bootstrap_servers='kafka:9092'
)
    

def config(connector_name, topic, api_endpoint):
    print(f'Intiating connection with: {topic} to API endpoint: {api_endpoint} for connector: {connector_name}')

    aiven_config = {
    "name": connector_name,
    "config": {
        "connector.class": "io.aiven.kafka.connect.http.HttpSinkConnector",
        "topics.regex": topic,
        "http.authorization.type": "none",
        "http.url": api_endpoint,
        "batching.enabled": "false",
        #"batch.max.size": 2,
        "tasks.max": "1",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false",
        "group.id": f'group_{connector_name}' 
        }
    }
    


    try:
        response = requests.post("http://debezium-source:8083/connectors", json=aiven_config, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        print(f"Connection successful: {response.json()}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")


def validate_api_endpoint(endpoint):
    url_regex = re.compile(r'https?://\S+')
    return url_regex.match(endpoint) is not None

data_list = list(consumer.topics())

for index, item in enumerate(data_list, start=1):
    print(f'{index}. {item}')

try:
    user_input = int(input("Enter the number of the topic you want to select: "))
    if 0 < user_input <= len(data_list):
        selected_topic = data_list[user_input - 1]
        api_endpoint = input("Enter the API endpoint: ")
        if validate_api_endpoint(api_endpoint):
            connector_name = input("Enter the connector name: ") 
            config(connector_name, selected_topic, api_endpoint)  
        else:
            print("Invalid API endpoint. Please run the script again.")
    else:
        print("Invalid selection. Please run the script again.")
except ValueError:
    print("Invalid input. Please enter a number.")
