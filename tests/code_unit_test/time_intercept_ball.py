
from TeamControl.process_workers.wm_runner import WMWorker
from TeamControl.process_workers.vision_runner import VisionProcess
from TeamControl.world.model_manager import WorldModelManager,WorldModel
from TeamControl.utils.Logger import LogSaver
from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.world.time_to_intercept import time_to_intercept
from TeamControl.world.velocity_est import velocity_est

# from multiprocessing.synchronize import Event
from multiprocessing import Queue, Process,Event


class Test_1:
    def __init__(self,is_running,wm):
        self.wm = wm
        self.is_running = is_running
        
        # presets
        self.is_yellow = True
        self.robot_id = 1
        self.version = 0 # vision version
        self.ball_last_known = (0,0)

    def running(self):
        while self.is_running.is_set():
            # check version update 
            has_update = self.get_update()
            # This is running
            
            if has_update is True:
                robot_pos, ball_hist = self.get_objects()
                # do functions here 
                t = time_to_intercept(ball_pos=self.ball_last_known,target=None, ball_hist=ball_hist)
                print(t)
                v_vector = velocity_est(ball_hist = ball_hist)
                print(v_vector)
                            
    def get_update(self):
        # get_update
        if self.version < self.wm.get_version():
            print("getting update")

            self.version = self.wm.get_version()
            self.frame = self.wm.get_latest_frame()
            self.frames =self.wm.get_last_n_frames(10) # you can pick how many frames to get
            # verified that you have a frame

            assert self.frame is not None
            assert self.frames is not None
            return True
        return False
    
    def get_objects(self):
        # getting a robot object 
        robot_obj = self.frame.get_yellow_robots(isYellow=self.is_yellow,robot_id=self.robot_id) 
        # accessing the specific robot position
        robot_pos = robot_obj.position
        # save new ball position
        self.ball_last_known = self.frame.ball.position
        assert robot_pos is not None
        assert self.ball_last_known is not None
        # getting ball history
        ball_hist = []

        for f in self.frames: 
            ball_hist.append(f.ball.position)
        assert len(ball_hist) > 1 # we have at least 1 frame
            
        # select what you want to return    
        return robot_pos, ball_hist
    

## running as a multiprocessing process
def run_test1(is_running,wm):
    sandbox = Test_1(is_running=is_running,wm=wm)
    sandbox.running()
    
    
    

if __name__ == "__main__":
    logger = LogSaver()
    vision_q = Queue()
    gc_q = Queue()
    use_grSim = True
    vision_port = 10006

    # event : System running ? 
    is_running = Event()
    is_running.set()

    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm:WorldModel = wm_manager.WorldModel()
    # processes 
    wmr = Process(target=WMWorker.run_worker, args=(is_running,logger,wm,vision_q,gc_q),)
    vision_wkr = Process(target=VisionProcess.run_worker, args=(is_running,logger,vision_q,use_grSim,vision_port),)
    test = Process(target=run_test1,args=(is_running,wm,))


    vision_wkr.start()
    wmr.start()
    test.start()

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
            
    vision_wkr.join(timeout=5)
    wmr.join(timeout=5)
    test.join(timeout=5)

