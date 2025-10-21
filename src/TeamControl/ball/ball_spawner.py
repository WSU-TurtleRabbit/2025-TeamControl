"""
Ball spawning logic for grSim sandbox process.
"""

import random
from TeamControl.ball.send_ball_grsim import send_ball_to_grsim
from TeamControl.network.ssl_sockets import grSimSender


class BallSpawner:
    """
    BallSpawner handles spawning balls for a grSim sandbox simulation.

    It can spawn balls either towards the goal or at random locations within
    the field. Velocities, field size, and goal parameters depend on the chosen
    division ('A' or 'B').

    Parameters
    ----------
    division : str
        Field division, either 'A' or 'B'. Determines field size and goal width.
    ball_speed : float
        Base velocity magnitude for spawned balls in m/s.
    goal_probability : float
        Probability [0,1] that the next spawned ball goes towards the goal
        instead of a random target.

    Attributes
    ----------
    field_x_min, field_x_max : float
        Minimum and maximum X coordinates of the field (in mm).
    field_y_min, field_y_max : float
        Minimum and maximum Y coordinates of the field (in mm).
    goal_line_x : float
        X position of the goal line (in mm).
    goal_width : float
        Width of the goal (in mm).
    """

    def __init__(self, division='B', ball_speed=5.0, goal_probability=0.5,
                 seed=None):
        self.division = division
        self.ball_speed = ball_speed
        self.goal_probability = goal_probability
        if seed is None:
            seed = random.randrange(0, 10000)

        self.random_gen = random.Random(seed)

        if self.division == 'B':
            self.field_x_min, self.field_x_max = -4500, 4500
            self.field_y_min, self.field_y_max = -3000, 3000
            self.goal_line_x = 4200
            self.goal_width = 950
        elif self.division == 'A':
            self.field_x_min, self.field_x_max = -6000, 6000
            self.field_y_min, self.field_y_max = -4500, 4500
            self.goal_line_x = 5700
            self.goal_width = 1750
        else:
            raise ValueError("Division must be 'A' or 'B'")

    def spawn_next_ball(self):
        """Return (x, y, vx, vy) for the next ball."""
        if self.random_gen.random() < self.goal_probability:
            return self.shoot_at_goal()
        else:
            return self.shoot_at_random_target()

    def shoot_at_goal(self):
        """Shoot a ball toward a random point within the goal."""
        ball_x = self.random_gen.uniform(0, 1)
        ball_y = self.random_gen.uniform(-1, 1)

        target_x = self.goal_line_x
        target_y = self.random_gen.uniform(-self.goal_width / 2, self.goal_width / 2)

        ratio = (target_y - ball_y) / (target_x - ball_x)
        vx = self.ball_speed
        vy = self.ball_speed * ratio
        return ball_x, ball_y, vx, vy

    def shoot_at_random_target(self):
        """Shoot a ball toward a random point in the field."""
        ball_x = self.random_gen.uniform(0, 1)
        ball_y = self.random_gen.uniform(-1, 1)

        ratio = self.random_gen.uniform(-1, 1)
        vx = self.ball_speed
        vy = self.ball_speed * ratio
        return ball_x, ball_y, vx, vy

    def is_ball_in_field(self, pos):
        """Check if a ball is within the field boundaries."""
        x, y = pos
        return self.field_x_min <= x <= self.field_x_max and self.field_y_min <= y <= self.field_y_max

    @staticmethod
    def is_ball_idle(current, previous):
        """Return True if the ball is nearly stationary."""
        ball_x, ball_y = current
        prev_x, prev_y = previous
        if ball_x == 0:
            return False
        return abs(ball_x - prev_x) + abs(ball_y - prev_y) < 0.2
