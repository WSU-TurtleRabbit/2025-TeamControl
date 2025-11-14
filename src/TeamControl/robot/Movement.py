import math
from TeamControl.world.transform_cords import world2robot

class RobotMovement:
    """Provides basic movement control utilities for robots."""
    
    @classmethod
    def goToPoint(
        cls, 
        robot_pos: tuple[float, float, float], 
        target: tuple[float, float], 
        velocity: float = 1.0, 
    ) -> tuple[float, float]:
        """
        Calculate the velocity (vx, vy) for the robot to move towards a target point
        and stop when it reaches it.

        Args:
            robot_pos (tuple[float, float, float]): Robot's current position (x, y, theta) in world coordinates.
            target (tuple[float, float]): Target position in world coordinates.
            velocity (float, optional): Constant velocity to move towards the target. Defaults to 1.0.

        Returns:
            tuple[float, float]: Velocity components (vx, vy) in robot coordinates.
        """
        if robot_pos is None or target is None:
            return 0.0, 0.0

        # Convert target from world coordinates to robot coordinates
        target_robot_frame = world2robot(robot_pos, target)

        # Distance to target
        dx, dy = target_robot_frame
        distance = math.sqrt(dx**2 + dy**2)

        # If close enough, stop
        if distance == 0:
            return 0.0, 0.0

        # Normalize direction and scale by velocity
        vx = (dx / distance) * velocity
        vy = (dy / distance) * velocity

        return vx, vy

    @classmethod
    def moveagent(
        cls,
        robot_pos: tuple[float, float, float],
        target: tuple[float, float],
        velocity: float = 1.0,
    ) -> tuple[float, float]:
        """
        Calculate the velocity (vx, vy) for the robot to move towards a target point
        and stop when is very close to it.

        Args:
            robot_pos (tuple[float, float, float]): Robot's current position (x, y, theta) in world coordinates.
            target (tuple[float, float]): Target position in world coordinates.
            velocity (float, optional): Constant velocity to move towards the target. Defaults to 1.0.
            stop_threshold (float, optional): Distance threshold to stop near the target. Defaults to 150.

        Returns:
            tuple[float, float]: Velocity components (vx, vy) in robot coordinates.
        """
        if robot_pos is None or target is None:
            return 0.0, 0.0

        # Convert target from world coordinates to robot coordinates
        target_robot_frame = world2robot(robot_pos, target)

        # Distance to target
        dx, dy = target_robot_frame
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normalize direction and scale by velocity
        if distance > 300:
            vx = (dx / distance) * velocity
            vy = (dy / distance) * velocity

        elif 150 < distance <= 300:
            vx = (dx / distance) * (velocity / 3)
            vy = (dy / distance) * (velocity / 3)

        elif 10 < distance <= 150:
            vx = (dx / distance) * (velocity / 7)
            vy = (dy / distance) * (velocity / 7)

        elif distance <= 10:
            vx = 0
            vy = 0

        return vx, vy
