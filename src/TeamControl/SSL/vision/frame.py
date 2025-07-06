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
        for data in balls_in_frame:
            new_ball = Ball(data)
            self._balls.append(new_ball)
        
    
    def update(self,new_frame_data):
        for data in new_frame_data.balls:
            self._balls.append(Ball(data))
        
        self.robots_blue.merge(Team(new_frame_data.robots_blue,team_is_yellow=False))
        self.robots_yellow.merge(Team(new_frame_data.robots_yellow,team_is_yellow=True))
        self.cameras.add(new_frame_data.camera_id)

       
class FrameList ():
    ### THIS IS A LIST CLASS so this would work like a list
    def __init__(self,cameras:int=1,history:int=5):
        self.newest_frame = 0
        self.cameras = cameras
        self.history = history
        self._frames = deque(maxlen=history)
        self._frame_lookup = {}  # Maps frame_id -> Frame
    
    
    def __repr__(self):
        return repr(self._frames)
    
    @property
    def is_complete(self):
        return self.latest.is_completed if isinstance(self.latest,Frame) else False
    
    @property
    def frame_ids(self) -> list[int]:
        return [f.id for f in self._frames]
    @property
    def frame_ids(self):
        return [frame.frame_number for frame in self._frames]    
    
    @property
    def latest(self) -> Frame | None:
        return self._frames[-1] if self._frames else None

    def update(self, new_detection):
        if new_detection.frame_number == self.newest_frame:
            self.latest.update(new_detection)
        elif new_detection.frame_number > self.newest_frame:
            self.newest_frame = new_detection.frame_number
            frame = Frame.from_proto(new_detection,max_cameras=self.cameras)
            self.append(frame)
    
        
    def append(self, frame: Frame):
        if frame.frame_number in self._frame_lookup:
            raise LookupError (f"{frame.frame_number} exist, use update instead")
            self.update(frame)
        # If full, remove oldest from both deque and dict
        if len(self._frames) == self.history:
            old_frame = self._frames.popleft() 
            del self._frame_lookup[old_frame.frame_number] 
        # Add new frame
        self._frames.append(frame)
        self._frame_lookup[frame.frame_number] = frame # adds to dictionary

    def get_frame_withid(self, frame_id: int) -> Frame | None:
        return self._frame_lookup.get(frame_id)

    def get_last_n_frames(self, n: int) -> list[Frame]:
        return list(self._frames)[-n:]

    
    def clear(self):
        self._frames.clear()
    
    # * index is 0-100, not frame number 
    def __getitem__(self, index):
        return self._frames[index]

    def __setitem__(self, index, value):
        self._frames[index] = value

    def __len__(self):
        return len(self._frames)

    def __iter__(self):
        return iter(self._frames)