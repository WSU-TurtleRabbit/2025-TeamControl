"""
Scenario 6: Static and Dynamic opponent as obstacles

Returns the target position for the robot to reach.
"""


def get_scenario():
    # Example target near opponent goal but outside defense area
    main_agent = {'id': 0, 'start': (3700, -1500), 'goal': (3000, 500),
                  'isYellow': True}

    # Static robots is a dictionary of robots (id, start and goal position)
    static_robots = {0: {'start': (3270, -700), 'goal': None, 'isYellow': False},
                     1: {'start': (2750, -700), 'goal': None, 'isYellow': False},
                     2: {'start': (2990, -450), 'goal': None, 'isYellow': False},
                     3: {'start': (2700, 0), 'goal': None, 'isYellow': False}}

    dynamic_robots = {4: {'start': (1200, 0), 'goal': (3500, -1700), 'isYellow': False},
                      5: {'start': (500, -1500), 'goal': (2900, -1300), 'isYellow': False}}

    return main_agent, static_robots, dynamic_robots