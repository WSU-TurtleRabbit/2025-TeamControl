# RoboCup SSL - Robot Control

This is the code you will need to control the SSL robots in grSim and also to control the real robots.

## Installation 

To install this module, do

```
git clone https://github.com/WSU-TurtleRabbit/2025-teamcontrol.git
```

### Create the virual environment and activate it
Then we will have to create a virtual environment. 
In Linux : 
```bash
python3 -m venv .venv
```
In Windows : 
```powershell
python -m venv .venv
```
*if this did not work, it is recommended to get the version of python (>=3.13) from the [python.org](https://www.python.org/downloads/). Then add python to path
in particular : Appdata/Python3.13/ (-> python) and Appdata/Python3.13/Scripts/ (-> pip) 
Then restart vscode or the app with terminal opened.


Then we will have to install the pip packages and our development project. 
To do so, you will first have to activate the environment.
In Linux : 
```bash 
source .venv/bin/activate
```
In Windows : 
```powershell
.\.venv\Scripts\activate.bat
```

### Install necessary modules
Then install the modules and this project as *Editable* project (that uses `pyproject.toml`)
```bash 
pip install -e . 
```

Now you should be able to run and start coding without any problem ! 

If you want to know what was installed (and what version), you can do :
```bash
pip list
```

### Deactivate the virtual environment
In Linux : 
```bash
deactivate 
```
In Windows : 
```powershell
.\.venv\Scripts\deactivate.bat
```

## Repository structure

- **docs/** – Contains documentation, and usage guides.  
- **src/** – Houses the core source code for the project.  
  - **TeamControl/** – The main package for robot and network control.  
    - **ball/** - Contains modules for ball spawning.
    - **network/** – Handles communication between the PC and the robots/simulation.  
    - **robot/** – Contains modules for robot behavior.  
    - **SSL/** – Implements Small Size League–specific software (game controller, grSim, vision).  
    - **utils/** – General-purpose helper functions.  
    - **world/** – Everything related to the world model.  
    - **main.py** – Primary entry script to start the system (on the real robots).  
- **tests/** – Includes test suites to ensure code reliability and correctness.  
- **pyproject.toml** – Defines project metadata, dependencies, and build configuration.  
- **setup.sh** – Shell script to set up the development environment.  
- **README.md** – Main documentation file (this file).  

## Code 

Most of the code in this repository is provided as a framework, so you do not need to modify everything. To help you get started, here are the main files and functions that are relevant for your lab work:

### Key Functions & Entry Points
- **Movement Control**
    - `goToPoint` function
    - Location: `src/TeamControl/robot/Movement.py`
    - This is the function you should improve for the first assignment.
    - Feel free to add more functions to `Movement.py`
- **Simulation Entry Point**
    - Start the grSim simulation
    - Location: `src/TeamControl/SSL/grSim/sandbox.py`
    - This is where the simulation begins. You can run this to see your robot behavior in action.
- **Behavior Setup**
    - This is the process `sandbox.py` runs
    - Entry point for defining robot behavior
    - Location: `src/TeamControl/SSL/grSim/sandbox_process.py`
    - This is where you will implement or modify strategies and behaviors for the robots.

### Important and useful functions/classes
**Coordinate transformation**

Import like this:
`from TeamControl.world.transform_cords import world2robot`


What it does:
```
def world2robot(robot_position,target_position):
    '''
        input:
            Target_position: position in the world coordinate system (x,y)
            robot_position: robot pose (x, y, theta)
        output:
            t: target position in respect to robot coordinate system (x,y)
    '''
```
**RobotCommand**

Import like this:
`from TeamControl.network.robot_command import RobotCommand`

What it does:
```
class RobotCommand():
    """
    RobotCommand represents the desired motion command for a single robot.

    Attributes:
        robot_id (int): Unique robot identifier.
        vx (float): Velocity along the X-axis (m/s).
        vy (float): Velocity along the Y-axis (m/s).
        w (float): Angular velocity (rad/s).
        kick (int): Kick flag (0 = no kick, 1 = kick).
        dribble (int): Dribble flag (0 = off, 1 = on).
        (time_origin (float): Original creation time of the packet.)
        (time_set (float): Timestamp when this RobotCommand object was instantiated.)
    """
```

**Spawning a ball**

Import like this:
`from TeamControl.ball.send_ball_grsim import send_ball_to_grsim`

What it does:
```
def send_ball_to_grsim(x, y, vx, vy, address="127.0.0.1", port=20011):
    """
    Spawn or move the ball in grSim to position (x, y)
    with velocity (vx, vy).

    Args:
        x (float): X position in mm.
        y (float): Y position in mm.
        vx (float): Velocity in X direction in m/s.
        vy (float): Velocity in Y direction in m/s.
    """
```

## Running Code in grSim
1. Run grSim `./bin/grSim` (in one terminal)
2. Check that the “vision port” in sandbox.py is set to the same value as “Vision multicast port” in grSim
3. Check that the “CMD_LISTEN_PORT” in sandbox_process.py is set to the same value as “Command listen port” in grSim
4. Run `sandbox.py` (in another terminal)