from multiprocessing import Queue,Process,Event
from TeamControl.SSL.vision.field import GeometryData
from TeamControl.SSL.vision.frame import Frame
from TeamControl.world.model import WorldModel
from TeamControl.utils.Logger import LogSaver

import time

def wm_runner(is_running:Event,wm:WorldModel,vision_q:Queue,gc_q:Queue,interval:int=5,wait_for_input=True):
    logger = LogSaver()
    delay_time = 0.001 # s
    end_count = 10
    cnt = 0
    end_time = time.time() + interval
    while is_running.is_set():
        try:
            if not vision_q.empty() :
                item = vision_q.get()
                if isinstance(item,Frame):
                    logger.info("Saving new vision Frame")
                    wm.add_new_frame(item)
                elif isinstance(item,GeometryData):
                    logger.info("Updating Geometry")
                    wm.update_geometry(item)
                        
            if not gc_q.empty():
                # we have something : 
                has_new_data = True
                
                new_info = gc_q.get_nowait()
                
                logger.info(f"Saving new Game Info {new_info}")
                wm.update_game_data(new_info)
            
            if wait_for_input is True: 
                end_time = time.time() + interval
        
            time.sleep(delay_time)
        except KeyboardInterrupt:
            continue
    print("runner quit")
