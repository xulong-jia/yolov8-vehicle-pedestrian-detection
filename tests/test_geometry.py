import pytest

from src.analytics.geometry import (
    bbox_bottom_center,
    bbox_center,
    bbox_size_and_area,
    crossed_line,
    crossing_direction,
    euclidean_distance,
    point_in_polygon,
    polygon_area,
    side_of_line,
)


def test_bbox_center_returns_midpoint():
    assert bbox_center(0, 0, 10, 20) == (5, 10)


def test_bbox_bottom_center_returns_bottom_midpoint():
    assert bbox_bottom_center(0, 0, 10, 20) == (5, 20)


def test_bbox_size_and_area_returns_width_height_area():
    assert bbox_size_and_area(0, 0, 10, 20) == (10, 20, 200)


@pytest.mark.parametrize(
    "bbox",
    [
        (10, 0, 0, 20),
        (0, 20, 10, 0),
    ],
)
def test_bbox_size_and_area_rejects_invalid_bbox(bbox):
    with pytest.raises(ValueError):
        bbox_size_and_area(*bbox)


def test_side_of_line_classifies_points_around_horizontal_line():
    line_start = (0, 0)
    line_end = (10, 0)

    upper_side = side_of_line((5, 5), line_start, line_end)
    lower_side = side_of_line((5, -5), line_start, line_end)
    on_line = side_of_line((5, 0), line_start, line_end)

    assert upper_side in {-1, 1}
    assert lower_side == -upper_side
    assert on_line == 0


def test_crossed_line_detects_strict_side_change():
    assert crossed_line((5, -1), (5, 1), (0, 0), (10, 0))


def test_crossed_line_rejects_same_side_motion():
    assert not crossed_line((5, 1), (5, 2), (0, 0), (10, 0))


def test_crossed_line_rejects_short_displacement():
    assert not crossed_line(
        (5, -0.2),
        (5, 0.2),
        (0, 0),
        (10, 0),
        min_displacement_px=1.0,
    )


def test_crossing_direction_is_consistent_for_reverse_crossings():
    line_start = (0, 0)
    line_end = (10, 0)

    forward = crossing_direction(
        (5, -1),
        (5, 1),
        line_start,
        line_end,
        positive_label="positive",
        negative_label="negative",
    )
    reverse = crossing_direction(
        (5, 1),
        (5, -1),
        line_start,
        line_end,
        positive_label="positive",
        negative_label="negative",
    )

    assert {forward, reverse} == {"positive", "negative"}


def test_crossing_direction_returns_none_without_crossing():
    assert crossing_direction((5, 1), (5, 2), (0, 0), (10, 0)) is None


def test_point_in_polygon_handles_inside_outside_and_boundary_modes():
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]

    assert point_in_polygon((5, 5), square)
    assert not point_in_polygon((15, 5), square)
    assert point_in_polygon((0, 5), square, include_boundary=True)
    assert not point_in_polygon((0, 5), square, include_boundary=False)


def test_polygon_area_returns_absolute_area_for_both_vertex_orders():
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]

    assert polygon_area(square) == 100
    assert polygon_area(list(reversed(square))) == 100


def test_polygon_area_rejects_too_few_points():
    with pytest.raises(ValueError):
        polygon_area([(0, 0), (1, 1)])


def test_euclidean_distance_returns_pythagorean_distance():
    assert euclidean_distance((0, 0), (3, 4)) == 5
