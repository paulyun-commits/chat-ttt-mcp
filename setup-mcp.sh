#!/bin/bash

# Setup script for MCP Server

echo "🐍 Setting up Python MCP Server..."

cd mcp-server

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "✏️ Please edit .env file if you need to customize settings"
fi

echo "✅ Setup complete!"
echo ""
echo "🚀 You can now run the MCP server with:"
echo "   cd mcp-server"
echo "   source venv/bin/activate"
echo "   python server.py"
echo ""
echo "🎮 Or run everything with the startup script:"
echo "   ./start.sh"
