#!/bin/bash

# Script to start the HTTP server for the ChatTTT MCP project

echo "Starting ChatTTT MCP HTTP Server..."

# Change to the mcp-server directory
cd "$(dirname "$0")/mcp-server"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-http.txt

# Start the HTTP server
echo "Starting HTTP server on http://localhost:8000"
python http_server.py
