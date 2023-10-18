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

### Configuring Aiven Connector

The Aiven connector plugin has been seamlessly integrated into the kafka-connectors plugins via the `aiven_config.py` script, simplifying the process of setting up a sink configuration.

#### Adding a New Connection:
1. **Launching Configuration Script**:
   - Attach a shell to the Python app and execute the command: `python3 aiven_connector/aiven_config.py`.

2. **Selecting a Topic**:
   - The script will display a list of available topics, each associated with a unique number.
   - Input the number corresponding to the topic you wish to subscribe to and press `Enter`.

3. **Entering API Endpoint**:
   - You'll then be prompted to input the API endpoint you wish to sink data to.
   - Ensure that the API endpoint is valid before proceeding.

4. **Naming the Connector**:
   - Lastly, you'll be asked to provide a unique connector name.
   - The connector name you provide will also serve as the group ID with a prefixed `Group_`. For instance, if you enter `sink_connector` as the connector name, the group ID will automatically be `Group_sink_connector`.

The `aiven_config.py` script will utilize these three inputs to configure a sink connector to the specified API endpoint, subscribing to the selected topic. This streamlined process ensures a straightforward setup for routing data to your desired sink.


### Deleting an Existing connector
An existing connector can be deleted by utilizing the Kafka Connect REST API through `curl`.

1. **Get list of existing connectors**:
   - Attach a shell to the python app and excute the following command to get the list of all existing connectors `curl http://debezium-source:8083/connectors`.

2. **Delete an existing connector**:
   - After identifying the connector you would like to delete run the following command `curl -X DELETE http://debezium-source:8083/connectors/<connector-name>` make sure you replace `<connector-name>` with the name of the connector you would like to delete.

3. **Checking connector status**:
   - To check the status of an existing connector run the following command `curl http://debezium-source:8083/connectors/<connector-name>/status` make sure you replace the connector-name with the name of the connector you would like to check status.

4. **Enabling and Disabling connector**:
   - To Enable a connector run the following command `curl -X PUT http://debezium-source:8083/connectors/<connector-name>/resume`.
   - To Disable a connector run the following command `curl -X PUT http://debezium-source:8083/connectors/<connector-name>/pause`.
   make sure replace <connector-name> with the connector name you would like to enable and disable.


### Advance configuration of the Aiven connector
There are two methods to manually configure the aiven connector in this program. 

- method 1: you can change the connector configuration manually by setting the connector parameter in the aiven_config.py script
- method 2: you can create a json file to for the json configuration and send a post request withe the json file as payload to the kafaka_connectors endpoint which in this case is http://debezium-source:8083/connectors

The configuration parameter dictionary can be found below:

``http.url``
  The URL to send data to.

  * Type: string
  * Valid Values: HTTP(S) URL
  * Importance: high

``http.authorization.type``
  The HTTP authorization type.

  * Type: string
  * Valid Values: [none, oauth2, static]
  * Importance: high
  * Dependents: ``http.headers.authorization``

``http.headers.authorization``
  The static content of Authorization header. Must be set along with 'static' authorization type.

  * Type: password
  * Default: null
  * Importance: medium

``http.headers.content.type``
  The value of Content-Type that will be send with each request. Must be non-blank.

  * Type: string
  * Default: null
  * Valid Values: Non-blank string
  * Importance: low

``http.headers.additional``
  Additional headers to forward in the http request in the format header:value separated by a comma, headers are case-insensitive and no duplicate headers are allowed.

  * Type: list
  * Default: ""
  * Valid Values: Key value pair string list with format header:value
  * Importance: low

``oauth2.access.token.url``
  The URL to be used for fetching an access token. Client Credentials is the only supported grant type.

  * Type: string
  * Default: null
  * Valid Values: HTTP(S) URL
  * Importance: high
  * Dependents: ``oauth2.client.id``, ``oauth2.client.secret``, ``oauth2.client.authorization.mode``, ``oauth2.client.scope``, ``oauth2.response.token.property``

