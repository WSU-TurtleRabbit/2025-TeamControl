
from TeamControl.robot.Movement import RobotMovement
from TeamControl.network.robot_command import RobotCommand

import py_trees
import numpy as np


# class Treeroot(py_trees.trees.BehaviourTree):
#     def __init__(self, root:py_trees.behaviour.Behaviour):
#         super().__init__(root)
    


class MainTreeNode(py_trees.behaviour.Behaviour):
    def __init__(self,wm,dispatcher_q,output_queue=None):
        """
        This is the bottom node

        """
        name = "MainTreeNode"
        self.wm = wm
        self.dispatcher_q = dispatcher_q
        self.output_queue = output_queue
        super().__init__(name)

    def setup(self):
        self.add_children([
            # add child nodes here 
            go_to_ball_dummy(wm=self.wm,dispatcher_q=self.dispatcher_q)
        ])
        pass

    def initialise(self):
        pass

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status:py_trees.common.Status):
        pass
    
# this is for basic testing, it does not do anything 
class go_to_ball_dummy(py_trees.behaviour.Behaviour):
    def __init__(self,wm,dispatcher_q,robot_id:int=0):
        name = "go_to_ball_dummy"
        self.wm = wm
        self.dispatcher_q = dispatcher_q
        self.robot_id = robot_id
        super().__init__(name)
    
    def setup(self):
        self.version = self.wm.get_version()
        self.frame = None
        self.ball_last_known = (0,0)
        pass
    
    def initialise(self):
        pass
        
    def update(self) -> py_trees.common.Status:
        self.get_wm_update()
        if self.frame is not None and self.ball_last_known is not None:
            ball_pos = self.ball_last_known
            robot_pos = self.frame.get_yellow_robots(isYellow=True, robot_id=self.robot_id).position
            
            print(ball_pos,robot_pos)
            # here we would create a RobotCommand to go to the ball
            # for this dummy, we just print
            print(f"[go_to_ball_dummy] Commanding robot to go to ball at {ball_pos}")
            # only this will return success
            return py_trees.common.Status.SUCCESS
        # otherwise keep running
        elif self.frame is None:
            print("[go_to_ball_dummy] No frame ")
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.RUNNING
    
    # this is reusable. 
    def get_wm_update(self):
        new_version = self.wm.get_version()
        if self.version < new_version:
            self.version = new_version
            self.frame = self.wm.get_latest_frame()
            if self.frame is not None and self.frame.ball is not None:
                self.ball_last_known = self.frame.ball.position
                print(self.ball_last_known)



class GoToBallSequence(py_trees.composites.Sequence):
    def __init__(self,wm,dispatcher_q,robot_id:int=0):
        name = "GoToBallSequence"
        super().__init__(name,memory=True)
        self.wm = wm
        self.dispatcher_q = dispatcher_q
        self.robot_id = robot_id
        self.version = 0
        self.bb = py_trees.blackboard.Client()


    def setup(self):
        self.bb.register_key(key="robot_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos",access=py_trees.common.Access.READ)
        self.bb.register_key(key="command",access=py_trees.common.Access.READ)
        self.bb.register_key(key="our_robots",access=py_trees.common.Access.READ)
        self.bb.register_key(key="threshold",access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.WRITE)
        self.bb.robot_id = self.robot_id
        
        self.add_children([
            GetWorldPositionUpdate(self.wm),
            GetRobotIDPosition(),
            RobotNotAtBall(),
            CalculateRobotToBall(),
            SendRobotCommand(self.dispatcher_q),
            # MoveToBall(self.dispatcher_q,self.robot_id),
            # SendRobotCommand(self.dispatcher_q,self.robot_id)
        ])
    
    def initialise(self):
        for i in self.children:
            i.setup()
    
    # def get_wm_update(self):
    #     new_version = self.wm.get_version()
    #     if self.version < new_version:
    #         self.version = new_version
    #         self.frame = self.wm.get_latest_frame()
    #         if self.frame is not None:
    #             if self.frame.ball is not None:
    #                 self.ball_last_known = self.frame.ball.position
    #                 self.bb.ball_pos = self.ball_last_known
    #                 print(self.ball_last_known)
                    
    #             robot = self.frame.get_yellow_robots(isYellow=True, robot_id=self.robot_id)
    #             if not isinstance(robot,int):
    #                 self.bb.robot_pos = robot.position # this should give (x,y,theta)
        
