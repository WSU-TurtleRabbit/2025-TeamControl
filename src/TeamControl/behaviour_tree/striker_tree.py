from time import time
from TeamControl.behaviour_tree.common_trees import GetWorldPositionUpdate,SendRobotCommand,GetRobotIDPosition
from TeamControl.behaviour_tree.goalie_tree import GetBallHistory
from TeamControl.behaviour_tree.test_tree import GoToTarget
from TeamControl.robot.striker import clamp
from TeamControl.world.Trajectory import predict_trajectory
from TeamControl.world.transform_cords import world2robot
from TeamControl.network.robot_command import RobotCommand
from TeamControl.robot.Movement import RobotMovement
from TeamControl.robot.velocity import turn_to_target,go_to_target,Mode

import py_trees
import numpy as np

class StrikerRunningSeq(py_trees.composites.Sequence):
    def __init__(self,wm,dispatcher_q,striker_id,isYellow,isPositive=None,logger=None):
        if logger is not None:
            self.logger = logger
        name="StrikerRunningSeq"
        self.wm = wm
        self.dispatcher_q = dispatcher_q
        self.robot_id = striker_id
        self.isYellow = isYellow  
    
        # use this if we have value for us on the Positive x side, otherwise use isYellow
        self.isPositive = isPositive if isPositive is not None else isYellow 
        self.bb = py_trees.blackboard.Client(name=name)
        super(StrikerRunningSeq, self).__init__(name=name,memory=True)

        
    def setup(self):
        # outline all variables here
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isYellow",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isPositive",access=py_trees.common.Access.WRITE)
        self.bb.robot_id=self.robot_id
        self.bb.isPositive = self.isPositive
        self.bb.isYellow = self.isYellow
        
        self.add_children([
            # GetGameStatus(wm=self.wm),
            # get update on robots and current ball
            GetWorldPositionUpdate(wm=self.wm),
            GetBallHistory(wm=self.wm),
            GetRobotIDPosition(),
            SetTargetToBall(),  # calculat target_pos
            TurnToTarget(mode=Mode.Percision),
            GoToTarget(threshold=150.0,mode=Mode.Percision),
            DribbleOrKick(dribble_threshold=130.0,kick_threshold=90.0,kick_angle=0.2),
            SendRobotCommand(dispatcher_q=self.dispatcher_q),
        ])
        
    def initialise(self):
        
        for c in self.children:
            c.setup()
        

