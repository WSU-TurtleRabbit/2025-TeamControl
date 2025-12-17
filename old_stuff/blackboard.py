import py_trees
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

@dataclass
class BBState:
    """Central state container for the behavior tree"""
    # World snapshots
    ball_position: Optional[Tuple[float, float]] = None
    ball_timestamp: float = 0.0
    robots: list = field(default_factory=list)
    field_size: Tuple[int, int] = (9000, 6000)
    us_yellow: bool = True
    us_positive: bool = True
    
    # Inference
    nearest_robot: Optional[object] = None
    nearest_order: List[object] = field(default_factory=list)
    
    # Goalie
    goal_threat: bool = False
    goalie_save_position: Optional[Tuple[float, float]] = None
    
    # Referee
    gc_command: Optional[str] = None
    gc_stage: Optional[str] = None
    
    # Roles (updated every tick)
    roles: Dict[int, str] = field(default_factory=dict)
    
    # Planner outputs
    waypoints: Dict[int, List[Tuple[float, float]]] = field(default_factory=dict)
    
    # Meta
    last_action: Optional[str] = None
    last_action_ts: float = 0.0
    tick_ts: float = 0.0


def bb() -> BBState:
    """Global accessor for a single BBState stored on the py_trees blackboard"""
    board = py_trees.blackboard.Blackboard()
    if not hasattr(board, "state"):
        board.state = BBState()
    return board.state
