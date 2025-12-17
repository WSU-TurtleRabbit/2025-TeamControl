import py_trees


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
        self.bb = self.attach_blackboard_client(name="MainTreeNode")
        super().__init__(name)

    def setup(self, timeout:float):
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
    

class go_to_ball_dummy(py_trees.behaviour.Behaviour):
    def __init__(self,wm,dispatcher_q,robot_id:int=0):
        name = "go_to_ball_dummy"
        self.wm = wm
        self.dispatcher_q = dispatcher_q
        self.robot_id = robot_id
        super().__init__(name)
    
    def setup(self, timeout:float):
        pass
    
    def initialise(self):
        self.version = self.wm.get_version()
        
    def update(self) -> py_trees.common.Status:
        self.get_wm_update()
        if self.frame is not None and self.ball_last_known is not None:
            ball_pos = self.ball_last_known
            robot_pos = self.frame.get_yellow_robot(robot_id=self.robot_id).position
            
            print(ball_pos,robot_pos)
            # here we would create a RobotCommand to go to the ball
            # for this dummy, we just print
            print(f"[go_to_ball_dummy] Commanding robot to go to ball at {ball_pos}")
        return py_trees.common.Status.SUCCESS
    
    def get_wm_update(self):
        new_version = self.wm.get_version()
        if self.version < new_version:
            self.version = new_version
            self.frame = self.wm.get_latest_frame()
            if self.frame is not None and self.frame.ball is not None:
                self.ball_last_known = self.frame.ball.position
