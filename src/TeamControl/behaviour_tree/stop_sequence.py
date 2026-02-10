import numpy as np
import py_trees
from py_trees.common import Status

from TeamControl.behaviour_tree.halt_sequence import StopRobot
from TeamControl.behaviour_tree.move_away import move_away_robot_from
from TeamControl.behaviour_tree.velocity import go_to_target


class StopSequence(py_trees.composites.Sequence):
    def __init__(self, robot_id, dispatcher_q):
        super(StopSequence, self).__init__(name=f"StopSequence (RobotID:{robot_id})", memory=False)
        self.robot_id = robot_id
        self.dispatcher_q = dispatcher_q
        # self.bb = py_trees.blackboard.Client(name="StopSequence")
        self.add_children([StopRobot(robot_id=self.robot_id, dispatcher_q=self.dispatcher_q), MoveawayFromBall(150)])


class MoveawayFromBall(py_trees.behaviour.Behaviour):
    def __init__(self, distance_threshold):
        super(MoveawayFromBall, self).__init__(name="MoveawayFromBall")
        self.distance_threshold = distance_threshold
        self.bb = py_trees.blackboard.Client(name="MoveawayFromBall")
        
    def setup(self):
        self.bb.register_key(key="robot_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="ball_pos", access=py_trees.common.Access.READ)
        self.bb.register_key(key="cmd_mgr", access=py_trees.common.Access.READ)

    def initialise(self):
        pass

    def update(self):
        cmd = {"vx": 0.0, "vy": 0.0, "w": 0.0, "kick": False, "dribble": False}
        robot_pos = self.bb.robot_pos
        ball_pos = self.bb.ball_pos
        target_pos = move_away_robot_from(
            robot_pos=robot_pos, target_pos=ball_pos, threshold=self.distance_threshold
        )
        if target_pos is None:
            return Status.INVALID

        if np.allclose(target_pos, robot_pos[:2]):
            cmd = {"vx": 0.0, "vy": 0.0}
            self.bb.cmd_mgr.update_command(**cmd)
            is_sent = self.bb.cmd_mgr.pack_and_send()
            if is_sent:
                return Status.SUCCESS
        else:
            vx, vy = go_to_target(robot_pos=robot_pos, target_pos=target_pos)
            cmd = {"vx": vx, "vy": vy}
            self.bb.cmd_mgr.update_command(cmd)
            self.bb.cmd_mgr.pack_and_send()

        return Status.RUNNING
