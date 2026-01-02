## how to run stuff to send to grSim ### 
## 1. create the socket for recving and sending
from TeamControl.network.ssl_sockets import grSimPacketFactory,grSimSender,RobotCommand

import time


SIM_IP = "127.0.0.1" 
SIM_COMMAND_LISTENING_PORT = 20010
SENDER = grSimSender(ip=SIM_IP , port=SIM_COMMAND_LISTENING_PORT)
SPEED = 1
def example_1():
    print("Example of Creating a robot command in grSim")
    time.sleep(SPEED)
    print("First, we create the robot_command using grSimPacketFactory.robot_command")
    packet = grSimPacketFactory.robot_command(robot_id=0,vx=2,vy=0,w=0,kick=0,dribble=0,isYellow=False)
    print(f"grSim command created : {packet}") 
    time.sleep(SPEED)
    print(f"now we have this packet with type : {type(packet)}, we will send it into the simulator")
    time.sleep(SPEED)
    print(f"to see a continuous result, we will need to be recreating this packet every iteration")
    print(f"hence the following will demonstrate for 3 seconds")
    end_time = time.time() + 3
    while time.time() < end_time :
        packet = grSimPacketFactory.robot_command(robot_id=0,vx=1,vy=0,w=0,kick=0,dribble=0,isYellow=False)
        SENDER.send_packet(packet) 
        
                
def example_2():
    print("Example of Converting an existing robot command in grSim")
    time.sleep(SPEED)
    print("First, we generate a random robot_command with RobotCommand")
    robot_command = RobotCommand(robot_id=0,vx=2,vy=3,w=4,kick=1,dribble=0,isYellow=True) 
    # use this function to directly send the robot command to the simulation
    print(f"now we have this robot_command with type : {type(robot_command)}, we cannot use the function send_packet() because it's not a packet")
    time.sleep(SPEED)
    print(f"instead, we will be using the function send_robot_command()")
    time.sleep(SPEED)
    print(f"This allows us to convert the command and send it away ")
    print(f"to see a better result, we will be sending this to the robot for 1 s")
    end_time = time.time() + 3
    while time.time() < end_time :
        
        SENDER.send_robot_command(robot_command)
    

def example_3():

    print("Example of robot replacement")
    time.sleep(SPEED)
    print("First, we will list out what we want to do with what robot")

    robot_isYellow = True
    robot_id = 0
    x,y,o = 1,0,3.14

    print(f'''
    {robot_isYellow=}
    {robot_id=}
    {x,y,o=}
          ''')
    
    time.sleep(SPEED)
    print(f"Next, we generate the robot replacement packet using : grSimPacketFactory.robot_replacement_command ")
    packet = grSimPacketFactory.robot_replacement_command(
        x=x,y=y,orientation=o,robot_id=robot_id,isYellow=robot_isYellow
    )
    print(f"now we have this packet with type : {type(packet)}, we will send it into the simulator")
    time.sleep(SPEED)
    SENDER.send_packet(packet)
    print(f"Now the packet has been sent, the robot {robot_id} should have been repositioned")


def example_4():
    ball_x,ball_y = 0,0
    ball_vx,ball_vy = 1.0,1.0
    print("Example of ball_replacement")
    time.sleep(SPEED)
    print("we are going to place to ball at a certain location where")
    time.sleep(SPEED)
    print(f"{ball_x=}, {ball_y=} with a velocity of x:{ball_vx},{ball_vy}")
    time.sleep(SPEED)
    packet = grSimPacketFactory.ball_replacement_command(
        x=ball_x,y=ball_y,vx=ball_vx,vy=ball_vy
    )
    print(f"{packet=} has been generated")
    time.sleep(SPEED)
    print("now the packet has been created, we shall send it out with the sender")
    time.sleep(SPEED)
    print(f"since it is type : {type(packet)}, we can use the send_packet() command to send it ")
    SENDER.send_packet(packet)
    print("packet has been sent, the ball should have been repositioned")
    time.sleep(SPEED)


if __name__ == "__main__":
    list_of_examples = [example_1,example_2,example_3,example_4]
    for example in list_of_examples:
        print("Begining example : ", example.__name__)
        example()
        print("Example Completed")
        time.sleep(5)
