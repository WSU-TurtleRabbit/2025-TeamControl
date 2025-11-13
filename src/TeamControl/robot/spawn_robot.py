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

    print(
        f"Robot sent to grSim: team={'Yellow' if team_yellow else 'Blue'} "
        f"ID={robot_id} pos=({x:.1f},{y:.1f}) dir={orientation:.2f} "
    )


if __name__ == "__main__":
    # Example usage:
    # Spawn blue robot 0 at (1000, -500) mm facing 45°
    send_robot_to_grsim(
        team_yellow=False,
        robot_id=0,
        x=1000.0,
        y=-500.0,
        orientation=0.7854
    )