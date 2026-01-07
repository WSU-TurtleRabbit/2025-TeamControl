from collections import deque 
FRAME_HIST_LEN = 10
ball_hist = deque(maxlen = FRAME_HIST_LEN)

import numpy as np 
# Using vx = covariane(t,x) / variance(t) 
# Least Squares line fit 

def velocity_est(ball_hist, fps = 60):
    # Number of balls captured in ball history 
    N = len(ball_hist)
    
    if N < 2: 
        return 0.0, 0.0
    
    # Constant delta t 
    dt = 1.0/fps 

    # Time values from 0 to (N-1)dt
    t = np.arange(N)*dt

    # X and Y coordinates of balls in ball_hist
    xs = np.array([p[0] for p in ball_hist]) 
    ys = np.array([p[1] for p in ball_hist])    

    # Means 
    t_mean = t.mean() 
    x_mean = xs.mean()
    y_mean = ys.mean() 

    # Equation

    # Numerator (Covariance of distance and time)
    num_x = np.sum((t - t_mean) * (xs - x_mean))
    num_y = np.sum((t - t_mean) * (ys - y_mean))

    # Denominator (Variation in time) 
    den = np.sum((t - t_mean)**2)

    if den == 0:
        return 0.0, 0.0 
    
    vx = num_x/den
    vy = num_y/den

    print (f"Velocity Estimation: f{vx, vy}")
    return vx, vy 



# When receiving 