"""
Run this to check if you can receive data from SSL VISION Or GRSIM at port 10006
"""

from TeamControl.network.ssl_sockets import Vision
from multiprocessing import Event
is_running = Event()
is_running.set()
def test_vision_initialization():
    vision = Vision(is_running=is_running)
    print(vision.addr)
    assert vision is not None
    data = vision.listen()
    # assert data is not None
    print(data)
    
test_vision_initialization()