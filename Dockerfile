# Start with the Python 3.8.10 image as the base
FROM python:3.8.10

# Set the working directory to /app
WORKDIR /app

# Copy your scripts into the Docker image
COPY ./cdc_pipeline /app/cdc_pipeline

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Set the default command to execute your script
CMD ["python", "run.py"]
