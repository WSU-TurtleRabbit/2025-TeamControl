from TeamControl.utils.Logger import LogSaver

import py_trees

class WMSnapshot(py_trees.behaviour.Behaviour):
    # this is for connecting to the world model
    def __init__(self, world_model,dispatcher_q, output_q=None, name="Snapshot"):
        super().__init__(name)
        self.wm = world_model
        self.d_q = dispatcher_q
        self.out_q = output_q
        self.bb = py_trees.blackboard.Client()
        self.logger = LogSaver(process_name=name)

    def setup(self, **kwargs):
        self.bb.register_key(key="game_state", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="frame_version", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="frame", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="has_gc", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="has_vision", access=py_trees.common.Access.WRITE)
        return super().setup(**kwargs)

    def update(self):
        # read wm once
        self.bb.game_state = self.wm.get_game_state()
        self.bb.frame_version = self.wm.get_version()
        self.bb.frame = self.wm.get_latest_frame()
        self.bb.has_gc = self.bb.game_state is not None
        self.bb.has_vision = self.bb.frame is not None
        
        # optional debug
        self.logger.debug(f"gc={self.bb.has_gc}, vision={self.bb.has_vision}, v={self.bb.frame_version}")
        return py_trees.common.Status.SUCCESS 
    
# proving connection to Game Controller and Vision
class ConnectionCheck(py_trees.behaviour.Behaviour):
    def __init__(self, name="wm_connection_Check"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Client()
        
        
    def setup(self, **kwargs):
        self.bb.register_key(key="game_state", access=py_trees.common.Access.READ)
        self.bb.register_key(key="frame_version", access=py_trees.common.Access.READ)
        self.bb.register_key(key="frame", access=py_trees.common.Access.READ)
        self.bb.register_key(key="has_gc", access=py_trees.common.Access.READ)
        self.bb.register_key(key="has_vision", access=py_trees.common.Access.READ)
        return super().setup(**kwargs)
    
    def update(self):
        if not self.bb.has_gc and not self.bb.has_vision:
            self.logger.error("No GC + No Vision")
            return py_trees.common.Status.FAILURE
        if not self.bb.has_vision:
            self.logger.error("No Vision")
            return py_trees.common.Status.SUCCESS  # or RUNNING if you want “wait”
        
        self.logger.info("Has Vision + GC")

        return py_trees.common.Status.SUCCESS
    
def build_main_tree(wm, dispatcher_q,output_q):
    root = py_trees.composites.Sequence("Root", memory=True)
    root.add_children([
        WMSnapshot(wm,None),
        ConnectionCheck(),
        # state tree ? 
        py_trees.behaviours.Success(name="hm")  # built-in leaf that returns RUNNING
    ])

    bt = py_trees.trees.BehaviourTree(root)
    bt.setup()
    return bt #m

if __name__ == "__main__":
      
    from TeamControl.world.model import WorldModel
    # example of running this behaviour standalone
    wm = WorldModel()
    bt = build_main_tree(wm,None,None)

    for i in range(5):
        bt.tick_tock(1000,stop_on_terminal_state=True)
