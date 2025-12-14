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

# ============================
# GAME ENGINE
# ============================
class GameEngine:
    def __init__(self, p1, p2):
        self.board = Board()
        self.p1 = p1
        self.p2 = p2
        self.current = p1

    def switch(self):
        self.current = self.p1 if self.current is self.p2 else self.p2

    def make_move(self, col: int) -> Optional[int]:
        if col not in self.board.valid_moves():
            return None
        self.board.drop_piece(col, self.current.pid)
        winner = self.board.check_winner()
        if winner or self.board.is_full():
            return winner
        self.switch()
        return None

    def reset(self):
        self.board.reset()
        self.current = self.p1

# ============================
# Console board printing (Style 3 with row separators)
# ============================
def print_console_board(board: Board):
    # Top border
    print("+---" * COLS + "+")
    for r in range(ROWS):
        row_str = "|"
        for c in range(COLS):
            cell = board.grid[r][c]
            symbol = "."
            if cell == PLAYER1:
                symbol = "X"
            elif cell == PLAYER2:
                symbol = "O"
            row_str += f" {symbol} |"
        print(row_str)
        # Row separator
        print("+---" * COLS + "+")
    # Column numbers
    print("  " + "   ".join(str(c) for c in range(COLS)))

# ============================
# Run Console Mode (withdraw GUI, play, then restore)
# ============================
def run_console_mode(root: tk.Tk, app, mode: int, difficulty_depth: Optional[int]):
    """
    mode: 1 PvP, 2 PvAI, 3 AIvAI
    difficulty_depth: used for AI depth
    root: main Tk root (will be withdrawn and deiconified)
    app: instance of App (to show LauncherFrame after finish)
    """
    # hide GUI
    root.withdraw()
    try:
        # prepare players
        if mode == 1:
            p1 = HumanPlayer(1)
            p2 = HumanPlayer(2)
        elif mode == 2:
            p1 = HumanPlayer(1)
            depth = difficulty_depth if difficulty_depth is not None else 4
            p2 = AIPlayer(2, depth=depth)
        else:
            depth = difficulty_depth if difficulty_depth is not None else 4
            p1 = AIPlayer(1, depth=depth)
            p2 = AIPlayer(2, depth=depth)

        engine = GameEngine(p1, p2)

        print("\n=== Connect 4 — Console Mode ===\n")
        print("Board legend: X = Player1, O = Player2\n")
        print_console_board(engine.board)

        # main console loop
        while True:
            current = engine.current
            if isinstance(current, HumanPlayer):
                move = current.choose_move(engine.board)
                result_info = f"Turn played by Player {current.pid}"
            else:
                move = current.choose_move(engine.board)
                result_info = f"Turn played by AI Player {current.pid}"
            winner = engine.make_move(move)

            # print board and turn info
            print()
            print(result_info)
            print_console_board(engine.board)

            if winner:
                print(f"\nGame Over — Player {winner} wins!")
                break
            if engine.board.is_full():
                print("\nGame Over — Draw!")
                break

        input("\nPress Enter to return to GUI...")
    finally:
        # restore GUI and show launcher frame
        root.deiconify()
        app.show_frame("LauncherFrame")

# ============================
# GUI with Frame Switching
# ============================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4")
        self.resizable(False, False)
        self.geometry(f"{COLS*CELL_SIZE}x{ROWS*CELL_SIZE + 120}")  # leave room for controls
        # shared state
        self.mode = 2  # default PvAI
        self.difficulty_depth = 4
        self.engine: Optional[GameEngine] = None

        # frames
        self.frames = {}
        for F in (LauncherFrame, ModeFrame, DifficultyFrame, GameFrame):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("LauncherFrame")

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

    def prepare_engine(self):
        # create players based on mode and difficulty
        if self.mode == 1:  # PvP
            p1 = HumanPlayer(1)
            p2 = HumanPlayer(2)
        elif self.mode == 2:  # PvAI
            p1 = HumanPlayer(1)
            p2 = AIPlayer(2, depth=self.difficulty_depth)
        else:  # AIvAI
            p1 = AIPlayer(1, depth=self.difficulty_depth)
            p2 = AIPlayer(2, depth=self.difficulty_depth)
        self.engine = GameEngine(p1, p2)

