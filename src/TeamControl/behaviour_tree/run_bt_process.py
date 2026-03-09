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

    py_trees.console.has_colours = False

    # create the root of the behaviour tree
    logger = LogSaver()
    # logger = None
    isYellow = True

    # Initialise with default state -- RUNNING
    root = MainTree(wm, dispatcher_q, logger)
    bt = py_trees.trees.BehaviourTree(root)
    bt.setup(timeout=15) # remember to add timeout

    # while is_running.is_set():
    #     bt.tick_tock(1, stop_on_terminal_state=True)
    #     logger.debug(py_trees.display.unicode_tree(root, show_status=True))

    while is_running.is_set():
        bt.tick()
        
        tree_snapshot = py_trees.display.unicode_tree(
            root,
            show_status=True,
            visited=True
        )
        
        logger.debug("\n" + tree_snapshot)