import math

class AvoidObstacle:

    @classmethod
    def collision_with_ball(cls, robot_pos, ball_pos, target_pos):
        """ Checks if the robot collides with the ball while moving to
                the target_pos"""

        x3, y3 = ball_pos
        x2, y2 = target_pos
        x1, y1, _ = robot_pos

        # First calculate the angle between the vector of movement of the
        # agent towards its shooting location and the vector of the line from
        # shooting location to ball_pos. if this angle is less than 90 degrees
        # then there is no collision

        # calculate a vector starting from target_pos towards the direction of
        # the agent (we dont want to use the vector from the current robot_pos
        # to the target) because when the agent reaches the target, this might
        # cause errors.
        # vx vy is the new vector that is in the same line robot_pos - target_pos
        vx, vy = x2 + (x2 - x1), y2 + (y2 - y1)
        ux, uy = x3 - x2, y3 - y2

        dot = vx * ux + vy * uy
        mag_v = math.sqrt(vx ** 2 + vy ** 2)
        mag_u = math.sqrt(ux ** 2 + uy ** 2)

        if mag_v == 0 or mag_u == 0:
            return False

        # Compute angle (in radians)
        cos_theta = dot / (mag_v * mag_u)
        # ensure that the cos is between -1 and 1
        cos_theta = max(min(cos_theta, 1), -1)
        theta = math.acos(cos_theta)

        if theta <= math.pi / 2:
            # There cannot be a collision
            return False

        # If theta is greater than 90, there might be a collision. To check it
        # out, we check the distance between the ball position and the direction
        # of the movement of the agent.
        # calculate line equation of robot_pos --- target_pos --
        # line form: Ax + By + C = 0
        A = y1 - y2
        B = x2 - x1
        C = x1 * y2 - x2 * y1

        # Calculate the shortest distance from ball (x,y) with the formula
        # dist =  Ax + By + C / sqrt(A^2 + B^2)
        numerator = abs(A * x3 + B * y3 + C)
        denominator = math.sqrt(A ** 2 + B ** 2)
        distance = numerator / denominator
        robot_radius = 90
        return distance < robot_radius

    @classmethod
    def avoid_collision_with_ball(cls, robot_pos, ball_pos, target_pos):
        """ It diverges the target location of the agent to avoid collision """
        if cls.collision_with_ball(robot_pos, ball_pos, target_pos):
            target_pos = cls.avoid_ball(robot_pos, ball_pos, target_pos)
        return target_pos

    @classmethod
    def avoid_ball(cls, robot_pos, ball_pos, target_pos):
        # find the vector that goes away from the goal and is perpendicular
        # to the line robot_pos --- target_pos.
        vec = cls.unit_vector_opposite_to_ball_pos(robot_pos, ball_pos, target_pos)
        # multiply with coefficient 500 because the vector is too small 
        new_target_pos = target_pos[0] + 500 * vec[0], target_pos[1] + 500 * vec[1]
        return new_target_pos

    @classmethod
    def unit_vector_opposite_to_ball_pos(cls, robot_pos, ball_pos, target_pos):
        x1, y1, _ = robot_pos
        x2, y2 = target_pos
        xp, yp = ball_pos

        # line robot_pos --- target_pos
        dx, dy = x2 - x1, y2 - y1

        # Right-angle unit normal
        nx, ny = -dy, dx
        mag = math.hypot(nx, ny)
        nx, ny = nx / mag, ny / mag  # normalize

        # Vector from line to ball
        vx, vy = xp - x1, yp - y1

        # Check orientation using dot product
        dot = vx * nx + vy * ny

        # If it points toward the point, flip it
        if dot > 0:
            nx, ny = -nx, -ny

        return nx, ny