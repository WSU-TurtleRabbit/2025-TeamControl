"""
network_interfaces.py

Provides network interfaces for SSL-Vision and grSim simulator communication.

Classes:
    Vision          - SSL-Vision multicast receiver.
    VisionTracker   - SSL-Vision tracked data receiver.
    GameControl     - Referee/GameController receiver.
    grSimVision     - Vision receiver for grSim simulator output.
    grSimSender     - UDP sender for grSim robot control.

Author:
    Emma — 2025
"""

from TeamControl.network.proto2 import (
    ssl_vision_wrapper_pb2,
    ssl_vision_detection_tracked_pb2,
    ssl_gc_referee_message_pb2)
from TeamControl.network.receiver import Multicast
from TeamControl.network.sender import Sender
from TeamControl.network.grSim_commands import GrSimRobotCommands


# ===============================
# SSL-VISION RECEIVERS
# ===============================
class Vision(Multicast):
    """
    SSL-Vision multicast receiver.

    Receives raw SSL-Vision packets via UDP multicast.
    These packets contain data about detected balls and robots from the vision system.

    Args:
        port (int): Port for the SSL-Vision multicast. Defaults to 10006.
    """
    def __init__(self,port : int=10006) -> None:
        decoder :object = ssl_vision_wrapper_pb2.SSL_WrapperPacket()
        group : str = "224.5.23.2"
        buffer_size : int = 6000
        super().__init__(port=port, group=group, decoder=decoder, buffer_size=buffer_size)
   
    def listen(self) -> ssl_vision_wrapper_pb2.SSL_WrapperPacket:
        """
        Listen for incoming SSL-Vision packets.

        Returns:
            SSL_WrapperPacket: decoded vision data.
        """
        vision_data, addr = super().listen()
        return vision_data
            
class VisionTracker(Multicast):
    """
    SSL-Vision tracked data receiver.

    Listens to processed (tracked) packets from the SSL vision system.
    """
    def __init__(self, port: int = 1234, group: str = "224.5.23.2",
                 buffer_size: int = 6000, timeout: float = 1.0) -> None:
        decoder = ssl_vision_detection_tracked_pb2.TrackerWrapperPacket()
        super().__init__(port=port, group=group, decoder=decoder, buffer_size=buffer_size, timeout=timeout)



class GameControl(Multicast):
    """
    SSL-GameController multicast receiver.

    Receives referee messages containing play state, goals, team info, etc.
    """
    def __init__(self) -> None:
        group : str = '224.5.23.1'
        port : int = 10003
        decoder = ssl_gc_referee_message_pb2.Referee()
        buffer_size : int = 6000
        timeout : float = 5.0
        super().__init__(port=port, group=group, decoder=decoder, buffer_size=buffer_size,timeout=timeout)
        
    def listen(self) -> ssl_gc_referee_message_pb2.Referee:
        """
        Listen for referee messages.

        Returns:
            Referee: decoded referee message protobuf.
        """
        data, addr = super().listen()
        return data
    

class grSimVision(Vision):
    """
    Vision receiver for the grSim simulator.

    Listens to simulated camera data broadcasted by grSim.
    """
    def __init__(self, port : int=10020) -> None:
        super().__init__(port=port)
        
# ===============================
# GRSIM COMMAND SENDER
# ===============================
class grSimSender(Sender):
    """
    UDP sender for grSim robot commands.

    Responsible for encoding and sending control packets to the grSim simulator.
    """

    def __init__(self, ip: str = "127.0.0.1", port : int = 20010, is_yellow = True) -> None:
        """
        Initialize grSim sender.

        Args:
            ip (str): Destination IP address of the grSim simulator.
            port (int): Destination port for control commands.
            is_yellow (bool): Whether this sender controls the yellow team.
        """
        self.is_yellow = is_yellow 
        self.GSC = GrSimRobotCommands(isYellow=is_yellow)
        super().__init__(ip=ip,port=port)
    
    def new_raw_command(self, robot_id, vx=0.0, vy=0.0, w=0.0, k=0, d=0, use_team_color=True):
        """
        Generate a new grSim robot command.

        Returns:
            grSim_Commands_pb2.grSim_Commands: command packet.
        """
        return self.GSC.new_command(robot_id=robot_id,vx=vx,vy=vy,w=w,k=k,d=d,use_team_color=use_team_color)
    
    def send(self,msg) -> None:
        """
        Send a command to grSim.

        Args:
            msg (grSim_Commands_pb2.grSim_Commands | bytes): Command to send.
        """
        if not isinstance(msg,bytes):
            try:
                msg = self.GSC.encode(msg)
            except Exception as e:
                raise ValueError(f"Error encoding grSim message: {e}")
        self.sock.sendto(msg,self.destination)
    
    def send_command(self, robot_command,use_team_color=True) -> None:
        """
        Convert a RobotCommand object into a grSim command and send it.

        Args:
            robot_command (RobotCommand): The robot command object.
            us (bool): Whether this is for our team (True) or the opponent.
        """
        packet = self.GSC.convert(robot_command=robot_command,use_team_color=use_team_color)
        encoded_msg = self.GSC.encode(packet)
        self.send(encoded_msg)
        



### NOT IN USE ###
# ## These are 2 way sockets
# class grSimControl(Sender):
#     def __init__(self, ip: str = "127.0.0.1", port: int = 10300) -> None:
#         """Socket for communicating with grSim Control

#         Args:
#             ip (str, optional): Ip of Simulation Device. Defaults to None -> self obtain.
#             port (int, optional): simulation control port. Defaults to 10300.
#         """
#         buffer_size = 1024
#         # self.coder = ssl_simulation_control_pb2.
#         super().__init__(ip=ip,port=port,buffer_size=buffer_size,binding=False)
    
#     def listen(self, duration: int = None) -> str:
#         return super().listen(duration) 

#     def decode(self,data):
#         raise NotImplementedError
#         decoded_data:str = self.decoder.FromString(data)
#         print("data received : ", decoded_data)
#         return decoded_data

#     def send (self,packet) -> None:
#         self.sock.sendto(packet,(self.ip,self.port))
#         ...
    
# class grSimYellowControl(grSimControl): 
#     def __init__(self, ip: str = "127.0.0.1", port: int = 10301) -> None:
#         super().__init__(ip, port)
    
#     def listen(self, duration: int = None) -> str | None:
#         return super().listen(duration)

#     def send(self, packet) -> None:
#         return super().send(packet)

# class grSimBlueControl(grSimControl):
#     def __init__(self, ip: str = "127.0.0.1", port: int = 10302) -> None:
#         """grSim Blue Team Control.

#         Args:
#             ip (str, optional): ip of simulation. Defaults to None.
#             port (int, optional): port receiving. Defaults to 10302.
#         """
#         super().__init__(ip, port)
        
#     def listen(self, duration: int = None):
#         return super().listen(duration)

#     def send(self, packet) -> None:
#         return super().send(packet)
  


# if __name__ == "__main__":
#     recv = GameControl()
#     data,addr = recv.listen()
#     print(f"{data} \n received from {addr}.")