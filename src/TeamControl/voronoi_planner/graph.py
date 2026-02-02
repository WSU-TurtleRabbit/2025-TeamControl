import numpy as np
from scipy.spatial import Voronoi


def voronoi_finite_polygons_2d(vor: Voronoi, radius=None):
    """
    Reconstruct infinite Voronoi regions to finite regions.
    Returns:
        regions: list[list[int]] indices into vertices for each input point
        vertices: np.ndarray (M,2) of vertices
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = np.ptp(vor.points, axis=0).max() * 2

    # Map ridge vertices to each point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    for p1, region_index in enumerate(vor.point_region):
        vertices = vor.regions[region_index]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue

        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v1 >= 0 and v2 >= 0:
                continue
            # Compute the missing endpoint at infinity
            t = vor.points[p2] - vor.points[p1]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = (vor.points[p1] + vor.points[p2]) / 2
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v1 if v1 >= 0 else v2] + direction * radius

            new_vertices.append(far_point.tolist())
            new_region.append(len(new_vertices) - 1)

        # Order region vertices counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]

        new_regions.append(new_region)

    return new_regions, np.asarray(new_vertices)


def clip_polygon_to_box(poly, x_min, x_max, y_min, y_max):
    """
    Sutherland–Hodgman polygon clipping to axis-aligned box.
    poly: (N,2)
    """
    def clip_edge(points, inside_fn, intersect_fn):
        if len(points) == 0:
            return points
        out = []
        prev = points[-1]
        prev_in = inside_fn(prev)
        for curr in points:
            curr_in = inside_fn(curr)
            if curr_in:
                if not prev_in:
                    out.append(intersect_fn(prev, curr))
                out.append(curr)
            elif prev_in:
                out.append(intersect_fn(prev, curr))
            prev, prev_in = curr, curr_in
        return np.array(out, dtype=float)

    def intersect_vertical(p1, p2, x):
        t = (x - p1[0]) / (p2[0] - p1[0] + 1e-12)
        return np.array([x, p1[1] + t * (p2[1] - p1[1])])

    def intersect_horizontal(p1, p2, y):
        t = (y - p1[1]) / (p2[1] - p1[1] + 1e-12)
        return np.array([p1[0] + t * (p2[0] - p1[0]), y])

    pts = np.array(poly, dtype=float)

    # Left
    pts = clip_edge(
        pts,
        inside_fn=lambda p: p[0] >= x_min,
        intersect_fn=lambda p1, p2: intersect_vertical(p1, p2, x_min),
    )
    # Right
    pts = clip_edge(
        pts,
        inside_fn=lambda p: p[0] <= x_max,
        intersect_fn=lambda p1, p2: intersect_vertical(p1, p2, x_max),
    )
    # Bottom
    pts = clip_edge(
        pts,
        inside_fn=lambda p: p[1] >= y_min,
        intersect_fn=lambda p1, p2: intersect_horizontal(p1, p2, y_min),
    )
    # Top
    pts = clip_edge(
        pts,
        inside_fn=lambda p: p[1] <= y_max,
        intersect_fn=lambda p1, p2: intersect_horizontal(p1, p2, y_max),
    )

    return pts


class ClosedVoronoi:
    """
    Build Voronoi cells where each obstacle centre has a forced, closed cell
    using helper ring sites + bounding square sites.

    Obstacles must have:
        obstacle.centre() -> np.array([x,y])
        obstacle.radius -> float
    """

    def __init__(self, width, height, threshold, ring_k=12):
        self.x_min = -width / 2
        self.x_max = +width / 2
        self.y_min = -height / 2
        self.y_max = +height / 2

        self.threshold = float(threshold)
        self.ring_k = int(ring_k)

    def _boundary_sites(self):
        # corners + midpoints (enough to bound everything)
        xm, xM, ym, yM = self.x_min, self.x_max, self.y_min, self.y_max
        cx, cy = (xm + xM) / 2, (ym + yM) / 2
        return np.array([
            [xm, ym], [xm, yM], [xM, ym], [xM, yM],
            [cx, ym], [cx, yM], [xm, cy], [xM, cy],
        ], dtype=float)

    def _ring_sites(self, c, r):
        # helper ring around obstacle centre
        angles = np.linspace(0, 2*np.pi, self.ring_k, endpoint=False)
        ring = np.stack([np.cos(angles), np.sin(angles)], axis=1)
        return c + ring * r

    def build(self, obstacles):
        """
        Returns:
            cells: dict[obstacle_index] = polygon (Nx2) closed & clipped
            vor: scipy.spatial.Voronoi (full diagram)
            adjacency: dict[point_index] -> set[neighbor_point_index]
        """
        if not obstacles:
            return {}, None, {}

        # --- assemble sites ---
        centre_sites = []
        all_sites = []

        # keep mapping: obstacle i -> site index of its centre in all_sites
        centre_site_index = {}

        for i, obs in enumerate(obstacles):
            c = np.asarray(obs.centre(), dtype=float).reshape(2)
            centre_site_index[i] = len(all_sites)
            centre_sites.append(c)
            all_sites.append(c)

            r = float(getattr(obs, "radius", 0.0)) + self.threshold
            ring = self._ring_sites(c, r)
            all_sites.extend(ring)

        # add boundary sites
        boundary = self._boundary_sites()
        all_sites.extend(boundary)

        points = np.asarray(all_sites, dtype=float)

        # --- compute Voronoi ---
        vor = Voronoi(points)

        # adjacency from ridge graph (useful for “connect with the rest”)
        adjacency = {i: set() for i in range(len(points))}
        for a, b in vor.ridge_points:
            adjacency[a].add(b)
            adjacency[b].add(a)

        # --- finite polygons + clip ---
        regions, vertices = voronoi_finite_polygons_2d(vor)

        cells = {}
        for obs_i, p_idx in centre_site_index.items():
            region = regions[p_idx]
            poly = vertices[region]
            poly = clip_polygon_to_box(poly, self.x_min, self.x_max, self.y_min, self.y_max)

            # if clipping collapses (rare), just skip
            if poly.shape[0] >= 3:
                cells[obs_i] = poly

        return cells, vor, adjacency



if __name__ == "__main__" : 
    # obstacles: list of your obstacle objects
    builder = ClosedVoronoi(width=9000, height=6000, threshold=300, ring_k=12)
    cells, vor, adj = builder.build(obstacles)

    # cells[i] is the closed polygon around obstacles[i].centre()
    poly0 = cells[0]  # Nx2 points