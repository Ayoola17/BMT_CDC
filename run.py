import time
import requests
import threading
from cdc_pipeline.src.debezium_config import (
    configure_debezium, mssql_connector, 
    postgres_connector, mysql_connector,
    mssql_connector_api, postgres_connector_api,
    mysql_connector_api
)

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


stop_event = threading.Event()

def run_database_sink():
    import cdc_pipeline.src.debezium_to_database

def run_api_ami_sink():
    import cdc_pipeline.src.debezium_to_ami_api

def run_api_postgres_sink():
    import cdc_pipeline.src.debezium_to_pgami_api

def run_api_mysql_sink():
    import cdc_pipeline.src.debezium_to_myami_api

def start_threads():
    stop_event.clear()
    db_thread = threading.Thread(target=run_database_sink)
    db_thread.start()
    api_ami_thread = threading.Thread(target=run_api_ami_sink)
    api_ami_thread.start()
    api_postgres_thread = threading.Thread(target=run_api_postgres_sink)
    api_postgres_thread.start()
    #start api to mysql sink
    api_mysql_thread = threading.Thread(target=run_api_mysql_sink)
    api_mysql_thread.start()
    
    return db_thread, api_ami_thread, api_postgres_thread, api_mysql_thread

def stop_threads(threads):
    stop_event.set()
    for t in threads:
        t.join()  # Wait for the threads to finish

if __name__ == "__main__":

    print("Waiting for 5 minutes before starting...")
    #time.sleep(300)

    connections = [
        mssql_connector, 
        postgres_connector, 
        mysql_connector,
        mssql_connector_api,
        postgres_connector_api,
        mysql_connector_api
        ]

    for connector_name in connections:
        # If the connector isn't already set up, configure it
        if not check_connector_existence(connector_name):
            print(f"Connector '{connector_name}' not found. Setting it up using Debezium.")
            configure_debezium()
        else:
            print(f"Connector '{connector_name}' already exists.")

    try:
        while True:
            print('Starting database and API sink threads...')
            threads = start_threads()
            #time.sleep(900)  # Sleep for 15 minutes
            print('Stopping database and API sink threads...')
            stop_threads(threads)
    except KeyboardInterrupt:
        print("Received keyboard interrupt. Stopping threads...")
        stop_threads(threads)