from multiprocessing import Process, Queue
from TeamControl.network.robot_command import RobotCommand
from TeamControl.network.YamlSender import YamlSender
from TeamControl.network.ssl_sockets import grSimSender
import time

class dispatch():
    def __init__(self, q,use_sim,is_yellow):
        self.q = q
        self.is_yellow = is_yellow 
        self.use_sim = use_sim

        self.running_commands = {}
        self.announce_initialisation()
        self.y_sender = YamlSender() 
        self.g_sender = grSimSender(ip="192.168.1.4",is_yellow=is_yellow)

    # Announce that the dispatcher has been created
    def announce_initialisation(self):
        print("Multi-robot dispatcher initialized!")
        print("socket is yellow :", self.is_yellow)
        print("Simulation is active :", self.use_sim)

    # Main processing loop
    def process_q(self):
        while True:
            lap_time = time.time()
            self.check_new_commands()
            # if time.time() > lap_time + 0.05:
            #     lap_time = time.time() +0.05
            self.handle_commands()
            self.check_command_timeout()
            

    # Get the next command from the queue and add it
    def check_new_commands(self):
        if not self.q.empty():
            queue_item = self.q.get_nowait()
            command, runtime = queue_item # this requires a command and runtime
            self.add(command, runtime)

    # Add a new command to the running commands and replace exisiting commands for the robot with the same ID
    def add(self, command, run_time):
        robot_id = command.robot_id
        self.running_commands[robot_id] = {"command": command, "runtime": run_time, "start_time": time.time()}
        print(f"[Robot {robot_id}] New command added for {run_time}s , command: {command}")
        
    # Check if any commands have expired
    def check_command_timeout(self):
        expired_commands = []
        
        for robot_id, packet in self.running_commands.items():
            elapsed_time = time.time() - packet["start_time"]
            
            if elapsed_time >= packet["runtime"]:
                print(f"[Robot {robot_id}] Command expired after {elapsed_time:.2f}s")
                expired_commands.append(robot_id)

        for robot_id in expired_commands:
            self.reset_command(robot_id)

    # Set a do nothing command for the specified robot
    def reset_command(self, robot_id):
        reset_command = RobotCommand(robot_id=robot_id, vx=0, vy=0, w=0, kick=0, dribble=0)
        print(f"[Robot {robot_id}] Reset to idle command")
        
        self.running_commands[robot_id] = {"command": reset_command, "runtime": 9999999, "start_time": time.time()}

    # Handle all active commands for all robots
    def handle_commands(self):
        for robot_id, packet in self.running_commands.items():
            command = packet["command"]
            self.send_command(command)
            
    def send_command(self,command:RobotCommand):
        # this handles how you'd use different senders to send a command.
        self.y_sender.send_command(command)
        if self.use_sim is True:
            self.g_sender.send_command(command)
            
def run_dispatcher(q,use_sim,is_yellow):
    d = dispatch(q=q,use_sim=use_sim,is_yellow=is_yellow)
    d.process_q()