import os
import json
import requests
import pymssql
from kafka import KafkaConsumer
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Read he environment variables
mssql_hostname = os.getenv('MSSQL_HOSTNAME')
mssql_port = os.getenv('MSSQL_PORT')
mssql_user = os.getenv('MSSQL_USER')
mssql_password = os.getenv('MSSQL_PASSWORD')

def convert_to_datetime(reading_dt):
    # Convert from 100-nanosecond intervals since January 1, 1601 to seconds since epoch (January 1, 1970)
    epoch_as_filetime = 116444736000000000
    microseconds = (reading_dt - epoch_as_filetime) // 10
    timestamp = datetime(1970, 1, 1) + timedelta(microseconds=microseconds)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


class consumer_cdc:
    def __init__(self, bootstrap_servers:str, source_and_topics:dict):
        self.bootstrap_servers = bootstrap_servers
        self.source_and_topics = source_and_topics
        self.topics = list(self.source_and_topics.keys())
        self.conn = self.init_db_connection()

    def init_db_connection(self):

        try:
            print("Initializing DB connection...") 
            conn =  pymssql.connect(
                server=f"{mssql_hostname}:{mssql_port}", 
                user=f"{mssql_user}", 
                password=f"{mssql_password}"
                )
            self.cursor = conn.cursor()
            print("DB connection established!")
            return conn
        except Exception as e:
            print("Error establishing DB connection:", e)
            return None
            


    
    def insert_to_db(self, source, rowid, customerid, locationid, reading, readingddt, meter, readingtype):

        #convert time to datetime
        readingddt_converted = convert_to_datetime(readingddt)

        query = """
            INSERT INTO MeterMaster.[dbo].[READINGS] (SOURCE, ROWID, CUSTOMERID, LOCATIONID, READING, READINGDT, METER, READINGTYPE, STREAMDT)
            VALUES (%s, %s, %s, %s, CONVERT(decimal(7, 2), %s), %s, %s, %s, GETDATE())
        """
               
        self.cursor.execute(query, (source, rowid, customerid, locationid, reading, readingddt_converted, meter, readingtype))
        self.conn.commit()


    def consume_from_debezium(self):
        print('comsuming')
       
        consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='latest',
            value_deserializer=lambda x: x.decode('utf-8')
        )

        for msg in consumer:
            print(f"{self.source_and_topics[msg.topic]} {msg.value}")

            message = json.loads(msg.value)
            print('loading to sink')

            self.insert_to_db(
                source=self.source_and_topics[msg.topic],
                rowid=message["READINGID"],
                customerid=message["CUSTOMERID"],
                locationid=message["LOCATIONID"],
                reading=message["READING"],
                readingddt=message["READING_DT"],
                meter=message["METERID"],
                readingtype=message["READING_TYPE"]
            )

consumer = consumer_cdc("kafka:9092", {"meter.AMI_MSSQL.dbo.CUSTOMER_READS": "A"})
consumer.consume_from_debezium()