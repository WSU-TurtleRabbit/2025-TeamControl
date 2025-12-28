from multiprocessing import Process, Queue,Event
from TeamControl.SSL.vision.Process import vision_worker
# from TeamControl.SSL.game_controller.compare import game_controller_worker
from TeamControl.SSL.game_controller.fsm import run_gcfsm
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model_runner import wm_runner
# from TeamControl.utils.dummy_process import DummyReader
from TeamControl.utils.follow_ball_dummy import run_follow_ball_dummy
from TeamControl.robot.goalie import run_goalie
from TeamControl.network.proto2 import *
from TeamControl.dispatcher.dispatch import run_dispatcher
from TeamControl.voronoi_planner.run_planner import run_planner
from TeamControl.behaviour_tree.run_bt_process import run_bt_process
# in multiprocessing this can only be a simple process

def main():
    use_sim = True
    is_yellow = True
    
    # queues
    vision_q = Queue()
    gc_q = Queue()
    dispatch_q = Queue()
    planner_q = Queue()
    
    # robot_feedback_q = Queue()
    
    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    wmr = Process(target=wm_runner, args=(wm,vision_q,gc_q,))
    
    # processes
    vision_wkr = Process(target=vision_worker, args=(vision_q,use_sim,))
    gc_wkr = Process(target=run_gcfsm, args=(gc_q,))
    dispatch_wkr = Process(target=run_dispatcher, args=(dispatch_q,use_sim,is_yellow))
    planner_wkr = Process(target=run_planner, args=(wm,dispatch_q))
    bt = Process(target=run_bt_process, args=(wm,dispatch_q,) )
    # goalie = Process(target=run_goalie,args=(dispatch_q,wm,0,is_yellow))
    # chaser = Process(target=run_follow_ball_dummy,args=(dispatch_q,wm,1,is_yellow))
    # some_other_process2 = Process(target=DummyReader,args=(wm,))'
    
    vision_wkr.start()
    gc_wkr.start()
    wmr.start()
    # goalie.start()
    dispatch_wkr.start()
    bt.start()
    # chaser.start()
    # planner_wkr.start()
    # some_other_process2.start()
    
    vision_wkr.join()
    gc_wkr.join()
    wmr.join()
    # goalie.join()
    dispatch_wkr.join()
    bt.join()
    # chaser.join()   
    # planner_wkr.join()
    # some_other_process2.join()

if __name__ == "__main__":
    main()