from TeamControl.voronoi_planner.planner import VoronoiPlanner
from TeamControl.world.model import WorldModel as wm

# testing go to target 
from TeamControl.robot.Movement import RobotMovement
from TeamControl.network.robot_command import RobotCommand
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.ion()

class PathPlanner():
    # values are from before.
    # CLEARANCE = 100
    # d0 = 1000
    # N = 100
    
    def __init__(self,world_model:wm,dispatcher_q,robot_id):
        self.isYellow = True
        self.robot_id = robot_id
        self.version = 0
        self.wm = world_model
        field_x, field_y = (9000,6000)
        self.p = VoronoiPlanner(xsize=field_x,ysize=field_y) #initialise planner
        self.output_q = dispatcher_q # output to behaviour tree or world model

    def check_wm_update(self):
    #get update from world model
        # updates from world model if this is active
        self.isYellow = self.wm.us_yellow() if hasattr(self.wm, "us_yellow") else self.isYellow 
        
        # frame version check. 
        new_version = self.wm.get_version() #compares version
        if self.version <= new_version:
            self.version = new_version
            self.frame = self.wm.get_latest_frame() #updates the frame
            return True
        return False
                
    def running (self):
        ## this is for multi processing usage
        robot_id = self.robot_id  # example for robot 0
        fig, ax = plt.subplots()
        ax.set_ylim(-2500, 2500)
        ax.set_xlim(-1400, 1400)
        plt.show(block=False)
        while True:
            is_updated = self.check_wm_update()
            # follow waypoints here 
            if is_updated is True and self.frame is not None:
                robot = self.frame.get_yellow_robots(isYellow=self.isYellow,robot_id=robot_id)
                target_pos = self.frame.ball.position # o1r some position
                if isinstance(robot,int) or target_pos is None:
                    continue
                # print(f"{target_pos=}")
                waypoints:list = self.pathplanning(robot_id=robot_id,target_pos=target_pos)
                # print(f"{waypoints[0]=}, {robot_pos=}, {target_pos=}")
                # keep going to point until we see clear path
                point = waypoints[0][1] if len(waypoints[0])>1 else None
                print(f" POINT ? ? {point}")
                #DEBUG
                # print("Robot pos:", robot_pos, "Next:", point)
                # if point is not None:
                ax.clear()
                ax.set_ylim(-2500, 2500)
                ax.set_xlim(-1400, 1400)

                waypoint_array = np.array(waypoints)
                if waypoint_array.size:
                    ax.scatter(waypoint_array[:,0], waypoint_array[:,1], s=0.1, c='g', alpha=0.5)

                yellow_robots = self.frame.get_yellow_robots()
                yellow_positions = np.array([[pos[0], pos[1]] for pos in (r.position for r in yellow_robots) if pos is not None])
                if yellow_positions.size:
                    ax.scatter(yellow_positions[:,0], yellow_positions[:,1], s=10, c='y', alpha=0.7)

                blue_robots = self.frame.get_yellow_robots(False)
                blue_positions = np.array([[pos[0], pos[1]] for pos in (r.position for r in blue_robots) if pos is not None])
                if blue_positions.size:
                    ax.scatter(blue_positions[:,0], blue_positions[:,1], s=10, c='b', alpha=0.7)

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.001)

                # vx,vy,w= RobotMovement.velocity_to_target(robot_pos=robot_pos,target=point,speed=1)
                # print(vx,vy)
                # command = RobotCommand(robot_id, vx, vy, 0,0,0) 
                # runtime = 1 
                # self.output_q.put((command, runtime))
                # time.sleep(0.01)
                # output to dispatcher for prototype 
                    # # assuming 0 angular velocity
                # break
                # if isinstance(waypoints, list): # if the waypoint exists
                #     # push forward waypoints to output (back to world model / behaviour tree)
                    #     self.output_q.put((robot_id,waypoints))  


    ## this is modified from the example, and I turned it into 1 robot only.
    def pathplanning(self,robot_id,target_pos):
        """
        This generates waypoints for all of our robots to target and returns as a list

        Args:
            robot_id (int): id of robot to plan for
            target_pos (tuple[float,float]): targeted location e.g. ball_pos 

        Returns:
            list: list of waypoints (for this robot_id)
        """
        path_obs = [self.frame.get_yellow_robots(isYellow=self.isYellow,robot_id=robot_id).obstacle]
        # obstacles
        our_robot_obs = [r.obstacle for r in self.frame.get_all_in_team_except(isYellow=self.isYellow, exclude=[])]
        enemy_robot_obs = [r.obstacle for r in self.frame.get_all_in_team_except(isYellow=not self.isYellow, exclude=[])]
        all_obstacles = our_robot_obs + enemy_robot_obs
        goals = [target_pos]
        print("number of Obstacles:",len(all_obstacles))

        start_time = time.time()
        
        path = self.p.do_plan(starting_obs=path_obs,ending_points=goals,all_obstacles=all_obstacles)
        print(f"100 {path=}")
        end_time = time.time()
        excution_time = end_time - start_time
        print(f"{excution_time=}")
        
        # Print graph
        self.p.plot(path_obs, goals, path)

        # print(f"{simplified_paths=}")
        return path # return all waypoints

def run_planner(world_model:wm,dispatcher_q, robot_id):
    planner = PathPlanner(world_model,dispatcher_q,robot_id)
    planner.running()