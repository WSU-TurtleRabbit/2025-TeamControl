# Instructions for A4
In previous assignments, we provided example implementations for various processes, such dynamic obstacles, ball spawning, and other core functionalities. In this exercise, however, you are expected to implement everything on your own based solely on the instructions provided in the assignment sheet. This approach is intentional: the final competition will involve a less structured task, and this exercise serves as preparation for it. If you get stuck, you may ask for help in the Ilias forum.

## sandbox.py
You will continue to run your processes through `sandbox.py` as usual. Therefore, you need to create a new process similar to `sandbox_process`, where you will develop the solution for the task. After creating it, import this new process into `sandbox.py` and call it from there.

## Adjusting the kicking power
In the previous exercises, the ball was kicked by setting `kick=1` in the `RobotCommand` class, for example:
```python
RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=1, dribble=0)
```

The variable kick was treated as a boolean and always applied the maximum kicking speed.
For passing the ball between your agents, you will now need to adjust the kick strength based on the distances between them.

To achieve this, you must replace the function `_robot_command_wrapper` in the file `../src/TeamControl/network/grSim_commands.py` with the following:

```python
def _robot_command_wrapper(self, robot_id:int, vx: float,vy: float,w: float, k:bool, d:bool) -> object:
    """
    Wrap raw command parameters into a grSim_Robot_Command protobuf.

    Args:
        robot_id (int): Robot ID.
        vx (float): Velocity in X direction.
        vy (float): Velocity in Y direction.
        w (float): Angular velocity.
        k (int): Kicking velocity.
        d (bool): Dribble flag.

    Returns:
        grSim_Robot_Command: GrSim protobuf command.
    """
    robot_id = int(robot_id)
    vx, vy, w = float(vx), float(vy), float(w)
    k, d = int(k), bool(d)

    grSim_robot_command =  grSim_Commands_pb2.grSim_Robot_Command(
        id=robot_id, 
        kickspeedx=k, 
        kickspeedz=self.kick_speed_z if k else 0.0, 
        veltangent=vx, 
        velnormal=vy, 
        velangular=w, 
        spinner=d, 
        wheelsspeed=self.wheel_speed
        )
    return grSim_robot_command
```

Then you can adjust the strength of your kick by using values between 1 and 10 
for the kick variable. Setting it to 0 still means no kicking.

e.g. 
```python
RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=5, dribble=0)
```

## spawning robots
You should start grSim with two robots per team in Division B. If you want to remove one or both of the blue robots (for example, to test your passing strategy without opponents), you can use the function `send_robot_to_grsim` in `../src/TeamControl/robot/spawn_robot.py` to move them out of the field.

e.g. 
```python
send_robot_to_grsim(
        team_yellow=False,
        robot_id=1,
        x=-5000,
        y=-5000,
        orientation=0
    )
```
This spawns the blue robot with id 1 outside of the field.