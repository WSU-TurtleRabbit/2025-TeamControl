"""
sandbox_process.py

Example sandbox process for sending movement commands to a robot in grSim.

This script demonstrates how to:
    1. Initialize a grSim sender.
    2. Continuously read the world model (wm) for robot and ball positions.
    3. Compute velocity commands toward a target using RobotMovement.
    4. Send RobotCommand packets to grSim.
"""

from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand 
from TeamControl.robot.Movement import RobotMovement

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

    Notes:
        - The target is currently set as the ball position.
        - Angular velocity (w), kick, and dribble are kept at 0 for simplicity.
        - Can be adapted for multi-robot or advanced control logic.
    """
    # grSim connection parameters
    SIM_IP = "127.0.0.1"
    CMD_LISTEN_PORT = 20011
    IS_YELLOW = True
    ROBOT_ID = 0

    # Initialize grSim command sender
    sender = grSimSender(ip=SIM_IP,port=CMD_LISTEN_PORT,is_yellow=IS_YELLOW)
    
    version = 0 # Track vision/world model version
    robot_pos = 0,0,0
    ball_pos = 0,0

    #cmd = RobotCommand(robot_id=1, vx=500, vy=0, w=0, kick=0, dribble=0)
    #sender.send_command(cmd)
    #print("Test command sent")

    while True:
        # Update world model when new frame is available
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=IS_YELLOW,robot_id=ROBOT_ID)
                robots = wm.get_yellow_robots(isYellow=IS_YELLOW,robot_id=None)
                robot_pos = robot_obj.position
                ball_pos = wm.get_latest_frame().ball.position
            except Exception :
                robot_pos = 0,0,0
                ball_pos = 0,0
        
        # Set target position
        #target_position = 0,0      # Center of the field
        target_position = ball_pos  # Ball

        # Compute velocities to move toward the target
        vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos, target=target_position)
        
        # Create and send the command
        cmd = RobotCommand(robot_id=0, vx=vx, vy=vy, w=0.0, kick=0, dribble=0)
        sender.send_command(cmd)