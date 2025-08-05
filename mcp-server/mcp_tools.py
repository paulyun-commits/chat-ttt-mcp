from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent, CallToolResult, Resource
from agent import TicTacToeAgent

class MCPTools:
    def __init__(self):
        self.agent = TicTacToeAgent()
    
    def get_tools(self) -> List[Tool]:
        """Return list of available MCP tools."""
        return [
            Tool(
                name="new_game",
                description="Clear the board and start a new game.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="best_move",
                description="Get the best move for a given board state",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {
                            "type": "array",
                            "items": {
                                "type": ["string", "null"]
                            },
                            "minItems": 9,
                            "maxItems": 9,
                            "description": "Array representing the board state"
                        },
                        "player": {
                            "type": "string",
                            "description": "Player to get move for (X or O)",
                            "enum": ["X", "O"]
                        },
                        "game_over": {
                            "type": "boolean",
                            "description": "Whether the game has ended",
                            "default": False
                        },
                        "winner": {
                            "type": ["string", "null"],
                            "description": "The winner of the game (X, O, or null for tie/ongoing)",
                            "enum": ["X", "O", None]
                        }
                    },
                    "required": ["board", "player"]
                }
            ),
            Tool(
                name="random_move",
                description="Get a random move",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {
                            "type": "array",
                            "items": {
                                "type": ["string", "null"]
                            },
                            "minItems": 9,
                            "maxItems": 9,
                            "description": "Array representing the board state"
                        },
                        "player": {
                            "type": "string",
                            "description": "Player to get move for (X or O)",
                            "enum": ["X", "O"]
                        },
                        "game_over": {
                            "type": "boolean",
                            "description": "Whether the game has ended",
                            "default": False
                        },
                        "winner": {
                            "type": ["string", "null"],
                            "description": "The winner of the game (X, O, or null for tie/ongoing)",
                            "enum": ["X", "O", None]
                        }
                    },
                    "required": ["board", "player"]
                }
            ),
            Tool(
                name="play_move",
                description="Play the move at the specified position",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "board": {
                            "type": "array",
                            "items": {
                                "type": ["string", "null"]
                            },
                            "minItems": 9,
                            "maxItems": 9,
                            "description": "Array representing the board state"
                        },
                        "position": {
                            "type": "integer",
                            "description": "Position to make the move (1-9)",
                            "minimum": 1,
                            "maximum": 9
                        },
                        "player": {
                            "type": "string",
                            "description": "Player making the move (X or O)",
                            "enum": ["X", "O"]
                        }
                    },
                    "required": ["board", "position", "player"]
                }
            ),
        ]
    
    def get_resources(self) -> List[Resource]:
        """Return list of available MCP resources."""
        return [
            Resource(
                uri="chatttp://game-rules",
                name="ChatTTT Game Rules",
                description="Complete rules and gameplay mechanics for ChatTTT, including how to play, winning conditions, interface features, and available commands",
                mimeType="text/plain"
            ),
            Resource(
                uri="chatttp://strategy-guide",
                name="ChatTTT Strategy Guide",
                description="Advanced strategies for optimal play, including opening moves, defensive tactics, endgame scenarios, and AI learning tips",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://ai-algorithms",
                name="AI Architecture and Algorithms",
                description="Technical details about ChatTTT's hybrid AI system, including minimax algorithm, language model integration, and MCP implementation",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://commands-reference",
                name="Natural Language Interface Guide",
                description="Comprehensive guide to interacting with ChatTTT using natural conversation, including examples, features, and troubleshooting",
                mimeType="text/plain"
            )
        ]
    
    async def get_resource_content(self, uri: str):
        """Get the content of a specific resource."""
        try:
            if uri == "chatttp://game-rules":
                return """# ChatTTT Game Rules

## Objective
Be the first player to get three of your marks (X or O) in a row, column, or diagonal.

## How to Play
1. The game is played on a 3x3 grid numbered 1-9:
```
1 2 3 
4 5 6 
7 8 9 
```

2. Players take turns placing their marks (X for human, O for AI).
3. You can make moves by:
   - Clicking on an empty cell in the web interface
   - Typing a position number (1-9) in the chat
   - Using natural language like "I'll take position 5" or "top left corner"

## Available Commands
- **Position numbers (1-9)**: Make a move at that position
- **Natural language moves**: "I'll play the center", "top right corner", etc.
- **"new game"** or **"restart"**: Start a new game (asks for confirmation if game in progress)
- **"random"** or **"surprise me"**: Get a random move suggestion
- **"best"** or **"what's the optimal play?"**: Get the best move suggestion from the AI
- **"help"**: Access game resources and strategy guides

## Game Features
- **Auto-Play Mode**: Toggle to let the AI play automatically when it's their turn
- **Chat Interface**: Natural conversation with the AI about strategy and gameplay
- **Resource Library**: Access to strategy guides, AI algorithm explanations, and command references
- **Real-time Status**: Live connection status for both Ollama and MCP services

## Winning Conditions
- Three marks in a row (horizontal, vertical, or diagonal)
- If all 9 positions are filled without a winner, it's a tie

## AI Features
- Uses minimax algorithm with perfect play capability
- Provides move suggestions and strategic analysis
- Can explain reasoning behind moves
- Supports both optimal and random play styles
"""
                
            elif uri == "chatttp://strategy-guide":
                return """# ChatTTT Strategy Guide

## Opening Strategy
### Best Opening Moves
1. **Center (Position 5)**: Controls the most winning lines
2. **Corners (1, 3, 7, 9)**: Force opponent into difficult positions
3. **Avoid edges (2, 4, 6, 8)**: Generally weaker opening moves

### Opening Sequences
- **X starts center**: Forces O to respond carefully
- **X starts corner**: Creates immediate threats
- **O responds to center**: Should take a corner
- **O responds to corner**: Take center if available

## Mid-Game Tactics
### Forcing Moves
1. **Create two threats at once**: Win immediately if opponent can't block both
2. **Fork creation**: Set up positions where you can win on the next move in multiple ways
3. **Block and attack**: Defend while setting up your own threats

### Defensive Play
1. **Always block immediate wins**: Priority #1 is preventing opponent victories
2. **Prevent forks**: Watch for opponent setups that create multiple threats
3. **Control the center**: The center position is involved in 4 of 8 winning lines

## Advanced Strategies
### Pattern Recognition
- **L-shapes**: Look for and create L-shaped patterns that can lead to forks
- **Line completion**: Always be aware of which lines you and your opponent are developing
- **Tempo**: Sometimes the best move isn't the most obvious one

### Endgame
- **Count remaining moves**: In close games, calculate if you can win before opponent
- **Force trades**: When ahead, simplify the position
- **Desperate measures**: When behind, look for trick plays and opponent mistakes

## AI Behavior
The ChatTTT AI uses minimax algorithm with:
- **Perfect play**: The AI will never make a mistake
- **Depth analysis**: Looks ahead to game end
- **Position evaluation**: Assigns values to board positions
- **Pruning**: Optimizes calculation speed

## Tips for Improvement
1. **Practice openings**: Master the key opening principles
2. **Visualize threats**: Always look for immediate wins and blocks
3. **Think ahead**: Consider opponent's best responses
4. **Learn from AI**: Use "best" command to see optimal moves
5. **Pattern study**: Memorize common winning and drawing patterns
"""
                
            elif uri == "chatttp://ai-algorithms":
                return """# ChatTTT AI Algorithms

## Overview
ChatTTT uses a sophisticated AI system combining multiple technologies:
- **Minimax Algorithm**: Perfect game-tree search for optimal tic-tac-toe play
- **Large Language Models**: Natural language understanding via Ollama
- **Model Context Protocol (MCP)**: Tool integration and resource management

## Minimax Algorithm Implementation
The core game AI uses the minimax algorithm with perfect play capability.

### How Minimax Works in ChatTTT
1. **Game Tree Exploration**: Analyzes all possible future game states from current position
2. **Position Evaluation**: Assigns scores to terminal positions:
   - AI Win: +1 point
   - AI Loss: -1 point  
   - Tie: 0 points
3. **Optimal Choice**: Selects moves that maximize AI score while minimizing opponent score
4. **Perfect Play**: Never makes suboptimal moves when playing optimally

### Algorithm Implementation
```python
def minimax(board, is_maximizing, ai_player):
    winner = check_winner(board)
    
    # Terminal state evaluation
    if winner == ai_player:  return 1   # AI wins
    elif winner is not None: return -1  # AI loses
    elif None not in board:  return 0   # Tie game
    
    # Recursive evaluation
    if is_maximizing:  # AI's turn
        best_score = -infinity
        for each empty position:
            make move for AI
            score = minimax(board, False, ai_player)
            undo move
            best_score = max(score, best_score)
        return best_score
    else:  # Opponent's turn
        best_score = +infinity
        for each empty position:
            make move for opponent
            score = minimax(board, True, ai_player)
            undo move
            best_score = min(score, best_score)
        return best_score
```

### Performance Characteristics
- **Completeness**: Always finds the optimal move if one exists
- **Time Complexity**: O(b^d) where b=branching factor, d=depth
- **Space Complexity**: O(d) for recursive call stack
- **Tic-tac-toe Specific**: Maximum 9! = 362,880 positions to evaluate

## Natural Language Processing
ChatTTT integrates with Ollama for conversational AI capabilities.

### Language Model Integration
- **Model Support**: Compatible with various Ollama models (Llama, etc.)
- **Tool Selection**: AI determines which game tools to use based on user input
- **Context Awareness**: Maintains conversation history and game state
- **Response Generation**: Creates natural, helpful responses

### Prompt Engineering
The system uses carefully crafted prompts for different functions:

1. **Tool Selection Prompt**: Helps AI choose appropriate game actions
2. **Conversation Prompt**: Enables natural chat about strategy and gameplay
3. **Context Integration**: Includes game state and chat history
4. **Resource Awareness**: AI knows about available help resources

### Configuration Options
- **Temperature**: Controls randomness (default: 0.2 for consistent tool selection)
- **Max Tokens**: Response length limit (default: 2048)
- **Context Window**: Conversation memory (default: 4096 tokens)
- **Stop Sequences**: Prevents role confusion in dialogue

## Model Context Protocol (MCP)
ChatTTT implements MCP for tool integration and resource management.

### Available Tools
1. **new_game**: Reset board and start fresh game
2. **best_move**: Get optimal move using minimax algorithm  
3. **random_move**: Get random valid move for variety/learning
4. **play_move**: Execute a move at specified position

### Resource System
MCP provides structured access to documentation:
- **Game Rules**: Complete gameplay mechanics and features
- **Strategy Guide**: Advanced tactics and winning patterns
- **AI Algorithms**: Technical implementation details
- **Commands Reference**: Natural language interface guide

### Tool Execution Flow
```
User Input → Language Model → Tool Selection → MCP Server → Game Logic → Response
```

## Hybrid AI Architecture
ChatTTT combines different AI approaches for optimal user experience:

### Deterministic Game AI
- **Perfect Information**: Complete knowledge of game state
- **Optimal Play**: Minimax ensures best possible moves
- **Predictable**: Consistent behavior for competitive play
- **Fast**: Efficient computation for real-time response

### Conversational AI
- **Natural Language**: Understands varied user expressions
- **Context Sensitive**: Adapts to conversation flow
- **Educational**: Explains reasoning and strategy
- **Flexible**: Handles ambiguous or creative input

### Integration Benefits
1. **Best of Both Worlds**: Perfect game play + natural conversation
2. **Learning Support**: AI can explain optimal strategies
3. **Accessibility**: Multiple ways to interact (clicks, text, conversation)
4. **Adaptability**: Can adjust play style (optimal vs. random vs. educational)

## Auto-Play Feature
The AI can automatically play moves when enabled:

### Implementation
- **State Monitoring**: Detects when it's AI's turn
- **Automatic Execution**: Calls best_move tool without user prompt
- **Configurable**: Can be toggled on/off during gameplay
- **Learning Tool**: Allows observation of optimal play patterns

### Use Cases
- **Study**: Watch perfect play to learn strategies
- **Demonstration**: Show optimal game sequences
- **Testing**: Validate game logic and AI behavior
- **Entertainment**: AI vs AI gameplay

## Random Move Algorithm
For educational variety and beginner-friendly play:

### Implementation
```python
def random_move(board, player, game_over, winner):
    if game_over: return -1
    
    valid_moves = [i for i, cell in enumerate(board) if cell is None]
    if not valid_moves: return -1
    
    return random.choice(valid_moves) + 1  # Convert to 1-based indexing
```

### Benefits
- **Learning**: Shows different move possibilities
- **Variety**: Prevents repetitive perfect play
- **Exploration**: Demonstrates various game paths
- **Beginner Friendly**: Less intimidating than perfect play

This multi-layered AI architecture makes ChatTTT both a challenging game and an educational tool for learning about game theory, AI algorithms, and natural language processing.
"""
                
            elif uri == "chatttp://commands-reference":
                return """# ChatTTT Natural Language Interface

## How to Interact
ChatTTT features an advanced natural language interface powered by AI. You don't need to memorize specific commands - just tell the AI what you want to do in natural language!

## Making Moves
### Position Selection
- **Natural**: "I'll take position 5", "Put my X in the center", "I choose the middle"
- **Simple**: Just type "5" or click on the cell
- **Descriptive**: "Top left corner", "middle right", "bottom center"
- **Conversational**: "Let me try the top row, second position"

### Board Layout Reference
```
1 2 3 
4 5 6 
7 8 9 
```

## Game Management
### Starting New Games
- **Natural**: "Let's start over", "I want a new game", "Can we restart?"
- **Simple**: "New game", "Restart", "Reset"
- **Conversational**: "This isn't going well, can we try again?"

### Getting Help and Information
- **Strategy**: "What's a good move?", "Help me decide", "What should I do?"
- **Random**: "Surprise me", "Pick something random", "Give me any move"
- **Best Move**: "What's the optimal play?", "Show me the best move", "What would you do?"
- **Resources**: "Help", "Show me the guides", "Tell me about the rules"

## AI Assistance Features
### Auto-Play Mode
- Toggle the "Auto-Play" switch in the chat header
- When enabled, AI automatically plays its moves
- Great for watching AI vs AI gameplay or learning from AI strategies
- Can be toggled on/off at any time during the game

### Move Suggestions
The AI can help in several ways:
- **Strategic analysis**: Ask "What should I do?" for optimal move recommendations
- **Learning support**: "What would you do?" for educational explanations
- **Exploration**: "Show me my options" for different possibilities
- **Random play**: "Make a random move" for variety and learning

### Conversation and Learning
- **Rules questions**: "How do I win?", "What are the rules?", "How does scoring work?"
- **Strategy discussion**: "What's a good opening?", "How does the AI think?", "Why did you pick that move?"
- **General chat**: Feel free to chat about anything - the AI is conversational!
- **Game analysis**: "How am I doing?", "What are my chances?", "Is this a good position?"

## Web Interface Features
### Visual Elements
- **Game Board**: Click any empty cell to make a move
- **Chat Interface**: Type natural language commands and questions
- **Status Panel**: Shows connection status for Ollama AI and MCP services
- **Resource Library**: Access strategy guides and documentation
- **Auto-Play Toggle**: Enable/disable automatic AI moves

### Service Configuration
- **Ollama Server**: Configure AI model server (default: localhost:11434)
- **Model Selection**: Choose from available AI models
- **MCP Server**: Configure game logic server (default: localhost:8000)
- **Resource Access**: View game rules, strategies, and AI algorithm details

## Confirmation Handling
When the system needs confirmation (like starting a new game mid-play):
- **Confirm**: "Yes", "OK", "Go ahead", "Sure", "Confirm", "Do it"
- **Cancel**: "No", "Cancel", "Never mind", "Stop", "Don't do it"

## Examples of Natural Input
### Move Commands
- "I'll play position 3"
- "Put my X in the bottom left"
- "5" (for center position)
- "Top right corner please"
- "Let me take the middle of the top row"

### Strategy Requests  
- "What's my best move here?"
- "Help me win this game"
- "What would you do in this situation?"
- "Give me a random suggestion"
- "Show me my options"

### Game Management
- "Let's start a fresh game"
- "I want to restart this"
- "New game please"
- "Can we play again?"
- "Reset the board"

### Questions and Learning
- "How does this game work?"
- "What's a good strategy for beginners?"
- "Why did you pick that move?"
- "Tell me about the AI algorithms"
- "What are the winning patterns?"
- "How can I improve my play?"

## Tips for Best Experience
1. **Be natural**: Speak as you would to a friend playing games with you
2. **Be specific**: "Top corner" is clearer than just "corner"
3. **Ask questions**: The AI loves to explain, teach, and discuss strategy
4. **Experiment**: Try different ways of expressing the same request
5. **Use context**: The AI remembers the current game state and conversation
6. **Explore resources**: Use the resource panel to access detailed guides
7. **Try auto-play**: Watch the AI play to learn optimal strategies

## Error Handling and Recovery
If the AI doesn't understand your input:
- Try rephrasing your request in simpler terms
- Be more specific about what you want
- Ask for clarification: "I meant position 5"
- Use the visual interface: click directly on the board
- Check the resource guides for examples

The AI is designed to be helpful, patient, and forgiving, so don't worry about making mistakes or asking for clarification!
"""
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
                
        except Exception as e:
            raise Exception(f"Error reading resource {uri}: {str(e)}")
    
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute a tool based on its name and arguments."""
        try:
            if name == "new_game":
                return await self._new_game()
            elif name == "best_move":
                return await self._best_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
            elif name == "random_move":
                return await self._random_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
            elif name == "play_move":
                return await self._play_move(
                    arguments["board"],
                    arguments["position"],
                    arguments["player"]
                )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )],
                    isError=True
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )],
                isError=True
            )

    async def _new_game(self) -> CallToolResult:
        """Start a new game."""
        result = self.agent.new_game()
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"New game started: {result}"
            )]
        )

    async def _best_move(self, board: List[Optional[str]], player: str, game_over: bool = False, winner: Optional[str] = None) -> CallToolResult:
        """Get the best move for the specified player."""
        best_move = self.agent.best_move(board, player, game_over, winner)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Best move for {player}: position {best_move}"
            )]
        )

    async def _random_move(self, board: List[Optional[str]], player: str, game_over: bool = False, winner: Optional[str] = None) -> CallToolResult:
        """Get a random move for the specified player."""
        random_move = self.agent.random_move(board, player, game_over, winner)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Random move for {player}: position {random_move}"
            )]
        )

    async def _play_move(self, board: List[Optional[str]], position: int, player: str) -> CallToolResult:
        """Make a move on the board."""
        result = self.agent.play_move(board, position, player)
        
        if result == -1:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Invalid move: position {position} for player {player}"
                )],
                isError=True
            )
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Move made: player {player} at position {result}"
                )]
            )
