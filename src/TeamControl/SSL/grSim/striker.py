"""
sandbox_process_ball_spawning.py

Example sandbox process for sending movement commands to a robot in grSim.

This script demonstrates how to:
    1. Initialize a grSim sender.
    2. Continuously read the world model (wm) for robot and ball positions.
    3. Spawn balls and respawn them automatically, tracking goals.
"""
from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand
from TeamControl.ball.send_ball_grsim import send_ball_to_grsim
from TeamControl.ball.ball_idle_test_scenarios_spawner import BallIdleSpawner
from TeamControl.robot.smooth_movement import RobotMovement
from TeamControl.robot.shooting import RobotShooting
from TeamControl.robot.obstacle_avoidance import AvoidObstacle
import math

# --------------------------
# Ball idle spawner parameters
# --------------------------
DIVISION = 'B'  # 'A' or 'B'

def striker_process(wm) -> None:
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

    # initialize values
    shooting_time = False

    # Initialize BallSpawner
    spawner = BallIdleSpawner(
        division=DIVISION
    )

    # Track number of goals scored
    goal_count = 0

    # Initial ball spawn
    x, y, vx, vy = spawner.spawn_next_ball(robot_pos)
    send_ball_to_grsim(x, y, vx, vy)

    while True:
        # Update world model when new frame is available
        # while time < 1 and mode == testing
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=IS_YELLOW,
                                                 robot_id=ROBOT_ID)
                robot_pos = robot_obj.position
                prev_ball_pos = ball_pos
                ball_pos = wm.get_latest_frame().ball.position

            except Exception:
                robot_pos = 0, 0, 0
                prev_ball_pos = (-1, -1)
                ball_pos = 0, 0

        # ---- STRIKER STRATEGY ----
        # This striker strategy is a rule based approach
        # Scoring a goal consists of 3 basic steps
        # 1. Go behind the ball (avoiding conflicts with the ball while getting there)
        #    This, so called shooting position should be a point on the line of
        #    the ball and the center of the goalpost
        # 2. Rotate the agent to place the kicker towards teh ball and towards
        #    the goal
        # 3. Move towards the ball while trying to kick the ball
        
        target_pos = RobotShooting.find_shooting_location(ball_pos)
        target_pos = AvoidObstacle.avoid_collision_with_ball(robot_pos, ball_pos, target_pos)
        if not target_pos_reached(robot_pos, target_pos) and not shooting_time:
            # Move behind the ball
            vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos,
                                                 target=target_pos)
            cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=0,
                                   dribble=0)

            sender.send_command(cmd)

        elif target_pos_reached(robot_pos, target_pos) and not shooting_time:
            # Get the proper robot angle to be able to shoot towards the goal
            shooting_angle = RobotShooting.find_shooting_angle(robot_pos, ball_pos)
            ang_vel = RobotMovement.rotate_to_target(robot_pos, shooting_angle)
            cmd = RobotCommand(robot_id=ROBOT_ID, vx=0, vy=0, w=ang_vel, kick=0,
                                   dribble=0)
            sender.send_command(cmd)

            if shooting_angle_reached(robot_pos[2], shooting_angle):
                shooting_time = True

        elif shooting_time:
            # Shoot the ball
            shooting_time = True
            vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos,
                                             target=ball_pos)
            cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=1,
                               dribble=0)

            sender.send_command(cmd)

        if shooting_time and not ball_idle(prev_ball_pos, ball_pos):
            shooting_time = False


        # ---- CHECK FOR GOAL ----
        # Check if the ball crossed the goal line and is within the goal posts
        goal_y_min = -spawner.goal_width / 2
        goal_y_max = spawner.goal_width / 2
        if ball_pos[0] >= spawner.goal_line_x and goal_y_min <= ball_pos[
            1] <= goal_y_max:
            goal_count += 1
            print(f"Total goals so far: {goal_count}")
            # Respawn the ball immediately after a goal
            x, y, vx, vy = spawner.spawn_next_ball(robot_pos)
            send_ball_to_grsim(x, y, vx, vy)
            prev_ball_pos = ball_pos
            ball_pos = (x, y)


        # ---- BALL RESPAWNING LOGIC (DO NOT CHANGE) ----
        elif not spawner.is_ball_in_field(ball_pos):
            x, y, vx, vy = spawner.spawn_next_ball(robot_pos)
            send_ball_to_grsim(x, y, vx, vy)
            prev_ball_pos = ball_pos
            ball_pos = (x, y)

def target_pos_reached(robot_pos, shooting_pos):
    x1, y1, _ = robot_pos
    x2, y2 = shooting_pos
    return abs(x1 - x2) + abs(y2 - y1) <= 20

def shooting_angle_reached(robot_angle, shooting_angle):
    if shooting_angle is None:
        return False

    return abs(robot_angle - shooting_angle) <= math.pi/45

def ball_idle(ball_prev, ball_curr):
    return (ball_prev[0] - ball_curr[0] == 0 and ball_prev[1] - ball_curr[1] == 0)