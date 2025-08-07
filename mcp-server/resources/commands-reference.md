# ChatTTT Natural Language Interface Examples

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
