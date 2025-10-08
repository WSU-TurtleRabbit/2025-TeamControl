# Team Control (2025)

This is the Repository for our server-side operation.

---

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
or you can get a file called `requirement.txt` as a backup for the current modules and stuff.
To do so, in Linux : 
```bash
pip freeze > requirement.txt
```
afterwards, you can do : 
```bash
pip install -r requirement.txt
```
This is then the modules install using `requirement.txt` (which is another way to do it). To learn more, see [how to setup a python project](https://github.com/WSU-TurtleRabbit/how-to/blob/b2daf710f8d522aca7eadc72b78dd3002f60de95/Code/PythonProjectSetup.md)

If got into any error, please copy or screenshot text and post it in Mattermost Chat, and await for reply. 

### Deactivate the virtual environment
To deactivate a virtual environment use:
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

### Code 

TODO (What code is actually interesting for the students?)

goToPoint function is located here:
src/TeamControl/robot/Movement.py

Entry point for the grSim simulation:
src/TeamControl/SSL/grSim/sandbox.py

Entry point for setting the behavior:
src/TeamControl/SSL/grSim/sandbox_process.py


## Running code in grSim
1. Run grSim `./bin/grSim`
2. ...

TODO (Step by step guide)

- Setting the correct ports
- Running sandbox.py