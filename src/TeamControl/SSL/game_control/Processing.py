""" Processing.py 
Contributors : Emma,  
This file contains how we process the Game Controller data after parsing in Message.py 
This file is an extension of Message.py, in which compares and stores static versions of the data

working in progress
"""

from TeamControl.SSL.game_control.Message import *
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Processing():
    def __init__(self,us_yellow: bool=None,us_positive: bool=None):
        self._command:Command = None
        self.us_yellow:bool = us_yellow
        self.us_positive:bool = us_positive
        self.timeout_times:int = 0
        self._game_event:GameEvent = None
    
    @property
    def command (self):
        return self._command
    @command.setter
    def command(self,cmd):
        if not isinstance(cmd, Command):
            raise TypeError("Requires Command Enum type object")

        if self._command != cmd:
            log.info(f"Command has been updated from : {self.command} to : {cmd}")
            self._command = cmd

    @property 
    def game_event(self):
        return self._game_event
    @game_event.setter
    def game_event(self,ge):
        if ge is None:
            return
        if not isinstance(ge,GameEvent):
            raise TypeError("need type : GameEvent")
        if self._game_event != ge:
            log.info(f"new game event : {ge}")
            self._game_event = ge
        
        
    @property
    def state (self): 
        match self.command:
            case Command.HALT:
                state = self.halt
            case Command.STOP:
                state = self.stop
            case Command.NORMAL_START:
                state = self.start
            case Command.FORCE_START:
                state = self.start
            case Command.PREPARE_KICKOFF_YELLOW :
                state = self.prepare_kickoff_yellow
            case Command.PREPARE_KICKOFF_BLUE :
                state = self.prepare_kickoff_blue
            case Command.PREPARE_PENALTY_YELLOW :
                state = self.prepare_penalty_yellow
            case Command.PREPARE_PENALTY_BLUE :
                state = self.prepare_penalty_blue
            case Command.DIRECT_FREE_YELLOW :
                state = self.direct_free_yellow
            case Command.DIRECT_FREE_BLUE :
                state = self.direct_free_blue
            case Command.INDIRECT_FREE_YELLOW :
                state = self.indirect_free_yellow
            case Command.INDIRECT_FREE_BLUE :
                state = self.indirect_free_blue
            case Command.TIMEOUT_YELLOW :
                state = self.timeout_yellow
            case Command.TIMEOUT_BLUE :
                state = self.timeout_blue
            case Command.GOAL_YELLOW :
               state =  self.goal_yellow
            case Command.GOAL_BLUE :
               state =  self.goal_blue
            case Command.BALL_PLACEMENT_YELLOW :
                state =  self.ball_placement_yellow
            case Command.BALL_PLACEMENT_BLUE :
                state =  self.ball_placement_blue
            case _:
                state = self.do_nothing
        return state
    
    
    def update(self,ref_msg:RefereeMessage):
        """update
        updates this processing class data
        """
        self.command:Command = ref_msg.command
        self.__set_team(ref_msg.blue,ref_msg.yellow, ref_msg.blue_team_on_positive_half)
        self.timeout_time = self.get_our_team(ref_msg).timeout_time
        return self.state

    def __set_team(self, blue:TeamInfo, yellow:TeamInfo, blue_is_positive:bool):
        if blue.name == "TurtleRabbit" and self.us_yellow is True:
            # updates us_yellow to false
            self.us_yellow = False
            log.info("We are BLUE Team")
        elif yellow.name == "TurtleRabbit" and self.us_yellow is not True:
            self.us_yellow = False
            log.info("We are BLUE Team")
                    
        if blue_is_positive is None:
            return
        elif bool(blue_is_positive) == bool(self.us_yellow):
            self.us_positive = False
            log.info("We are on Negative Half")

        else:
            self.us_positive = True
            log.info("We are on Positive Half")


    def get_our_team(self,ref_msg: RefereeMessage) -> TeamInfo:
        if self.us_yellow is True:
            return ref_msg.yellow
        elif self.us_yellow is False:
            return ref_msg.blue
        else:
            raise AttributeError("us_yellow is not set")
            # return None
            
    
    def do_nothing(self):
        print("No command, doing nothing")

    
    def halt(self):
        print("game halted")
        
    def stop(self):
        print("game stopped")
    
    def start(self):
        print("game starting")

    def prepare_kickoff_yellow(self):
        print(f"Kickoff : us ? {self.is_our_team(isYellow=True)}")
    
    def prepare_kickoff_blue(self):
        print(f"Kickoff : us ? {self.is_our_team(isYellow=False)}")
    
    def prepare_penalty_yellow(self):
        print(f"prep for penalty : us ? {self.is_our_team(isYellow=True)}")
    
    def prepare_penalty_blue(self):
        print(f"prep for penalty : us ? {self.is_our_team(isYellow=False)}")
    
    def direct_free_yellow(self):
        print(f"direct Free : us ? {self.is_our_team(isYellow=True)}")
        
    def direct_free_blue(self):
        print(f"direct Free : us ? {self.is_our_team(isYellow=False)}")
    
    def indirect_free_yellow(self):
        print(f"Indirect Free : us ? {self.is_our_team(isYellow=True)}")
        
    def indirect_free_blue(self):
        print(f"Indirect Free : us ? {self.is_our_team(isYellow=False)}")
    
    def timeout_yellow(self):
        print(f"Timeout : us ? {self.is_our_team(isYellow=True)}")
    
    def timeout_blue(self):
        print(f"Timeout : us ? {self.is_our_team(isYellow=False)}")
        
    def ball_placement_yellow(self):
        print(f"Ball Placement : us ? {self.is_our_team(isYellow=True)}")

    def ball_placement_blue(self):
        print(f"Ball Placement : us ? {self.is_our_team(isYellow=False)}")

    def goal_yellow(self):
        print(f"Yellow Team has scored a goal, us ? {self.is_our_team(isYellow=True)}")
    
    def goal_blue(self):
        print(f"Blue Team has scored a goal, us ? {self.is_our_team(isYellow=False)}")
    



    def is_our_team(self,isYellow: bool):
        """
        matching the team's turn using the boolean "isYellow"

        Args:
            isYellow (bool): if the current command's Term is for Yellow Team

        Returns:
            boolean: is our Turn : T = YES / F = NO
        """
        if isYellow is True: 
            return self.us_yellow
        elif isYellow is False:
            return not(self.us_yellow)
        

if __name__ == "__main__":
    from TeamControl.network import GameControl
    import time
    
    gc_recv = GameControl()
    gc = Processing()
    gc.us_yellow = False
    
    while True:
        # for i in range (18):
        #     print(i)
        #     gc.command = Command(i)
        #     gc.state()

        ref_msg = gc_recv.listen()
        start_time = time.time()
        message = RefereeMessage(referee=ref_msg)
        gc.update(message)
        gc.state()
        log.debug(f"Internal Processing Time : {time.time() - start_time} \n")
        