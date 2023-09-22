import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Read he environment variables
mssql_hostname = os.getenv('MSSQL_HOSTNAME')
mssql_port = os.getenv('MSSQL_PORT')
mssql_user = os.getenv('MSSQL_USER')
mssql_password = os.getenv('MSSQL_PASSWORD')


mssql_connector = "mssql_config"

def configure_debezium():
    # Define the Debezium source connector configuration fo mssql
    connector_config = {
        "name": f"{mssql_connector}",
        "config": {
            "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector",
            "database.hostname": f"{mssql_hostname}",
            "database.port": f"{mssql_port}",
            "database.user": f"{mssql_user}",
            "database.password": f"{mssql_password}",
            "database.names": "AMI_MSSQL",
            "topic.prefix": "meter",
            "table.include.list": "dbo.CUSTOMER_READS",
            "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
            "schema.history.internal.kafka.topic": "mssql_database_cdc",
            "database.encrypt": "false",
            "slot.name":"test1",
            "key.converter.schemas.enable":"false",
            "value.converter.schemas.enable":"false",
            "key.converter":"org.apache.kafka.connect.json.JsonConverter",
            "value.converter":"org.apache.kafka.connect.json.JsonConverter",
            "decimal.handling.mode": "string"

        }
    }



    try:
        response = requests.post("http://debezium-source:8083/connectors", json=connector_config, headers={"Content-Type": "application/json"})
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







