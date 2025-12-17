
import py_trees
import logging
import time
from typing import Optional, List, Tuple
from TeamControl.behaviour_tree.blackboard import bb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

class BlackboardUpdater(py_trees.behaviour.Behaviour):
    """Updates the blackboard with latest world model data"""
    
    def __init__(self, world_model, robots: list):
        super().__init__("BlackboardUpdater")
        self.world = world_model
        self.robots = robots
        self.logger = logging.getLogger(self.__class__.__name__)

    def update(self):
        try:
            state = bb()
            state.tick_ts = time.time()
            state.robots = self.robots
            
            # Update field size
            if hasattr(self.world, "field") and self.world.field:
                state.field_size = (self.world.field.x, self.world.field.y)
            
            # Update ball position
            frame = self.world.get_latest_frame()
            if frame and hasattr(frame, 'ball') and frame.ball:
                state.ball_position = (frame.ball.x, frame.ball.y)
                state.ball_timestamp = time.time()
            else:
                state.ball_position = None
            
            # Update nearest robot calculation
            if state.ball_position and self.robots:
                try:
                    from TeamControl.world.nearest import Nearest
                    state.nearest_robot = Nearest.robot(state.ball_position, self.robots)
                    ordered = Nearest.robot_ordered(state.ball_position, self.robots.copy())
                    state.nearest_order = list(ordered)
                except Exception as e:
                    self.logger.warning(f"Failed to calculate nearest robots: {e}")
                    state.nearest_robot = None
                    state.nearest_order = []
            else:
                state.nearest_robot = None
                state.nearest_order = []
            
            # Goalie trajectory prediction
            if state.ball_position:
                try:
                    from TeamControl.world.Trajectory import predict_trajectory
                    hist = []
                    frames = self.world.get_last_n_frames(7)
                    for f in frames:
                        if hasattr(f, 'ball') and f.ball:
                            hist.append([f.ball.x, f.ball.y])
                    
                    if len(hist) >= 3:
                        goalie_pos, threat = predict_trajectory(
                            hist, 3, 
                            isPostive=getattr(self.world, 'us_positive', True),
                            feild_size=state.field_size
                        )
                        state.goal_threat = bool(threat)
                        state.goalie_save_position = goalie_pos
                    else:
                        state.goal_threat = False
                        state.goalie_save_position = None
                except Exception as e:
                    self.logger.warning(f"Failed trajectory prediction: {e}")
                    state.goal_threat = False
                    state.goalie_save_position = None
            else:
                state.goal_threat = False
                state.goalie_save_position = None
            
            # Update referee data
            if hasattr(self.world, "ref_data"):
                state.gc_command = getattr(self.world.ref_data, "command", None)
                state.gc_stage = getattr(self.world.ref_data, "stage", None)
            
            return py_trees.common.Status.SUCCESS
            
        except Exception as e:
            self.logger.error(f"BlackboardUpdater failed: {e}")
            return py_trees.common.Status.FAILURE
        
        
class IsBallVisible(py_trees.behaviour.Behaviour):
    """Check if ball is visible in the world model"""
    
    def __init__(self):
        super().__init__("IsBallVisible")
    
    def update(self):
        state = bb()
        visible = state.ball_position is not None
        return py_trees.common.Status.SUCCESS if visible else py_trees.common.Status.FAILURE


class IsClosestToBall(py_trees.behaviour.Behaviour):
    """Check if this robot is closest to the ball"""
    
    def __init__(self, robot):
        super().__init__(f"IsClosest_{robot.id}")
        self.robot = robot
    
    def update(self):
        state = bb()
        if not state.nearest_robot:
            return py_trees.common.Status.FAILURE
        
        closest = state.nearest_robot.id == self.robot.id
        return py_trees.common.Status.SUCCESS if closest else py_trees.common.Status.FAILURE


class IsGoalThreatened(py_trees.behaviour.Behaviour):
    """Check if there's a threat to our goal"""
    
    def __init__(self):
        super().__init__("IsGoalThreatened")
    
    def update(self):
        state = bb()
        return py_trees.common.Status.SUCCESS if state.goal_threat else py_trees.common.Status.FAILURE


