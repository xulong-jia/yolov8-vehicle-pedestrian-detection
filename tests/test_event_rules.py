import pytest

from src.analytics.event_rules import (
    detect_crowd_warning,
    detect_long_stay,
    detect_wrong_direction,
    summarize_events,
)


CROWD_RULE = {
    "id": "crowd_main",
    "event_type": "crowd_warning",
    "enabled": True,
    "roi_id": "roi_main",
    "target_classes": ["Person"],
    "parameters": {
        "min_count": 3,
        "min_duration_sec": 2.0,
        "cooldown_sec": 10.0,
    },
}

LONG_STAY_RULE = {
    "id": "long_stay_main",
    "event_type": "long_stay",
    "enabled": True,
    "roi_id": "roi_main",
    "target_classes": ["Car", "Person"],
    "parameters": {
        "min_duration_sec": 5.0,
        "cooldown_sec": 10.0,
    },
}

WRONG_DIRECTION_RULE = {
    "id": "wrong_direction_main",
    "event_type": "wrong_direction",
    "enabled": True,
    "line_id": "line_main",
    "target_classes": ["Car"],
    "parameters": {
        "expected_direction": "in",
        "min_track_length": 3,
        "min_displacement_px": 5.0,
        "cooldown_sec": 10.0,
    },
}


def roi_count(frame_index, timestamp_sec, object_count, class_name="Person", roi_id="roi_main"):
    return {
        "video_id": "demo",
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "roi_id": roi_id,
        "roi_name": "Main ROI",
        "class_name": class_name,
        "object_count": object_count,
        "unique_track_count": object_count,
    }


def track_row(
    track_id,
    frame_index,
    timestamp_sec,
    class_name="Car",
    roi_id="roi_main",
    line_id="line_main",
    direction=None,
    center_x=0.0,
    center_y=0.0,
):
    return {
        "video_id": "demo",
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "track_id": track_id,
        "class_name": class_name,
        "roi_id": roi_id,
        "line_id": line_id,
        "direction": direction,
        "center_x": center_x,
        "center_y": center_y,
    }


def test_crowd_warning_triggers_after_min_duration():
    rows = [
        roi_count(0, 0.0, 3),
        roi_count(1, 1.0, 4),
        roi_count(2, 2.0, 5),
    ]

    events = detect_crowd_warning(rows, CROWD_RULE)

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "crowd_warning"
    assert event["video_id"] == "demo"
    assert event["frame_index"] == 2
    assert event["timestamp_sec"] == 2.0
    assert event["track_id"] is None
    assert event["class_name"] == "Person"
    assert event["roi_id"] == "roi_main"
    assert event["line_id"] is None
    assert event["severity"] == "warning"
    assert event["evidence"] == {
        "max_count": 5,
        "min_count": 3,
        "duration_sec": 2.0,
        "min_duration_sec": 2.0,
    }


@pytest.mark.parametrize(
    "rows, rule",
    [
        ([roi_count(0, 0.0, 2), roi_count(1, 1.0, 2), roi_count(2, 2.0, 2)], CROWD_RULE),
        ([roi_count(0, 0.0, 3), roi_count(1, 1.0, 4)], CROWD_RULE),
        ([roi_count(0, 0.0, 3), roi_count(1, 1.0, 4), roi_count(2, 2.0, 5)], {**CROWD_RULE, "enabled": False}),
        ([roi_count(0, 0.0, 3, class_name="Car"), roi_count(1, 1.0, 4, class_name="Car"), roi_count(2, 2.0, 5, class_name="Car")], CROWD_RULE),
    ],
)
def test_crowd_warning_does_not_trigger_for_non_matching_conditions(rows, rule):
    assert detect_crowd_warning(rows, rule) == []


def test_long_stay_triggers_when_track_stays_in_roi_long_enough():
    rows = [
        track_row(1, 0, 0.0),
        track_row(1, 1, 3.0),
        track_row(1, 2, 6.0),
    ]

    events = detect_long_stay(rows, LONG_STAY_RULE)

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "long_stay"
    assert event["video_id"] == "demo"
    assert event["frame_index"] == 2
    assert event["timestamp_sec"] == 6.0
    assert event["track_id"] == 1
    assert event["class_name"] == "Car"
    assert event["roi_id"] == "roi_main"
    assert event["line_id"] is None
    assert event["evidence"] == {
        "duration_sec": 6.0,
        "min_duration_sec": 5.0,
        "start_time_sec": 0.0,
        "end_time_sec": 6.0,
    }


