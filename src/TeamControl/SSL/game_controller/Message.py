""" Message.py  
Contributors : Jason, Emma, Ali
This file contains classes (in python) to be parsed from SSL-Game-Controller (protobuf message)

Potential Known Error : 
Some fields within GAME EVENT > EVENT might be optional
-- fixed 07 July 2025 -- by Emma. 
"""
from TeamControl.SSL.game_controller.common import *
from TeamControl.SSL.game_controller.event_class import GameEvent
from typing import Optional, Union, List
from dataclasses import dataclass, field

@dataclass
class GameEventProposal:
    id:Optional[str] = None
    accepted:Optional[bool] = None
    game_events:Optional[List[GameEvent]] = field(default_factory=list)
    
    @classmethod
    def from_proto(cls,game_event_proposal):
        # optional
        id:str = str(game_event_proposal.id) if has_proto_field(game_event_proposal,"id") else None 
        accepted:bool = bool(game_event_proposal.accepted) if has_proto_field(game_event_proposal,"accepted") else None 
        # repeated
        game_events = [GameEvent.from_proto(g) for g in getattr(game_event_proposal, "game_events", [])]
        
        return cls(id,accepted,game_events)
        
@dataclass
class TeamInfo():
    # def __init__(self,name,score,red_cards,yellow_cards,timeouts,timeout_time,goalkeeper,
    #              foul_counter=None,ball_placement_failures=None,can_place_ball=None,max_allowed_bots=None,
    #                bot_substitution_intent=None,ball_placement_failures_reached=None,bot_substitution_allowed=None,
    #                bot_substitutions_left=None,bot_substitution_time_left=None,yellow_card_times=list()):
    # Required
    name:str
    score:int
    red_cards:int
    yellow_cards:int
    timeouts:int
    timeout_time:int
    goalkeeper:int
    
    ## Optional
    foul_counter:Optional[int] = None
    ball_placement_failures:Optional[int] = None
    can_place_ball:Optional[bool] = None
    max_allowed_bots:Optional[int] = None
    bot_substitution_intent:Optional[bool] = None
    ball_placement_failures_reached:Optional[bool] = None
    bot_substitution_allowed:Optional[bool] = None
    bot_substitutions_left:Optional[int] = None
    bot_substitution_time_left:Optional[int] = None
    
    ## repeated       
    yellow_card_times: Optional[List[str]] = field(default_factory=list)
    
    @classmethod
    def from_proto(cls,team):
        name = str(team.name)
        score = int(team.score)
        red_cards = int(team.red_cards)
        yellow_cards = int(team.yellow_cards)
        timeouts = int(team.timeouts)
        timeout_time = int(team.timeout_time)
        goalkeeper = int(team.goalkeeper)
        # Optional
        foul_counter = int(team.foul_counter) if has_proto_field(team,"foul_counter") else None
        ball_placement_failures = int(team.ball_placement_failures) if has_proto_field(team,"ball_placement_failures") else None
        can_place_ball = bool(team.can_place_ball) if has_proto_field(team,"can_place_ball") else None
        max_allowed_bots = int(team.max_allowed_bots) if has_proto_field(team,"max_allowed_bots") else None
        bot_substitution_intent = bool(team.bot_substitution_intent) if has_proto_field(team,"bot_substitution_intent") else None
        ball_placement_failures_reached = bool(team.ball_placement_failures_reached) if has_proto_field(team,"ball_placement_failures_reached") else None
        bot_substitution_allowed = bool(team.bot_substitution_allowed) if has_proto_field(team,"bot_substitution_allowed") else None
        bot_substitutions_left = int(team.bot_substitutions_left) if has_proto_field(team,"bot_substitutions_left") else None
        bot_substitution_time_left = int(team.bot_substitution_time_left) if has_proto_field(team,"bot_substitution_time_left") else None
        # repeated       
        yellow_card_times = [int(yellow_card_time) for yellow_card_time in getattr(team, "yellow_card_times", [])]
        
        return cls(name,score,red_cards,yellow_cards,timeouts,timeout_time,goalkeeper,
                   foul_counter,ball_placement_failures,can_place_ball,max_allowed_bots,
                   bot_substitution_intent,ball_placement_failures_reached,bot_substitution_allowed,
                   bot_substitutions_left,bot_substitution_time_left,yellow_card_times)
  
@dataclass
class RefereeMessage():
    """
    This is the main class !!! 
    parse the protobuf using from proto
    """
    packet_timestamp:int
    stage:Stage
    command:Command
    command_cnt:int
    command_ts:int
    yellow:TeamInfo
    blue:TeamInfo
    # Optional
    match_type:Optional[MatchType] = None
    source_id:Optional[str] = None
    stage_time_left:Optional[int] = None
    designated_position:Optional[Point] = None
    blue_team_on_positive_half:Optional[bool] = None
    next_command:Optional[Command] = None
    current_action_time_remaining:Optional[int] = None
    status_message:Optional[str] = None
    # Repeated
    game_events:Optional[List[GameEvent]] = field(default_factory=list)
    game_event_proposals:Optional[List[GameEventProposal]] = field(default_factory=list)
    
    @classmethod
    def from_proto(cls,referee):
        packet_timestamp = int(referee.packet_timestamp)
        stage = Stage(referee.stage)
        command = Command(referee.command)
        command_cnt = int(referee.command_counter)
        command_ts = int(referee.command_timestamp)
        yellow = TeamInfo.from_proto(referee.yellow)
        blue = TeamInfo.from_proto(referee.blue)
        ## optional
        match_type = MatchType(referee.match_type) if has_proto_field(referee,"match_type") else None        
        source_id = str(referee.source_identifier) if has_proto_field(referee,"source_identifier") else None
        stage_time_left = int(referee.stage_time_left) if has_proto_field(referee,"stage_time_left") else None
        designated_position = Point(referee.designated_position) if has_proto_field(referee,"designated_position") else None
        blue_team_on_positive_half = bool(referee.blue_team_on_positive_half) if has_proto_field(referee,"blue_team_on_positive_half") else None
        next_command = Command(referee.next_command) if has_proto_field(referee,"next_command") else None
        current_action_time_remaining = int(referee.current_action_time_remaining) if has_proto_field(referee,"current_action_time_remaining") else None
        status_message = str(referee.status_message) if has_proto_field(referee,"status_message") else None
        
        ## repeated
        game_events = [GameEvent.from_proto(g) for g in getattr(referee, "game_events", [])]
        game_event_proposals = [GameEventProposal.from_proto(gep) for gep in getattr(referee, "game_event_proposal", [])]

        return cls(packet_timestamp,stage,command,command_cnt,command_ts,yellow,blue,
                    match_type, source_id, stage_time_left, designated_position, blue_team_on_positive_half, next_command, 
                    current_action_time_remaining, status_message, game_events,game_event_proposals)
        
        
    def _command_has_changed(self,other):
        ## self is newer than other (<) older (>)
        if self.command != other.command:
            # print("command has changed")
            return True
        
    def _stage_has_changed(self,other):
        if self.stage != other.stage:
            # print("stage has changed")
            return True
    
    def _team_has_changed(self,other)-> bool:
        if self.blue_team_on_positive_half != other.blue_team_on_positive_half:
            return True
            # print("team sides changed")
        if self.yellow !=  other.yellow :
            return True
            # print("Different Yellow Data")
        if self.blue != other.blue : 
            return True
            # print("Different Blue data")
        return False
            
        

       
# if __name__ == "__main__":
    