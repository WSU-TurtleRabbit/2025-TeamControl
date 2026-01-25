from multiprocessing import Process, Queue,Event
from TeamControl.world.model import WorldModel
from TeamControl.behaviour_tree.test_tree import TestTreeSeq
from TeamControl.behaviour_tree.goalie_tree import GoalieRunningSeq
from TeamControl.utils.Logger import LogSaver

import typing
import py_trees


def run_bt_process(is_running:Event,wm:WorldModel, dispatcher_q:Queue)->None:
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
    root = TestTreeSeq(wm=wm,dispatcher_q=dispatcher_q,robot_id=1,isYellow=isYellow,logger=logger)
    # root = GoToBallSequence(wm,dispatcher_q,logger)
    bt = py_trees.trees.BehaviourTree(root)
    bt.setup(timeout=15) # remember to add timeout
    
    while is_running.is_set():
        # print(wm.get_game_state())
        # print(wm.get_version())
        bt.tick_tock(1, stop_on_terminal_state=True)
        # logger.debug(py_trees.display.unicode_tree(root, show_status=True))
