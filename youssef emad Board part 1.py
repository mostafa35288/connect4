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
# BOARD
# ============================
class Board:
    def __init__(self):
        self.grid: List[List[int]] = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self.last_move: Optional[Tuple[int, int]] = None

    def copy(self):
        b = Board()
        b.grid = [row[:] for row in self.grid]
        b.last_move = self.last_move
        return b

    def reset(self):
        self.__init__()

    def valid_moves(self):
        return [c for c in range(COLS) if self.grid[0][c] == EMPTY]

    def drop_piece(self, col, player):
        if col < 0 or col >= COLS or self.grid[0][col] != EMPTY:
            return False
        for r in range(ROWS - 1, -1, -1):
            if self.grid[r][col] == EMPTY:
                self.grid[r][col] = player
                self.last_move = (r, col)
                return True
        return False

    def is_full(self):
        return all(self.grid[0][c] != EMPTY for c in range(COLS))

    def check_winner(self) -> Optional[int]:
        """Return winner id or None."""
        for r in range(ROWS):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                if v != EMPTY and all(self.grid[r][c + i] == v for i in range(4)):
                    return v
        for c in range(COLS):
            for r in range(ROWS - 3):
                v = self.grid[r][c]
                if v != EMPTY and all(self.grid[r + i][c] == v for i in range(4)):
                    return v
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                if v != EMPTY and all(self.grid[r + i][c + i] == v for i in range(4)):
                    return v
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                if v != EMPTY and all(self.grid[r - i][c + i] == v for i in range(4)):
                    return v
        return None

    def winning_positions(self) -> Optional[List[Tuple[int,int]]]:
        """Return list of 4 coords if there's a winning four, else None."""
        for r in range(ROWS):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                coords = [(r, c + i) for i in range(4)]
                if v != EMPTY and all(self.grid[rr][cc] == v for rr, cc in coords):
                    return coords
        for c in range(COLS):
            for r in range(ROWS - 3):
                v = self.grid[r][c]
                coords = [(r + i, c) for i in range(4)]
                if v != EMPTY and all(self.grid[rr][cc] == v for rr, cc in coords):
                    return coords
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                coords = [(r + i, c + i) for i in range(4)]
                if v != EMPTY and all(self.grid[rr][cc] == v for rr, cc in coords):
                    return coords
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                v = self.grid[r][c]
                coords = [(r - i, c + i) for i in range(4)]
                if v != EMPTY and all(self.grid[rr][cc] == v for rr, cc in coords):
                    return coords
        return None

    # Heuristic helpers
    def evaluate_window(self, window: List[int], player: int) -> int:
        score = 0
        opp = PLAYER1 if player == PLAYER2 else PLAYER2
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(player) == 2 and window.count(EMPTY) == 2:
            score += 2
        if window.count(opp) == 3 and window.count(EMPTY) == 1:
            score -= 4
        return score

    def score_position(self, player: int) -> int:
        score = 0
        # center column control
        center = [self.grid[r][COLS // 2] for r in range(ROWS)]
        score += center.count(player) * 3
        # horizontal
        for r in range(ROWS):
            row_array = self.grid[r]
            for c in range(COLS - 3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, player)
        # vertical
        for c in range(COLS):
            col_array = [self.grid[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, player)
        # pos diag
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [self.grid[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player)
        # neg diag
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [self.grid[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, player)
        return score