# Launcher Frame
class LauncherFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Connect 4", font=("Arial", 20)).pack(pady=12)
        tk.Label(self, text="Choose Interface:", font=("Arial", 12)).pack(pady=6)

        btn_gui = tk.Button(self, text="Start (GUI)", width=20, command=lambda: controller.show_frame("ModeFrame"))
        btn_gui.pack(pady=6)

        # Console button: open popup to select mode/difficulty then run console mode
        btn_console = tk.Button(self, text="Start (Console)", width=20, command=self.launch_console_popup)
        btn_console.pack(pady=6)

        btn_quit = tk.Button(self, text="Quit", width=20, command=controller.destroy)
        btn_quit.pack(pady=6)

    def launch_console_popup(self):
        # simple Toplevel to ask mode/difficulty
        popup = tk.Toplevel(self)
        popup.title("Console Mode - Choose Mode")
        tk.Label(popup, text="Select Mode for Console:", font=("Arial", 12)).pack(padx=10, pady=8)

        def set_mode(m):
            popup.destroy()
            if m == 2:
                # ask difficulty
                self.ask_difficulty_console()
            else:
                # launch console directly
                self.controller.mode = m
                self.controller.difficulty_depth = 4
                run_console_mode(self.master, self.controller, m, None)

        tk.Button(popup, text="Player vs Player", width=25, command=lambda: set_mode(1)).pack(padx=10, pady=6)
        tk.Button(popup, text="Player vs AI", width=25, command=lambda: set_mode(2)).pack(padx=10, pady=6)
        tk.Button(popup, text="AI vs AI", width=25, command=lambda: set_mode(3)).pack(padx=10, pady=6)

        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)

    def ask_difficulty_console(self):
        popup = tk.Toplevel(self)
        popup.title("Choose Difficulty")
        tk.Label(popup, text="Choose Difficulty:", font=("Arial", 12)).pack(padx=10, pady=8)

        def set_diff(label):
            popup.destroy()
            mapping = {"Easy": 2, "Medium": 4, "Hard": 6}
            depth = mapping.get(label, 4)
            self.controller.mode = 2
            self.controller.difficulty_depth = depth
            run_console_mode(self.master, self.controller, 2, depth)

        tk.Button(popup, text="Easy (Depth 2)", width=25, command=lambda: set_diff("Easy")).pack(padx=10, pady=6)
        tk.Button(popup, text="Medium (Depth 4)", width=25, command=lambda: set_diff("Medium")).pack(padx=10, pady=6)
        tk.Button(popup, text="Hard (Depth 6)", width=25, command=lambda: set_diff("Hard")).pack(padx=10, pady=6)

        popup.transient(self)
        popup.grab_set()
        self.wait_window(popup)

# Mode Selection Frame
class ModeFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Select Game Mode", font=("Arial", 16)).pack(pady=10)
        tk.Button(self, text="Player vs Player", width=25, command=self.choose_pvp).pack(pady=6)
        tk.Button(self, text="Player vs AI", width=25, command=self.choose_pvai).pack(pady=6)
        tk.Button(self, text="AI vs AI", width=25, command=self.choose_aivai).pack(pady=6)
        tk.Button(self, text="Back", width=12, command=lambda: controller.show_frame("LauncherFrame")).pack(pady=8)

    def choose_pvp(self):
        self.controller.mode = 1
        self.controller.difficulty_depth = 4
        self.controller.prepare_engine()
        self.controller.show_frame("GameFrame")
        self.controller.frames["GameFrame"].start_game()

    def choose_pvai(self):
        self.controller.mode = 2
        # go to difficulty selection
        self.controller.show_frame("DifficultyFrame")

    def choose_aivai(self):
        self.controller.mode = 3
        self.controller.difficulty_depth = 4
        self.controller.prepare_engine()
        self.controller.show_frame("GameFrame")
        self.controller.frames["GameFrame"].start_game()

# Difficulty Frame
class DifficultyFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        tk.Label(self, text="Select Difficulty (Player vs AI)", font=("Arial", 14)).pack(pady=10)
        tk.Button(self, text="Easy (Depth 2)", width=25, command=lambda: self.choose("Easy")).pack(pady=6)
        tk.Button(self, text="Medium (Depth 4)", width=25, command=lambda: self.choose("Medium")).pack(pady=6)
        tk.Button(self, text="Hard (Depth 6)", width=25, command=lambda: self.choose("Hard")).pack(pady=6)
        tk.Button(self, text="Back", width=12, command=lambda: controller.show_frame("ModeFrame")).pack(pady=8)

    def choose(self, label):
        mapping = {"Easy": 2, "Medium": 4, "Hard": 6}
        self.controller.difficulty_depth = mapping.get(label, 4)
        self.controller.prepare_engine()
        self.controller.show_frame("GameFrame")
        self.controller.frames["GameFrame"].start_game()

