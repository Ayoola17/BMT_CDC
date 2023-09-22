import requests
import threading
from cdc_pipeline.src.debezium_config import configure_debezium, mssql_connector

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

def run_api_sink():
    import cdc_pipeline.src.debezium_to_api

if __name__ == "__main__":
    connector_name = mssql_connector

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
    api_thread = threading.Thread(target=run_api_sink)
    api_thread.start()
    print('thread started')

    try:
        # Keep the main thread running
        while True:
            db_thread.join(60)  # check every minute if the db_thread is still alive
            api_thread.join(60)  # check every minute if the api_thread is still alive
    except KeyboardInterrupt:
        print("Received keyboard interrupt. Stopping threads...")