``oauth2.client.id``
  The client id used for fetching an access token.

  * Type: string
  * Default: null
  * Valid Values: OAuth2 client id
  * Importance: high
  * Dependents: ``oauth2.access.token.url``, ``oauth2.client.secret``, ``oauth2.client.authorization.mode``, ``oauth2.client.scope``, ``oauth2.response.token.property``

``oauth2.client.secret``
  The secret used for fetching an access token.

  * Type: password
  * Default: null
  * Importance: high
  * Dependents: ``oauth2.access.token.url``, ``oauth2.client.id``, ``oauth2.client.authorization.mode``, ``oauth2.client.scope``, ``oauth2.response.token.property``

``oauth2.client.authorization.mode``
  Specifies how to encode ``client_id`` and ``client_secret`` in the OAuth2 authorization request. If set to ``header``, the credentials are encoded as an ``Authorization: Basic <base-64 encoded client_id:client_secret>`` HTTP header. If set to ``url``, then ``client_id`` and ``client_secret`` are sent as URL encoded parameters. Default is ``header``.

  * Type: string
  * Default: HEADER
  * Valid Values: HEADER,URL
  * Importance: medium
  * Dependents: ``oauth2.access.token.url``, ``oauth2.client.id``, ``oauth2.client.secret``, ``oauth2.client.scope``, ``oauth2.response.token.property``

``oauth2.client.scope``
  The scope used for fetching an access token.

  * Type: string
  * Default: null
  * Valid Values: OAuth2 client scope
  * Importance: low
  * Dependents: ``oauth2.access.token.url``, ``oauth2.client.id``, ``oauth2.client.secret``, ``oauth2.client.authorization.mode``, ``oauth2.response.token.property``

``oauth2.response.token.property``
  The name of the JSON property containing the access token returned by the OAuth2 provider. Default value is ``access_token``.

  * Type: string
  * Default: access_token
  * Valid Values: OAuth2 response token
  * Importance: low
  * Dependents: ``oauth2.access.token.url``, ``oauth2.client.id``, ``oauth2.client.secret``, ``oauth2.client.authorization.mode``, ``oauth2.client.scope``

Batching
^^^^^^^^

``batching.enabled``
  Whether to enable batching multiple records in a single HTTP request.

  * Type: boolean
  * Default: false
  * Importance: high

``batch.max.size``
  The maximum size of a record batch to be sent in a single HTTP request.

  * Type: int
  * Default: 500
  * Valid Values: [1,...,1000000]
  * Importance: medium

``batch.prefix``
  Prefix added to record batches. Written once before the first record of a batch. Defaults to "" and may contain escape sequences like ``\n``.

  * Type: string
  * Default: ""
  * Importance: high

``batch.suffix``
  Suffix added to record batches. Written once after the last record of a batch. Defaults to "\n" (for backwards compatibility) and may contain escape sequences.

  * Type: string
  * Default: null
  * Importance: high

``batch.separator``
  Separator for records in a batch. Defaults to "\n" and may contain escape sequences.

  * Type: string
  * Default: null
  * Importance: high

Delivery
^^^^^^^^

``kafka.retry.backoff.ms``
  The retry backoff in milliseconds. This config is used to notify Kafka Connect to retry delivering a message batch or performing recovery in case of transient failures.

  * Type: long
  * Default: null
  * Valid Values: null,[0, 86400000]
  * Importance: medium

``max.retries``
  The maximum number of times to retry on errors when sending a batch before failing the task.

  * Type: int
  * Default: 1
  * Valid Values: [0,...]
  * Importance: medium

``retry.backoff.ms``
  The time in milliseconds to wait following an error before a retry attempt is made.

  * Type: int
  * Default: 3000
  * Valid Values: [0,...]
  * Importance: medium

Timeout
^^^^^^^

``http.timeout``
  HTTP Response timeout (seconds). Default is 30 seconds.

  * Type: int
  * Default: 30
  * Valid Values: [1,...]
  * Importance: low

For more details and examples, you can refer to the official documentation on GitHub: [Aiven HTTP Connector Configuration Options](https://github.com/Aiven-Open/http-connector-for-apache-kafka/blob/main/docs/sink-connector-config-options.rst).