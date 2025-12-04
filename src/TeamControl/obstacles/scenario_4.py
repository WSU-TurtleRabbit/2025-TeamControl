"""
Scenario 4: Static and Dynamic opponent as obstacles

Returns the target position for the robot to reach.
"""


def get_scenario():
    # Example target near opponent goal but outside defense area
    main_agent = {'id': 0, 'start': (0, 0), 'goal': (2600, 0),
                  'isYellow': True}

    # Static robots is a dictionary of robots (id, start and goal position)
    static_robots = {0: {'start': (800, -100), 'goal': None, 'isYellow': False},
                     1: {'start': (1600, 100), 'goal': None, 'isYellow': False},
                     2: {'start': (2400, -100), 'goal': None, 'isYellow': False},
                     3: {'start': (2650, -450), 'goal': None, 'isYellow': False},
                     4: {'start': (2550, 350), 'goal': None, 'isYellow': False}}

    dynamic_robots = {}

    return main_agent, static_robots, dynamic_robots