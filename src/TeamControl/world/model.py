import numpy as np
import numpy.typing as npt

from TeamControl.SSL.vision.field import *
from TeamControl.SSL.vision.Process import VisionProcessExample
from TeamControl.SSL.game_control.Processing import Processing

import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class WorldModel:
    """
    World Model aka wm
    Description : 
        This class contains data extracted from Vision world. (Either Simulation or Vision-ssl). 
        
        The model will first compare whether the data is type 'detection' or 'geometry'. 
        
        -- Detection --
        If the data is detection, the model will check the 'Frame Number'.
            if it is an existing one, it will reuse the frame and update new data. 
            if it is a NEW one, it will initiate a new Frame object
            
        -- Geometry --
        if the data is geometry, the model will create an Object of the class : Field
        *since this is a static data, it does not require constant update*
        
    Params : 
        --Booleans--
        usYellow (bool) : is Our Team Yellow
        usPositive (bool) : is Our Team on x-Positive side
        is_detection_updated (bool) : is vision detection updated yet
        has_new_event (bool) : New event from game Controller
        has_new_state (bool) : New state from game controller 
        
        
    """
    def __init__(self, us_yellow : bool=None, us_positive : bool=None, history:int=5, use_sim: bool = False):
        self.use_sim = use_sim 
        self.us_yellow : bool= us_yellow
        self.us_positive : bool= us_positive
        self.history:int = history # histroy length
    
        # vision data
        self.detection_updated:bool = False
        self.geometry_updated:bool = False        
        self.gc_updated:bool = False
        self.vision_manager = VisionProcessExample(use_grSim=use_sim,history=history)
        self.gc_manager = Processing()
        # self.field_manager = Field_manager

    @property
    def detection(self):
        return self.vision_manager.frames

    def run_vision(self):
        self.detection_updated = self.vision_manager.update_detection()
        if self.detection_updated:
            print("vision has updated ! ")

if __name__ == "__main__":
    import time
    wm = WorldModel(use_sim=True,history=60)
    start_time = time.time()
    wm.detection_updated = wm.vision_manager.update_detection()
    print(f"time taken {time.time() - start_time}")
    print(f"{wm.detection}")
