import time
import random
from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand
from TeamControl.ball.send_ball_grsim import send_ball_to_grsim
from TeamControl.ball.ball_spawner import BallSpawner

# Ball spawner parameters
DIVISION = 'B'          # 'A' or 'B'

# grSim connection parameters
SIM_IP = "127.0.0.1"
CMD_LISTEN_PORT = 20011

def competition_example_process(wm) -> None:
    # Initialize match standing
    goal_count_blue = 0
    goal_count_yellow = 0

    # Initialize grSim command sender
    sender_yellow = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=True)
    sender_blue = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=False)

    # Initialize world model version
    version = 0

    # Initialize BallSpawner
    spawner = BallSpawner(
        division=DIVISION
    )

    while True:
        # Update the world model when new frame is available
        if version < wm.get_version():
            version = wm.get_version()

            frame = wm.get_latest_frame()
            if frame is None:
                continue

            if frame.ball is None:
                continue

            try:
                robots_yellow = wm.get_our_robots(True)
                robots_blue = wm.get_our_robots(False)
                ball_pos = wm.get_latest_frame().ball.position

            except (AttributeError, KeyError, IndexError):
                continue

        elif version == 0:
            continue


        # --- IMPLEMENT YOUR TEAM STRATEGY HERE ---



        # ------------   CHECK FOR GOAL (DO NOT CHANGE)  ------------
        # Check if the ball crossed the goal line and is within the goal posts
        goal_y_min = -spawner.goal_width / 2
        goal_y_max = spawner.goal_width / 2
        if (ball_pos[0] >= spawner.goal_line_x and goal_y_min <=
                ball_pos[1] <= goal_y_max):
            goal_count_blue += 1
            print(f"Blue Team scored a GOAL !!!!!")
            print(f"Blue Team Goals: {goal_count_blue}")
            print(f"Yellow Team Goals: {goal_count_yellow}")
            spawn_ball_randomly_in_the_middle()

        elif (ball_pos[0] <= -spawner.goal_line_x and goal_y_min <=
                ball_pos[1] <= goal_y_max):
            goal_count_yellow += 1
            print(f"Yellow Team scored a GOAL !!!!!")
            print(f"Yellow Team Goals: {goal_count_yellow}")
            print(f"Blue Team Goals: {goal_count_blue}")
            spawn_ball_randomly_in_the_middle()

        # ---- SPAWN THE BALL IN THE MIDDLE OF THE FIELD (DO NOT CHANGE) ----
        elif not spawner.is_ball_in_field(ball_pos):
            spawn_ball_randomly_in_the_middle()

def spawn_ball_randomly_in_the_middle():
    x = random.uniform(-0.5, 0.5)
    y = random.uniform(-0.5, 0.5)
    send_ball_to_grsim(x, y, 0, 0)
    time.sleep(0.1)
