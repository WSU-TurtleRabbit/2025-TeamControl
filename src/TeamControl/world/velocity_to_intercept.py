from TeamControl.utils.goal_trajectory import predict_trajectory, goal_intersection,TrajectoryType
from TeamControl.world.velocity_est import velocity_est
import math as m 
import numpy as np 
# Assumptions 

# Assume that this function is only used for intersection with goal line only
# t = d/v
def velocity_to_intercept(ball_pos, ball_hist, ball_seen = True):
    
    # put calculate ball velocity here if you need ball vel
    print(ball_hist)
    result = predict_trajectory(history = ball_hist,num_samples = 10,calculate_velocity = True)
    trajectory_y_at_goal_line = result["trajectory_y_at_goal"]
    direction_info = result["direction_info"]
    # velocity = result["velocity"]
    
    intersects_line, intersection_point = goal_intersection(trajectory_y_at_goal_line)

    # Euclidean Distance
    dist = m.sqrt((ball_pos[0]- intersection_point[0])**2 + (ball_pos[1] - intersection_point[1])**2)

    # Speed (Velocity magnitude)
    
    velocity = velocity_est(ball_hist = ball_hist)

    # if np.allclose(velocity, v): 
    #     return True 

    print(velocity, direction_info, intersects_line)
    # if velocity== 0 or direction_info == TrajectoryType.MOVE_AWAY_FROM_GOAL or intersects_line is False:
    #     return None
    
    # print(f"Time to intercept: {dist/velocity}")
    outcomes = [intersects_line, intersection_point]
    return outcomes



if __name__ == "__main__": 
    ball_pos = [1,1]

    history = [ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos]
    ball_pos1 = [1,2]
    
    print(velocity_to_intercept(ball_pos, None, history))