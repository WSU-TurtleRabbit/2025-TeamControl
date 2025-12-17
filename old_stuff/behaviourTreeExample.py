import py_trees
import logging
import time
from TeamControl.world.model import WorldModel
from TeamControl.SSL.vision.frame import Robot
from TeamControl.robot.Movement import RobotMovement
from TeamControl.world.Trajectory import predict_trajectory
from TeamControl.world.nearest import Nearest
from TeamControl.network.robot_command import RobotCommand


logging.basicConfig(level=logging.INFO)

def make_dummy_robot(robot_id: int, is_yellow: bool):
    dummy = type('DummyRobot', (), {})()
    dummy.id = robot_id
    dummy.isYellow = is_yellow
    dummy.position = (0, 0, 0)
    return dummy

class BlackboardUpdater(py_trees.behaviour.Behaviour):
    def __init__(self, world, robots):
        super().__init__("BlackboardUpdater")
        self.world = world
        self.robots = robots
        self.bb = py_trees.blackboard.Blackboard()
    def update(self):
        self.bb.world = self.world
        self.bb.robots = self.robots
        frame = self.world.get_latest_frame()
        self.bb.ball_position = getattr(frame.ball, 'position', None) if frame and frame.ball else None
        if self.bb.ball_position:
            self.bb.nearest_robot = Nearest.robot(self.bb.ball_position, self.robots)
        else:
            self.bb.nearest_robot = None
        if self.bb.ball_position:
            ball_hist = []
            frames = self.world.get_last_n_frames(5)
            for f in frames:
                if f.ball:
                    ball_hist.append([f.ball.x, f.ball.y])
            if ball_hist:
                goalie_pos, threat = predict_trajectory(ball_hist, 3, isPostive=True, feild_size=(9000, 6000))
                self.bb.goal_threat = threat
                self.bb.goalie_save_position = goalie_pos
        return py_trees.common.Status.SUCCESS

