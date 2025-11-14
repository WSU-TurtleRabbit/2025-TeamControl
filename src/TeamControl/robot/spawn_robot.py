import socket
from TeamControl.network.proto2 import grSim_Replacement_pb2
from TeamControl.network.proto2 import grSim_Packet_pb2


def send_robot_to_grsim(
    team_yellow: bool,
    robot_id: int,
    x: float,
    y: float,
    orientation: float = 0.0,
    address: str = "127.0.0.1",
    port: int = 20011
):
    """
    Spawn or move a robot in grSim to position (x, y) with given velocity and orientation.

    Args:
        team_yellow (bool): True for yellow team, False for blue team.
        robot_id (int): Robot ID (0–10).
        x, y (float): Position in mm (field coordinates).
        orientation (float): Orientation in radians.
        vx, vy (float): Linear velocity (mm/s or m/s depending on grSim setup).
        vtheta (float): Angular velocity (rad/s).
        address (str): UDP address for grSim.
        port (int): UDP port for grSim (default 20011).
    """
    #change the coordinates to meters
    x = x/1000
    y = y/1000
    
    # Create the RobotReplacement message
    robot = grSim_Replacement_pb2.grSim_RobotReplacement()
    robot.id = robot_id
    robot.yellowteam = team_yellow
    robot.x = x
    robot.y = y
    robot.dir = orientation

    # Wrap inside a Replacement message
    replacement = grSim_Replacement_pb2.grSim_Replacement()
    replacement.robots.append(robot)

    # Create the top-level Packet
    packet = grSim_Packet_pb2.grSim_Packet()
    packet.replacement.CopyFrom(replacement)

    # Serialize to bytes and send via UDP
    data = packet.SerializeToString()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (address, port))
    sock.close()

    # print(
    #     f"Robot sent to grSim: team={'Yellow' if team_yellow else 'Blue'} "
    #     f"ID={robot_id} pos=({x:.1f},{y:.1f}) dir={orientation:.2f} "
    # )
    
def spawn_robots_at_initial_positions(main_agent, static_robots, dynamic_robots):
    # spawn main robot
    send_robot_to_grsim(
        team_yellow=True,
        robot_id=main_agent['id'],
        x=main_agent['start'][0],
        y=main_agent['start'][1],
        orientation=0
    )
    # spawn static robots at the correct positions
    for robot_id, robot_data in static_robots.items():
        send_robot_to_grsim(
            team_yellow=False,
            robot_id=robot_id,
            x=robot_data['start'][0],
            y=robot_data['start'][1],
            orientation=0
        )
    for robot_id, robot_data in dynamic_robots.items():
        send_robot_to_grsim(
            team_yellow=False,
            robot_id=robot_id,
            x=robot_data['start'][0],
            y=robot_data['start'][1],
            orientation=0
        )

def remove_robots_not_in_scenario(robots_yellow, robots_blue, static_robots, dynamic_robots):
    for robot_yellow_id in robots_yellow.active:
        if robot_yellow_id != 0:
            # spawn it outside of the field
            send_robot_to_grsim(
                team_yellow=True,
                robot_id=robot_yellow_id,
                x=-5000,
                y=-5000,
                orientation=0
            )

    for robot_blue_id in robots_blue.active:
        if robot_blue_id != dynamic_robots and robot_blue_id != static_robots:
            # spawn it outside of the field
            send_robot_to_grsim(
                team_yellow=False,
                robot_id=robot_blue_id,
                x=-5100,
                y=-5100,
                orientation=0
            )

    

if __name__ == "__main__":
    # Example usage:
    # Spawn blue robot 0 at (1000, -500) mm facing 45°
    send_robot_to_grsim(
        team_yellow=False,
        robot_id=0,
        x=1,
        y=1,
        orientation=0.7854
    )
    
    