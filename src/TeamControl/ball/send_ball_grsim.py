import socket
from TeamControl.network.proto2 import grSim_Replacement_pb2
from TeamControl.network.proto2 import grSim_Packet_pb2


def send_ball_to_grsim(x, y, vx, vy, address="127.0.0.1", port=20011):
    """
    Spawn or move the ball in grSim to position (x, y)
    with velocity (vx, vy).
    """

    # Create the BallReplacement message
    ball = grSim_Replacement_pb2.grSim_BallReplacement()
    ball.x = x
    ball.y = y
    ball.vx = vx
    ball.vy = vy

    # Create the Replacement message
    replacement = grSim_Replacement_pb2.grSim_Replacement()
    replacement.ball.CopyFrom(ball)

    # Create the Packet message
    packet = grSim_Packet_pb2.grSim_Packet()
    packet.replacement.CopyFrom(replacement)

    # Serialize to bytes
    data = packet.SerializeToString()

    # Send via UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (address, port))
    sock.close()

    print(f"Ball sent to grSim: pos=({x:.2f}, {y:.2f}) vel=({vx:.2f}, {vy:.2f})")


if __name__ == "__main__":
    # Example:
    send_ball_to_grsim(x=0.0, y=0.0, vx=2.0, vy=1.0)