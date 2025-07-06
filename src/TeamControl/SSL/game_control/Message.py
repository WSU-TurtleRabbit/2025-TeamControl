""" Message.py  
Contributors : Jason, Emma, Ali
This file contains classes (in python) to be parsed from SSL-Game-Controller (protobuf message)

Potential Known Error : 
Some fields within GAME EVENT > EVENT might be optional (noted by "#o").
This will give out an error known as : attribute "xyz" not found. 
Please replace the "#o" with the following :  
`if getattr(event,"xyz") else None`

"""

import enum
from enum import auto, unique
from typing import Optional, Union, List


class Point():
    def __init__(self,point):
        # required
       self.x = float(point.x)
       self.y = float(point.y)
       self.vector = [self.x, self.y]
    

class Command(enum.Enum):
    HALT = 0
    STOP = 1
    NORMAL_START = 2
    FORCE_START = 3
    PREPARE_KICKOFF_YELLOW = 4
    PREPARE_KICKOFF_BLUE = 5
    PREPARE_PENALTY_YELLOW = 6
    PREPARE_PENALTY_BLUE = 7
    DIRECT_FREE_YELLOW = 8
    DIRECT_FREE_BLUE = 9
    INDIRECT_FREE_YELLOW = 10
    INDIRECT_FREE_BLUE = 11
    TIMEOUT_YELLOW = 12
    TIMEOUT_BLUE = 13
    GOAL_YELLOW = 14
    GOAL_BLUE = 15
    BALL_PLACEMENT_YELLOW = 16
    BALL_PLACEMENT_BLUE = 17

class Team(enum.Enum):
    UNKNOWN = 0
    YELLOW = 1
    BLUE = 2
    
class GameEventType(enum.Enum):
    UNKNOWN_GAME_EVENT_TYPE = 0

    BALL_LEFT_FIELD_TOUCH_LINE = 6
    BALL_LEFT_FIELD_GOAL_LINE = 7
    AIMLESS_KICK = 11

    ATTACKER_TOO_CLOSE_TO_DEFENSE_AREA = 19
    DEFENDER_IN_DEFENSE_AREA = 31
    BOUNDARY_CROSSING = 41
    KEEPER_HELD_BALL = 13
    BOT_DRIBBLED_BALL_TOO_FAR = 17

    BOT_PUSHED_BOT = 24
    BOT_HELD_BALL_DELIBERATELY = 26
    BOT_TIPPED_OVER = 27
    BOT_DROPPED_PARTS = 47

    ATTACKER_TOUCHED_BALL_IN_DEFENSE_AREA = 15
    BOT_KICKED_BALL_TOO_FAST = 18
    BOT_CRASH_UNIQUE = 22
    BOT_CRASH_DRAWN = 21

    DEFENDER_TOO_CLOSE_TO_KICK_POINT = 29
    BOT_TOO_FAST_IN_STOP = 28
    BOT_INTERFERED_PLACEMENT = 20
    EXCESSIVE_BOT_SUBSTITUTION = 48

    POSSIBLE_GOAL = 39
    GOAL = 8
    INVALID_GOAL = 42

    ATTACKER_DOUBLE_TOUCHED_BALL = 14
    PLACEMENT_SUCCEEDED = 5
    PENALTY_KICK_FAILED = 43

    NO_PROGRESS_IN_GAME = 2
    PLACEMENT_FAILED = 3
    MULTIPLE_CARDS = 32
    MULTIPLE_FOULS = 34
    BOT_SUBSTITUTION = 37
    TOO_MANY_ROBOTS = 38
    CHALLENGE_FLAG = 44
    CHALLENGE_FLAG_HANDLED = 46
    EMERGENCY_STOP = 45

    UNSPORTING_BEHAVIOR_MINOR = 35
    UNSPORTING_BEHAVIOR_MAJOR = 36

