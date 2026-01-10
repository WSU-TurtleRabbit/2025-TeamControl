from multiprocessing import Process, Queue, Event
from TeamControl.utils.Logger import LogSaver
from TeamControl.process_workers.worker import BaseWorker
from TeamControl.network.robot_command import RobotCommand
from TeamControl.network.sender import Sender
from TeamControl.network.ssl_sockets import grSimSender
import time
from pathlib import Path

import yaml
try:
    from yaml import CLoader as Loader
except ImportError as e:
    from yaml import Loader


class Dispatcher(BaseWorker):
    def __init__(self,is_running:Event ,logger:LogSaver, ):
        super().__init__(is_running,logger)
        
        self.running_commands = {}
        
    
    def setup(self,*args):
        """
        takes dispatcher_q and preset_config
        """
        q,config  = args
        self.q = q
        self.send_to_grSim = config.send_to_grSim
        self.yellow = config.yellow
        self.blue = config.blue
        self.r_sender = Sender()
        if self.send_to_grSim is True:
            self.g_sender = grSimSender(*config.grSim_addr)
        else:
            self.g_sender = None
        
         
        # self.g_sender = grSimSender()
        self.announce_initialisation()
        
    # Announce that the dispatcher has been created
    def announce_initialisation(self):
        print("Multi-robot dispatcher initialized!")
        print("Sender : ", self.r_sender)
        print("Sending to GrSim :", self.send_to_grSim)
    
    # Main processing loop
    def run(self):
        return super().run()
    
    def step(self):
        self.check_new_commands()
        self.handle_commands()
        self.check_command_timeout()
        
    def shutdown(self):
        print("reseting all robots to 0 ")
        self.reset_all_robots()
        self.handle_commands()
        print("Dispatcher has been shutdown")
        super().shutdown()
    # Get the next command from the queue and add it
    def check_new_commands(self):
        if not self.q.empty():
            queue_item = self.q.get_nowait()
            command, runtime = queue_item
            self.add(command, runtime)
        

    # Add a new command to the running commands and replace existing commands
    # for the robot with the same ID
    def add(self, command: RobotCommand, run_time: float):
        robot_id = command.robot_id
        isYellow = command.isYellow
        self.running_commands[robot_id] = {"isYellow": isYellow,"command": command, "runtime": run_time, "start_time": time.time()}
        self.logger.debug(f"[{robot_id=},{isYellow=}] New command added for {run_time}s , command: {command}")
        
    # Check if any commands have expired
    def check_command_timeout(self):
        expired_commands = []

        for robot_id, packet in self.running_commands.items():
            elapsed_time = time.time() - packet["start_time"]
            if elapsed_time >= packet["runtime"]:
                self.logger.debug(f"[Robot {robot_id}] Command expired after {elapsed_time:.2f}s")
                expired_commands.append(robot_id)

        for robot_id in expired_commands:
            self.reset_command(robot_id)

    # Set a do nothing command for the specified robot
    def reset_command(self, robot_id):
        isYellow = self.running_commands[robot_id]["isYellow"]
        reset_command = RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=0, dribble=0,isYellow=isYellow)
        self.logger.debug(f"[{isYellow=} {robot_id}] Reset to idle command")
        
        self.running_commands[robot_id] = {"isYellow" : isYellow, "command": reset_command, "runtime": 9999999, "start_time": time.time()}

    def reset_all_robots(self):
        for robot_id in self.running_commands:
            self.reset_command(robot_id=robot_id)
            
                
    # Handle all active commands for all robots
    def handle_commands(self):
        for robot_id, packet in self.running_commands.items():
            command = packet["command"]
            self.send_command(command)
            
    def send_command(self,command:RobotCommand):
        # this handles how you'd use different senders to send a command.
        shell_id = command.robot_id
        isYellow = command.isYellow
        robot_dict = self.get_dict_from_shell(shell_id,isYellow)
        self.r_sender.send(command,robot_dict["ip"],robot_dict["port"])
        if self.send_to_grSim is True:
            self.g_sender.send_robot_command(command,override_id=robot_dict["grSimID"])
        self.logger.info(f"RobotCommand has been sent to robot : {robot_dict["shellID"]=} , {robot_dict["grSimID"]=}")
    
    def get_dict_from_shell(self,shell_id,isYellow) -> str:
        team = self.yellow if isYellow is True else self.blue
        for robot_key, robot_dict in team.items():
            if robot_dict.get("shellID") == shell_id:
                return robot_dict
        raise ValueError (f"No robot with {shell_id=} found ")

    
# def run_dispatcher(is_running,q,use_sim,is_yellow):
#     d = dispatch(q=q,use_sim=use_sim,is_yellow=is_yellow)
#     d.process_q(is_running)
