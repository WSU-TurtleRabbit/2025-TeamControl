"""
Scenario 1: Only avoid opponent defense area.
No other obstacles, just the defense area polygon.

Returns the target position for the robot to reach.
"""

def get_scenario():
    # Example target near opponent goal but outside defense area
    main_agent = {'id': 0, 'start': (4200, -1550), 'goal': (4100, 1500), 'isYellow': True}

    static_robots = {} # no static obstacles in this scenario
    dynamic_robots = {}  # no dynamic obstacles either

    return main_agent, static_robots, dynamic_robots
