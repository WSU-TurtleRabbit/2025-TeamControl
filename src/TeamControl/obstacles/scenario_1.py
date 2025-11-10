"""
Scenario 1: Only avoid opponent defense area.
No other obstacles, just the defense area polygon.

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
    target_pos = (0, 0) # TODO: Change this

    static_robots = []  # no static obstacles in this scenario
    dynamic_robots = []  # no dynamic obstacles either

    return target_pos, static_robots, dynamic_robots