class IsBallVisible(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__("IsBallVisible")
    def update(self):
        bb = py_trees.blackboard.Blackboard()
        visible = hasattr(bb, "ball_position") and bb.ball_position is not None
        return py_trees.common.Status.SUCCESS if visible else py_trees.common.Status.FAILURE

class IsClosestToBall(py_trees.behaviour.Behaviour):
    def __init__(self, robot):
        super().__init__(f"IsClosest_{robot.id}")
        self.robot = robot
    def update(self):
        bb = py_trees.blackboard.Blackboard()
        closest = hasattr(bb, "nearest_robot") and bb.nearest_robot and bb.nearest_robot.id == self.robot.id
        return py_trees.common.Status.SUCCESS if closest else py_trees.common.Status.FAILURE

class IsGoalThreatened(py_trees.behaviour.Behaviour):
    def __init__(self):
        super().__init__("IsGoalThreatened")
    def update(self):
        bb = py_trees.blackboard.Blackboard()
        threatened = hasattr(bb, "goal_threat") and bb.goal_threat
        return py_trees.common.Status.SUCCESS if threatened else py_trees.common.Status.FAILURE

class GoShootVelocity(py_trees.behaviour.Behaviour):
    def __init__(self, robot):
        super().__init__(f"GoShootVelocity_{robot.id}")
        self.robot = robot
    def update(self):
        bb = py_trees.blackboard.Blackboard()
        if not (hasattr(bb, "ball_position") and bb.ball_position):
            return py_trees.common.Status.FAILURE
        vx, vy, w = RobotMovement.goShootVelcoity(self.robot.position, bb.ball_position)
        cmd = RobotCommand(self.robot.id, vx, vy, w, kick=True, dribble=False)
        logging.info(f"[BT] Robot {self.robot.id} Shooting: {cmd}")
        return py_trees.common.Status.SUCCESS

class MoveToSupportPosition(py_trees.behaviour.Behaviour):
    def __init__(self, robot, position):
        super().__init__(f"SupportMove_{robot.id}")
        self.robot = robot
        self.position = position
    def update(self):
        vx, vy, w = RobotMovement.velocity_to_target(self.robot.position, self.position)
        cmd = RobotCommand(self.robot.id, vx, vy, w, kick=False, dribble=False)
        logging.info(f"[BT] Robot {self.robot.id} Moving to Support: {cmd}")
        return py_trees.common.Status.SUCCESS

class MoveToSavePosition(py_trees.behaviour.Behaviour):
    def __init__(self, robot):
        super().__init__(f"SaveShot_{robot.id}")
        self.robot = robot
    def update(self):
        bb = py_trees.blackboard.Blackboard()
        target_pos = getattr(bb, "goalie_save_position", (0, 0))
        vx, vy, w = RobotMovement.velocity_to_target(self.robot.position, target_pos)
        cmd = RobotCommands(self.robot.id, vx, vy, w, kick=False, dribble=False)
        logging.info(f"[BT] Goalie {self.robot.id} Saving Shot: {cmd}")
        return py_trees.common.Status.SUCCESS

class MoveToDefaultGoalieSpot(py_trees.behaviour.Behaviour):
    def __init__(self, robot, position):
        super().__init__(f"ResetGoalie_{robot.id}")
        self.robot = robot
        self.position = position
    def update(self):
        vx, vy, w = RobotMovement.velocity_to_target(self.robot.position, self.position)
        cmd = RobotCommand(self.robot.id, vx, vy, w, kick=False, dribble=False)
        logging.info(f"[BT] Goalie {self.robot.id} Resetting Position: {cmd}")
        return py_trees.common.Status.SUCCESS

class Idle(py_trees.behaviour.Behaviour):
    def __init__(self, robot):
        super().__init__(f"Idle_{robot.id}")
        self.robot = robot
    def update(self):
        logging.info(f"[BT] Robot {self.robot.id} Idling")
        return py_trees.common.Status.SUCCESS

def build_field_player_tree(robot, use_shoot_velocity=True):
    attack_seq = py_trees.composites.Sequence(f"AttackSeq_{robot.id}", memory=False)
    attack_seq.add_children([
        IsBallVisible(),
        IsClosestToBall(robot),
        GoShootVelocity(robot) if use_shoot_velocity else MoveToSupportPosition(robot, (0, 0))
    ])
    support_seq = py_trees.composites.Sequence(f"SupportSeq_{robot.id}", memory=False)
    support_seq.add_children([
        IsBallVisible(),
        MoveToSupportPosition(robot, (1000, 0))
    ])
    selector = py_trees.composites.Selector(f"PlayerSelector_{robot.id}", memory=False)
    selector.add_children([attack_seq, support_seq, Idle(robot)])
    return selector

def build_goalie_tree(robot):
    save_seq = py_trees.composites.Sequence("SaveShotSeq", memory=False)
    save_seq.add_children([
        IsGoalThreatened(),
        MoveToSavePosition(robot)
    ])
    reset_seq = py_trees.composites.Sequence("ResetGoalieSeq", memory=False)
    reset_seq.add_children([
        MoveToDefaultGoalieSpot(robot, (4500, 0))
    ])
    selector = py_trees.composites.Selector("GoalieSelector", memory=False)
    selector.add_children([save_seq, reset_seq, Idle(robot)])
    return selector

def create_team_tree(world, robots):
    root = py_trees.composites.Parallel("TeamRoot", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
    root.add_child(BlackboardUpdater(world, robots))
    root.add_child(build_goalie_tree(robots[0]))
    for i in range(1, 4):
        root.add_child(build_field_player_tree(robots[i], use_shoot_velocity=True))
    for i in range(4, 6):
        root.add_child(build_field_player_tree(robots[i], use_shoot_velocity=False))
    return root

if __name__ == "__main__":
    wm = WorldModel()
    robots = [make_dummy_robot(i, True) for i in range(6)]
    tree = create_team_tree(wm, robots)
    tree.setup(timeout=15)
    for _ in range(5):
        tree.tick_once()
        time.sleep(0.5) #need to be 0.05 in real scenario