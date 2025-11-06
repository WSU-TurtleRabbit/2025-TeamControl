"""
Idel ball spawning logic for grSim sandbox process.
"""

import random
from TeamControl.ball.send_ball_grsim import send_ball_to_grsim
from TeamControl.network.ssl_sockets import grSimSender


class BallIdleSpawner:
    test_scenarios = [(2, -0.5), (3.5, -1.5), (3.9, 1.8), (1, 0), (0.5, 0), (0.1, 0.2)]

    def __init__(self, division='B', seed=None):
        self.division = division
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

    def spawn_next_ball(self, robot_pos):
        """Return (x, y, vx, vy) for the next ball."""
        while BallIdleSpawner.test_scenarios:
            ball_pos = BallIdleSpawner.test_scenarios[0]
            ball_x = ball_pos[0]
            ball_y = ball_pos[1]
            vx = vy = 0
            BallIdleSpawner.test_scenarios.pop(0)
            return ball_x, ball_y, vx, vy

        ball_pos_max_x = 0.9 * self.field_x_max / 1000
        ball_pos_min_x = 0
        ball_pos_max_y = 0.9 * self.field_y_max / 1000
        ball_pos_min_y = 0.9 * self.field_y_min / 1000
        ball_x = self.random_gen.uniform(ball_pos_min_x, ball_pos_max_x)
        ball_y = self.random_gen.uniform(ball_pos_max_y, ball_pos_min_y)
        # Don't spawn the ball at the position of the agent
        while (robot_pos[0] - 0.09 < ball_x < robot_pos[0] + 0.09 and
               robot_pos[1] - 0.09 < ball_y < robot_pos[1] + 0.09):
            ball_x = self.random_gen.uniform(ball_pos_min_x, ball_pos_max_x)
            ball_y = self.random_gen.uniform(ball_pos_max_y, ball_pos_min_y)

        vx = 0
        vy = 0
        return ball_x, ball_y, vx, vy

    def is_ball_in_field(self, pos):
        """Check if a ball is within the field boundaries."""
        x, y = pos
        return self.field_x_min <= x <= self.field_x_max and self.field_y_min <= y <= self.field_y_max