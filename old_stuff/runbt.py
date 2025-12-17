
""

import py_trees
import logging
import time
from TeamControl.SSL.game_controller.common import Command
from TeamControl.world.model import WorldModel
from TeamControl.network.robot_command import RobotCommand

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONDITION BEHAVIORS
# ============================================================================

class UpdateFromWorldModel(py_trees.behaviour.Behaviour):
    """Updates blackboard from world model ref_data"""
    
    def __init__(self, world_model: WorldModel):
        super().__init__("UpdateFromWorldModel")
        self.world_model = world_model
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        # Get command from world model if available
        if hasattr(self.world_model, 'ref_data') and self.world_model.ref_data:
            if hasattr(self.world_model.ref_data, 'command'):
                self.bb.gc_command = self.world_model.ref_data.command
            if hasattr(self.world_model.ref_data, 'stage'):
                self.bb.gc_stage = self.world_model.ref_data.stage
        
        # Store world model reference for other behaviors
        self.bb.world_model = self.world_model
        
        return py_trees.common.Status.SUCCESS


class IsHALT(py_trees.behaviour.Behaviour):
    """Check if command is HALT"""
    
    def __init__(self):
        super().__init__("IsHALT")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        gc_command = getattr(self.bb, 'gc_command', None)
        
        # Handle both enum and string comparison
        if gc_command == Command.HALT:
            return py_trees.common.Status.SUCCESS
        elif hasattr(gc_command, 'value') and gc_command.value == 'HALT':
            return py_trees.common.Status.SUCCESS
        elif str(gc_command) == 'Command.HALT':
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.FAILURE


class IsSTOP(py_trees.behaviour.Behaviour):
    """Check if command is STOP"""
    
    def __init__(self):
        super().__init__("IsSTOP")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        gc_command = getattr(self.bb, 'gc_command', None)
        
        # Handle both enum and string comparison
        if gc_command == Command.STOP:
            return py_trees.common.Status.SUCCESS
        elif hasattr(gc_command, 'value') and gc_command.value == 'STOP':
            return py_trees.common.Status.SUCCESS
        elif str(gc_command) == 'Command.STOP':
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.FAILURE


class IsNormalStart(py_trees.behaviour.Behaviour):
    """Check if command is NORMAL_START or FORCE_START"""
    
    def __init__(self):
        super().__init__("IsNormalStart")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        gc_command = getattr(self.bb, 'gc_command', None)
        
        # Check for either NORMAL_START or FORCE_START
        if gc_command in [Command.NORMAL_START, Command.FORCE_START]:
            return py_trees.common.Status.SUCCESS
        elif hasattr(gc_command, 'value'):
            if gc_command.value in ['NORMAL_START', 'FORCE_START']:
                return py_trees.common.Status.SUCCESS
        elif str(gc_command) in ['Command.NORMAL_START', 'Command.FORCE_START']:
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.FAILURE


class NotAlreadyHalted(py_trees.behaviour.Behaviour):
    """Check if we haven't already sent halt command"""
    
    def __init__(self):
        super().__init__("NotAlreadyHalted")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        # Initialize if not exists
        if not hasattr(self.bb, 'is_halted'):
            self.bb.is_halted = False
        
        return py_trees.common.Status.FAILURE if self.bb.is_halted else py_trees.common.Status.SUCCESS


class NotAlreadyStopped(py_trees.behaviour.Behaviour):
    """Check if we haven't already sent stop command"""
    
    def __init__(self):
        super().__init__("NotAlreadyStopped")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        # Initialize if not exists
        if not hasattr(self.bb, 'is_stopped'):
            self.bb.is_stopped = False
        
        return py_trees.common.Status.FAILURE if self.bb.is_stopped else py_trees.common.Status.SUCCESS


# ============================================================================
# ACTION BEHAVIORS
# ============================================================================

class SendHaltCommand(py_trees.behaviour.Behaviour):
    """Send HALT command to all robots"""
    
    def __init__(self, robot_ids: list = None, command_queue=None):
        super().__init__("SendHaltCommand")
        self.robot_ids = robot_ids or list(range(6))
        self.command_queue = command_queue
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        logger.warning("="*60)
        logger.warning("HALT COMMAND - EMERGENCY STOP ALL ROBOTS")
        logger.warning("="*60)
        
        for robot_id in self.robot_ids:
            # Create halt command
            cmd = RobotCommand(
                robot_id=robot_id,
                vx=0.0,
                vy=0.0,
                w=0.0,
                kick=False,
                dribble=False
            )
            
            logger.info(f"  Robot {robot_id}: HALT (vx=0, vy=0, w=0, kick=OFF, dribble=OFF)")
            
            # Send command if queue provided
            if self.command_queue:
                self.command_queue.put(cmd)
        
        # Mark as halted
        self.bb.is_halted = True
        self.bb.is_stopped = False
        self.bb.last_command_sent = "HALT"
        self.bb.last_command_time = time.time()
        
        return py_trees.common.Status.SUCCESS


