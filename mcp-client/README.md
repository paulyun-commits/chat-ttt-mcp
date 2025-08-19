# MCP Client - ChatTTT Game Frontend

This is the web frontend for the ChatTTT (Tic-Tac-Toe) game, built with Express.js and vanilla JavaScript. It provides a web interface for playing the game and can communicate with the MCP server for AI gameplay.

## Prerequisites

- **Node.js** (version 14 or higher)
- **npm** (comes with Node.js)

## Installation

1. Navigate to the mcp-client directory:
   ```bash
   cd mcp-client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Client

### Option 1: Standard Mode (Recommended)
Run the basic game server without MCP integration:

```bash
npm start
```

This will start the server on port 8888 (or the port specified in the PORT environment variable).

### Option 2: Development Mode
For development with auto-restart on file changes:

```bash
npm run dev-mcp-client
```

### Option 3: MCP Bridge Mode
To run with MCP server integration:

```bash
npm run dev-mcp-bridge
```

## Access the Game

Once the server is running, open your web browser and navigate to:

```
http://localhost:8888
```

## Project Structure

```
mcp-client/
├── package.json          # Node.js dependencies and scripts
├── server.js             # Basic Express server
├── server-with-mcp-bridge.js # Express server with MCP integration
├── mcp-bridge.js         # MCP communication bridge
└── public/               # Static web files
    ├── index.html        # Game interface
    ├── script.js         # Game logic and UI
    └── style.css         # Game styling
```

## Configuration

- **Port**: The server runs on port 8888 by default. You can change this by setting the `PORT` environment variable:
  ```bash
  PORT=3000 npm start
  ```

## Features

- **Interactive Tic-Tac-Toe Game**: Play against the computer or another player
- **Web Interface**: Clean, responsive design
- **MCP Integration**: When using the bridge mode, can communicate with the MCP server for AI moves
- **Real-time Updates**: Game state updates in real-time

## Troubleshooting

### Port Already in Use
If you get an error that the port is already in use, either:
- Stop the process using that port
- Use a different port: `PORT=3001 npm start`

### Dependencies Issues
If you encounter dependency issues:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Development

The client is built with:
- **Express.js**: Web server framework
- **HTML/CSS/JavaScript**: Frontend technologies
- **CORS**: For cross-origin requests when needed

For development, use the `dev-mcp-client` script which uses nodemon for automatic restarting when files change.
