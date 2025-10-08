"""
Sender.py

UDP sending sockets for robot control.

Classes:
    Sender      - Generic UDP sender.
    Broadcaster - UDP broadcast sender.
    Multicaster - UDP multicast sender (Not Implemented).

Raises:
    NotImplementedError - if user attempts to use Multicaster.
"""

import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

from TeamControl.network.baseUDP import BaseSocket, SocketType
          
class Sender(BaseSocket):
    """
    Generic UDP sender socket.

    Attributes:
        destination_ip (str): IP of the remote destination.
        destination_port (int): Port of the remote destination.
    """
    def __init__(self, ip: str='127.0.0.1', port: int=0, type=SocketType.SOCK_UDP, binding=False) -> None:
        device_ip = None 
        device_port = self._generate_port()
        self.destination_ip = ip 
        self.destination_port = port
        super().__init__(ip=device_ip,port=device_port,type=type,binding=binding)
    
    @property
    def destination_ip(self):
        """Get the destination IP address."""
        return self._destination_ip
    
    @destination_ip.setter
    def destination_ip(self,value):
        """Set the destination IP address."""
        if not isinstance(value,str):
            raise TypeError("Need IP Address (v4) as string type")
        self._destination_ip = value
        
    @property
    def destination(self):
        """Return the destination as a tuple (IP, port)."""
        return (self.destination_ip, self.destination_port)
    
    
    def send(self, msg, ip:str=None, port:int=None):
        """
        Send a message via UDP.

        Args:
            msg (str | bytes): Message to send.
            ip (str, optional): Override destination IP.
            port (int, optional): Override destination port.
        """
        addr = tuple(ip,port) if isinstance(ip,str) and isinstance(port,int) else self.destination

        if not isinstance(msg, bytes):
            try:
                msg = msg.encode()
            except Exception as e:
                raise ValueError(f"Error encoding message: {e}")
            
        self.sock.sendto(msg,addr)
            
    
    def update_destination(self, destination:str|tuple[str,int]) -> None:
        """
        Update the default destination for future sends.

        Args:
            destination (str | tuple): IP and port, either as a tuple or string "(ip, port)".
        """
        if isinstance(destination,str):
            destination = self.string_to_tuple(destination)
        self.destination_ip = destination[0]
        self.port = destination[1]
    

class Broadcaster(Sender):
    """
    UDP broadcast sender.
    """
    def __init__(self, broadcasting_port: int = 12342) -> None:
        """
        UDP Broadcast sending channel

        Args:
            broadcasting_port (int, optional): Broadcast channel. Defaults to 12342. *This has to be calibrated with recipients
        
        Params:
            ip (str) : Default broadcast. See python udp_broadcast for more information.
        """
        ip = '<broadcast>'
        type =SocketType.SOCK_BROADCAST_UDP
        super().__init__(ip=ip,port=broadcasting_port,type=type,binding=True)
        
        
class Multicaster(Sender):
    """
    UDP multicast sender (Not Implemented)
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Multicaster is not yet implemented.")

if __name__ == "__main__":
    import time

    sender = Sender(ip='', port=50514)
    while True:
        # time.sleep(2)
        for i in range (500):
            sender.send(str(i))
        time.sleep(1)  # prevent network flooding