import os
import json
import requests
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
    if source == 'A':
        seconds = reading_dt / 1e9
        
        # Convert to datetime
        dt = datetime.utcfromtimestamp(seconds)

    elif  source == 'C':
        seconds = reading_dt / 1000000
        
        # Convert to datetime
        dt = datetime.utcfromtimestamp(seconds)
    
    else:
        timestamp_seconds = reading_dt / 1000  # Convert to seconds

        dt = datetime.utcfromtimestamp(timestamp_seconds)
    
    return dt



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
            if source == 'A':
                # use mssql schema
                if message["op"] == "d":
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["before"]["READINGID"] if message["before"] else None,
                        customerid=message["before"]["CUSTOMERID"] if message["before"] else None,
                        locationid=message["before"]["LOCATIONID"] if message["before"] else None,
                        reading=message["before"]["READING"] if message["before"] else None,
                        readingddt=message["before"]["READING_DT"] if message["before"] else None,
                        meter=message["before"]["METERID"] if message["before"] else None,
                        readingtype=message["before"]["READING_TYPE"] if message["before"] else None
                    )
                else:
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["after"]["READINGID"] if message["after"] else None,
                        customerid=message["after"]["CUSTOMERID"] if message["after"] else None,
                        locationid=message["after"]["LOCATIONID"] if message["after"] else None,
                        reading=message["after"]["READING"] if message["after"] else None,
                        readingddt=message["after"]["READING_DT"] if message["after"] else None,
                        meter=message["after"]["METERID"] if message["after"] else None,
                        readingtype=message["after"]["READING_TYPE"] if message["after"] else None
                    )

            elif source == 'B':
                # use mysql schema
                if message["op"] == "d":
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["before"]["READID"] if message["before"] else None,
                        customerid=message["before"]["CUSTID"] if message["before"] else None,
                        locationid=message["before"]["LOCID"] if message["before"] else None,
                        reading=message["before"]["CNSUM"] if message["before"] else None,
                        readingddt=message["before"]["CNSDT"] if message["before"] else None,
                        meter=message["before"]["METID"] if message["before"] else None,
                        readingtype=message["before"]["CNTYP"] if message["before"] else None
                    )
                else:
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["after"]["READID"] if message["after"] else None,
                        customerid=message["after"]["CUSTID"] if message["after"] else None,
                        locationid=message["after"]["LOCID"] if message["after"] else None,
                        reading=message["after"]["CNSUM"] if message["after"] else None,
                        readingddt=message["after"]["CNSDT"] if message["after"] else None,
                        meter=message["after"]["METID"] if message["after"] else None,
                        readingtype=message["after"]["CNTYP"] if message["after"] else None
                    )
            

            elif source == 'C':
                #use postgres schema
                if message["op"] == "d":
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["before"]["rid"] if message["before"] else None,
                        customerid=message["before"]["cust"] if message["before"] else None,
                        locationid=message["before"]["loc"] if message["before"] else None,
                        reading=message["before"]["cosum"] if message["before"] else None,
                        readingddt=message["before"]["cosdt"] if message["before"] else None,
                        meter=message["before"]["meter"] if message["before"] else None,
                        readingtype=message["before"]["costy"] if message["before"] else None
                    )
                else:
                    self.handle_db_operation(
                        op=message["op"],
                        source=source,
                        rowid=message["after"]["rid"] if message["after"] else None,
                        customerid=message["after"]["cust"] if message["after"] else None,
                        locationid=message["after"]["loc"] if message["after"] else None,
                        reading=message["after"]["cosum"] if message["after"] else None,
                        readingddt=message["after"]["cosdt"] if message["after"] else None,
                        meter=message["after"]["meter"] if message["after"] else None,
                        readingtype=message["after"]["costy"] if message["after"] else None
                    )

        if self.conn:
            self.conn.close()

bootstrap_server = "kafka:9092"
source_and_topics = {
    "meter.AMI_MSSQL.dbo.CUSTOMER_READS": "A",
    "mysql.MyAMIdb.READINGS" :"B",
    "postgres5.public.mreads": "C"
    }

consumer = consumer_cdc(bootstrap_server, source_and_topics)
consumer.consume_from_debezium()