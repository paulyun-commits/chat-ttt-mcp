import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))

# Game server configuration
GAME_SERVER_URL = os.getenv("GAME_SERVER_URL", "http://127.0.0.1:3000")

# MCP configuration
MCP_SERVER_NAME = "chattt-ai"
MCP_SERVER_VERSION = "1.0.0"
