#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  2 18:27:43 2024

@author: oliver
"""
import numpy as np

class Obstacle:
    def __init__(self, point:tuple[float,float], radius: float, unum:int, isYellow:bool):
        """
        RoboCup obstacles are disks.
        
        :param point: The centre coordinate (array with x, y).
        :param radius: The radius.
        :param unum: The uniform number (object id)
        :param isYellow: bool 
        """
        self.x, self.y = point
        self.radius = radius
        self.radius2 = radius * radius
        self.id = unum
        self.isYellow = isYellow
        
    @classmethod
    def from_numpy_array(cls, points, radius, unums, isYellow):
        """
        Create a list of Obstacle objects from a NumPy array of points.
        
        :param points: NumPy array of shape (n, 2) where n is the number of points.
        :param radius: The radius for all obstacles.
        :params isYellow: bool or list of bools (if list, length must be len(unums))
        :return: List of Obstacle objects.
        """
        if isinstance(isYellow, list):
            return [cls(point, radius, unum, yellow) for point, unum, yellow in zip(points, unums, isYellow)]
        else:
            return [cls(point, radius, unum, isYellow) for point, unum in zip(points, unums)]
            

    def is_point_inside(self, point,buffer):
        """
        Check if a given point is inside the obstacle.
        
        :param point: The point to check (tuple of x, y).
        :param buffer: The buffer zone clearance.
        :return: True if the point is inside the obstacle, False otherwise.
        """
        px, py = point
        return (px - self.x) ** 2 + (py - self.y) ** 2 <= (self.radius + buffer) **2
    
    def unum(self):
        return self.id
    
    def centre(self):
        return np.array((self.x, self.y))
    
    def intersects_line(self, start, goal, buffer):
        start = np.asarray(start, dtype=float).reshape(2,)
        goal  = np.asarray(goal,  dtype=float).reshape(2,)
        c     = np.asarray(self.centre(), dtype=float).reshape(2,)

        r = float(self.radius + buffer)

        line_vec = goal - start
        line_len = float(np.linalg.norm(line_vec))

        # zero-length segment: treat as point vs circle
        if line_len < 1e-9:
            return float(np.linalg.norm(c - start)) <= r

        line_dir = line_vec / line_len

        to_centre = c - start
        proj_len = float(np.dot(to_centre, line_dir))

        if proj_len <= 0.0:
            closest_point = start
        elif proj_len >= line_len:
            closest_point = goal
        else:
            closest_point = start + proj_len * line_dir

        distance_to_centre = float(np.linalg.norm(c - closest_point))
        return distance_to_centre <= r
    
    def __repr__(self):
        return f"Obstacle(ID={self.id} ({self.x}, {self.y}), radius={self.radius})"

    
def main():
    clearance = 1
    # create some obstacle with radius 2
    obstacle = Obstacle((5, 5), 2, None, True)

    # define a lines that intersects with obstacle
    line1_start = np.array([3, 3])
    line1_end = np.array([7, 7])  
    # define another one that doesn't
    line2_start = np.array([1, 1])
    line2_end = np.array([2, 2])  
    # do the check if the lines intersect with the obstacle
    intersects_line1 = obstacle.intersects_line(line1_start, line1_end,clearance)
    intersects_line2 = obstacle.intersects_line(line2_start, line2_end,clearance)

    print(f"Line from {line1_start} to {line1_end} intersects with obstacle: {intersects_line1}")
    print(f"Line from {line2_start} to {line2_end} intersects with obstacle: {intersects_line2}")

if __name__ == "__main__":
    main()    