# TeamControl/robot/Movement.py
import math
from TeamControl.world.transform_cords import world2robot


class RobotMovement:
    @classmethod
    def velocity_to_target(
        cls,
        robot_pos: tuple[float, float, float],
        target: tuple[float, float],
        turning_target: tuple[float, float] | None = None,
        stop_threshold: float = 150.0,
    ) -> tuple[float, float, float]:
        """
        Move toward a world-frame target.
        Optionally rotate to face another world-frame target.
        """
        if robot_pos is None:
            return 0.0, 0.0, 0.0

        trans_target = world2robot(robot_pos, target)
        vx, vy = cls.go_To_Target(trans_target, stop_threshold=stop_threshold, speed=2.0)

        if turning_target is None:
            w = 0.0
        else:
            trans_turn = world2robot(robot_pos, turning_target)
            w = cls.turn_to_target(trans_turn, epsilon=0.15, max_speed=2.0)

        return vx, vy, w

    @staticmethod
    def behind_ball_point(
        ball: tuple[float, float],
        goal: tuple[float, float],
        buffer_radius: float,
    ):
        """
        Compute a point behind the ball on the ball→goal (ball→shooting_point) line.
        """
        bx, by = ball
        gx, gy = goal

        dx = gx - bx
        dy = gy - by
        d = math.hypot(dx, dy)

        if d == 0.0:
            return (bx, by)

        dx /= d
        dy /= d

        return (bx - dx * buffer_radius, by - dy * buffer_radius)

    @staticmethod
    def orbit_behind_ball(
        robot_pose: tuple[float, float, float],
        ball_pos: tuple[float, float],
        face_target: tuple[float, float],
        radius: float,
        clockwise: bool,
        kp_radial: float = 0.006,   # tune 0.003–0.012
        v_tangent: float = 1.0,     # tune 0.6–1.4
        max_v: float = 2.0,
    ) -> tuple[float, float, float]:
        """
        Orbit around the ball while staying approximately 'radius' away,
        and ALWAYS face 'face_target'. Returns vx, vy, w in ROBOT frame.

        - radial term: pushes robot to stay on circle
        - tangential term: moves robot around circle (CW/CCW)
        """
        rx, ry, _ = robot_pose
        bx, by = ball_pos

        # world vector from ball -> robot
        dx = rx - bx
        dy = ry - by
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            dist = 1e-6

        # unit radial (ball -> robot)
        ux = dx / dist
        uy = dy / dist

        # tangential direction (rotate radial by 90°)
        if clockwise:
            tx, ty = uy, -ux
        else:
            tx, ty = -uy, ux

        # radial error: positive if outside circle
        err = dist - radius

        # desired world velocity
        vx_w = tx * v_tangent - ux * (kp_radial * err * 1000.0)
        vy_w = ty * v_tangent - uy * (kp_radial * err * 1000.0)

        # convert that world-direction into robot frame by stepping a small point
        step_target = (rx + vx_w * 100.0, ry + vy_w * 100.0)  # 100mm step
        step_rel = world2robot(robot_pose, step_target)

        # normalize to max_v
        norm = math.hypot(step_rel[0], step_rel[1])
        if norm > 1e-6:
            vx = (step_rel[0] / norm) * max_v
            vy = (step_rel[1] / norm) * max_v
        else:
            vx, vy = 0.0, 0.0

        # face target
        face_rel = world2robot(robot_pose, face_target)
        w = RobotMovement.turn_to_target(face_rel, epsilon=0.10, max_speed=2.0)

        return vx, vy, w

    @staticmethod
    def go_To_Target(target_pos, stop_threshold=150.0, speed=2.0):
        """
        Simple proportional translation controller in robot frame.
        Returns vx, vy in robot frame.
        """
        if target_pos is None:
            return 0.0, 0.0

        dist = math.hypot(target_pos[0], target_pos[1])
        if dist <= stop_threshold:
            return 0.0, 0.0

        return (
            (target_pos[0] / dist) * speed,
            (target_pos[1] / dist) * speed,
        )

    @staticmethod
    def turn_to_target(target, epsilon=0.15, max_speed=2.0):
        """
        Rotate robot to face target (robot frame).
        Smooth proportional controller.
        """
        angle = math.atan2(target[1], target[0])

        if abs(angle) < epsilon:
            return 0.0

        w = 2.0 * angle  # proportional
        if w > max_speed:
            w = max_speed
        if w < -max_speed:
            w = -max_speed
        return w
