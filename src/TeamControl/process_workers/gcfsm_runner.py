from TeamControl.SSL.game_controller.Message import RefereeMessage,GameEvent
from TeamControl.SSL.game_controller.common import Command,Stage,GameEventType,Team,PacketType, GameState
from TeamControl.network.ssl_sockets import GameControl

from TeamControl.process_workers.worker import BaseWorker
from multiprocessing import Queue
from multiprocessing.managers import ValueProxy
from enum import Enum,auto
from typing import List



class GCfsm (BaseWorker):
    def __init__(self, is_running, logger):
        super().__init__(is_running,logger)    
        self.recv:GameControl = GameControl(is_running=is_running)
        self.last_msg:RefereeMessage = None
        self.us_name:str = "TurtleRabbit"
        self.blue_is_positive:bool = None
        self.ge : List[GameEvent]= list()
        self.command = None
        self.stage = None
        
    @property
    def checks(self):
        return [
            self.check_team_color,
            self.check_team_sides,
            self.check_command,
            self.check_stage,
            self.check_game_events,
        ]
    
    def team_color(self,us=True) -> Team:
        if us: 
            return Team.YELLOW if self.us_yellow else Team.BLUE
        else:
            return Team.BLUE if self.us_yellow else Team.YELLOW
    
    
    def team_side_positive(self,us=True) -> bool:
        if self.blue_is_positive is None:
            self.logger.warning("No sides available, using default {self.us_positive=}")
            return self.us_positive
        color = self.team_color() if us else self.team_color(us=False)
        match color:
            case Team.YELLOW:
                return not(self.blue_is_positive)
            case Team.BLUE:
                return self.blue_is_positive
        
    def setup(self,*args):
        output_q, us_yellow, us_positive, shared_state = args
        self.output_q:bool = output_q
        self.us_yellow:bool = us_yellow
        self.us_positive:bool = us_positive 
        # value accessed via manager
        self.shared_state : GameState= shared_state   
        self.logger.info (f"[GCP] : Setup Complete {self.output_q=}, {us_yellow=}, {us_positive=}, {shared_state=}")
        
    def step(self):
        # for each step do : 
        new_info = self.recv.listen()
        
        if new_info is None:
            self.logger.error("[GCP] received None from Socket")
            raise AttributeError ("[GCFSM] NO GC Message")
        
        new_ref_msg:RefereeMessage = RefereeMessage.from_proto(new_info)
        # self.logger.info(f"Checking Updates  {new_ref_msg.packet_timestamp=}")
        self.check_updates(new_ref_msg)
        
        
        
    def check_updates(self,new_ref_msg:RefereeMessage):
        msg_list = []
        if self.last_msg is None:
            self.last_msg = new_ref_msg
            self.logger.info("INITIALISING WM")
            self.output_q.put([PacketType.INITIALISE, new_ref_msg])
        
        # if there's a sequence error (timestamp)
        elif self.last_msg.packet_timestamp > new_ref_msg.packet_timestamp:
            raise LookupError (f"new message packet is older than current {int(new_ref_msg.packet_timestamp) - int(self.last_msg.packet_timestamp)}")
            
        for check in self.checks:
            has_update,msg = check(new_ref_msg)
            
            if has_update :
                msg_list.append(msg)
        if len (msg_list) > 0:
            self.output_q.put(msg)
            self.logger.info(f"new update,{msg_list}")

    
    def check_team_color(self,new_ref_msg:RefereeMessage)-> bool:
        us_yellow:bool = new_ref_msg.yellow.name == self.us_name
        us_blue:bool = new_ref_msg.blue.name == self.us_name
        
        # validate result
        if us_yellow == us_blue or not(us_yellow,us_blue):
            return False,None
        
        if self.us_yellow == us_yellow and not(self.us_yellow) == us_blue:
            # no change color 
            return False,None
        else:
            self.us_yellow = True if us_yellow else False
            self.logger.info(f"Team Colors Sides Has Changed {self.us_yellow=}")

            return True,[PacketType.SWITCH_COLOR,self.us_yellow]

    def check_team_sides(self,new_ref_msg:RefereeMessage):
        # get attr
        # print(f"{self.blue_is_positive=}")
        blue_positive = new_ref_msg.blue_team_on_positive_half
        # if this field does not exists
        if blue_positive is None:
            return False, None
        # check what team we are
        if self.blue_is_positive != blue_positive:
            self.blue_is_positive = blue_positive # update
            self.us_positive = blue_positive if self.team_color == Team.BLUE else not(blue_positive)
            self.logger.info(f"Sides has changed, {self.team_side_positive()=}")
            return True, [PacketType.SWITCH_SIDES,self.us_positive]
        
        return False, None
            
        
    def check_game_events(self,new_ref_msg:RefereeMessage):
        new_ge= new_ref_msg.game_events
        update = False
        if len(new_ge) > 0:
            # there a game event update
            for i in new_ge: 
                # print(i)
                if i.id not in self.ge:
                    self.ge.append(i.id)
                    print(f"New Game Event ! {i.event},total {len(self.ge)}")
                    update = True
        if update: 
            return True,[PacketType.NEW_EVENT,self.ge]
        
        return False,None
                
    
    def check_command(self,new_ref_msg:RefereeMessage):
        if self.command != new_ref_msg.command:
            self.command = new_ref_msg.command
            return True,[PacketType.NEW_COMMAND,self.command]
        
        return False,None
    
    def check_stage(self,new_ref_msg:RefereeMessage):
        if self.stage != new_ref_msg.stage:
            self.stage = new_ref_msg.stage
            return True, [PacketType.NEW_STAGE,self.stage]
        
        return False,None