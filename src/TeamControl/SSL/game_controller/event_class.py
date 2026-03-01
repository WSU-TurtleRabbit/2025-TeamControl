from typing import Optional
from TeamControl.SSL.game_controller.common import *
from dataclasses import dataclass, field
from typing import Optional, Union, List

class BaseEvent():
    def __init__(self,event):
        pass
    
    def __repr__(self) -> str:
        return f"EventClass : {self.__class__.__name__} {vars(self)} "


class BallLeftField(BaseEvent):
    def __init__(self, event) -> None:
        self.by_team:Team = Team(event.by_team)
        self.by_bot:int =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location:Point = Point(event.location) if has_proto_field(event,"location") else None

class AimlessKick(BaseEvent):
    def __init__(self, event) -> None:
        self.by_team:Team = Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location:Point = Point(event.location) if has_proto_field(event,"location") else None
        self.kick_location:Point = Point(event.kick_location) if has_proto_field(event,"kick_location") else None

class Goal(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team:Team = Team(event.by_team)
        self.kicking_team:Team = Team(event.kicking_team) if has_proto_field(event,"kicking_team") else None
        self.location:Point = Point(event.location) if has_proto_field(event,"location") else None
        self.kick_location:Point = Point(event.kick_location) if has_proto_field(event,"kick_location") else None
        self.max_ball_height:float = float(event.max_ball_height) if has_proto_field(event,"max_ball_height") else None
        self.num_robots_by_team = int(event.num_robots_by_team) if has_proto_field(event,"num_robots_by_team") else None
        self.last_touch_by_team = int(event.last_touch_by_team) if has_proto_field(event,"last_touch_by_team") else None
        self.message = str(event.message) if has_proto_field(event,"message") else None

class indirect_goal(BaseEvent): # depeciated 
    def __init__(self,event) -> None:
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.kick_location = Point(event.kick_location) if has_proto_field(event,"kick_location") else None

class chipped_goal(BaseEvent): #depeciated
    def __init__(self,event) -> None:
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.kick_location = Point(event.kick_location) if has_proto_field(event,"kick_location") else None
        self.max_ball_height = float(event.max_ball_height) if has_proto_field(event,"max_ball_height") else None

class BotTooFastInStop(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.speed = float(event.speed) if has_proto_field(event,"speed") else None

class DefenderTooCloseToKickPoint(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance ") else None

class BotCrashDrawn(BaseEvent):
    def __init__(self,event):
        self.bot_yellow = int(event.bot_yellow) if has_proto_field(event,"bot_yellow") else None
        self.bot_blue = int(event.bot_blue) if has_proto_field(event,"bot_blue") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.crash_speed = float(event.crash_speed) if has_proto_field(event,"crash_speed") else None
        self.speed_diff = float(event.speed_diff) if has_proto_field(event,"speed_diff") else None
        self.crash_angle = float(event.crash_angle) if has_proto_field(event,"crash_angle") else None


class BotCrashUnique(BaseEvent):
    def __init__(self,event): 
        self.by_team:Team =Team(event.by_team)
        self.violator = int(event.violator) if has_proto_field(event,"violator") else None
        self.victim = int(event.victim) if has_proto_field(event,"victim") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.crash_speed = float(event.crash_speed) if has_proto_field(event,"crash_speed") else None
        self.speed_diff = float(event.speed_diff) if has_proto_field(event,"speed_diff") else None
        self.crash_angle = float(event.crash_angle) if has_proto_field(event,"crash_angle") else None

class BotPushedBot(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team:Team =Team(event.by_team)
        self.violator = int(event.violator) if has_proto_field(event,"violator") else None
        self.victim = int(event.victim) if has_proto_field(event,"victim") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance") else None

class BotTippedOver(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class BotDroppedParts(BaseEvent):
    def __init__(self,event):
        self.by_team:Team = Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class DefenderInDefenseArea(BaseEvent):
    def __init__(self,event):
        self.by_team:Team = Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class defender_in_defense_area_partially(BaseEvent): # depreciated
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class AttackerTouchedBallInDefenseArea(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location =Point(event.location) if has_proto_field(event,"location") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance") else None

class BotKickedBallTooFast(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location =Point(event.location) if has_proto_field(event,"location") else None
        self.initial_ball_speed = float(event.initial_ball_speed) if has_proto_field(event,"initial_ball_speed") else None
        self.chipped = bool(event.chipped) if has_proto_field(event,"chipped") else None

class BotDribbledBallTooFar(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.start = Point(event.start) if has_proto_field(event,"start") else None
        self.end = Point(event.end) if has_proto_field(event,"end") else None

class attacker_touched_opponent_in_defense_area(BaseEvent): # depreciated
    def __init__(self,event):
        self.by_team:Team = Team(event.by_team)
        self.by_bot = int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.victim = int(event.victim) if has_proto_field(event,"victim") else None
        self.location = Point(event.location) if has_proto_field(event,"location") else None

class AttackerDoubleTouchedBall(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location =Point(event.location) if has_proto_field(event,"location") else None

class AttackerTooCloseToDefenseArea(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class BotHeldBallDeliberately(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance") else None
        self.duration = float(event.duration) if has_proto_field(event,"duration") else None

class BotInterferedPlacement(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        self.by_bot =int(event.by_bot) if has_proto_field(event,"by_bot") else None
        self.location =Point(event.location) if has_proto_field(event,"location") else None

class MultipleCards(BaseEvent):
    def __init__(self, event) -> None:
        self.by_team:Team = Team(event.by_team)

class MultipleFouls(BaseEvent):
    def __init__(self,event):
        self.by_team:Team =Team(event.by_team)
        #repeated
        ## This will cause an infinite loop if a game event of MULTIPLE FOULS is here again and again ... 
        self.caused_game_events = [GameEvent.from_proto(caused_game_event) for caused_game_event in getattr(event, "caused_game_events", [])]

class multiple_placement_failure(BaseEvent): # depreciated
    def __init__(self, event) -> None:
        self.by_team : Team= Team(event.by_team)

class kick_timeout(BaseEvent): # depreciated
    def __init__(self,event):
        self.by_team : Team = Team(event.by_team)
        self.location : Point  = Point(event.location) if has_proto_field(event,"location") else None
        self.time : float = float(event.time) if has_proto_field(event,"time") else None

class NoProgressInGame(BaseEvent):
    def __init__(self,event) -> None:
        self.location: Point  = Point(event.location) if has_proto_field(event,"location") else None 
        self.time: float = float(event.time) if has_proto_field(event,"time") else None 

class PlacementFailed(BaseEvent):
    def __init__(self, event) -> None:
        self.by_team:Team = Team(event.by_team)
        self.remaining_distance:float = float(event.remaining_distance) if has_proto_field(event,"nearest_own_bot_distance") else None
        self.nearest_own_bot_distance :float = float(event.nearest_own_bot_distance) if has_proto_field(event,"nearest_own_bot_distance") else None

class UnsportingBehaviorMinor(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team :Team = Team(event.by_team)
        self.reason:str = str(event.reason)

class UnsportingBehaviorMajor(BaseEvent):
    def __init__(self,event) -> None:
        #required
        self.by_team :Team = Team(event.by_team)
        self.reason :str = str(event.reason)

class KeeperHeldBall(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.duration = float(event.duration) if has_proto_field(event,"duration") else None

class PlacementSucceeded(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team = Team(event.by_team)
        self.time_taken = float(event.time_taken) if has_proto_field(event,"time_taken") else None
        self.precision = float(event.precision) if has_proto_field(event,"precision") else None
        self.distance = float(event.distance) if has_proto_field(event,"distance") else None

class prepared(BaseEvent): #depreciated
    def __init__(self, event) -> None:
        self.time_taken = float(event.time_taken) if has_proto_field(event,"time_taken") else None

class BotSubstitution(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)

class ExcessiveBotSubstitution(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)

class ChallengeFlag(BaseEvent):
    def __init__(self,event):
        self.by_team =Team(event.by_team)

class ChallengeFlagHandled(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.accepted = bool(event.accepted) 

class EmergencyStop(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)

class TooManyRobots(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team)
        self.num_robots_allowed = int(event.num_robots_allowed) if has_proto_field(event,"num_robots_allowed") else None
        self.num_robots_on_field = int(event.num_robots_on_field) if has_proto_field(event,"num_robots_on_field") else None
        self.ball_location = Point(event.ball_location) if has_proto_field(event,"ball_location") else None

class BoundaryCrossing(BaseEvent):
    def __init__(self,event) -> None:
        self.by_team =Team(event.by_team) 
        self.location = Point(event.location) if has_proto_field(event,"location") else None

class PenaltyKickFailed(BaseEvent):
    def __init__(self,event):
        self.by_team =Team(event.by_team)
        self.location = Point(event.location) if has_proto_field(event,"location") else None
        self.reason = str(event.reason)  if has_proto_field(event,"reason") else None


EVENT_MAP = {
    # STOPPING : ball out of field events
    GameEventType.BALL_LEFT_FIELD_TOUCH_LINE : BallLeftField,
    GameEventType.BALL_LEFT_FIELD_GOAL_LINE : BallLeftField,
    GameEventType.AIMLESS_KICK : AimlessKick,

    # FOULS - STOPPING
    GameEventType.ATTACKER_TOO_CLOSE_TO_DEFENSE_AREA: AttackerTooCloseToDefenseArea,
    GameEventType.DEFENDER_IN_DEFENSE_AREA : DefenderInDefenseArea,
    GameEventType.BOUNDARY_CROSSING : BoundaryCrossing,
    GameEventType.KEEPER_HELD_BALL : KeeperHeldBall,
    GameEventType.BOT_DRIBBLED_BALL_TOO_FAR : BotDribbledBallTooFar,

    GameEventType.BOT_PUSHED_BOT : BotPushedBot,
    GameEventType.BOT_HELD_BALL_DELIBERATELY : BotHeldBallDeliberately,
    GameEventType.BOT_TIPPED_OVER : BotTippedOver,
    GameEventType.BOT_DROPPED_PARTS : BotDroppedParts,

    # FOULS - Non-Stopping
    GameEventType.ATTACKER_TOUCHED_BALL_IN_DEFENSE_AREA : AttackerTouchedBallInDefenseArea,
    GameEventType.BOT_KICKED_BALL_TOO_FAST: BotKickedBallTooFast,
    GameEventType.BOT_CRASH_UNIQUE : BotCrashUnique,
    GameEventType.BOT_CRASH_DRAWN : BotCrashDrawn,

    # FOULS - while ball out of play
    GameEventType.DEFENDER_TOO_CLOSE_TO_KICK_POINT : DefenderTooCloseToKickPoint,
    GameEventType.BOT_TOO_FAST_IN_STOP : BotTooFastInStop,
    GameEventType.BOT_INTERFERED_PLACEMENT : BotInterferedPlacement,
    
    # Scoring Goals
    GameEventType.POSSIBLE_GOAL : Goal,
    GameEventType.GOAL: Goal,
    GameEventType.INVALID_GOAL: Goal,

    # other events
    GameEventType.ATTACKER_DOUBLE_TOUCHED_BALL : AttackerDoubleTouchedBall,
    GameEventType.PLACEMENT_SUCCEEDED : PlacementSucceeded,
    GameEventType.PENALTY_KICK_FAILED : PenaltyKickFailed,

    GameEventType.NO_PROGRESS_IN_GAME : NoProgressInGame,
    GameEventType.PLACEMENT_FAILED : PlacementFailed,
    GameEventType.MULTIPLE_CARDS : MultipleCards,
    GameEventType.MULTIPLE_FOULS : MultipleFouls,
    GameEventType.BOT_SUBSTITUTION : BotSubstitution,
    GameEventType.EXCESSIVE_BOT_SUBSTITUTION : ExcessiveBotSubstitution,

    GameEventType.TOO_MANY_ROBOTS : TooManyRobots,
    GameEventType.CHALLENGE_FLAG : ChallengeFlag,
    GameEventType.CHALLENGE_FLAG_HANDLED : ChallengeFlagHandled,
    GameEventType.EMERGENCY_STOP : EmergencyStop,

    GameEventType.UNSPORTING_BEHAVIOR_MAJOR : UnsportingBehaviorMajor,
    GameEventType.UNSPORTING_BEHAVIOR_MINOR : UnsportingBehaviorMinor,
    ## Depreciated not included ##
}
@dataclass
class GameEvent:
    event:str # name of event
    type:Optional[GameEventType] = None # enum type
    created_timestamp:Optional[int] = None
    id:Optional[str] = None
    origin:Optional[List[str]] = field(default_factory=list)
    event_data:Optional[BaseEvent] = None
    # to access specific event related data use event_data
    
    @classmethod
    def from_proto(cls,game_event):
        #Oneof
        event:str = game_event.WhichOneof('event')#this will give you a string
        #optional
        id:str = game_event.id if has_proto_field(game_event,"id") else None 
        type:GameEventType = GameEventType(game_event.type) if has_proto_field(game_event,"type") else None 
        created_timestamp:int = int(game_event.created_timestamp) if has_proto_field(game_event,"created_timestamp") else None 
        #repeated
        origin:List[str] = [str(origin) for origin in getattr(game_event, "origin", [])]
        # Event object 
        event_data = None
        if type in EVENT_MAP:
            proto_event = getattr(game_event, event, None)
            if proto_event:
                event_data = EVENT_MAP[type](proto_event)
        else:
            print(f"[WARN] Unmapped event type: {type}")
        return cls(event,type,created_timestamp,id,origin,event_data)
