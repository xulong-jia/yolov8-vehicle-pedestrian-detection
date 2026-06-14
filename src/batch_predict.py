"""Batch image prediction CLI for local YOLOv8 qualitative inference."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DEFAULT_OUTPUT_DIR = "local_outputs/batch_predictions"
CSV_FIELDS = [
    "image_path",
    "image_name",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run batch YOLOv8 image prediction and write a CSV summary."
    )
    parser.add_argument("--model", required=True, help="Path to local model weight.")
    parser.add_argument("--source", required=True, help="Image file or image directory.")
    parser.add_argument("--output-csv", required=True, help="Output CSV path.")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference image size.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--device", default="cpu", help="Inference device.")
    parser.add_argument(
        "--save-images",
        action="store_true",
        help="Save annotated prediction images to output-dir.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for annotated images when --save-images is used.",
    )
    return parser.parse_args()


def short_error(exc: Exception, max_length: int = 180) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def collect_images(source: Path) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image file extension: {source}")
        return [source]

    if source.is_dir():
        return sorted(
            path
            for path in source.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        )

    raise FileNotFoundError(f"Source not found: {source}")


def empty_detection_row(image_path: Path) -> dict[str, str]:
    row = {field: "" for field in CSV_FIELDS}
    row["image_path"] = str(image_path)
    row["image_name"] = image_path.name
    return row


def detection_rows(image_path: Path, result) -> list[dict[str, str | int | float]]:
    if result.boxes is None or len(result.boxes) == 0:
        return [empty_detection_row(image_path)]

    rows = []
    names = result.names
    boxes = result.boxes.xyxy.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    for box, confidence, class_id in zip(boxes, confidences, class_ids):
        xmin, ymin, xmax, ymax = box.tolist()
        rows.append(
            {
                "image_path": str(image_path),
                "image_name": image_path.name,
                "class_id": class_id,
                "class_name": names.get(class_id, str(class_id)),
                "confidence": round(float(confidence), 4),
                "xmin": round(float(xmin), 2),
                "ymin": round(float(ymin), 2),
                "xmax": round(float(xmax), 2),
                "ymax": round(float(ymax), 2),
            }
        )
    return rows


def save_annotated_image(result, image_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    annotated = result.plot()
    Image.fromarray(annotated).save(output_dir / image_path.name)


def main() -> int:
    args = parse_args()
    model_path = Path(args.model)
    source_path = Path(args.source)
    output_csv = Path(args.output_csv)
    output_dir = Path(args.output_dir)

    if not model_path.is_file():
        print(f"ERROR: Model weight not found: {model_path}")
        print("Place the model locally and do not commit weights to Git.")
        return 1

    try:
        image_paths = collect_images(source_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {short_error(exc)}")
        return 1

    if not image_paths:
        print(f"ERROR: No supported images found in source: {source_path}")
        return 1

    if not str(output_dir).startswith("local_outputs"):
        print(
            "WARNING: output-dir is outside local_outputs/. "
            "Ensure generated files are not committed to Git."
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    try:
        model = YOLO(str(model_path))
    except Exception as exc:
        print(f"ERROR: Model loading failed: {short_error(exc)}")
        return 1

    images_with_detections = 0
    images_without_detections = 0
    total_boxes = 0

    try:
        with output_csv.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
            writer.writeheader()

            for image_path in image_paths:
                results = model.predict(
                    source=str(image_path),
                    imgsz=args.imgsz,
                    conf=args.conf,
                    device=args.device,
                    save=False,
                    verbose=False,
                )
                result = results[0]
                boxes_count = 0 if result.boxes is None else len(result.boxes)

                if boxes_count:
                    images_with_detections += 1
                    total_boxes += boxes_count
                else:
                    images_without_detections += 1

                writer.writerows(detection_rows(image_path, result))

                if args.save_images:
                    save_annotated_image(result, image_path, output_dir)
    except Exception as exc:
        print(f"ERROR: Prediction failed: {short_error(exc)}")
        return 1

    print("Batch prediction summary")
    print(f"images processed: {len(image_paths)}")
    print(f"images with detections: {images_with_detections}")
    print(f"images without detections: {images_without_detections}")
    print(f"total boxes: {total_boxes}")
    print(f"output csv path: {output_csv}")
    if args.save_images:
        print(f"annotated images output dir: {output_dir}")
    else:
        print("annotated images were not saved")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
