import json
from typing import Any, Dict, List, Optional
from pathlib import Path
from mcp.types import Tool, TextContent, CallToolResult, Resource, Prompt
from agent import TicTacToeAgent

class MCPTools:
    def __init__(self):
        self.agent = TicTacToeAgent()
        self.tools_dir = Path(__file__).parent / "tools"
        self.resources_dir = Path(__file__).parent / "resources"
        self.prompts_dir = Path(__file__).parent / "prompts"
        
    def _load_tool_config(self, filename: str) -> Dict[str, Any]:
        """Load tool configuration from a JSON file."""
        file_path = self.tools_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Tool config file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_resource_file(self, filename: str) -> str:
        """Load resource content from a file."""
        file_path = self.resources_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Resource file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_resource_config(self) -> Dict[str, Any]:
        """Load resource configuration from the single resources-config.json file."""
        config_file = self.resources_dir / "resources-config.json"
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
    
    def _load_prompt_template(self, template_filename: str) -> str:
        """Load prompt template from a text file."""
        file_path = self.prompts_dir / template_filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
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
        
        # Load resources from the single resources-config.json file
        if not self.resources_dir.exists():
            print(f"Warning: Resource directory not found at {self.resources_dir}")
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
        """Return list of available MCP prompts loaded from merged configuration file."""
        prompts = []
        
        # Load from the merged prompts-config.json file
        if not self.prompts_dir.exists():
            print(f"Warning: Prompts directory not found at {self.prompts_dir}")
            return prompts
            
        config_file = self.prompts_dir / "prompts-config.json"
        if not config_file.exists():
            print(f"Warning: Prompts config file not found at {config_file}")
            return prompts
            
        try:
            config = self._load_prompt_config("prompts-config.json")
            for prompt_config in config.get("prompts", []):
                prompt = Prompt(
                    name=prompt_config["name"],
                    description=prompt_config["description"],
                    arguments=prompt_config["arguments"]
                )
                prompts.append(prompt)
        except Exception as e:
            print(f"Warning: Failed to load prompts config: {e}")
                
        return prompts

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

    async def get_resource_content(self, uri: str):
        """Get the content of a specific resource."""
        try:
            # Build resource mapping dynamically from the single resources-config.json file
            resource_mapping = {}
            
            if self.resources_dir.exists():
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

# Tool Handlers

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

# Prompt Handlers

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
        
        # Load prompt template from file
        prompt_template = self._load_prompt_template("templates/strategy_coach.txt")
        prompt_text = prompt_template.format(
            skill_level=skill_level,
            focus_area=focus_area,
            board_context=board_context
        )

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
        
        # Load prompt template from file
        prompt_template = self._load_prompt_template("templates/game_analyzer.txt")
        prompt_text = prompt_template.format(
            analysis_depth=analysis_depth,
            total_moves=len(move_history),
            moves_text=moves_text
        )

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
        
        # Load prompt template from file
        prompt_template = self._load_prompt_template("templates/learning_path.txt")
        prompt_text = prompt_template.format(
            current_level=current_level,
            learning_goals=learning_goals
        )

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
