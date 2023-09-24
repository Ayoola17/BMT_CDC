import requests
import threading
from cdc_pipeline.src.debezium_config import configure_debezium, mssql_connector, postgres_connector, mysql_connector

def check_connector_existence(connector_name):
    """
    Determines if the given connector name is already registered with Debezium.
    """
    try:
        response = requests.get('http://debezium-source:8083/connectors')
        connectors = response.json()
        return connector_name in connectors

    except requests.RequestException as e:
        return False
    
def run_database_sink():
    import cdc_pipeline.src.debezium_to_database

def run_api_ami_sink():
    import cdc_pipeline.src.debezium_to_ami_api

def run_api_postgres_sink():
    import cdc_pipeline.src.debezium_to_pgami_api

def run_api_mysql_sink():
    import cdc_pipeline.src.debezium_to_myami_api

if __name__ == "__main__":
    connections = [mssql_connector, postgres_connector, mysql_connector]

    for connector_name in connections:

        # If the connector isn't already set up, configure it
        if not check_connector_existence(connector_name):
            print(f"Connector '{connector_name}' not found. Setting it up using Debezium.")
            configure_debezium()
        else:
            print(f"Connector '{connector_name}' already exists.")

    print('Starting database and API sink threads...')
    # Start the database sink in its own thread
    db_thread = threading.Thread(target=run_database_sink)
    db_thread.start()
    
    # Start the API sink in its own thread
    api_ami_thread = threading.Thread(target=run_api_ami_sink)
    api_ami_thread.start()

    # Start api to pgami sink
    api_postgres_thread = threading.Thread(target=run_api_postgres_sink)
    api_postgres_thread.start()

    #start api to mysql sink
    api_mysql_thread = threading.Thread(target=run_api_mysql_sink)
    api_mysql_thread.start()


    print('thread started')

    try:
        # Keep the main thread running
        while True:
            db_thread.join(60)  # check every minute if the db_thread is still alive
            api_ami_thread.join(60)  # check every minute if the api_thread is still alive
            api_postgres_thread.join(60)
            api_mysql_thread.join(60)
    except KeyboardInterrupt:
        print("Received keyboard interrupt. Stopping threads...")