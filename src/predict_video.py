"""CSV-first YOLOv8 video detection skeleton.

This writes detections.csv rows for video detections. It does not track
objects, integrate ByteTrack/DeepSORT, or render tracked video.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "runs/detect/train/weights/best.pt"

DETECTION_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "detection_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]

YOLO = None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLOv8 video detection CSV export.")
    parser.add_argument("--source", required=True, help="Video file path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to trained best.pt.")
    parser.add_argument("--output-csv", type=Path, help="Output detections.csv path.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size.")
    parser.add_argument("--device", default="cpu", help="Inference device.")
    parser.add_argument("--video-id", help="Optional stable video_id for output rows.")
    parser.add_argument(
        "--save-annotated",
        action="store_true",
        help="Explicitly save YOLO annotated video output using Ultralytics.",
    )
    parser.add_argument("--project", default="results", help="Annotated video project directory.")
    parser.add_argument("--name", default="videos", help="Annotated video run name.")
    return parser.parse_args(argv)


def yolo_result_to_detection_rows(
    result: Any,
    video_id: str,
    frame_index: int,
    timestamp_sec: float,
) -> list[dict[str, Any]]:
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(getattr(boxes, "xyxy", [])) == 0:
        return []

    xyxy_rows = _as_list(boxes.xyxy)
    confidences = _as_list(boxes.conf)
    class_ids = [int(value) for value in _as_list(boxes.cls)]
    names = getattr(result, "names", {}) or {}

    rows: list[dict[str, Any]] = []
    for detection_index, (box, confidence, class_id) in enumerate(
        zip(xyxy_rows, confidences, class_ids),
        start=1,
    ):
        xmin, ymin, xmax, ymax = [float(value) for value in box]
        rows.append(
            {
                "video_id": video_id,
                "frame_index": frame_index,
                "timestamp_sec": timestamp_sec,
                "detection_id": detection_index,
                "class_id": class_id,
                "class_name": names.get(class_id, str(class_id)),
                "confidence": round(float(confidence), 4),
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
        )
    return rows


def write_detections_csv(rows: list[dict[str, Any]], output_csv: str | Path) -> Path:
    path = Path(output_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=DETECTION_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def run_video_detection_csv(
    model_path: str | Path,
    source: str | Path,
    output_csv: str | Path,
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
    video_id: str | None = None,
) -> dict[str, Any]:
    model_path_str = str(model_path)
    source_str = str(source)
    output_path = Path(output_csv)
    model = _load_yolo_model(model_path_str)
    results = model.predict(
        source=source_str,
        conf=conf,
        imgsz=imgsz,
        device=device,
        stream=False,
        verbose=False,
        save=False,
    )

    effective_video_id = video_id or Path(source_str).name
    rows: list[dict[str, Any]] = []
    for frame_index, result in enumerate(results):
        # Skeleton behavior: timestamps use frame_index until fps integration is wired from video_reader.
        rows.extend(
            yolo_result_to_detection_rows(
                result,
                video_id=effective_video_id,
                frame_index=frame_index,
                timestamp_sec=float(frame_index),
            )
        )

    written_path = write_detections_csv(rows, output_path)
    return {
        "model_path": model_path_str,
        "source": source_str,
        "output_csv": str(written_path),
        "rows": len(rows),
        "conf": conf,
        "imgsz": imgsz,
        "device": device,
    }


def run_annotated_video_predict(
    model_path: str | Path,
    source: str | Path,
    conf: float = 0.25,
    project: str = "results",
    name: str = "videos",
) -> dict[str, Any]:
    source_path = existing_file(str(source), "Video source")
    model_path_obj = existing_file(str(model_path), "Model weights")
    model = _load_yolo_model(str(model_path_obj))
    model.predict(
        source=str(source_path),
        conf=conf,
        save=True,
        project=project,
        name=name,
    )
    return {
        "mode": "annotated_video",
        "model_path": str(model_path_obj),
        "source": str(source_path),
        "project": project,
        "name": name,
        "conf": conf,
    }


def existing_file(path: str, description: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"{description} not found: {file_path}. "
            "Please create or provide the file before running this command."
        )
    return file_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.save_annotated:
        summary = run_annotated_video_predict(
            model_path=args.model,
            source=args.source,
            conf=args.conf,
            project=args.project,
            name=args.name,
        )
    else:
        output_csv = args.output_csv or Path("detections.csv")
        summary = run_video_detection_csv(
            model_path=args.model,
            source=args.source,
            output_csv=output_csv,
            conf=args.conf,
            imgsz=args.imgsz,
            device=args.device,
            video_id=args.video_id,
        )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


def _load_yolo_model(model_path: str):
    global YOLO
    if YOLO is None:
        try:
            from ultralytics import YOLO as ultralytics_yolo
        except ImportError as exc:
            raise RuntimeError("ultralytics is required for video detection CSV export") from exc
        YOLO = ultralytics_yolo
    return YOLO(model_path)


def _as_list(value: Any) -> list[Any]:
    for method_name in ("cpu", "numpy"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return tolist()
    return list(value)


if __name__ == "__main__":
    raise SystemExit(main())
