import tkinter as tk
from tkinter import messagebox
import math
from typing import List, Tuple, Optional

# ============================
# CONSTANTS
# ============================
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
CELL_SIZE = 80
HIGHLIGHT_COLOR = "green"
P1_COLOR = "red"
P2_COLOR = "yellow"
EMPTY_COLOR = "white"



# ============================
# MINIMAX with Alpha-Beta
# ============================
class Minimax:
    def best_move(self, board: Board, depth: int, player: int) -> int:
        best_score = -math.inf
        best_col = board.valid_moves()[0]
        for col in sorted(board.valid_moves(), key=lambda x: abs(x - 3)):
            b = board.copy()
            b.drop_piece(col, player)
            score = self._minimax(b, depth - 1, -math.inf, math.inf, False, player)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

    def _minimax(self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool, player: int) -> int:
        winner = board.check_winner()
        if depth == 0 or winner or board.is_full():
            if winner == player:
                return 1_000_000
            elif winner is not None and winner != player:
                return -1_000_000
            else:
                return board.score_position(player)
        valid = board.valid_moves()
        ordered = sorted(valid, key=lambda c: abs(c - 3))
        if maximizing:
            value = -math.inf
            for col in ordered:
                b = board.copy()
                b.drop_piece(col, player)
                value = max(value, self._minimax(b, depth - 1, alpha, beta, False, player))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            opp = PLAYER1 if player == PLAYER2 else PLAYER2
            for col in ordered:
                b = board.copy()
                b.drop_piece(col, opp)
                value = min(value, self._minimax(b, depth - 1, alpha, beta, True, player))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

# ============================
# PLAYERS
# ============================
class HumanPlayer:
    def __init__(self, pid: int):
        self.pid = pid

    def choose_move(self, board: Board) -> int:
        # Console fallback (used in Console mode)
        while True:
            try:
                col = int(input(f"Player {self.pid} turn. Choose a column {board.valid_moves()}: "))
                if col in board.valid_moves():
                    return col
                print("Invalid column, try again.")
            except ValueError:
                print("Please enter an integer column.")

class AIPlayer:
    def __init__(self, pid: int, depth: int = 4):
        self.pid = pid
        self.depth = depth
        self.ai = Minimax()

    def choose_move(self, board: Board) -> int:
        # Non-blocking note: Minimax is CPU-bound; keep depth moderate
        print(f"AI (P{self.pid}) thinking (depth={self.depth})...")
        return self.ai.best_move(board, self.depth, self.pid)
