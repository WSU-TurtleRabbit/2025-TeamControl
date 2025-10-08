"""
RobotCommand.py

Represents a single robot command for a robot soccer system.

This class can be used to:
- Initialize robot commands with velocities, kick, and dribble flags.
- Encode commands into a byte string for UDP transmission.
- Decode received command strings or bytes back into a RobotCommand object.

Author: Emma
"""

import logging
import datetime
import time

class RobotCommand():
    """
    RobotCommand represents the desired motion command for a single robot.

    Attributes:
        robot_id (int): Unique robot identifier.
        vx (float): Velocity along the X-axis (m/s).
        vy (float): Velocity along the Y-axis (m/s).
        w (float): Angular velocity (rad/s).
        kick (int): Kick flag (0 = no kick, 1 = kick).
        dribble (int): Dribble flag (0 = off, 1 = on).
        time_origin (float): Original creation time of the packet.
        time_set (float): Timestamp when this RobotCommand object was instantiated.
    """

    def __init__(self, robot_id : int, vx : float=0.0, vy: float=0.0, w : float=0.0, kick : int=0, dribble : int=0, time_origin : float= 0.0):
        """
        Initialize a RobotCommand object.

        Args:
            robot_id (int): Robot ID.
            vx (float): Desired X velocity.
            vy (float): Desired Y velocity.
            w (float): Desired angular velocity.
            kick (int): Kick command (0 or 1).
            dribble (int): Dribble command (0 or 1).
            time_origin (float): Original packet creation time. Default=0.0.

        Params:
            time_set (float): Time of RobotCommand instantiation (auto-set).
        """
        self.time_set: float = time.time()
        self.robot_id: int = int(robot_id)
        self.vx: float = float(vx)
        self.vy: float = float(vy)
        self.w: float = float(w)
        self.kick: int = int(kick)
        self.dribble: int = int(dribble)
        self.time_origin: float = float(time_origin)
    
    def __str__(self) -> str:
        """
        Convert the RobotCommand to a string.

        Returns:
            str: String representation of the RobotCommand.
        """
        return f"{self.robot_id} {self.vx} {self.vy} {self.w} {self.kick} {self.dribble} {self.time_set}"

    def __repr__(self) -> str:
        """
        Debug representation of the RobotCommand object.

        Returns:
            str: Multiline string for debugging.
        """
        return f'''
            Robot Command: 
            {self.time_set=} , {self.time_origin=} : {self.robot_id=}
            Velocity : {self.vx=} , {self.vy=}, {self.w=}
            Kick? : {self.kick=}
            Dribble? : {self.dribble=}
            '''
                
    def encode(self) -> bytes:
        """
        Encode the RobotCommand into bytes for UDP transmission.

        Returns:
            bytes: UTF-8 encoded byte string of the RobotCommand.
        """

        self.encoded = bytes(str(self).encode('utf-8'))
        return self.encoded
    
    @classmethod
    def decode(cls,command_msg:str|bytes) -> object:
        """
        Decode a received command string or bytes into a RobotCommand object.

        Args:
            command_msg (str | bytes): Command message received via UDP.

        Returns:
            RobotCommand: A new RobotCommand object.
        """
        ## Convert bytes to string if necessary
        if isinstance(command_msg, bytes):
            command_msg = command_msg.decode()

        # Split the command string into components
        try:
            robot_id, vx, vy, w, kick, dribble, time_origin = command_msg.split(" ")
        except ValueError as e:
            raise ValueError(f"Invalid command format: {command_msg}") from e
        
        # Convert string arguments to appropriate types
        args = [
            int(robot_id), 
            float(vx),
            float(vy),
            float(w),
            int(kick),
            int(dribble),
            float(time_origin)]
        
        return RobotCommand(*args) 
