from TeamControl.network.proto2 import ssl_vision_wrapper_pb2,ssl_vision_detection_tracked_pb2,ssl_gc_referee_message_pb2
from TeamControl.network.receiver import Multicast
from TeamControl.network.sender import Sender
from TeamControl.network.grSim_commands import GrSimRobotCommands


# Classes of Vision Wolrd Receivers
class Vision(Multicast):
    """ Vision SSL multicast receiver
        world vision SSL  mulitcast listener
    Args:
        Multicast (Class): base Class
    """
    def __init__(self,port : int=10006) -> None:
        """
        Initialising Multicast Vision SSL Socket

        Args:
            world_model (wm): current world model
            port (int, optional): Port for Vision World multicast. Defaults to 10005. change accordingly if needed
        """
        decoder :object = ssl_vision_wrapper_pb2.SSL_WrapperPacket()
        group : str = "224.5.23.2"
        buffer_size : int = 6000
        super().__init__(port=port,group=group,decoder=decoder,buffer_size=buffer_size)
   
    def listen(self) -> bool:
        result= super().listen()
        if isinstance(result,tuple):
            data, addr = result
        # print(result)
            return data
            
class VisionTracker(Multicast):
    """
    For Tracked Packets

    Args:
        Multicast: the recv socket
    """
    def __init__(self, port, group, decoder, buffer_size = 6000, timeout = 1):
        port = 1234
        decoder = ssl_vision_detection_tracked_pb2.TrackerWrapperPacket()
        group : str = "224.5.23.2"
        buffer_size : int = 6000
        super().__init__(port, group, decoder, buffer_size, timeout)


class GameControl(Multicast):
    def __init__(self) -> None:
        group : str = '224.5.23.1'
        port : int = 10003
        decoder = ssl_gc_referee_message_pb2.Referee()
        buffer_size : int = 6000
        timeout : float = 5.0
        super().__init__(port=port, group=group, decoder=decoder, buffer_size=buffer_size,timeout=timeout)
        
    def listen(self) -> ssl_gc_referee_message_pb2.Referee:
        # see Multicast listen(), decode()
        data, addr = super().listen()
        return data
    

class grSimVision(Vision):
    def __init__(self, port : int=10020) -> None:
        """
        Initialising Multicast GR Sim World Socket
        
        Args:
            ip (str, optional): ip of the grSim device. Defaults to None -> local.
            port (int, optional): port of grSim Vision. Defaults to 10020.
        """
        super().__init__(port=port)
        
### Simulation Control ### 

class grSimSender(Sender):
    def __init__(self, ip: str = "127.0.0.1", port : int = 20010,is_yellow = True) -> None: #please check and verify this port
        self.is_yellow = is_yellow 
        self.GSC = GrSimRobotCommands(isYellow=is_yellow)
        super().__init__(ip=ip,port=port)
    
    def new_raw_command(self,robot_id,vx=0.0,vy=0.0,w=0.0,k=0,d=0,us=True):
        return GSC.new_command(robot_id=robot_id,vx=vx,vy=vy,w=w,k=k,d=d,us=us)
    
    def send(self,msg) -> None:
        """
        send GrSimRobotCommands or bytes to grSim
        """
        if not isinstance(msg,bytes):
            try:
                msg = self.GSC.encode(msg)
            except Exception as e:
                raise(e, "Error with GRSIM message packing")
        self.sock.sendto(msg,self.destination)
    
    def send_command(self, robot_command,us=True) -> None:
        """send_command
        
        sending Command over grsim command sender port
        
        converting RobotCommands into grSim commands
        """
        packet = self.GSC.convert(robot_command=robot_command,us=us)
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