# Game Frame
class GameFrame(tk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller
        self.canvas = tk.Canvas(self, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg="blue")
        self.canvas.pack(pady=(10,0))
        self.canvas.bind("<Button-1>", self.on_click)
        # bottom control frame
        ctrl = tk.Frame(self)
        ctrl.pack(fill="x", pady=6)
        self.status_label = tk.Label(ctrl, text="Status: Ready", anchor="w")
        self.status_label.pack(side="left", padx=6)
        tk.Button(ctrl, text="Restart", command=self.restart_game).pack(side="right", padx=6)
        tk.Button(ctrl, text="Back to Menu", command=self.back_to_menu).pack(side="right")
        # draw empty circles and keep ids
        self.cell_ids = [[None for _ in range(COLS)] for __ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c*CELL_SIZE + 5
                y1 = r*CELL_SIZE + 5
                x2 = x1 + CELL_SIZE - 10
                y2 = y1 + CELL_SIZE - 10
                cid = self.canvas.create_oval(x1, y1, x2, y2, fill=EMPTY_COLOR, tags=f"cell_{r}_{c}")
                self.cell_ids[r][c] = cid
        self.after_id = None

    def start_game(self):
        # engine is prepared by controller
        self.controller.prepare_engine()
        self.engine = self.controller.engine
        self.update_board()
        self.status_label.config(text="Status: Game started")
        # if AI to move first, schedule
        if isinstance(self.engine.current, AIPlayer):
            self.schedule_ai_move(300)

    def update_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                v = self.engine.board.grid[r][c]
                color = EMPTY_COLOR
                if v == PLAYER1: color = P1_COLOR
                elif v == PLAYER2: color = P2_COLOR
                self.canvas.itemconfig(self.cell_ids[r][c], fill=color)
        # remove any previous highlight outline
        for r in range(ROWS):
            for c in range(COLS):
                self.canvas.itemconfig(self.cell_ids[r][c], outline="black", width=1)

    def on_click(self, event):
        if not isinstance(self.engine.current, HumanPlayer):
            return
        col = event.x // CELL_SIZE
        if col not in self.engine.board.valid_moves():
            return
        winner = self.engine.make_move(col)
        self.update_board()
        if winner:
            self.handle_game_over()
            return
        # schedule AI if next
        if isinstance(self.engine.current, AIPlayer):
            self.schedule_ai_move(300)

    def schedule_ai_move(self, delay_ms):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(delay_ms, self.ai_move)

    def ai_move(self):
        if not isinstance(self.engine.current, AIPlayer):
            return
        col = self.engine.current.choose_move(self.engine.board)
        winner = self.engine.make_move(col)
        self.update_board()
        if winner:
            self.handle_game_over()
            return
        # if next is AI too, continue
        if isinstance(self.engine.current, AIPlayer):
            self.schedule_ai_move(300)

    def handle_game_over(self):
        # highlight winning four if exists
        coords = self.engine.board.winning_positions()
        if coords:
            for (r, c) in coords:
                self.canvas.itemconfig(self.cell_ids[r][c], outline="white", width=3)
                self.canvas.itemconfig(self.cell_ids[r][c], fill=HIGHLIGHT_COLOR)
        winner = self.engine.board.check_winner()
        if winner:
            self.status_label.config(text=f"Status: Player {winner} wins!")
            messagebox.showinfo("Game Over", f"Player {winner} wins!")
        else:
            self.status_label.config(text="Status: Draw")
            messagebox.showinfo("Game Over", "Draw!")
        # cancel any scheduled AI moves
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def restart_game(self):
        # restart with same players and depths
        self.controller.prepare_engine()
        self.engine = self.controller.engine
        self.update_board()
        self.status_label.config(text="Status: Restarted")
        if isinstance(self.engine.current, AIPlayer):
            self.schedule_ai_move(300)

    def back_to_menu(self):
        # cancel pending AI callbacks
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.controller.show_frame("ModeFrame")

# ============================
# Run App
# ============================
def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
