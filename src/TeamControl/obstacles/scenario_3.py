"""
Scenario 3: Static and Dynamic opponent as obstacles 

Returns the target position for the robot to reach.
"""


def get_scenario():
    # Example target near opponent goal but outside defense area
    main_agent = {'id': 0, 'start': (0, -1000), 'goal': (2000, 1200), 'isYellow': True}

    # Static robots is a dictionary of robots (id, start and goal position)
    static_robots = {0: {'start': (800, -300), 'goal': None, 'isYellow': False},
                     1: {'start': (1000, -1000), 'goal': None, 'isYellow': False},
                     2: {'start': (1300, 700), 'goal': None, 'isYellow': False}}
    
    dynamic_robots = {3: {'start': (0, 0), 'goal': (650, -1000), 'isYellow': False}}

    return main_agent, static_robots, dynamic_robots