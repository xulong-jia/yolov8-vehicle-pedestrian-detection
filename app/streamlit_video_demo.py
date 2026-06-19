from __future__ import annotations

from typing import Any

import streamlit as st

from src.services.video_demo_catalog import build_demo_catalog


def _nested_value(data: dict[str, Any], path: list[str], default: Any = 0) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _file_rows(files: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for artifact, summary in files.items():
        if not isinstance(summary, dict):
            continue
        rows.append(
            {
                "artifact": artifact,
                "exists": summary.get("exists", False),
                "path": summary.get("path", ""),
                "line_count": summary.get("line_count", ""),
                "row_count": summary.get("row_count", ""),
            }
        )
    return rows


def _render_csv_preview(title: str, rows: list[dict[str, Any]]) -> None:
    st.subheader(title)
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.caption("No preview rows available.")


def main() -> None:
    st.set_page_config(page_title="YOLOv8 Video Analysis Demo", layout="wide")
    st.title("YOLOv8 Video Analysis Demo")

    st.warning(
        "This page is read-only. It does not run YOLO, does not run ByteTrack, "
        "does not run analytics, and does not generate videos. Do not commit "
        "local output artifacts."
    )

    with st.sidebar:
        st.header("Artifacts")
        run_dir = st.text_input(
            "Video analysis run directory",
            value="",
            placeholder="/tmp/yolov8_bytetrack_pipeline_validation/analytics/bytetrack_validation",
            help="Directory containing metadata.json, tracks.csv, events.jsonl, and video_analysis_summary.json.",
        )
        tracked_video = st.text_input(
            "Tracked preview video path",
            value="",
            placeholder="/tmp/yolov8_bytetrack_pipeline_validation/bytetrack_tracked_preview_300.mp4",
        )
        comparison_json = st.text_input(
            "Tracking comparison JSON path",
            value="",
            placeholder="/tmp/yolov8_tracking_comparison.json",
        )
        load_clicked = st.button("Load artifacts", type="primary")

    if not load_clicked:
        st.info("Enter local artifact paths in the sidebar and click Load artifacts.")
        return

    catalog = build_demo_catalog(
        base_dir=run_dir.strip() or None,
        tracked_video=tracked_video.strip() or None,
        comparison_json=comparison_json.strip() or None,
    )
    analysis_run = catalog["video_analysis_run"]
    summary = analysis_run.get("summary", {})
    files = analysis_run.get("files", {})
    tracks_summary = files.get("tracks_csv", {})

    st.caption("Catalog notes: " + " ".join(catalog.get("notes", [])))

    st.subheader("Run Summary")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Detections", _nested_value(summary, ["detection_count"]))
    metric_cols[1].metric("Tracks", _nested_value(summary, ["track_count"]))
    metric_cols[2].metric("Line Count", _nested_value(summary, ["count_summary", "total_count"]))
    metric_cols[3].metric("ROI Frames", _nested_value(summary, ["roi_summary", "frames_observed"]))
    metric_cols[4].metric("Events", _nested_value(summary, ["event_summary", "total_events"]))

    st.subheader("Tracks Summary")
    track_cols = st.columns(3)
    track_cols[0].metric("Track Rows", tracks_summary.get("row_count", 0))
    track_cols[1].metric("Unique Tracks", tracks_summary.get("unique_tracks", 0))
    track_cols[2].metric("Frames With Tracks", tracks_summary.get("frames_with_rows", 0))
    st.json(tracks_summary.get("class_counts", {}))

    st.subheader("Artifacts")
    st.dataframe(_file_rows(files), use_container_width=True)

    _render_csv_preview("Tracks CSV Preview", tracks_summary.get("head", []))
    _render_csv_preview(
        "Count Events CSV Preview",
        files.get("count_events_csv", {}).get("head", []),
    )
    _render_csv_preview(
        "ROI Frame Counts CSV Preview",
        files.get("roi_frame_counts_csv", {}).get("head", []),
    )

    st.subheader("Events JSONL Preview")
    events_head = files.get("events_jsonl", {}).get("head", [])
    if events_head:
        st.json(events_head)
    else:
        st.caption("No event preview rows available.")

    st.subheader("Tracking Comparison")
    if catalog.get("comparison"):
        st.json(catalog["comparison"])
    else:
        st.caption("No comparison JSON loaded.")

    st.subheader("Tracked Preview Video")
    video_summary = catalog.get("tracked_video", {})
    if video_summary.get("exists"):
        st.caption(f"{video_summary['path']} ({video_summary['size_mb']} MB)")
        st.video(video_summary["path"])
    else:
        st.caption("No tracked preview video found for the provided path.")


if __name__ == "__main__":
    main()
