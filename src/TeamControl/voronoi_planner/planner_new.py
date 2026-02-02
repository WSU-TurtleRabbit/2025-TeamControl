#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rewritten Voronoi Path Planner with Obstacle Avoidance
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.spatial import Voronoi, voronoi_plot_2d
import networkx as nx
import time
import sys

plt.ion()

from TeamControl.voronoi_planner.obstacle import Obstacle
from TeamControl.voronoi_planner.graph import ClosedVoronoi

# CLEARANCE is the width of the path taken by the robot
CLEARANCE = 1300
# additional radius to the obstacle
BUFFER_ZONE = 80
# THRESHOLD is for logical decision making (decision boundary)
THRESHOLD = CLEARANCE + BUFFER_ZONE

def offset_goal_if_inside_obstacle(start_pos:tuple[float], goal_pos:tuple[float], obstacles, threshold=THRESHOLD,buffer=BUFFER_ZONE):
    '''
    clearance not used, therefore none.
    '''
    start_pos = np.array(start_pos)
    goal_pos = np.array(goal_pos)

    for obs in obstacles:
        if obs.is_point_inside(goal_pos,buffer):
            direction = goal_pos - start_pos
            norm = np.linalg.norm(direction)
            if norm == 0:
                return start_pos
            return goal_pos - threshold * (direction / norm) # return adjusted
    return goal_pos # return original


