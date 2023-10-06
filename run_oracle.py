import time
import requests
import threading
from oracle_pipeline.src.debezium_config_oracle import oracle_connector, configure_debezium

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

def run_database_oracle_sink():
    import oracle_pipeline.src.debezium_to_database_oracle


def run_api_oracle_sink():
    import oracle_pipeline.src.debezium_to_oracle_api


def start_threads():
    stop_event.clear()
    oracle_db_thread = threading.Thread(target=run_database_oracle_sink)
    oracle_db_thread.start()
    api_oracle_thread = threading.Thread(target=run_api_oracle_sink)
    api_oracle_thread.start()
    
    return oracle_db_thread, api_oracle_thread

def stop_threads(threads):
    stop_event.set()
    for t in threads:
        t.join()  # Wait for the threads to finish



if __name__ == "__main__":

    print("Waiting for 5 minutes before starting...")
    time.sleep(300)

    connections = [
        oracle_connector
        ]

    for connector_name in connections:
        # If the connector isn't already set up, configure it
        if not check_connector_existence(connector_name):
            print(f"Oracle Connector '{connector_name}' not found. Setting it up using Debezium.")
            configure_debezium()
        else:
            print(f"Oracle Connector '{connector_name}' already exists.")

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