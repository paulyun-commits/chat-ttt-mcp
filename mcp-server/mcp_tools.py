from typing import Any, Dict, List, Optional
import os
from pathlib import Path
from mcp.types import Tool, TextContent, CallToolResult, Resource, Prompt
from agent import TicTacToeAgent

class MCPTools:
    def __init__(self):
        self.agent = TicTacToeAgent()
        self.resources_dir = Path(__file__).parent / "resources"
    
    def _load_resource_file(self, filename: str) -> str:
        """Load resource content from a file."""
        file_path = self.resources_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Resource file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
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
            resource_mapping = {
                "chatttp://game-rules": "game-rules.md",
                "chatttp://strategy-guide": "strategy-guide.md", 
                "chatttp://ai-algorithms": "ai-algorithms.md",
                "chatttp://commands-reference": "commands-reference.md"
            }
            
            if uri in resource_mapping:
                return self._load_resource_file(resource_mapping[uri])
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
