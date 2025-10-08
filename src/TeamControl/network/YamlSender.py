"""
sender.py

UDP-based command sender that reads robot network configuration from a YAML file.

This module provides:
    1. YamlSender — Sends `RobotCommand` objects to multiple robots over UDP,
       using IP and port mappings specified in a YAML configuration file.

Example YAML file (`ipconfig.yaml`):
    "1": 
    ip: "127.0.0.0"
    port: 1234
    shell_number: 6

    "2": 
    ip: "127.0.0.0"
    port: 1234
    shell_number: 7

Example usage:
    >>> sender = YamlSender()
    >>> commands = [RobotCommand(1), RobotCommand(2)]
    >>> sender.send_command(commands)

Raises:
    FileNotFoundError: If the YAML configuration file is missing.
    TypeError: If command_list contains non-RobotCommand objects.
"""

import logging
import socket
import yaml

from TeamControl.network.robot_command import RobotCommand
from TeamControl.network.baseUDP import BaseSocket,UDP

try:
    from yaml import CLoader as Loader
except ImportError as e:
    from yaml import Loader
  
class YamlSender(BaseSocket):
    """
    UDP command sender using YAML configuration.

    This class sends `RobotCommand` packets to multiple robot endpoints
    defined in a YAML configuration file (`src/TeamControl/utils/ipconfig.yaml`).

    Each robot’s IP and port are read from the YAML file, allowing flexible
    and centralized network configuration.

    Attributes:
        robot (dict): Mapping of robot IDs to their network configurations.
        sock (socket.socket): UDP socket for sending data.
    """

    CONFIG_PATH = "src/TeamControl/utils/ipconfig.yaml"

    def __init__(self) -> None:
        """Initialize the sender and load robot network configuration."""
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            with open(self.CONFIG_PATH, "r") as file:
                self.robot = yaml.load(file, Loader=Loader)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found: {self.CONFIG_PATH}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}") from e

        logging.info(f"Loaded robot configuration: {self.robot}")
        
    
    def send_command(self, command_list:RobotCommand) -> None:
        """
        Send a list of robot commands via UDP.

        Iterates through each `RobotCommand` object, determines its destination
        from the YAML configuration, and sends the encoded packet.

        Args:
            command_list (list[RobotCommand]): List of commands to send.

        Raises:
            TypeError: If any item in `command_list` is not a `RobotCommand` instance.
            KeyError: If a robot ID is not found in the YAML configuration.
        """

        for command in command_list:
            robot_id = str(command.robot_id)

            if robot_id not in self.robot:
                raise KeyError(f"Robot ID {robot_id} not found in configuration.")
            
            destination = self.robot[robot_id]["ip"]
            port = self.robot[robot_id]["port"]

            encoded_command:bytes = command.encode()
            self.sock.sendto(encoded_command, (destination, port))

            logging.debug(f"Sent command to Robot {robot_id} -> {destination}:{port}")

        logging.info(f"Successfully sent {len(command_list)} commands.")
            

if __name__ == "__main__" :
    # Example usage
    sender = YamlSender()
    commands = [RobotCommand(i) for i in range(1, 5)]
    sender.send_command(commands)