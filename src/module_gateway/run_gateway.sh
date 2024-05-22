#!/bin/bash

# Function to stop containers
stop_containers() {
    echo "Stopping all containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
}

# Trap exit signal to stop containers
trap stop_containers EXIT

# Check if Dockerfile and docker-compose file are provided as arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <Dockerfile> <docker-compose file>"
    exit 1
fi

DOCKERFILE="$1"
DOCKER_COMPOSE_FILE="$2"

# Step 1: Build the Docker image
echo "Building Docker image..."
docker build -t gatewaysubscriber -f "$DOCKERFILE" .

# Step 2: Start containers using docker-compose
echo "Starting container..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# Wait for a few seconds to ensure containers are up and running
sleep 5

# Infinite loop to keep the script running
# This ensures that the trap is activated when the script is terminated
while true; do
    sleep 1
done