class SendStopCommand(py_trees.behaviour.Behaviour):
    """Send STOP command to all robots"""
    
    def __init__(self, robot_ids: list = None, command_queue=None):
        super().__init__("SendStopCommand")
        self.robot_ids = robot_ids or list(range(6))
        self.command_queue = command_queue
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        logger.info("-"*60)
        logger.info("STOP COMMAND - STOPPING ALL ROBOTS")
        logger.info("-"*60)
        
        for robot_id in self.robot_ids:
            # Create stop command
            cmd = RobotCommand(
                robot_id=robot_id,
                vx=0.0,
                vy=0.0,
                w=0.0,
                kick=False,
                dribble=False
            )
            
            logger.info(f"  Robot {robot_id}: STOP (vx=0, vy=0, w=0)")
            
            # Send command if queue provided
            if self.command_queue:
                self.command_queue.put(cmd)
        
        # Mark as stopped
        self.bb.is_stopped = True
        self.bb.is_halted = False
        self.bb.last_command_sent = "STOP"
        self.bb.last_command_time = time.time()
        
        return py_trees.common.Status.SUCCESS


class ClearStopFlags(py_trees.behaviour.Behaviour):
    """Clear halt/stop flags when resuming play"""
    
    def __init__(self):
        super().__init__("ClearStopFlags")
        self.bb = py_trees.blackboard.Blackboard()
    
    def update(self):
        if getattr(self.bb, 'is_halted', False) or getattr(self.bb, 'is_stopped', False):
            logger.info("*"*60)
            logger.info("RESUMING NORMAL PLAY")
            logger.info("*"*60)
            
            self.bb.is_halted = False
            self.bb.is_stopped = False
            self.bb.last_command_sent = "RESUME"
            self.bb.last_command_time = time.time()
        
        return py_trees.common.Status.SUCCESS


class Idle(py_trees.behaviour.Behaviour):
    """Default idle behavior"""
    
    def __init__(self):
        super().__init__("Idle")
    
    def update(self):
        return py_trees.common.Status.SUCCESS


# ============================================================================
# TREE BUILDER
# ============================================================================

def create_halt_stop_tree(world_model: WorldModel, robot_ids: list = None, command_queue=None):
    """
    Create behavior tree for HALT/STOP commands
    
    Args:
        world_model: Your existing WorldModel instance
        robot_ids: List of robot IDs (default: [0,1,2,3,4,5])
        command_queue: Optional queue for sending robot commands
    
    Returns:
        Root node of behavior tree
    """
    
    robot_ids = robot_ids or list(range(6))
    
    # Root runs children in parallel
    root = py_trees.composites.Parallel(
        "HaltStopRoot",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )
    
    # Always update from world model
    root.add_child(UpdateFromWorldModel(world_model))
    
    # Main command selector
    command_handler = py_trees.composites.Selector(
        "CommandHandler",
        memory=False
    )
    
    # HALT sequence (highest priority)
    halt_sequence = py_trees.composites.Sequence("HaltSequence", memory=False)
    halt_sequence.add_children([
        IsHALT(),
        NotAlreadyHalted(),
        SendHaltCommand(robot_ids, command_queue)
    ])
    
    # STOP sequence
    stop_sequence = py_trees.composites.Sequence("StopSequence", memory=False)
    stop_sequence.add_children([
        IsSTOP(),
        NotAlreadyStopped(),
        SendStopCommand(robot_ids, command_queue)
    ])
    
    # Resume sequence
    resume_sequence = py_trees.composites.Sequence("ResumeSequence", memory=False)
    resume_sequence.add_children([
        IsNormalStart(),
        ClearStopFlags()
    ])
    
    # Add all handlers in priority order
    command_handler.add_children([
        halt_sequence,
        stop_sequence,
        resume_sequence,
        Idle()
    ])
    
    root.add_child(command_handler)
    
    return root


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example of how to use with your existing code"""
    from multiprocessing import Queue
    
    # Create world model (your existing one)
    wm = WorldModel()
    
    # Optional: create command queue for robot commands
    robot_command_queue = Queue()
    
    # Create behavior tree
    tree = create_halt_stop_tree(
        world_model=wm,
        robot_ids=[0, 1, 2, 3, 4, 5],
        command_queue=robot_command_queue  # Optional
    )
    
    # Setup tree
    tree.setup(timeout=15)
    
    # Main loop - integrate this into your existing loop
    while True:
        # Tree will automatically read from world model ref_data
        tree.tick_once()
        
        # Process any robot commands from queue if needed
        while not robot_command_queue.empty():
            cmd = robot_command_queue.get()
            # Send cmd to your robot communication system
            
        time.sleep(0.05)  # 20Hz tick rate


if __name__ == "__main__":
    # Test without actual world model
    logger.info("Testing HALT/STOP Behavior Tree")
    
    # Create mock world model
    wm = WorldModel()
    
    # Create tree
    tree = create_halt_stop_tree(wm)
    tree.setup(timeout=15)
    
    # Simulate commands
    test_commands = [
        Command.NORMAL_START,
        Command.STOP,
        Command.HALT,
        Command.NORMAL_START,
        Command.STOP,
    ]
    
    for cmd in test_commands:
        logger.info(f"\nSetting command: {cmd}")
        
        # Simulate updating world model
        if not hasattr(wm, 'ref_data'):
            wm.ref_data = type('RefData', (), {})()
        wm.ref_data.command = cmd
        
        # Tick tree
        tree.tick_once()
        
        # Display tree state
        print(py_trees.display.unicode_tree(tree, show_status=True))
        
        time.sleep(0.5)