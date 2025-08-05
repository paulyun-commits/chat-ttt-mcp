# MCP Client - ChatTTT Frontend

Express.js web server providing the game interface for ChatTTT with real-time AI chat integration.

## Features

- **Game Board**: Interactive 3x3 tic-tac-toe grid
- **Chat Interface**: Natural language conversation with AI
- **Auto-Play Mode**: Toggle for automatic AI moves
- **Resource Library**: Access to strategy guides and documentation
- **Service Status**: Live connection monitoring for Ollama and MCP
- **Responsive Design**: Clean, modern UI

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start server:**
   ```bash
   npm start
   # or for development:
   npm run dev
   ```

3. **Access game:**
   - Open http://localhost:3000

## Configuration

The web interface allows configuration of:
- **Ollama Server**: AI model server URL (default: localhost:11434)
- **Model Selection**: Choose from available Ollama models
- **MCP Server**: Game logic server URL (default: localhost:8000)

## File Structure

- `server.js`: Express.js web server
- `public/index.html`: Main game page
- `public/script.js`: Frontend JavaScript logic
- `public/style.css`: Game styling and UI

## Dependencies

- **express**: Web server framework
- **nodemon**: Development auto-reload (dev dependency)

## How It Works

1. User interacts with game board or chat
2. Frontend sends requests to MCP server
3. AI processes natural language via Ollama
4. Game logic executes via MCP tools
5. Results update the UI in real-time
