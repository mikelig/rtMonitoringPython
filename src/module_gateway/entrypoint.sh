#!/bin/bash

# Source environment variables
source /app/.env

# Run the database initialization script
/app/init_db.sh

# Execute the Python application
exec python /app/main.py
