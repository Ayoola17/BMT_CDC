## Introduction

Our solution leverages Debezium, an open-source CDC (Change Data Capture) tool, to efficiently stream data from various database sources, namely MSSQL, Oracle, MySQL, and PostgreSQL. This streamed data is channeled into a consolidated "Meter Master" table in an MSSQL server, as well as being dispatched to specific API endpoints for each database.

Debezium, in essence, acts as a bridge capturing row-level changes in the databases and producing events to Kafka. Subsequent consumers then process these events, ensuring they are appropriately directed to their designated sinks, whether that be the Meter Master table or one of the individual API endpoints.

The architecture can be visualized as follows:

```
 +------------+     +---------+     +----------+     +-----------------------+         +----------------------------+
 |  Database  |---->|Debezium |---->|  Kafka   |---->| Kafka Consumer        |   --->  |  Meter master Table        |
 +------------+     +---------+     +----------+     +-----------------------+         +----------------------------+
                                                                  |
                                                                  V
                                                           +-------------+
                                                           | API Endpoint|
                                                           +-------------+
```

In this representation:
- **Database**: Represents the origin databases (MSSQL, Oracle, MySQL, PostgreSQL) where changes are captured.
- **Debezium**: Captures row-level changes and produces them as events.
- **Kafka**: Receives these events and manages them for consumption.
- **Kafka Consumer**: Consumes the events from Kafka and updates the "Meter Master" table in MSSQL.
- **Meter master Table**: Unified database to capture changes from multiple source
- **API Endpoint**: The various endpoints, each specific to a database, consuming and presenting the changes.

Through this pipeline, real-time data syncing is achieved with minimized latency, ensuring up-to-date reflections across both the Meter Master table and the API endpoints.



### Running the Pipeline with Docker

#### Initial Setup and Invocation

1. **Docker Initialization**:
   - Start by navigating to the project's root directory in your terminal.
   - To initialize the Docker environment, run:
     ```
     docker-compose up
     ```
     This command initiates the Docker containers, including the databases, Kafka, Debezium, and other dependencies. Given the complexity of our setup, there's an intentional 5-minute waiting period post initialization. This ensures all dependent services, especially the databases, Kafka, and Debezium, are fully operational before the pipeline kicks off. 

2. **Manual Activation**:
The pipeline can also be triggered manually by doing the following.

   - Once you're sure the Docker containers are fully initialized, access the primary container's shell:
     ```
     docker exec -it [CONTAINER_ID] /bin/bash
     ```
     Replace `[CONTAINER_ID]` with the appropriate identifier for the main container.
   - Direct yourself to the application's primary directory within the container:
     ```
     cd /app
     ```
   - Activate the pipeline by running:
     ```
     python3 run.py
     ```

The pipeline is now in motion! It will dynamically track changes from the source databases and channel them to the Meter Master table and the distinct API endpoints.
 
 
 
#### Development Notes

The pipeline is now configured to automatically initiate upon executing the `docker-compose up` command. To enhance robustness and account for potential delays or lags, each pipeline module has been designed to consume from its individual topic. This approach ensures that if one database experiences latency or fails to consume a message immediately upon its production, it doesn't cause inconsistencies or incomplete data in the sink. This decoupling mechanism serves to optimize the reliability and consistency of the data flow across the system.

#### Stopping the Pipeline and Cleaning Up

- To halt the pipeline and shut down all the associated containers, use:
  ```
  docker-compose down
  ```



To delete all Docker images and clear memory associated with them, you can use the following commands:

1. **Stop all running containers**:
   ```bash
   docker stop $(docker ps -a -q)
   ```

2. **Remove all containers**:
   ```bash
   docker rm $(docker ps -a -q)
   ```

3. **Delete all images**:
   ```bash
   docker rmi $(docker images -q)
   ```

4. **Clean up unused Docker objects** (like volumes, networks, etc.):
   ```bash
   docker system prune -a
   ```

5. **Optional: Clear Docker cache**:
   ```bash
   docker builder prune -a
   ```

<<<<<<< HEAD


=======
>>>>>>> ed14607 (Update README.md)
If you want to delete the volumes of Docker containers, especially where databases were created on your local machine, you can use the following steps:

1. **List all volumes**:
   Before deleting, you might want to list all the volumes to identify which ones to delete:
   
   ```bash
   docker volume ls
   ```

2. **Remove a specific volume**:
   If you know the name of the volume you wish to remove:
   
   ```bash
   docker volume rm VOLUME_NAME
   ```

3. **Remove dangling volumes**:
   Dangling volumes are volumes that are no longer associated with a container. To remove them:
   
   ```bash
   docker volume prune
   ```

   This command will ask for confirmation before deleting.

4. **Remove all volumes**:
   If you want to delete all volumes (use with caution as this is irreversible):
   
   ```bash
   docker volume rm $(docker volume ls -q)
   ```

   This command will list all volumes with `docker volume ls -q` and pass them to `docker volume rm` to remove them.

5. **Delete volumes when removing containers**:
   When you're removing a container and want to also remove its associated volumes, you can use:
   
   ```bash
   docker rm -v CONTAINER_NAME_OR_ID
   ```

   This `-v` flag will remove the volume associated with the container.

Please be cautious when deleting volumes, especially if they contain databases. Once a volume is removed, the data within it is lost and cannot be recovered unless you have backups. Always ensure you have a backup of your data before performing any deletions.

**NOTE**: Before running these commands, it's important to note that they will stop all your containers, remove all of them, and delete all your images.
dir