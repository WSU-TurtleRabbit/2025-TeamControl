# import time
# import math

# from TeamControl.network.robot_command import RobotCommand
# from TeamControl.world.model import WorldModel
# from TeamControl.world.transform_cords import world2robot
# from TeamControl.robot.Movement import RobotMovement


# # =========================
# # Tunable constants
# # =========================
# APPROACH_RADIUS = 350.0        # mm: start caring about ball
# KICK_DISTANCE = 120.0         # mm: allow kick
# ALIGN_TOL = 0.15              # rad: facing goal tolerance
# ROBOT_OFFSET = 700.0          # mm: behind-ball distance
# FALLBACK_FIELD_LEN = 9000.0   # mm


# def run_striker(
#     dispatch_q,
#     wm: WorldModel,
#     robot_id: int = 0,
#     is_yellow: bool = True,
# ):
#     """
#     STRIKER BEHAVIOUR (simple + stable):

#     1) Go behind the ball (ball → goal line)
#     2) Dribble while approaching the ball
#     3) Stop and align to the goal
#     4) Kick

#     Dribbler is ON the entire time.
#     """

#     while True:
#         # --------------------------------------------------
#         # 1) Get latest frame
#         # --------------------------------------------------
#         frame = wm.get_latest_frame()
#         if frame is None or frame.ball is None:
#             time.sleep(0.02)
#             continue

#         # --------------------------------------------------
#         # 2) Ball position (world frame)
#         # --------------------------------------------------
#         ball_pos = (float(frame.ball.x), float(frame.ball.y))

#         # --------------------------------------------------
#         # 3) Our robot
#         # --------------------------------------------------
#         try:
#             robot = frame.get_yellow_robots(
#                 isYellow=is_yellow,
#                 robot_id=robot_id
#             )
#         except Exception:
#             robot = None

#         if robot is None or robot.position is None:
#             time.sleep(0.02)
#             continue

#         robot_pose = robot.position   # (x, y, theta)
#         robot_pos_tuple = (
#             float(robot_pose[0]),
#             float(robot_pose[1]),
#             float(robot_pose[2]),
#         )

#         # --------------------------------------------------
#         # 4) Which goal are we attacking?
#         # --------------------------------------------------
#         try:
#             us_positive = wm.us_positive()
#         except Exception:
#             us_positive = True

#         field_len = FALLBACK_FIELD_LEN
#         if getattr(wm, "field", None) is not None:
#             try:
#                 field_len = float(wm.field.field_length)
#             except Exception:
#                 pass

#         goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
#         goal_pos = (goal_x, 0.0)

#         # --------------------------------------------------
#         # 5) Ball & goal in robot frame
#         # --------------------------------------------------
#         ball_rel = world2robot(robot_pose, ball_pos)
#         goal_rel = world2robot(robot_pose, goal_pos)

#         dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
#         angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

#         # --------------------------------------------------
#         # 6) DEFAULT COMMAND VALUES
#         # --------------------------------------------------
#         vx, vy, w = 0.0, 0.0, 0.0
#         dribble = 1     # <-- DRIBBLER ON ALWAYS
#         kick = 0

#         # ==================================================
#         # STATE 1: FAR → go behind the ball
#         # ==================================================
#         if dist_to_ball > APPROACH_RADIUS:
#             behind_pos = RobotMovement.behind_ball_point(
#                 ball_pos,
#                 goal_pos,
#                 ROBOT_OFFSET
#             )

#             vx, vy, w = RobotMovement.velocity_to_target(
#                 robot_pos=robot_pos_tuple,
#                 target=behind_pos,
#                 turning_target=goal_pos,
#                 stop_threshold=120.0
#             )

#             print(f"[STRIKER] FAR → behind ball | dist={dist_to_ball:.1f}")

#         # ==================================================
#         # STATE 2: MID → go to ball while dribbling
#         # ==================================================
#         elif dist_to_ball > KICK_DISTANCE:
#             vx, vy, w = RobotMovement.velocity_to_target(
#                 robot_pos=robot_pos_tuple,
#                 target=ball_pos,
#                 turning_target=goal_pos,
#                 stop_threshold=90.0
#             )

#             print(f"[STRIKER] MID → dribbling | dist={dist_to_ball:.1f}")

#         # ==================================================
#         # STATE 3: CLOSE → align then kick
#         # ==================================================
#         else:
#             vx, vy = 0.0, 0.0

#             if abs(angle_to_goal) > ALIGN_TOL:
#                 w = 3.0 * math.copysign(1.0, angle_to_goal)
#                 kick = 0
#                 print("[STRIKER] ALIGNING TO GOAL")
#             else:
#                 w = 0.0
#                 kick = 1
#                 print("[STRIKER] KICKING")

#         # --------------------------------------------------
#         # 7) Send command
#         # --------------------------------------------------
#         cmd = RobotCommand(
#             robot_id=robot_id,
#             vx=vx,
#             vy=vy,
#             w=w,
#             kick=kick,
#             dribble=dribble,
#         )

