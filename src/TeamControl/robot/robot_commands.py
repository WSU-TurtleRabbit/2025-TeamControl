"""
RobotCommands Module

This module defines a RobotCommands class to represent a single robot command. 
It uses Python's `struct` module to pack and unpack data into a fixed-size binary 
format suitable for communication between systems or devices.

Key Features:
- Fixed-size message using a defined binary layout.
- Supports velocity, angular velocity, kick/dribble actions, and timestamps.
- Ensures consistent serialization and deserialization of robot commands.
"""

import struct
import time

class RobotCommands:
    """
        Represents a robot command that can be serialized to and deserialized from a binary format.

        Attributes:
            FORMAT (str): Struct format string defining the binary layout.
            SIZE (int): Total size of the packed binary data in bytes.
            robot_id (int): Unique ID of the robot.
            vx (float): Velocity in the X direction.
            vy (float): Velocity in the Y direction.
            w (float): Angular velocity.
            k (bool): Kick command flag.
            d (bool): Dribble command flag.
            time_created (float): Timestamp when the command was created.
            time_origin (float): Optional timestamp representing original command generation time.
        """
    
    FORMAT = '<Ifff??d' # Little-endian: unsigned int, 3 floats, 2 bools, 1 double
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, robot_id:int, vx:float, vy:float, w:float, kick:bool, dribble:bool, time_origin:float=None):
        """
        Initialize a RobotCommands instance.

        Args:
            robot_id (int): Robot's unique identifier.
            vx (float): Velocity along the X-axis.
            vy (float): Velocity along the Y-axis.
            w (float): Angular velocity.
            kick (bool): Whether the robot should kick.
            dribble (bool): Whether the robot should dribble.
            time_origin (float, optional): Original timestamp of command generation. Defaults to None.
        """
        self.robot_id = robot_id
        self.vx = vx
        self.vy = vy
        self.w = w
        self.k = kick
        self.d = dribble
        self.time_created = time.time()
        self.time_origin = time_origin
    
    def pack(self) -> bytes:
        """
        Pack the RobotCommands instance into a binary format.

        Returns:
            bytes: Binary representation of the robot command.
        """
        return struct.pack(self.FORMAT, self.robot_id, self.vx, self.vy, self.w, self.k, self.d, self.time_created)

    @classmethod
    def unpack(cls, data):
        """
        Unpack binary data into a RobotCommands instance.

        Args:
            data (bytes): Binary data representing a RobotCommands object.

        Raises:
            ValueError: If the length of data does not match the expected SIZE.

        Returns:
            RobotCommands: A new instance created from the unpacked data.
        """
        if len(data) != cls.SIZE:
            raise ValueError("Invalid data size")
        robot_id, vx, vy, w, kick, dribble, time_origin= struct.unpack(cls.FORMAT, data)
        return cls(robot_id, vx, vy, w, kick, dribble, time_origin)

    def __repr__(self) -> str:
        """
        Return a human-readable string representation of the RobotCommands instance.

        Returns:
            str: Readable representation of robot status.
        """
        return f"<Status: robot={self.robot_id}. Velocity_X(vx)={self.vx}, Velocity_Y(vy)={self.vy}, Angular_Velocity(w)={self.w}, kick?={self.k}, dribble?={self.d} time_created={self.time_created}, time_origin={self.time_origin}>"

if __name__ == "__main__":
    # Example usage
    packet = RobotCommands(robot_id=1,vx=1.1,vy=1.1,w=2.2,kick=0,dribble=1)
    print(packet)

    # Pack the command to binary
    packet_as_struct = packet.pack()
    print(packet_as_struct)
    
    # Unpack the binary back to a RobotCommands instance
    unpack = RobotCommands.unpack(packet_as_struct)
    print(unpack)