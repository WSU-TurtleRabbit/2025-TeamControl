import numpy as np
from numpy.linalg import inv


def transformation_matrix(p):
    """
    input:
        p: robot pose (x, y, theta)
    output:
        transformation matrix (rotation and translation)
    """
    is_grsim = True
    if is_grsim:
        angle = p[2]
    else:
        angle = p[2] - np.pi / 2
    c = np.cos(angle)
    s = np.sin(angle)

    transformation_matrix = np.array([[c, -s, p[0]], [s, c, p[1]], [0, 0, 1]])

    return transformation_matrix


def world2robot(robot_position, target_position) -> tuple[float, float]:
    """
    input:
        Target_position: position in the world coordinate system (x,y)
        robot_position: robot pose (x, y, theta)
    output:
        t: targeted position in respect to robot coordinate system (x,y)
    """
    if robot_position is None or target_position is None:
        raise ValueError(f"Value is None: {robot_position=}, {target_position=}")

    trans_matrix = inv(transformation_matrix(robot_position))
    target_position = np.append(target_position, 1)  # (x,y,1)

    t = np.dot(trans_matrix, target_position)[:2]

    return t


def robot2world(robot_pos, r_target):
    """
    input:
        r_target: position in the robot coordinate system (x,y)
        robot_pos: robot pose (x, y, theta)
    output:
        w: position in the robot coordinate system (x,y)
    """
    trans_matrix = transformation_matrix(robot_pos)
    target_pos = np.append(r_target, 1)  # (x,y,1)

    w = np.dot(trans_matrix, target_pos)[:2]

    return w


if __name__ == "__main__":
    robot_pos = [1, 2, 0]
    target_pos = np.array([5, 2])
    trans_target = world2robot(robot_pos, target_pos)
    new_tar = robot2world(robot_pos, trans_target)
    assert np.allclose(new_tar, target_pos)
    print("Transformation successful", target_pos, new_tar)
