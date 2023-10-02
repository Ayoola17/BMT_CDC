import os
import requests




def configure_debezium():
    # Define the Debezium source connector configuration fo mssql
    connector_config = [
    {
    "name": "oracle-connector",
    "config": {
    "connector.class": "io.debezium.connector.oracle.OracleConnector",
    "tasks.max": "1",
    "database.hostname": "oracleami",
    "database.port": "1521",
    "database.user": "c##dbzuser",
    "database.password": "dbz",
    "database.dbname": "ORCLCDB",
    "database.pdb.name": "ORCLPDB1",
    "database.server.name": "oracleami",
    "topic.prefix": "oracle1",
    "slot.name":"slot1",
    "schema.history.internal.kafka.bootstrap.servers" : "kafka:9092", 
    "schema.history.internal.kafka.topic": "schema-changes.cusreads",
    "key.converter.schemas.enable":"false",
    "value.converter.schemas.enable":"false",
    "key.converter":"org.apache.kafka.connect.json.JsonConverter",
    "value.converter":"org.apache.kafka.connect.json.JsonConverter",
    "decimal.handling.mode": "string",
    "datetime.handling.mode": "string",
    "tombstones.on.delete": "false",    
    "group.id": "debezium-oracle-group1",
        }
    }
        

    ]
    for config in connector_config:
        try:
            response = requests.post("http://debezium-source:8083/connectors", json=config, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            print(f"Connection successful: {response.json()}")
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err, response.json()}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")


configure_debezium()
