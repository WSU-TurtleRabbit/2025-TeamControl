from multiprocessing import Event
from TeamControl.network.receiver import Receiver

IP = "127.0.0.1"
PORT_NUMBER = 50514
is_running = Event()

def main():
    recv = Receiver(is_running, ip=IP,port=PORT_NUMBER)
    print(f"RECEIVER CREATED @ {recv.addr}")
    while True:
        message,addr = recv.listen()
        print(f"message {message} recv from {addr}")
        
main()