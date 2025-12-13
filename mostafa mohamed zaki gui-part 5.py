
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