class IsHALT(py_trees.behaviour.Behaviour):
    """Check if game controller sent HALT command"""
    
    def __init__(self):
        super().__init__("IsHALT")
    
    def update(self):
        state = bb()
        is_halt = state.gc_command == "HALT"
        return py_trees.common.Status.SUCCESS if is_halt else py_trees.common.Status.FAILURE


class IsSTOP(py_trees.behaviour.Behaviour):
    """Check if game controller sent STOP command"""
    
    def __init__(self):
        super().__init__("IsSTOP")
    
    def update(self):
        state = bb()
        is_stop = state.gc_command == "STOP"
        return py_trees.common.Status.SUCCESS if is_stop else py_trees.common.Status.FAILURE


# ============================================================================
# ACTION BEHAVIORS
# ============================================================================

class GoShootVelocity(py_trees.behaviour.Behaviour):
    """Calculate shooting velocity and send command"""
    
    def __init__(self, robot):
        super().__init__(f"GoShoot_{robot.id}")
        self.robot = robot
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self):
        
        state = bb()
        
        if not state.ball_position:
            return py_trees.common.Status.FAILURE
        
        try:
            from TeamControl.robot.Movement import RobotMovement
            from TeamControl.robot.robot_commands import RobotCommands
            
            vx, vy, w = RobotMovement.goShootVelcoity(
                self.robot.position, 
                state.ball_position
            )
            cmd = RobotCommands(self.robot.id, vx, vy, w, kick=True, dribble=False)
            self.logger.info(f"Robot {self.robot.id} shooting: vx={vx:.1f}, vy={vy:.1f}")
            
            # TODO: Send command to robot controller
            return py_trees.common.Status.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed to calculate shoot velocity: {e}")
            return py_trees.common.Status.FAILURE


class MoveToPosition(py_trees.behaviour.Behaviour):
    """Move robot to a target position"""
    
    def __init__(self, robot, position: Tuple[float, float], name: str = "Move"):
        super().__init__(f"{name}_{robot.id}")
        self.robot = robot
        self.position = position
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self):
        try:
            from TeamControl.robot.Movement import RobotMovement
            from TeamControl.robot.robot_commands import RobotCommands
            
            vx, vy, w = RobotMovement.velocity_to_target(
                self.robot.position, 
                self.position
            )
            cmd = RobotCommands(self.robot.id, vx, vy, w, kick=False, dribble=False)
            self.logger.info(f"Robot {self.robot.id} moving to {self.position}")
            
            # TODO: Send command to robot controller
            return py_trees.common.Status.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed to move robot: {e}")
            return py_trees.common.Status.FAILURE


class MoveToSavePosition(py_trees.behaviour.Behaviour):
    """Move goalie to intercept ball"""
    
    def __init__(self, robot):
        super().__init__(f"SaveShot_{robot.id}")
        self.robot = robot
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self):
        state = bb()
        target_pos = state.goalie_save_position or (4500, 0)
        
        try:
            from TeamControl.robot.Movement import RobotMovement
            from TeamControl.robot.robot_commands import RobotCommands
            
            vx, vy, w = RobotMovement.velocity_to_target(
                self.robot.position, 
                target_pos
            )
            cmd = RobotCommands(self.robot.id, vx, vy, w, kick=False, dribble=False)
            self.logger.info(f"Goalie {self.robot.id} saving at {target_pos}")
            
            # TODO: Send command to robot controller
            return py_trees.common.Status.SUCCESS
            
        except Exception as e:
            self.logger.error(f"Failed goalie save: {e}")
            return py_trees.common.Status.FAILURE


class DoHaltAll(py_trees.behaviour.Behaviour):
    """Emergency halt - stop all robots immediately"""
    
    def __init__(self):
        super().__init__("DoHaltAll")
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self):
        state = bb()
        state.last_action = "HALT"
        state.last_action_ts = time.time()
        
        self.logger.warning("HALT: Stopping all robots (vx=vy=w=0, actuators safe)")
        
        # TODO: Broadcast halt command to all robots
        return py_trees.common.Status.SUCCESS


