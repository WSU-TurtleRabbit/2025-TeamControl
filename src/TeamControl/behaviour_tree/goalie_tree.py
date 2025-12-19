from TeamControl.behaviour_tree.common_trees import GetWorldPositionUpdate,SendRobotCommand,GetRobotIDPosition
from TeamControl.world.Trajectory import predict_trajectory
from TeamControl.world.transform_cords import world2robot
from TeamControl.network.robot_command import RobotCommand
from TeamControl.robot.Movement import RobotMovement

import py_trees
import numpy as np


class GoalieRunningSeq(py_trees.composites.Sequence):
    def __init__(self,wm,dispatch_q,goalie_id,isYellow,isPositive=None,logger=None):
        if logger is not None:
            self.logger = logger
        name="GoalieRunningSeq"
        self.wm = wm
        self.dispatch_q = dispatch_q
        self.robot_id = goalie_id
        self.isYellow = isYellow
        # use this if we have value for us on the Positive x side, otherwise use isYellow
        self.isPositive = isPositive if isPositive is not None else isYellow 
        self.bb = py_trees.blackboard.Client(name=name)
        super(GoalieRunningSeq, self).__init__(name=name,memory=True)

        
    def setup(self):
        # outline all variables here
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_hist", access=py_trees.common.Access.READ)
        self.bb.register_key(key="gamestate",access=py_trees.common.Access.READ)

        # write here if you want to 
        self.bb.register_key(key="robot_id",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isYellow",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isPositive",access=py_trees.common.Access.WRITE)
        self.bb.robot_id = self.robot_id
        self.bb.isPositive = self.isPositive
        self.bb.isYellow = self.isYellow
        
        self.add_children([
            # GetGameStatus(wm=self.wm),
            # get update on robots and current ball
            GetWorldPositionUpdate(wm=self.wm),
            GetBallHistory(wm=self.wm),
            GetRobotIDPosition(robot_id=self.robot_id),
            DoBallToGoalTrajectory(),
            RobotLookAtBall(),
            RobotGoToTarget(turn=True),
            SendRobotCommand(dispatcher_q=self.dispatch_q),
        ])
        
    def initialise(self):
        
        for c in self.children:
            c.setup()

class GetGameStatus(py_trees.behaviour.Behaviour):
    def __init__(self,wm):
        # use world model as the source of truth
        self.wm = wm
        self.current_game_state = "HALT"
        name = self.__class__.__name__
        self.bb = py_trees.blackboard.Client(name=name)

        super().__init__(name)
    
    def setup(self):
        self.bb.register_key(key="gamestate",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isPositive",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isYellow",access=py_trees.common.Access.WRITE)
    
    def update(self):
        new_game_state = self.wm.get_game_state()
        if new_game_state is not None:
            self.bb.gamestate = new_game_state
            if self.current_game_state != new_game_state:
                pass 
            self.bb.isPositive = self.wm.us_positive()
            self.bb.isYellow = self.wm.us_yellow()
            self.logger.info("[GetGameStatus] : Updated")
            return py_trees.common.Status.SUCCESS
        else:
            # no state available
            self.logger.info("[GetGameStatus] : No state")

            return py_trees.common.Status.FAILURE



class GetBallHistory(py_trees.behaviour.Behaviour):
    def __init__(self, wm, frames:int=10):
        """Get Ball History

        Args:
            wm (World Model): The shared Manager Proxy World Model
            frames (int, optional): The number of frames for ball history that we want to get. Defaults to 10.
        """
        self.wm = wm
        name = self.__class__.__name__
        self.num = frames
        self.bb = py_trees.blackboard.Client(name=name)

        super().__init__(name)

    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        self.bb.register_key(key="ball_hist", access=py_trees.common.Access.WRITE)
        
        
    def update(self):
        ball_hist = self.get_ball_hist(self.num)
        if ball_hist is not None:
            self.bb.ball_hist = ball_hist
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
        
    
    def get_ball_hist(self,n:int):
        self.ball_hist = list()
        frames = self.wm.get_last_n_frames(n)
        l = len(frames)
        for i in range(l):
            ball_data = frames[i].ball
            if ball_data != None:
                # print(ball_data)
                self.ball_hist.append([ball_data.x,ball_data.y])
        # print(len(self.ball_hist))
        return self.ball_hist
        

