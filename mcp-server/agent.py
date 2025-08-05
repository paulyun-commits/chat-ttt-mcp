from typing import List, Optional
import random

class TicTacToeAgent:
    def __init__(self):
        pass

    def new_game(self) -> int:
        print("MCP-TicTacToeAgent: new_game")
        return 1

    def best_move(self, board: List[Optional[str]], player: str, game_over: bool = False, winner: Optional[str] = None) -> int:
        print("MCP-TicTacToeAgent: best_move", player, board)
        if game_over: return -1

        valid_moves = [i for i, cell in enumerate(board) if cell is None]
        if not valid_moves: return -1

        best_score = float('-inf')
        best_move_idx = valid_moves[0]
        
        for move in valid_moves:
            # Make the move
            board_copy = board.copy()
            board_copy[move] = player
            
            # Get the score for this move
            score = self._minimax(board_copy, False, player)
            
            # If this move is better, save it
            if score > best_score:
                best_score = score
                best_move_idx = move
        
        return best_move_idx + 1  # Convert to 1-based indexing

    def random_move(self, board: List[Optional[str]], player: str, game_over: bool = False, winner: Optional[str] = None) -> int:
        print("MCP-TicTacToeAgent: random_move", player, board)
        if game_over: return -1

        valid_moves = [i for i, cell in enumerate(board) if cell is None]
        if not valid_moves: return -1

        return random.choice(valid_moves) + 1  # Convert to 1-based indexing

    def play_move(self, board: List[Optional[str]], position: int, player: str) -> int:
        print("MCP-TicTacToeAgent: play_move", player, board)
        if position < 1 or position > 9: return -1
        if board[position - 1] is not None: return -1
        return position

    def _minimax(self, board: List[Optional[str]], is_maximizing: bool, ai_player: str) -> int:
        winner = self._check_winner(board)
        
        # Terminal states
        if winner == ai_player:  return 1  # Win
        elif winner is not None: return -1 # Loss
        elif None not in board:  return 0  # Tie
        
        opponent = 'X' if ai_player == 'O' else 'O'
        
        if is_maximizing:
            best_score = float('-inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = ai_player
                    score = self._minimax(board, False, ai_player)
                    board[i] = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = opponent
                    score = self._minimax(board, True, ai_player)
                    board[i] = None
                    best_score = min(score, best_score)
            return best_score

    def _check_winner(self, board: List[Optional[str]]) -> Optional[str]:
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
