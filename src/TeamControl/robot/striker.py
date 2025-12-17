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
PUSH_VX = 1.1

# extra “must be true before kick”
BALL_FRONT_DOT_MIN = 30.0        # mm-ish in robot-forward direction (tune 10–80)
BALL_CENTER_TOL = 0.15           # radians: ball must be close to centerline
GOAL_TURN_ONLY_TOL = 0.35        # radians: if bigger than this, rotate-in-place
MAX_W = 2.0


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


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

        # ---- opponent goal (IMPORTANT) ----
        try:
            us_positive = wm.us_positive()
        except Exception:
            us_positive = True

        field_len = FALLBACK_FIELD_LEN
        if getattr(wm, "field", None):
            field_len = float(wm.field.field_length)

        # our goal sign:
        our_goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
        # opponent goal is opposite:
        opp_goal_x = -our_goal_x
        goal_pos = (opp_goal_x, 0.0)

        # robot-frame vectors
        ball_rel = world2robot(robot_pose, ball_pos)   # (x_fwd, y_left)
        goal_rel = world2robot(robot_pose, goal_pos)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_ball = math.atan2(ball_rel[1], ball_rel[0])
        angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

        # ball-in-front check (prevents “kick while ball is sideways/behind”)
        ball_in_front = ball_rel[0] > BALL_FRONT_DOT_MIN

        vx, vy, w = 0.0, 0.0, 0.0
        dribble = DRIBBLE_ON
        kick = 0

        # ---------------------------
        # 1) FAR: go behind the ball (and face goal)
        # ---------------------------
        if dist_to_ball > APPROACH_RADIUS:
            behind = RobotMovement.behind_ball_point(ball_pos, goal_pos, ROBOT_OFFSET)

            vx, vy, w = RobotMovement.velocity_to_target(
                robot_pos,
                behind,
                turning_target=goal_pos,      # face opponent goal
                stop_threshold=120.0,
            )

            # Don't slide while tuning (your planner + vy=0 is fine)
            vy = 0.0

            # If facing is way off, rotate-in-place (this fixes “drives while sideways”)
            if abs(angle_to_goal) > GOAL_TURN_ONLY_TOL:
                vx = 0.0
                w = 1.8 * math.copysign(1.0, angle_to_goal)

        # ---------------------------
        # 2) MID: capture the ball (face ball first, then goal)
        # ---------------------------
        elif dist_to_ball > CAPTURE_DISTANCE:
            # If ball isn't centered, prioritize centering ball (otherwise you “brush past” it)
            if abs(angle_to_ball) > BALL_CENTER_TOL:
                vx = 0.3
                w = 2.0 * math.copysign(1.0, angle_to_ball)
            else:
                vx, vy, w = RobotMovement.velocity_to_target(
                    robot_pos,
                    ball_pos,
                    turning_target=goal_pos,
                    stop_threshold=40.0,
                )
                vy = 0.0

        # ---------------------------
        # 3) CLOSE: align + kick
        # ---------------------------
        else:
            # Step A: ensure ball is in front + centered
            if (not ball_in_front) or (abs(angle_to_ball) > BALL_CENTER_TOL):
                vx = 0.2
                w = 2.2 * math.copysign(1.0, angle_to_ball)

            # Step B: face goal (rotate more than translate if error is large)
            elif abs(angle_to_goal) > ALIGN_TOL:
                if abs(angle_to_goal) > GOAL_TURN_ONLY_TOL:
                    vx = 0.0
                else:
                    vx = 0.15
                w = 2.0 * math.copysign(1.0, angle_to_goal)

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

        # Kick pulse + IMPORTANT: turn dribbler OFF while kicking
        kick = 1 if time.time() < kick_until else 0
        if kick:
            dribble = 0

        cmd = RobotCommand(
            robot_id=robot_id,
            vx=vx,
            vy=0.0,
            w=w,
            kick=kick,
            dribble=dribble,
        )

        dispatch_q.put((cmd, 0.1))
        time.sleep(0.02)
