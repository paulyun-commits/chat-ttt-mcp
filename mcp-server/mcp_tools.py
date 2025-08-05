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
                description="Complete rules and gameplay mechanics for ChatTTT, including how to play, winning conditions, and available commands",
                mimeType="text/plain"
            ),
            Resource(
                uri="chatttp://strategy-guide",
                name="ChatTTT Strategy Guide",
                description="Advanced strategies for optimal play, including opening moves, defensive tactics, and endgame scenarios",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://ai-algorithms",
                name="AI Algorithm Information",
                description="Technical details about the AI algorithms used in ChatTTT, including the minimax algorithm and evaluation functions",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://commands-reference",
                name="Natural Language Interface Guide",
                description="How to interact naturally with ChatTTT using conversational language instead of specific commands",
                mimeType="text/plain"
            )
        ]
    
    async def get_resource_content(self, uri: str):
        """Get the content of a specific resource."""
        try:
            if uri == "chatttp://game-rules":
                content = """# ChatTTT Game Rules

## Objective
Be the first player to get three of your marks (X or O) in a row, column, or diagonal.

## How to Play
1. The game is played on a 3x3 grid numbered 1-9:
   ```
    1 | 2 | 3 
   -----------
    4 | 5 | 6 
   -----------
    7 | 8 | 9 
   ```

2. Players take turns placing their marks (X for human, O for AI).
3. You can make moves by:
   - Clicking on an empty cell
   - Typing a position number (1-9) in the chat
   - Using voice commands like "play position 5"

## Available Commands
- **Numbers 1-9**: Make a move at that position
- **"new"**: Start a new game (asks for confirmation if game in progress)
- **"random"**: Get a random move suggestion
- **"best"**: Get the best move suggestion from the AI
- **"help"**: Show available commands and resources

## Winning Conditions
- Three marks in a row (horizontal, vertical, or diagonal)
- If all 9 positions are filled without a winner, it's a tie

## AI Features
- The AI uses a minimax algorithm for optimal play
- AI can provide move suggestions with "random" or "best" commands
- Real-time game state analysis and strategic recommendations
"""
                return content
                
            elif uri == "chatttp://strategy-guide":
                content = """# ChatTTT Strategy Guide

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
                return content
                
            elif uri == "chatttp://ai-algorithms":
                content = """# ChatTTT AI Algorithms

## Minimax Algorithm
The core AI uses the minimax algorithm with alpha-beta pruning.

### How Minimax Works
1. **Game Tree**: Explores all possible future game states
2. **Evaluation**: Assigns scores to terminal positions:
   - Win: +10 points
   - Loss: -10 points  
   - Tie: 0 points
3. **Backpropagation**: Chooses moves that maximize AI score while minimizing human score

### Algorithm Steps
```
function minimax(board, depth, isMaximizing):
    if game is over:
        return score
    
    if isMaximizing (AI turn):
        bestScore = -infinity
        for each empty position:
            make move
            score = minimax(board, depth+1, false)
            bestScore = max(score, bestScore)
            undo move
        return bestScore
    else (Human turn):
        bestScore = +infinity
        for each empty position:
            make move
            score = minimax(board, depth+1, true)
            bestScore = min(score, bestScore)
            undo move
        return bestScore
```

## Alpha-Beta Pruning
Optimization technique that eliminates branches that won't affect the final decision.

### Benefits
- **Speed**: Reduces computation time significantly
- **Same result**: Always finds the same best move as basic minimax
- **Scalability**: Allows deeper search in larger games

## Position Evaluation
### Static Evaluation Factors
1. **Win/Loss detection**: Immediate game-ending positions
2. **Threat analysis**: Positions that could lead to wins
3. **Control metrics**: Center control, corner control
4. **Pattern recognition**: Common tactical motifs

### Heuristics Used
- **Center bonus**: Extra value for controlling position 5
- **Corner preference**: Corners are generally stronger than edges
- **Line development**: Progress toward completing winning lines
- **Fork potential**: Positions that could create multiple threats

## Implementation Details
### Data Structures
- **Board representation**: Array of 9 positions
- **Game state**: Current player, game status, winner
- **Move generation**: List of legal moves from current position

### Performance Optimizations
- **Move ordering**: Try most promising moves first
- **Transposition tables**: Cache previously calculated positions
- **Iterative deepening**: Gradually increase search depth
- **Quiescence search**: Handle tactical complications

## Random Move Algorithm
For learning and variety, the AI can also generate random moves:

1. **Find empty positions**: Scan board for available moves
2. **Random selection**: Use cryptographically secure random number generator
3. **Validation**: Ensure selected move is legal
4. **Fallback**: If random fails, use minimax as backup

This approach helps beginners learn by showing various move possibilities rather than always playing perfectly.
"""
                return content
                
            elif uri == "chatttp://commands-reference":
                content = """# ChatTTT Natural Language Interface

## How to Interact
ChatTTT uses natural language understanding, so you don't need to memorize specific commands. Just tell me what you want to do!

## Making Moves
### Position Selection
- **Natural**: "I'll take position 5" or "Put my X in the center"
- **Simple**: "5" or just click on the cell
- **Descriptive**: "Top left corner" or "middle right"

### Board Layout Reference
```
 1 | 2 | 3 
-----------
 4 | 5 | 6 
-----------
 7 | 8 | 9 
```

## Game Control
### Starting New Games
- **Natural**: "Let's start over" or "I want a new game"
- **Simple**: "New game" or "Restart"
- **Conversational**: "Can we play again?"

### Getting Help
- **Strategy**: "What's a good move?" or "Help me decide"
- **Random**: "Surprise me" or "Pick something random"
- **Best Move**: "What's the optimal play?" or "Show me the best move"

## AI Assistance
### Move Suggestions
The AI can help in several ways:
- **Strategic analysis**: Ask "What should I do?" for the best move
- **Learning**: Ask "What would you do?" for educational suggestions  
- **Exploration**: Say "Show me options" for different possibilities
- **Random play**: "Make a random move" for variety

### Conversation
- **Rules questions**: "How do I win?" or "What are the rules?"
- **Strategy discussion**: "What's a good opening?" or "How does the AI work?"
- **General chat**: Feel free to chat about anything!

## Confirmation Handling
When the system needs confirmation (like starting a new game mid-play):
- **Confirm**: "Yes", "OK", "Go ahead", "Sure", "Confirm"
- **Cancel**: "No", "Cancel", "Never mind", "Stop"

## Examples of Natural Input
### Move Commands
- "I'll play position 3"
- "Put my X in the bottom left"
- "5" (for center position)
- "Top right corner please"

### Strategy Requests  
- "What's my best move here?"
- "Help me win this game"
- "What would you do?"
- "Give me a random suggestion"

### Game Management
- "Let's start a fresh game"
- "I want to restart"
- "New game please"
- "Can we play again?"

### Questions and Chat
- "How does this game work?"
- "What's a good strategy?"
- "Why did you pick that move?"
- "Tell me about the AI"

## Tips for Best Experience
1. **Be natural**: Speak as you would to a friend
2. **Be specific**: "Top corner" is clearer than just "corner"
3. **Ask questions**: The AI loves to explain and teach
4. **Experiment**: Try different ways of saying things
5. **Use context**: The AI remembers the current game state

## Error Handling
If the AI doesn't understand:
- Try rephrasing your request
- Be more specific about what you want
- Ask for clarification: "I meant position 5"
- Use simpler language if needed

The AI is designed to be helpful and forgiving, so don't worry about making mistakes!
"""
                return content
                
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
