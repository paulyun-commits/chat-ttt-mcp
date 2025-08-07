# MCP Server - ChatTTT Backend

The Model Context Protocol (MCP) server provides the game logic, AI algorithms, and tool integration for ChatTTT.

## Features

- **Game Logic**: Tic-tac-toe rules, win detection, move validation
- **AI Engine**: Minimax algorithm with perfect play
- **MCP Tools**: Game actions (new_game, best_move, random_move, play_move)
- **MCP Prompts**: Strategy guides and gameplay advice
- **Resources**: Strategy guides and documentation
- **HTTP API**: RESTful endpoints for web integration
- **Logging**: Configurable logging levels and notifications

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # For HTTP server:
   pip install -r requirements-http.txt
   ```

3. **Run MCP server:**
   ```bash
   python server.py
   ```

4. **Run HTTP server (optional):**
   ```bash
   python http_server.py
   ```

## Configuration

Create `.env` file:
```
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434
```

## Available Tools

- `new_game`: Reset board and start fresh
- `best_move`: Get optimal move using minimax
- `random_move`: Get random valid move
- `play_move`: Execute move at position

## Available Prompts

- `strategy_coach`: Get personalized tic-tac-toe strategy coaching based on current game state and skill level
- `game_analyzer`: Analyze a completed or ongoing tic-tac-toe game and provide detailed feedback  
- `learning_path`: Generate a personalized learning path for improving tic-tac-toe skills

## API Endpoints (HTTP Server)

### Standard MCP Endpoints
- `POST /mcp/initialize`: Initialize MCP session
- `GET /mcp/tools/list`: List available tools
- `POST /mcp/tools/call`: Execute MCP tool
- `GET /mcp/resources/list`: List available resources
- `POST /mcp/resources/read`: Read resource content
- `GET /mcp/prompts/list`: List available prompts
- `POST /mcp/prompts/get`: Get prompt content
- `POST /mcp/logging/setLevel`: Set logging level
- `GET /mcp/ping`: Connectivity test
- `GET /mcp/roots/list`: List accessible file system roots

### Notification Endpoints (Stubs)
- `POST /mcp/notifications/tools/list_changed`: Tools list changed
- `POST /mcp/notifications/resources/list_changed`: Resources list changed
- `POST /mcp/notifications/resources/updated`: Resources updated
- `POST /mcp/notifications/prompts/list_changed`: Prompts list changed

### Additional Endpoints
- `GET /info`: Server information, capabilities, and health status

## Files

- `server.py`: Main MCP server
- `http_server.py`: HTTP API wrapper
- `agent.py`: Game logic and AI algorithms
- `mcp_tools.py`: MCP tool definitions
- `config.py`: Server configuration
