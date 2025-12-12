''' World Model - Central Storage and access control
- apply this in multiprocessing or equivalent 
@author - Emma

'''

from TeamControl.SSL.vision.frame_list import FrameList
from TeamControl.SSL.vision.field import GeometryData,FieldSize
from TeamControl.SSL.vision.frame import Frame
from TeamControl.SSL.game_controller.fsm import PacketType,GameState
from TeamControl.SSL.game_controller.common import Command,Stage
from TeamControl.SSL.game_controller.Message import TeamInfo


from multiprocessing import Queue,Manager
import numpy as np
import numpy.typing as npt

import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class WorldModel:
    """
    World Model aka wm
    Description : 
        ...
        
        
    """
    def __init__(self,update_interval:int=10,history:int=60, use_sim:bool=True,us_yellow=True,us_positive=True):
        mgr = Manager()
        self._us_yellow = us_yellow
        self._us_positive = us_positive
        self.count = 0
        self.update_interval:int = update_interval
        self.use_sim:bool = use_sim 
        self.frame_list:FrameList[Frame] = FrameList(history=history)
        self.geometry:GeometryData = None
        self.field:FieldSize = None
        self._version = mgr.Value('i', 0)   # int counter
        self._state = None # current state from GC
        self.robot_active = 6 # robots active
        self.blf_location = None # ball left field location
    
    def update_game_data(self,game_data):
        if isinstance(game_data,Command):
            self.ref_data.command = game_data
        
        elif isinstance(game_data,Stage):
            self.ref_data.stage = game_data
            
        elif isinstance(game_data,tuple):
            if isinstance(game_data[0],TeamInfo):
                self.ref_data.yellow = game_data[0]
                self.ref_data.blue = game_data[1]
    


    def update_team(self,us_yellow:bool,us_positive:bool):
        self.us_yellow = us_yellow
        self.us_positive = us_positive
        self.robot_active = 6 # robots active
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
    


   
    
    def add_new_frame(self,frame:Frame):
        self.count += 1
        if self.count >= self.update_interval:
            self._version.value +=1
            self.count = 0
        self.frame_list.append(frame)

    def update_geometry(self,geometry:GeometryData):
        self.geometry = geometry
        self.field = geometry.field
        self.ball_model = geometry.models

    def update_gc_data(self,packet):
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
            
    def update_robots_active(self,new_active) : 
        self.robot_active = new_active
    
    def update_state(self,new_state):
        # when we have a new incoming state, it updates this
        self._state = new_state 

        
    def update_team(self,us_yellow:bool,us_positive:bool):
        self._us_yellow = us_yellow
        self._us_positive = us_positive
    
    def update_ball_left_field_location(self,location):
        self.blf_location = location
    
    def get_ball_left_field_location(self):
        return self.blf_location
    
    def get_game_state(self):
        return self._state
    
    def us_yellow(self):
        return self._us_yellow 
    
    def us_positive(self):
        return self._us_positive
    
    #vision
    def get_latest_frame(self):
        return self.frame_list.latest
    
    def get_last_n_frames(self,n:int):
        return self.frame_list.get_last_n_frames(n)
    def get_version(self):
        return self._version.value
    
    
    # avoid using this. I realised that there's problems here
    # high level
    def get_all_in_team_except(self,us:bool,exclude:list[int]):
        # get the latest frame
        isYellow = self._us_yellow if us is True else not(self._us_yellow)
        frame = self.frame_list.latest
        # get the team
        if isYellow is True:
            team  = frame.robots_yellow
        elif isYellow is False:
            team = frame.robots_blue
        # print(team)
        # nothing is being excluded ! 
        if exclude is None or len(exclude) == 0:
            # return the team
            return team
        # now check the list of wanting to be excluded.  
        else: # returning except robot with excluded id
            for e in list(exclude):
                if e in team:
                    team.remove(e)
            return team
        
    # depeciated
    def get_yellow_robots(self,isYellow, robot_id=None) -> object | list:
        raise DeprecationWarning("use frame.get_yellow_robots() instead")
        if isYellow is True:
            if isinstance(robot_id,int):
                return self.frame_list.latest.robots_yellow[robot_id]
            return self.frame_list.latest.robots_yellow
        elif isYellow is False :
            if isinstance(robot_id,int):
                return self.frame_list.latest.robots_blue[robot_id]
            return self.frame_list.latest.robots_blue
        
    # Depeciated
    def get_our_robots(self, us=True, robot_id=None) -> object | list:
        raise DeprecationWarning("use frame.get_yellow_robots() instead")
        frame = self.frame_list.latest
        # use is_yellow value as us_yellow if us== True, otherwise, the opposite i.e. not(us_yellow)
        is_yellow = self._us_yellow if us else not(self._us_yellow)
        # get list of robots base on team color
        robots = frame.robots_yellow if is_yellow else frame.robots_blue
        # returns a robot if a valid id is given, otherwise, returns list of robot
        return robots[robot_id] if isinstance(robot_id, int) else robots

    
    
    def get_active_robots(self):
        return self.robot_active
    
# if __name__ == "__main__":
#     import time
