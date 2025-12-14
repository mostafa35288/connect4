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