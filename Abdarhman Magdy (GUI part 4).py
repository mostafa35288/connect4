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
