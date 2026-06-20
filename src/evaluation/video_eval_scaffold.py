"""Lightweight GT evaluation scaffold for video analytics artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


def read_csv_rows(path: str | Path | None) -> list[dict[str, str]]:
    if not path:
        return []
    input_path = Path(path)
    if not input_path.exists():
        return []
    with input_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def read_jsonl_rows(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    input_path = Path(path)
    if not input_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with input_path.open(encoding="utf-8") as file:
        for line in file:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_event_rows(path: str | Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    input_path = Path(path)
    if input_path.suffix.lower() == ".jsonl":
        return read_jsonl_rows(input_path)
    return read_csv_rows(input_path)


def evaluate_counting(
    pred_rows: Iterable[dict[str, Any]],
    gt_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    pred_total = sum(_row_count(row) for row in pred_rows)
    gt_total = sum(_row_count(row) for row in gt_rows)
    abs_error = abs(pred_total - gt_total)
    return {
        "gt_count": gt_total,
        "pred_count": pred_total,
        "abs_error": abs_error,
        "MAE": float(abs_error),
    }


def evaluate_roi(
    pred_rows: Iterable[dict[str, Any]],
    gt_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    pred_map = {_roi_key(row): _row_count(row) for row in pred_rows}
    gt_map = {_roi_key(row): _row_count(row) for row in gt_rows}
    keys = sorted(set(pred_map) | set(gt_map))
    errors = [abs(pred_map.get(key, 0) - gt_map.get(key, 0)) for key in keys]
    return {
        "frame_count_mae": float(mean(errors)) if errors else 0.0,
        "compared_rows": len(keys),
    }


def evaluate_events(
    pred_rows: Iterable[dict[str, Any]],
    gt_rows: Iterable[dict[str, Any]],
    time_window_sec: float = 1.0,
) -> dict[str, Any]:
    pred_events = list(pred_rows)
    gt_events = list(gt_rows)
    unmatched = pred_events.copy()
    matched = 0
    for gt_event in gt_events:
        match_index = _find_event_match(gt_event, unmatched, time_window_sec)
        if match_index is not None:
            matched += 1
            unmatched.pop(match_index)

    precision = matched / len(pred_events) if pred_events else 0.0
    recall = matched / len(gt_events) if gt_events else 0.0
    return {
        "gt_events": len(gt_events),
        "pred_events": len(pred_events),
        "matched_events": matched,
        "precision": precision,
        "recall": recall,
        "match_rule": "event_type + time_window",
        "time_window_sec": time_window_sec,
    }


def evaluate_tracking_engineering(pred_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    lengths: dict[str, int] = defaultdict(int)
    for row in pred_rows:
        track_id = str(row.get("track_id", "")).strip()
        if track_id:
            lengths[track_id] += 1

    track_lengths = list(lengths.values())
    short_tracks = sum(1 for length in track_lengths if length <= 2)
    return {
        "track_count": len(track_lengths),
        "avg_track_length": float(mean(track_lengths)) if track_lengths else 0.0,
        "short_track_ratio": short_tracks / len(track_lengths) if track_lengths else 0.0,
        "gt_required_for_idf1": True,
    }


def run_video_eval_scaffold(
    *,
    pred_tracks: str | Path | None = None,
    pred_count_events: str | Path | None = None,
    pred_roi_counts: str | Path | None = None,
    pred_events: str | Path | None = None,
    gt_tracks: str | Path | None = None,
    gt_count_events: str | Path | None = None,
    gt_roi_counts: str | Path | None = None,
    gt_events: str | Path | None = None,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tracking_metrics = evaluate_tracking_engineering(read_csv_rows(pred_tracks))
    if gt_tracks:
        tracking_metrics["gt_rows"] = len(read_csv_rows(gt_tracks))

    counting_metrics = evaluate_counting(
        read_csv_rows(pred_count_events),
        read_csv_rows(gt_count_events),
    )
    roi_metrics = evaluate_roi(
        read_csv_rows(pred_roi_counts),
        read_csv_rows(gt_roi_counts),
    )
    event_metrics = evaluate_events(
        read_event_rows(pred_events),
        read_event_rows(gt_events),
    )

    _write_metrics_csv(output_path / "tracking_metrics.csv", tracking_metrics)
    _write_metrics_csv(output_path / "counting_metrics.csv", counting_metrics)
    _write_metrics_csv(output_path / "roi_metrics.csv", roi_metrics)
    _write_metrics_csv(output_path / "event_metrics.csv", event_metrics)

    summary = {
        "tracking": tracking_metrics,
        "counting": counting_metrics,
        "roi": roi_metrics,
        "event": event_metrics,
        "artifact_paths": {
            "tracking_metrics": str(output_path / "tracking_metrics.csv"),
            "counting_metrics": str(output_path / "counting_metrics.csv"),
            "roi_metrics": str(output_path / "roi_metrics.csv"),
            "event_metrics": str(output_path / "event_metrics.csv"),
            "summary": str(output_path / "evaluation_summary.json"),
        },
    }
    (output_path / "evaluation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate predicted video analytics CSV/JSONL artifacts against optional GT templates."
    )
    parser.add_argument("--pred-tracks")
    parser.add_argument("--pred-count-events")
    parser.add_argument("--pred-roi-counts")
    parser.add_argument("--pred-events")
    parser.add_argument("--gt-tracks")
    parser.add_argument("--gt-count-events")
    parser.add_argument("--gt-roi-counts")
    parser.add_argument("--gt-events")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_video_eval_scaffold(
        pred_tracks=args.pred_tracks,
        pred_count_events=args.pred_count_events,
        pred_roi_counts=args.pred_roi_counts,
        pred_events=args.pred_events,
        gt_tracks=args.gt_tracks,
        gt_count_events=args.gt_count_events,
        gt_roi_counts=args.gt_roi_counts,
        gt_events=args.gt_events,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _row_count(row: dict[str, Any]) -> int:
    for field in ("count", "total_count", "object_count", "event_count"):
        value = row.get(field)
        if value not in (None, ""):
            return int(float(value))
    return 1


def _roi_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("video_id", "")),
        str(row.get("roi_id", "")),
        str(row.get("frame_index", "")),
    )


def _find_event_match(
    gt_event: dict[str, Any],
    pred_events: list[dict[str, Any]],
    time_window_sec: float,
) -> int | None:
    gt_type = str(gt_event.get("event_type", ""))
    gt_time = _float_or_none(gt_event.get("timestamp_sec"))
    for index, pred_event in enumerate(pred_events):
        if str(pred_event.get("event_type", "")) != gt_type:
            continue
        if gt_time is None:
            return index
        pred_time = _float_or_none(pred_event.get("timestamp_sec"))
        if pred_time is not None and abs(pred_time - gt_time) <= time_window_sec:
            return index
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _write_metrics_csv(path: Path, metrics: dict[str, Any]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)


if __name__ == "__main__":
    raise SystemExit(main())
