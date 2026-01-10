import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from enum import Enum,auto
# PARAMETERSAG
GOAL_WIDTH = 2760  # mm - Update this value based on actual goal width
FIELD_WIDTH = 2760  # mm
FIELD_LENGTH = 5040  # mm
FRAME_RATE = 60  # Hz
GOALIE_LINE = -1200  # mm

class TrajectoryType(Enum):
    MOVE_AWAY_FROM_GOAL = auto() # "Moving away from the goal"
    MOVE_TOWARDS_GOAL = auto() # "Moving towards the goal"
    NO_MOVEMENT_DETECTED = auto() # "Moving perpendicular to the goal/not moving"

# Plot
def plot_trajectory_w_goal(trajectory, ball_positions_x, ball_positions_y, intersects_line, intersection_point, direction_info, velocity, plot_enabled=True):
    '''
    This function plots the ball's trajectory, the goal line/area, and indicates whether there is an 
    intersection with the goal line. It also shows the direction of the ball's movement. All coordinates
    are in the field coordinate system and are in units of millimeters.

    Parameters:
        trajectory (list of tuples): set of (x, y) values for the estimated trajectory
        ball_positions_x (list of floats): x values of the observed ball positions
        ball_positions_y (list of floats): y values of the observed ball positions
        intersects_line (bool): indicates whether the ball trajectory intersects the goal line
        intersection_point (tuple): point(x, y) where the ball intersects with the goal line
        direction_info (str): information whether the ball is moving towards the goal, 
                             away from the goal, or perpendicular to the goal.
        velocity (float): velocity of the ball in mm/s.
        plot_enabled (bool, optional): whether to enable plotting, default is True.

    Returns:
        None
    '''

    if not plot_enabled:
        return
    
    # plot ball trajectory
    plt.plot([pos[0] for pos in trajectory], [pos[1] for pos in trajectory], label="Trajectory")
    
    # plot ball positions
    plt.scatter(ball_positions_x[:-1], ball_positions_y[:-1], color='gray', label='Previous Ball Positions')
    plt.scatter(ball_positions_x[-1], ball_positions_y[-1], color='orange', label='Current Ball Position')
    
    # plot vertical goal line x = -5040/2
    plt.axvline(x=GOALIE_LINE, color='r', linestyle='--', label="Goalie Line")
    
    # plot rectangular goal area as rectangle
    plt.fill_between([-FIELD_LENGTH/2, -FIELD_LENGTH/2 + 200], -GOAL_WIDTH/2, GOAL_WIDTH/2, color='r', alpha=0.1, label="Goal Area")

    # if trajectory intersects the line, print result
    if intersects_line:
        plt.scatter(*intersection_point, color='red', label='Intersection Point')
        plt.text(-100, -1200, f'Intersection: {intersection_point}, {direction_info}, Velocity: {velocity/1000} m/s', color='r', fontsize=10)
    else:
        plt.text(-100, -1200, 'No Intersection', color='g', fontsize=10)

    # plot settings
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Ball Trajectory and Goal Line Intersection')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.xlim(-FIELD_LENGTH/2, FIELD_LENGTH/2)
    plt.ylim(-FIELD_WIDTH/2, FIELD_WIDTH/2)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


def predict_trajectory(history, num_samples, calculate_velocity=False):
    '''
    This function predicts the trajectory of a ball based on its recent positions using linear regression.
    It also determines the direction of the ball's movement and optionally calculates its velocity.

    Parameters:
        history (list of dicts): A list of dictionaries containing the ball's recent positions. 
                                 Each dictionary has keys 'x' and 'y' for the coordinates.
        num_samples (int): The number of recent samples to use for predicting the trajectory.
        calculate_velocity (bool, optional): Whether to calculate the ball's velocity. Default is False.

    Returns:
        tuple: A tuple containing:
            - list of tuples: predicted trajectory as a list of (x, y) values.
            - str: Information about the ball's direction of movement.
            - float: The y-coordinate of the ball at the goalie line.
            - float or None: The velocity of the ball in mm/s, or None if not calculated.
    '''
    # ensure we have atleast 2 points to predict the line
    if len(history) < 2:
        return None, None, None, None

    # extract x and y coordinates from history
    ball_positions_x = [coord[0] for coord in history]
    ball_positions_y = [coord[1] for coord in history]

    # select last num_samples position for regression
    last_ball_positions_x = ball_positions_x[-num_samples:]
    last_ball_positions_y = ball_positions_y[-num_samples:]

    # Fit a linear regression model to selected positions
    model = LinearRegression()
    model.fit(np.array(last_ball_positions_x).reshape(-1, 1), last_ball_positions_y)
    
    # generate set of x values to predict trajectory
    x_values = np.linspace(-FIELD_LENGTH/2, FIELD_LENGTH/2, 20)
    y_values = model.predict(x_values.reshape(-1, 1))

    # determine current and previous x positions
    current_x = ball_positions_x[-1]
    previous_x = ball_positions_x[-2] if len(ball_positions_x) > 1 else current_x

    # determine the direction of ball's movement
    if GOALIE_LINE < 0:
        if current_x > previous_x:
            direction_info = TrajectoryType.MOVE_AWAY_FROM_GOAL
        elif current_x < previous_x:
            direction_info = TrajectoryType.MOVE_TOWARDS_GOAL
        else:
            direction_info = TrajectoryType.NO_MOVEMENT_DETECTED
    else:
        if current_x < previous_x:
            direction_info = TrajectoryType.MOVE_AWAY_FROM_GOAL
        elif current_x > previous_x:
            direction_info = TrajectoryType.MOVE_TOWARDS_GOAL
        else:
            direction_info = TrajectoryType.NO_MOVEMENT_DETECTED

    # predict y coordinates of the ball at the goalie line
    trajectory_y_at_goal_line = model.predict(np.array([GOALIE_LINE]).reshape(-1, 1))[0]
    
    # calculate velocity if requested
    velocity = None
    if calculate_velocity and len(ball_positions_x) > 1:
        delta_x = current_x - previous_x
        delta_y = ball_positions_y[-1] - ball_positions_y[-2]
        time_elapsed = 1 / FRAME_RATE
        velocity = np.sqrt((delta_x / time_elapsed) ** 2 + (delta_y / time_elapsed) ** 2)

    # Output predicted trajectory, direction info, y-coordinate at the goalie line, velocity
    return {
        "predicted_trajectory": list(zip(x_values, y_values)),
        "direction_info":direction_info,
        "trajectory_y_at_goal":trajectory_y_at_goal_line,
        "velocity": velocity
    }
   

def goal_intersection(trajectory_y_at_goal_line):
    """
    This function checks whether estimated ball trajectory intersects the goal line
    and calculates the intersection point if it exists.

    Parameters:
        trajectory_y_at_goal_line (float): y-coordinate where the estimated trajectory intersects
                                           the goal line.

    Returns:
        tuple:
            intersects_line (bool): indicates whether ball trajectory intersects the goal line.
            intersection_point (tuple): point (x, y) where ball intersects with the goal line
    """
    intersects_line = -GOAL_WIDTH / 2 <= trajectory_y_at_goal_line <= GOAL_WIDTH / 2
    intersection_point = (GOALIE_LINE, round(trajectory_y_at_goal_line))

    return intersects_line, intersection_point
