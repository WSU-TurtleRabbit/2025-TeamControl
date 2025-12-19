import py_trees


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
        

class GetRobotIDPosition(py_trees.behaviour.Behaviour):
    def __init__(self,robot_id:int=0):
        self.robot_id = robot_id
        name = "GetRobotIDPosition"
        super().__init__(name)
        
        
    def setup(self,logger=None):
        if logger is not None:
            self.logger = logger
        self.bb = py_trees.blackboard.Client(name="GetRobotIDPosition")
        # self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        pass
    
    def update(self) -> py_trees.common.Status:
        # gets the robot position base on robot_id

        our_robots = self.bb.our_robots
        if our_robots is not None and isinstance(our_robots[self.robot_id],object):
            robot = our_robots[self.robot_id]
            # store position
            self.bb.robot_pos = robot.position
            self.logger.info(f"[GetRobotIDPosition] Robot {self.robot_id} position: {robot.position}")
            return py_trees.common.Status.SUCCESS
        else:
            # otherwise 0,0
            self.bb.robot_pos = (0,0)
            return py_trees.common.Status.FAILURE
 