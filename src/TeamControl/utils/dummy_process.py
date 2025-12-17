"""
Dummy process to read from world model and print updates.
"""

from multiprocessing import Queue
import time

class DummyReader():
    def __init__(self, world_model,input_queue:Queue, output_queue:Queue):
        """
        This is a dummy process that just reads whatever is in the input queue

        Args:
            world_model (WorldModel): This is the shared Model from the main process
            input_queue (Queue): This is a Queue that receives items into this process
            output_queue (Queue): This is where we put the output of this process
        """
        self.wm = world_model
        self.last_version = 0 # used to track updates
        self.in_q = input_queue
        self.out_q = output_queue
        self.frame = None
        
    def running(self):
        """
        This is the main process that will keep this sub-process alive. 
        What usually happens is that we read any updates, any inputs 
        Then if there's a new version in the world model, we get a frame out of it. 
        Afterwards, we do some process. 
        Finally, we will probably generate and output, so we send the output away ! 
        """
        while True:
            new_input = self.read_input()
            is_updated = self.check_update()
            if is_updated is True:
                # do some process. 
                print("new_input:",new_input)
                # for this dummy process, we just print the frame number
                print(f"New Frame Version: {self.frame.frame_number}")
                # we can also send output
                self.send_output(self.frame.frame_number)
            time.sleep(0.1) # to avoid busy waiting
                
    def read_input(self):
        # read from input queue
        # need to do if not empty check to avoid error
        if not self.in_q.empty():
            item = self.in_q.get()
            return item
        return None
            
    def check_update(self) -> bool:
        # if this version is different from the last version, 
        if self.last_version != self.wm.get_version:
            print(f"new version : {self.wm.get_version}")
            self.last_version = self.wm.get_version
            # get new frame data here
            self.frame = self.wm.get_latest_frame()
            # we want to access data from self.frame later
            return True
        return False
    
    def send_output(self, data):
        # send data to output queue
        # only put if the queue is not full to avoid error
        if not self.out_q.full():
            self.out_q.put(data)
    
    
def run_dummy_reader(wm,input_queue):
    # how a process is run
    # initialize the dummy reader object
    r = DummyReader(wm,input_queue)
    # start running the main loop
    r.running()