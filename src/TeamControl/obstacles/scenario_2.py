"""
Scenario 2: Static opponent obstacles 

Returns the target position for the robot to reach.
"""

def get_scenario():
    """
    Returns:
        target_pos: tuple (x, y) of the goal position
        static_robots: list of positions (empty here)
        dynamic_robots: list of positions (empty here)
    """
    # Example target near opponent goal but outside defense area
    target_pos = (3000, 0)
    
    # Static robots is a dictionary of robots (id, start and goal position)
    static_robots = {0: {'start': (800, 50), 'goal': (800, 50)},
                      1: {'start': (1600, -50), 'goal': (1600, -50)},
                       2: {'start': (2400, 50), 'goal': (2400, 50)}}
    dynamic_robots = []  # no dynamic obstacles

    return target_pos, static_robots, dynamic_robots