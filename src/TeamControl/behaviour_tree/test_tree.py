
from TeamControl.robot.Movement import RobotMovement
from TeamControl.world.transform_cords import world2robot
from TeamControl.network.robot_command import RobotCommand
from TeamControl.behaviour_tree.common_trees import GetWorldPositionUpdate,GetRobotIDPosition
# from TeamControl.utils.Logger import LogSaver


import py_trees
import numpy as np
import math
import time

MAX_SPEED = 1

class TestTreeSeq(py_trees.composites.Sequence):
    def __init__(self,wm,dispatcher_q,robot_id:int,isYellow=True,isPositive=None,logger=None):
        color = "YELLOW" if isYellow is True else "BLUE"
        name = f"TestTreeSeq {robot_id},{color}"
        super().__init__(name,memory=True)
        if logger is not None:
            self.logger = logger
        self.robot_id = robot_id
        self.isYellow = isYellow
        self.isPositive = isPositive if isPositive is not None else isYellow
        self.bb = py_trees.blackboard.Client(name=name)
        self.wm = wm
        self.dispatcher_q = dispatcher_q


    def setup(self):
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos",access=py_trees.common.Access.READ)
        
        self.bb.register_key(key="command",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isYellow", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isPositive", access=py_trees.common.Access.WRITE)
        
        self.bb.robot_id = self.robot_id
        self.bb.isYellow = self.isYellow
        self.bb.isPositive = self.isPositive
        self.bb.command = RobotCommand(self.robot_id,isYellow=self.isYellow)
        
        
        self.add_children([
            GetWorldPositionUpdate(self.wm),
            GetRobotIDPosition(),
            GoToBallSeq(turn_to_ball=True),
            SendRobotCommand(self.dispatcher_q),
        ])
    
    def initialise(self):
        for i in self.children:
            i.setup()
        
        
class GoToBallSeq(py_trees.composites.Sequence):
    def __init__(self, turn_to_ball=True):
        name="GoToBall"
        self.turn_to_ball = turn_to_ball
        super().__init__(name,memory=True)
        self.bb = py_trees.blackboard.Client(name=name)
        if self.turn_to_ball:
            # self.add_child(LookAtTarget(facing_pos=[343.981232,-26.9238338],speed=MAX_SPEED/2))
            self.add_child(LookAtTarget(epsilon=0.1,
                                        speed=0.5))
        self.add_child(GoToTarget(threshold=70))
        self.add_child(DoDribbleKick(speed=MAX_SPEED/2,
                                     dribble_threshold=130,
                                     kick_threshold=90,
                                     kick_angle=0.2))
        
    def setup(self):
        
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_pos",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="facing_pos",access=py_trees.common.Access.WRITE)
        
    def initialise(self):
        # if getattr(self.bb)
        self.bb.target_pos = self.bb.ball_pos
        if self.turn_to_ball is True:
            self.bb.facing_pos = self.bb.ball_pos
        for i in self.children:
            i.setup()

        
class LookAtTarget(py_trees.composites.Selector):
    
    def __init__(self,  
                 facing_pos:tuple[float,float]=None,
                 epsilon:float=0.015,
                 speed:float=0.05
                ):
        name = f"look_at_Target"
        super().__init__(name,memory=True)        
        self.b1 = py_trees.blackboard.Client(name=name)
        
        self.facing_pos = facing_pos    
        
        self.add_children([
            AlreadyLookingAtTarget(epsilon=epsilon),
            CalculateAngularVelocity(epsilon=epsilon,speed=speed)
        ])
    
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        
        self.b1.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.b1.register_key(key="target_pos",access=py_trees.common.Access.READ)
        self.b1.register_key(key="facing_pos",access=py_trees.common.Access.WRITE)
        self.b1.register_key(key="new_dir",access=py_trees.common.Access.WRITE)
        if self.facing_pos is not None:
            self.b1.facing_pos = self.facing_pos 
    

    def initialise(self):
        if self.facing_pos is None:
            self.b1.facing_pos = self.b1.target_pos
        
        current_pos = self.b1.robot_pos
        target_pos = self.b1.facing_pos
        self.b1.new_dir = world2robot(robot_position=current_pos,target_position=target_pos)

        
        for i in self.children:
            i.setup(self.logger)


class AlreadyLookingAtTarget(py_trees.behaviour.Behaviour):
    def __init__(self,epsilon: float=0.15):
        self.epsilon = epsilon
        name = "AlreadyLookingAtTarget"
        self.bb = py_trees.blackboard.Client(name=name)
        super().__init__(name)
    
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        # read values off mutual blackboard
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)

        self.bb.register_key(key="new_dir",access=py_trees.common.Access.READ)
        self.bb.register_key(key="d_theta",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="w",access=py_trees.common.Access.WRITE)
    
    def wrap_to_pi(self,a) -> float:
        return (a + np.pi) % (2*np.pi) - np.pi
    
    def update(self) -> py_trees.common.Status:
        # check if robot is at ball
        trans_pos = self.bb.new_dir
        new_orientation = self.wrap_to_pi(np.arctan2(trans_pos[1],trans_pos[0]))
        
        self.bb.d_theta = new_orientation  
        # print(self.bb.d_theta,new_orientation,self.bb.robot_pos[2])

        if abs(self.bb.d_theta) < self.epsilon: #smaller than threshold
            self.logger.info("Already looking at target")
            self.bb.w = 0
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE




