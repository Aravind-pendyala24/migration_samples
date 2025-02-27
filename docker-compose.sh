#!/bin/bash

# Start the Ubuntu container
docker-compose up -d

# Execute into the container
echo "Starting bash shell in the Ubuntu container..."
docker exec -it ubuntu-container bash

# Note: When you exit the bash shell, the container will still be running
# To stop the container, run: docker-compose down
