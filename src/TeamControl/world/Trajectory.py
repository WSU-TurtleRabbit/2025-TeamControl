import time
import math
import numpy as np
import numpy as np
import matplotlib.pyplot as plt
try:
    from sklearn.linear_model import LinearRegression
except ModuleNotFoundError as e:
    raise ModuleNotFoundError ("please install scikit-learn for running trajectory")


def predict_trajectory(history: list, num_samples, isPostive:bool, field_size ):
    '''
        This function takes are input a list of ball positions and uses the last num_samples ball positions
        to fit a ball trajectory by applying a linear regression model. We then check whether this
        trajectory intercepts the goal line. If it does we send this information and the interception
        point to the goalie so the goalie can block the ball.

        History example: [{'x': -118.86381, 'y': 1343.0244}, {'x': -118.86381, 'y': 1343.0244}, ...]

        input:
            history: history of the last ball positions
            num_samples: number of samples that should be used to estimate the trajectory
        output:
            the position the the golie depending on the state of the ball 
    '''
    field_x, field_y =field_size
            # PARAMETERS
    #GOALIE_LINE = -FIELD_LENGTH/2 + 200 #mm #On the other side of the field if we are the other team
    if isPostive == True:
        goal_pos = field_x/2 - 200
    else:
        goal_pos = -field_x/2 + 200

    goal_width = 1000
    goal_line = goal_pos # the goal line is the x coordinates of the goals line 
    num_samples = 5
    #print(ball_pos)
    ball_pos_x = [pos[0] for pos in history]
    ball_pos_y = [pos[1] for pos in history]
    if len(history) <= 0:
        return
    
    # use all available ball positions
    last_ball_positions_x = ball_pos_x
    last_ball_positions_y = ball_pos_y

    # print(last_ball_positions_x)1
    # print(last_ball_positions_y)
    if True:
        model = LinearRegression()

        model.fit(np.array(last_ball_positions_x).reshape(-1, 1), last_ball_positions_y)

        # Generate trajectory points
        x_values = np.linspace(-field_x/2, field_x/2, 20) 

        current_ball_position_x = ball_pos_x[0]  # Current ball position

        trajectory_y_at_goal_line = model.predict(np.array([goal_line]).reshape(-1, 1))

        intersect_line = -goal_width / 2 <= trajectory_y_at_goal_line <= goal_width/ 2

        # Calculate intersection point if exists

        golie_pos = None

        # defult goal position is the fomation golie position.
    
        golie_pos = (goal_line, round(trajectory_y_at_goal_line.item()))
       
    return golie_pos, intersect_line
    