#         dispatch_q.put((cmd, 0.1))
#         time.sleep(0.02)


######################################################################################################################################################################################
# import time
# import math

# from TeamControl.network.robot_command import RobotCommand
# from TeamControl.world.model import WorldModel
# from TeamControl.world.transform_cords import world2robot
# from TeamControl.robot.Movement import RobotMovement

# # =========================
# # Tunable constants
# # =========================
# APPROACH_RADIUS = 350.0        # mm: far zone -> go behind ball
# CAPTURE_DISTANCE = 160.0       # mm: ball is basically at dribbler
# KICK_DISTANCE = 120.0          # mm: kick allowed when very close
# ALIGN_TOL = 0.15               # rad: facing goal tolerance
# ROBOT_OFFSET = 700.0           # mm: behind-ball distance
# FALLBACK_FIELD_LEN = 9000.0    # mm

# DRIBBLE_ON = 1
# KICK_ON = 1
# KICK_COOLDOWN = 0.35           # seconds (prevents repeated kicking)
# PUSH_SPEED = 0.6               # forward speed while capturing the ball (tune 0.4–0.8)


# def run_striker(
#     dispatch_q,
#     wm: WorldModel,
#     robot_id: int = 0,
#     is_yellow: bool = True,
# ):
#     """
#     Striker:
#     1) Go behind the ball while facing goal
#     2) Drive toward ball with dribbler ON
#     3) When very close, "capture" ball (push forward gently) + align
#     4) Kick into goal (once)
#     """

#     last_kick_time = 0.0

#     while True:
#         # 1) Latest frame
#         frame = wm.get_latest_frame()
#         if frame is None or frame.ball is None:
#             time.sleep(0.02)
#             continue

#         # 2) Ball position
#         ball_pos = (float(frame.ball.x), float(frame.ball.y))

#         # 3) Robot
#         try:
#             robot = frame.get_yellow_robots(isYellow=is_yellow, robot_id=robot_id)
#         except Exception:
#             robot = None

#         if robot is None or robot.position is None:
#             time.sleep(0.02)
#             continue

#         robot_pose = robot.position
#         robot_pos_tuple = (float(robot_pose[0]), float(robot_pose[1]), float(robot_pose[2]))

#         # 4) Goal we attack
#         try:
#             us_positive = wm.us_positive()
#         except Exception:
#             us_positive = True

#         field_len = FALLBACK_FIELD_LEN
#         if getattr(wm, "field", None) is not None:
#             try:
#                 field_len = float(wm.field.field_length)
#             except Exception:
#                 pass

#         goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
#         goal_pos = (goal_x, 0.0)

#         # 5) Robot-frame measurements
#         ball_rel = world2robot(robot_pose, ball_pos)
#         goal_rel = world2robot(robot_pose, goal_pos)

#         dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
#         angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

#         # Defaults
#         vx, vy, w = 0.0, 0.0, 0.0
#         dribble = DRIBBLE_ON
#         kick = 0

#         # ==================================================
#         # STATE 1: FAR -> get behind ball (facing goal)
#         # ==================================================
#         if dist_to_ball > APPROACH_RADIUS:
#             behind_pos = RobotMovement.behind_ball_point(ball_pos, goal_pos, ROBOT_OFFSET)

#             vx, vy, w = RobotMovement.velocity_to_target(
#                 robot_pos=robot_pos_tuple,
#                 target=behind_pos,
#                 turning_target=goal_pos,
#                 stop_threshold=120.0,
#             )

#             print(f"[STRIKER] FAR: behind ball | dist={dist_to_ball:.1f}")

#         # ==================================================
#         # STATE 2: MID -> go to the ball (dribbler ON)
#         # ==================================================
#         elif dist_to_ball > CAPTURE_DISTANCE:
#             # Keep facing goal while moving to ball
#             vx, vy, w = RobotMovement.velocity_to_target(
#                 robot_pos=robot_pos_tuple,
#                 target=ball_pos,
#                 turning_target=goal_pos,
#                 stop_threshold=70.0,
#             )

#             print(f"[STRIKER] MID: approach ball | dist={dist_to_ball:.1f}")

#         # ==================================================
#         # STATE 3: CAPTURE + KICK
#         # ==================================================
#         else:
#             # We are close enough to "have" the ball.
#             # Do NOT strafe; push forward gently to keep ball in dribbler.
#             vy = 0.0

#             # Step A: align to goal (small rotation). Avoid big spins.
#             if abs(angle_to_goal) > ALIGN_TOL:
#                 vx = 0.0
#                 w = 2.0 * math.copysign(1.0, angle_to_goal)  # gentler than 3.0
#                 kick = 0
#                 print("[STRIKER] CAPTURE: aligning")

#             # Step B: once aligned, push forward a bit and then kick
#             else:
#                 w = 0.0

#                 # Push forward to ensure ball is seated in dribbler
#                 vx = PUSH_SPEED

