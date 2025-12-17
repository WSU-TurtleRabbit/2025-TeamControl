import math
import numpy as np
from TeamControl.world.transform_cords import world2robot


class RobotMovement:

    @classmethod
    def velocity_to_target(
        cls,
        robot_pos: tuple[float, float, float],
        target: tuple[float, float],
        turning_target: tuple[float, float] | None = None,
        stop_threshold: float = 150.0
    ) -> tuple[float, float, float]:
        """
        Move toward a world-frame target.
        Optionally rotate to face another world-frame target.
        """

        if robot_pos is None:
            return 0.0, 0.0, 0.0

        # Convert target to robot frame
        trans_target = world2robot(robot_pos, target)
        vx, vy = cls.go_To_Target(trans_target, stop_threshold)

        # Handle rotation
        if turning_target is None:
            w = 0.0
        else:
            trans_turn = world2robot(robot_pos, turning_target)
            w = cls.turn_to_target(trans_turn)

        return vx, vy, w

    @staticmethod
    def behind_ball_point(ball, goal, buffer_radius):
        """
        Compute a point behind the ball on the ball→goal line.
        """

        bx, by = ball
        gx, gy = goal

        dx = gx - bx
        dy = gy - by
        d = math.hypot(dx, dy)

        if d == 0:
            return (bx, by)

        dx /= d
        dy /= d

        return (bx - dx * buffer_radius, by - dy * buffer_radius)

    @staticmethod
    def go_To_Target(target_pos, stop_threshold=150.0, speed=1.0):
        """
        Simple proportional translation controller in robot frame.
        """

        if target_pos is None:
            return 0.0, 0.0

        dist = math.hypot(target_pos[0], target_pos[1])
        if dist > stop_threshold:
            return (
                (target_pos[0] / dist) * speed,
                (target_pos[1] / dist) * speed
            )

        return 0.0, 0.0

    @staticmethod
    def turn_to_target(target, epsilon=0.15, speed=5.0):
        """
        Rotate robot to face target (robot frame).
        """

        angle = math.atan2(target[1], target[0])

        if abs(angle) < epsilon:
            return 0.0

        return speed * math.copysign(1.0, angle)