class DoBallToGoalTrajectory(py_trees.behaviour.Behaviour):
    
    def __init__(self,num_samples=3, field_x=9000, field_y=6000,penalty_depth=500,penalty_width=1000 ):
        self.ball_hist = None
        self.isPositive = None
        self.fieldsize = [field_x,field_y]
        self.penalty_depth = penalty_depth
        self.penalty_width = penalty_width
        self.num_samples = num_samples
        self.neutral_x_pos = None
        name = self.__class__.__name__
        self.bb = py_trees.blackboard.Client(name=name)
        super().__init__(name)

    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_hist",access=py_trees.common.Access.READ)
        self.bb.register_key(key="isPositive",access=py_trees.common.Access.READ)
        
        self.bb.register_key(key="target_pos",access=py_trees.common.Access.WRITE)
        
        
        
    def update(self):
        self.isPositive = self.bb.isPositive
        self.neutral_x_pos = (2 * (self.isPositive) - 1)*(self.fieldsize[0]/2-self.penalty_depth)
        if getattr(self.bb,"ball_hist"):
            ball_hist = self.bb.ball_hist
        
        if ball_hist is None :# or not existing vairable
            return py_trees.common.Status.FAILURE
        elif len(ball_hist) < self.num_samples:
            self.feedback_message = "Not enough samples"
            return py_trees.common.Status.FAILURE

        blocking_pos, has_intersection = predict_trajectory(history=ball_hist,
                                            num_samples=self.num_samples, 
                                            isPostive=self.isPositive,
                                            field_size=self.fieldsize)

            
        if has_intersection is True:
            # go to the point to block
            target_pos = blocking_pos
        else: #reset position
            target_pos = (self.neutral_x_pos,0)
        # updates target position
        self.bb.target_pos = target_pos
        
        return py_trees.common.Status.SUCCESS  
            
class RobotLookAtBall(py_trees.behaviour.Behaviour):
    
    def __init__(self):
        name = self.__class__.__name__
        self.bb = py_trees.blackboard.Client(name=name)
        super().__init__(name)
        
    def setup(self):
        self.bb.register_key(key="robot_id",access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_hist",access=py_trees.common.Access.READ)
        # writable
        self.bb.register_key(key="facing_pos",access=py_trees.common.Access.WRITE)
        
    def update(self):
        # get the newest ball and set as target
        self.bb.facing_pos = self.bb.ball_hist[0]        
        return py_trees.common.Status.SUCCESS

class RobotGoToTarget(py_trees.behaviour.Behaviour):
    def __init__(self,turn=False,stop_threshold=50):
        self.turn = turn
        self.stop_threshold = stop_threshold
        name = self.__class__.__name__
        self.bb = py_trees.blackboard.Client(name=name)
        super().__init__(name)
    
    def setup(self):
        self.bb.register_key(key="robot_id",access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_pos",access=py_trees.common.Access.READ)
        if self.turn is True:
            self.bb.register_key(key="facing_pos",access=py_trees.common.Access.WRITE)
            self.bb.facing_pos = None
        self.bb.register_key(key="command",access=py_trees.common.Access.WRITE)
        

    def update(self):
        robot_pos = self.bb.robot_pos
        target_pos = self.bb.target_pos
        
        if self.turn is True:
            facing_pos = self.bb.facing_pos if self.bb.facing_pos is not None else self.bb.target_pos
            print(facing_pos)
        vx,vy,w = RobotMovement.velocity_to_target(robot_pos=robot_pos,
                                                   target=target_pos,
                                                   turning_target=facing_pos,
                                                   stop_threshold=self.stop_threshold)
        
        self.bb.command = RobotCommand(self.bb.robot_id,
                                       vx,vy,w,
                                       dribble=False,
                                       kick=False)
        
        return py_trees.common.Status.SUCCESS
    