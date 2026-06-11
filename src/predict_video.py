"""Run YOLOv8 inference on a video file."""

from pathlib import Path
import argparse

from ultralytics import YOLO


DEFAULT_MODEL = "runs/detect/train/weights/best.pt"


def existing_file(path: str, description: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"{description} not found: {file_path}. "
            "Please create or provide the file before running this command."
        )
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLOv8 video inference.")
    parser.add_argument("--source", required=True, help="Video file path.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to trained best.pt.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--project", default="results", help="Output project directory.")
    parser.add_argument("--name", default="videos", help="Output run name.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = existing_file(args.source, "Video source")
    model_path = existing_file(args.model, "Model weights")

    model = YOLO(str(model_path))
    model.predict(
        source=str(source_path),
        conf=args.conf,
        save=True,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()
