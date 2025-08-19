# MCP Server - ChatTTT AI Engine

This is the Model Context Protocol (MCP) server for the ChatTTT (Tic-Tac-Toe) game. It provides AI capabilities, game logic, and strategic analysis through MCP tools, prompts, and resources.

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)

## Installation

1. Navigate to the mcp-server directory:
   ```bash
   cd mcp-server
   ```

2. Create a Python virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   **For STDIO mode (MCP standard):**
   ```bash
   pip install -r requirements.txt
   ```

   **For HTTP mode (web interface):**
   ```bash
   pip install -r requirements-http.txt
   ```

## Running the Server

### Option 1: STDIO Mode (Standard MCP)
This is the standard MCP protocol mode for use with MCP-compatible clients:

```bash
python server.py
```

### Option 2: HTTP Mode (Web API)
This mode provides HTTP endpoints for web integration:

```bash
python http_server.py
```

The HTTP server will start on `http://localhost:8000` and provides:
- RESTful API endpoints
- WebSocket support for real-time communication
- Web interface for testing

## MCP Server Capabilities

### Tools
The server provides the following MCP tools:

- **`new_game`**: Start a new Tic-Tac-Toe game
- **`play_move`**: Make a move on the game board
- **`best_move`**: Get the AI's recommended best move
- **`random_move`**: Get a random valid move

### Prompts
Pre-configured prompts for AI assistance:

- **`game_analyzer`**: Analyze current game state and suggest strategies
- **`learning_path`**: Provide learning recommendations based on gameplay
- **`strategy_coach`**: Offer strategic coaching and tips

### Resources
Educational resources available through the MCP protocol:

- **`docs/game-rules.md`**: Complete Tic-Tac-Toe rules
- **`docs/strategy-guide.md`**: Advanced strategy guide
- **`docs/ai-algorithms.md`**: AI algorithms documentation
- **`docs/commands-reference.md`**: Command reference guide

## Project Structure

```
mcp-server/
├── server.py                # Main MCP STDIO server
├── http_server.py           # HTTP/WebSocket server
├── agent.py                 # AI game agent logic
├── mcp_tools.py            # MCP tools implementation
├── config.py               # Configuration settings
├── requirements.txt        # STDIO mode dependencies
├── requirements-http.txt   # HTTP mode dependencies
├── prompts/                # MCP prompts configuration
│   ├── prompts-config.json
│   └── templates/          # Prompt templates
├── resources/              # MCP resources
│   ├── resources-config.json
│   └── docs/              # Documentation files
└── tools/                 # Tool definitions
    ├── new_game.json
    ├── play_move.json
    ├── best_move.json
    └── random_move.json
```

## Configuration

### Environment Variables
- `MCP_SERVER_PORT`: Port for HTTP server (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

### Game Settings
The AI agent can be configured in `config.py`:
- Difficulty levels
- Algorithm preferences
- Logging settings

## API Usage Examples

### HTTP Mode Endpoints

**Start a new game:**
```bash
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "new_game", "arguments": {}}'
```

**Make a move:**
```bash
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "play_move", "arguments": {"position": 0, "player": "X"}}'
```

**Get best move:**
```bash
curl -X POST http://localhost:8000/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "best_move", "arguments": {"board": ["X", "", "", "", "O", "", "", "", ""], "player": "X"}}'
```

### WebSocket Connection
Connect to `ws://localhost:8000/ws` for real-time game updates.

## Development

### Running Tests
```bash
python -m pytest tests/  # If tests are available
```

### Logging
Logs are written to `TicTacToeAgent.log` and stderr. Adjust logging level in `config.py`.

### Adding New Tools
1. Create tool definition in `tools/` directory
2. Implement tool logic in `mcp_tools.py`
3. Register tool in the server initialization

## Troubleshooting

### Import Errors
Make sure you've activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt  # or requirements-http.txt
```

### Port Already in Use
Change the port in HTTP mode:
```bash
MCP_SERVER_PORT=8001 python http_server.py
```

### MCP Client Connection Issues
For STDIO mode, ensure the client is properly configured to communicate via stdin/stdout with the Python process.

## Integration

This MCP server is designed to work with:
- MCP-compatible AI clients (Claude, etc.)
- The companion web frontend in `mcp-client/`
- Any application that supports the MCP protocol

For full integration, use the provided startup scripts in the project root that coordinate both the client and server components.
