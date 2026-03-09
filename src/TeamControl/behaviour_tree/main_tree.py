## this is where the entry point of behaviour tree goes
# Author: Liam Vercueil

'''
Create a parallel behaviour tree to tick all behaviours at the same time. 
Each "behaviour" in this case is really a subtree that handles a robot.
This simulates a multi-agent behaviour tree.
'''

from TeamControl.behaviour_tree.common_trees import *
from TeamControl.behaviour_tree.halt_sequence import *
from TeamControl.behaviour_tree.stop_sequence import *
from TeamControl.behaviour_tree.cmd_mgr import CommandManager
from TeamControl.SSL.game_controller.common import GameState
import py_trees
import random

# Game states
# RUNNING = "RUNNING"
# STOPPED = "STOPPED"
# HALTED = "HALTED"

# Generic markers for success/fail
FAIL = 0
SUCCESS = 1

# list of placeholder actions
ACTIONS = [
        GoToBall(),
        GoToFormation(),
        GoToInterception(),
        PassBall(),
        GetBall(),
        RotateWithBall(),
        KickBall()
    ]

class MainTree(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q, logger=None):
        name = "MainTree"
        super().__init__(name, memory=False)
        self.wm = wm
        self.dispatch_q = dispatch_q
        # self.state = state
        if logger is not None:
            self.logger = logger
        
        # print("Debug: MainTree initialized")
    
    # def setup(self):
        subtrees = []
        # for config in self.robot_configs:
            # robot_id = config['robot_id']
            # isYellow = config['isYellow']
            # behaviour_tree_class = config['behaviour_tree_class']

        for robot_id in range(0,3):  # assuming 3 robots
            # in future, we can load the actual behaviour tree class from a config file
            # in this case, the subtree is only a single behaviour, but it could be more complex
            run_tree = RunTree(wm=self.wm, dispatch_q=self.dispatch_q, robot_id=robot_id)
            stop_tree = StopTree(wm=self.wm, dispatch_q=self.dispatch_q, robot_id=robot_id)
            halt_tree = HaltTree(wm=self.wm, dispatch_q=self.dispatch_q, robot_id=robot_id)
            # add state trees to parallel subtree list
            # each robot has its own run/stop/halt subtree
            subtrees.extend([run_tree, stop_tree, halt_tree])

        parallel_bt = ParallelBT(robot_subtrees=subtrees)

        self.add_children([
            GetState(wm=self.wm),
            GetWorldPositionUpdate(wm=self.wm),
            parallel_bt
        ])

    def setup(self, **kwargs):
        super().setup(**kwargs)

    # def initialise(self):
        # for c in self.children:
            # c.setup()
    
    def print_tree(self):
        print((py_trees.display.unicode_tree(self, show_status=True)))


class RunTree(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q, robot_id):
        name = f"RunTree (RobotID:{robot_id})"
        super().__init__(name, memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        self.robot_id = robot_id
        self.bb = py_trees.blackboard.Client(name=name)
        # self.logger = logger
        # print("Debug: RunTree initialized")
        
        self.add_children([
            IsRunning(),
            RunningSequence(wm=self.wm, dispatch_q=self.dispatch_q, robot_id=self.robot_id)
        ])

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.WRITE)
        # initialise cmd_mgr
        self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        our_robots = self.bb.our_robots
        if our_robots is not None:
            self.bb.robot_pos = our_robots[self.robot_id].position
        else:
            self.bb.robot_pos = []
    
    def update(self) -> py_trees.common.Status: 
        if self.bb.robot_pos is None:
            our_robots = self.bb.our_robots
            self.bb.robot_pos = our_robots[self.robot_id].position

        if self.bb.cmd_mgr is None:
            self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q) 

        # get the status (success/failure) of the first child IsRunning
        isRunningStatus = self.children[0].status

        # return the status of the first child
        # this can change
        if isRunningStatus == py_trees.common.Status.SUCCESS:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

    # def initialise(self):
        # for c in self.children:
            # c.setup()

