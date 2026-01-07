# from TeamControl.process_workers.worker import run_worker
from TeamControl.process_workers.vision_runner import VisionProcess
from TeamControl.process_workers.gcfsm_runner import GCfsm
from TeamControl.process_workers.wm_runner import WMWorker
from TeamControl.world.model_manager import WorldModelManager

from TeamControl.utils.Logger import LogSaver
from TeamControl.dispatcher.dispatch import Dispatcher
from TeamControl.utils.yaml_config import Config

from TeamControl.voronoi_planner.run_planner import run_planner
# from TeamControl.behaviour_tree.run_bt_process import run_bt_process
# from TeamControl.utils.dummy_process import DummyReader
from TeamControl.utils.follow_ball_dummy import run_follow_ball_dummy
from TeamControl.robot.goalie import run_goalie

from TeamControl.robot.striker import run_striker
from TeamControl.robot.unittest import run_test_to_goal
from TeamControl.plotter.plot import run_plotter



# in multiprocessing this can only be a simple process
from multiprocessing import Process, Queue,Event

# use this to catch keyboard interrupt
import sys

import time

def main():
    # add a timer
    start_time = time.time()
    preset = Config()
    
    # queues
    vision_q = Queue()
    gc_q = Queue()
    dispatch_q = Queue()
    planner_q = Queue()
    
    # robot_feedback_q = Queue()

    # logger = LogSaver()
    logger = None
        
    # event : System running ? 
    is_running = Event()
    
    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    
    
    # processes
    wmr = Process(target=WMWorker.run_worker, args=(is_running,logger,wm,vision_q,gc_q),)
    vision_wkr = Process(target=VisionProcess.run_worker, args=(is_running,logger,vision_q,preset.use_grSim_vision,preset.vision[1]),)
    gc_wkr = Process(target=GCfsm.run_worker, args=(is_running, logger, gc_q, preset.us_yellow, preset.us_positive ),)
    
    dispatch_wkr = Process(target=Dispatcher.run_worker, args=(is_running,logger,dispatch_q,preset,),)
    # planner_wkr = Process(target=run_planner, args=(wm,dispatch_q))

    goalie = Process(target=run_goalie,args=(is_running,dispatch_q,wm,1,preset.us_yellow))
    # chaser = Process(target=run_follow_ball_dummy,args=(dispatch_q,wm,1,preset.us_yellow))
    # some_other_process2 = Process(target=DummyReader,args=(wm,))'
    plot_test = Process(target=run_plotter, args=(is_running,wm,))

    is_running.set()
    is_running.set()
    vision_wkr.start()
    gc_wkr.start()
    wmr.start()
    goalie.start()
    dispatch_wkr.start()
    plot_test.start()

    # bt.start()
    # chaser.start()
    # planner_wkr.start()
    # some_other_process2.start()

    while is_running.is_set():
        try:

            print("Type 'exit' to quit: ")
            user_input = input()
            if user_input.lower() == 'exit':
                print("Shutdown signal received...")
                is_running.clear()
                break
        except KeyboardInterrupt:
            print("\nShutdown signal received...")
            is_running.clear()
            # sys.exit()


        # Give processes time to see the event change and shut down
        print("Waiting for processes to shut down...")
        time.sleep(1)  # or 2 seconds if needed

    # Then wait for processes
    vision_wkr.join(timeout=5)
    gc_wkr.join(timeout=5)
    wmr.join(timeout=5)
    dispatch_wkr.join(timeout=5)
            
    # bt.join()
    # chaser.join()   
    goalie.join()
    plot_test.join(timeout=5)


    # planner_wkr.join()
    # some_other_process2.join()
        
    print("All processes has been ended")
        
        
if __name__ == "__main__":
    main()