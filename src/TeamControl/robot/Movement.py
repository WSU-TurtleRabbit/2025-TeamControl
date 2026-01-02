from TeamControl.world.transform_cords import *
from typing import Tuple, Union, List, Optional

import numpy as np
import math

class RobotMovement():
    
    @classmethod
    def velocity_to_target(cls,robot_pos: tuple[float, float, float],
                           target: tuple[float,float], 
                           turning_target:tuple[float, float] = None,
                           speed: float = 0.01
                           , stop_threshold = 150) -> tuple[float, float, float]: 
        '''
        Gets the velocity required for the robot go to position and trun to target
        '''
        if robot_pos is None:
            print("Robot pos is none")
            pass
        
        transTarget = world2robot(robot_pos, target)
        vx, vy = cls.go_To_Target(transTarget, stop_threshold = stop_threshold,speed=speed)
        if turning_target is None:
            w = 0
        else:
            transTurningTarget = world2robot(robot_pos, turning_target)
            w = cls.turn_to_target(transTurningTarget)
            
        return vx, vy, w
    
    @classmethod
    def goShootVelcoity(cls, robot_pos:tuple[float, float,float], target: tuple[float, float]):
        shooting_position = cls.shooting_pos(target)
        vx, vy, w = cls.velocity_to_target(robot_pos, shooting_position, target)
        return vx, vy, w
    
    @staticmethod
    def turn_to_target(target:tuple[float,float] =None, epsilon: float=0.15, speed: float = 0.005, robotOmega = None):
        '''
            This function returns an agular velocity. The goal is to turn the robot
            in such a way that it is facing the ball with its kicker side.

            input: 
                ball_position: ball position in the robot coordinate systen (e.g. (10mm,50mm))
                epsilon: Threshold for the orientation (orientation does not have to be zero to 
                        consider it correct -> avoids jitter)
        '''
        if target is None :
            return None
        orientation_to_ball = np.arctan2(target[0], target[1])-np.pi/2

        if abs(orientation_to_ball) < epsilon:
            # to avoid jitter
            omega = 0
        elif abs(orientation_to_ball) > epsilon and abs(orientation_to_ball) < 2 * epsilon:
            omega = -speed*np.sign(orientation_to_ball) * 0.05
        else:
            omega = speed*np.sign(orientation_to_ball)* 0.5
        
        print(orientation_to_ball)
        return omega 
    
    @staticmethod
    def go_To_Target(target_pos: tuple[float,float], speed: int=0.08, stop_threshold:float=150):
        """go To Target Position (in respect to Robot)
        if the distance is further away from stop_threshold,
        it will go to target position with calculated speed.

        Args:
            target_pos (tuple[float,float]): targeted position relative to robot
            speed (int, optional): Speed of Robot going to target. Defaults to 5.
            stop_threshold (float, optional): Distance range for robot to ignore. Defaults to 300.

        Returns:
            tuple[float,float]: velcocity x , velocity y
        """
        if target_pos is None:
            return 0,0
        distance = math.sqrt(target_pos[0]**2 + target_pos[1]**2)

        # print(distance)
        if distance > stop_threshold:
            vy:float = (target_pos[1] / distance) * speed
            vx:float = (target_pos[0] / distance) * speed
            return vx,vy
        else: 
            return 0,0

    @staticmethod
    def shooting_pos(ball_pos:tuple[float,float],shootingTarget: tuple[float,float], robot_offset = 500):
        '''
        This function returns the target position for a robot. It needs this
        to aim and shoot a ball.
        shootingTarget: target your aiming to shoot
        robot_offset: how far in front you want teh robot to be
        '''
        # Calculate direction vector from ball to target
        direction = np.array(shootingTarget) - np.array(ball_pos)
        
        # Normalize direction vector
        direction = direction.astype(float)  # Ensure direction vector is float
        direction = np.linalg.norm(direction)
        
        # Calculate robot position slightly behind the ball
        robot_position = np.array(ball_pos) - robot_offset * direction
        
        return robot_position
    
    
   

    @staticmethod 
    def calculate_target_position(target, ball, robot_offset):
        '''
            This function returns the target position for a robot. It needs this
            to aim and shoot a ball.
        '''
        # Calculate direction vector from ball to target
        direction = np.array(target) - np.array(ball)
        
        # Normalize direction vector
        direction = direction.astype(float)  # Ensure direction vector is float
        direction = np.linalg.norm(direction)
        
        # Calculate robot position slightly behind the ball
        robot_position = np.array(ball) - robot_offset * direction
        
        return robot_position
        

class Follow_path:
        def __init__(self):
            self.path = None
        def update_path(self, path:list):
            """
            Adds a path to follow
            Prams --> path as a list[x position , y position]
            """
            self.path = path
        
        def get_point(self, robot_pos:tuple[float, float]):
            '''
            Gets the fist point of a given path, will remove the first point once reached  
            Prams --> the robot position [x position , y position]
            '''
            if self.path == None:
                print("Please update the path before you call this function")
            else:
                x_y_diff = np.array(self.path[0]) - np.array(robot_pos)

                diff = np.sqrt(np.power(x_y_diff[0], 2) + np.power(x_y_diff[1], 2))

                if len(self.path) == 1:   # Checks if the path length is 1 
                    return self.path # paths become a singular point 
                elif diff < 0.5: # if we are close enough we just delete the cuurent point and move on to the next one so path[1] --> path[0] 
                    del self.path[0]
                    return self.path[0]
                else: #if we are transiation between paths 
                    return self.path[0]
                
class calculateBallVelocity:
    """
    step() returns a 2-tuple:
      (distance, speed)
    where:
      - distance : float            # world-frame distance to the ball
      - speed    : Optional[float]  # chosen speed (m/s), or None if unreachable
    """

    def __init__(self, time_threshold: float = 1.5): #emma to check threshhold 
        self.time_threshold = time_threshold
        self.speed_levels   = [0.02, 0.04, 0.06, 0.08, 0.10] #possible speedds

    def _pick_speed(self, distance: float) -> Optional[float]:
        # build (speed, time_needed) pairs
        options = [(v, distance / v) for v in self.speed_levels]
        # filter those that meet the time threshold
        valid = [v for v, t in options if t <= self.time_threshold]
        return min(valid) if valid else None

    def step(
        self,
        robot_pose: Tuple[float, float, float],
        ball_pos:   Tuple[float, float]
    ) -> Tuple[float, Optional[float]]:
        # 1) compute world-frame distance
        dx = ball_pos[0] - robot_pose[0]
        dy = ball_pos[1] - robot_pose[1]
        distance = math.hypot(dx, dy)

        # 2) choose a speed (or return  None if unreachable)
        speed = self._pick_speed(distance)

        return distance, speed
