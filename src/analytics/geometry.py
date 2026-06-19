"""Pure Python geometry helpers for video analytics contracts."""

from __future__ import annotations

from math import sqrt
from typing import Sequence


Point = tuple[float, float]
Polygon = Sequence[Point]


def bbox_center(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
) -> Point:
    _validate_bbox(xmin, ymin, xmax, ymax)
    return ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0)


def bbox_bottom_center(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
) -> Point:
    _validate_bbox(xmin, ymin, xmax, ymax)
    return ((xmin + xmax) / 2.0, ymax)


def bbox_size_and_area(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
) -> tuple[float, float, float]:
    _validate_bbox(xmin, ymin, xmax, ymax)
    width = xmax - xmin
    height = ymax - ymin
    return (width, height, width * height)


def side_of_line(
    point: Point,
    line_start: Point,
    line_end: Point,
    epsilon: float = 1e-9,
) -> int:
    _validate_line(line_start, line_end)
    ax, ay = line_start
    bx, by = line_end
    px, py = point
    cross_product = (bx - ax) * (py - ay) - (by - ay) * (px - ax)

    if cross_product > epsilon:
        return 1
    if cross_product < -epsilon:
        return -1
    return 0


def crossed_line(
    prev_point: Point,
    curr_point: Point,
    line_start: Point,
    line_end: Point,
    min_displacement_px: float = 0.0,
    epsilon: float = 1e-9,
) -> bool:
    if euclidean_distance(prev_point, curr_point) < min_displacement_px:
        return False

    prev_side = side_of_line(prev_point, line_start, line_end, epsilon)
    curr_side = side_of_line(curr_point, line_start, line_end, epsilon)

    if prev_side == 0 or curr_side == 0:
        return False

    return prev_side != curr_side


def crossing_direction(
    prev_point: Point,
    curr_point: Point,
    line_start: Point,
    line_end: Point,
    positive_label: str = "positive",
    negative_label: str = "negative",
    min_displacement_px: float = 0.0,
    epsilon: float = 1e-9,
) -> str | None:
    if not crossed_line(
        prev_point,
        curr_point,
        line_start,
        line_end,
        min_displacement_px,
        epsilon,
    ):
        return None

    prev_side = side_of_line(prev_point, line_start, line_end, epsilon)
    curr_side = side_of_line(curr_point, line_start, line_end, epsilon)

    if prev_side < curr_side:
        return positive_label
    if prev_side > curr_side:
        return negative_label
    return None


def point_in_polygon(
    point: Point,
    polygon: Polygon,
    include_boundary: bool = True,
) -> bool:
    _validate_polygon(polygon)

    if _point_on_polygon_boundary(point, polygon):
        return include_boundary

    x, y = point
    inside = False
    vertex_count = len(polygon)

    for index in range(vertex_count):
        x1, y1 = polygon[index]
        x2, y2 = polygon[(index + 1) % vertex_count]

        crosses_ray = (y1 > y) != (y2 > y)
        if not crosses_ray:
            continue

        x_intersection = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
        if x_intersection > x:
            inside = not inside

    return inside


def polygon_area(polygon: Polygon) -> float:
    _validate_polygon(polygon)
    area_twice = 0.0

    for index, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(index + 1) % len(polygon)]
        area_twice += x1 * y2 - x2 * y1

    return abs(area_twice) / 2.0


def euclidean_distance(p1: Point, p2: Point) -> float:
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def _validate_bbox(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
) -> None:
    if xmax < xmin:
        raise ValueError("xmax must be greater than or equal to xmin")
    if ymax < ymin:
        raise ValueError("ymax must be greater than or equal to ymin")


def _validate_line(line_start: Point, line_end: Point) -> None:
    if line_start == line_end:
        raise ValueError("line_start and line_end must be different points")


def _validate_polygon(polygon: Polygon) -> None:
    if len(polygon) < 3:
        raise ValueError("polygon must contain at least 3 points")


def _point_on_polygon_boundary(point: Point, polygon: Polygon) -> bool:
    for index in range(len(polygon)):
        if _point_on_segment(point, polygon[index], polygon[(index + 1) % len(polygon)]):
            return True
    return False


def _point_on_segment(
    point: Point,
    segment_start: Point,
    segment_end: Point,
    epsilon: float = 1e-9,
) -> bool:
    px, py = point
    x1, y1 = segment_start
    x2, y2 = segment_end

    cross_product = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    if abs(cross_product) > epsilon:
        return False

    return (
        min(x1, x2) - epsilon <= px <= max(x1, x2) + epsilon
        and min(y1, y2) - epsilon <= py <= max(y1, y2) + epsilon
    )
