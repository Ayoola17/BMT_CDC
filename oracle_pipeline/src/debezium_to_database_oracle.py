import os
import json
import requests
import base64
import uuid
import pymssql
from kafka import KafkaConsumer
from datetime import datetime, timedelta

from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Read he environment variables
mssql_hostname = os.getenv('MSSQL_HOSTNAME')
mssql_port = os.getenv('MSSQL_PORT')
mssql_user = os.getenv('MSSQL_USER')
mssql_password = os.getenv('MSSQL_PASSWORD')


mssql_connector = "mssql_config"

def convert_to_datetime(reading_dt, source):
    # Convert nanoseconds to seconds
    if source == 'D':
        seconds = reading_dt / 1e9
        
        # Convert to datetime
        dt = datetime.utcfromtimestamp(seconds)

    
    return dt


def base64_to_uuid(b64_string):
    # Decode the Base64 string to bytes
    bytes_data = base64.b64decode(b64_string)

    # Ensure we have 16 bytes
    if len(bytes_data) != 16:
        raise ValueError("The provided Base64 string does not represent 16 bytes of data.")

    # Convert bytes to UUID
    return str(uuid.UUID(bytes=bytes_data))



class consumer_cdc:
    def __init__(self, bootstrap_servers:str, source_and_topics:dict, refresh_interval=100):
        self.bootstrap_servers = bootstrap_servers
        self.source_and_topics = source_and_topics
        self.topics = list(self.source_and_topics.keys())
        self.refresh_interval = refresh_interval
        self.msg_count = 0
        self.conn = None
        self.init_db_connection()
        

    def init_db_connection(self, auto_commit=True):
        if self.conn:
            self.conn.close()

        try:
            print("Initializing DB connection...") 
            self.conn =  pymssql.connect(
                server=f"{mssql_hostname}:{mssql_port}", 
                user=f"{mssql_user}", 
                password=f"{mssql_password}"
                )
            self.conn.autocommit(auto_commit)
            print("DB connection established!")
            
        except Exception as e:
            print("Error establishing DB connection:", e)

    
    def maybe_refresh_connection(self):
        self.msg_count += 1
        if self.msg_count % self.refresh_interval == 0:
            print("Refreshing DB connection...")
            self.init_db_connection()

    def handle_db_operation(self, op, source, rowid, customerid, locationid, reading, readingddt, meter, readingtype):


        #convert row id to uuid 
        rowid = base64_to_uuid(rowid)

        # initiate cursor AND CONN
        cursor = self.conn.cursor()

        try:
            if op == "c" or op == "r":  # Create/Insert or Read/Snapshot
                # convert datetime
                converted_readingdt = convert_to_datetime(readingddt, source)

                query = """
                    INSERT INTO MeterMaster.[dbo].[READINGS] (SOURCE, ROWID, CUSTOMERID, LOCATIONID, READING, READINGDT, METER, READINGTYPE, STREAMDT)
                    VALUES (%s, %s, %s, %s, CONVERT(decimal(7, 2), %s), %s, %s, %s, GETDATE())
                """
                try:
                    cursor.execute(query, (source, rowid, customerid, locationid, reading, converted_readingdt, meter, readingtype))
                except pymssql._pymssql.IntegrityError as e:
                    if 'Violation of PRIMARY KEY constraint' in str(e):
                        # Log or handle the duplicate key error
                        print(f"Duplicate key error for {rowid}. Skipping...")
                    else:
                        # Raise the error if it's not a duplicate key error
                        raise

            elif op == "u":  # Update
                # convert datetime
                converted_readingdt = convert_to_datetime(readingddt, source)

                query = """
                    UPDATE MeterMaster.[dbo].[READINGS]
                    SET READING = CONVERT(decimal(7, 2), %s), READINGDT = %s, METER = %s, READINGTYPE = %s, STREAMDT = GETDATE()
                    WHERE SOURCE = %s AND ROWID = %s
                """
                cursor.execute(query, (reading, converted_readingdt, meter, readingtype, source, rowid))

            elif op == "d":  # Delete
                query = """
                    DELETE FROM MeterMaster.[dbo].[READINGS]
                    WHERE SOURCE = %s AND ROWID = %s
                """
                cursor.execute(query, (source, rowid))

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally re-raise the exception if needed
            # raise

        finally:
            # Commit the transaction to the database
            self.conn.commit()
            cursor.close()


    def consume_from_debezium(self):
        print('Ready to consume message...')

        self.init_db_connection()
       
        consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='latest',
            value_deserializer=lambda x: x.decode('utf-8') if x else None
        )

        for msg in consumer:
            self.maybe_refresh_connection()
            source = self.source_and_topics[msg.topic]
            message = json.loads(msg.value)
            print(message)
            print('writing to metermaster table..')

            # Check streaming source
            if source == 'D':
                # use mssql schema
                if message["op"] == "d":
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["before"]["ROWNO"] if message["before"] else None,
                        customerid=message["before"]["CUST"] if message["before"] else None,
                        locationid=message["before"]["LOC"] if message["before"] else None,
                        reading=message["before"]["CONSUMPTION"] if message["before"] else None,
                        readingddt=message["before"]["CONSUMDT"] if message["before"] else None,
                        meter=message["before"]["METER"] if message["before"] else None,
                        readingtype=message["before"]["RDRTYPE"] if message["before"] else None
                    )
                else:
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["after"]["ROWNO"] if message["after"] else None,
                        customerid=message["after"]["CUST"] if message["after"] else None,
                        locationid=message["after"]["LOC"] if message["after"] else None,
                        reading=message["after"]["CONSUMPTION"] if message["after"] else None,
                        readingddt=message["after"]["CONSUMDT"] if message["after"] else None,
                        meter=message["after"]["METER"] if message["after"] else None,
                        readingtype=message["after"]["RDRTYPE"] if message["after"] else None
                    )

        if self.conn:
            self.conn.close()

bootstrap_server = "kafka:9094"
source_and_topics = {
    "oracle1.DEBEZIUM.CUSREADS": "D"
    }

consumer = consumer_cdc(bootstrap_server, source_and_topics)
consumer.consume_from_debezium()