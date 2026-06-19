import pytest

from src.analytics.roi_counter import count_roi_occupancy, summarize_roi_counts


ROI_CONFIG = {
    "id": "roi_main",
    "name": "Main ROI",
    "polygon": [[0, 0], [10, 0], [10, 10], [0, 10]],
    "target_classes": ["Car", "Person"],
    "enabled": True,
}


def track_row(
    track_id,
    frame_index,
    timestamp_sec,
    xmin,
    ymin,
    xmax,
    ymax,
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
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
        "center_x": (xmin + xmax) / 2,
        "center_y": (ymin + ymax) / 2,
        "state": state,
    }


def test_single_frame_roi_count_excludes_outside_tracks():
    rows = [
        track_row(1, 0, 0.0, 4, 4, 6, 6, class_name="Car", class_id=1),
        track_row(2, 0, 0.0, 14, 4, 16, 6, class_name="Person", class_id=3),
    ]

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert counts == [
        {
            "video_id": "demo",
            "frame_index": 0,
            "timestamp_sec": 0.0,
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "class_name": "Car",
            "object_count": 1,
            "unique_track_count": 1,
        }
    ]
    assert summary["max_count"] == 1
    assert summary["avg_count"] == 1.0
    assert summary["by_class"]["Car"] == {
        "max_count": 1,
        "avg_count": 1.0,
        "unique_tracks": 1,
    }


def test_multi_frame_roi_counts_track_class_occupancy_per_frame():
    rows = [
        track_row(1, 0, 0.0, 4, 4, 6, 6, class_name="Car", class_id=1),
        track_row(1, 1, 0.5, 5, 4, 7, 6, class_name="Car", class_id=1),
        track_row(2, 1, 0.5, 2, 2, 3, 3, class_name="Person", class_id=3),
    ]

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert counts == [
        {
            "video_id": "demo",
            "frame_index": 0,
            "timestamp_sec": 0.0,
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "class_name": "Car",
            "object_count": 1,
            "unique_track_count": 1,
        },
        {
            "video_id": "demo",
            "frame_index": 1,
            "timestamp_sec": 0.5,
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "class_name": "Car",
            "object_count": 1,
            "unique_track_count": 1,
        },
        {
            "video_id": "demo",
            "frame_index": 1,
            "timestamp_sec": 0.5,
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "class_name": "Person",
            "object_count": 1,
            "unique_track_count": 1,
        },
    ]
    assert summary["frames_observed"] == 2
    assert summary["by_class"]["Car"]["unique_tracks"] == 1
    assert summary["by_class"]["Person"]["unique_tracks"] == 1


def test_target_classes_filter_excludes_other_classes():
    rows = [track_row(3, 0, 0.0, 4, 4, 6, 6, class_name="Bus", class_id=0)]

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert counts == []
    assert summary["frames_observed"] == 0


def test_disabled_roi_returns_empty_counts_and_summary():
    disabled_config = {**ROI_CONFIG, "enabled": False}

    counts, summary = count_roi_occupancy(
        [track_row(1, 0, 0.0, 4, 4, 6, 6)],
        disabled_config,
    )

    assert counts == []
    assert summary == summarize_roi_counts([])


def test_point_modes_can_produce_different_membership_results():
    rows = [track_row(1, 0, 0.0, 4, 4, 6, 12)]

    bottom_counts, bottom_summary = count_roi_occupancy(
        rows,
        ROI_CONFIG,
        point_mode="bottom_center",
    )
    center_counts, center_summary = count_roi_occupancy(
        rows,
        ROI_CONFIG,
        point_mode="center",
    )

    assert bottom_counts == []
    assert bottom_summary["frames_observed"] == 0
    assert len(center_counts) == 1
    assert center_summary["frames_observed"] == 1


@pytest.mark.parametrize("state", ["tentative", "lost"])
def test_non_confirmed_tracks_are_not_counted(state):
    rows = [track_row(4, 0, 0.0, 4, 4, 6, 6, state=state)]

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert counts == []
    assert summary["frames_observed"] == 0


def test_missing_state_defaults_to_confirmed():
    rows = [track_row(5, 0, 0.0, 4, 4, 6, 6)]
    rows[0].pop("state")

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert len(counts) == 1
    assert summary["frames_observed"] == 1


def test_boundary_point_is_counted_by_default():
    rows = [track_row(6, 0, 0.0, 0, -2, 0, 0)]

    counts, summary = count_roi_occupancy(rows, ROI_CONFIG)

    assert len(counts) == 1
    assert counts[0]["object_count"] == 1
    assert summary["max_count"] == 1


def test_summary_handles_multiple_classes_and_unique_tracks():
    counts = [
        {
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "frame_index": 0,
            "class_name": "Car",
            "object_count": 2,
            "unique_track_count": 2,
            "_track_ids": {1, 2},
        },
        {
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "frame_index": 1,
            "class_name": "Car",
            "object_count": 1,
            "unique_track_count": 1,
            "_track_ids": {1},
        },
        {
            "roi_id": "roi_main",
            "roi_name": "Main ROI",
            "frame_index": 1,
            "class_name": "Person",
            "object_count": 1,
            "unique_track_count": 1,
            "_track_ids": {3},
        },
    ]

    summary = summarize_roi_counts(counts)

    assert summary == {
        "roi_id": "roi_main",
        "roi_name": "Main ROI",
        "frames_observed": 2,
        "max_count": 2,
        "avg_count": pytest.approx(4 / 3),
        "by_class": {
            "Car": {
                "max_count": 2,
                "avg_count": 1.5,
                "unique_tracks": 2,
            },
            "Person": {
                "max_count": 1,
                "avg_count": 1.0,
                "unique_tracks": 1,
            },
        },
    }


def test_empty_summary_has_zero_counts():
    assert summarize_roi_counts([]) == {
        "roi_id": "",
        "roi_name": "",
        "frames_observed": 0,
        "max_count": 0,
        "avg_count": 0.0,
        "by_class": {},
    }


@pytest.mark.parametrize(
    "invalid_config",
    [
        {"name": "Missing ID", "polygon": [[0, 0], [1, 0], [1, 1]]},
        {"id": "missing_polygon", "name": "Missing Polygon"},
        {"id": "short_polygon", "name": "Short", "polygon": [[0, 0], [1, 1]]},
    ],
)
def test_invalid_roi_config_raises_value_error(invalid_config):
    with pytest.raises(ValueError):
        count_roi_occupancy([], invalid_config)


def test_unsupported_point_mode_raises_value_error():
    with pytest.raises(ValueError):
        count_roi_occupancy([], ROI_CONFIG, point_mode="centroid")
