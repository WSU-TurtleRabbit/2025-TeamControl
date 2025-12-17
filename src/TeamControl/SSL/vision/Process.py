from TeamControl.SSL.vision.frame import Frame
from TeamControl.SSL.vision.field import GeometryData
from TeamControl.network.ssl_sockets import Vision,VisionTracker
from TeamControl.utils.Logger import LogSaver

from TeamControl.network.ssl_sockets import Vision,VisionTracker
from TeamControl.utils.Logger import LogSaver

import numpy as np
import numpy.typing as npt
from multiprocessing import Queue, Process



class VisionProcess():
    GRSIM_CAMERAS = 4
    REAL_LIFE_CAMERAS = 1
    def __init__(self,output_q:Queue,logs,use_grSim:bool=True,vision_port=10006):
        self.logs:LogSaver = logs
    def __init__(self,output_q:Queue,logs,use_grSim:bool=True,vision_port=10006):
        self.logs:LogSaver = logs
        self.use_grSim = use_grSim
        self.output_q = output_q
        self.recv = Vision(port=vision_port)    
        self.field = None
        self.frame = None
        self.frame_number = -1
    
    @property
    def cameras(self):
        return self.GRSIM_CAMERAS if self.use_grSim is True else self.REAL_LIFE_CAMERAS
    
    @property
    def has_field(self):
        return self.field is not None
    

    def run(self) -> bool:
        while True:
            new_vision_data = self.recv.listen()
            if new_vision_data is None: # idk why but this maybe none
                continue
            if new_vision_data.HasField("detection"):
                new_detection_data = new_vision_data.detection
                if self.frame_number < new_detection_data.frame_number:
                    self.logs.info(f"{new_detection_data.frame_number=}")
                    self.logs.info(f"{new_detection_data.frame_number=}")
                    # generates new frame
                    self.frame = Frame.from_proto(new_detection_data,self.cameras)
                    self.frame_number = self.frame.frame_number
                if self.frame_number == new_detection_data.frame_number:
                    self.logs.info(f"updating last one, {new_detection_data.camera_id}")
                    self.frame.update(new_detection_data)
                    if self.frame.is_completed:
                        self.send(self.frame)
            if new_vision_data.HasField("geometry"):
                geometry = new_vision_data.geometry
                self.field = GeometryData.from_proto(geometry)
                self.send(self.field)
    
    def send(self,data):
        if not self.output_q.full():
            self.output_q.put(data)
        else:
            self.logs.warning("QUEUE IS FULL")

def vision_worker(output_q:Queue,use_grSim:bool=True,vision_port=10006):
    logs = LogSaver()
    v = VisionProcess(output_q,logs,use_grSim,vision_port)
    v.run()

if __name__ == "__main__" :
    def read(input_q):
        while True:
            if not input_q.empty():
                item = input_q.get_nowait()
                # print(type(item))
                # print(type(item))
            
    output_q = Queue()
    vision = Process(target=vision_worker,args=(output_q,))
    reader = Process(target=read,args=(output_q,))
    
    vision.start()
    reader.start()
    vision.join()
    reader.join()