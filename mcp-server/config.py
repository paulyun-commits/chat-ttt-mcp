import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8000))

# Game server configuration
GAME_SERVER_URL = os.getenv("GAME_SERVER_URL", "http://localhost:5000")

# MCP configuration
MCP_SERVER_NAME = "chattt-ai"
MCP_SERVER_VERSION = "1.0.0"
