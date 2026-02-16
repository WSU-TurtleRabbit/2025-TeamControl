from multiprocessing import Queue,Process,Event
from TeamControl.SSL.vision.field import GeometryData
from TeamControl.SSL.vision.frame import Frame
from TeamControl.world.model import WorldModel
from TeamControl.utils.Logger import LogSaver

def wm_runner(wm:WorldModel,vision_q:Queue,gc_q:Queue,interval:int=5):
    log = LogSaver()
    while True:
        try:
            if not vision_q.empty():
                item = vision_q.get_nowait()
                if isinstance(item,Frame):
                    log.info("new frame")
                    wm.add_new_frame(item)
                elif isinstance(item,GeometryData):
                    wm.update_geometry(item)
                    
            if not gc_q.empty():
                new_info = gc_q.get_nowait()
                wm.update_game_data(new_info)
            
        except Exception as e:
            log.error("ERROR", e)