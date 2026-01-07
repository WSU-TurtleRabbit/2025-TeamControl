# typings
from multiprocessing import Queue,Process,Event
from TeamControl.SSL.vision.field import GeometryData
from TeamControl.SSL.vision.frame import Frame
from TeamControl.world.model import WorldModel
from TeamControl.utils.Logger import LogSaver
from TeamControl.process_workers.worker import BaseWorker
import time


class WMWorker(BaseWorker):
    def __init__(self,is_running,logger):
        super().__init__(is_running=is_running,logger=logger)
        self.delay_time = 0.001 # s

        
    def setup(self, *args):
        """ setup for wm :
        expected in order : 
            wm = world model shared object
            vision_q (Queue): the shared queue between vision and this process
            gc_q (Queue) : the shared queue between gcfsm and this  process
        """
        wm,vision_q,gc_q = args
        
        self.wm:WorldModel = wm
        self.vision_q:Queue = vision_q
        self.gc_q:Queue = gc_q
        self.logger.info(f"[wmr] : L setup completed")
            
    def step(self):
        if not self.vision_q.empty() :
            item = self.vision_q.get()
            if isinstance(item,Frame):
                self.logger.info("[wmr] : Updating World Model Frame")
                self.wm.add_new_frame(item)
            elif isinstance(item,GeometryData):
                self.logger.info("[wmr] : Updating World Model Geometry")
                self.wm.update_geometry(item)
                        
        if not self.gc_q.empty():
            new_info = self.gc_q.get_nowait()
            self.logger.info(f"[wmr] : Updating World Model Game Info {new_info[0]}")
            self.wm.update_game_data(new_info)
        
        time.sleep(self.delay_time)
    
    def run(self):
        return super().run()   
    
    def shutdown(self):
        return super().shutdown()        

if __name__ == "__main__":
    logger = LogSaver()
    is_running = Event()
    is_running.set()
    
    wm = WorldModel()
    gc_q = Queue()
    vision_q = Queue()
    
    worker = Process(target=WMWorker.run_worker,args=(is_running,logger,wm,vision_q,gc_q,),)
    worker.start()
    try: 
        print("[main] : type something to quit")
        s = input()
        print("[main] : finishing this loop")
        is_running.clear()
        
    
    except KeyboardInterrupt:
        logger.info(f"[main] : Force Quitting workers ")
        is_running.clear()

    logger.info("[main] : waiting for workers to be shut down")
    worker.join(timeout=4)
