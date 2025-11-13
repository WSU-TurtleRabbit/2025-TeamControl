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
from TeamControl.network.robot_command import RobotCommand
# import your obstacle avoidance code here
from TeamControl.Examples.PathPlanner import pathplanning
from TeamControl.voronoi_planner.voronoi_planner import VoronoiPlanner
from TeamControl.robot.smooth_movement import RobotMovement
from TeamControl.robot.spawn_robot import send_robot_to_grsim

def obstacle_avoidance_process(wm):
    # Load scenario from command line argument or default
    # TODO: Move this to sandbox.py
    scenario_name = sys.argv[1] if len(sys.argv) > 1 else "scenario_2"
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

    static_robots_pos = [static_rob['start'] for static_rob in static_robots.values()]
    for robot_id, robot_data in static_robots.items():
        send_robot_to_grsim(
            team_yellow=False,
            robot_id=robot_id,
            x=robot_data['start'][0],
            y=robot_data['start'][1],
            orientation=0.7854
        )
    
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
        print("static", static_robots_pos)
        print("dynamic", dynamic_robots)
        stop, message = check_stop_conditions(
            agent_pos=pos_2d,
            target_pos=target_pos,
            static_robots=static_robots_pos,
            dynamic_robots=dynamic_robots,
            robot_radius=0.85,
            elapsed_time=time.time() - start_time,
            time_limit=TIME_LIMIT
        )
        if stop:
            print(message)
            break

        # Define your obstacle avoidance here
        # ...
        #waypoints = pathplanning(planner, wm, target_pos)
        print(target_pos)
        vx, vy = RobotMovement.goToPoint(robot_pos=robot_pos,
                                         target=target_pos)
        cmd = RobotCommand(robot_id=ROBOT_ID, vx=vx, vy=vy, w=0.0, kick=0,
                           dribble=0)

        sender.send_command(cmd)
        

    else: 
        print("Time limit reached.\n0 POINTS")

