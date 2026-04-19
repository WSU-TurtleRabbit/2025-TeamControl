import math
from typing import Tuple, Optional

from TeamControl.world.transform_cords import world2robot


class PID:
    """
    Simple 1D PD controller (Proportional + Derivative).

    We use one instance per controlled variable:
        - x position
        - y position
        - orientation (theta)

    Why no integral (I)?
        In SSL, integral is often avoided because:
        - it can cause overshoot
        - robots need fast, reactive control (not slow accumulation)
    """

    def __init__(self, kp: float, kd: float):
        self.kp = kp  # proportional gain (how strongly we react to error)
        self.kd = kd  # derivative gain (how strongly we damp motion)
        self.prev_error = 0.0  # needed to compute derivative term

    def compute(self, error: float, dt: float) -> float:
        """
        Compute control output using PD formula:

            output = Kp * error + Kd * (d(error)/dt)

        Args:
            error: current error (distance to target in one axis)
            dt: time since last update (VERY important for stability)

        Returns:
            control output (velocity in that axis)
        """

        # Derivative term = rate of change of error
        # Prevent division by zero if dt is bad
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0

        # PD control law
        output = self.kp * error + self.kd * derivative

        # Store error for next timestep
        self.prev_error = error

        return output


class RobotMovement:
    """
    Main motion controller for the robot.

    Responsibilities:
        - Move robot toward a target (x, y)
        - Rotate robot toward a turning target (optional)
        - Output velocities (vx, vy, omega) in ROBOT FRAME

    Important:
        This class is STATEFUL because PID needs previous error.
        → You should create ONE instance per robot.
    """

    def __init__(self, kp_pos=1.0, kd_pos=0.1, kp_ang=2.0, kd_ang=0.2):
        """
        Initialize PID controllers.

        We use:
            - One PID for x-axis motion
            - One PID for y-axis motion
            - One PID for rotation

        Gains should be tuned experimentally.
        """

        # Position controllers (translation)
        self.pid_x = PID(kp_pos, kd_pos)
        self.pid_y = PID(kp_pos, kd_pos)

        # Angular controller (rotation)
        self.pid_theta = PID(kp_ang, kd_ang)

    def velocity_to_target(
        self,
        robot_pos: Tuple[float, float, float],
        target: Tuple[float, float],
        turning_target: Optional[Tuple[float, float]] = None,
        dt: float = 0.016,  # ~60Hz control loop
        max_speed: float = 2.0,
        max_omega: float = 5.0,
    ) -> Tuple[float, float, float]:
        """
        Compute velocity commands to move robot toward a target.

        Args:
            robot_pos: (x, y, orientation) in WORLD frame
            target: (x, y) target position in WORLD frame
            turning_target: optional (x, y) point to face
            dt: timestep (seconds)
            max_speed: max linear speed (safety clamp)
            max_omega: max angular speed (safety clamp)

        Returns:
            (vx, vy, omega) in ROBOT FRAME

        Why robot frame?
            SSL robots expect velocities relative to themselves:
                vx = forward/backward
                vy = left/right
        """

        if robot_pos is None or target is None:
            raise ValueError("Robot pos or Target is None")

        # =========================================================
        # 1. POSITION CONTROL (TRANSLATION)
        # =========================================================

        # Convert target from WORLD frame → ROBOT frame
        # This makes control independent of robot orientation
        rel_target = world2robot(robot_pos, target)

        # Error in robot frame
        # These are the distances we want to reduce to zero
        error_x, error_y = rel_target

        # Apply PD control independently on x and y axes
        vx = self.pid_x.compute(error_x, dt)
        vy = self.pid_y.compute(error_y, dt)

        # ---------------------------------------------------------
        # Speed limiting (VERY IMPORTANT in real robots)
        # Prevents:
        #   - unrealistic commands
        #   - instability
        #   - motor saturation
        # ---------------------------------------------------------
        speed = math.hypot(vx, vy)

        if speed > max_speed:
            scale = max_speed / speed
            vx *= scale
            vy *= scale

        # =========================================================
        # 2. ROTATION CONTROL
        # =========================================================

        if turning_target is None:
            # No orientation goal → don't rotate
            omega = 0.0
        else:
            # Convert turning target into robot frame
            rel_turn = world2robot(robot_pos, turning_target)

            # Angle error: how far we need to rotate
            # atan2 gives angle between robot's forward direction and target
            angle_error = math.atan2(rel_turn[1], rel_turn[0])

            # Apply PD control on angle
            omega = self.pid_theta.compute(angle_error, dt)

            # Clamp angular velocity for safety
            omega = max(-max_omega, min(max_omega, omega))

        # =========================================================
        # 3. OPTIONAL: DEADZONE (reduces jitter near target)
        # =========================================================
        # Small errors can cause oscillation → we ignore tiny values

        if abs(error_x) < 1.0:
            vx = 0.0
        if abs(error_y) < 1.0:
            vy = 0.0
        if turning_target is not None and abs(angle_error) < 0.01:
            omega = 0.0

        return vx, vy, omega