class CalculateAngularVelocity(py_trees.behaviour.Behaviour):
    def __init__(self,speed:float,epsilon: float=0.15,d_time:float = 1):
        self.epsilon = epsilon
        self.speed = speed
        self.d_time = d_time
        name = "CalculateAngularVelocity"
        self.bb = py_trees.blackboard.Client(name=name)
        super().__init__(name)
    
    def clamp (self,val):
        return max(-self.speed, min(self.speed,val))

    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        # read values off mutual blackboard
        self.bb.register_key(key="d_theta",access=py_trees.common.Access.READ)
        self.bb.register_key(key="w",access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        # calculate w        
        d_time = self.d_time
        d_theta = self.bb.d_theta 
        if abs(d_theta) > self.epsilon*2:
            w = d_theta * self.speed*5
        else:
            w = d_theta * self.speed *1 

        self.bb.w = self.clamp(w)      
        
        return py_trees.common.Status.SUCCESS
        
 
  
class GoToTarget(py_trees.composites.Selector):
    def __init__(self,threshold:int=150,speed=1):
        name = f"Go_To_Target"
        super().__init__(name,memory=True)
        self.b1 = py_trees.blackboard.Client(name=name)

        self.threshold = threshold
        
        self.add_children([
            # check if it is at target
            AlreadyAtTarget(threshold=threshold),
            # otherwise calculate the velocity to target
            CalculateLinearVelocity(threshold=threshold,speed=speed)
        ]) 
        
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
            
        self.b1.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.b1.register_key(key="target_pos",access=py_trees.common.Access.READ)
        self.b1.register_key(key="trans_pos",access=py_trees.common.Access.WRITE)
               
    

    def initialise(self):
        current_pos = self.b1.robot_pos
        target_pos = self.b1.target_pos
        self.b1.trans_pos = world2robot(robot_position=current_pos,target_position=target_pos)
        for i in self.children:
            i.setup(self.logger)

        
        
class AlreadyAtTarget(py_trees.behaviour.Behaviour):
    def __init__(self,threshold:float=300):
        self.threshold = threshold
        name = "RobotAtTarget"
        self.bb = py_trees.blackboard.Client(name=name)

        super().__init__(name)
    
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        # read values off mutual blackboard
        self.bb.register_key(key="trans_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_dist",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="vx",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="vy",access=py_trees.common.Access.WRITE)
    
    def update(self) -> py_trees.common.Status:
        # check if robot is at ball
        trans_pos = self.bb.trans_pos
        distance = math.sqrt(trans_pos[0]**2 + trans_pos[1]**2)
        self.bb.target_dist = distance
        
        if distance <= self.threshold: 
            self.logger.info("Already At Target")
            self.bb.vx,self.bb.vy = 0,0
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class CalculateLinearVelocity(py_trees.behaviour.Behaviour):
    def __init__(self,threshold:float,speed:float):
        name = "CalculateLinearVelocity"
        self.bb = py_trees.blackboard.Client(name=name)
        self.threshold = threshold
        self.speed = speed
        # self.cnt = 0
        super().__init__(name)
    
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        # read values off mutual blackboard
        # values for calculating values
        self.bb.register_key(key="trans_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="d_theta",access=py_trees.common.Access.READ)
        self.bb.register_key(key="target_dist", access=py_trees.common.Access.READ)
        self.bb.register_key(key="vx", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="vy", access=py_trees.common.Access.WRITE)
        
    
    def update(self) -> py_trees.common.Status:
        trans_pos = self.bb.trans_pos
        angle_diff = self.bb.d_theta

        distance = self.bb.target_dist
        if abs(angle_diff) > 0.1 :
            self.threshold = 200 
        else:
            self.threshold = 70 
        speed = RobotMovement.threshold_zone(distance,MAX_SPEED)
        
        # print(distance)
        if distance > self.threshold:
            self.bb.vy:float = (trans_pos[1] / distance) * speed
            self.bb.vx:float = (trans_pos[0] / distance) * speed
        else:
            self.bb.vx =0 
            self.bb.vy =0 
        return py_trees.common.Status.SUCCESS
        
        # otherwise this is failure
        print("[CalculateRobotToBall] threshold error")
        return py_trees.common.Status.FAILURE

class DoDribbleKick(py_trees.behaviour.Behaviour):
    def __init__(self, speed:float,dribble_threshold:float,kick_threshold:float,kick_angle:float):
        name = "Doing Dribble Kick"
        super().__init__(name)
        self.dribble_threshold = dribble_threshold
        self.kick_threshold = kick_threshold
        self.kick_angle = kick_angle
        self.start_time = 0
        self.cnt = 0
        self.has_ball = False
        self.speed = speed
        self.bb = py_trees.blackboard.Client(name=name)
        self.bb.register_key(key="dribble",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="kick",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="vx",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="vy",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="w",access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="target_dist",access=py_trees.common.Access.READ)
        self.bb.register_key(key="trans_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="d_theta",access=py_trees.common.Access.READ)
        
    
    def update(self):
        dribble =0
        kick = 0
        distance = self.bb.target_dist 
        angle_diff = self.bb.d_theta
        print("distance",distance, " angle ",angle_diff)
                
        if distance <= self.dribble_threshold and abs(angle_diff) <= self.kick_angle:
            self.logger.info("DRIBBLING")
            dribble = 1
            self.bb.vx = 0.1
            

            if self.start_time == 0:
                self.logger.info("START_TIMER_____")
                self.start_time = time.time()
                self.has_ball = True

                print(f"time diff {self.start_time - time.time()}")
            if self.start_time + 0.5 <= time.time():
                self.logger.info("KICK")
                self.start_time = 0
                dribble = 0 
                kick = 1 
                self.has_ball = False

        else :
            dribble = 0
            self.start_time = 0

            if self.has_ball is True:
                kick = 1 
                self.logger.info("KICK ANYWAYS")

                self.has_ball = False


        self.bb.dribble = dribble
        self.bb.kick = kick

            # starts dribble
        #     self.dribble = True
        #     self.bb.vx,self.bb.vy = 0,0
        #     self.bb.w = 0
        # if self.dribble is True:
        #     self.bb.dribble = 1 
        #     self.cnt += 1
        #     print(self.cnt) 
        # if self.cnt >= 5 :
        #     self.bb.dribble = 0
        #     self.bb.kick = 1
        #     self.cnt = 0
        #     self.dribble = False
        # if self.dribble is False:
        #     self.bb.dribble = 0

        #     if self.dribble_time == 0 : 
        #         self.logger.info("DRIBBLING")
        #         self.dribble_time = time.time()
        #     elif self.dribble_time +1 <= time.time():
        #         self.bb.dribble = 0

        #     elif self.dribble_time + 2 <= time.time():
        #     # elif self.dribble_time + 2 <= time.time() or distance <= self.kick_threshold:
        #         self.logger.info("KICK")

        #         self.dribble_time = 0
        #         self.bb.dribble = 0
        #         self.bb.vx,self.bb.vy = 0,0
        #         self.bb.kick = 1 
        # else:
        #     self.dribble_time = 0
        #     self.bb.kick = 0
        #     self.bb.dribble = 0
        #     self.logger.info("NO DRIBBLE")

            
        return py_trees.common.Status.SUCCESS

        
## temp

class SendRobotCommand(py_trees.behaviour.Behaviour):
    def __init__(self,dispatcher_q,runtime=2):
        name = "SendRobotCommand"
        self.dispatcher_q = dispatcher_q
        self.runtime = runtime
        super().__init__(name)
    
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        self.bb = py_trees.blackboard.Client(name="SendRobotCommand")
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="isYellow", access=py_trees.common.Access.READ)
        self.bb.register_key(key="vx", access=py_trees.common.Access.READ)
        self.bb.register_key(key="vy", access=py_trees.common.Access.READ)
        self.bb.register_key(key="w", access=py_trees.common.Access.READ)
        self.bb.register_key(key="kick", access=py_trees.common.Access.READ)
        self.bb.register_key(key="dribble", access=py_trees.common.Access.READ)
        self.bb.register_key(key="command", access=py_trees.common.Access.WRITE)
        
        # preset 
        self.last_command = self.bb.command
        
        
    def initialise(self):
        robot_id = self.bb.robot_id
        isYellow = self.bb.isYellow
        vx = self.bb.vx if self.bb.exists("vx") else 0.0
        vy = self.bb.vy if self.bb.exists("vy") else 0.0
        w = self.bb.w if self.bb.exists("w") else 0.0
        kick = self.bb.kick if self.bb.exists("kick") else 0
        dribble = self.bb.dribble if self.bb.exists("dribble") else 0
        self.bb.command = RobotCommand(robot_id=robot_id,
                                   vx=vx,vy=vy,w=w,
                                   kick=kick,dribble=dribble,
                                   isYellow=isYellow
                                   ) 
        
    
    
    def update(self) -> py_trees.common.Status:
        command = self.bb.command
        # if self.last_command.to_dict() == command.to_dict() : 
        #     print(f"[SendRobotCommand] No new command")
        #     return py_trees.common.Status.SUCCESS
        
        packet = (command, self.runtime)
        # print(f"[SendRobotCommand] Sending command: {command}")
        if not self.dispatcher_q.full():
            self.dispatcher_q.put(packet)
            self.last_command = command
            return py_trees.common.Status.SUCCESS
        
        else:
            print("[SendRobotCommand] Dispatcher queue is full, cannot send command")
            return py_trees.common.Status.FAILURE
        # this is always success until we put more stuff to check here.
        
