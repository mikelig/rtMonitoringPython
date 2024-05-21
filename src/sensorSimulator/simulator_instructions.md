# Instructions to Start run_sensors.sh Script

This guide provides step-by-step instructions on how to start the run_sensors.sh bash script, which is used to build an image called "sensorSimulator" from a Dockerfile and then start 10 containers based on that image using a docker-compose file.

## Prerequisites

Before proceeding, ensure that you have the following installed:
- docker
- docker-compose

## Steps
1. Download the Script
Download the run_sensors.sh script to your local machine.
2. Make the Script Executable
Open a terminal and navigate to the directory where the run_sensors.sh script is located. Use the following command to make the script executable:

```bash
chmod +x run_sensors.sh
```

3. Start the Script
Once the script is executable, you can start it by running the following command in the terminal. This command will build the "sensorSimulator" image from the Dockerfile and start 10 containers based on that image using the docker-compose file:

```bash
./run_sensors.sh Dockerfile docker-compose.yml
```

4. Stopping the Script
To stop the script and the containers it started, you can terminate the script by pressing Ctrl+C in the terminal. The script is configured to stop the containers gracefully when it exits.