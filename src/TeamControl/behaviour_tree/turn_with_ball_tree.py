import py_trees

from TeamControl.behaviour_tree.test_tree import AlreadyLookingAtTarget, CalculateAngularVelocity
from TeamControl.behaviour_tree.common_trees import SendRobotCommand
from TeamControl.robot.velocity import Mode
import numpy as np

class TurnWithBallSelector(py_trees.composites.Selector):
    def __init__(self, wm, dispatcher_q, robot_id, isYellow, mode=Mode.Normal, logger=None):
        if logger is not None:
            self.logger = logger
                
            name="TurnWithBallSelector"
            self.wm=wm
            self.dispatcher_q = dispatcher_q
            self.robot_id = robot_id
            self.isYellow = isYellow            
            self.mode = mode
            self.logger = logger
            self.bb = py_trees.blackboard.Client(name=name)
            super().__init__(name=name, memory=True)
            
    def setup(self,**kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.WRITE)  
        self.bb.register_key(key="isYellow", access=py_trees.common.Access.WRITE)
        self.bb.robot_id = self.robot_id
        self.bb.isYellow = self.isYellow 
            
        self.add_children([
            FacingTargetWithBall(),
            RobotTurnWithBall(mode=self.mode),
            DoNothing()
        ])
    def initialise(self):
    
        for c in self.children:
            c.setup()
                
        
class FacingTargetWithBall(py_trees.composites.Sequence):
    def __init__(self, epsilon=0.15):
        super().__init__(name="FacingTargetWithBall", memory=True)
        self.bb = py_trees.blackboard.Client(name=self.name)
        
        self.add_children([
            HasBall(),
            AlreadyFacingTarget(epsilon=epsilon)
        ])

             
class RobotTurnWithBall(py_trees.composites.Sequence):
    def __init__(self, mode=Mode.Normal):
        super().__init__("RobotTurnWithBall")
        self.bb = py_trees.blackboard.Client(name=self.name)
        self.mode = mode

        self.add_children([
            HasBall(),
            MakeRobotTurnWithBall(),
        ])
    
    
class HasBall(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__("HasBall")
        self.bb = py_trees.blackboard.Client(name=self.name)
    
    def setup(self, logger=None):
        self.logger = logger or py_trees.logging.Level.INFO
        self.bb.register_key("has_ball", py_trees.common.Access.READ)

    def update(self):
        if getattr(self.bb, "has_ball", False):
            print("Has ball")
            return py_trees.common.Status.SUCCESS
        else:
            self.logger.info("Does not have ball")
            print("Does not have ball")
            return py_trees.common.Status.FAILURE
        
class AlreadyFacingTarget(AlreadyLookingAtTarget):
    def __init__(self,epsilon: float=0.15):
        super().__init__(epsilon=epsilon)
        self.name = "AlreadyFacingTarget"
        self.bb = py_trees.blackboard.Client(name=self.name)
# 1. call parent constructor
# 2. parent sets name = "AlreadyLookingAtTarget"
# 3. child overwrites name
    
    def setup(self,logger=None):
        super().setup(logger)
        self.bb.register_key("w_ball", py_trees.common.Access.WRITE)
        self.bb.register_key("can_kick", py_trees.common.Access.WRITE)
        self.bb.register_key("dribbler", py_trees.common.Access.WRITE)
    
   
    def update(self):

        status = super().update()
        if status == py_trees.common.Status.SUCCESS:
            self.bb.w_ball = 0
            self.bb.can_kick = True
            self.bb.dribbler = False
            print("Already facing target with ball, can kick")

        return status
        
        
class MakeRobotTurnWithBall(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__("MakeRobotTurnWithBall")
        self.bb = py_trees.blackboard.Client(name=self.name)
        self.bb.register_key("d_theta", py_trees.common.Access.READ)
        self.bb.register_key("w_ball", py_trees.common.Access.WRITE)
        self.bb.register_key("dribbler", py_trees.common.Access.WRITE)
        self.bb.register_key("kick", py_trees.common.Access.WRITE)

    def update(self):
            self.bb.w_ball =CalculateAngularVelocity(self.bb.d_theta)
            self.bb.dribbler = True
            self.bb.kick = False
            print(f"Turning with ball, angular velocity: {self.bb.w_ball}")
            return py_trees.common.Status.SUCCESS
       
            
    
class DoNothing(py_trees.behaviour.Behaviour):
    def __init__(self):
        name="DoNothing"
        super().__init__(name=name)
        self.bb = py_trees.blackboard.Client(name=name)
        self.bb.register_key("can_kick", py_trees.common.Access.WRITE)
        self.bb.register_key("w_ball", py_trees.common.Access.WRITE)
        self.bb.register_key("dribbler", py_trees.common.Access.WRITE)
    
    def update(self):
        self.bb.can_kick = False
        self.bb.w_ball = 0
        self.bb.dribbler = False
        print("Doing nothing")
        return py_trees.common.Status.SUCCESS