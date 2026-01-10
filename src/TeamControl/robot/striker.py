import time
import math

from TeamControl.network.robot_command import RobotCommand
from TeamControl.world.model import WorldModel
from TeamControl.world.transform_cords import world2robot
from TeamControl.robot.Movement import RobotMovement

APPROACH_RADIUS = 300.0       # mm
ALIGN_TOL = 0.15              # rad (~8.5°)
KICK_DISTANCE = 120.0         # mm
ROBOT_OFFSET = 700         # mm
FALLBACK_FIELD_LEN = 9000.0   # mm
buffer_radius=500.0


def run_striker(
    dispatch_q,
    wm: WorldModel,
    robot_id: int = 0,
    is_yellow: bool = True,
):
    """
    Striker behaviour:
    - Far from ball: go to a point behind the ball on ball→goal line, facing goal.
    - Close to ball: stop translating, only rotate toward goal.
    - Kick when close to ball AND aligned with goal.
    """

    while True:
        # 1) Latest frame
        try:
            frame = wm.get_latest_frame()
        except Exception as e:
            print("[STRIKER] get_latest_frame error:", e)
            time.sleep(0.02)
            continue

        if frame is None:
            # no vision yet
            time.sleep(0.02)
            continue

        # 2) Ball
        ball = frame.ball
        if ball is None:
            # no ball seen
            time.sleep(0.02)
            continue

        ball_pos = (float(ball.x), float(ball.y))

        # 3) Our robot
        try:
            robot = frame.get_yellow_robots(isYellow=is_yellow, robot_id=robot_id)
        except Exception as e:
            print("[STRIKER] get_yellow_robots error:", e)
            time.sleep(0.02)
            continue

        if robot is None or robot.position is None:
            print("[STRIKER] robot is None or has no position")
            time.sleep(0.02)
            continue

        robot_pose = robot.position
        robot_pos_tuple = (
            float(robot_pose[0]),
            float(robot_pose[1]),
            float(robot_pose[2]),
        ) #(x,y,theta)

        # 4) Which way are WE attacking?
        try:
            us_positive = wm.us_positive()
        except Exception:
            us_positive = True  # safe fallback

        # 5) Field length (via getattr so proxy doesn't explode)
        field_len = FALLBACK_FIELD_LEN
        field = getattr(wm, "field", None)
        if field is not None:
            try:
                field_len = float(field.field_length)
            except Exception:
                pass

        # Opponent goal position in world coords
        # If us_positive → we attack +x, else we attack -x
        goal_sign = 1.0 if us_positive else -1.0
        goal_pos = (goal_sign * field_len / 2.0, 0.0)

        # 6) Ball & goal in robot frame
        ball_rel = world2robot(robot_pose, ball_pos)
        goal_rel = world2robot(robot_pose, goal_pos)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

        # ==================================================
        # MODE 2: CLOSE-RANGE ALIGNMENT & SHOOT
        # ==================================================
        if dist_to_ball < APPROACH_RADIUS:
            vx = 0.0
            vy = 0.0

            if abs(angle_to_goal) > ALIGN_TOL:
                w = 3.0 * math.copysign(1.0, angle_to_goal)
            else:
                w = 0.0

            if dist_to_ball < KICK_DISTANCE and abs(angle_to_goal) < ALIGN_TOL:
                kick = 1
            else:
                kick = 0

            print(
                f"[STRIKER] CLOSE RANGE: dist={dist_to_ball:.1f}, "
                f"angle={angle_to_goal:.2f}, w={w:.2f}, kick={kick}"
            )

        # ==================================================
        # MODE 1: APPROACH BEHIND BALL
        # ==================================================
        else:
            behind_pos = RobotMovement.behind_ball_point(ball_pos, goal_pos, buffer_radius)


            vx, vy, w = RobotMovement.velocity_to_target(
                robot_pos=robot_pos_tuple,
                target=behind_pos,
                turning_target=goal_pos,
                stop_threshold=90
            )

            kick = 0

            print(
                f"[STRIKER] APPROACH: dist={dist_to_ball:.1f}, "
                f"{behind_pos=}, vx={vx:.2f}, vy={vy:.2f}, w={w:.2f}"
            )

        # 7) Send command
        cmd = RobotCommand(
            robot_id=robot_id,
            vx=vx,
            vy=vy,
            w=w,
            kick=kick,
            dribble=0,
        )

        dispatch_q.put((cmd, 0.1))
        time.sleep(0.02)
