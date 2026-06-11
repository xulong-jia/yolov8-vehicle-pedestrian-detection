"""Run YOLOv8 inference on an image file or image directory."""

from pathlib import Path
import argparse

from ultralytics import YOLO


DEFAULT_MODEL = "runs/detect/train/weights/best.pt"


def existing_path(path: str, description: str) -> Path:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(
            f"{description} not found: {target}. "
            "Please create or provide the path before running this command."
        )
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run YOLOv8 image inference.")
    parser.add_argument("--source", default="dataset/test/images", help="Image file or directory.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to trained best.pt.")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--project", default="results", help="Output project directory.")
    parser.add_argument("--name", default="images", help="Output run name.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = existing_path(args.source, "Image source")
    model_path = existing_path(args.model, "Model weights")

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
