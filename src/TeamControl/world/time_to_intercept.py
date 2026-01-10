from TeamControl.utils.goal_trajectory import predict_trajectory, goal_intersection,TrajectoryType
from TeamControl.world.velocity_est import velocity_est
import math as m 
# Assumptions 

# Assume that this function is only used for intersection with goal line only
# t = d/v
def time_to_intercept(ball_pos, target, ball_hist):
    
    # put calculate ball velocity here if you need ball vel
    
    result = predict_trajectory(history = ball_hist,num_samples = 10,)
    trajectory_y_at_goal_line = result["trajectory_y_at_goal"]
    direction_info = result["direction_info"]
    velocity = result["velocity"]

    
    intersects_line, intersection_point = goal_intersection(trajectory_y_at_goal_line)

    # Euclidean Distance
    dist = m.sqrt((ball_pos[0]- intersection_point[0])**2 + (ball_pos[1] - intersection_point[1])**2)

    # Speed (Velocity magnitude)
    
    vx, vy = velocity_est(ball_hist = ball_hist)
    v = m.sqrt(vx**2 + vy**2) 


    if  v==0 or direction_info == TrajectoryType.MOVE_AWAY_FROM_GOAL or intersects_line is False:
        return None
    
    print(f"Time to intercept: {dist/v}")
    return dist/v



if __name__ == "__main__": 
    ball_pos = [0,0]

    history = [ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos,ball_pos]
    ball_pos1 = [1,0]
    
    time_to_intercept(ball_pos, None, history)