class Stage(enum.IntEnum):
    NORMAL_FIRST_HALF_PRE = 0
    NORMAL_FIRST_HALF = 1
    NORMAL_HALF_TIME = 2
    NORMAL_SECOND_HALF_PRE = 3
    NORMAL_SECOND_HALF = 4
    EXTRA_TIME_BREAK = 5
    EXTRA_FIRST_HALF_PRE = 6
    EXTRA_FIRST_HALF = 7
    EXTRA_HALF_TIME = 8
    EXTRA_SECOND_HALF_PRE = 9
    EXTRA_SECOND_HALF = 10
    PENALTY_SHOOTOUT_BREAK = 11
    PENALTY_SHOOTOUT = 12
    POST_GAME = 13

class MatchType(enum.Enum):
    UNKNOWN_MATCH = 0
    GROUP_PHASE = 1
    ELIMINATION_PHASE = 2
    FRIENDLY = 3
           
class GameEvent():
    def __init__(self,game_event):
        #Oneof
        self.event = game_event.WhichOneof('event')#this will give you a string
        #optional
        self.id = game_event.id if getattr(game_event,"id") else None 
        self.type:enum = GameEventType(game_event.type) if getattr(game_event,"type") else None 
        self.created_timestamp = game_event.created_timestamp if getattr(game_event,"created_timestamp") else None 
        #repeated
        self.origin = [str(origin) for origin in getattr(game_event, "origin", [])]
        self.match_event(game_event)

        
    def ball_left_field(self, event) -> None:
        self.by_team = Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location = Point(event.location) #o

    def aimless_kick(self, event) -> None:
        self.by_team = Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.kick_location = Point(event.kick_location) #o

    def goal(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.kicking_team = Team(event.kicking_team) #o
        self.location = Point(event.location) #o
        self.kick_location = Point(event.kick_location) #o
        self.max_ball_height = float(event.max_ball_height) #o
        self.num_robots_by_team = int(event.num_robots_by_team) #o
        self.last_touch_by_team = int(event.last_touch_by_team) #o
        self.message = str(event.message) #o

    def indirect_goal(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.kick_location = Point(event.kick_location) #o

    def chipped_goal(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.kick_location = Point(event.kick_location) #o
        self.max_ball_height = float(event.max_ball_height) #o

    def bot_too_fast_in_stop(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.speed = float(event.speed) #o

    def defender_too_close_to_kick_point(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.distance = float(event.distance) #o

    def bot_crash_drawn(self,event):
        self.bot_yellow = int(event.bot_yellow) #o
        self.bot_blue = int(event.bot_blue) #o
        self.location = Point(event.location) #o
        self.crash_speed = float(event.crash_speed) #o
        self.speed_diff = float(event.speed_diff) #o
        self.crash_angle = float(event.crash_angle) #o

    
    def bot_crash_unique(self,event): 
        self.by_team =Team(event.by_team)
        self.violator = int(event.violator) #o
        self.victim = int(event.victim) #o
        self.location = Point(event.location) #o
        self.crash_speed = float(event.crash_speed) #o
        self.speed_diff = float(event.speed_diff) #o
        self.crash_angle = float(event.crash_angle) #o

    def bot_pushed_bot(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.violator = int(event.violator) #o
        self.victim = int(event.victim) #o
        self.location = Point(event.location) #o
        self.distance = float(event.distance) #o

    def bot_tipped_over(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.ball_location = Point(event.ball_location) #o

    def bot_dropped_parts(self,event):
        self.by_team = Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.ball_location = Point(event.ball_location) #o

    def defender_in_defense_area_partially(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.location = Point(event.location) #o
        self.ball_location = Point(event.ball_location) #o

    def attacker_touched_ball_in_defense_area(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location =Point(event.location) #o
        self.distance = float(event.distance) #o

    def bot_kicked_ball_too_fast(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location =Point(event.location) #o
        self.initial_ball_speed = float(event.initial_ball_speed) #o
        self.chipped = bool(event.chipped) #o

    def bot_dribbled_ball_too_far(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.start = Point(event.start) #o
        self.end = Point(event.end) #o

    def attacker_touched_opponent_in_defense_area(self,event):
        self.by_team = Team(event.by_team)
        self.by_bot = int(event.by_bot) #o
        self.victim = int(event.victim) #o
        self.location = Point(event.location) #o

    def attacker_double_touched_ball(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location =Point(event.location) #o

    def attacker_too_close_to_defense_area(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.distance = float(event.distance) #o
        self.ball_location = Point(event.ball_location) #o

    def bot_held_ball_deliberately(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.distance = float(event.distance) #o
        self.duration = float(event.duration) #o

    def bot_interfered_placement(self,event):
        self.by_team =Team(event.by_team)
        self.by_bot =int(event.by_bot) #o
        self.location =Point(event.location) #o

    def multiple_cards(self, event) -> None:
        self.by_team : Team = Team(event.by_team)

    def multiple_fouls(self,event):
        self.by_team =Team(event.by_team)
        #repeated
        self.caused_game_events = [GameEvent(caused_game_event) for caused_game_event in getattr(event, "caused_game_events", [])]
 
    def multiple_placement_failure(self, event) -> None:
        self.by_team : Team= Team(event.by_team)

    def multiple_placement_failure(self,event):
        self.by_team =Team(event.by_team)
        self.location =Point(event.location)
        self.time = float(event.time)

    def no_progress_in_game(self,event) -> None:
        self.location: Point  = Point(event.location) if getattr(event,"location") else None
        self.time: float = float(event.time) if getattr(event,"time") else None

    def placement_failure(self, event) -> None:
        self.by_team:Team = Team(event.by_team)
        self.remaining_distance:float = float(event.remaining_distance) if getattr(event,"nearest_own_bot_distance") else None
        self.nearest_own_bot_distance :float = float(event.nearest_own_bot_distance) if getattr(event,"nearest_own_bot_distance") else None

    def unsporting_behavior_minor(self,event) -> None:
        self.by_team :Team = Team(event.by_team)
        self.reason:str = str(event.reason)

    def unsporting_behavior_major(self,event) -> None:
        #required
        self.by_team :Team = Team(event.by_team)
        self.reason :str = str(event.reason)

    def keeper_held_ball(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.location = Point(event.location) #O
        self.duration = float(event.duration) #o

    def placement_succeeded(self,event) -> None:
        self.by_team = Team(event.by_team)
        self.time_taken = float(event.time_taken) #o
        self.precision = float(event.precision) #o
        self.distance = float(event.distance) #o

    def prepared(self, event) -> None:
        self.time_taken = float(event.time_taken) #o

    def bot_substitution(self,event) -> None:
        self.by_team =Team(event.by_team)

    def excessive_bot_substitution(self,event) -> None:
        self.by_team =Team(event.by_team)

    def challenge_flag(self,event):
        self.by_team =Team(event.by_team)

    def challenge_flag_handled(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.accepted = bool(event.accepted) 

    def emergency_stop(self,event) -> None:
        self.by_team =Team(event.by_team)

    def too_many_robots(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.num_robots_allowed = int(event.num_robots_allowed) #o
        self.num_robots_on_field = int(event.num_robots_on_field) #o
        self.ball_location = Point(event.ball_location) #o

    def boundary_crossing(self,event) -> None:
        self.by_team =Team(event.by_team) 
        self.location = Point(event.location) #o

    def penalty_kick_failed(self,event):
        self.by_team =Team(event.by_team)
        self.location = Point(event.location) #o
        self.reason = str(event.reason)  #o
        
    
    def match_event(self,game_event):
        ## access the corresponding event attribute
        event = getattr(game_event,self.event) 
        match self.type:
            case GameEventType.BALL_LEFT_FIELD_TOUCH_LINE:
                return self.ball_left_field(event)
            case GameEventType.BALL_LEFT_FIELD_GOAL_LINE:
                return self.ball_left_field(event)
            case GameEventType.AIMLESS_KICK:
                return self.aimless_kick(event)
            case GameEventType.ATTACKER_TOO_CLOSE_TO_DEFENSE_AREA:
                return self.attacker_touched_ball_in_defense_area(event)
            case GameEventType.DEFENDER_IN_DEFENSE_AREA:
                return self.defender_in_defense_area_partially(event)
            case GameEventType.BOUNDARY_CROSSING:
                return self.boundary_crossing(event)
            case GameEventType.KEEPER_HELD_BALL:
                return self.keeper_held_ball(event)
            case GameEventType.BOT_DRIBBLED_BALL_TOO_FAR:
                return self.bot_dribbled_ball_too_far(event)
            case GameEventType.BOT_PUSHED_BOT:
                return self.bot_push_bot(event)
            case GameEventType.BOT_HELD_BALL_DELIBERATELY:
                return self.bot_held_ball_deliberately(event)
            case GameEventType.BOT_TIPPED_OVER:
                return self.bot_tipped_over(event)
            case GameEventType.BOT_DROPPED_PARTS:
                return self.bot_dropped_parts(event)
            case GameEventType.ATTACKER_TOUCHED_BALL_IN_DEFENSE_AREA:
                return self.attacker_too_close_to_defense_area(event)
            case GameEventType.BOT_KICKED_BALL_TOO_FAST:
                return self.bot_kicked_ball_too_fast(event)
            case GameEventType.BOT_CRASH_UNIQUE:
                return self.bot_crash_unique(event)
            case GameEventType.BOT_CRASH_DRAWN:
                return self.bot_crash_drawn(event)
            case GameEventType.DEFENDER_TOO_CLOSE_TO_KICK_POINT:
                return self.defender_too_close_to_kick_point(event)
            case GameEventType.BOT_TOO_FAST_IN_STOP:
                return self.bot_too_fast_in_stop(event)
            case GameEventType.BOT_INTERFERED_PLACEMENT:
                return self.bot_interfered_placement(event)
            case GameEventType.EXCESSIVE_BOT_SUBSTITUTION:
                return self.excessive_bot_substitution(event)
            case GameEventType.POSSIBLE_GOAL:
                return self.goal(event)
            case GameEventType.GOAL:
                return self.goal(event)
            case GameEventType.INVALID_GOAL:
                return self.goal(event)
            case GameEventType.ATTACKER_DOUBLE_TOUCHED_BALL:
                return self.attacker_double_touched_ball(event)
            case GameEventType.PLACEMENT_SUCCEEDED:
                return self.placement_succeeded(event)
            case GameEventType.PENALTY_KICK_FAILED:
                return self.penalty_kick_failed(event)
            case GameEventType.NO_PROGRESS_IN_GAME:
                return self.no_progress_in_game(event)
            case GameEventType.PLACEMENT_FAILED:
                return self.placement_failure(event)
            case GameEventType.MULTIPLE_CARDS:
                return self.multiple_cards(event)
            case GameEventType.MULTIPLE_FOULS:
                return self.multiple_fouls(event)
            case GameEventType.BOT_SUBSTITUTION:
                return self.bot_substitution(event)
            case GameEventType.TOO_MANY_ROBOTS:
                return self.too_many_robots(event)
            case GameEventType.CHALLENGE_FLAG:
                return self.challenge_flag(event)
            case GameEventType.CHALLENGE_FLAG_HANDLED:
                return self.challenge_flag_handled(event)
            case GameEventType.EMERGENCY_STOP:
                return self.emergency_stop(event)
            case GameEventType.UNSPORTING_BEHAVIOR_MINOR:
                return self.unsporting_behavior_minor(event)
            case GameEventType.UNSPORTING_BEHAVIOR_MAJOR:
                return self.unsporting_behavior_major(event)


class GameEventProposal():
    def __init__(self,game_event_proposal):
            # optional
            self.id:str = str(game_event_proposal.id) if getattr(game_event_proposal,"id") else None 
            self.accepted:bool = bool(game_event_proposal.accepted) if getattr(game_event_proposal,"accepted") else None 
            # repeated
            self.game_events = [GameEvent(game_event) for game_event in getattr(game_event_proposal, "game_events", [])]
 
class TeamInfo():
    def __init__(self,team):
        # Required
        self.name = str(team.name)
        self.score = int(team.score)
        self.red_cards = int(team.red_cards)
        self.yellow_cards = int(team.yellow_cards)
        self.timeouts = int(team.timeouts)
        self.timeout_time = int(team.timeout_time)
        self.goalkeeper = int(team.goalkeeper)
        
        ## Optional
        self.foul_counter = int(team.foul_counter) if getattr(team,"foul_counter") else None
        self.ball_placement_failures = int(team.ball_placement_failures) if getattr(team,"ball_placement_failures") else None
        self.can_place_ball = bool(team.can_place_ball) if getattr(team,"can_place_ball") else None
        self.max_allowed_bots = int(team.max_allowed_bots) if getattr(team,"max_allowed_bots") else None
        self.bot_substitution_intent = bool(team.bot_substitution_intent) if getattr(team,"bot_substitution_intent") else None
        self.ball_placement_failures_reached = bool(team.ball_placement_failures_reached) if getattr(team,"ball_placement_failures_reached") else None
        self.bot_substitution_allowed = bool(team.bot_substitution_allowed) if getattr(team,"bot_substitution_allowed") else None
        self.bot_substitutions_left = int(team.bot_substitutions_left) if getattr(team,"bot_substitutions_left") else None
        self.bot_substitution_time_left = int(team.bot_substitution_time_left) if getattr(team,"bot_substitution_time_left") else None
        
        ## repeated       
        self.yellow_card_times = [int(yellow_card_time) for yellow_card_time in getattr(team, "yellow_card_times", [])]

    
class RefereeMessage():
    """
    This is the main class !!! 
    """
    def __init__(self,referee):
        self.packet_timestamp = int(referee.packet_timestamp)
        self.stage = Stage(referee.stage)
        self.command = Command(referee.command)
        self.command_cnt = int(referee.command_counter)
        self.command_ts = int(referee.command_timestamp)
        self.yellow = TeamInfo(referee.yellow)
        self.blue = TeamInfo(referee.blue)
        ## optional
        self.match_type = MatchType(referee.match_type) if getattr(referee,"match_type") else None        
        self.source_id = str(referee.source_identifier) if getattr(referee,"source_identifier") else None
        self.stage_time_left = int(referee.stage_time_left) if getattr(referee,"stage_time_left") else None
        self.designated_position = Point(referee.designated_position) if getattr(referee,"designated_position") else None
        self.blue_team_on_positive_half = bool(referee.blue_team_on_positive_half) if getattr(referee,"blue_team_on_positive_half") else None
        self.next_command = Command(referee.next_command) if getattr(referee,"next_command") else None
        self.current_action_time_remaining = int(referee.current_action_time_remaining) if getattr(referee,"current_action_time_remaining") else None
        self.status_message = str(referee.status_message) if getattr(referee,"status_message") else None
        
        ## repeated
        self.game_events = [GameEvent(game_event) for game_event in getattr(referee, "game_events", [])]
        self.game_event_proposals = [GameEventProposal(game_event_proposal) for game_event_proposal in getattr(referee, "game_event_proposal", [])]

        
        
       
if __name__ == "__main__":
    from TeamControl.network import GameControl
    import time
    
    gc_recv = GameControl()
    
    while True:
        ref_msg = gc_recv.listen()
        start_time = time.time()
        new_ref_msg = RefereeMessage(referee=ref_msg)
        print(ref_msg)
        print(f"internal process time :{time.time()-start_time}\t\n"+
              f"recv + process time :{time.time()-new_ref_msg.packet_timestamp/1000000}\t\n"+
              f"{(new_ref_msg.game_events[0].by_team)}\t  {type(new_ref_msg.game_events[0].type)}\n"
              )