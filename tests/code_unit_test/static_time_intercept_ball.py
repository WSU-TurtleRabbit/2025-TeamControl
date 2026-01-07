

from TeamControl.world.time_to_intercept import time_to_intercept
from TeamControl.world.velocity_est import velocity_est
from random import randint

def generate_ball_history(n:int):
    ball_hist = []
    for _ in range (n):
        x = randint(1,10)
        y = randint(1,10)
        ball_hist.append([x,y])
    
    return ball_hist

def ball_history_to_goal(n:int,goal_is_positive):
    ball_hist = []
    sign = -1 if goal_is_positive is False else 1
    for i in range (n):
        x = sign*i
        y = 0
        ball_hist.append([x,y])
    return ball_hist

def test_time_intercept_static():
    goal_is_positive = False # do check for both sides

    # ball_hist = generate_ball_history(10)
    ball_hist = ball_history_to_goal(10,goal_is_positive)
    print("ball history generated : ", ball_hist)
    t = time_to_intercept(ball_pos=ball_hist[-1],target=None, ball_hist=ball_hist)
    print(t)
    assert t is not None
    v_vector = velocity_est(ball_hist = ball_hist)
    print(v_vector)
    assert v_vector is not None


test_time_intercept_static()