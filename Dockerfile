# Start with the latest Ubuntu image as the base
FROM ubuntu:latest

# Update and install basic tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    vim \
    git \
    curl \
    wget \
    openjdk-8-jdk \
    # Add other tools you need for your project
    && rm -rf /var/lib/apt/lists/*


# Add user and password 
RUN useradd -m test && echo "test:test" | chpasswd

# Set the working directory to /app
WORKDIR /app

# Copy your scripts into the Docker image
COPY ./cdc_pipeline /app/cdc_pipeline

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

# When the container starts, start a Bash shell
CMD ["python3", "run.py"] 