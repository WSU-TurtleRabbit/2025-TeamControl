"""
Obstacle avoidance process for SSL RoboCup.

Usage:
    python obstacle_avoidance_process.py scenario_1
"""

import sys
import time
import importlib
from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.obstacles.helpers import check_stop_conditions
# import your obstacle avoidance code here

def obstacle_avoidance_process(wm):
    # Load scenario from command line argument or default
    # TODO: Move this to sandbox.py
    scenario_name = sys.argv[1] if len(sys.argv) > 1 else "scenario_1"
    print(f"Loading scenario: {scenario_name}")

    scenario_module = importlib.import_module(f"TeamControl.obstacles.{scenario_name}")
    target_pos, static_robots, dynamic_robots = scenario_module.get_scenario()

    print(f"Target position: {target_pos}")
    print(f"Static obstacles: {static_robots}")
    print(f"Dynamic obstacles: {dynamic_robots}")

    # grSim connection setup
    SIM_IP = "127.0.0.1"
    CMD_LISTEN_PORT = 20011
    IS_YELLOW = True
    ROBOT_ID = 0

    sender = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=IS_YELLOW)

    version = 0
    robot_pos = (10, 10, 0)

    start_time = time.time()
    TIME_LIMIT = 30  # seconds

    while time.time() - start_time < TIME_LIMIT:
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=IS_YELLOW, robot_id=ROBOT_ID)
                robot_pos = robot_obj.position  # (x, y, orientation)
            except Exception:
                robot_pos = (0, 0, 0)

        pos_2d = robot_pos[:2]

        # check for stop conditions: 
        # - reached target
        # - left field
        # - collision
        # - in opponent defense area
        stop, message = check_stop_conditions(
            agent_pos=pos_2d,
            target_pos=target_pos,
            static_robots=static_robots,
            dynamic_robots=dynamic_robots,
            robot_radius=0.2,
            elapsed_time=time.time() - start_time,
            time_limit=TIME_LIMIT
        )
        if stop:
            print(message)
            break

        # Define your obstacle avoidance here
        # ...

    else: 
        print("Time limit reached.\n0 POINTS")