class HaltTree(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q, robot_id):
        name = f"HaltTree (RobotID:{robot_id})"
        super().__init__(name, memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        self.robot_id = robot_id
        self.bb = py_trees.blackboard.Client(name=name)
        # self.logger = logger
        # print("Debug: HaltTree initialized")
        
        self.add_children([
            IsHalted(),
            HaltSequence(robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        ])

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.WRITE)
        # initialise cmd_mgr
        self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        our_robots = self.bb.our_robots
        if our_robots is not None:
            self.bb.robot_pos = our_robots[self.robot_id].position
        else:
            self.bb.robot_pos = []

    def update(self) -> py_trees.common.Status:
        if self.bb.robot_pos is None:
            our_robots = self.bb.our_robots
            self.bb.robot_pos = our_robots[self.robot_id].position
        
        if self.bb.cmd_mgr is None:
            self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        
        # get the status (success/failure) of the first child IsHalted
        isHaltedStatus = self.children[0].status

        # return the status of the first child
        # this can change
        if isHaltedStatus == py_trees.common.Status.SUCCESS:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

    # def initialise(self):
        # for c in self.children:
            # c.setup()

class StopTree(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q, robot_id):
        name = f"StopTree (RobotID:{robot_id})"
        super().__init__(name, memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        self.robot_id = robot_id
        self.bb = py_trees.blackboard.Client(name=name)
        # self.logger = logger
        # print("Debug: StopTree initialized")
        
        self.add_children([
            IsStopped(),
            StopSequence(robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        ])

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="our_robots", access=py_trees.common.Access.READ)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.WRITE)
        # initialise cmd_mgr
        self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q)
        our_robots = self.bb.our_robots
        if our_robots is not None:
            self.bb.robot_pos = our_robots[self.robot_id].position
        else:
            self.bb.robot_pos = []

    def update(self) -> py_trees.common.Status:
        if self.bb.robot_pos is None:
            our_robots = self.bb.our_robots
            self.bb.robot_pos = our_robots[self.robot_id].position

        if self.bb.cmd_mgr is None:
            self.bb.cmd_mgr = CommandManager(isYellow=True, robot_id=self.robot_id, dispatcher_q=self.dispatch_q)

        # get the status (success/failure) of the first child IsStopped
        isStoppedStatus = self.children[0].status

        # return the status of the first child
        # this can change
        if isStoppedStatus == py_trees.common.Status.SUCCESS:
            return py_trees.common.Status.SUCCESS
        elif isStoppedStatus == py_trees.common.Status.INVALID:
            print("[StopTree] isStoppedStatus for isStopped = INVALID")
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

    # def initialise(self):
    #   for c in self.children:
    #    c.setup()

# necessary for choosing different children in running subtree
class CheckCondition(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "CheckCondition"
        super(CheckCondition, self).__init__(name=name)
        self.bb = py_trees.blackboard.Client(name=name)
    
    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="condition", access=py_trees.common.Access.WRITE)
        self.bb.condition = random.randint(0, 1) # randomly choose success or fail

    def update(self) -> py_trees.common.Status:
        if self.bb.condition == SUCCESS:
            return py_trees.common.Status.SUCCESS
        elif self.bb.condition == FAIL or self.bb.condition is None:
            return py_trees.common.Status.FAILURE

class ChooseRandomBehaviour(py_trees.composites.Sequence):
    def __init__(self, robot_id):
        name = "ChooseRandomBehaviour"
        super(ChooseRandomBehaviour, self).__init__(name=name,memory=True)
        self.robot_id = robot_id

        self.add_children([
            CheckCondition(),
            GetBallPosition(robot_id=self.robot_id)
        ])

