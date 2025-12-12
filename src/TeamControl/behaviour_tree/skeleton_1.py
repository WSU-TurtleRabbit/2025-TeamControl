#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""ATTEMPT 1 do not use, keep as reference"""


import random
import typing
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from py_trees.composites import Selector, Sequence, Parallel
import py_trees
from TeamControl.utils.Logger import LogSaver

#typings : 
from TeamControl.SSL.game_controller.common import *
from TeamControl.SSL.game_controller.fsm import GameState
from TeamControl.world.model import WorldModel


class BaseTree(Behaviour):
    ## depeciated

    """The node to get the update from worldmodel"""

    def __init__(
        self,
        world_model:WorldModel,   # shared world model object
        dispatcher_q,             # command output -> dispatcher queue
        children,
        name: str,                # Name of Tree
        memory = True,
        output_q=None,            # optional output from this behaviour Tree
        
    ):
        """
        Tree Root's 1 time initialisation.
        
        ARGS :

            world_model (WorldModel): World Model Shared Manager from Main Loop
            dispatcher_queue (multiprocessing.Queue): Queue to send RobotCommands to Dispatcher
            output_q (multiprocessing.Queue): Queue to send data to other processes / world model. 
                x> not Implemented yet. Defaults to None.

        A good rule of thumb is to only include the initialisation relevant

        for being able to insert this behaviour in a tree for offline rendering to dot graphs.

        Other one-time initialisation requirements should be met via

        the setup() method.
        

        """
        
        # initialise the main tree
        self.name = name
        self.children = children
        super(BaseTree, self).__init__(self.name,memory,children)
        self.wm = world_model
        self.dispatcher_q = dispatcher_q
        self.output_q = output_q
        self.frame_ver = 0
        self.dc_count = 0

        self.logger = LogSaver(process_name=self.name)



    def setup(self, **kwargs:typing.Any) -> None:

        """
        Minimal setup implementation.

        When is this called?
          This function should be either manually called by your program
          to setup this behaviour alone, or more commonly, via
          :meth:`~py_trees.behaviour.Behaviour.setup_with_descendants`
          or :meth:`~py_trees.trees.BehaviourTree.setup`, both of which
          will iterate over this behaviour, its children (its children's
          children ...) calling :meth:`~py_trees.behaviour.Behaviour.setup`
          on each in turn.

          If you have vital initialisation necessary to the success
          execution of your behaviour, put a guard in your
          :meth:`~py_trees.behaviour.Behaviour.initialise` method
          to protect against entry without having been setup.

        What to do here?
          Delayed one-time initialisation that would otherwise interfere
          with offline rendering of this behaviour in a tree to dot graph
          or validation of the behaviour's configuration.
          Good examples include:
          - Hardware or driver initialisation
          - Middleware initialisation (e.g. ROS pubs/subs/services)
          - A parallel checking for a valid policy configuration after
            children have been added or removed

        """
        self.status = self.update_world_model()
        


    def initialise(self) -> None:

        """

        Minimal initialisation implementation.


        When is this called?

          The first time your behaviour is ticked and anytime the

          status is not RUNNING thereafter.


        What to do here?

          Any initialisation you need before putting your behaviour

          to work.

        """
        # announce initialisation 
        
        self.logger.info(f"Tree has World model : {self.wm is not None}")
        self.logger.info(f"Current Frame Version: {self.frame_ver}")
        self.logger.info(f"Tree has Dispatcher Queue : {self.dispatcher_q is not None}")
        self.logger.info(f"Tree has Output Queue: {self.wm is not None}")



    def update(self) -> Status:

        """

        This is the base update Minimal update implementation.
        When is this called?
          Every time your behaviour is ticked.
        What to do here?
          - Triggering, checking, monitoring. Anything...but do not block!
          - Set a feedback message
          - return a py_trees.common.Status.[RUNNING, SUCCESS, FAILURE, INVALID]

        """
        current_state = self.update_world_model()
        return current_state

    def terminate(self, new_status: Status) -> None:

        """

        Minimal termination implementation.


        When is this called?

           Whenever your behaviour switches to a non-running state.

            - SUCCESS || FAILURE : your behaviour's work cycle has finished

            - INVALID : a higher priority branch has interrupted, or shutting down

        """

        self.logger.debug(f"Tree : {self.name} has been terminated")
        # announce final decision made / why it failed or something
        
    
    def get_world_state(self) -> bool:
        self.world_state = self.wm.get_game_state()
        return True if self.world_state is not None else False
    
    def get_frame_update(self,n=10) -> bool:
        new_version = self.wm.get_version()
        if new_version > self.frame_ver:
            self.frame_ver = new_version
            self.frame_list = self.wm.get_last_n_frames(n)
            self.frame = self.frame_list[0]
            self.logger.info(f"[Tree:{self.name}]: frame updated -> v{self.frame_ver}")
            return True
        return False
        
    def update_world_model(self):
        self.has_gc_con = self.get_world_state()
        self.has_vision_con = self.get_frame_update()
        if self.has_gc_con is True and self.has_vision_con is True:
            current_status = Status.RUNNING
        elif self.has_gc_con is False and self.has_vision_con is False:
            self.logger.error("No Vision or Game Controller connection")  
            current_status = Status.FAILURE
        elif self.has_vision_con is True: 
            current_status = Status.RUNNING
            self.logger.warning("Only Vision has connection")      
        elif self.has_gc_con is True:
            current_status = Status.FAILURE
            self.logger.error("No Vision found")  
        else:
            self.logger.warning("??? why are you here ?")
            current_status = Status.INVALID
            
        # if this fails, try 5 times otherwise return fail
        if current_status == Status.FAILURE:
            self.dc_count += 1
            if self.dc_count < 5:
                current_status = Status.RUNNING

        return current_status
            
def print_tree(tree: py_trees.trees.BehaviourTree) -> None:

    """Print the behaviour tree and its current status."""

    print(py_trees.display.unicode_tree(root=tree.root, show_status=True))
    
if __name__ == "__main__":
    
    from TeamControl.world.model import WorldModel
    # example of running this behaviour standalone
    wm = WorldModel()
    tree = BaseTree(name="tree1",world_model=wm, dispatcher_q=None,children=None)
    print(py_trees.display.unicode_tree(root=tree,show_status=True))
    tree.setup()
    for i in range(10):
        tree.tick_once()