#                 # Kick only if close enough AND cooldown passed
#                 now = time.time()
#                 if dist_to_ball < KICK_DISTANCE and (now - last_kick_time) > KICK_COOLDOWN:
#                     kick = KICK_ON
#                     last_kick_time = now
#                     print("[STRIKER] KICK!")

#                 else:
#                     kick = 0
#                     print("[STRIKER] CAPTURE: holding + pushing")

#         # 7) Send command
#         cmd = RobotCommand(
#             robot_id=robot_id,
#             vx=vx,
#             vy=vy,
#             w=w,
#             kick=kick,
#             dribble=dribble,
#         )

#         dispatch_q.put((cmd, 0.1))
#         time.sleep(0.02)
#########################################################################################################################################



import time
import math

from TeamControl.network.robot_command import RobotCommand
from TeamControl.world.model import WorldModel
from TeamControl.world.transform_cords import world2robot
from TeamControl.robot.Movement import RobotMovement

APPROACH_RADIUS = 350.0        # far: go behind ball
CAPTURE_DISTANCE = 180.0       # close: ball should be in dribbler
KICK_DISTANCE = 120.0          # kick allowed
ALIGN_TOL = 0.15               # rad
ROBOT_OFFSET = 700.0
FALLBACK_FIELD_LEN = 9000.0

DRIBBLE_ON = 1
KICK_ON = 1
KICK_COOLDOWN = 0.35           # seconds
PUSH_VX = 1.2                  # grSim: forward push while holding ball (tune 0.8–1.8)


def run_striker(dispatch_q, wm: WorldModel, robot_id: int = 0, is_yellow: bool = True):
    last_kick_time = 0.0

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
        robot_pos_tuple = (float(robot_pose[0]), float(robot_pose[1]), float(robot_pose[2]))

        # Goal we attack
        try:
            us_positive = wm.us_positive()
        except Exception:
            us_positive = True

        field_len = FALLBACK_FIELD_LEN
        if getattr(wm, "field", None) is not None:
            try:
                field_len = float(wm.field.field_length)
            except Exception:
                pass

        goal_x = (field_len / 2.0) * (1.0 if us_positive else -1.0)
        goal_pos = (goal_x, 0.0)

        # Robot-frame calculations
        ball_rel = world2robot(robot_pose, ball_pos)
        goal_rel = world2robot(robot_pose, goal_pos)

        dist_to_ball = math.hypot(ball_rel[0], ball_rel[1])
        angle_to_goal = math.atan2(goal_rel[1], goal_rel[0])

        # Defaults
        vx, vy, w = 0.0, 0.0, 0.0
        dribble = DRIBBLE_ON
        kick = 0

        # -----------------------------
        # 1) FAR: behind ball
        # -----------------------------
        if dist_to_ball > APPROACH_RADIUS:
            behind_pos = RobotMovement.behind_ball_point(ball_pos, goal_pos, ROBOT_OFFSET)
            vx, vy, w = RobotMovement.velocity_to_target(
                robot_pos=robot_pos_tuple,
                target=behind_pos,
                turning_target=goal_pos,
                stop_threshold=120.0,
            )

        # -----------------------------
        # 2) MID: go to ball (dribble on)
        # -----------------------------
        elif dist_to_ball > CAPTURE_DISTANCE:
            # MID: approach ball with dribbler ON (grSim stable)
            vx, vy, w = RobotMovement.velocity_to_target(
                robot_pos=robot_pos_tuple,
                target=ball_pos,
                turning_target=goal_pos,
                stop_threshold=40.0,   # <-- get closer before stopping
            )

            vy = 0.0   # <-- CRITICAL: no strafing while dribbling


        # -----------------------------
        # 3) CLOSE: capture + push + kick
        # -----------------------------
        else:
            # CLOSE: capture ball, align, push forward, then kick
            dribble = DRIBBLE_ON
            kick = 0
            vy = 0.0

            # ball_rel[0] > 0 means ball is in front of robot
            ball_forward = ball_rel[0]

            # 1) CAPTURE: ball not fully in dribbler yet → push gently
            if ball_forward < 80.0:
                vx = 0.6
                w = 0.0
                print("[STRIKER] CAPTURE: pushing ball into dribbler")

            # 2) ALIGN: rotate gently, no translation
            elif abs(angle_to_goal) > ALIGN_TOL:
                vx = 0.0
                w = 2.0 * math.copysign(1.0, angle_to_goal)
                print("[STRIKER] ALIGN: rotating to goal")

            # 3) PUSH + KICK
            else:
                vx = PUSH_VX
                w = 0.0

                now = time.time()
                if dist_to_ball < KICK_DISTANCE and (now - last_kick_time) > KICK_COOLDOWN:
                    kick = KICK_ON
                    last_kick_time = now
                    print("[STRIKER] KICK!")
                else:
                    print("[STRIKER] PUSH: driving forward with ball")


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
