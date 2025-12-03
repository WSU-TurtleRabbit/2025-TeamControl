# Instructions for A4

## sandbox.py
As usual your Processes are run through sandbox.py. Thus, you have to 
create a new process similar to the sandbox_process where you will develop
the solution for the task and then import this process and call it from sandbox.py

## `Adjusting kicking power
In the previous exercises the ball was kicked by setting kick=1 in the RobotCommand class.
e.g. RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=1,dribble=0)

the variable 'kick' was translated to boolean and got the maximum speed. 
Now for passing the ball around, you 'll need to adjust the strength of the kick
based on the distances between your agents.

To do that you have to replace the function "_robot_command_wrapper" in the
folder ../src/TeamControl/network/grSim_commands.py, with the following:

```python
def _robot_command_wrapper(self, robot_id:int, vx: float,vy: float,w: float, k:bool, d:bool) -> object:
    """
    Wrap raw command parameters into a grSim_Robot_Command protobuf.

    Args:
        robot_id (int): Robot ID.
        vx (float): Velocity in X direction.
        vy (float): Velocity in Y direction.
        w (float): Angular velocity.
        k (bool): Kick flag.
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
for the kick variable.
e.g. RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=5,dribble=0)

## spawning robots
You should start grSim with 2 robots per team in division B. In case you want to 
remove 1 or both of the blue robots (to test your passing strategy without opponents)
from the field, you can use the function "send_robot_to_grsim" in 
../src/TeamControl/robot/spawn_robot.py to move them out of the field.

e.g. send_robot_to_grsim(
        team_yellow=False,
        robot_id=1,
        x=-5000,
        y=-5000,
        orientation=0
    )
    which spawns the blue robot with id 1 outside of the field.