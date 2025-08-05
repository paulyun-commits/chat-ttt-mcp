# ChatTTT - AI-Powered Tic-Tac-Toe

A sophisticated tic-tac-toe game powered by AI with natural language conversation capabilities. ChatTTT combines a minimax algorithm for perfect gameplay with large language models for conversational interaction via the Model Context Protocol (MCP).

## Features

- 🤖 **Perfect AI**: Minimax algorithm for optimal gameplay
- 💬 **Natural Language**: Chat with AI in plain English
- 🎮 **Web Interface**: Play via web browser with real-time chat
- 📚 **Strategy Resources**: Built-in guides and tutorials
- 🔄 **Auto-Play Mode**: Watch AI vs AI gameplay
- 🎲 **Random Mode**: Educational variety in AI moves

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd chat-ttt-mcp
   chmod +x *.sh
   ./setup-mcp.sh
   ```

2. **Start the application:**
   ```bash
   ./start.sh
   ```

3. **Open your browser:**
   - Game: http://localhost:3000
   - MCP Server: http://localhost:8000

## Prerequisites

- **Node.js** (v14+)
- **Python 3.8+**
- **Ollama** (for AI conversation features)

### Ollama Setup

Install Ollama and pull a model:
```bash
# Install Ollama (see https://ollama.ai)
ollama pull llama3.2:3b  # or your preferred model
ollama serve              # starts on localhost:11434
```

## Architecture

- **mcp-client/**: Express.js web server and game interface
- **mcp-server/**: Python MCP server with game logic and AI

## Configuration

Configure AI model in the web interface or set environment variables in `mcp-server/.env`:
```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

## Alternative Startup Methods

### Individual Services

Start game server only:
```bash
cd mcp-client && npm start
```

Start MCP server only:
```bash
cd mcp-server && source venv/bin/activate && python server.py
```

Start HTTP server for web API:
```bash
./start-http.sh
```

### VS Code Tasks

Use the configured VS Code tasks for development:
- `Start Game Server`
- `Start MCP Server` 
- `Start HTTP Server`

## How to Play

1. **Make moves**: Click cells or type position numbers (1-9)
2. **Natural language**: "I'll take the center" or "top left corner"
3. **Get help**: Ask "What's the best move?" or "Show me strategy"
4. **New game**: Say "restart" or "new game"
5. **Auto-play**: Toggle to watch AI gameplay

## License

MIT License
