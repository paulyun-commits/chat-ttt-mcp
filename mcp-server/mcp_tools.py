from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent, CallToolResult, Resource, Prompt
from agent import TicTacToeAgent

class MCPTools:
    def __init__(self):
        self.agent = TicTacToeAgent()
    
    def get_tools(self) -> List[Tool]:
        """Return list of available MCP tools."""
        return [
            Tool(
                name="new_game",
                description="Start a fresh tic-tac-toe game. Use when the user wants to restart, begin a new game, or clear the current board. No parameters required.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="best_move",
                description="Calculate the optimal move using minimax algorithm. Use when the user asks for the best move, wants strategic advice, or requests optimal play suggestions. Returns position 1-9 of the strongest move.",
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
                            "description": "Current board state as array of 9 elements. Each element is 'X', 'O', or null for empty cells. Index 0 = position 1, index 8 = position 9."
                        },
                        "player": {
                            "type": "string",
                            "description": "Which player to calculate the best move for ('X' for human, 'O' for AI)",
                            "enum": ["X", "O"]
                        },
                        "game_over": {
                            "type": "boolean",
                            "description": "Whether the current game has ended (win/tie)",
                            "default": False
                        },
                        "winner": {
                            "type": ["string", "null"],
                            "description": "Winner of the game if ended: 'X', 'O', or null for tie/ongoing",
                            "enum": ["X", "O", None]
                        }
                    },
                    "required": ["board", "player"]
                }
            ),
            Tool(
                name="random_move",
                description="Get a random valid move for educational or casual play. Use when user wants surprise moves, random suggestions, or less competitive gameplay. Returns position 1-9 of a randomly chosen valid move.",
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
                            "description": "Current board state as array of 9 elements. Each element is 'X', 'O', or null for empty cells. Index 0 = position 1, index 8 = position 9."
                        },
                        "player": {
                            "type": "string",
                            "description": "Which player to generate a random move for ('X' for human, 'O' for AI)",
                            "enum": ["X", "O"]
                        },
                        "game_over": {
                            "type": "boolean",
                            "description": "Whether the current game has ended (win/tie)",
                            "default": False
                        },
                        "winner": {
                            "type": ["string", "null"],
                            "description": "Winner of the game if ended: 'X', 'O', or null for tie/ongoing",
                            "enum": ["X", "O", None]
                        }
                    },
                    "required": ["board", "player"]
                }
            ),
            Tool(
                name="play_move",
                description="Execute a move at a specific board position. Use when user specifies a position number (1-9) or describes a specific cell they want to play. Validates the move is legal and updates game state.",
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
                            "description": "Current board state as array of 9 elements. Each element is 'X', 'O', or null for empty cells. Index 0 = position 1, index 8 = position 9."
                        },
                        "position": {
                            "type": "integer",
                            "description": "Board position to play (1-9). Layout: 1-3 top row, 4-6 middle row, 7-9 bottom row",
                            "minimum": 1,
                            "maximum": 9
                        },
                        "player": {
                            "type": "string",
                            "description": "Player making the move ('X' for human, 'O' for AI)",
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
                name="ChatTTT Game Rules and Interface Guide",
                description="Complete reference for ChatTTT gameplay mechanics, board layout, winning conditions, user interface features, and available interaction methods. Essential for understanding how the game works.",
                mimeType="text/plain"
            ),
            Resource(
                uri="chatttp://strategy-guide", 
                name="Tic-Tac-Toe Strategy and Tactics",
                description="Advanced strategic guidance for optimal tic-tac-toe play including opening theory, tactical patterns, endgame principles, and minimax algorithm insights. Useful for explaining game concepts to users.",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://ai-algorithms",
                name="Technical Implementation Details",
                description="In-depth technical documentation of ChatTTT's AI architecture, minimax algorithm implementation, MCP integration, and language model capabilities. For technical discussions about how the system works.",
                mimeType="text/markdown"
            ),
            Resource(
                uri="chatttp://commands-reference",
                name="Natural Language Interface Examples",
                description="Comprehensive guide showing how users can interact with ChatTTT using natural conversation, including example phrases, command patterns, and troubleshooting common interaction issues.",
                mimeType="text/plain"
            )
        ]
    
    def get_prompts(self) -> List[Prompt]:
        """Return list of available MCP prompts."""
        return [
            Prompt(
                name="strategy_coach",
                description="Get personalized tic-tac-toe strategy coaching based on current game state and skill level",
                arguments=[
                    {
                        "name": "board_state",
                        "description": "Current board state as 9-element array",
                        "required": False
                    },
                    {
                        "name": "skill_level",
                        "description": "Player skill level: beginner, intermediate, or expert",
                        "required": False
                    },
                    {
                        "name": "focus_area",
                        "description": "Specific area to focus on: opening, tactics, endgame, or general",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="game_analyzer",
                description="Analyze a completed or ongoing tic-tac-toe game and provide detailed feedback",
                arguments=[
                    {
                        "name": "move_history",
                        "description": "Sequence of moves made in the game",
                        "required": True
                    },
                    {
                        "name": "analysis_depth",
                        "description": "Level of analysis: quick, detailed, or comprehensive",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="learning_path",
                description="Generate a personalized learning path for improving tic-tac-toe skills",
                arguments=[
                    {
                        "name": "current_level",
                        "description": "Current skill assessment: beginner, intermediate, or expert",
                        "required": True
                    },
                    {
                        "name": "learning_goals",
                        "description": "Specific learning objectives or areas of interest",
                        "required": False
                    }
                ]
            )
        ]
    
    async def get_resource_content(self, uri: str):
        """Get the content of a specific resource."""
        try:
            if uri == "chatttp://game-rules":
                return """# ChatTTT Game Rules and Interface Guide

## Game Objective
Be the first player to get three of your marks in a row, column, or diagonal on a 3x3 grid.

## Board Layout
The game uses a numbered 3x3 grid:
```
1 | 2 | 3 
---------
4 | 5 | 6 
---------
7 | 8 | 9 
```

## Players
- **Human Player**: Always plays as 'X' and goes first
- **AI Player**: Always plays as 'O' and responds to human moves

## How to Make Moves

### Web Interface
- **Direct Click**: Click any empty cell on the visual game board
- **Chat Input**: Type moves in the chat interface using any of these methods:

### Chat Commands for Moves
- **Position Numbers**: Type "5" or "position 5" for center, "1" for top-left, etc.
- **Natural Language**: "I'll take the center", "top right corner", "middle left"
- **Descriptive**: "Put my X in position 3", "I choose the bottom row middle"

### Game Management Commands
- **New Game**: "new game", "restart", "start over", "let's play again"
- **Move Suggestions**: 
  - "best move" or "what should I do?" - Get optimal move using minimax
  - "random move" or "surprise me" - Get a random valid move suggestion
- **Help**: "help", "rules", "how to play" - Access game documentation

## Game Features

### Chat Interface
- **Natural Conversation**: Talk to the AI about strategy, ask questions, get explanations
- **Move Analysis**: Ask why certain moves are good or bad
- **Strategy Discussion**: Learn about tic-tac-toe tactics and theory

### Auto-Play Mode
- **Toggle Control**: Use the "Auto-Play" switch in the chat header
- **When Enabled**: AI automatically makes its moves without waiting for prompts
- **When Disabled**: AI waits for user to ask for moves or suggestions
- **Use Cases**: Watch AI vs AI, study optimal play patterns, demonstration mode

### Service Status Panel
- **Ollama Status**: Shows connection to AI language model server
- **MCP Status**: Shows connection to game logic server
- **Settings**: Configure server URLs and AI model selection
- **Resource Library**: Access strategy guides and technical documentation

## Winning Conditions
- **Victory**: Three marks in a row (horizontal, vertical, or diagonal)
- **Tie**: All 9 positions filled with no winner
- **Game Status**: Displayed above the board and updated in real-time

## Board State Representation
Internally, the game uses a 9-element array where:
- Index 0 = Position 1 (top-left)
- Index 4 = Position 5 (center) 
- Index 8 = Position 9 (bottom-right)
- Values: 'X' for human, 'O' for AI, null for empty

## Interface Messages
- **Game Status**: Shows whose turn it is or game outcome
- **Chat Messages**: AI responses, move confirmations, explanations
- **System Messages**: Tool calls, server status, error notifications

## Error Handling
- **Invalid Moves**: Attempting to play in occupied cells shows error message
- **Server Issues**: Status indicators show connection problems
- **Input Clarification**: AI asks for clarification on ambiguous requests

## Tips for Best Experience
1. **Be Natural**: Speak conversationally - the AI understands varied phrasing
2. **Ask Questions**: The AI can explain strategy, rules, and reasoning
3. **Use Visual + Chat**: Click for quick moves, chat for strategy discussion
4. **Try Auto-Play**: Learn by watching optimal AI gameplay
5. **Explore Resources**: Access detailed guides through the resource panel
"""
                
            elif uri == "chatttp://strategy-guide":
                return """# Tic-Tac-Toe Strategy and Tactics Guide

## Fundamental Principles

### Board Position Values
In tic-tac-toe, not all positions are equal:
1. **Center (Position 5)**: Most valuable - participates in 4 winning lines
2. **Corners (1, 3, 7, 9)**: Strong - each participates in 3 winning lines  
3. **Edges (2, 4, 6, 8)**: Weakest - each participates in only 2 winning lines

### Basic Strategic Rules
1. **Win if possible**: Always take a winning move when available
2. **Block opponent wins**: Always prevent opponent from winning on their next turn
3. **Create threats**: Set up multiple ways to win simultaneously
4. **Control center**: The center position offers maximum flexibility
5. **Force opponent mistakes**: Create difficult choices for your opponent

## Opening Strategy

### Best First Moves
- **Center (5)**: Controls maximum winning lines, forces opponent into difficult responses
- **Corners (1, 3, 7, 9)**: Create immediate threats and control key diagonal lines
- **Avoid Edges (2, 4, 6, 8)**: Generally suboptimal opening moves with limited potential

### Opening Sequences
1. **X plays center (5)**:
   - O should respond with a corner for best defense
   - If O plays edge, X can often force a win

2. **X plays corner (e.g., 1)**:
   - O should take center (5) if available
   - Creates immediate threats O must address

3. **X plays edge (not recommended)**:
   - O can take center and gain advantage
   - Limits X's winning potential

## Tactical Patterns

### The Fork
A fork creates two winning threats simultaneously, guaranteeing victory:
- **Corner Fork**: Playing opposite corners often creates fork opportunities
- **L-Shape Fork**: Creating L-shaped patterns can lead to multiple threats
- **Example**: X in positions 1 and 9, then X in 5 creates unstoppable threats

### Defensive Patterns
1. **Block Immediate Wins**: Priority #1 - never let opponent win on next move
2. **Prevent Forks**: Watch for opponent setups that create multiple threats
3. **Maintain Balance**: Don't leave opponent with multiple good options

### Advanced Tactics
- **Tempo Control**: Sometimes the non-obvious move is best
- **Sacrifice Plays**: Give up material advantage to prevent opponent forks
- **End-game Counting**: Calculate who can win first in close positions

## Position Analysis

### Common Winning Patterns
```
X X X    X . .    X . .    X . .
. . .    X . .    . X .    . . .
. . .    X . .    . . X    . . X

Row Win  Col Win  Diag 1   Diag 2
```

### Critical Decision Points
1. **Move 3 (X's second move)**: Often determines game outcome
2. **Move 5 (X's third move)**: Last chance to create winning threats
3. **Move 7-9**: Endgame precision required

## AI Behavior in ChatTTT

### Minimax Algorithm
The ChatTTT AI uses perfect minimax with these characteristics:
- **Perfect Play**: Never makes mistakes when playing optimally
- **Deterministic**: Same board position always yields same move
- **Complete Analysis**: Examines all possible game continuations
- **Optimal Defense**: Minimizes opponent's winning chances

### AI Playing Styles
1. **Best Move Tool**: Always returns mathematically optimal move
2. **Random Move Tool**: Provides educational variety and casual play
3. **Auto-Play Mode**: Demonstrates perfect play patterns

### Learning from AI
- **Ask for explanations**: "Why did you play there?"
- **Request analysis**: "What are my best options?"
- **Study patterns**: Use auto-play to watch optimal sequences
- **Compare moves**: See difference between optimal and random play

## Strategy for Human Players

### Against Perfect AI
- **Learn optimal play**: Study the AI's move choices
- **Understand why**: Ask AI to explain strategic reasoning  
- **Practice patterns**: Memorize key opening and defensive sequences
- **Accept draws**: Perfect play by both sides leads to ties

### Improvement Tips
1. **Master the fundamentals**: Win-block-fork-center-corner priority
2. **Visualize threats**: Always look ahead one move for both players
3. **Practice endgames**: Learn to count moves in close positions
4. **Study openings**: Memorize optimal responses to common starts
5. **Use tools wisely**: Compare your ideas with "best move" suggestions

## Common Mistakes to Avoid

### Strategic Errors
- **Playing edges as opening moves**: Limits winning potential
- **Ignoring opponent threats**: Always check for immediate dangers
- **Focusing only on offense**: Balance attack and defense
- **Missing fork opportunities**: Look for ways to create multiple threats

### Tactical Mistakes
- **Not blocking wins**: Letting opponent win when you could prevent it
- **Creating opponent forks**: Setting up opponent for multiple threats  
- **Premature aggression**: Attacking before securing your position
- **Endgame miscounting**: Making moves without calculating to game end

## Practice Exercises

### Pattern Recognition Drills
1. **Find the Fork**: Look for positions where you can create multiple threats
2. **Block the Fork**: Identify and prevent opponent fork setups
3. **Endgame Studies**: Practice counting moves in nearly-full boards
4. **Opening Variations**: Try different opening moves and analyze results

### Using ChatTTT for Learning
- **Compare strategies**: Try your move, then ask for "best move"
- **Random practice**: Use random moves to explore different game paths
- **Auto-play study**: Watch AI vs AI games to see perfect play
- **Strategy discussion**: Ask AI about specific positions and tactics

This strategic foundation will help you understand both optimal play and common human tendencies in tic-tac-toe, making you a stronger player and better able to appreciate the AI's decision-making process.
"""
                
            elif uri == "chatttp://ai-algorithms":
                return """# ChatTTT Technical Implementation and AI Architecture

## System Overview
ChatTTT implements a sophisticated multi-layered AI system combining several technologies:
- **Minimax Algorithm**: Perfect game-tree search for optimal tic-tac-toe play
- **Language Model Integration**: Natural language understanding via Ollama
- **Model Context Protocol (MCP)**: Structured tool integration and resource management
- **Hybrid Architecture**: Combines deterministic game AI with conversational AI

## Core Game AI: Minimax Algorithm

### Algorithm Implementation
ChatTTT uses a classic minimax algorithm for perfect tic-tac-toe play:

```python
def minimax(self, board, is_maximizing, ai_player):
    winner = self._check_winner(board)
    
    # Terminal state evaluation
    if winner == ai_player:  return 1   # AI wins
    elif winner is not None: return -1  # AI loses  
    elif None not in board:  return 0   # Tie game
    
    opponent = 'X' if ai_player == 'O' else 'O'
    
    if is_maximizing:  # AI's turn
        best_score = float('-inf')
        for i in range(9):
            if board[i] is None:
                board[i] = ai_player
                score = self.minimax(board, False, ai_player)
                board[i] = None
                best_score = max(score, best_score)
        return best_score
    else:  # Opponent's turn
        best_score = float('inf')
        for i in range(9):
            if board[i] is None:
                board[i] = opponent
                score = self.minimax(board, True, ai_player)
                board[i] = None
                best_score = min(score, best_score)
        return best_score
```

### Minimax Characteristics
- **Completeness**: Always finds optimal move if one exists
- **Deterministic**: Same board state always produces same move
- **Perfect Play**: Never makes suboptimal moves when used optimally
- **Time Complexity**: O(b^d) where b=branching factor, d=depth
- **Space Complexity**: O(d) for recursive call stack
- **Tic-tac-toe Specific**: Maximum 9! = 362,880 game states to evaluate

### Win Condition Detection
```python
def _check_winner(self, board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns  
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    
    for combo in winning_combinations:
        if (board[combo[0]] is not None and 
            board[combo[0]] == board[combo[1]] == board[combo[2]]):
            return board[combo[0]]
    return None
```

## Natural Language Processing Layer

### Ollama Integration
ChatTTT integrates with Ollama for conversational AI capabilities:

- **Model Flexibility**: Compatible with various models (Llama, Mistral, etc.)
- **Tool Selection**: AI determines appropriate MCP tools based on user input
- **Context Awareness**: Maintains game state and conversation history
- **Natural Response Generation**: Creates helpful, contextual responses

### Language Model Configuration
```javascript
const ollamaConfig = {
    temperature: 0.2,        // Low for consistent tool selection
    max_tokens: 2048,        // Sufficient for detailed responses
    context_window: 4096,    // Maintains conversation memory
    stop_sequences: [...],   // Prevents role confusion
}
```

### Prompt Engineering Strategy
The system uses carefully crafted prompts for different functions:

1. **Tool Selection Prompt**: Helps AI choose appropriate MCP tools
```
You are a smart assistant for a tic-tac-toe game that can select tools.
Analyze the user's request and pick an appropriate tool if there is one.
Be choosy and only select the tool that's right for the job, otherwise return 'none'.
If the user's request is a single number, you can assume the play_move tool.
```

2. **Context Integration**: Includes current game state, board layout, and chat history
3. **Resource Awareness**: AI knows about available documentation and guides

## Model Context Protocol (MCP) Implementation

### Available Tools
ChatTTT exposes four core tools through MCP:

1. **`new_game`**: Reset board state and start fresh game
   - Parameters: None
   - Returns: Confirmation message
   - Use case: User wants to restart or begin new game

2. **`best_move`**: Calculate optimal move using minimax
   - Parameters: board state, player, game_over, winner
   - Returns: Position (1-9) of strongest move
   - Use case: Strategic advice, optimal play

3. **`random_move`**: Generate random valid move
   - Parameters: board state, player, game_over, winner  
   - Returns: Position (1-9) of randomly selected move
   - Use case: Educational variety, casual play

4. **`play_move`**: Execute move at specified position
   - Parameters: board state, position, player
   - Returns: Confirmation or error message
   - Use case: User specifies exact move to make

### Resource System
MCP provides structured access to documentation:
- **Game Rules**: Complete gameplay mechanics and interface guide
- **Strategy Guide**: Advanced tactics and winning patterns
- **AI Algorithms**: Technical implementation details (this document)
- **Commands Reference**: Natural language interface examples

### Tool Execution Flow
```
User Input → Language Model → Tool Selection → MCP Server → Game Logic → Response
     ↓              ↓              ↓              ↓              ↓
Natural Text → Intent Analysis → Tool Choice → Method Call → Game Update → User Feedback
```

## Hybrid AI Architecture Benefits

### Deterministic Game Logic + Conversational Interface
This combination provides several advantages:

1. **Perfect Game Play**: Minimax ensures optimal tic-tac-toe moves
2. **Natural Interaction**: Users can communicate in plain English
3. **Educational Value**: AI can explain reasoning and strategy
4. **Flexibility**: Supports both competitive and casual play styles

### Architecture Layers
```
┌─────────────────────┐
│   User Interface    │ ← Web UI, chat input, visual board
├─────────────────────┤
│   Language Model    │ ← Ollama (natural language processing)
├─────────────────────┤
│   MCP Protocol      │ ← Tool selection and resource management  
├─────────────────────┤
│   Game Logic        │ ← Python agent with minimax algorithm
└─────────────────────┘
```

## Auto-Play Feature Implementation

### Automatic Move Generation
When auto-play is enabled:
- **State Monitoring**: JavaScript detects when it's AI's turn
- **Automatic Tool Call**: Calls `best_move` without user prompt
- **Immediate Execution**: Makes optimal move automatically
- **User Override**: Can be toggled on/off during gameplay

### Implementation Details
```javascript
async function handleAutoPlay() {
    if (autoPlayEnabled && gameState.player === 'O' && !gameState.gameOver) {
        const bestMove = await callMCPTool('best_move', {
            board: gameState.board,
            player: 'O',
            game_over: gameState.gameOver,
            winner: gameState.winner
        });
        await executeMove(bestMove.position, 'O');
    }
}
```

## Random Move Algorithm

### Implementation for Educational Variety
```python
def random_move(self, board, player, game_over=False, winner=None):
    if game_over: return -1
    
    valid_moves = [i for i, cell in enumerate(board) if cell is None]
    if not valid_moves: return -1
    
    return random.choice(valid_moves) + 1  # Convert to 1-based indexing
```

### Use Cases
- **Learning**: Shows different strategic possibilities
- **Variety**: Prevents repetitive perfect play patterns
- **Beginner Friendly**: Less intimidating than perfect play
- **Exploration**: Demonstrates various game paths and outcomes

## Performance Characteristics

### Minimax Performance
- **Tic-tac-toe Optimization**: Game tree small enough for real-time perfect play
- **Maximum Depth**: 9 moves (board positions)
- **Branching Factor**: Decreases as game progresses (9, 8, 7, ...)
- **Response Time**: Sub-second for all positions

### Language Model Performance
- **Tool Selection**: Typically < 1 second for simple requests
- **Context Processing**: Scales with conversation length
- **Memory Usage**: Manages conversation history efficiently
- **Error Recovery**: Graceful handling of ambiguous input

## System Integration

### Client-Server Architecture
```
Web Browser ←→ MCP Client (Node.js) ←→ MCP Server (Python) ←→ Game Agent
     ↓                    ↓                      ↓               ↓
   UI Logic        HTTP Bridge           Tool Execution    Game Logic
```

### Communication Protocols
- **HTTP**: Browser to MCP client communication
- **MCP Protocol**: Structured tool and resource access
- **JSON**: Data serialization for board states and messages
- **WebSocket**: Real-time status updates (if implemented)

## Error Handling and Validation

### Input Validation
- **Board State**: Validates 9-element array with correct values
- **Position Range**: Ensures positions are 1-9
- **Move Legality**: Checks if position is empty before playing
- **Game State**: Verifies game hasn't ended before allowing moves

### Error Recovery
- **Graceful Degradation**: System continues functioning with partial failures
- **User Feedback**: Clear error messages for invalid operations
- **Alternative Paths**: Multiple ways to accomplish same goals
- **State Consistency**: Maintains valid game state throughout

This technical architecture enables ChatTTT to provide both perfect game play and natural conversational interaction, making it both a challenging opponent and an educational tool for learning about game theory, AI algorithms, and natural language processing.
"""
                
            elif uri == "chatttp://commands-reference":
                return """# ChatTTT Natural Language Interface Examples

## Overview
ChatTTT features an advanced natural language interface powered by AI language models. Users can interact through natural conversation rather than memorizing specific commands. The AI analyzes user input and automatically selects appropriate tools based on context.

## How the Interface Works
1. **User Input**: Type natural language in the chat interface
2. **AI Analysis**: Language model analyzes intent and current game state  
3. **Tool Selection**: AI automatically chooses the right tool (new_game, best_move, random_move, play_move, or none)
4. **Action Execution**: Selected tool is called with current board state
5. **Response**: AI provides natural language response about the action taken

## Making Moves

### Direct Position Selection
The most straightforward way to make moves:
- **Simple Numbers**: "5", "1", "9" 
- **Position Phrases**: "position 5", "spot 3", "cell 7"
- **With Context**: "I'll take position 5", "Put my X in position 1"

### Descriptive Location References
Natural descriptions of board positions:
- **Center**: "center", "middle", "position 5"
- **Corners**: "top left" (1), "top right" (3), "bottom left" (7), "bottom right" (9)
- **Edges**: "top middle" (2), "middle left" (4), "middle right" (6), "bottom middle" (8)
- **Row/Column**: "top row middle", "left column bottom", "right side center"

### Conversational Move Requests
- **Casual**: "I'll go here", "Let me try this spot", "How about position 5?"
- **Decisive**: "I choose the center", "I'll take the top corner", "Put me in position 3"
- **Descriptive**: "I want the middle of the top row", "Give me the bottom left corner"

## Game Management

### Starting New Games
- **Direct**: "new game", "restart", "start over"
- **Conversational**: "Let's play again", "Can we start fresh?", "I want to try again"
- **Contextual**: "This isn't going well, let's restart", "New game please"

### Getting Move Suggestions

#### Best Move Requests
Triggers the `best_move` tool for optimal play:
- **Direct**: "best move", "what's the best move?", "optimal play"
- **Advisory**: "what should I do?", "help me decide", "what would you play?"
- **Strategic**: "what's the strongest move?", "show me the best option"

#### Random Move Requests  
Triggers the `random_move` tool for variety:
- **Direct**: "random move", "surprise me", "pick something random"
- **Casual**: "give me any move", "you choose", "something different"
- **Learning**: "show me another option", "what else could I play?"

## Advanced Interaction Patterns

### Questions and Learning
The AI can discuss strategy without triggering tools:
- **Rule Questions**: "How do I win?", "What are the rules?", "How does scoring work?"
- **Strategy Discussion**: "Why is the center good?", "What makes that a strong move?"
- **Game Analysis**: "How am I doing?", "What are my chances?", "Is this position good?"
- **AI Behavior**: "How do you think?", "Why did you pick that move?"

### Context-Aware Responses
The AI maintains conversation context:
- **Follow-up Questions**: "What about that corner instead?", "Is there a better option?"
- **Clarification**: "I meant position 5", "Actually, let me try the center"
- **Strategy Chat**: Build on previous discussion topics naturally

### Auto-Play Mode Integration
When auto-play is enabled:
- **AI Automatically Plays**: No need to request moves for the AI
- **User Can Still Chat**: Ask questions while AI plays automatically
- **Toggle Control**: "Turn on auto-play", "Let the AI play automatically"

## Web Interface Features

### Visual + Chat Combination
- **Click to Move**: Direct cell clicks trigger `play_move` tool automatically
- **Chat for Strategy**: Use chat for questions, suggestions, and discussion
- **Status Updates**: Game status shown above board and in chat

### Service Configuration
- **Server Settings**: Configure Ollama and MCP server connections
- **Model Selection**: Choose different AI models for conversation
- **Resource Access**: View documentation and guides through web interface

## Tool Triggering Patterns

### Automatic Tool Selection
The AI automatically determines which tool to use based on input:

1. **`play_move` Triggered By**:
   - Position numbers: "5", "position 3"
   - Location descriptions: "center", "top left corner"
   - Move statements: "I'll take position 5"

2. **`best_move` Triggered By**:
   - Strategy requests: "best move", "what should I do?"
   - Advice seeking: "help me decide", "optimal play"
   - Analysis requests: "what would you do?"

3. **`random_move` Triggered By**:
   - Random requests: "surprise me", "random move"
   - Variety seeking: "something different", "you choose"
   - Casual play: "give me any move"

4. **`new_game` Triggered By**:
   - Restart requests: "new game", "start over"
   - Reset phrases: "let's try again", "restart please"

5. **No Tool (Chat Only)**:
   - Questions: "How does this work?", "What's a good strategy?"
   - Comments: "Nice move!", "This is fun!"
   - Discussion: "Tell me about minimax", "Why is that good?"

## Error Handling and Clarification

### When AI Needs Clarification
- **Ambiguous Input**: "Did you mean position 5 or 6?"
- **Invalid Moves**: "Position 5 is already taken, try another spot"
- **Context Issues**: "Are you asking for a move suggestion or making a move?"

### Recovery Strategies
- **Be More Specific**: "I meant the center position" instead of "there"
- **Use Numbers**: "Position 5" is clearer than "middle somewhere"
- **Rephrase**: Try different wording if not understood initially
- **Visual Backup**: Click directly on the board if chat input unclear

## Example Conversations

### Natural Move-Making
```
User: "I'll take the center"
AI: "Good choice! Playing X in position 5 (center). That's a strong opening move."

User: "How about the top right?"
AI: "Playing X in position 3 (top right corner). The AI is thinking..."
```

### Strategic Discussion
```
User: "What's my best move here?"
AI: "The optimal move is position 7. This blocks the AI's winning threat and sets up your own."

User: "Why is that better than position 2?"
AI: "Position 2 doesn't block the threat - the AI could win with position 9 on their next turn."
```

### Casual Interaction
```
User: "Surprise me with a move"
AI: "Random move suggestion: position 6! Sometimes unpredictable play can be educational."

User: "That's interesting, I hadn't considered that spot"
AI: "Position 6 creates some tactical possibilities. Want to try it or explore other options?"
```

This natural language system makes ChatTTT accessible to users regardless of their familiarity with formal game notation or command syntax. The AI adapts to user communication style and provides helpful, contextual responses.
"""
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
                
        except Exception as e:
            raise Exception(f"Error reading resource {uri}: {str(e)}")
    
    async def get_prompt_content(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get the content of a specific prompt."""
        try:
            if name == "strategy_coach":
                return await self._strategy_coach_prompt(arguments or {})
            elif name == "game_analyzer":
                return await self._game_analyzer_prompt(arguments or {})
            elif name == "learning_path":
                return await self._learning_path_prompt(arguments or {})
            else:
                raise ValueError(f"Unknown prompt: {name}")
        except Exception as e:
            raise Exception(f"Error getting prompt {name}: {str(e)}")
    
    async def _strategy_coach_prompt(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategy coaching prompt based on current game state."""
        board_state = arguments.get("board_state", None)
        skill_level = arguments.get("skill_level", "intermediate")
        focus_area = arguments.get("focus_area", "general")
        
        # Build context based on board state
        board_context = ""
        if board_state:
            board_context = f"Current board state: {board_state}\n"
            # Analyze current position
            empty_positions = [i+1 for i, cell in enumerate(board_state) if cell is None]
            x_positions = [i+1 for i, cell in enumerate(board_state) if cell == 'X']
            o_positions = [i+1 for i, cell in enumerate(board_state) if cell == 'O']
            
            board_context += f"Empty positions: {empty_positions}\n"
            board_context += f"X positions: {x_positions}\n"
            board_context += f"O positions: {o_positions}\n"
        
        prompt_text = f"""You are an expert tic-tac-toe coach providing personalized strategy guidance.

Player Information:
- Skill Level: {skill_level}
- Focus Area: {focus_area}

{board_context}

Instructions:
1. Analyze the current position if provided
2. Provide strategic advice appropriate for the {skill_level} level
3. Focus on {focus_area} aspects of play
4. Explain reasoning behind your recommendations
5. Suggest specific moves or patterns when relevant
6. Use encouraging and educational tone

Please provide comprehensive strategy coaching that helps the player improve their tic-tac-toe skills."""

        return {
            "description": f"Strategy coaching for {skill_level} player focusing on {focus_area}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        }
    
    async def _game_analyzer_prompt(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate game analysis prompt based on move history."""
        move_history = arguments.get("move_history", [])
        analysis_depth = arguments.get("analysis_depth", "detailed")
        
        if not move_history:
            raise ValueError("Move history is required for game analysis")
        
        # Convert move history to readable format
        moves_text = ""
        for i, move in enumerate(move_history):
            player = "X" if i % 2 == 0 else "O"
            moves_text += f"Move {i+1}: {player} plays position {move}\n"
        
        prompt_text = f"""You are an expert tic-tac-toe analyst providing detailed game review.

Game Information:
- Analysis Depth: {analysis_depth}
- Total Moves: {len(move_history)}

Move History:
{moves_text}

Analysis Instructions:
1. Review each move and evaluate its quality
2. Identify key turning points in the game
3. Highlight missed opportunities or mistakes
4. Explain strategic concepts demonstrated
5. Provide overall game assessment
6. Suggest improvements for future games

Analysis Level: {analysis_depth}
- Quick: Brief overview with key points
- Detailed: Move-by-move analysis with explanations
- Comprehensive: In-depth strategic discussion with variations

Please provide thorough game analysis that helps players learn from this game."""

        return {
            "description": f"{analysis_depth.title()} analysis of {len(move_history)}-move game",
            "messages": [
                {
                    "role": "user", 
                    "content": {
                        "type": "text",
                        "text": prompt_text
                    }
                }
            ]
        }
    
    async def _learning_path_prompt(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized learning path prompt."""
        current_level = arguments.get("current_level", "beginner")
        learning_goals = arguments.get("learning_goals", "improve overall play")
        
        prompt_text = f"""You are an expert tic-tac-toe instructor creating a personalized learning curriculum.

Student Information:
- Current Level: {current_level}
- Learning Goals: {learning_goals}

Curriculum Requirements:
1. Assess appropriate starting point for {current_level} player
2. Create structured learning progression
3. Include specific skills and concepts to master
4. Suggest practice exercises and drills
5. Provide milestones and progress indicators
6. Adapt to stated learning goals: {learning_goals}

Learning Path Structure:
- Foundational concepts (if needed)
- Core strategic principles 
- Tactical pattern recognition
- Advanced concepts (if appropriate)
- Practice recommendations
- Assessment methods

Please create a comprehensive learning path that efficiently guides the student from their current level toward mastery of tic-tac-toe strategy."""

        return {
            "description": f"Personalized learning path for {current_level} player",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text", 
                        "text": prompt_text
                    }
                }
            ]
        }
    
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