class DoStopAll(py_trees.behaviour.Behaviour):
    """Stop all robots per game controller"""
    
    def __init__(self):
        super().__init__("DoStopAll")
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self):
        state = bb()
        state.last_action = "STOP"
        state.last_action_ts = time.time()
        
        self.logger.info("STOP: Stopping all robots (vx=vy=w=0)")
        
        # TODO: Broadcast stop command to all robots
        return py_trees.common.Status.SUCCESS


class Idle(py_trees.behaviour.Behaviour):
    """Robot idle behavior"""
    
    def __init__(self, robot=None):
        name = f"Idle_{robot.id}" if robot else "Idle"
        super().__init__(name)
        self.robot = robot
    
    def update(self):
        return py_trees.common.Status.SUCCESS


# ============================================================================
# TREE BUILDERS
# ============================================================================

def build_field_player_tree(robot, use_shoot_velocity: bool = True):
    """Build behavior tree for a field player"""
    
    # Attack sequence: if ball visible and closest, shoot
    attack_seq = py_trees.composites.Sequence(
        f"AttackSeq_{robot.id}", 
        memory=False
    )
    attack_seq.add_children([
        IsBallVisible(),
        IsClosestToBall(robot),
        GoShootVelocity(robot) if use_shoot_velocity 
            else MoveToPosition(robot, (0, 0), "Attack")
    ])
    
    # Support sequence: if ball visible, move to support position
    support_seq = py_trees.composites.Sequence(
        f"SupportSeq_{robot.id}", 
        memory=False
    )
    support_seq.add_children([
        IsBallVisible(),
        MoveToPosition(robot, (1000, 0), "Support")
    ])
    
    # Selector: try attack, then support, then idle
    selector = py_trees.composites.Selector(
        f"PlayerSelector_{robot.id}", 
        memory=False
    )
    selector.add_children([attack_seq, support_seq, Idle(robot)])
    
    return selector


def build_goalie_tree(robot, default_pos: Tuple[float, float] = (4500, 0)):
    """Build behavior tree for goalie"""
    
    # Save sequence: if goal threatened, move to intercept
    save_seq = py_trees.composites.Sequence("SaveShotSeq", memory=False)
    save_seq.add_children([
        IsGoalThreatened(),
        MoveToSavePosition(robot)
    ])
    
    # Reset sequence: move to default position
    reset_seq = py_trees.composites.Sequence("ResetGoalieSeq", memory=False)
    reset_seq.add_children([
        MoveToPosition(robot, default_pos, "ResetGoalie")
    ])
    
    # Selector: try save, then reset, then idle
    selector = py_trees.composites.Selector("GoalieSelector", memory=False)
    selector.add_children([save_seq, reset_seq, Idle(robot)])
    
    return selector


def build_safety_tree():
    """Build safety tree for HALT/STOP commands"""
    
    # HALT sequence
    halt_seq = py_trees.composites.Sequence("HALT_SEQ", memory=False)
    halt_seq.add_children([IsHALT(), DoHaltAll()])
    
    # STOP sequence
    stop_seq = py_trees.composites.Sequence("STOP_SEQ", memory=False)
    stop_seq.add_children([IsSTOP(), DoStopAll()])
    
    # Selector: check HALT, then STOP
    selector = py_trees.composites.Selector("SafetySelector", memory=False)
    selector.add_children([halt_seq, stop_seq])
    
    return selector


def create_team_tree(world_model, robots: list):
    """
    Create complete team behavior tree
    
    Args:
        world_model: WorldModel instance
        robots: List of robot objects (length 6)
    
    Returns:
        Root node of the behavior tree
    """
    
    # Root parallel: all behaviors run simultaneously
    root = py_trees.composites.Parallel(
        "TeamRoot",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    
    # Always update blackboard first
    root.add_child(BlackboardUpdater(world_model, robots))
    
    # Safety checks (HALT/STOP) - high priority
    root.add_child(build_safety_tree())
    
    # Goalie (robot 0)
    if len(robots) > 0:
        root.add_child(build_goalie_tree(robots[0]))
    
    # Attacking field players (robots 1-3)
    for i in range(1, min(4, len(robots))):
        root.add_child(build_field_player_tree(robots[i], use_shoot_velocity=True))
    
    # Supporting field players (robots 4-5)
    for i in range(4, len(robots)):
        root.add_child(build_field_player_tree(robots[i], use_shoot_velocity=False))
    
    return root
