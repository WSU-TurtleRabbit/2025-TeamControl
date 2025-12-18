# TeamControl/robot/striker.py
import time
import math

from TeamControl.network.robot_command import RobotCommand
from TeamControl.world.model import WorldModel
from TeamControl.world.transform_cords import world2robot
from TeamControl.robot.Movement import RobotMovement

APPROACH_RADIUS = 350.0
CAPTURE_DISTANCE = 180.0
KICK_DISTANCE = 140.0
ALIGN_TOL = 0.20
ROBOT_OFFSET = 700.0
FALLBACK_FIELD_LEN = 9000.0

DRIBBLE_ON = 1
KICK_PULSE = 0.12
KICK_COOLDOWN = 0.4

# extra “must be true before kick”
BALL_FRONT_DOT_MIN = 30.0        # mm-ish in robot-forward direction (tune 10–80)
BALL_CENTER_TOL = 0.15           # radians: ball must be close to centerline
GOAL_TURN_ONLY_TOL = 0.35        # radians: if bigger than this, rotate-in-place
MAX_W = 2.0

# --- orbit / behind-ball tuning ---
ORBIT_RADIUS = 500.0          # circle around ball (tune 350–700)
BEHIND_POS_TOL = 130.0        # how close to behind point counts as behind
BEHIND_ANGLE_TOL = 0.25       # radians: how "behind" we require
HAVE_BALL_DRIVE_VX = 0.35     # forward speed while steering with ball


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _wrap_pi(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


def run_striker(dispatch_q, wm: WorldModel, robot_id=0, is_yellow=True):
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

        robot_pose = robot.position
        robot_pos = (float(robot_pose[0]), float(robot_pose[1]), float(robot_pose[2]))

        # ---- opponent goal ----
        try:
            us_positive = wm.us_positive()
        except Exception:
            us_positive = True

        field_len = FALLBACK_FIELD_LEN
        if getattr(wm, "field", None):
            field_len = float(wm.field.field_length)

        our_goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
        opp_goal_x = -our_goal_x
        goal_pos = (opp_goal_x, 0.0)

        # --- choose your shooting point ---
        # Option A: middle of field (as you described)
        shooting_point = (0.0, 0.0)

        # Option B: opponent goal center (uncomment if you prefer)
        # shooting_point = goal_pos

        # robot-frame vectors
        ball_rel = world2robot(robot_pose, ball_pos)  # (x_fwd, y_left)
        goal_rel = world2robot(robot_pose, shooting_point)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_ball = math.atan2(ball_rel[1], ball_rel[0])
        angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

        ball_in_front = ball_rel[0] > BALL_FRONT_DOT_MIN

        vx, vy, w = 0.0, 0.0, 0.0
        dribble = DRIBBLE_ON
        kick = 0

        # desired behind point on circle
        behind = RobotMovement.behind_ball_point(ball_pos, shooting_point, ORBIT_RADIUS)

        # world bearing "are we behind?"
        rx, ry, _ = robot_pos
        bx, by = ball_pos

        ball_to_shoot = (shooting_point[0] - bx, shooting_point[1] - by)
        ball_to_robot = (rx - bx, ry - by)

        ang_shoot = math.atan2(ball_to_shoot[1], ball_to_shoot[0])
        ang_robot = math.atan2(ball_to_robot[1], ball_to_robot[0])
        bearing_err = _wrap_pi(ang_robot - ang_shoot)

        dist_to_behind = math.hypot(rx - behind[0], ry - behind[1])

        # ---------------------------
        # 1) NOT CLOSE: orbit behind ball on circle, facing shooting point
        # ---------------------------
        if dist_to_ball > CAPTURE_DISTANCE:
            need_orbit = (dist_to_behind > BEHIND_POS_TOL) or (abs(bearing_err) > BEHIND_ANGLE_TOL)

            if need_orbit:
                clockwise = True if bearing_err > 0 else False

                vx, vy, w = RobotMovement.orbit_behind_ball(
                    robot_pose=robot_pose,
                    ball_pos=ball_pos,
                    face_target=shooting_point,
                    radius=ORBIT_RADIUS,
                    clockwise=clockwise,
                    v_tangent=1.0,
                    max_v=2.0,
                )

                # IMPORTANT: dribbler OFF while orbiting
                dribble = 0

            else:
                # now behind -> capture ball while facing shooting point
                vx, vy, w = RobotMovement.velocity_to_target(
                    robot_pos,
                    ball_pos,
                    turning_target=shooting_point,
                    stop_threshold=40.0,
                )
                dribble = 1

        # ---------------------------
        # 2) CLOSE: align + kick
        # ---------------------------
        else:
            # Step A: ensure ball is in front + centered
            if (not ball_in_front) or (abs(angle_to_ball) > BALL_CENTER_TOL):
                vx = 0.25
                w = 2.2 * math.copysign(1.0, angle_to_ball)

            # Step B: face goal (BUT do not spin in place while holding ball)
            elif abs(angle_to_goal) > ALIGN_TOL:
                vx = HAVE_BALL_DRIVE_VX
                w = 2.0 * angle_to_goal

            # Step C: kick (no drifting, dribbler off during kick)
            else:
                vx = 0.0
                w = 0.0

                now = time.time()
                if (now - last_kick_time) > KICK_COOLDOWN:
                    kick_until = now + KICK_PULSE
                    last_kick_time = now

        # clamp rotation
        w = _clamp(w, -MAX_W, MAX_W)

        # kick pulse + dribbler OFF while kicking
        kick = 1 if time.time() < kick_until else 0
        if kick:
            dribble = 0

        cmd = RobotCommand(
            robot_id=robot_id,
            vx=vx,
            vy=vy,
            w=w,
            kick=kick,
            dribble=dribble,
        )

        dispatch_q.put((cmd, 0.1))
        time.sleep(0.02)
