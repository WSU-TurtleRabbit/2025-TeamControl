from multiprocessing import Process, Queue 
from TeamControl.world.model import WorldModel
from TeamControl.behaviour_tree.main_tree import MainTreeNode
import typing
import py_trees


def run_bt_process(wm:WorldModel, dispatcher_q:Queue)->None:
    """
    Run a behaviour tree in a separate process.

    ARGS :
        wm (WorldModel): Shared World Model from Main Loop
        dispatcher_q (multiprocessing.Queue): Queue to send RobotCommands to Dispatcher

    """
    # create the root of the behaviour tree
    root = MainTreeNode(wm,dispatcher_q)
    bt = py_trees.trees.BehaviourTree(root)
    bt.setup()
    
    while True:
        # print(wm.get_game_state())
        # print(wm.get_version())
        bt.tick_tock(1000, stop_on_terminal_state=True)