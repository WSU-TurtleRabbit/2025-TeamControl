# Additional Files for A3

This document explains the additional files provided for A3, where to place them in your project structure, and how to use them.

## Robot Spawning

Place the file **`spawn_robot.py`** at:

```
src/TeamControl/robot/spawn_robot.py
```

This module provides the functionality to spawn your active agent (team **yellow**, ID **0**) at the correct starting position.
It is also used to spawn static and dynamic robots that act as obstacles, which your agent must avoid while navigating to its target position.

> **Note**: The robot spawner uses meters and not milimeters.

## Robot Movement
To keep it comparable between groups we will provide you with a movement function for the obstacle robots. Please copy and paste this function into the `RobotMovement` class in `Movement.py`.

```python
@classmethod
def moveagent(
    cls,
    robot_pos: tuple[float, float, float],
    target: tuple[float, float],
    velocity: float = 1.0,
) -> tuple[float, float]:
    """
    Calculate the velocity (vx, vy) for the robot to move towards a target point
    and stop when is very close to it.

    Args:
        robot_pos (tuple[float, float, float]): Robot's current position (x, y, theta) in world coordinates.
        target (tuple[float, float]): Target position in world coordinates.
        velocity (float, optional): Constant velocity to move towards the target. Defaults to 1.0.
        stop_threshold (float, optional): Distance threshold to stop near the target. Defaults to 150.

    Returns:
        tuple[float, float]: Velocity components (vx, vy) in robot coordinates.
    """
    if robot_pos is None or target is None:
        return 0.0, 0.0

    # Convert target from world coordinates to robot coordinates
    target_robot_frame = world2robot(robot_pos, target)

    # Distance to target
    dx, dy = target_robot_frame
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Normalize direction and scale by velocity
    if distance > 300:
        vx = (dx / distance) * velocity
        vy = (dy / distance) * velocity

    elif 150 < distance <= 300:
        vx = (dx / distance) * (velocity / 3)
        vy = (dy / distance) * (velocity / 3)

    elif 10 < distance <= 150:
        vx = (dx / distance) * (velocity / 7)
        vy = (dy / distance) * (velocity / 7)

    elif distance <= 10:
        vx = 0
        vy = 0

    return vx, vy
```

This function will be used to move the dynamic obstacles in the obstacle avoidance process.

## Obstacle Avoidance Scenarios

Place the entire **`obstacles`** folder at:

```
src/TeamControl/obstacles
```

This folder contains:

* `__init__.py` — marks the directory as a module
* `helpers.py` — utility functions (e.g., collision checking)
* `scenario_1.py` — avoid only the opponent’s defense area
* `scenario_2.py` — avoid the defense area + static robots
* `scenario_3.py` — avoid the defense area + static and dynamic robots

For the live demonstration, you will additionally receive:

* `scenario_4.py`
* `scenario_5.py`
* `scenario_6.py`

Place these files in the same folder as well.

> **Note:** You may create your own scenarios for testing, but **do not use the filenames** `scenario_4.py`, `scenario_5.py`, or `scenario_6.py`, as these are reserved for the live demonstration setup.

### Opponent Defense Area

The opponent’s defense area is defined by the following polygon:

```python
DEFENSE_AREA_POLYGON = [
    (3500, 1000),  # top-left (in mm)
    (4500, 1000),  # top-right (in mm)
    (4500, -1000), # bottom-right (in mm)
    (3500, -1000), # bottom-left (in mm)
]
```

## Obstacle Avoidance Process

Place **`obstacle_avoidance_process.py`** at:

```
src/TeamControl/SSL/grSim/obstacle_avoidance_process.py
```

This file is responsible for executing the scenarios.
You will implement your agent logic here: navigating from its start position to the target position (defined in the scenario files) without entering the opponent's defense area or colliding with other robots.

### Controlling Both Teams

We now move **both** blue and yellow robots. Since each robot ID appears once per team, you must create **two separate** `grSimSender` instances, one for each team.

#### Previously:

```python
sender = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=IS_YELLOW)

cmd = RobotCommand(robot_id=0, vx=vx, vy=vy, w=0.0, kick=0, dribble=0)
sender.send_command(cmd)
```

#### Now:

```python
sender_yellow = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=True)
sender_blue   = grSimSender(ip=SIM_IP, port=CMD_LISTEN_PORT, is_yellow=False)

cmd = RobotCommand(robot_id=0, vx=vx, vy=vy, w=0.0, kick=0, dribble=0)
sender_yellow.send_command(cmd)
sender_blue.send_command(cmd)
```

So make sure to send the commands for you active agent (team **yellow**, ID **0**) to `sender_yellow`.

## `sandbox.py`

You will need to update `sandbox.py` in the following way:
- Import the process at the top of the file like this
```from TeamControl.SSL.grSim.obstacle_avoidance_process import obstacle_avoidance_process```
- Start your obstacle avoidance process like this ```sandbox = Process(target=obstacle_avoidance_process, args=(wm,))```

To run a specific scenario:

```bash
python sandbox.py scenario_1
```

or 

```bash
python sandbox.py scenario_2
```

etc.