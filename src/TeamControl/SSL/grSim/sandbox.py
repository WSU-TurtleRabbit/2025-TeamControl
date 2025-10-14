"""
main_runner.py

Entry point for running the SSL simulation pipeline.

This script demonstrates how to launch multiple processes for vision processing,
world model management, and robot command generation in parallel. It supports
both simulation (grSim) and real-world setups.

Processes:
    1. vision_worker: Reads vision frames from SSL vision multicast.
    2. wm_runner: Updates the world model using vision and game controller data.
    3. sandbox_process: Sends robot commands to grSim based on the world model.

Queues:
    - vision_q: Transports vision frames from the vision worker to the world model.
    - gc_q: Placeholder queue for game controller events (currently unused).
"""

from multiprocessing import Process, Queue,Event
from TeamControl.SSL.vision.Process import vision_worker
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model_runner import wm_runner
from TeamControl.SSL.grSim.sandbox_process import sandbox_process
from TeamControl.SSL.grSim.goalie_process import goalie_process

# in multiprocessing this can only be a simple process

def main():
    """
    Main entry point for launching the SSL multiprocessing pipeline.

    Sets up and runs:
        - Vision worker process to receive frames.
        - World model manager and runner to maintain robot/world state.
        - Sandbox process to send robot commands to grSim.

    Queues:
        vision_q: Queue for vision data.
        gc_q: Queue for game controller data (currently unused).

    Notes:
        - All processes are joined at the end to ensure proper shutdown.
        - This setup is currently configured for simulation (use_sim=True).
        - Ports and other parameters can be adjusted as needed.
    """
    # Simulation parameters
    use_sim = True
    vision_port = 10020

    # Queues for inter-process communication
    vision_q = Queue()
    gc_q = Queue() # placeholder for game controller
    
    # Initialize and start vision worker
    vision_wkr = Process(target=vision_worker, args=(vision_q,True,vision_port,))

    # Initialize world model manager
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    
    # World model runner process
    wmr = Process(target=wm_runner, args=(wm,vision_q,gc_q,))

    # Sandbox process for sending commands to grSim
    sandbox = Process(target=sandbox_process, args=(wm,))
    #sandbox = Process(target=goalie_process, args=(wm,)) # This is where you will implement your goalie logic

    # Start all processes
    vision_wkr.start()
    wmr.start()
    sandbox.start()
    # some_other_process2.start()
    
    # Wait for all processes to finish
    vision_wkr.join()
    wmr.join()
    sandbox.join()
    # some_other_process2.join()

if __name__ == "__main__":
    main()