# this is the subtree responsible for handling the running sequence (GetWorldPositionUpdate + ParallelBT)
# testing: this is a selector (randomly choose one behaviour and display result)
class RunningSequence(py_trees.composites.Selector):
    def __init__(self, wm, dispatch_q, robot_id):
        name = "RunningSequence"
        super(RunningSequence, self).__init__(name=name,memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        self.robot_id = robot_id
        # self.logger = logger
        # print("Debug: RunningSequence initialized")

        self.add_children([
            ChooseRandomBehaviour(robot_id=self.robot_id),
            GetRobotIDPosition(robot_id=self.robot_id)           
        ])

    def setup(self, **kwargs):
        super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        # For now, just return SUCCESS
        return py_trees.common.Status.SUCCESS

    def print_tree(self):
        print((py_trees.display.unicode_tree(self, show_status=True)))

# Tree for running multiple robots in parallel
class ParallelBT(py_trees.composites.Parallel):
    def __init__(self, robot_subtrees:list):
        name = "ParallelBT"
        policy = py_trees.common.ParallelPolicy.SuccessOnAll()
        super().__init__(name, policy)
        self.robot_subtrees = robot_subtrees
        self.create_children()
        # print("Debug: ParallelBT initialized")
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
    
    def update(self):
        # all_success = True
        # for subtree in self.robot_subtrees:
            # status = subtree.tick_once()
            # if status != py_trees.common.Status.SUCCESS:
                # all_success = False
        # if all_success:
            # return py_trees.common.Status.SUCCESS
        
        if len(self.robot_subtrees) == 0:
            return py_trees.common.Status.FAILURE
        else:
            return py_trees.common.Status.SUCCESS
        
    def create_children(self):
        for subtree in self.robot_subtrees:
            self.add_child(subtree)
            # print(subtree, "\n")            


class HaltedTreeSeq(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q):
        name = "HaltedTreeSeq"
        super(HaltedTreeSeq, self).__init__(name=name,memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        # self.logger = logger
        # print("Debug: HaltedTreeSeq initialized")

    def setup(self, **kwargs):
        # print(f"{self.name} setup")
        super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        # For now, just return SUCCESS
        return py_trees.common.Status.SUCCESS


class StopTreeSeq(py_trees.composites.Sequence):
    def __init__(self, wm, dispatch_q):
        name = "StopTreeSeq"
        super(StopTreeSeq, self).__init__(name=name,memory=True)
        self.wm = wm
        self.dispatch_q = dispatch_q
        # self.logger = logger
        # print("Debug: StopTreeSeq initialized")

    def setup(self, **kwargs):
        super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        # For now, just return SUCCESS
        return py_trees.common.Status.SUCCESS

    # def initialise(self):
        # for c in self.children:
            # c.setup()

#########################################################

class GetState(py_trees.behaviour.Behaviour):
    def __init__(self, wm):
        name = "GetState"
        super(GetState, self).__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        self.wm = wm
        
        # for now, we shall comment this out -- testing
        self.state = self.wm.get_game_state()

        print(f"[GetState] Initialized with state: {self.state}")
        # print("Debug: GetState initialized")

    def setup(self, **kwargs):  
        super().setup(**kwargs)
        self.bb.register_key(key="game_state", access=py_trees.common.Access.WRITE)
        self.bb.game_state = self.state
       
    # note: instead of passing state_for_testing, get the actual state from the game controller
    # default is RUNNING for test operation, but should be changed for real use
    def update(self) -> py_trees.common.Status:
        self.bb.game_state = self.wm.get_game_state()
        old_state = self.bb.game_state
        new_state = self.wm.get_game_state()
        
        # if old_state == new_state:
        #     print("[GetState] Game state unchanged:", new_state)
        #     return py_trees.common.Status.SUCCESS
       
        if self.bb.game_state is None:
            print("NO STATE")
            return py_trees.common.Status.FAILURE
        elif new_state == GameState.STOPPED:
            print("[GetState] Game state is STOPPED")
            return py_trees.common.Status.SUCCESS
        elif new_state == GameState.RUNNING:
            print("[GetState] Game state is RUNNING")
            return py_trees.common.Status.SUCCESS
        elif new_state == GameState.HALTED:
            print("[GetState] Game state is HALTED")
            return py_trees.common.Status.SUCCESS
        else:
            # print("Unknown Game State:", self.bb.game_state, 
            #       "\nHint: Try using 'RUNNING', 'STOPPED' or 'HALTED'")
            return py_trees.common.Status.FAILURE

    # def print_state(self):
        # state = self.bb.game_state
        # print(f"Current Game State: {state}")


class IsRunning(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "IsRunning"
        super(IsRunning, self).__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        # initialise isRunning to false
        self.isRunning = False
        # print("Debug: IsRunning initialized")

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="game_state", access=py_trees.common.Access.READ)

    def update(self):
        self.isRunning = self.bb.game_state == GameState.RUNNING
        if self.isRunning:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class IsStopped(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "IsStopped"
        super(IsStopped, self).__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        # initialise isStopped to false
        self.isStopped = False

    def setup(self, **kwargs):
        super().setup(**kwargs)
        self.bb.register_key(key="game_state", access=py_trees.common.Access.READ)

    def update(self):
        self.isStopped = self.bb.game_state == GameState.STOPPED
        if self.isStopped:
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE

class IsHalted(py_trees.behaviour.Behaviour):
    def __init__(self):
        name = "IsHalted"
        super(IsHalted, self).__init__(name)
        self.bb = py_trees.blackboard.Client(name=name)
        # initialise isHalted to false
        self.isHalted = False

    def setup(self, **kwargs):
        # print(f"{self.name} setup")
        super().setup(**kwargs)
        self.bb.register_key(key="game_state", access=py_trees.common.Access.READ)

    def update(self):
        self.isHalted = self.bb.game_state == GameState.HALTED
        if self.isHalted:
            return py_trees.common.Status.SUCCESS
        else: 
            return py_trees.common.Status.FAILURE

######################################################

if __name__ == "__main__":
    # simple test
    # from TeamControl.world.model import WorldModel
    from TeamControl.world.model_manager import WorldModelManager
    from TeamControl.utils.Logger import LogSaver
    from multiprocessing import Queue

    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    
    dispatch_q = Queue()

    logger = LogSaver()
    
    # test with STOPPED state
    main_tree = MainTree(wm=wm, dispatch_q=dispatch_q, state=GameState.STOPPED, logger=logger)
    bt = py_trees.trees.BehaviourTree(main_tree)
    bt.setup(timeout=15)
    bt.tick()

    main_tree.print_tree()