class VoronoiPlanner:
    def __init__(self, xsize, ysize, obstacles=[]):
        self.xsize = xsize//2 # vision field has both + and - 
        self.ysize = ysize//2
        self.obstacles = obstacles
        self.plt= None
        self.builder = ClosedVoronoi(width=xsize, height=ysize, threshold=THRESHOLD, ring_k=4)
        
        
        

        fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.title("Voronoi Path Planning with Obstacle Avoidance")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True)
        plt.show(block=False)

        self.fig = fig
        self.ax = self.ax

        if len(obstacles) > 0:
            self.update_obstacles(obstacles)

    def do_plan(self,starting_obs,ending_points):
        # main sequence for pathplanner :
        # if self.graph is None or self.obstacles is None:
        #     raise AttributeError("NEED TO UPDATE OBSTACLES FIRST")
            # return
        planner_points = self.generate_waypoints(starts=starting_obs,goals=ending_points,threshold=THRESHOLD)                
        shortcuts = self.find_shortcuts(starting_obs=starting_obs,
                                        generated_waypoints=planner_points,
                                        ending_points=ending_points,
                                        clearance=THRESHOLD)
        

        return planner_points

    def find_shortcuts(self,starting_obs,generated_waypoints,ending_points,clearance,buffer=BUFFER_ZONE):
        simplified_paths = []
        for start, wp, goal in zip(starting_obs, generated_waypoints, ending_points):
            full_path = [start.centre()] + wp
            if start.isYellow is True:
                exclude_yellow = [start.unum()]
                exclude_blue = []
            else:
                exclude_blue = [start.unum()]
                exclude_yellow = []

            # simplify using proper segment collision check
            simple = self.simplify(full_path, clearance,exclude_yellow=exclude_yellow,exclude_blue=exclude_blue )
            # simple = full_path
            # keep only points that are safe (NOTE: needs clearance-aware check)
            sp = []
            for point in simple:
                if all(not obs.is_point_inside(point,buffer) for obs in self.obstacles):
                    sp.append(point)
                    # print(f"86 {sp}, {simple}")

            # goal safety check (also needs clearance-aware check)
            goal_is_safe = all(not obs.is_point_inside(goal,buffer) for obs in self.obstacles)
            if goal_is_safe:
                if (len(sp) == 0) or (not np.allclose(sp[-1], goal)):
                    sp.append(goal)
            # if goal_is_safe and not np.allclose(sp[-1], goal):
            #     sp.append(goal)

            simplified_paths.append(sp)
            print(f"87 simplified path {simplified_paths}")

        return simplified_paths
        

    
    # Fixes objects being too close or overlapping
    def cluster_obstacles(self, obstacles, clearance=CLEARANCE,exclude=[]):
        """
        Merge obstacles that are too close (overlapping or nearly overlapping).
        Produces a single larger obstacle for each cluster.
        """
            
        clusters = []
        used = set()
        radius = obstacles[0].radius

        for i, o in enumerate(obstacles):
            if i in used:
                continue

            # start a new cluster
            cluster = [o]
            used.add(i)

            for j, o2 in enumerate(obstacles):
                if j in used:
                    continue
                if o2 in exclude:
                    continue

                d = np.linalg.norm(o.centre() - o2.centre())

                if d < (radius*2 + clearance):
                    cluster.append(o2)
                    used.add(j)

            # Merge cluster into one obstacle
            centers = np.array([c.centre() for c in cluster])
            centroid = centers.mean(axis=0)

            # new radius = distance to furthest centre + obstacle radius
            max_r = max(np.linalg.norm(c.centre() - centroid) + c.radius for c in cluster)

            merged = Obstacle(centroid, max_r, cluster[0].unum(), cluster[0].isYellow)
            clusters.append(merged)

        return clusters



    # Replaced
    # def update_obstacles(self, obstacles):
    #     self.obstacles = obstacles or []
    #     self.obstacle_centres = [o.centre() for o in self.obstacles]
    #     if len(self.obstacle_centres) >= 4:  # Voronoi requires at least 4 points
    #         self.voronoi_diagram = Voronoi(self.obstacle_centres)
    #         self.voronoi_vertices = self.voronoi_diagram.vertices
    #         self.graph = self.build_voronoi_graph()
    #     else:
    #         self.voronoi_diagram = None
    #         self.voronoi_vertices = np.empty((0, 2))
    #         self.graph = nx.Graph()

    def update_obstacles(self, obstacles: list,exclude=[]):
        """
        Update the list of obstacles, cluster overlapping/close obstacles,
        and rebuild the Voronoi diagram and graph.
        """
        # Step 1: store raw obstacles
        if not isinstance(obstacles, list):
            raise TypeError("Please put list of obstacles only")
            return

        self.obstacles = obstacles

        # Step 2: cluster overlapping or close obstacles
        # self.obstacles = self.cluster_obstacles(self.obstacles,exclude=exclude)

        # Step 3: get obstacle centers for Voronoi seeds
        self.obstacle_centres = [o.centre() for o in self.obstacles]
        cells, vor, adj = self.builder.build(self.obstacles)

        # Step 4: build Voronoi diagram if we have enough points
        self.voronoi_diagram = vor
        self.voronoi_vertices = self.voronoi_diagram.vertices
        self.graph = self.build_voronoi_graph()



    def build_voronoi_graph(self):
        graph = nx.Graph()
        for v1, v2 in self.voronoi_diagram.ridge_vertices:
            if v1 == -1 or v2 == -1:
                continue
            p1, p2 = self.voronoi_vertices[v1], self.voronoi_vertices[v2]
            if not self.is_in_field(p1) or not self.is_in_field(p2):
                continue
            graph.add_edge(v1, v2)
        return graph

    def is_in_field(self, point):
        """
        if the point is within field boundaries
        """
        return 0 <= np.abs(point[0]) <= self.xsize and 0 <= np.abs(point[1]) <= self.ysize

    def find_nearest_voronoi_vertex(self, point):
        if len(self.voronoi_vertices) == 0:
            # no vertices here
            return point, -1
        distances = np.linalg.norm(self.voronoi_vertices - point, axis=1)
        index = np.argmin(distances)
        return self.voronoi_vertices[index], index

    def is_path_free(self, start, goal, clearance, exclude_yellow=[],exclude_blue=[]):
        """
        exclude : obstacle object
        """
        clearance = clearance + BUFFER_ZONE
        for obs in self.obstacles:
            if (obs.isYellow is True and obs.unum() in exclude_yellow) or (obs.isYellow is False and obs.unum() in exclude_blue):
                # print(f"skipping {obs.unum()} {obs.isYellow}")
                continue
          
            if obs.intersects_line(start, goal, clearance):
                # print(f"[DEBUG] Path blocked between {start} -> {goal} by obstacle {obs.unum()} {obs.isYellow}")
                return False
        return True

    def plan(self, start, goal):
        # make path go to the nearest vertex
        _, s_idx = self.find_nearest_voronoi_vertex(start)
        _, g_idx = self.find_nearest_voronoi_vertex(goal)

        if s_idx == -1 or g_idx == -1:
            return []
        try:
            path_indices = nx.dijkstra_path(self.graph, s_idx, g_idx)
            # for i in path_indices
            return list(self.voronoi_vertices[i] for i in path_indices)
        except nx.NetworkXNoPath:
            # print(f"[DEBUG] No path between {start} and {goal}")
            return []

    def simplify(self, path, clearance, exclude_yellow=[],exclude_blue=[]):
        """ excluded= obstacles"""
        if len(path) < 3: # already simple enough
            return path
        simplified = [path[0]]
        i = 0
        while i < len(path) - 1:
            next_i = i + 1
            for j in range(i + 2, len(path)):
                if self.is_path_free(path[i], path[j], clearance,
                                     exclude_yellow=exclude_yellow, exclude_blue=exclude_blue):
                    # print(f"258 PATH IS FREE : {path[i]=},{path[j]=},{clearance}")
                    next_i = j
                    continue
            simplified.append(path[next_i])
            # print(simplified)
            i = next_i
        return simplified

    def generate_waypoints(self, starts:list[Obstacle], goals:tuple[float], buffer=BUFFER_ZONE,threshold=THRESHOLD)-> list[float]:
        waypoints = []
        for start, goal in zip(starts, goals):
            if start.isYellow is True:
                exclude_yellow = [start.unum()]
                exclude_blue = []
            else:
                exclude_blue = [start.unum()]
                exclude_yellow = []
            
            # adjust the individual goal first 
            goal = offset_goal_if_inside_obstacle(
                start.centre(), goal, self.obstacles, start.radius+buffer 
            )
            # check if there's a direct free path
            if self.is_path_free(start.centre(), goal,THRESHOLD  ,
                                 exclude_yellow=exclude_yellow,exclude_blue=exclude_blue):
                # waypoints[start.unum()] = [goal] # dict
                # print(f"path is free 253")
                waypoints.append([goal])
                continue # done with this robot, skip
            
            # otherwise do the plan
            path = self.plan(start.centre(), goal)
            # print(f" 250 {path=}")
            if path and not np.allclose(path[-1], goal):
                path.append(goal)
            
            # saves this set of path
            waypoints.append(path)
        # print(f"{waypoints=}")
        return waypoints

    def plot(self, starts:list[Obstacle], goals:tuple[float], waypoints:list[list[float]]):
        filename = "path"
        self.ax.clear()
        if self.voronoi_diagram:
            voronoi_plot_2d(self.voronoi_diagram, ax=self.ax, show_vertices=True, show_points=True)
        self.ax.set_xlim((-self.xsize), self.xsize)
        self.ax.set_ylim((-self.ysize), self.ysize)

        # Obstacles
        for obs in self.obstacles:
            circle = Circle(obs.centre(), obs.radius, color='b', fill=True)
            self.ax.add_patch(circle)

        # Start & Goals
        
        for s, g in zip(starts, goals):
            self.ax.plot(s.x, s.y, 'go')
            self.ax.plot(g[0], g[1], 'ro')

        # Paths
        cmap = plt.colormaps['tab10']
        for i, path in enumerate(waypoints):
            # print(path)
            if path:
                p = add_jitter(np.array([s.centre() for s in [starts[i]]] + path))
                self.ax.plot(p[:, 0], p[:, 1], '-', color=cmap(i % 10), linewidth=2)

        self.ax.set_aspect('equal')


        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        


