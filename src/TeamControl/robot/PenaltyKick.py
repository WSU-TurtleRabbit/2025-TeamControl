from TeamControl.robot.Movement import RobotMovement
from TeamControl.world.transform_cords import world2robot
from TeamControl.utils.goal_trajectory import predict_trajectory, goal_intersection, TrajectoryType
from TeamControl.world.velocity_est import velocity_est
''' 
1. Fundamental penalty kick rules:
-  Firstly, ball is placed on the penalty mark:
+ Goalie has to move to the goal line and keep touching the goal line 
+ One attacking robot is allowed to approach the ball but not touch it 
- Every other robots have to be 1m behind the ball 
- When normal start command is issued ==> attacker could manipulate the ball, but could only navigate the ball
towards the opponent goal (as measured by x coordinate) ==> goalie could move freely 
- After the start, the procedure lasts for 10 seconds at maximum 

2. Penalty goal is awarded when:
- Ball touches inner surface of a goal wall/ the ground of the goal of the defending team
- Defending team commits any foul

3. Penalty goal is not awarded when:
- Ball crosses any field lines outside the goal
- Goalie deflects the ball ==> ball speed vector changes direction by at least 90 degrees in 2D space 
- Attack team commits any foul 
- Ball still in play after 10 seconds 

==> Goalie requirements: 
- Goalie moves to the goal line (go to middle and drag back) at command
- Goalie predicts ball trajectory (use predict_trajectory function)
- Goalie adjusts speed according to the ball's speed
- Maintain the state of predicting ball's trajectory in 10 seconds (the ball might be deflected but still moving towards the goal)
'''
DEFENSE_AREA_WIDTH = 1000
DEFENSE_AREA_LENGTH = 2000
FIELD_X = 9000
FIELD_Y = 6000
GOAL_DEPTH = 160
GOAL_WIDTH = 1000

ROBOT_DIAMETER = 180
FAST_BALL = 50
SLOW_BALL = 10

# Step 1: Goalie moves back to goal line 
def moveBackToGoalLine(robot_pos: tuple, is_positive: bool, ball_pos: tuple = None, stop_threshold: int = 150) -> tuple:
    """
    Goalie repositions to goal line 
    Args: 
        robot_pos: Robot position (x,y,w) in world2robot frame
        is_positive: True if defending positive-x goal, False if negative-x goal 
        ball_pos: Ball positions (x,y) in world2robot frame. Goalie faces ball when moving
        stop_threshold: Threshold where robot determines that it arrived
    
    Returns:
        (vx,vy,w): Velocity commands to send via RobotCommand
    """

    goal_line_x = (FIELD_X/2) if is_positive else -(FIELD_X/2)
    goal_line_center = (goal_line_x, 0)

    vx,vy,w = RobotMovement.velocity_to_target(
        robot_pos = robot_pos,
        target = goal_line_center,
        turning_target = ball_pos,
        stop_threshold= ROBOT_DIAMETER/2
    )

    return vx,vy,w 

# Step 2: Patrol the goal line to intercept the ball 
def patrolGoalLine(robot_pos: tuple, ball_hist: list, is_positive: bool) -> tuple: 
    """
    Moves keeper laterally along the goal line to intercept the ball regarding the predicted ball trajectory
    Called constantly after repositioning back to the goal line
    Args: 
        robot_pos: Robot position (x,y,w) in world frame 
        ball_hist: List of recent ball positions [[x,y], ...]
        is_positive: True if defending positive-x goal, False if negative-x
    Returns: 
        (vx,vy,w): Velocity commands to send via RobotCommand. 
    """

    goal_line_x = (FIELD_X/2) if is_positive else -(FIELD_X/2)
    # trajectory prediction 
    result = predict_trajectory(ball_hist, num_samples = 5)
    direction = result["direction_info"]
    trajectory_y = result["trajectory_y_at_goal"]

    # if ball is not threatening, hold center 
    if direction != TrajectoryType.MOVE_TOWARDS_GOAL:
        target_y = 0
    # otherwise, block the ball
    else: 
        half_goal = GOAL_WIDTH/2 
        target_y = max(-half_goal, min(half_goal, trajectory_y))
    vx, vy, w = RobotMovement.velocity_to_target(
        robot_pos=robot_pos,
        target=(goal_line_x, target_y),
        turning_target=None,
        stop_threshold=ROBOT_DIAMETER / 2,
    )

    vx = 0  # lock x: keeper must not leave the goal line

    # boost lateral speed based on ball speed
    ball_vel = velocity_est(ball_hist, fps=60)
    if ball_vel >= FAST_BALL:  # fast ball, react quickly
        vy = vy * 2
    elif ball_vel <= SLOW_BALL: # slow ball, react slowly
        vy = vy / 2

    return vx, vy, w

# Maintain the state for 10 secs ==> implement into goalie.py 



    
    





