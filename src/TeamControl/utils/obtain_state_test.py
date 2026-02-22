# test for obtaining state from the game controller

from TeamControl.process_workers.wm_runner import WMWorker
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model import WorldModel

from multiprocessing import Process, Queue, Event
from TeamControl.utils.Logger import LogSaver

if __name__ == "__main__":
    # world model

    # Event: Is system running? 
    is_running = Event()
    is_running.set()

    # Logger
    logger = None

    # Queues
    vision_q = Queue()
    gc_q = Queue()

    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    wmr = wmr = Process(target=WMWorker.run_worker, args=(is_running,logger,wm,vision_q,gc_q),)
    wmr.start()
    wmr.join(timeout=5)