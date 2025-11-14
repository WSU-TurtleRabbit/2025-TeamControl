"""
Scenario 2: Static opponent as obstacles 

Returns the target position for the robot to reach.
"""

def get_scenario():
    # Example target near opponent goal but outside defense area
    main_agent = {'id': 0, 'start': (0, 0), 'goal': (3000, 0), 'isYellow': True}
    
    # Static robots is a dictionary of robots (id, start and goal position)
    static_robots = {0: {'start': (1000, 100), 'goal': None, 'isYellow': False},
                      1: {'start': (1000, 0), 'goal': None, 'isYellow': False},
                       2: {'start': (1000, -100), 'goal': None, 'isYellow': False}}
    dynamic_robots = {}  # no dynamic obstacles

    return main_agent, static_robots, dynamic_robots