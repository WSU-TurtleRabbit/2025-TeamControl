### DEPRECIATED ##


# this is to get us ready to turn the commands to grSim RobotCommands
from TeamControl.network.robot_command import RobotCommand
# from TeamControl.robot.robot_commands import RobotCommands # do not use
# proto import
from TeamControl.network.proto2 import grSim_Commands_pb2
from TeamControl.network.proto2 import grSim_Packet_pb2

import time

class GrSimRobotCommands:
    def __init__(self,isYellow: bool):
        """GSC - GrSim Robot Commands
        This is responsible to generate grsim commands to be sent to grsim
        ARGS:
            isYellow (bool): sending to team isYellow = True/ False. 
        PARAMS: 
            kick_speed_x (float): kick speed in x direction (Default=10.0)
            kick_speed_z (float): kick speed in z direction (Default=0.0)
            wheel_speed (bool): Using individual wheel velocity ? (Default=False)
            
        """
        self.isYellow : bool = isYellow 
        self.kick_speed_x : float = 10.0
        self.kick_speed_z : float = 0.0 #we have no chip kick
        self.wheel_speed : bool = False
        
    def update_is_yellow(self,new_is_Yellow: bool) -> None:
        # at any time if you want to switch 
        self.isYellow = new_is_Yellow
        # log update
    
    
    def _robot_command_wrapper(self,robot_id:int,vx: float,vy: float,w: float,k:bool,d:bool) -> object:
        # the follow converts the data types, if you got a problem, check your code
        robot_id = int(robot_id)
        vx = float(vx)
        vy = float(vy)
        w = float(w)
        k = bool(k)
        d = bool(d)
        grSim_robot_command =  grSim_Commands_pb2.grSim_Robot_Command(id=robot_id, 
            kickspeedx=(self.kick_speed_x*k), kickspeedz=(self.kick_speed_z*k), 
            veltangent=vx, velnormal=vy, velangular=w, 
            spinner=d, wheelsspeed=self.wheel_speed)
        return grSim_robot_command
    
    def _commands_wrapper(self,is_yellow,grSim_robot_command) -> object:
        grSim_commands = grSim_Commands_pb2.grSim_Commands(timestamp=time.time(),
                                                           isteamyellow=is_yellow,
                                                           robot_commands=[grSim_robot_command])
        return grSim_commands
    
    def new_command(self,robot_id,vx,vy,w,k,d,us=True):
        """new_command **use this to generate new command**
        ARGS: 
            robot_id (int): id of robot
            vx (float) : velocity in x
            vy (float) : velocity in y 
            w (float)  : angular velocity
            k (bool) : kick ? Yes/no
            dribble(bool) : dribble ? Yes/no
        
        """
        isYellow = self.isYellow if us is True else not(self.isYellow)
        grSim_robot_command = self._robot_command_wrapper(robot_id,vx,vy,w,k,d)
        grSim_commands = self._commands_wrapper(isYellow,grSim_robot_command)
        return grSim_commands
    
    def convert(self,robot_command:RobotCommand,us=True) -> object:
        """new_command **use this to generate new command**
        ARGS: 
            robot_command : the normal robot_commands
        RETURN: 
            __type__ : object 
            returns the grSim_commands to be encoded
        """
        grSim_command = self.new_command(robot_id=robot_command.robot_id,
            vx=robot_command.vx,vy=robot_command.vy,w=robot_command.w,
            k=robot_command.kick,d=robot_command.dribble,us=us)
        return grSim_command

    def encode(self,grSim_commands) -> bytes:
        grSim_packet = grSim_Packet_pb2.grSim_Packet(commands=grSim_commands)
        byte_packet = grSim_packet.SerializeToString()
        return byte_packet
    
    def decode(self,grSim_commands)-> object :
        # returns grSim command object
        decoder = grSim_Packet_pb2.grSim_Packet()
        grSim_commands:str= decoder.FromString(grSim_commands) 
        return grSim_commands
# Test run
def example_1():
    # we need to initialise this
    isYellow = True
    GSC = GrSimRobotCommands(isYellow=isYellow) #remember ! ! 
    # creating a new raw command
    msg1 = GSC.new_command(robot_id=1,vx=2.0,vy=1.0,w=1,k=1,d=1,us=True)
    print(msg1) 
    # we put msg1 into sender and the sender will encode it and send it
    # or you can encode it 
    encoded = GSC.encode(msg1) #encoded to be sent

def example_2():
    isYellow = True
    GSC = GrSimRobotCommands(isYellow=isYellow) #remember ! ! always initialise this
    r1 = RobotCommand(1,2,3,4,1,0) 
    msg2 = GSC.convert(r1)
    # afterwards, you can pack and send it ! no problem
    encoded = GSC.encode(msg2)
    print(msg2,encoded)

def example_3():
    isYellow = True
    GSC = GrSimRobotCommands(isYellow=isYellow) #remember ! ! 
    # creating a new raw command
    msg3 = GSC.new_command(robot_id=1,vx=2.0,vy=1.0,w=1,k=1,d=1,us=False)
    print(msg3)
    encoded = GSC.encode(msg3) #encoded to be sent


def example_4():
    isYellow = True
    GSC = GrSimRobotCommands(isYellow=isYellow) #remember ! ! 
    # creating a new raw command
    GSC.update_is_yellow(not(isYellow))
    msg3 = GSC.new_command(robot_id=1,vx=2.0,vy=1.0,w=1,k=1,d=1,us=True)

    print(f"Before: {isYellow}, After: {GSC.isYellow},Packet is Yellow: {msg3.isteamyellow=}")

if __name__ == "__main__":
    example_1() # raw input method
    
    example_2() # converting robot commands into grSim commands
    
    example_3() # creating command for the opposite team
    
    example_4() # updating team color preset
    