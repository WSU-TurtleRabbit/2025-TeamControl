from multiprocessing import Process, Queue
from TeamControl.SSL.vision.Process import vision_worker
from TeamControl.SSL.game_controller.fsm import run_gcfsm
from TeamControl.world.model_manager import WorldModelManager
from TeamControl.world.model_runner import wm_runner
from TeamControl.robot.goalie import run_goalie
from TeamControl.network.proto2 import *
from TeamControl.dispatcher.dispatch import run_dispatcher
from TeamControl.voronoi_planner.run_planner import run_planner
from TeamControl.robot.striker import run_simple_striker



def main():
    use_sim = True
    is_yellow = True

    # queues
    vision_q = Queue()
    gc_q = Queue()
    dispatch_q = Queue()
    planner_q = Queue()

    # world model
    wm_manager = WorldModelManager()
    wm_manager.start()
    wm = wm_manager.WorldModel()
    wmr = Process(target=wm_runner, args=(wm, vision_q, gc_q))

    # processes
    vision_wkr = Process(target=vision_worker, args=(vision_q, use_sim))
    gc_wkr = Process(target=run_gcfsm, args=(gc_q,))
    dispatch_wkr = Process(target=run_dispatcher, args=(dispatch_q, use_sim, is_yellow))
    planner_wkr = Process(target=run_planner, args=(wm, dispatch_q))
    striker_wkr = Process(target=run_simple_striker, args=(dispatch_q, wm, 0, is_yellow))

    vision_wkr.start()
    gc_wkr.start()
    wmr.start()
    dispatch_wkr.start()
    # planner_wkr.start()  # enable if you want path planner
    striker_wkr.start()

    vision_wkr.join()
    gc_wkr.join()
    wmr.join()
    dispatch_wkr.join()
    # planner_wkr.join()
    striker_wkr.join()


if __name__ == "__main__":
    main()
