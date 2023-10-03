import os
import requests
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Read the environment variables
# Mssql server
mssql_hostname = os.getenv('MSSQL_HOSTNAME')
mssql_port = os.getenv('MSSQL_PORT')
mssql_user = os.getenv('MSSQL_USER')
mssql_password = os.getenv('MSSQL_PASSWORD')
mssql_connector = "mssql_config"
mssql_connector_api = "mssql_config_api"

# Mysql server
mysql_hostname = os.getenv('MYSQL_HOSTNAME')
mysql_user = os.getenv('MYSQL_USER')
mysql_port = os.getenv('MYSQL_PORT')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_connector = "mysql_config"
mysql_connector_api = "mysql_config_api"

# Postgres server
postgres_hostname = os.getenv('POSTGRES_HOST')
postgres_port = os.getenv('POSTGRES_PORT')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_connector = "postgres_config"
postgres_connector_api = "postgres_config_api"



def configure_debezium():
    # Define the Debezium source connector configuration fo mssql
    connector_config = [
        {
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
            "decimal.handling.mode": "string",
            "datetime.handling.mode": "string",
            "tombstones.on.delete": "false",
            "group.id": "debezium-mssql-group"
            }              
        },
        
        {
        "name" : postgres_connector,
        "config" : {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": postgres_hostname,
            "database.port": postgres_port,
            "database.user": postgres_user,
            "database.password": postgres_password,
            "database.dbname" : "Pgami_db",
            "database.server.name" : "pgAMI",
            "slot.name":"test_slot_1",
            "plugin.name" :"pgoutput",
            "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
            "schema.history.internal.kafka.topic": "postgres_database_cdc",
            "key.converter.schemas.enable":"false",
            "value.converter.schemas.enable":"false",
            "key.converter":"org.apache.kafka.connect.json.JsonConverter",
            "value.converter":"org.apache.kafka.connect.json.JsonConverter",
            "table.include.list":"public.MREADS",
            "topic.prefix": "postgres5",
            "decimal.handling.mode": "string",
            "datetime.handling.mode": "string",
            "tombstones.on.delete": "false",
            "group.id": "debezium-postgres-group"
            }
        },
        {
            "name": mysql_connector,
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "database.hostname": mysql_hostname,
                "database.port": mysql_port,
                "database.user": "root",
                "database.password": "rootpassword",
                "database.server.id": "1",
                "topic.prefix": "mysql",
                "database.include.list": "Myami_db",
                "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
                "schema.history.internal.kafka.topic": "mysql_database_cdc",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "decimal.handling.mode": "string",
                "datetime.handling.mode": "string",
                "tombstones.on.delete": "false",
                "group.id": "debezium-mysql-group",
                "key.converter.schemas.enable": "false",
                "value.converter.schemas.enable": "false",
                "time.precision.mode": "connect",
                "datetime.precision.mode": "adaptive_time_microseconds"

            }
        },
         {
        "name": f"{mssql_connector_api}",
        "config": {
            "connector.class": "io.debezium.connector.sqlserver.SqlServerConnector",
            "database.hostname": f"{mssql_hostname}",
            "database.port": f"{mssql_port}",
            "database.user": f"{mssql_user}",
            "database.password": f"{mssql_password}",
            "database.names": "AMI_MSSQL",
            "topic.prefix": "api",
            "table.include.list": "dbo.CUSTOMER_READS",
            "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
            "schema.history.internal.kafka.topic": "mssql_database_cdc",
            "database.encrypt": "false",
            "slot.name":"test1",
            "key.converter.schemas.enable":"false",
            "value.converter.schemas.enable":"false",
            "key.converter":"org.apache.kafka.connect.json.JsonConverter",
            "value.converter":"org.apache.kafka.connect.json.JsonConverter",
            "decimal.handling.mode": "string",
            "datetime.handling.mode": "string",
            "tombstones.on.delete": "false",
            "group.id": "debezium-mssql-group"
            }              
        },
        
        {
        "name" : postgres_connector_api,
        "config" : {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "database.hostname": postgres_hostname,
            "database.port": postgres_port,
            "database.user": postgres_user,
            "database.password": postgres_password,
            "database.dbname" : "Pgami_db",
            "database.server.name" : "pgAMI",
            "slot.name":"test_slot_1",
            "plugin.name" :"pgoutput",
            "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
            "schema.history.internal.kafka.topic": "postgres_database_cdc",
            "key.converter.schemas.enable":"false",
            "value.converter.schemas.enable":"false",
            "key.converter":"org.apache.kafka.connect.json.JsonConverter",
            "value.converter":"org.apache.kafka.connect.json.JsonConverter",
            "table.include.list":"public.MREADS",
            "topic.prefix": "postgres5_api",
            "decimal.handling.mode": "string",
            "datetime.handling.mode": "string",
            "tombstones.on.delete": "false",
            "group.id": "debezium-postgres-group"
            }
        },
        {
            "name": mysql_connector_api,
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "database.hostname": mysql_hostname,
                "database.port": mysql_port,
                "database.user": "root",
                "database.password": "rootpassword",
                "database.server.id": "1",
                "topic.prefix": "mysql_api",
                "database.include.list": "Myami_db",
                "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
                "schema.history.internal.kafka.topic": "mysql_database_cdc",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "decimal.handling.mode": "string",
                "datetime.handling.mode": "string",
                "tombstones.on.delete": "false",
                "group.id": "debezium-mysql-group",
                "key.converter.schemas.enable": "false",
                "value.converter.schemas.enable": "false",
                "time.precision.mode": "connect",
                "datetime.precision.mode": "adaptive_time_microseconds"

            }
        }

    ]
    for config in connector_config:
        try:
            response = requests.post("http://debezium-source:8083/connectors", json=config, headers={"Content-Type": "application/json"})
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


