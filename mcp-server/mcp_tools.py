from typing import Any, Dict, List, Optional
import os
import json
from pathlib import Path
from mcp.types import Tool, TextContent, CallToolResult, Resource, Prompt
from agent import TicTacToeAgent

class MCPTools:
    def __init__(self):
        self.agent = TicTacToeAgent()
        self.resources_dir = Path(__file__).parent / "resources"
        self.resource_config_dir = self.resources_dir / "config"
        self.tools_dir = Path(__file__).parent / "tools"
        self.prompts_dir = Path(__file__).parent / "prompts"
    
    def _load_resource_file(self, filename: str) -> str:
        """Load resource content from a file."""
        file_path = self.resources_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Resource file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_tool_config(self, filename: str) -> Dict[str, Any]:
        """Load tool configuration from a JSON file."""
        file_path = self.tools_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Tool config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_resource_config(self) -> Dict[str, Any]:
        """Load resource configuration from the single resources.json file."""
        config_file = self.resource_config_dir / "resources.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Resource config file not found: {config_file}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_prompt_config(self, filename: str) -> Dict[str, Any]:
        """Load prompt configuration from a JSON file."""
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_tools(self) -> List[Tool]:
        """Return list of available MCP tools loaded from configuration files."""
        tools = []
        
        # Automatically discover all JSON files in the tools directory
        if not self.tools_dir.exists():
            print(f"Warning: Tools directory not found at {self.tools_dir}")
            return tools
            
        for tool_file in self.tools_dir.glob("*.json"):
            try:
                config = self._load_tool_config(tool_file.name)
                tool = Tool(
                    name=config["name"],
                    description=config["description"],
                    inputSchema=config["inputSchema"]
                )
                tools.append(tool)
            except Exception as e:
                print(f"Warning: Failed to load tool config from {tool_file.name}: {e}")
                
        return tools
    
    def get_resources(self) -> List[Resource]:
        """Return list of available MCP resources loaded from configuration file."""
        resources = []
        
        # Load resources from the single resources.json file
        if not self.resource_config_dir.exists():
            print(f"Warning: Resource config directory not found at {self.resource_config_dir}")
            return resources
            
        try:
            config = self._load_resource_config()
            resource_configs = config.get("resources", [])
            
            for resource_config in resource_configs:
                try:
                    resource = Resource(
                        uri=resource_config["uri"],
                        name=resource_config["name"],
                        description=resource_config["description"],
                        mimeType=resource_config["mimeType"]
                    )
                    resources.append(resource)
                except Exception as e:
                    print(f"Warning: Failed to create resource from config: {e}")
                    
        except Exception as e:
            print(f"Warning: Failed to load resource config: {e}")
                
        return resources
    
    def get_prompts(self) -> List[Prompt]:
        """Return list of available MCP prompts loaded from configuration files."""
        prompts = []
        
        # Automatically discover all JSON files in the prompts directory
        if not self.prompts_dir.exists():
            print(f"Warning: Prompts directory not found at {self.prompts_dir}")
            return prompts
            
        for prompt_file in self.prompts_dir.glob("*.json"):
            try:
                config = self._load_prompt_config(prompt_file.name)
                prompt = Prompt(
                    name=config["name"],
                    description=config["description"],
                    arguments=config["arguments"]
                )
                prompts.append(prompt)
            except Exception as e:
                print(f"Warning: Failed to load prompt config from {prompt_file.name}: {e}")
                
        return prompts
    
    async def get_resource_content(self, uri: str):
        """Get the content of a specific resource."""
        try:
            # Build resource mapping dynamically from the single resources.json file
            resource_mapping = {}
            
            if self.resource_config_dir.exists():
                try:
                    config = self._load_resource_config()
                    resource_configs = config.get("resources", [])
                    
                    for resource_config in resource_configs:
                        resource_mapping[resource_config["uri"]] = resource_config["filename"]
                        
                except Exception as e:
                    print(f"Warning: Failed to load resource config: {e}")
            
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
