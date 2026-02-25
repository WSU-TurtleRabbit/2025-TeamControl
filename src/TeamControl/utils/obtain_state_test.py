# test for obtaining state from the game controller

from TeamControl.process_workers.vision_runner import VisionProcess
from TeamControl.process_workers.gcfsm_runner import GCfsm
from TeamControl.process_workers.wm_runner import WMWorker
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model import WorldModel
from TeamControl.utils.yaml_config import Config
from TeamControl.utils.Logger import LogSaver

from multiprocessing import Process, Queue, Event

if __name__ == "__main__":
    # Event: Is system running? 
    is_running = Event()
    is_running.set()

    # Logger
    logger = None

    # Queues
    vision_q = Queue()
    gc_q = Queue()

    preset = Config()

    # World Model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    
    # Processes
    wmr = wmr = Process(target=WMWorker.run_worker, args=(is_running,logger,wm,vision_q,gc_q),)
    vision_wkr = Process(target=VisionProcess.run_worker, args=(is_running,logger,vision_q,preset.use_grSim_vision,preset.vision[1]),)
    gc_wkr = Process(target=GCfsm.run_worker, args=(is_running, logger, gc_q, preset.us_yellow, preset.us_positive ),)


    vision_wkr.start()
    gc_wkr.start()
    wmr.start()

    vision_wkr.join(timeout=5)
    gc_wkr.join(timeout=5)
    wmr.join(timeout=5)