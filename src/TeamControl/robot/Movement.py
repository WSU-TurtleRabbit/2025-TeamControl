import math
import numpy as np
from typing import Tuple, Optional, List

from TeamControl.world.transform_cords import world2robot

def wrap_to_pi(a) -> float:
    return (a + np.pi) % (2*np.pi) - np.pi
    
class RobotMovement:
    
    
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
            w = 0.0
        else:
            trans_turn_target = world2robot(robot_pos, turning_target)
            w = cls.turn_to_target(trans_turn_target)

        return vx, vy, w

    @staticmethod
    def turn_to_target(target:tuple[float,float] =None, epsilon: float=0.1, speed: float = 1, d_time:float = 1):
        '''
            This function returns an agular velocity. The goal is to turn the robot
            in such a way that it is facing the ball with its kicker side.

            input: 
                target: the relative target postition format: (x,y)
                epsilon: Threshold for the orientation (orientation does not have to be zero to 
                        consider it correct -> avoids jitter)
                speed: the average default speed 
                d_time : the time scaler for how fast we want to turn while going
        '''
        if target is None:
            return 0.0

        # Correct orientation for robot coordinate frame
        angle = math.atan2(target[1], target[0])
        
        if abs(angle)<epsilon:
            omega=0.0
        elif abs(angle)<0.18:
            omega=speed*math.copysign(1, angle)
        elif abs(angle)<0.7:
            omega=speed*2*math.copysign(1, angle)
        elif abs(angle)<1.57:
            omega=speed*3*math.copysign(1, angle)
        else:
            omega=speed*4*math.copysign(1, angle)
            
        return omega

        
    
    @staticmethod
    def behind_ball_point(ball, goal, buffer_radius):
        """
        ball  = (bx, by)
        goal  = (gx, gy)
        buffer_radius = distance of the behind-ball point from the ball

        Returns: (x, y) behind-ball target position
        """

        bx, by = ball
        gx, gy = goal

        # Direction vector from ball → goal
        dx = gx - bx
        dy = gy - by

        # Distance
        d = math.sqrt(dx**2 + dy**2) # is this dx2/dx**2
        if d == 0:
            raise ValueError("Ball and goal cannot be at the same point")

        # Normalize direction
        dx /= d
        dy /= d

        # Opposite direction (behind the ball)
        behind_x = bx - dx * buffer_radius
        behind_y = by - dy * buffer_radius

        return behind_x, behind_y
    
    @staticmethod
    def threshold_zone(distance:float)-> float:
        # return max speed allowed in that zone
        
        if distance < 1: #kicker zone
            return 0.0
        if distance < 300: #dribble zone
            return 0.04
        if distance < 500: #normal zone
            return 0.08
        return 0.1 #fast zone


    @staticmethod
    def go_To_Target(target_pos: tuple[float, float],
                     speed: float = 1.0,
                     stop_threshold: float = 150.0):

        if target_pos is None:
            return 0.0, 0.0
        
        

        dist = math.hypot(target_pos[0], target_pos[1])
        speed = RobotMovement.threshold_zone(dist)
        
        
        if dist<=0.0:
            return 0.0, 0.0
        
        vx = (target_pos[0] / dist) * speed
        vy = (target_pos[1] / dist) * speed
        
        return vx, vy


    @staticmethod
    def shooting_pos(ball_pos: tuple[float, float],
                     shootingTarget: tuple[float, float],
                     robot_offset: float = 200.0):

        direction = np.array(shootingTarget) - np.array(ball_pos)
        direction = direction.astype(float)  # Ensure direction vector is float
        norm = np.linalg.norm(direction)
        
        if norm == 0:
            return np.array(ball_pos, dtype=float)

        direction /= norm
        return np.array(ball_pos) - robot_offset * direction
    
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