class SetTargetToBall(py_trees.behaviour.Behaviour):
    """
    Computes distance and angle to a target for the striker.
    Writes target_pos, target_dist, and d_theta to the blackboard.
    """
    def __init__(self, target_pos=None):
        name = "SetTargetToBall"
        super().__init__(name)
        self.target_pos = target_pos
        self.bb = py_trees.blackboard.Client(name=name)
        
    def setup(self):
        self.bb.register_key("robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key("target_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key("facing_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key("ball_pos", access=py_trees.common.Access.READ)
        
    def update(self):
        self.bb.target_pos = self.bb.ball_pos
        self.bb.facing_pos = self.bb.target_pos
        return py_trees.common.Status.SUCCESS
    
    
def clamp(low, high, value):
    return max(low, min(high, value))
        
class TurnToTarget(py_trees.behaviour.Behaviour):
    def __init__(self, mode=Mode.Percision):
        name = "TurnToTarget"
        super().__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        self.mode=mode
        
    def setup(self):
        self.bb.register_key("robot_pos",access=py_trees.common.Access.READ) # in GetRobotIDPosition
        self.bb.register_key("target_pos", access=py_trees.common.Access.READ)
        self.bb.register_key("w",access=py_trees.common.Access.WRITE)
        self.bb.register_key("d_theta",access=py_trees.common.Access.WRITE)
        
    def update(self):
        w=turn_to_target(robot_pos=self.bb.robot_pos,
                         target_pos=self.bb.target_pos,
                         mode=self.mode)
        self.bb.w = w
        
        relative = world2robot(
            robot_position=self.bb.robot_pos,
            target_position=self.bb.target_pos
        )
        self.bb.d_theta = np.arctan2(relative[1], relative[0])
        
        return py_trees.common.Status.SUCCESS   
    
    
class DribbleOrKick(py_trees.composites.Selector):
    def __init__(self, dribble_threshold:float, kick_threshold:float, kick_angle:float):
        name = "Dribble Sequence"
        super(DribbleOrKick,self).__init__(name=name,memory=True)
        self.dribble_threshold = dribble_threshold
        self.kick_threshold = kick_threshold
        self.kick_angle = kick_angle
        self.bb = py_trees.blackboard.Client(name=name)

        self.add_children([
            Dribble(dribble_threshold=self.dribble_threshold),
            Kick(kick_threshold=self.kick_threshold,kick_angle=self.kick_angle)
        ])
        
def Dribble(dribble_threshold:float):
    dribble_seq = py_trees.composites.Sequence(name="Dribble Sequence",memory=True)
    dribble_seq.add_children([
        CanDribble(dribble_threshold=dribble_threshold),
        DoDribble()
    ])
    return dribble_seq
        
class CanDribble(py_trees.behaviour.Behaviour):
    def __init__(self, dribble_threshold:float):
        name = "Can Dribble"
        super().__init__(name)
        self.dribble_threshold = dribble_threshold
        self.bb = py_trees.blackboard.Client(name=name)
        
    
    def setup(self):
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_pos",access=py_trees.common.Access.READ)
        
    
    def update(self):
        relative_target_arr = world2robot(robot_position=self.bb.robot_pos, target_position=self.bb.target_pos)
        relative_distance = np.linalg.norm(relative_target_arr)       
        if relative_distance <= self.dribble_threshold:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
        
class DoDribble(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "Doing Dribble"
        super().__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        
    def setup(self):
        self.bb.register_key(key="dribble",access=py_trees.common.Access.WRITE)
    
    def update(self):
        self.bb.dribble = 1
        return py_trees.common.Status.SUCCESS
    
def Kick(kick_threshold:float,kick_angle:float):
    kick_seq = py_trees.composites.Sequence(name="Kick Sequence",memory=True)
    kick_seq.add_children([
        CanKick(kick_threshold=kick_threshold,kick_angle=kick_angle),
        DoKick()
    ])
    return kick_seq
    
# class KickSequence(py_trees.composites.Sequence):
#     def __init__(self, kick_threshold:float,kick_angle:float):
#         name = "Kick Sequence"
#         super(KickSequence,self).__init__(name=name,memory=True)
#         self.kick_threshold = kick_threshold
#         self.kick_angle = kick_angle
#         self.bb = py_trees.blackboard.Client(name=name)
        
#         self.add_children([
#             CanKick(kick_threshold=kick_threshold,kick_angle=kick_angle),
#             DoKick()
#         ])
        
    
class CanKick(py_trees.behaviour.Behaviour):
    def __init__(self, kick_threshold:float,kick_angle:float):
        name = "Can Kick"
        super().__init__(name)
        self.kick_threshold = kick_threshold
        self.kick_angle = kick_angle
        self.bb = py_trees.blackboard.Client(name=name)
        
    def setup(self):
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_pos",access=py_trees.common.Access.READ)
        \
        
    def update(self):
        relative_target_arr = world2robot(robot_position=self.bb.robot_pos, target_position=self.bb.target_pos)
        distance = np.linalg.norm(relative_target_arr)
        angle_diff = np.arctan2(relative_target_arr[1], relative_target_arr[0])
        
        if distance <= self.kick_threshold and abs(angle_diff) <= self.kick_angle:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class DoKick(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "Doing Kick"
        super().__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        
    def setup(self):
        self.bb.register_key(key="kick",access=py_trees.common.Access.WRITE)
    
    def update(self):
        self.bb.kick = 1
        return py_trees.common.Status.SUCCESS