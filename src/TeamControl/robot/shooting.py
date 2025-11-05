import math


class RobotShooting:

    @classmethod
    def find_shooting_location(cls, ball_pos):
        # We assume we are in division B
        goalpost = (4300, 0)

        x2, y2 = goalpost
        x1, y1 = ball_pos

        # Find the angle between the ball and the goalpost
        angle_ball_goal = cls.calculate_angle(ball_pos, goalpost)

        # we want to find a shooting position for the agent so that it is on the same line
        # of the ball - goalpost line and also has a distance of 200mm from the
        # ball.
        # the angle between this shooting position of the robot and the ball
        # has the same angle with the angle_ball_goal. Thus we use cosine to find
        # the x value of the shooting position of the robot
        x_distance = math.cos(angle_ball_goal) * 200
        shoot_pos_x = x1 - x_distance

        # x2 and x1 will never have the same value in our experiments
        # so we don't need to care for the case where x2 - x1 = 0
        lamda = (y2 - y1) / (x2 - x1)

        # line interpolation: line is y - y1 = lamda * (x - x1) between goal, ball and robot.
        # Get an interpolated point on the line that is on the left side of the
        # ball
        shoot_pos_y = y1 + lamda * (shoot_pos_x - x1)

        return shoot_pos_x, shoot_pos_y


    @classmethod
    def calculate_angle(cls, loc1, loc2):
        x2, y2 = loc2
        x1, y1 = loc1
        angle = math.atan2(y2 - y1, x2 - x1)

        return angle

    @classmethod
    def find_shooting_angle(cls, robot_pos, ball_pos):
        x, y, w = robot_pos
        robot_pos_xy = (x, y)
        phi = cls.calculate_angle(robot_pos_xy, ball_pos)
        return phi
