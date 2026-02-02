
import pygame
import math
import time

from TeamControl.network.sender import LockedSender
from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand

class Remote_robot():
    def __init__(self, robot_id=1, isYellow=True):  
        self.robot_id = robot_id
        self.us_yellow = isYellow
        robot_ip = "172.20.10.2"
        self.sender = LockedSender(ip=robot_ip,port=50514)
        # self.sender = grSimSender()
        


    def run_remote_control(self):
        speed = 0.1
        # vx,vy,vw,k,d = 0,0,0,0,0
        # dribbler_on = False
        pygame.init()
        screen = pygame.display.set_mode((400, 300))
        running = True
        while running:
            vx,vy,vw,k,d = 0,0,0,0,0
            pygame.event.pump()  # Process internal events

            keys = pygame.key.get_pressed()  # Get key states
            if keys[pygame.K_ESCAPE]:  # Close the program
                    running = False
                    
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                vx= +speed
                
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                vx = -speed
                
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                vy += +speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                vy += -speed                
            if keys[pygame.K_q] or keys[pygame.K_PAGEUP]:
                vw += +speed/(2*math.pi)
            if keys[pygame.K_e] or keys[pygame.K_PAGEDOWN]:
                vw += -speed/(2*math.pi)
            
            
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                vx = vx*10
                vy = vy*10
                vw = vw*5
                
            if keys[pygame.K_f]:
                k = 1
            # if keys[pygame.K_r]: #chip kick
            #     k = 2
            if keys[pygame.K_SPACE]:    
                d = 1
            
                                            
            Command = RobotCommand(robot_id=self.robot_id, vx=vx,vy=vy,w=vw,kick=k,dribble=d,isYellow=self.us_yellow)
            # if Command.vx == 0 and Command.vy == 0 and Command.w ==0 :
            #     continue # skips the command send
            self.sender.send(Command.encode())
            print("Command sent : ", Command)
            
            time.sleep(0.01)



if __name__ == "__main__":
    rc = Remote_robot()
    rc.run_remote_control()