## to test with YAML Sender (that use relative pathing) run it at 1 level up i.e. python3 ./tests/m_processing_test.py
from multiprocessing import Queue,Process,Event
from TeamControl.dispatcher.dispatch import Dispatcher
from TeamControl.utils.yaml_config import Config
from TeamControl.dispatcher.generate_packet import generate_w_interval



if __name__ == "__main__":
    q = Queue()
    is_yellow = True
    is_running = Event()
    is_running.set()
    c = Config()
    input = Process(target=generate_w_interval, args=(q,))
    output = Process(target=Dispatcher.run_worker, args=(is_running,None,q,c))
    
    input.start()
    output.start()
    
    input.join()
    output.join()
