import py_trees
import logging
import time
from typing import Optional, List, Tuple
from TeamControl.behaviour_tree.blackboardUpdater import create_team_tree  # <-- ADD THIS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def make_dummy_robot(robot_id: int, is_yellow: bool = True):
    """Create a dummy robot for testing"""
    dummy = type('DummyRobot', (), {})()
    dummy.id = robot_id
    dummy.isYellow = is_yellow
    dummy.position = (0, 0, 0)
    return dummy


if __name__ == "__main__":
    logger.info("Creating behavior tree...")
    
    robots = [make_dummy_robot(i, True) for i in range(6)]
    
    # Build and setup tree
    tree = create_team_tree(wm, robots)
    tree.setup_with_descendants()
    
    logger.info("Running behavior tree test...")
    
    # Run several ticks
    for tick in range(5):
        logger.info(f"\n{'='*60}")
        logger.info(f"Tick {tick + 1}")
        logger.info(f"{'='*60}")
        
        tree.tick_once()
        time.sleep(0.5)
    
    logger.info("\nBehavior tree test complete!")