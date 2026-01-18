from TeamControl.network.robot_command import RobotCommand
import py_trees
import numpy as np

class GetWorldPositionUpdate(py_trees.behaviour.Behaviour):
    def __init__(self,wm):
        name = "GetWorldPositionUpdate"
        self.wm = wm
        super().__init__(name)
    
    def setup(self,logger=None):
        if logger is not None: # use this instead
            self.logger = logger 
        self.version = self.wm.get_version()
        self.frame = None
        self.ball_last_known = (0,0)
        self.bb = py_trees.blackboard.Client(name="GetWorldPositionUpdate")
        self.bb.register_key(key="ball_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="isYellow", access=py_trees.common.Access.READ)
    def initialise(self):
        pass
        
    def update(self) -> py_trees.common.Status:
        self.isYellow = self.bb.isYellow    

        new_version = self.wm.get_version()
        if self.version < new_version:
            self.version = new_version
            self.frame = self.wm.get_latest_frame()
            if self.frame is not None:
                if self.frame.ball is not None:
                    self.ball_last_known = self.frame.ball.position
                    self.bb.ball_pos = self.ball_last_known
                    # print(self.ball_last_known)
                our_robots = self.frame.get_yellow_robots(isYellow=self.isYellow)
                self.bb.our_robots = our_robots
                
            return py_trees.common.Status.SUCCESS
        # otherwise keep running
        return py_trees.common.Status.RUNNING


class SendRobotCommand(py_trees.behaviour.Behaviour):
    def __init__(self,dispatcher_q,runtime=1):
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
        
        
        
    def initialise(self):
        # preset
        self.last_command = getattr(self.bb,"command",None)
        
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
        print(f"[SendRobotCommand] Sending command: {command}")
        if not self.dispatcher_q.full():
            self.dispatcher_q.put(packet)
            self.last_command = command
            return py_trees.common.Status.SUCCESS
        
        else:
            print("[SendRobotCommand] Dispatcher queue is full, cannot send command")
            return py_trees.common.Status.FAILURE
        # this is always success until we put more stuff to check here.
        

class GetRobotIDPosition(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "GetRobotIDPosition"
        super().__init__(name)
        self.bb = py_trees.blackboard.Client(name="GetRobotIDPosition")
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        self.robot_id = self.bb.robot_id
        
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        
        pass
    
    def update(self) -> py_trees.common.Status:
        # gets the robot position base on robot_id

        our_robots = self.bb.our_robots
        if our_robots is not None:
            robot = our_robots[self.robot_id]
            # store position
            if isinstance(robot,int):
                return py_trees.common.Status.FAILURE
            # self.bb.robot_pos = [robot.position[0],robot.position[1],robot.position[2]-np.pi/2]
            self.bb.robot_pos = [robot.position[0],robot.position[1],robot.position[2]]
            self.logger.info(f"[GetRobotIDPosition] Robot {self.robot_id} position: {robot.position}")
            return py_trees.common.Status.SUCCESS
        else:
            # otherwise 0,0
            self.bb.robot_pos = (0,0)
            return py_trees.common.Status.FAILURE
 