from TeamControl.network.ssl_sockets import grSimSender
from TeamControl.network.robot_command import RobotCommand 
from TeamControl.robot.Movement import RobotMovement

def sandbox_process(wm):
    sim_ip = "127.0.0.1"
    cmd_listen_port = 20011
    is_yellow = True
    robot_id = 1
    sender = grSimSender(ip=sim_ip,port=cmd_listen_port,is_yellow=is_yellow)
    
    version = 0 # vision version
    robot_pos = 0,0,0
    ball = 0,0

    #cmd = RobotCommand(robot_id=1, vx=500, vy=0, w=0, kick=0, dribble=0)
    #sender.send_command(cmd)
    #print("Test command sent")

    while True:
        # This is running
        # get_update
        if version < wm.get_version():
            version = wm.get_version()
            try:
                robot_obj = wm.get_yellow_robots(isYellow=is_yellow,robot_id=robot_id)
                robots = wm.get_yellow_robots(isYellow=is_yellow,robot_id=None)
                robot_pos = robot_obj.position
                robot_obstacle = robot_obj.obstacle
                ball = wm.get_latest_frame().ball.position
            except Exception :
                robot_pos = 0,0,0
                ball = 0,0
                
        vx, vy, w = RobotMovement.velocity_to_target(robot_pos=robot_pos, target=ball)
        
        cmd = RobotCommand(robot_id=1, vx=vx, vy=vy, w=w, kick=0, dribble=0)
        sender.send_command(cmd)