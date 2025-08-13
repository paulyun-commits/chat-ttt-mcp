#!/bin/bash

# ChatTTT AI Startup Script

echo "🎮 Starting ChatTTT AI Application..."

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $GAME_PID 2>/dev/null
    kill $MCP_PID 2>/dev/null
    exit 0
}

# Set up trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start the game server
echo "🚀 Starting Game Server on port 8888..."
cd mcp-client
npm start &
GAME_PID=$!
cd ..

# Wait a moment for game server to start
sleep 2

# Check if Python virtual environment exists
if [ ! -d "mcp-server/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd mcp-server
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start the MCP server
echo "🤖 Starting MCP Server on port 8000..."
cd mcp-server
source venv/bin/activate
python server.py &
MCP_PID=$!
cd ..

# Wait a moment for MCP server to start
sleep 3

echo ""
echo "🎉 All servers are running!"
echo ""
echo "🌐 Game Interface: http://localhost:8888"
echo "🤖 MCP Server API: http://localhost:8000"
echo "📊 Server Info: http://localhost:8000/info"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for background processes
wait
