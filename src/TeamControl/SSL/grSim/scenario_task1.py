"""
sandbox_process.py

Example sandbox process for sending movement commands to a robot in grSim.

This script demonstrates how to:
    1. Initialize a grSim sender.
    2. Continuously read the world model (wm) for robot and ball positions.
    3. Compute velocity commands toward a target using RobotMovement.
    4. Send RobotCommand packets to grSim.
"""
import time
import random

from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand
from TeamControl.robot.movement_to_radius import RobotMovement
from TeamControl.ball.send_ball_grsim import send_ball_to_grsim


def sandbox_process(wm) -> None:
    """
    Main loop for controlling a single robot toward a target in a simulated environment.

    Args:
        wm: WorldModel object that provides robot and ball positions via:
            - wm.get_version()
            - wm.get_yellow_robots()
            - wm.get_latest_frame()

    Behavior:
        - Continuously monitors the world model version to detect updates.
        - Reads the position of the specified robot and the ball.
        - Computes velocities (vx, vy) to move the robot toward the ball.
        - Sends the commands to grSim using a UDP sender.
    """
    # grSim connection parameters
    SIM_IP = "127.0.0.1"
    CMD_LISTEN_PORT = 20011
    IS_YELLOW = True
    ROBOT_ID = 0

    # Initialize grSim command sender
    sender = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=IS_YELLOW)

    # Track world model
    version = 0
    robot_pos = (0, 0, 0)
    ball_pos = (0, 0)
    prev_ball_pos = (-1, -1)

    # Goalpost cooridnates for agent (it seems that when spawning the boal
    # the coordinates are different)
    goalpost_x = 4200
    goalpost_y = 0

    # Ball initial settings in mm
    ball_spawn = (0, 0)
    ball_velocity = (4, 0)  # m/s

    # Spawn ball initially
    send_ball_to_grsim(x=ball_spawn[0], y=ball_spawn[1], vx=ball_velocity[0],
                       vy=ball_velocity[1])


    last_time = time.time()

    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # Update world model when new frame is available
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=IS_YELLOW,
                                                 robot_id=ROBOT_ID)
                robot_pos = robot_obj.position

                prev_ball_pos = ball_pos
                ball_pos = wm.get_latest_frame().ball.position

            except Exception:
                robot_pos = (0, 0, 0)
                prev_ball_pos = (-1, -1)
                ball_pos = (0, 0)

        # The goalkeeper should be always near the goalpost
        if robot_pos[0] < 4100 or robot_pos[0] > 4300:
            vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos,
                                             target=(goalpost_x, goalpost_y))
            cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=0,
                               dribble=0)
            sender.send_command(cmd)

        else:
            # intercept the ball
            ball_target_y = calculate_ball_trajectory(ball_pos,
                                                    prev_ball_pos, goalpost_x)
            if ball_target_y is not None:
                vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos,
                                                 target=(goalpost_x, ball_target_y))
                cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=0,
                                   dribble=0)
                sender.send_command(cmd)


        # If ball is out of bounds or idle, respawn it
        if (is_ball_idle(ball_pos, prev_ball_pos) or
                not is_ball_in_field(ball_pos)):
            if random.random() < 0.5:
                x, y, vx, vy = shoot_at_random_target()
            else:
                x, y, vx, vy = shoot_at_goal()

            send_ball_to_grsim(x, y, vx, vy)
            prev_ball_pos = ball_pos
            ball_pos = (x , y)



def is_ball_idle(current_ball_pos, prev_ball_pos):
    ball_x, ball_y = current_ball_pos
    prev_ball_x, prev_ball_y = prev_ball_pos
    if ball_x == 0:
        return False
    return abs(ball_x - prev_ball_x) + abs(ball_y - prev_ball_y) < 0.2

def is_ball_in_field(current_ball_pos):
    # These are the dimensions of division B in grSim
    FIELD_X_MIN, FIELD_X_MAX = -4400, 4400
    FIELD_Y_MIN, FIELD_Y_MAX = -3000, 3000

    ball_x, ball_y = current_ball_pos
    return (FIELD_X_MIN <= ball_x <= FIELD_X_MAX and
            FIELD_Y_MIN <= ball_y <= FIELD_Y_MAX)

def calculate_ball_trajectory(current_ball_pos, prev_ball_pos, goalxpos):
    ball_x, ball_y = current_ball_pos
    prev_ball_x, prev_ball_y = prev_ball_pos

    # Check if the ball moves horizontally
    if ball_x == prev_ball_x:
        # you cannot score by shooting verically, robot should stay at current position
        return None

    m = (ball_y - prev_ball_y) / (ball_x - prev_ball_x)
    b = prev_ball_y - m * prev_ball_x
    y_at_goal = m * goalxpos + b
    return y_at_goal

def shoot_at_goal():
    # randomize the ball position inside a reasonable rectangle
    ball_x = random.uniform(0, 1)
    ball_y = random.uniform(-1, 1)

    # randomize the target at goalpost
    target_x = 4.2
    target_y = random.uniform(-0.4, 0.4)

    # calculate ratio of velocities
    ratio = (target_y - ball_y)/(target_x - ball_x)
    vx = 5
    vy = 5 * ratio
    return ball_x, ball_y, vx, vy

def shoot_at_random_target():
    # randomize the ball position inside a reasonable rectangle
    ball_x = random.uniform(0, 1)
    ball_y = random.uniform(-1, 1)

    # random ratio
    ratio = random.uniform(-1,1)
    vx = 5
    vy = 5 * ratio
    return ball_x, ball_y, vx, vy