def generate_points(N, dmin, xrange, yrange, existing=[]):
    points = []
    all_points = list(existing)
    while len(points) < N:
        new = np.array([
            round(np.random.uniform(*xrange), 1),
            round(np.random.uniform(*yrange), 1)
        ])
        if all(np.linalg.norm(new - p) >= dmin for p in all_points):
            points.append(new)
            all_points.append(new)
    return np.array(points)


def add_jitter(path, amount=0.05):
    return path + np.random.uniform(-amount, amount, path.shape)



if __name__ == "__main__":
    np.random.seed(42)

    vp = VoronoiPlanner(9000, 6000)
    clearance = CLEARANCE
    d0 = 1000

    # Clear field
    # starts_np = np.array([[3500, 2500]])
    # goals = np.array([[6000, 5000]])

    # Uncomment for more robots
    # starts_np = np.array([...])
    # goals = np.array([...])

    #All starts and goals
    starts_np = np.array([
        [200, 1800], [1000, 800], [1800, 5000],
        [2500, 1000], [1000, 1500], [500, 300], [4000, 4500], [2100,3200], [7000, 5000], [500, 4500], [5000, 800], [8500, 2500]
    ])
    goals = np.array([
        [5500, 2500], [4000, 1200], [2300, 2300],
        [3000, 200], [3800, 350], [1800, 400], [6000, 1000], [3500, 3200], [6842, 3000], [2500, 5500], [7000, 5000], [7500, 1200]
    ])

    our_robots = Obstacle.from_numpy_array(
        starts_np, clearance, list(range(1, len(starts_np) + 1)), isYellow=True
    )

    opponent_np = generate_points(11, 2 * clearance, (0, 9000), (0, 6000), starts_np)
    their_robots = Obstacle.from_numpy_array(
        opponent_np, clearance, list(range(100, 111)), isYellow=False
    )

    all_obstacles = our_robots + their_robots
    vp.update_obstacles(all_obstacles)

    waypoints = vp.generate_waypoints(our_robots, goals, d0)
    simplified_paths = []
    for i, (start, wp, goal) in enumerate(zip(our_robots, waypoints, goals)):
        full_path = [start.centre()] + wp
        simple = vp.simplify(full_path, clearance, [start.unum()])
        goal_is_safe = all(
            not obs.is_point_inside(goal)
            for obs in all_obstacles
        )

        if goal_is_safe and not np.allclose(simple[-1], goal):
            simple.append(goal)

        simplified_paths.append(simple)

    vp.plot(our_robots, goals, simplified_paths)
