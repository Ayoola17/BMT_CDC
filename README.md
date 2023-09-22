### README - Running the Pipeline with Docker

#### Setting Up and Running the Pipeline

1. **Building Docker Images**:
   - Navigate to the base directory of the project using the terminal.
   - Execute the following command to build the necessary Docker images:
     ```
     docker-compose up
     ```
     Please be patient as building the Docker images might take some time.

2. **Starting the Pipeline**:
   - Once the Docker containers are up and running, attach a shell to the `ubuntu` container.
   - Navigate to the application's working directory within the container:
     ```
     cd /app
     ```
   - Start the pipeline using the command:
     ```
     python3 run.py
     ```

#### Development Notes

The pipeline doesn't automatically start with the `docker-compose up` command due to our current development environment setup. In this phase, the pipeline operates in a development environment. Once development is completed, each individual pipeline module can be transformed into its own service. These services will then be automatically initiated when `docker-compose up` is run.

#### Stopping the Pipeline and Cleaning Up

- To halt the pipeline and shut down all the associated containers, use:
  ```
  docker-compose down
  ```

- If you wish to remove all built Docker images and free up memory
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

**NOTE**: Before running these commands, it's important to note that they will stop all your containers, remove all of them, and delete all your images.
