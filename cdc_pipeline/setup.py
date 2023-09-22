import os
import subprocess



# Download findspark, boto3, pandas, kafka
subprocess.run(["pip", "install", "pandas", "kafka-python", "pymssql", "requests"])