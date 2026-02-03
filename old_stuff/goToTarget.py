import time
'''
THIS HAS BEEN MOVED TO BEHAVIOUR.PY
'''
from TeamControl.world.transform_cords import *
import math
import numpy as np
c = time.localtime()
TIME = time.strftime("%H:%M:%S", c)

def old_turn_to_target(target:tuple[float,float], epsilon: float=0.15, speed: float = 5.0):
    '''
        This function returns an agular velocity. The goal is to turn the robot
        in such a way that it is facing the ball with its kicker side.

        input: 
            ball_position: ball position in the robot coordinate systen (e.g. (10mm,50mm))
            epsilon: Threshold for the orientation (orientation does not have to be zero to 
                     consider it correct -> avoids jitter)
    '''
    if target is None:
        return 0
    orientation_to_ball = np.arctan2(target[0], target[1])-np.pi/2

    if abs(orientation_to_ball) < epsilon:
        # to avoid jitter
        omega = 0
    elif abs(orientation_to_ball) > epsilon and abs(orientation_to_ball) < 4*epsilon:
        omega = -speed*np.sign(orientation_to_ball) * 0.5
    else:
        omega = -speed*np.sign(orientation_to_ball)
    return omega 



@staticmethod
def turn_to_target(
    target: tuple[float, float] | None = None,
    epsilon: float = 0.15,
    speed: float = 5.0,
    robotOmega: float | None = None,
) -> float:
    """
    Returns an angular velocity to rotate the robot so its forward axis
    points toward 'target' in *robot coordinates*.

    Robot frame:
      target[0] = x_forward
      target[1] = y_left
    """
    if target is None:
        return 0.0

    # ✅ Correct: atan2(y, x)
    angle = math.atan2(target[1], target[0])

    # Avoid jitter when almost aligned
    if abs(angle) < epsilon:
        omega = 0.0
    elif abs(angle) < 2 * epsilon:
        omega = speed * math.copysign(0.05, angle)
    else:
        omega = speed * math.copysign(0.5, angle)

    print("[turn_to_target] angle =", angle)
    return omega


def go_To_Target(target_pos: tuple[float,float], speed: int=1, stop_threshold:float=150):
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
