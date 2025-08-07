#!/bin/bash

# Test script for ChatTTT AI

echo "🧪 Testing ChatTTT AI Application..."

# Test if game server is running
echo "🎮 Testing Game Server..."
if curl -s http://127.0.0.1:3000/api/game-state > /dev/null; then
    echo "✅ Game Server is responding"
else
    echo "❌ Game Server is not responding on port 3000"
fi

# Test if MCP server is running
echo "🤖 Testing MCP Server..."
if curl -s http://127.0.0.1:8000/info > /dev/null; then
    echo "✅ MCP Server is responding"
    echo "📊 Server Info:"
    curl -s http://127.0.0.1:8000/info | python3 -m json.tool
else
    echo "❌ MCP Server is not responding on port 8000"
fi

echo ""
echo "🎯 Test complete!"
