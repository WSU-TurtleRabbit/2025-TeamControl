from TeamControl.network.robot_command import RobotCommand
from TeamControl.robot.Movement import RobotMovement
from TeamControl.robot.PenaltyKick import moveBackToGoalLine, patrolGoalLine

from TeamControl.utils.goal_trajectory import predict_trajectory, goal_intersection
from TeamControl.world.velocity_to_intercept import velocity_to_intercept
from TeamControl.world.velocity_est import velocity_est
from TeamControl.world.transform_cords import world2robot

import time
# from TeamControl.voronoi_planner.voronoi_planner import VoronoiPlanner
 
# typings
from TeamControl.world.model import WorldModel
from TeamControl.SSL.vision.frame import Frame
from multiprocessing import Queue

import numpy as np 

class Goalie():
    def __init__(self,dispatch_q:Queue,wm:WorldModel,goalie_id,is_yellow):
        self.dispatch_q = dispatch_q
        self.is_yellow = is_yellow
        self.wm = wm
        self.id = goalie_id
        self.version = 0
        self.field_x = 9000 
        self.field_y = 6000
        self.goal_depth = 500
        self.is_positive = is_yellow
        self.ball_hist =list()
        self.neutral_x_pos = self.field_x/2-self.goal_depth if self.is_positive else -(self.field_x/2-self.goal_depth)

    def test(self):
        pass
    
    def run(self):            
        while True:     
            # if self.version <= self.wm.get_version():
            try: 
                frame = self.wm.get_latest_frame()
                robot = frame.get_yellow_robots(isYellow=self.is_yellow,robot_id=self.id)
                self.ball_hist = self.update_ball_history(10)

            
            except AttributeError:
                continue
            
            if len(self.ball_hist) < 10 or isinstance(robot,int):
                continue

            print(self.ball_hist)
            
            # goalie_points = predict_trajectory(self.ball_hist, 3, isPostive=self.is_positive, feild_size=(self.field_x,self.field_y))
        
            goalie_pos = robot.position
            
            # if goalie_points[1] == True:   
            #     # if there's a point go block           
            #     target_pos1 = world2robot(robot_position=goalie_pos,target_position=goalie_points[0])
            # else: #reset position
            #     target_pos1 = world2robot(robot_position=goalie_pos,target_position= (self.neutral_x_pos, 0))
                
            # # print("Relative Target : ", target_pos1)
            # vx1,vy1 = RobotMovement.go_To_Target(target_pos=target_pos1, stop_threshold=50)

            # implement vel 2 target threshold = 70 (inertia)

            outcome = velocity_to_intercept(self.ball_hist[-1], ball_hist = self.ball_hist)
            ball_pos = outcome[1]
            vx, vy,w = RobotMovement.velocity_to_target(robot_pos = goalie_pos, target = ball_pos, turning_target = ball_pos, stop_threshold = 90)
            
            ball_vel = velocity_est(self.ball_hist, fps =  60)
            if ball_vel > 50: # fast ball
                vx = vx * 2
            else:  # slow or not dangerous ball
                vy = vy * 2

            print(vx,vy)

            if outcome[0] == True: 
                command1 = RobotCommand(robot_id=self.id,vx=vx,vy=vy)

                 
                # puts command into queue
                self.dispatch_q.put((command1, 1)) # 0.1 seconds runtime

            # if all close to the ball ==> print (done, reached the target) ==> if ball - robot pos < 90
            if np.allclose(abs(goalie_pos[0] - ball_pos[0] + goalie_pos[1] - ball_pos[1]), 90):
                print("Blocked ball")
    
    def penalty_kick(self):
        # Step 1: Reposition to goal line 
        while True: 
            try: 
                frame = self.wm.get_latest_frame()
                robot = frame.get_yellow_robots(isYellow=self.is_yellow, robot_id=self.id)
                self.ball_hist = self.update_ball_history(10)
            except AttributeError:
                continue

            if len(self.ball_hist) < 10 or isinstance(robot, int):
                continue 
            goalie_pos = robot.position 
            ball_pos = self.ball_hist[-1]
            vx, vy, w = moveBackToGoalLine(goalie_pos, self.is_positive, ball_pos)
            self.dispatch_q.put((RobotCommand(robot_id=self.id, vx=vx, vy=vy, w=w), 1))

            if vx == 0 and vy == 0:  # arrived at goal line
                break
        
        # Step 2: Patrol goal line for 10 seconds 
        start_time = time.time()
        while time.time() - start_time < 10: 
            try:
                frame = self.wm.get_latest_frame()
                robot = frame.get_yellow_robots(isYellow=self.is_yellow, robot_id=self.id)
                self.ball_hist = self.update_ball_history(10)
            except AttributeError:
                continue

            if len(self.ball_hist) < 10 or isinstance(robot, int):
                continue

            goalie_pos = robot.position

            vx, vy, w = patrolGoalLine(goalie_pos, self.ball_hist, self.is_positive)
            self.dispatch_q.put((RobotCommand(robot_id=self.id, vx=vx, vy=vy, w=w), 1))
        
             
        
    def update_ball_history(self,n = 10): # null = last ball pos
        self.ball_hist = list()
        frames = self.wm.get_last_n_frames(n)
        l = len(frames)
        for i in range(l):
            ball_data = frames[i].ball
            if ball_data != None:
                # print(ball_data)
                self.ball_hist.append([ball_data.x,ball_data.y])
            else: 
                ball_data == self.ball_hist[-1]
        # print(len(self.ball_hist))
        return self.ball_hist
        
    
def run_goalie(dispatch_q,wm: WorldModel,goalie_id,is_yellow):
    g = Goalie(dispatch_q,wm,goalie_id=goalie_id,is_yellow=is_yellow)
    g.run()