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

from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand 
from TeamControl.robot.Movement import RobotMovement
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
    ROBOT_ID = 1

    # Initialize grSim command sender
    sender = grSimSender(ip=SIM_IP,port=CMD_LISTEN_PORT,is_yellow=IS_YELLOW)
    
    # Track world model
    version = 0
    robot_pos = (0,0,0)
    ball_pos = (0,0)
    
    # Robot patrol settings in mm
    patrol_y_min = -600
    patrol_y_max = 600
    patrol_x = 4400
    robot_direction = 1  # 1 = moving up, -1 = moving down
    patrol_speed = 2000  # mm/s

    # Ball initial settings in mm
    ball_spawn = (0, 0)
    ball_velocity = (5, 0)  # m/s

    # Spawn ball initially
    send_ball_to_grsim(x=ball_spawn[0], y=ball_spawn[1], vx=ball_velocity[0], vy=ball_velocity[1])

    FIELD_X_MIN, FIELD_X_MAX = -4500, 4500
    FIELD_Y_MIN, FIELD_Y_MAX = -3000, 3000

    last_time = time.time()

    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # Update world model when new frame is available
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=IS_YELLOW, robot_id=ROBOT_ID)
                robot_pos = robot_obj.position

                ball_pos = wm.get_latest_frame().ball.position
            except Exception:
                robot_pos = (0,0,0)
                ball_pos = (0,0)

        # --- Robot patrols between goal posts ---
        next_y = robot_pos[1] + robot_direction * patrol_speed * dt
        if next_y > patrol_y_max:
            next_y = patrol_y_max
            robot_direction = -1
        elif next_y < patrol_y_min:
            next_y = patrol_y_min
            robot_direction = 1

        vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos, target=(patrol_x, next_y))
        cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=0, dribble=0)
        sender.send_command(cmd)

        # --- Ball respawn logic ---
        ball_x, ball_y = ball_pos
        # If ball is out of bounds, respawn it
        if not (FIELD_X_MIN <= ball_x <= FIELD_X_MAX and FIELD_Y_MIN <= ball_y <= FIELD_Y_MAX):
            send_ball_to_grsim(x=ball_spawn[0], y=ball_spawn[1],
                               vx=ball_velocity[0], vy=ball_velocity[1])
            ball_pos = ball_spawn

        time.sleep(0.01)  # small delay to avoid busy loop