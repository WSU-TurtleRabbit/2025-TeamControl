
""" SENDER
Sender includes :
    1. Sender            - UDP socket for server.
    2. Broadcaster       - UDP broadcast socket for server.
    3. Multicaster       - UDP Multicast socket (Not Implemented)
Raises:
    NotImplementedError: if user try to use an empty function
"""
import ast

import logging

from TeamControl.network.robot_command import RobotCommand
from TeamControl.network.baseUDP import BaseSocket,SocketType
import yaml
try:
    from yaml import CLoader as Loader
except ImportError as e:
    from yaml import Loader

import socket
import numpy
          
class YamlSender(BaseSocket):
    def __init__(self):
        file = open("ipconfig.yaml", "r")
        self.robot = yaml.load(file, Loader)
        super().__init__(type=SocketType.SOCK_UDP,ip='')

        
    
    def send_command(self, command:RobotCommand):
        """
        Sending command via UDP

        Args:
            command (RobotCommand): Command that wants to be sent
            d_addr (tuple[str,int]): destination address to be delivered to 
            
        Params: 
            encoded_Command(bytes): see Command.encode
        Exceptions:
            TypeError : Only Command or byte objects allowed
        """
        robot_id = str(command.robot_id)
        destination = self.robot[robot_id]["ip"]
        port = self.robot[robot_id]["port"]
        enocded_command:bytes = command.encode()
        self.sock.sendto(enocded_command, (destination, port))
        # print(robot_id,destination,port, command, " Message Sent")

            