class GetWorldPositionUpdate(py_trees.behaviour.Behaviour):
    def __init__(self,wm):
        name = "GetWorldPositionUpdate"
        self.wm = wm
        super().__init__(name)
    
    def setup(self):
        self.version = self.wm.get_version()
        self.frame = None
        self.ball_last_known = (0,0)
        self.bb = py_trees.blackboard.Client(name="GetWorldPositionUpdate")
        self.bb.register_key(key="ball_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.WRITE)
        pass
    
    def initialise(self):
        pass
        
    def update(self) -> py_trees.common.Status:
        new_version = self.wm.get_version()
        if self.version < new_version:
            self.version = new_version
            self.frame = self.wm.get_latest_frame()
            if self.frame is not None:
                if self.frame.ball is not None:
                    self.ball_last_known = self.frame.ball.position
                    self.bb.ball_pos = self.ball_last_known
                    print(self.ball_last_known)
                    our_robots = self.frame.get_yellow_robots(isYellow=True)
                    self.bb.our_robots = our_robots
                    
            return py_trees.common.Status.SUCCESS
        # otherwise keep running
        return py_trees.common.Status.RUNNING



class GetRobotIDPosition(py_trees.behaviour.Behaviour):
    def __init__(self,robot_id:int=0):
        name = "GetRobotIDPosition"
        super().__init__(name)
        
    
    def setup(self):
        self.bb = py_trees.blackboard.Client(name="GetRobotIDPosition")
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        pass
    
    def update(self) -> py_trees.common.Status:
        robot_id = self.bb.robot_id
        our_robots = self.bb.our_robots
        if our_robots is not None and isinstance(our_robots[robot_id],object):
            robot = our_robots[robot_id]
            self.bb.robot_pos = robot.position
            print(f"[GetRobotIDPosition] Robot {robot_id} position: {robot.position}")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE
    
class RobotNotAtBall(py_trees.behaviour.Behaviour):
    def __init__(self,threshold:float=50):
        name = "RobotNotAtBall"
        super().__init__(name)
    
    def setup(self):
        self.threshold = 180  # in mm
        # read values off mutual blackboard
        self.bb = py_trees.blackboard.Client(name="RobotNotAtBall")
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="threshold", access=py_trees.common.Access.WRITE)
        self.bb.threshold = self.threshold # sets threshold here

    
    def update(self) -> py_trees.common.Status:
        # check if robot is at ball
        robot_pos = self.bb.robot_pos[::2]  # only x,y
        ball_pos = self.bb.ball_pos
        if np.all(np.abs(robot_pos - ball_pos) <= self.threshold): # axis aligned
        # if np.linalg.norm(robot_pos - ball_pos) <= self.threshold: # euclidean
            return py_trees.common.Status.FAILURE
        else:
            return py_trees.common.Status.SUCCESS


class CalculateRobotToBall(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "CalculateRobotToBall"
        super().__init__(name)
    
    def setup(self):
        # read values off mutual blackboard
        self.bb = py_trees.blackboard.Client(name="CalculateRobotToBall")
        # values for calculating values
        self.bb.register_key(key="threshold", access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="command", access=py_trees.common.Access.WRITE)
        pass
    
    def update(self) -> py_trees.common.Status:
        robot_pos = self.bb.robot_pos
        ball_pos = self.bb.ball_pos
        if robot_pos is not None and ball_pos is not None:
            print(f"[CalculateRobotToBall] Calculating robot to ball at {ball_pos} from {robot_pos}")
            if np.array_equal(robot_pos, ball_pos):
                print("[CalculateRobotToBall] Robot is already at ball position")
                return py_trees.common.Status.FAILURE

            vx, vy, w = RobotMovement.velocity_to_target(robot_pos, ball_pos, stop_threshold=self.bb.threshold)
            # if vx != 0 or vy != 0 or w != 0:
            self.bb.command = RobotCommand(self.bb.robot_id, vx, vy, w, kick=False, dribble=False)
            print(self.bb.command)
            return py_trees.common.Status.SUCCESS
        # otherwise this is failure
        print("[CalculateRobotToBall] Missing robot or ball position")
        return py_trees.common.Status.FAILURE

class SendRobotCommand(py_trees.behaviour.Behaviour):
    def __init__(self,dispatcher_q,runtime=1):
        name = "SendRobotCommand"
        self.dispatcher_q = dispatcher_q
        self.runtime = runtime
        super().__init__(name)
    
    def setup(self):
        self.bb = py_trees.blackboard.Client(name="SendRobotCommand")
        self.bb.register_key(key="command", access=py_trees.common.Access.READ)
        pass
    
    def update(self) -> py_trees.common.Status:
        command = self.bb.command

        packet = (command, self.runtime)
        print(f"[SendRobotCommand] Sending command: {command}")
        if not self.dispatcher_q.full():
            self.dispatcher_q.put(packet)
            return py_trees.common.Status.SUCCESS
        else:
            print("[SendRobotCommand] Dispatcher queue is full, cannot send command")
            return py_trees.common.Status.FAILURE
        # this is always success until we put more stuff to check here.