from multiprocessing import Process, Queue,Event
import random
from TeamControl.behaviour_tree.main_tree import MainTree
from TeamControl.world.model import WorldModel
from TeamControl.behaviour_tree.test_tree import TestTreeSeq
from TeamControl.behaviour_tree.goalie_tree import GoalieRunningSeq
from TeamControl.utils.Logger import LogSaver

import typing
import py_trees

def run_bt_process(is_running:Event, wm:WorldModel, dispatcher_q:Queue)->None:
    """
    Run a behaviour tree in a separate process.

    ARGS :
        wm (WorldModel): Shared World Model from Main Loop
        dispatcher_q (multiprocessing.Queue): Queue to send RobotCommands to Dispatcher

    """
    # create the root of the behaviour tree
    logger = LogSaver()
    # logger = None
    isYellow = True
    # root = TestTreeSeq(wm=wm,dispatcher_q=dispatcher_q,robot_id=5,isYellow=isYellow,logger=logger)
    # root = GoToBallSequence(wm,dispatcher_q,logger)
    
    '''
    note to self: 

    I suspect that changing state via gcfsm_runner is the wrong approach
    world model already has a mechanism to update the state, and the behaviour tree should read the state 
    from the world model at each tick - this is why GetState node exists in the bt. 

    the state is updated in the world model, yet, root is only initialised once outside the loop
    this means that the state is not updated in the behaviour tree, which is a problem for testing different states

    ------------------------------------------------------------------

    what needs to be done next....

    test with GCfsm runner to push packets to GC queue
    test with vision runner to push packets to vision queue
    
    then test update_gc_data() in the WMRunner to see if the 
    world model is correctly updating the state from the GC

    '''

    # Initialise with default state -- RUNNING
    state = "RUNNING"
    print(f"[run_bt_process] Chosen state for testing: {state}")
    root = MainTree(wm, dispatcher_q, state, logger)
    bt = py_trees.trees.BehaviourTree(root)
    bt.setup(timeout=15) # remember to add timeout

    while is_running.is_set():
        # print(wm.get_game_state())
        # print(wm.get_version())
        bt.tick_tock(1, stop_on_terminal_state=True)
        # logger.debug(py_trees.display.unicode_tree(root, show_status=True))
