import pytest

from src.analytics.line_counter import count_line_crossings, summarize_count_events


LINE_CONFIG = {
    "id": "line_main",
    "name": "Main Counting Line",
    "points": [[0, 0], [10, 0]],
    "directions": {"positive": "in", "negative": "out"},
    "target_classes": ["Car", "Person"],
    "enabled": True,
}


def track_row(
    track_id,
    frame_index,
    timestamp_sec,
    center_x,
    center_y,
    class_name="Car",
    class_id=1,
    state="confirmed",
    video_id="demo",
):
    return {
        "video_id": video_id,
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "track_id": track_id,
        "class_id": class_id,
        "class_name": class_name,
        "center_x": center_x,
        "center_y": center_y,
        "state": state,
    }


def test_single_track_crossing_creates_count_event():
    rows = [
        track_row(1, 0, 0.0, 5, -1),
        track_row(1, 1, 0.5, 5, 1),
    ]

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert len(events) == 1
    assert events[0] == {
        "video_id": "demo",
        "line_id": "line_main",
        "frame_index": 1,
        "timestamp_sec": 0.5,
        "track_id": 1,
        "class_id": 1,
        "class_name": "Car",
        "direction": "in",
        "center_x": 5,
        "center_y": 1,
    }
    assert summary["total_count"] == 1
    assert summary["by_direction"] == {"in": 1}


def test_reverse_crossing_uses_opposite_direction():
    forward_events, _ = count_line_crossings(
        [track_row(1, 0, 0.0, 5, -1), track_row(1, 1, 0.5, 5, 1)],
        LINE_CONFIG,
    )
    reverse_events, _ = count_line_crossings(
        [track_row(2, 0, 0.0, 5, 1), track_row(2, 1, 0.5, 5, -1)],
        LINE_CONFIG,
    )

    assert len(reverse_events) == 1
    assert reverse_events[0]["direction"] != forward_events[0]["direction"]
    assert {forward_events[0]["direction"], reverse_events[0]["direction"]} == {
        "in",
        "out",
    }


def test_same_side_motion_does_not_create_event():
    events, summary = count_line_crossings(
        [track_row(3, 0, 0.0, 5, 1), track_row(3, 1, 0.5, 5, 2)],
        LINE_CONFIG,
    )

    assert events == []
    assert summary["total_count"] == 0


def test_target_classes_filter_excludes_other_classes():
    rows = [
        track_row(4, 0, 0.0, 5, -1, class_name="Bus", class_id=0),
        track_row(4, 1, 0.5, 5, 1, class_name="Bus", class_id=0),
    ]

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert events == []
    assert summary["total_count"] == 0


def test_disabled_line_returns_no_events_and_empty_summary():
    disabled_config = {**LINE_CONFIG, "enabled": False}

    events, summary = count_line_crossings(
        [track_row(1, 0, 0.0, 5, -1), track_row(1, 1, 0.5, 5, 1)],
        disabled_config,
    )

    assert events == []
    assert summary == summarize_count_events([])


def test_repeated_crossings_are_deduplicated_by_direction():
    rows = [
        track_row(1, 0, 0.0, 5, -1),
        track_row(1, 1, 0.5, 5, 1),
        track_row(1, 2, 1.0, 5, -1),
        track_row(1, 3, 1.5, 5, 1),
    ]

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert len(events) == 2
    assert summary["total_count"] == 2
    assert summary["by_direction"] == {"in": 1, "out": 1}


@pytest.mark.parametrize("state", ["tentative", "lost"])
def test_non_confirmed_tracks_are_not_counted(state):
    rows = [
        track_row(5, 0, 0.0, 5, -1, state=state),
        track_row(5, 1, 0.5, 5, 1, state=state),
    ]

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert events == []
    assert summary["total_count"] == 0


def test_missing_state_defaults_to_confirmed():
    rows = [
        track_row(6, 0, 0.0, 5, -1),
        track_row(6, 1, 0.5, 5, 1),
    ]
    for row in rows:
        row.pop("state")

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert len(events) == 1
    assert summary["total_count"] == 1


def test_summary_counts_direction_class_line_and_class_groups():
    events = [
        {
            "line_id": "line_main",
            "direction": "in",
            "class_name": "Car",
        },
        {
            "line_id": "line_main",
            "direction": "out",
            "class_name": "Person",
        },
        {
            "line_id": "line_side",
            "direction": "in",
            "class_name": "Truck",
        },
    ]

    summary = summarize_count_events(events)

    assert summary == {
        "total_count": 3,
        "by_direction": {"in": 2, "out": 1},
        "by_class": {"Car": 1, "Person": 1, "Truck": 1},
        "by_line": {"line_main": 2, "line_side": 1},
        "vehicle_total": 2,
        "pedestrian_total": 1,
    }


def test_rows_are_sorted_by_track_and_frame_before_counting():
    rows = [
        track_row(8, 1, 0.5, 5, 1),
        track_row(7, 1, 0.5, 5, -1),
        track_row(8, 0, 0.0, 5, -1),
        track_row(7, 0, 0.0, 5, 1),
    ]

    events, summary = count_line_crossings(rows, LINE_CONFIG)

    assert len(events) == 2
    assert summary["total_count"] == 2
    assert {event["track_id"] for event in events} == {7, 8}


def test_line_config_requires_two_points():
    invalid_config = {**LINE_CONFIG, "points": [[0, 0]]}

    with pytest.raises(ValueError):
        count_line_crossings([], invalid_config)
