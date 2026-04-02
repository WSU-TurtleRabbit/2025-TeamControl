"""
Dispatcher GUI — a Tkinter-based graphical interface for sending robot
commands through the dispatcher queue.

Launch standalone:
    python -m TeamControl.dispatcher.gui

Or import and use programmatically:
    from TeamControl.dispatcher.gui import DispatcherGUI
    gui = DispatcherGUI(dispatch_queue)
    gui.run()
"""

import tkinter as tk
from tkinter import ttk, messagebox
from multiprocessing import Queue, Process, Event
from typing import Optional
import time

from TeamControl.network.robot_command import RobotCommand
from TeamControl.utils.yaml_config import Config
from TeamControl.dispatcher.dispatch import Dispatcher


# ──────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────
YELLOW_COLOUR = "#f5c542"
BLUE_COLOUR   = "#4287f5"
BG_COLOUR     = "#2b2b2b"
FG_COLOUR     = "#e0e0e0"
ENTRY_BG      = "#3c3c3c"
BTN_ACTIVE    = "#505050"
HEADER_FONT   = ("Segoe UI", 14, "bold")
LABEL_FONT    = ("Segoe UI", 10)
MONO_FONT     = ("Consolas", 10)


class DispatcherGUI:
    """Tkinter GUI that pushes ``(RobotCommand, runtime)`` tuples into the
    dispatcher queue, exactly the same way the rest of the system does."""

    def __init__(self, dispatch_q: Optional[Queue] = None, standalone: bool = False):
        self.dispatch_q = dispatch_q or Queue()
        self.standalone = standalone
        self.is_running: Event | None = None
        self.dispatcher_process: Optional[Process] = None
        self.sent_log: list[dict] = []

        # ── Load robot definitions from config ──────────────────
        self.config = Config()
        self.yellow_robots = self.config.yellow or {}
        self.blue_robots   = self.config.blue   or {}

        # ── Build the window ────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("TeamControl — Dispatcher GUI")
        self.root.configure(bg=BG_COLOUR)
        self.root.minsize(860, 660)
        self._build_ui()

    # ================================================================
    #  UI construction
    # ================================================================
    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_COLOUR)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        tk.Label(header, text="🤖  Dispatcher Control Panel",
                 font=HEADER_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(side="left")

        # Status indicator
        self.status_var = tk.StringVar(value="Queue mode")
        tk.Label(header, textvariable=self.status_var,
                 font=LABEL_FONT, bg=BG_COLOUR, fg="#8bc34a").pack(side="right")

        # ── Main paned area ─────────────────────────────────────
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL,
                              bg=BG_COLOUR, sashwidth=6, sashrelief=tk.FLAT)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        left = self._build_command_panel(main)
        right = self._build_log_panel(main)
        main.add(left, minsize=380)
        main.add(right, minsize=340)

        # ── Bottom bar ──────────────────────────────────────────
        bottom = tk.Frame(self.root, bg=BG_COLOUR)
        bottom.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self._build_bottom_bar(bottom)

    # ── Left: command entry ─────────────────────────────────────
    def _build_command_panel(self, parent) -> tk.Frame:
        frame = tk.LabelFrame(parent, text=" Send Command ", font=LABEL_FONT,
                               bg=BG_COLOUR, fg=FG_COLOUR, bd=1, relief="groove")

        # Team selector
        team_frame = tk.Frame(frame, bg=BG_COLOUR)
        team_frame.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(team_frame, text="Team:", font=LABEL_FONT,
                 bg=BG_COLOUR, fg=FG_COLOUR).pack(side="left")
        self.team_var = tk.StringVar(value="Yellow")
        for txt, val, colour in [("Yellow", "Yellow", YELLOW_COLOUR),
                                  ("Blue", "Blue", BLUE_COLOUR)]:
            rb = tk.Radiobutton(team_frame, text=txt, variable=self.team_var,
                                value=val, font=LABEL_FONT, bg=BG_COLOUR,
                                fg=colour, selectcolor=BG_COLOUR,
                                activebackground=BG_COLOUR, activeforeground=colour,
                                command=self._update_robot_dropdown)
            rb.pack(side="left", padx=8)

        # Robot selector
        robot_frame = tk.Frame(frame, bg=BG_COLOUR)
        robot_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(robot_frame, text="Robot:", font=LABEL_FONT,
                 bg=BG_COLOUR, fg=FG_COLOUR).pack(side="left")
        self.robot_combo = ttk.Combobox(robot_frame, state="readonly", width=28)
        self.robot_combo.pack(side="left", padx=(8, 0))
        self._update_robot_dropdown()

        # Separator
        ttk.Separator(frame, orient="horizontal").pack(fill="x", padx=10, pady=8)

        # ── Velocity / control sliders ──────────────────────────
        self.sliders: dict[str, tk.DoubleVar] = {}
        slider_defs = [
            ("vx",  "Velocity X (m/s)",      -0.5,  0.5, 0.0),
            ("vy",  "Velocity Y (m/s)",      -0.5,  0.5, 0.0),
            ("w",   "Angular vel ω (rad/s)", -1.0,  1.0, 0.0),
        ]
        for key, label, lo, hi, default in slider_defs:
            self._add_slider(frame, key, label, lo, hi, default)

        # ── Kick / Dribble toggles ──────────────────────────────
        toggle_frame = tk.Frame(frame, bg=BG_COLOUR)
        toggle_frame.pack(fill="x", padx=10, pady=5)

        self.kick_var = tk.IntVar(value=0)
        tk.Checkbutton(toggle_frame, text="Kick", variable=self.kick_var,
                       font=LABEL_FONT, bg=BG_COLOUR, fg=FG_COLOUR,
                       selectcolor=ENTRY_BG, activebackground=BG_COLOUR,
                       activeforeground=FG_COLOUR).pack(side="left", padx=(0, 20))

        self.dribble_var = tk.IntVar(value=0)
        tk.Checkbutton(toggle_frame, text="Dribble", variable=self.dribble_var,
                       font=LABEL_FONT, bg=BG_COLOUR, fg=FG_COLOUR,
                       selectcolor=ENTRY_BG, activebackground=BG_COLOUR,
                       activeforeground=FG_COLOUR).pack(side="left")

        # ── Runtime ─────────────────────────────────────────────
        rt_frame = tk.Frame(frame, bg=BG_COLOUR)
        rt_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(rt_frame, text="Runtime (s):", font=LABEL_FONT,
                 bg=BG_COLOUR, fg=FG_COLOUR).pack(side="left")
        self.runtime_var = tk.StringVar(value="3.0")
        tk.Entry(rt_frame, textvariable=self.runtime_var, width=8,
                 font=MONO_FONT, bg=ENTRY_BG, fg=FG_COLOUR,
                 insertbackground=FG_COLOUR, bd=1, relief="solid").pack(side="left", padx=8)

        # ── Buttons ─────────────────────────────────────────────
        btn_frame = tk.Frame(frame, bg=BG_COLOUR)
        btn_frame.pack(fill="x", padx=10, pady=(10, 10))

        send_btn = tk.Button(btn_frame, text="▶  Send Command",
                             font=("Segoe UI", 11, "bold"),
                             bg="#4caf50", fg="white", activebackground="#66bb6a",
                             relief="flat", cursor="hand2",
                             command=self._send_command)
        send_btn.pack(fill="x", ipady=6)

        sub_btns = tk.Frame(btn_frame, bg=BG_COLOUR)
        sub_btns.pack(fill="x", pady=(6, 0))
        tk.Button(sub_btns, text="Reset sliders", font=LABEL_FONT,
                  bg=ENTRY_BG, fg=FG_COLOUR, activebackground=BTN_ACTIVE,
                  relief="flat", command=self._reset_sliders).pack(side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(sub_btns, text="Stop robot", font=LABEL_FONT,
                  bg="#d32f2f", fg="white", activebackground="#e57373",
                  relief="flat", command=self._stop_robot).pack(side="left", expand=True, fill="x", padx=(3, 0))

        return frame

    def _add_slider(self, parent, key, label, lo, hi, default):
        row = tk.Frame(parent, bg=BG_COLOUR)
        row.pack(fill="x", padx=10, pady=3)

        var = tk.DoubleVar(value=default)
        self.sliders[key] = var

        tk.Label(row, text=label, font=LABEL_FONT, bg=BG_COLOUR,
                 fg=FG_COLOUR, width=22, anchor="w").pack(side="left")

        scale = tk.Scale(row, variable=var, from_=lo, to=hi, orient="horizontal",
                         resolution=0.01, length=180, bg=BG_COLOUR, fg=FG_COLOUR,
                         troughcolor=ENTRY_BG, highlightthickness=0,
                         font=("Consolas", 8))
        scale.pack(side="left", expand=True, fill="x")

        val_label = tk.Label(row, textvariable=var, font=MONO_FONT,
                             bg=BG_COLOUR, fg=FG_COLOUR, width=6)
        val_label.pack(side="right")

    # ── Right: per-robot command logs ──────────────────────────
    LOG_COLUMNS = ("time", "team", "id", "vx", "vy", "w", "kick", "drib", "rt")
    LOG_HEADERS = {
        "time": ("Time", 60),
        "team": ("Team", 50),
        "id":   ("ID", 30),
        "vx":   ("vx", 45),
        "vy":   ("vy", 45),
        "w":    ("ω", 45),
        "kick": ("K", 25),
        "drib": ("D", 25),
        "rt":   ("Run", 40),
    }

    def _build_log_panel(self, parent) -> tk.Frame:
        frame = tk.LabelFrame(parent, text=" Command Log ", font=LABEL_FONT,
                               bg=BG_COLOUR, fg=FG_COLOUR, bd=1, relief="groove")

        # Style tweaks for dark theme (set once)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                         background=ENTRY_BG, foreground=FG_COLOUR,
                         fieldbackground=ENTRY_BG, font=("Consolas", 9))
        style.configure("Treeview.Heading",
                         background="#404040", foreground=FG_COLOUR,
                         font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#555555")])
        style.configure("TNotebook", background=BG_COLOUR, borderwidth=0)
        style.configure("TNotebook.Tab", background=ENTRY_BG, foreground=FG_COLOUR,
                         padding=[8, 4], font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", "#505050")],
                  foreground=[("selected", FG_COLOUR)])

        # Tabbed notebook: "All" + one tab per robot
        self.log_notebook = ttk.Notebook(frame)
        self.log_notebook.pack(fill="both", expand=True, padx=6, pady=6)

        # dict mapping tab_key -> treeview  (tab_key = "all" | "Y0" | "B2" etc.)
        self.log_trees: dict[str, ttk.Treeview] = {}

        # "All" tab
        self._add_log_tab("All", "all")

        # Yellow robot tabs
        for name, info in self.yellow_robots.items():
            sid = info.get("shellID", "?")
            tab_key = f"Y{sid}"
            self._add_log_tab(f"Y {name} ({sid})", tab_key)

        # Blue robot tabs
        for name, info in self.blue_robots.items():
            sid = info.get("shellID", "?")
            tab_key = f"B{sid}"
            self._add_log_tab(f"B {name} ({sid})", tab_key)

        return frame

    def _add_log_tab(self, title: str, tab_key: str):
        """Create a scrollable Treeview inside a new notebook tab."""
        tab_frame = tk.Frame(self.log_notebook, bg=BG_COLOUR)
        self.log_notebook.add(tab_frame, text=title)

        tree = ttk.Treeview(tab_frame, columns=self.LOG_COLUMNS,
                             show="headings", height=18)
        for col, (heading, width) in self.LOG_HEADERS.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=width, anchor="center")

        scroll = ttk.Scrollbar(tab_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.log_trees[tab_key] = tree

    # ── Bottom bar ──────────────────────────────────────────────
    def _build_bottom_bar(self, parent):
        parent.columnconfigure(0, weight=1)

        if self.standalone:
            self.dispatch_btn_var = tk.StringVar(value="▶  Start Dispatcher")
            btn = tk.Button(parent, textvariable=self.dispatch_btn_var,
                            font=LABEL_FONT, bg="#1976d2", fg="white",
                            activebackground="#42a5f5", relief="flat",
                            command=self._toggle_dispatcher)
            btn.grid(row=0, column=0, sticky="w")

        tk.Button(parent, text="Clear Log", font=LABEL_FONT,
                  bg=ENTRY_BG, fg=FG_COLOUR, activebackground=BTN_ACTIVE,
                  relief="flat", command=self._clear_log).grid(row=0, column=1, sticky="e")

        self.queue_label = tk.StringVar(value="Queue size: 0")
        tk.Label(parent, textvariable=self.queue_label, font=("Consolas", 9),
                 bg=BG_COLOUR, fg="#888").grid(row=0, column=2, sticky="e", padx=(10, 0))

        # Periodic queue-size updater
        self._update_queue_size()

    # ================================================================
    #  Actions
    # ================================================================
    def _update_robot_dropdown(self):
        is_yellow = self.team_var.get() == "Yellow"
        robots = self.yellow_robots if is_yellow else self.blue_robots
        items = []
        for name, info in robots.items():
            sid = info.get("shellID", "?")
            items.append(f"{name}  (shell {sid})")
        self.robot_combo["values"] = items
        if items:
            self.robot_combo.current(0)

    def _get_selected_shell_id(self) -> int:
        text = self.robot_combo.get()
        # Format: "A  (shell 0)"
        try:
            return int(text.split("shell")[1].strip().rstrip(")"))
        except (IndexError, ValueError):
            raise ValueError("Select a robot first")

    def _send_command(self):
        try:
            shell_id = self._get_selected_shell_id()
            is_yellow = self.team_var.get() == "Yellow"
            vx  = self.sliders["vx"].get()
            vy  = self.sliders["vy"].get()
            w   = self.sliders["w"].get()
            kick    = self.kick_var.get()
            dribble = self.dribble_var.get()
            runtime = float(self.runtime_var.get())

            cmd = RobotCommand(
                robot_id=shell_id,
                vx=vx, vy=vy, w=w,
                kick=kick, dribble=dribble,
                isYellow=is_yellow,
            )
            self.dispatch_q.put((cmd, runtime))
            self._log_command(shell_id, is_yellow, vx, vy, w, kick, dribble, runtime)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _stop_robot(self):
        """Send an all-zeros command for 9999 s (effectively a hard stop)."""
        try:
            shell_id = self._get_selected_shell_id()
            is_yellow = self.team_var.get() == "Yellow"
            cmd = RobotCommand(robot_id=shell_id, vx=0, vy=0, w=0,
                               kick=0, dribble=0, isYellow=is_yellow)
            self.dispatch_q.put((cmd, 9999))
            self._log_command(shell_id, is_yellow, 0, 0, 0, 0, 0, 9999)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _reset_sliders(self):
        for var in self.sliders.values():
            var.set(0.0)
        self.kick_var.set(0)
        self.dribble_var.set(0)

    def _log_command(self, sid, is_yellow, vx, vy, w, kick, dribble, runtime):
        ts = time.strftime("%H:%M:%S")
        team = "Y" if is_yellow else "B"
        values = (
            ts, team, sid,
            f"{vx:.1f}", f"{vy:.1f}", f"{w:.1f}",
            kick, dribble, f"{runtime:.1f}"
        )
        # Insert into the "All" log
        self.log_trees["all"].insert("", 0, values=values)
        # Insert into the per-robot log
        robot_key = f"{team}{sid}"
        if robot_key in self.log_trees:
            self.log_trees[robot_key].insert("", 0, values=values)

    def _clear_log(self):
        for tree in self.log_trees.values():
            for item in tree.get_children():
                tree.delete(item)

    def _update_queue_size(self):
        try:
            size = self.dispatch_q.qsize()
        except NotImplementedError:
            size = "?"
        self.queue_label.set(f"Queue size: {size}")
        self.root.after(500, self._update_queue_size)

    # ── Standalone dispatcher toggle ────────────────────────────
    def _toggle_dispatcher(self):
        if self.dispatcher_process and self.dispatcher_process.is_alive():
            # Stop
            self.is_running.clear()
            self.dispatcher_process.join(timeout=3)
            self.dispatcher_process = None
            self.dispatch_btn_var.set("▶  Start Dispatcher")
            self.status_var.set("Dispatcher stopped")
        else:
            # Start
            self.is_running = Event()
            self.is_running.set()
            self.dispatcher_process = Process(
                target=Dispatcher.run_worker,
                args=(self.is_running, None, self.dispatch_q, self.config),
            )
            self.dispatcher_process.start()
            self.dispatch_btn_var.set("⏹  Stop Dispatcher")
            self.status_var.set("Dispatcher running")

    # ================================================================
    #  Lifecycle
    # ================================================================
    def run(self):
        """Start the Tk main loop (blocking)."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.dispatcher_process and self.dispatcher_process.is_alive():
            self.is_running.clear()
            self.dispatcher_process.join(timeout=3)
        self.root.destroy()


# ──────────────────────────────────────────────────────────────────
#  Standalone entry-point
# ──────────────────────────────────────────────────────────────────
def main():
    gui = DispatcherGUI(standalone=True)
    gui.run()


if __name__ == "__main__":
    main()
