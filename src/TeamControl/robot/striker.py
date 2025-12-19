# import time
# import math

# from TeamControl.network.robot_command import RobotCommand
# from TeamControl.world.model import WorldModel
# from TeamControl.world.transform_cords import world2robot
# from TeamControl.robot.Movement import RobotMovement

# ROBOT_OFFSET = 500.0
# STOP_THRESH = 140.0          # stop when within this distance of behind_pt
# ORBIT_ENTER_DIST = 550.0     # when close to ball, use orbit to get behind
# GOAL_TURN_ONLY_TOL = 0.45
# MAX_W = 2.0
# FALLBACK_FIELD_LEN = 9000.0


# def _clamp(x, lo, hi):
#     return max(lo, min(hi, x))


# def _dist(a, b):
#     return math.hypot(a[0] - b[0], a[1] - b[1])


# def _is_behind_ball(robot_xy, ball_xy, goal_xy) -> bool:
#     bgx = goal_xy[0] - ball_xy[0]
#     bgy = goal_xy[1] - ball_xy[1]
#     brx = robot_xy[0] - ball_xy[0]
#     bry = robot_xy[1] - ball_xy[1]
#     return (bgx * brx + bgy * bry) < 0.0


# def run_go_behind_ball(dispatch_q, wm: WorldModel, robot_id=0, is_yellow=True):
#     while True:
#         frame = wm.get_latest_frame()
#         if frame is None or frame.ball is None:
#             time.sleep(0.02)
#             continue

#         ball_pos = (float(frame.ball.x), float(frame.ball.y))

#         try:
#             robot = frame.get_yellow_robots(isYellow=is_yellow, robot_id=robot_id)
#         except Exception:
#             robot = None

#         if robot is None or robot.position is None:
#             time.sleep(0.02)
#             continue

#         rx, ry, rtheta = float(robot.position[0]), float(robot.position[1]), float(robot.position[2])
#         robot_pos = (rx, ry, rtheta)
#         robot_xy = (rx, ry)

#         # opponent goal
#         try:
#             us_positive = wm.us_positive()
#         except Exception:
#             us_positive = True
#         #getting goal center to find goal shooting position.
#         field_len = FALLBACK_FIELD_LEN
#         if getattr(wm, "field", None):
#             field_len = float(wm.field.field_length)

#         our_goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
#         goal_pos = (-our_goal_x, 0.0)

#         # compute behind point every tick
#         behind_pt = RobotMovement.behind_ball_point(ball_pos, goal_pos, ROBOT_OFFSET)

#         # robot-frame angles for control
#         goal_rel = world2robot(robot_pos, goal_pos)
#         ball_rel = world2robot(robot_pos, ball_pos)
#         angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

#         dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
#         dist_to_behind = _dist(robot_xy, behind_pt)
#         behind_ok = _is_behind_ball(robot_xy, ball_pos, goal_pos)

#         vx, vy, w = 0.0, 0.0, 0.0

#         # --- Orbit if we're close to ball but not behind yet (prevents oscillation) ---
#         if (dist_to_ball < ORBIT_ENTER_DIST) and (not behind_ok):
#             orbit_dir = 1.0 if ball_rel[1] > 0 else -1.0
#             vx = 0.20
#             vy = 0.85 * orbit_dir
#             w = _clamp(1.8 * angle_to_goal, -MAX_W, MAX_W)

#         # --- Otherwise, go to the behind point while facing goal ---
#         elif dist_to_behind > STOP_THRESH:
#             vx, vy, w = RobotMovement.velocity_to_target(
#                 robot_pos,
#                 behind_pt,
#                 turning_target=goal_pos,
#                 stop_threshold=STOP_THRESH,
#                 speed=1.2,
#             )

#             # if facing is very bad, rotate more and slow translation
#             if abs(angle_to_goal) > GOAL_TURN_ONLY_TOL:
#                 vx *= 0.3
#                 vy *= 0.3
#                 w = _clamp(2.0 * angle_to_goal, -MAX_W, MAX_W)

#         # --- Arrived behind point: stop, keep facing goal ---
#         else:
#             vx, vy = 0.0, 0.0
#             w = _clamp(1.2 * angle_to_goal, -MAX_W, MAX_W)

#         cmd = RobotCommand(
#             robot_id=robot_id,
#             vx=vx,
#             vy=vy,
#             w=_clamp(w, -MAX_W, MAX_W),
#             kick=0,
#             dribble=0,
#         )
#         dispatch_q.put((cmd, 0.1))
#         time.sleep(0.02)


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
        frame = wm.get_latest_frame()
        if frame is None or frame.ball is None:
            time.sleep(0.02)
            continue

        ball_pos = (float(frame.ball.x), float(frame.ball.y))

        try:
            robot = frame.get_yellow_robots(isYellow=is_yellow, robot_id=robot_id)
        except Exception:
            robot = None

        if robot is None or robot.position is None:
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
        ball_rel = world2robot(robot_pos, ball_pos)
        goal_rel = world2robot(robot_pos, goal_pos)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_ball = math.atan2(ball_rel[1], ball_rel[0])
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
            vx = 0.8
            w = clamp(2.0 * angle_to_ball, -MAX_W, MAX_W)

        # =========================
        # 2) CAPTURE / DRIBBLE
        # =========================
        else:
            # keep ball centered first
            if not ball_centered:
                vx = 0.3
                w = clamp(2.2 * angle_to_ball, -MAX_W, MAX_W)

            # face goal
            else:
                if abs(angle_to_goal) > GOAL_ALIGN_TOL:
                    vx = 0.0
                    w = clamp(2.0 * angle_to_goal, -MAX_W, MAX_W)
                else:
                    vx = 0.4
                    w = clamp(1.2 * angle_to_goal, -MAX_W, MAX_W)

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
            vy=0.0,
            w=clamp(w, -MAX_W, MAX_W),
            kick=kick,
            dribble=dribble,
        )

        dispatch_q.put((cmd, 0.1))
        time.sleep(0.02)
