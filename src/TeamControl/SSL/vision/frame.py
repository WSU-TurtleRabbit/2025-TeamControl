from TeamControl.SSL.vision.robots import Team,Robot
from TeamControl.SSL.vision.balls import Ball
from collections import deque

import numpy as np
import numpy.typing as npt
import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

debug = False

def debug_print(*args, **kwargs):
    if debug:
        print(*args, **kwargs)
 
class Frame():
    """
    This class contains the FrameDetection Protobuf Data
    It has the following attributes:
    
    frame_number (int) : this number of frame
    balls (list[Ball]) : a list of balls currently on the field
    robots_yellow (Team) : the Team of robots with team color : yellow
    robots_blue (Team) : the Team of robots with team color : blue
    
    Additional Attribute : 
        ball (Ball) : gets the first available ball out of self.balls
    """
    def __init__(self,frame_camera_id:int,frame_number:int, balls: list[Ball],robots_yellow:Team, robots_blue:Team, max_cameras:int) -> object:
        self._balls: list[Ball]= [] #init
        # stores a backup copy of the data combines 
        self.cameras: set[int]= set()
        self.cameras.add(frame_camera_id)
        
        self.max_cameras:int= max_cameras
        self.frame_number: int= frame_number
        self.balls= balls
        self.robots_yellow: Team= robots_yellow
        self.robots_blue: Team= robots_blue
    
    
    def __repr__(self) -> str:
        return f"{self.is_completed=}, {self.frame_number=},\n {self.balls=}, {self.robots_yellow=}\n {self.robots_blue=}"
    
    
    @classmethod
    def from_proto(cls,frame_data,max_cameras:int):
        return cls(
            frame_camera_id=frame_data.camera_id,
            frame_number=frame_data.frame_number,
            balls=frame_data.balls,
            robots_yellow=Team(frame_data.robots_yellow,team_is_yellow=True),
            robots_blue=Team(frame_data.robots_blue,team_is_yellow=False),
            max_cameras=max_cameras
        )
        
    @property
    def is_completed(self):
        ## check if it goes through all specify cameras
        return len(self.cameras) == self.max_cameras
    
    @property
    def ball(self) -> Ball: 
        # returns the first ball
        return self._balls[0] if self._balls else None
    # to see the position use : frame.ball.position
    
    @property
    def balls(self) -> list:
        return self._balls
    # if you want to count balls use len(frame.balls)
    
    @balls.setter
    def balls(self,balls_in_frame):
        # print("dealing with Ball", type(balls_in_frame))
        balls = list(balls_in_frame)
        # print("dealing with Ball", balls_in_frame)
        if len(balls) <1 : 
            # print("No Ball")
            self._balls = []
        for data in balls:
            # print("adding balls")
            new_ball = Ball(data)
            self._balls.append(new_ball)
        
    
    def update(self,new_frame_data):
        for data in new_frame_data.balls:
            self._balls.append(Ball(data))
        
        self.robots_blue.merge(Team(new_frame_data.robots_blue,team_is_yellow=False))
        self.robots_yellow.merge(Team(new_frame_data.robots_yellow,team_is_yellow=True))
        self.cameras.add(new_frame_data.camera_id)

       
    def get_all_in_team_except(self,isYellow:bool,exclude:list[int]=None):
        # get the latest frame
        # get the team
        if isYellow is True:
            team  = self.robots_yellow
        elif isYellow is False:
            team = self.robots_blue
        else:
            raise AttributeError("isYellow needs to be True / False")  # shouldn't get into here, but ok
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
        
    
    def get_yellow_robots(self,isYellow, robot_id=None):
        if isYellow is True:
            if isinstance(robot_id,int):
                return self.robots_yellow[robot_id]
            return self.robots_yellow
        elif isYellow is False :
            if isinstance(robot_id,int):
                return self.robots_blue[robot_id]
            return self.robots_blue
        