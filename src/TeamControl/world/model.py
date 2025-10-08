"""
world_model.py

Central World Model (wm) for the SSL robots.

This module provides an interface for robot and game state information. 
It maintains vision frames, field geometry, and game controller updates, 
allowing other processes to query or act on the latest world state.

Features:
    - Multiprocessing safe with Manager values.
    - History of frames stored for temporal queries.
    - Keeps track of active robots, team assignment, and ball location.
    - Provides helpers for accessing our team and opponent robots.

Author: Emma
"""

from TeamControl.SSL.vision.frame_list import FrameList
from TeamControl.SSL.vision.field import GeometryData,FieldSize
from TeamControl.SSL.vision.frame import Frame
from TeamControl.SSL.game_controller.fsm import PacketType,GameState

from multiprocessing import Queue,Manager
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)


class WorldModel:
    """
    WorldModel (wm) maintains the global state of the SSL environment.

    Attributes:
        update_interval (int): Number of frames before incrementing version.
        use_sim (bool): Whether the world model is running in simulation mode.
        frame_list (FrameList[Frame]): Historical list of frames.
        geometry (GeometryData): Field and model geometry.
        field (FieldSize): Field dimensions.
        _version (Manager.Value): Version counter for multiprocessing.
        robot_active (int): Number of active robots.
        game_state (GameState): Current game state.
        _us_yellow (bool): Whether our team is yellow.
        _us_positive (bool): Whether our coordinate system is positive.
        blf_location (tuple): Last recorded ball-left-field location.
    """
    def __init__(self,update_interval:int=5,history:int=60, use_sim:bool=True,us_yellow=True,us_positive=True):
        mgr = Manager()
        self._us_yellow = us_yellow
        self._us_positive = us_positive
        self.count = 0
        self.update_interval:int = update_interval
        self.use_sim:bool = use_sim 
        self.frame_list:FrameList[Frame] = FrameList(history=history)
        self.geometry:GeometryData = None
        self.field:FieldSize = None
        self._version = mgr.Value('i', 0)  # int counter
        self.robot_active = 6 # robots active
        self.game_state = GameState.HALTED
        self.blf_location = None
        # self.logger = logSaver()
    
    # def update_game_data(self,game_data):
    #     if isinstance(game_data,Command):
    #         self.ref_data.command = game_data
        
    #     elif isinstance(game_data,Stage):
    #         self.ref_data.stage = game_data
            
    #     elif isinstance(game_data,tuple):
    #         if isinstance(game_data[0],TeamInfo):
    #             self.ref_data.yellow = game_data[0]
    #             self.ref_data.blue = game_data[1]

   
    # ------ Frame management ------    
    def add_new_frame(self,frame:Frame):
        """Add a new vision frame and update version periodically."""
        self.count += 1
        if self.count >= self.update_interval:
            self._version.value +=1
            self.count = 0
        self.frame_list.append(frame)

    def get_latest_frame(self) -> Frame:
        """Return the most recent vision frame."""
        return self.frame_list.latest
    
    def get_last_n_frames(self, n:int):
        """Return the last n frames for temporal analysis."""
        return self.frame_list.get_last_n_frames(n)

    # ------ Geometry ------
    def update_geometry(self,geometry:GeometryData):
        self.geometry = geometry
        self.field = geometry.field
        self.ball_model = geometry.models

    # ------ Game Controller Updates ------
    def update_gc_data(self,packet):
        """
        Apply game controller updates based on packet type.

        Supported packet types:
            - PacketType.ROBOTS_ACTIVE
            - PacketType.NEW_STATE
            - PacketType.SWITCH_TEAM
            - PacketType.BLF_LOCATION
        """
        type, data = packet[0],packet[1]
        match type:
            case PacketType.ROBOTS_ACTIVE:
                self.update_robots_active(data)
            case PacketType.NEW_STATE:
                self.update_state(data)
            case PacketType.SWITCH_TEAM :
                self.update_team(data["YELLOW"],data["POSITIVE"])
            case PacketType.BLF_LOCATION:
                self.update_ball_left_field_location(data)
            
            case _: # if the packet type is unknown 
                log.exception(f"undefined {type=}, {data=}")
            
    def update_robots_active(self, new_active:int): 
        """Update the number of active robots on the field."""
        self.robot_active = new_active
    
    def update_state(self,new_state):
        """Update current game state."""
        self._state = new_state 

    def update_team(self, us_yellow:bool, us_positive:bool):
        """Update team assignment and coordinate polarity."""
        self._us_yellow = us_yellow
        self._us_positive = us_positive
    
    def update_ball_left_field_location(self,location):
        """Store the last ball-left-field location."""
        self.blf_location = location
    
    def get_ball_left_field_location(self):
        return self.blf_location
    
    def get_current_state(self):
        return self._state
    
    def us_yellow(self):
        return self._us_yellow 
    
    def us_positive(self):
        return self._us_positive
    
    # ------ Robot Queries ------    
    def get_all_in_team(self, isYellow:bool, exclude:list[int]=None):
        """Return all robots in a team, optionally excluding specific IDs."""
        frame = self.frame_list.latest
        team = frame.robots_yellow if isYellow else frame.robots_blue
        if exclude:
            return {k: v for k, v in team.items() if k not in exclude}
        return team
        
    
    def get_yellow_robots(self, isYellow, robot_id=None):
        """Return yellow or blue robots, optionally a specific robot by ID."""
        if isYellow is True:
            if isinstance(robot_id,int):
                return self.frame_list.latest.robots_yellow[robot_id]
            return self.frame_list.latest.robots_yellow
        elif isYellow is False:
            if isinstance(robot_id,int):
                return self.frame_list.latest.robots_blue[robot_id]
            return self.frame_list.latest.robots_blue
        
    def get_our_robots(self, us=True, robot_id=None):
        """Return our team robots based on `us_yellow` setting."""
        frame = self.frame_list.latest
        # use is_yellow value as us_yellow if us== True, otherwise, the opposite i.e. not(us_yellow)
        is_yellow = self._us_yellow if us else not(self._us_yellow)
        # get list of robots base on team color
        robots = frame.robots_yellow if is_yellow else frame.robots_blue
        # returns a robot if a valid id is given, otherwise, returns list of robot
        return robots[robot_id] if isinstance(robot_id, int) else robots
    
    def get_active_robots(self):
        return self.robot_active
    
    def get_version(self):
        """Return the current version of the world model."""
        return self._version.value
    