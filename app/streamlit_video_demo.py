from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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


def _api_request(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed with HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"API request failed: {exc.reason}") from exc
    return json.loads(body) if body else {}


def _render_api_job_launcher() -> None:
    st.header("Video Job Launcher")
    st.caption(
        "This launcher calls the FastAPI service. The API writes results under "
        "`local_outputs/api_video_jobs/<job_id>/`; do not commit those outputs."
    )
    api_base_url = st.text_input("FastAPI base URL", value="http://localhost:8000")

    with st.form("video_job_form"):
        model_path = st.text_input("Model path", value="local_weights/best.pt")
        video_path = st.text_input("Video path", value="local_videos/source/demo.mp4")
        run_name = st.text_input("Run name", value="streamlit_run")
        video_id = st.text_input("Video ID", value="streamlit_demo")
        conf = st.number_input("Confidence", min_value=0.0, max_value=1.0, value=0.25, step=0.05)
        imgsz = st.number_input("Image size", min_value=1, value=640, step=32)
        device = st.text_input("Device", value="cpu")
        submitted = st.form_submit_button("Submit video job", type="primary")

    if submitted:
        payload = {
            "model_path": model_path,
            "video_path": video_path,
            "run_name": run_name,
            "video_id": video_id,
            "conf": conf,
            "imgsz": int(imgsz),
            "device": device,
        }
        try:
            created = _api_request("POST", f"{api_base_url.rstrip('/')}/api/videos/analyze", payload)
        except RuntimeError as exc:
            st.error(str(exc))
        else:
            st.session_state["video_job_id"] = created.get("job_id", "")
            st.success(f"Created job {created.get('job_id')} with status {created.get('status')}")
            st.json(created)

    st.subheader("Query Job")
    job_id = st.text_input("Job ID", value=st.session_state.get("video_job_id", ""))
    if st.button("Query job status"):
        if not job_id.strip():
            st.warning("Enter a job ID first.")
        else:
            try:
                job = _api_request(
                    "GET",
                    f"{api_base_url.rstrip('/')}/api/videos/jobs/{job_id.strip()}",
                )
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.json(job)
                time_rows = [
                    {"field": key, "value": job.get(key) or ""}
                    for key in ("created_at", "updated_at", "started_at", "finished_at")
                ]
                st.dataframe(time_rows, use_container_width=True)
                if job.get("summary_path"):
                    st.caption(f"Summary: {job['summary_path']}")
                artifact_paths = job.get("artifact_paths") or {}
                if artifact_paths:
                    st.dataframe(
                        [{"artifact": key, "path": value} for key, value in artifact_paths.items()],
                        use_container_width=True,
                    )


def main() -> None:
    st.set_page_config(page_title="YOLOv8 Video Analysis Demo", layout="wide")
    st.title("YOLOv8 Video Analysis Demo")

    st.info(
        "Use the launcher to submit jobs to the FastAPI service, or use the "
        "artifact browser to inspect existing outputs. Do not commit local "
        "output artifacts."
    )

    with st.expander("Start or query FastAPI video jobs", expanded=False):
        _render_api_job_launcher()

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
