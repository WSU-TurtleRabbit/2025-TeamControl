## halt state sequence
import py_trees
from py_trees.common import Status


class HaltSequence(py_trees.composites.Sequence):
    def __init__(self, name="HaltSequence"):
        super(HaltSequence, self).__init__(name=name, memory=True)
        self.bb = py_trees.blackboard.Client(name=name)
        self.bb.register_key(key="command", access=py_trees.common.Access.WRITE)
        self.bb.register_key(key="robot_id", access=py_trees.common.Access.READ)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.READ)
        self.add_child(StopRobot())

    def initialise(self) -> None:
        pass


class StopRobot(py_trees.behaviours.Success):
    def __init__(self, name="StopRobot"):
        super(StopRobot, self).__init__(name=name)
        self.bb = py_trees.blackboard.Client(name=name)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.READ)

    def update(self) -> Status:
        cmd = {"vx": 0.0, "vy": 0.0, "w": 0.0, "kick": False, "dribble": False}
        self.bb.cmd_mgr.update_command(**cmd)
        is_sent = self.bb.cmd_mgr.pack_and_send()
        if is_sent:
            return Status.SUCCESS
        else:
            return Status.FAILURE
