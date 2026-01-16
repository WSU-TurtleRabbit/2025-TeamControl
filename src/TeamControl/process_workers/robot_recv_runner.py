from TeamControl.process_workers.worker import BaseWorker
from TeamControl.network.receiver import Receiver

class RobotRecv(BaseWorker):
    def __init__(self, is_running, logger):
        super().__init__(is_running, logger)
        self.recv = Receiver(is_running=is_running,port=50513)
        
    def step(self):
        data,addr = self.recv.listen()
        print(f"[Recv] : {data , addr}")
        
    