import math
from shapely.geometry import Point, Polygon

# ----------------------------------------------------
# ------------ Constants and Polygons ----------------
# ----------------------------------------------------
ROBOT_RADIUS = 85 # m
COLLISION_DISTANCE = ROBOT_RADIUS * 2 

DEFENSE_AREA_POLYGON = [
    (3500, 1000),  # top-left
    (4500, 1000),  # top-right
    (4500, -1000), # bottom-right
    (3500, -1000), # bottom-left
]

FIELD_POLYGON = Polygon([
    (-4500, -3000),  # bottom-left corner
    (-4500, 3000),   # top-left corner
    (4500, 3000),    # top-right corner
    (4500, -3000),   # bottom-right corner
])

# ----------------------------------------------------
# --------------- GEOMETRY HELPERS -------------------
# ----------------------------------------------------
def distance(p1, p2):
    """Euclidean distance between points p1 and p2."""
    print('p1', p1, 'p2', p2 )
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

# ----------------------------------------------------
# -------- STOP CONDITION CHECKING HELPERS -----------
# ----------------------------------------------------
def point_in_defense_area(agent_pos, robot_radius=ROBOT_RADIUS):
    """
    Check if the robot body (circle with radius) intersects the opponent defense area polygon.

    Args:
        agent_pos (tuple): (x, y) robot center position.
        robot_radius (float): radius of the robot.

    Returns:
        bool: True if any part of the robot is inside the defense area.
    """
    robot_circle = Point(agent_pos).buffer(robot_radius)
    defense_area_poly = Polygon(DEFENSE_AREA_POLYGON)
    return robot_circle.intersects(defense_area_poly)

def check_collisions(agent_pos, other_robot_pos):
    """
    Returns True if agent robot is touching another robot.
    Touching means distance between centers <= 2*robot radius.
    """
    for robot_position in other_robot_pos:
        if distance(agent_pos, robot_position) <= COLLISION_DISTANCE:
            return True

    return False

def check_collision(agent_pos, other_robot_pos):
    """
    Returns True if agent robot is touching another robot.
    Touching means distance between centers <= 2*robot radius.
    """
    return distance(agent_pos, other_robot_pos) <= COLLISION_DISTANCE

def has_reached_target(robot_pos, target_pos, threshold=5):
    """
    Checks if the robot is within `threshold` distance of the target position.

    Args:
        robot_pos (tuple): (x, y) current position of the robot.
        target_pos (tuple): (x, y) target position.
        threshold (float): Distance tolerance to consider as "reached". (in cm)

    Returns:
        bool: True if robot is within threshold distance of target, else False.
    """
    # TODO: Change threshold if needed
    dx = robot_pos[0] - target_pos[0]
    dy = robot_pos[1] - target_pos[1]
    dist = math.sqrt(dx * dx + dy * dy)
    return dist <= threshold

def is_in_field(position):
    """
    Check if a given (x, y) position is inside the soccer field.

    Args:
        position (tuple): (x, y) coordinates.

    Returns:
        bool: True if inside the field polygon, False otherwise.
    """
    point = Point(position)
    return FIELD_POLYGON.contains(point)

def check_stop_conditions(agent_pos, target_pos, static_robots, dynamic_robots, robot_radius, elapsed_time=0, time_limit=30):
    """
    Check all stop conditions and return (should_stop, message).

    Args:
        agent_pos (tuple): (x, y) position of the robot.
        target_pos (tuple): (x, y) target position.
        static_robots (list of tuples): List of (x, y) positions.
        dynamic_robots (list of tuples): List of (x, y) positions.
        robot_radius (float): Radius of the robot.
        elapsed_time (float): Seconds elapsed since scenario start.

    Returns:
        (bool, str): Tuple where first element is True if scenario should stop,
                     second element is a human-readable message.
    """

    if has_reached_target(agent_pos, target_pos):
        return True, f"Target reached in {elapsed_time:.2f} seconds.\n{time_limit-elapsed_time:.2f} POINTS, {agent_pos}"

    if not is_in_field(agent_pos):
        return True, "Robot left the field!\n0 POINTS"

    all_obstacles = static_robots + dynamic_robots
    if len(all_obstacles):
        if check_collisions(agent_pos, all_obstacles):
            return True, "Collision detected with another robot!\n0 POINTS"

    if point_in_defense_area(agent_pos):
        return True, "Robot entered opponent's defense area!\n0 POINTS"

    return False, ""

# ----------------------------------------------------
# --------------- STATIC OBSTACLES -------------------
# ----------------------------------------------------
def generate_static_robots():
    pass

# ----------------------------------------------------
# -------------- DYNAMIC OBSTACLES -------------------
# ----------------------------------------------------
def generate_moving_robots():
    pass