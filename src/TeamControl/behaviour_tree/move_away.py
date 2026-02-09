import numpy as np

from .velocity import go_to_target


def move_away_robot_from(robot_pos, target_pos, threshold=150):
    robot_pos = robot_pos[:2]
    direction_2d = robot_pos - target_pos
    distance = np.linalg.norm(direction_2d)
    # if it is on top of target
    if distance == 0:
        # On top of the target. Pick arbitrary direction to move away.
        unit_vec = np.array([1.0, 0.0])
        distance_to_move = threshold
    elif distance < threshold:
        unit_vec = direction_2d / distance
        distance_to_move = threshold - distance
    else:
        return robot_pos  # no need to move

    # calculate the target position for robot to get to
    target_pos = robot_pos + unit_vec * distance_to_move

    return target_pos


if __name__ == "__main__":
    robot_pos = np.array([0, 100, 0])
    target_pos = np.array([50, 100])
    new_pos = move_away_robot_from(robot_pos, target_pos, threshold=150)
    vx, vy = go_to_target(robot_pos, new_pos)
    print(new_pos, vx, vy)
