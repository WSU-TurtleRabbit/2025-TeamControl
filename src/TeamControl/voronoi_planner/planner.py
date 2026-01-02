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

from TeamControl.voronoi_planner.obstacle import Obstacle

THRESHOLD = 300
CLEARANCE = 100


def offset_goal_if_inside_obstacle(start, goal, obstacles, clearance, threshold=150):
    start = np.array(start)
    goal = np.array(goal)

    for obs in obstacles:
        if obs.is_point_inside(goal):
            direction = goal - start
            norm = np.linalg.norm(direction)
            if norm == 0:
                return start
            return goal - threshold * (direction / norm)
    return goal


class VoronoiPlanner:
    def __init__(self, xsize, ysize, obstacles=None):
        self.xsize = xsize//2 # vision field has both + and - 
        self.ysize = ysize//2
        self.obstacles = []
        self.radius = 75
        self.update_obstacles(obstacles)

    
    # Fixes objects being too close or overlapping
    def cluster_obstacles(self, obstacles, merge_dist=CLEARANCE * 2):
        """
        Merge obstacles that are too close (overlapping or nearly overlapping).
        Produces a single larger obstacle for each cluster.
        """
        clusters = []
        used = set()

        for i, o in enumerate(obstacles):
            if i in used:
                continue

            # start a new cluster
            cluster = [o]
            used.add(i)

            for j, o2 in enumerate(obstacles):
                if j in used:
                    continue

                d = np.linalg.norm(o.centre() - o2.centre())

                if d < merge_dist:
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
    #     self.obstacle_points = [o.centre() for o in self.obstacles]
    #     if len(self.obstacle_points) >= 4:  # Voronoi requires at least 4 points
    #         self.voronoi_diagram = Voronoi(self.obstacle_points)
    #         self.voronoi_vertices = self.voronoi_diagram.vertices
    #         self.graph = self.build_voronoi_graph()
    #     else:
    #         self.voronoi_diagram = None
    #         self.voronoi_vertices = np.empty((0, 2))
    #         self.graph = nx.Graph()

    def update_obstacles(self, obstacles):
        """
        Update the list of obstacles, cluster overlapping/close obstacles,
        and rebuild the Voronoi diagram and graph.
        """
        # Step 1: store raw obstacles
        self.obstacles = obstacles or []

        # Step 2: cluster overlapping or close obstacles
        self.obstacles = self.cluster_obstacles(self.obstacles)

        # Step 3: get obstacle centers for Voronoi seeds
        self.obstacle_points = [o.centre() for o in self.obstacles]

        # Step 4: build Voronoi diagram if we have enough points
        if len(self.obstacle_points) >= 4:
            self.voronoi_diagram = Voronoi(self.obstacle_points)
            self.voronoi_vertices = self.voronoi_diagram.vertices
            self.graph = self.build_voronoi_graph()
        else:
            # Not enough points for Voronoi, keep empty structures
            self.voronoi_diagram = None
            self.voronoi_vertices = np.empty((0, 2))
            self.graph = nx.Graph()


    def build_voronoi_graph(self):
        G = nx.Graph()
        for v1, v2 in self.voronoi_diagram.ridge_vertices:
            if v1 == -1 or v2 == -1:
                continue
            p1, p2 = self.voronoi_vertices[v1], self.voronoi_vertices[v2]
            if not self.is_in_bounds(p1) or not self.is_in_bounds(p2):
                continue
            G.add_edge(v1, v2, weight=np.linalg.norm(p1 - p2))
        return G

    def is_in_bounds(self, point):
        return 0 <= np.abs(point[0]) <= self.xsize and 0 <= np.abs(point[1]) <= self.ysize

    def find_nearest_voronoi_vertex(self, point):
        if len(self.voronoi_vertices) == 0:
            return point, -1
        distances = np.linalg.norm(self.voronoi_vertices - point, axis=1)
        index = np.argmin(distances)
        return self.voronoi_vertices[index], index

    def is_path_free(self, start, goal, clearance, exclude_unums=[]):
        for obs in self.obstacles:
            if obs.unum() in exclude_unums:
                continue
            if obs.intersects_line(start, goal, clearance):
                print(f"[DEBUG] Path blocked between {start} -> {goal} by obstacle {obs.unum()}")
                return False
        return True

    def plan(self, start, goal):
        _, s_idx = self.find_nearest_voronoi_vertex(start)
        _, g_idx = self.find_nearest_voronoi_vertex(goal)
        if s_idx == -1 or g_idx == -1:
            return []
        try:
            path_indices = nx.dijkstra_path(self.graph, s_idx, g_idx)
            return list(self.voronoi_vertices[i] for i in path_indices)
        except nx.NetworkXNoPath:
            print(f"[DEBUG] No path between {start} and {goal}")
            return []

    def simplify(self, path, clearance, exclude_unums=[]):
        if len(path) < 3:
            return path
        simplified = [path[0]]
        i = 0
        while i < len(path) - 1:
            next_i = i + 1
            for j in range(i + 2, len(path)):
                if self.is_path_free(path[i], path[j], clearance, exclude_unums):
                    next_i = j
            simplified.append(path[next_i])
            i = next_i
        return simplified

    def generate_waypoints(self, starts, goals, d0, stop_threshold=THRESHOLD):
        waypoints = []
        for start, goal in zip(starts, goals):
            exclude = [start.unum()]
            if self.is_path_free(start.centre(), goal, start.radius, exclude):
                waypoints.append([goal])
                continue

            adjusted_goal = offset_goal_if_inside_obstacle(
                start.centre(), goal, self.obstacles, start.radius, threshold=stop_threshold
            )
            path = self.plan(start.centre(), adjusted_goal)
            if path and not np.allclose(path[-1], adjusted_goal):
                path.append(adjusted_goal)
            waypoints.append(path)
        return waypoints

    def plot(self, starts, goals, waypoints):
        filename = "path"
        fig, ax = plt.subplots(figsize=(10, 10))
        if self.voronoi_diagram:
            voronoi_plot_2d(self.voronoi_diagram, ax=ax, show_vertices=False, show_points=False)

        ax.set_xlim((-self.xsize), self.xsize)
        ax.set_ylim((-self.ysize), self.ysize)

        # Obstacles
        for obs in self.obstacles:
            circle = Circle(obs.centre(), obs.radius, color='b', fill=True)
            ax.add_patch(circle)

        # Start & Goals
        print(type(starts),type(goals))
        for s, g in zip(starts, goals):
            ax.plot(s.x, s.y, 'go')
            ax.plot(g[0], g[1], 'ro')

        # Paths
        cmap = plt.colormaps['tab10']
        for i, path in enumerate(waypoints):
            if path:
                p = add_jitter(np.array([s.centre() for s in [starts[i]]] + path))
                ax.plot(p[:, 0], p[:, 1], '-', color=cmap(i % 10), linewidth=2)

        ax.set_aspect('equal')
        plt.title("Voronoi Path Planning with Obstacle Avoidance")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True)
        # plt.show()
        
        # png 
        plt.savefig(filename, dpi=50, bbox_inches='tight')  
        plt.close(fig)


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