@pytest.mark.parametrize(
    "rows, rule",
    [
        ([track_row(1, 0, 0.0), track_row(1, 1, 3.0)], LONG_STAY_RULE),
        ([track_row(1, 0, 0.0), track_row(1, 1, 6.0)], {**LONG_STAY_RULE, "enabled": False}),
        ([track_row(1, 0, 0.0, class_name="Bus"), track_row(1, 1, 6.0, class_name="Bus")], LONG_STAY_RULE),
        ([track_row(1, 0, 0.0, roi_id="other"), track_row(1, 1, 6.0, roi_id="other")], LONG_STAY_RULE),
    ],
)
def test_long_stay_does_not_trigger_for_non_matching_conditions(rows, rule):
    assert detect_long_stay(rows, rule) == []


def test_wrong_direction_triggers_for_unexpected_direction_with_enough_motion():
    rows = [
        track_row(1, 0, 0.0, direction="out", center_x=0.0, center_y=0.0),
        track_row(1, 1, 1.0, direction="out", center_x=3.0, center_y=4.0),
        track_row(1, 2, 2.0, direction="out", center_x=6.0, center_y=8.0),
    ]

    events = detect_wrong_direction(rows, WRONG_DIRECTION_RULE)

    assert len(events) == 1
    event = events[0]
    assert event["event_type"] == "wrong_direction"
    assert event["video_id"] == "demo"
    assert event["frame_index"] == 2
    assert event["timestamp_sec"] == 2.0
    assert event["track_id"] == 1
    assert event["class_name"] == "Car"
    assert event["roi_id"] is None
    assert event["line_id"] == "line_main"
    assert event["evidence"] == {
        "expected_direction": "in",
        "actual_direction": "out",
        "track_length": 3,
        "displacement_px": 10.0,
        "min_displacement_px": 5.0,
    }


@pytest.mark.parametrize(
    "rows, rule",
    [
        ([track_row(1, 0, 0.0, direction="in", center_x=0.0, center_y=0.0), track_row(1, 1, 1.0, direction="in", center_x=3.0, center_y=4.0), track_row(1, 2, 2.0, direction="in", center_x=6.0, center_y=8.0)], WRONG_DIRECTION_RULE),
        ([track_row(1, 0, 0.0, direction="out", center_x=0.0, center_y=0.0), track_row(1, 1, 1.0, direction="out", center_x=6.0, center_y=8.0)], WRONG_DIRECTION_RULE),
        ([track_row(1, 0, 0.0, direction="out", center_x=0.0, center_y=0.0), track_row(1, 1, 1.0, direction="out", center_x=1.0, center_y=1.0), track_row(1, 2, 2.0, direction="out", center_x=2.0, center_y=2.0)], WRONG_DIRECTION_RULE),
        ([track_row(1, 0, 0.0, direction="out", center_x=0.0, center_y=0.0), track_row(1, 1, 1.0, direction="out", center_x=6.0, center_y=8.0), track_row(1, 2, 2.0, direction="out", center_x=12.0, center_y=16.0)], {**WRONG_DIRECTION_RULE, "enabled": False}),
        ([track_row(1, 0, 0.0, class_name="Person", direction="out", center_x=0.0, center_y=0.0), track_row(1, 1, 1.0, class_name="Person", direction="out", center_x=6.0, center_y=8.0), track_row(1, 2, 2.0, class_name="Person", direction="out", center_x=12.0, center_y=16.0)], WRONG_DIRECTION_RULE),
    ],
)
def test_wrong_direction_does_not_trigger_for_non_matching_conditions(rows, rule):
    assert detect_wrong_direction(rows, rule) == []


def test_summarize_events_counts_type_severity_roi_and_line():
    events = [
        {
            "event_type": "crowd_warning",
            "severity": "warning",
            "roi_id": "roi_main",
            "line_id": None,
        },
        {
            "event_type": "long_stay",
            "severity": "warning",
            "roi_id": "roi_main",
            "line_id": None,
        },
        {
            "event_type": "wrong_direction",
            "severity": "critical",
            "roi_id": None,
            "line_id": "line_main",
        },
    ]

    assert summarize_events(events) == {
        "total_events": 3,
        "by_type": {"crowd_warning": 1, "long_stay": 1, "wrong_direction": 1},
        "by_severity": {"warning": 2, "critical": 1},
        "by_roi": {"roi_main": 2},
        "by_line": {"line_main": 1},
    }


def test_empty_event_summary_has_zero_counts():
    assert summarize_events([]) == {
        "total_events": 0,
        "by_type": {},
        "by_severity": {},
        "by_roi": {},
        "by_line": {},
    }


def test_event_id_is_non_empty_and_deterministic():
    rows = [
        roi_count(0, 0.0, 3),
        roi_count(1, 1.0, 4),
        roi_count(2, 2.0, 5),
    ]

    first = detect_crowd_warning(rows, CROWD_RULE)
    second = detect_crowd_warning(rows, CROWD_RULE)

    assert first[0]["event_id"]
    assert first[0]["event_id"] == second[0]["event_id"]
