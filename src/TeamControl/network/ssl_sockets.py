from TeamControl.network.proto2 import ssl_vision_wrapper_pb2,ssl_vision_detection_tracked_pb2,ssl_gc_referee_message_pb2,grSim_Packet_pb2
from TeamControl.network.receiver import SSL_Multicast
from TeamControl.network.sender import LockedSender
from TeamControl.network.robot_command import RobotCommand
from TeamControl.network.grSimPacketFactory import grSimPacketFactory
from multiprocessing import Event

# Classes of Vision Wolrd Receivers
class Vision(SSL_Multicast):
    """ Vision SSL multicast receiver
        world vision SSL  mulitcast listener
    Args:
        Multicast (Class): base Class
    """
    def __init__(self,is_running:Event,port : int=10006) -> None:
        """
        Initialising Multicast Vision SSL Socket

        Args:
            world_model (wm): current world model
            port (int, optional): Port for Vision World multicast. Defaults to 10005. change accordingly if needed
        """
        decoder :object = ssl_vision_wrapper_pb2.SSL_WrapperPacket()
        group : str = "224.5.23.2"
        buffer_size : int = 6000
        super().__init__(is_running=is_running,port=port,group=group,decoder=decoder,buffer_size=buffer_size)
   
    def listen(self) -> bool:
        return super().listen()
            
class VisionTracker(SSL_Multicast):
    """
    For Tracked Packets 
    Default :  224.5.23.2:10010
    Args:
        Multicast: the recv socket
    """
    def __init__(self, is_running:Event,port, group, decoder, buffer_size = 6000, timeout = 1):
        port = 10007
        decoder = ssl_vision_detection_tracked_pb2.TrackerWrapperPacket()
        group : str = "224.5.23.2"
        buffer_size : int = 6000
        super().__init__(port, group, decoder, buffer_size, timeout)


class GameControl(SSL_Multicast):
    def __init__(self,is_running:Event) -> None:
        group : str = '224.5.23.1'
        port : int = 10003
        decoder = ssl_gc_referee_message_pb2.Referee()
        buffer_size : int = 6000
        timeout : float = 5.0
        super().__init__(is_running=is_running,port=port, group=group, decoder=decoder, buffer_size=buffer_size,timeout=timeout)
        
    def listen(self) -> ssl_gc_referee_message_pb2.Referee:
        # see Multicast listen(), decode()
        return super().listen()

class grSimVision(Vision):
    def __init__(self, is_running:Event, port : int=10020) -> None:
        """
        Initialising Multicast GR Sim World Socket
        
        Args:
            is_running(Event): Multiprocessing Event to manage operation
            ip (str, optional): ip of the grSim device. Defaults to None -> local.
            port (int, optional): port of grSim Vision. Defaults to 10020.
        """
        super().__init__(is_running, port=port)
        
### Simulation Control ### 

class grSimSender(LockedSender):
    def __init__(self, ip: str = "127.0.0.1", port : int = 20010) -> None: #please check and verify this port
        super().__init__(ip=ip,port=port)
    
    def send_robot_command(self,robot_command:RobotCommand,override_id=None):
        if not isinstance(robot_command,RobotCommand):
            raise TypeError("Expecting RobotCommand Object, got ", type(robot_command))
        # creates a packet
        cmd_dict = robot_command.to_dict()

        if override_id is not None:
            cmd_dict["robot_id"] = int(override_id)
            
        packet = grSimPacketFactory.robot_command(**cmd_dict)
        # send this packet
        self.send_packet(packet)
        
    
    def send_packet(self,packet:grSim_Packet_pb2) -> None:
        """
        send RobotCommand or bytes to grSim
        *see grSimPacketFactory for how to generate packet
        """

        if not isinstance(packet,grSim_Packet_pb2.grSim_Packet):
            raise TypeError("Only accept grSim_Packet_pb2 Object")
        
        # encodes the packet
        encoded_msg = self.encode(packet)
        # feedback statement ? 
        # print(f"{packet} \n has been sent to {self.destination}.")
        # sends the packet
        self.send(encoded_msg)

    
    def send(self,byte_string: bytearray)->None:
        if not isinstance(byte_string,bytes):
            raise TypeError("expected byte-like object, use send_packet() or send_robot_command instead ?")
        self.sock.sendto(byte_string,self.destination)
        
    
    @staticmethod
    def encode(packet) -> bytes:
        bytes_packet = packet.SerializeToString()
        return bytes_packet
    



if __name__ == "__main__":
    sender = grSimSender()
    cmd = RobotCommand(1)
    sender.send_robot_command(cmd)
    
    



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
  
