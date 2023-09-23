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

def convert_to_datetime(reading_dt):
    # Convert nanoseconds to seconds
    seconds = reading_dt / 1e9

    # Convert to datetime
    dt = datetime.utcfromtimestamp(seconds)
    return dt


class consumer_cdc:
    def __init__(self, bootstrap_servers:str, source_and_topics:dict):
        self.bootstrap_servers = bootstrap_servers
        self.source_and_topics = source_and_topics
        self.topics = list(self.source_and_topics.keys())
        

    def init_db_connection(self):

        try:
            print("Initializing DB connection...") 
            conn =  pymssql.connect(
                server=f"{mssql_hostname}:{mssql_port}", 
                user=f"{mssql_user}", 
                password=f"{mssql_password}"
                )
            print("DB connection established!")
            return conn
        except Exception as e:
            print("Error establishing DB connection:", e)
            return None
            

    def handle_db_operation(self, op, source, rowid, customerid, locationid, reading, readingddt, meter, readingtype):

        # intiate cursor AND CONN
        self.conn = self.init_db_connection()
        self.cursor = self.conn.cursor()

        #convert datetime
        converted_readingdt = convert_to_datetime(readingddt)
        
        
        if op == "c":  # Create/Insert
            query = """
                INSERT INTO MeterMaster.[dbo].[READINGS] (SOURCE, ROWID, CUSTOMERID, LOCATIONID, READING, READINGDT, METER, READINGTYPE, STREAMDT)
                VALUES (%s, %s, %s, %s, CONVERT(decimal(7, 2), %s), %s, %s, %s, GETDATE())
            """
            self.cursor.execute(query, (source, rowid, customerid, locationid, reading, converted_readingdt, meter, readingtype))

        
        elif op == "u":  # Update
            query = """
                UPDATE MeterMaster.[dbo].[READINGS]
                SET READING = CONVERT(decimal(7, 2), %s), READINGDT = %s, METER = %s, READINGTYPE = %s, STREAMDT = GETDATE()
                WHERE SOURCE = %s AND ROWID = %s
            """
            self.cursor.execute(query, (reading, converted_readingdt, meter, readingtype, source, rowid))

        elif op == "d":  # Delete
            query = """
                DELETE FROM MeterMaster.[dbo].[READINGS]
                WHERE SOURCE = %s AND ROWID = %s
            """
            self.cursor.execute(query, (source, rowid))
        
        # Commit the transaction to the database
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


    def consume_from_debezium(self):
        print('Ready to consume message...')
       
        consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='latest',
            value_deserializer=lambda x: x.decode('utf-8')
        )

        for msg in consumer:
            message = json.loads(msg.value)
            print('writing to metermaster table..')

            self.handle_db_operation(
                op=message["op"],
                source=self.source_and_topics[msg.topic],
                rowid=message["after"]["READINGID"] if message["after"] else None,
                customerid=message["after"]["CUSTOMERID"] if message["after"] else None,
                locationid=message["after"]["LOCATIONID"] if message["after"] else None,
                reading=message["after"]["READING"] if message["after"] else None,
                readingddt=message["after"]["READING_DT"] if message["after"] else None,
                meter=message["after"]["METERID"] if message["after"] else None,
                readingtype=message["after"]["READING_TYPE"] if message["after"] else None
            )



consumer = consumer_cdc("kafka:9092", {"meter.AMI_MSSQL.dbo.CUSTOMER_READS": "A"})
consumer.consume_from_debezium()