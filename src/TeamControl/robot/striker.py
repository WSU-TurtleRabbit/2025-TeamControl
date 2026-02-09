import time
import math

from TeamControl.network.robot_command import RobotCommand
from TeamControl.world.model import WorldModel
from TeamControl.world.transform_cords import world2robot

# =========================
# Tunables
# =========================
CAPTURE_DISTANCE = 200.0
KICK_DISTANCE = 140.0

BALL_CENTER_TOL = 0.20        # rad
GOAL_ALIGN_TOL = 0.20         # rad
BALL_FRONT_MIN = 30.0         # mm

DRIBBLE_ON = 1
KICK_PULSE = 0.12
KICK_COOLDOWN = 0.4

MAX_W = 2.0
FALLBACK_FIELD_LEN = 9000.0

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def run_simple_striker(dispatch_q, wm: WorldModel, robot_id=0, is_yellow=True):
    last_kick_time = 0.0
    kick_until = 0.0

    while True:
        # 23.01.2026
        # robot.position and other robot-ball observations are not updating...
        # hence angle_to_ball is constant and robot spins in place
        # ideally the angle should update as the robot moves

        # fix to the above ^ make sure to go ipconfig.yaml and set use_grSim_vision to true

        # commented out angular velocity

        # time.sleep(0.5)
        frame = wm.get_latest_frame()
        if frame is None or frame.ball is None :
            time.sleep(0.02)
            continue

        ball_pos = (float(frame.ball.x), float(frame.ball.y))

        try:
            robot = frame.get_yellow_robots(isYellow=is_yellow, robot_id=robot_id)
            # position = robot.position        
        except Exception:
            robot = None

        if isinstance(robot,int) or robot.position is None:
            time.sleep(0.02)
            continue

        rx, ry, rtheta = robot.position
        robot_pos = (float(rx), float(ry), float(rtheta))

        # -------- opponent goal --------
        try:
            us_positive = wm.us_positive()
        except Exception:
            us_positive = True

        field_len = FALLBACK_FIELD_LEN
        if getattr(wm, "field", None):
            field_len = float(wm.field.field_length)

        our_goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
        goal_pos = (-our_goal_x, 0.0)

        # -------- robot-frame observations --------
        # print("\n\nRobot position = ", robot.position)
        ball_rel = world2robot(robot_pos, ball_pos)
        goal_rel = world2robot(robot_pos, goal_pos)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_ball = math.atan2(ball_rel[1], ball_rel[0])
        # print("ball_rel[0]: ", ball_rel[0], "\tball_rel[1]: ", ball_rel[1])
        angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

        ball_centered = abs(angle_to_ball) < BALL_CENTER_TOL
        ball_in_front = ball_rel[0] > BALL_FRONT_MIN

        vx, vy, w = 0.0, 0.0, 0.0
        dribble = DRIBBLE_ON
        kick = 0

        now = time.time()

        # =========================
        # 1) GO TO BALL
        # =========================
        if dist_to_ball > CAPTURE_DISTANCE:
            # time.sleep(0.02)
            # DEBUG
            # print("Going to ball...")
            # print("[ANGLE TO BALL] Angle to ball: ", angle_to_ball)
            vx = 0.8
            mult = 2.0
            # for multiplier in range(1, 3):
                # if abs(angle_to_ball) < math.pi / 2:
                    #mult = multiplier
            w = clamp(mult * angle_to_ball, -MAX_W, MAX_W)
            # print("[ANGULAR VELOCITY] W = ", w)

        # =========================
        # 2) CAPTURE / DRIBBLE
        # =========================
        else:
            # DEBUG
            print("Capturing ball...")
            # keep ball centered first
            if not ball_centered:
                vx = 0.3
                # w = clamp(2.2 * angle_to_ball, -MAX_W, MAX_W)

            # face goal
            else:
                if abs(angle_to_goal) > GOAL_ALIGN_TOL:
                    vx = 0.0
                    # w = clamp(2.0 * angle_to_goal, -MAX_W, MAX_W)
                else:
                    vx = 0.4
                    # w = clamp(1.2 * angle_to_goal, -MAX_W, MAX_W)

            # =========================
            # 3) KICK
            # =========================
            if (
                dist_to_ball < KICK_DISTANCE
                and ball_in_front
                and abs(angle_to_goal) < GOAL_ALIGN_TOL
            ):
                if (now - last_kick_time) > KICK_COOLDOWN:
                    kick_until = now + KICK_PULSE
                    last_kick_time = now

        kick = 1 if time.time() < kick_until else 0
        if kick:
            dribble = 0

        cmd = RobotCommand(
            robot_id=robot_id,
            vx=vx,
            vy=vy,
            w=clamp(w, -MAX_W, MAX_W),
            kick=kick,
            dribble=dribble,
        )

        dispatch_q.put((cmd, 0.1))
        # time.sleep(0.02)
