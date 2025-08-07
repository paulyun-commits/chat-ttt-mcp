# ChatTTT Game Rules and Interface Guide

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
