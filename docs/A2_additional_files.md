# Additional Files for A2

## `ball_idle_spawner.py`
We have provided a new ball spawner for A2 which will spawn balls randomly on the field but in contrast to the ball spawner of A1 the balls will be idle. 

Please place this file in `src/TeamControl/ball/ball_idle_spawner.py`.

This ball spawner will be used in `striker_process.py`.

## `striker_process.py`
This is where you will implement your agent that will shoot at the goal. This has the ball spawning already implemented and all you have to do is to add the logic for your striker. 

The striker process has a time limit of 90s implemented at the moment. We will use this for the live demonstration. You may of course increase the time limit to a longer period of time or even infinity for developing purposes as long as you can change it back to the 90s later for the live demonstration.

Please place this file in `src/TeamControl/SSL/grSim/striker_process.py`.

To start the striker from `sandbox.py` you can add the following line of code to `sandbox.py`:
```python
sandbox = Process(target=striker_process, args=(wm,))
```

Make sure to import the striker process at the top of `sandbox.py` like this:
```python
from TeamControl.SSL.grSim.striker_process import striker_process
```

**Note**: Same as with the first assignment sheet, please do not change the ball spawning logic or the goal counter as we will use this for the live demonstration.

