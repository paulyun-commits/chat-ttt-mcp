#!/bin/bash

# ChatTTT AI Startup Script - Stdio MCP Version

echo "🎮 Starting ChatTTT AI Application (Stdio MCP)..."

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $GAME_PID 2>/dev/null
    kill $BRIDGE_PID 2>/dev/null
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Check if Python virtual environment exists
if [ ! -d "mcp-server/venv" ]; then
    echo "📦 Setting up Python environment..."
    ./setup-mcp.sh
fi

# Start the MCP bridge server
echo "🌉 Starting MCP Bridge Server on port 8888..."
cd mcp-client
node mcp-bridge.js &
BRIDGE_PID=$!
cd ..

# Wait for bridge to start
sleep 3

# Start the game server
echo "🚀 Starting Game Server on port 8888..."
cd mcp-client
npm start &
GAME_PID=$!
cd ..

echo ""
echo "🎉 ChatTTT is ready!"
echo "📄 HTTP MCP version: http://localhost:8888"
echo "🔌 Stdio MCP version: http://localhost:8888/stdio"
echo "🌉 MCP Bridge: http://localhost:8888"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for any process to exit
wait
