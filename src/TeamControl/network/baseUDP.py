""" BaseSocket.py
Fundamental socket creation and management module.

This module provides a reusable BaseSocket class that simplifies the creation 
and configuration of UDP, broadcast, and multicast sockets. It includes 
methods for automatic IP detection, port generation, and socket binding.

Author : Emma
Notes / Comments
This is the modified from the previous BaseUDP.py.
"""

import socket
import sys
import time
import random
import os 
import ast
import enum
from enum import auto
import logging

# Configure logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class SocketType(enum.IntEnum):
    """
    Enum for supported socket types.
    """
    SOCK_BROADCAST_UDP = auto()
    SOCK_UDP = auto()
    SOCK_MULTICAST_UDP = auto()

class BaseSocket():
    """
    Base class for socket creation and management.

    Provides automatic initialization, optional binding to a port, and utilities 
    for IP and port management.

    Attributes:
        ip (str): IP address of this device. Auto-detected if not specified.
        port (int): Port number of the socket. Randomized if 0 is provided.
        type (SocketType): Type of socket (UDP, Broadcast, Multicast).
        sock (socket.socket): Underlying socket object.
        is_ready (bool): Indicates if the socket is successfully initialized and bound.
    """
    
    def __init__(self, type:SocketType, ip:str=None, port:int=0, binding:bool=False):
        """
        Initialize the BaseSocket.

        Args:
            type (SocketType): Type of socket to create (UDP, Broadcast, Multicast).
            ip (str, optional): Device IP address. Defaults to None (auto-detect).
            port (int, optional): Port number. Defaults to 0 (randomized).
            binding (bool, optional): If True, binds the socket to the IP and port. Defaults to False.
        """
        self.ip:str = ip
        self.port:int = port
        self.type = type
        self.sock:socket = self._init_sock(type)
        self.is_ready = self._bind_sock() if binding is True else True

    @property 
    def ip(self) -> str:
        """Get the IP address of the socket."""
        return self._ip

    @ip.setter
    def ip (self,value):
        """Set the IP address of the socket."""
        if value is None: # since not specified, using system's IP
            value = self._obtain_sys_ip()
        if not isinstance(value, str): # type validation
            raise TypeError(f"IP Address (v4) must be a string, received {type(value)}")
        self._ip = value

    @property 
    def port(self) -> int:
        """Get the port number of the socket."""
        return self._port
    
    @port.setter
    def port(self,value:int):
        """Set the port number, generating a random one if value is 0."""
        if not isinstance(value, int): # type validation
            raise TypeError(f"Port must be an integer, got {type(value)}")
        if value == 0: # use generated port
            self._port = self._generate_port()
            self.use_generated_port = True 
        elif 1024 < value < 65535:  # do not edit this !!!
            self._port = value
            self.use_generated_port = False    
        else:
            raise ValueError("Port must be in range 1024 - 65535")
        
    @property
    def addr(self) -> tuple:
        """
        Get the socket's address as a tuple.

        Returns:
            tuple: (IP, port)
        """
        return (self.ip,self.port)
    
    def __str__(self):
        return f"{self.addr}"
    
    def __repr__(self):
        return f"{self.__class__.__name__} created on {self.addr}, available = {self.is_ready}"
    
    def close(self):
        """Close the socket and mark it as not ready."""
        self.is_ready = False
    
    def _bind_sock(self) -> bool:
        """
        Bind the socket to its IP and port.

        Returns:
            bool: True if binding was successful.

        Raises:
            ConnectionError: If the socket cannot be bound after several attempts.
        """
        is_binded = False
        tries = 0
        max_tries = 3
        
        while not is_binded and tries < max_tries + 1:
            try:
                self.sock.bind(self.addr)
                is_binded = True
            except socket.error as se:
                is_binded = False
                log.debug(f"socket binding failed: {se}")
                if self.use_generated_port is True: 
                    # generates port and tries again
                    self.port = self._generate_port()
                tries += 1
                continue   

        if is_binded is False:
            raise ConnectionError("Socket was not Activated Correctly")    
        return is_binded
        
    @staticmethod
    def _init_sock(type:SocketType) -> socket.socket:
        """
        Initialize a socket of the specified type.

        Args:
            type (SocketType): Type of socket.

        Returns:
            socket.socket: Initialized socket object.
        """
        if type == SocketType.SOCK_BROADCAST_UDP:
            broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            return broadcast
        elif type == SocketType.SOCK_UDP: 
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return udp
        elif type == SocketType.SOCK_MULTICAST_UDP:
            multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            multicast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            return multicast            
        
    @staticmethod
    def _obtain_sys_ip() -> str:
        """
        Attempt to obtain the system's IP address automatically.

        Returns:
            str: IP address of the device.

        Raises:
            ValueError: If the IP cannot be obtained automatically.
        """
        os_system = sys.platform
        match os_system:
            case 'win32':
                ip = socket.gethostbyname(socket.gethostname())
            case 'linux':
                ip = os.popen('hostname -I').read().strip().split(" ")[0]
                # ip = os.popen('hostname -I').read().strip().split(" ")[1] # for jetsons
                print(f'available : {os.popen("hostname -I").read().strip().split(" ")} , using : {ip}')
            case 'darwin':
                ip = os.popen('ipconfig getifaddr en0').read().strip()
            case _:
                raise ValueError("Cannot obtain IP, please input ip address manually")       
        return ip
    
    @staticmethod
    def _generate_port() -> int:
        """
        Generate a random port number in the range 5000-9000.

        Returns:
            int: Random port number.
        """
        port = random.randint(5000, 9000)
        log.debug(f"port generated : {port}")
        return port
    
    @staticmethod
    def is_valid_port(port: int) -> bool:
        """
        Validate if a port number is within the valid range.

        Args:
            port (int): Port number to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return 1024 < port < 65535
    
    @staticmethod
    def string_to_tuple(ip_with_port_string:str) -> tuple:
        """
        Convert a string representation of an address to a tuple.

        Args:
            ip_with_port_string (str): Address string in format "(IP, port)".

        Returns:
            tuple: (IP, port)
        """
        return ast.literal_eval(ip_with_port_string)

    
if __name__ == "__main__":
    test_sock = BaseSocket(type=SocketType.SOCK_UDP,binding=True)
    print(repr(test_sock))