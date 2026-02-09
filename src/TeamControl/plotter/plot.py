from TeamControl.SSL.vision.field import FieldLines, Vector2f
import matplotlib.pyplot as plt
from time import time
import numpy as np
import math
import time

# typing : 
from multiprocessing.synchronize import Event


# ================= FIELD CONSTANTS (mm) =================
line_thickness = 1.0

length = 4500.0          # half field length
width = 3000.0           # half field width
margin = 300.0

penalty_width = 1000.0
center_circle = 500.0

outer_length = length + margin
outer_width = width + margin
arrow_len = 300.0

def line(x1, y1, x2, y2):
    """Create a field line using SSL FieldLines"""
    return FieldLines("", Vector2f(x1, y1), Vector2f(x2, y2), line_thickness)


# ================= PLOTTER =================
class Plotter:
    def __init__(self, enable=True):
        self.enable = enable
        if not self.enable:
            return
        
        plt.ion() # interactive mode on

        self.fig, self.ax = plt.subplots(figsize=(10, 7))

        # objects that change every frame
        self.dynamic = []

        # persistent objects
        self.targets = []
        self.lines = []

        # draw static field once
        self._draw_field()

    # ================= FIELD =================
    def _draw_field(self):
        ax = self.ax

        # prevent redrawing field
        if hasattr(ax, "field_drawn"):
            return

        # ---- green background (field + margin) ----
        ax.add_patch(
            plt.Rectangle(
                (-outer_length, -outer_width),
                2 * outer_length,
                2 * outer_width,
                color="green",
                zorder=0
            )
        )

        # ---- field lines ----
        field = [
            # main field
            line(-length,  width,  length,  width),   # top
            line(-length, -width,  length, -width),   # bottom
            line(-length, -width, -length,  width),   # left
            line( length, -width,  length,  width),   # right

            # center
            line(0.0, -width, 0.0, width),
            line(-length, 0.0, length, 0.0),

            # left penalty box
            line(-length,  penalty_width, -length + penalty_width,  penalty_width),
            line(-length, -penalty_width, -length + penalty_width, -penalty_width),
            line(-length + penalty_width, -penalty_width,
                 -length + penalty_width,  penalty_width),

            # right penalty box
            line(length,  penalty_width, length - penalty_width,  penalty_width),
            line(length, -penalty_width, length - penalty_width, -penalty_width),
            line(length - penalty_width, -penalty_width,
                 length - penalty_width,  penalty_width),

            # left goal
            line(-length-200.0,  500.0, -length,  500.0),
            line(-length-200.0, -500.0, -length, -500.0),
            line(-length-200.0,  500.0, -length-200.0, -500.0),

            # right goal
            line(length,  500.0, length+200.0,  500.0),
            line(length, -500.0, length+200.0, -500.0),
            line(length+200.0, 500.0, length+200.0, -500.0),
        ]

        # draw field lines
        for l in field:
            ax.plot(
                [l.p1.x, l.p2.x],
                [l.p1.y, l.p2.y],
                linewidth=l.thickness,
                color="white"
            )

        # center circle
        ax.add_patch(
            plt.Circle(
                (0, 0),
                center_circle,
                fill=False,
                linewidth=line_thickness,
                color="white"
            )
        )

        ax.set_aspect("equal")
        ax.axis("off")

        ax.field_drawn = True

    # ================= UPDATE ================= 
    def update(self, robots_yellow=None, robots_blue=None, ball=None):
        if not self.enable:
            return

        self._clear_dynamic()

        if robots_yellow:
            self._draw_robots(robots_yellow)

        if robots_blue:
            self._draw_robots(robots_blue, team_color="blue")

        if ball:
            self.dynamic.append(
                self.ax.scatter(
                    ball[0],
                    ball[1],
                    s=70,
                    c="orange",
                    label="Ball",
                    zorder=5 # make it appear above the field
                )
            )

        plt.pause(0.001)
        

    # ================= ROBOTS =================
    def _draw_robots(self, robots, team_color="yellow"):
        if team_color == "yellow":
            base_color="yellow"
        elif team_color == "blue":
            base_color="blue"

        for r in robots:
            """
            r = (x, y, theta, id)
            """
            x, y, theta, rid = r

            body = self.ax.scatter(
                x,
                y,
                s=70,
                c=base_color,
                edgecolors="black",
                zorder=4
            )

            arrow = self.ax.arrow(
                x,
                y,
                math.cos(theta) * 300.0,
                math.sin(theta) * 300.0,
                head_width=80,
                length_includes_head=True,
                color=base_color,
                zorder=5
            )
            
            # draw robot ID so it does not overlap with arrow
            offset_x = -math.sin(theta) * 200.0
            offset_y =  math.cos(theta) * 200.0
            
            label = self.ax.text(

                x + offset_x, 
                y + offset_y,     
                str(rid),        # text is the robot ID
                color="black",   # text color
                fontsize=12,
                fontweight="bold",
                ha="center",     # horizontally centered
                va="center",     # vertically centered
                zorder=6
            )

            self.dynamic.extend([body, arrow, label])

    # ================= TARGETS =================
    def set_target(self, *points):
        if not self.enable:
            return

        for p in points:
            t = self.ax.scatter(
                p[0],
                p[1],
                marker="x",
                c="red",
                label="Target",
                zorder=6
            )
            self.targets.append(t)

    # ================= LINES =================
    def add_line(self, A, B):
        if not self.enable:
            return

        line_obj, = self.ax.plot(
            [A[0], B[0]],
            [A[1], B[1]],
           "r--",
            zorder=3
        )
        self.lines.append(line_obj)

    # ================= BEST FIT =================
    def do_line_of_best_fit(self, points):
        if not self.enable or len(points) < 2:
            return

        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])

        m, c = np.polyfit(x, y, 1)
        y_fit = m * x + c

        line_obj, = self.ax.plot(
            x,
            y_fit,
            "y--",
            linewidth=2,
            zorder=3
        )

        self.lines.append(line_obj)

    # ================= UTILS =================
    def _clear_dynamic(self):
        for obj in self.dynamic:
            obj.remove()
        self.dynamic.clear()

    def clear_all(self):
        for obj in self.dynamic + self.targets + self.lines:
            obj.remove()
        self.dynamic.clear()
        self.targets.clear()
        self.lines.clear()

    def set_enable(self, enable: bool):
        """Start / stop ongoing graphing"""
        self.enable = enable


def run_plotter(is_running:Event, world_model):
    """
    This will run inside its own process.
    Continuously fetch data from the world model and update the plot.
    """
    w = world_model
    plotter = Plotter(enable=True)
    
    plt.show(block=False) 

    while is_running.is_set():
        try:
            frame = w.get_latest_frame()  # fetch live data

            if frame is None:
                # time.sleep(0.05)
                continue

            # prepare robot lists
            robots_yellow = [(r.x, r.y, r.o, r.id) for r in frame.robots_yellow] if frame.robots_yellow else []
            robots_blue   = [(r.x, r.y, r.o, r.id) for r in frame.robots_blue] if frame.robots_blue else []

            # ball
            ball = (frame.ball.x, frame.ball.y) if frame.ball else None

            # update the plot
            plotter.update(robots_yellow, robots_blue, ball)

            plt.pause(0.01)  # small delay to reduce CPU usage
        except KeyboardInterrupt:
            break
    print("Plotter exited")

    