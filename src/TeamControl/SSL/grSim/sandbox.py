from multiprocessing import Process, Queue,Event
from TeamControl.SSL.vision.Process import vision_worker
# from TeamControl.SSL.game_controller.fsm import run_gcfsm
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model_runner import wm_runner
# from TeamControl.utils.dummy_process import DummyReader
from TeamControl.SSL.grSim.sandbox_process import run_grsim_sandbox_process

# in multiprocessing this can only be a simple process

def main():
    use_sim = True
    vision_port = 10020

    vision_q = Queue()
    # no game controller 
    gc_q = Queue()
    dispatcher_q = Queue()
    
    # inputs
    vision_wkr = Process(target=vision_worker, args=(vision_q,True,vision_port,))
    
    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    wmr = Process(target=wm_runner, args=(wm,vision_q,gc_q,))
    # sandbox = Process(target=sandbox_process, args=(wm,) )
    bt = Process(target=run_bt_process, args=(wm,dispatcher_q,) )
    
    
    sandbox = Process(target=run_grsim_sandbox_process, args=(wm,) )
    vision_wkr.start()
    wmr.start()
    # sandbox.start()
    bt.start()
    # some_other_process2.start()
    
    vision_wkr.join()
    wmr.join()
    # sandbox.join()
    bt.join()

    # some_other_process2.join()

if __name__ == "__main__":
    main()