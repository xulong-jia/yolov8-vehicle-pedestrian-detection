"""Train a YOLOv8 detector.

This script is a runnable entry point only. It does not run unless invoked by
the user and requires a real YOLOv8 dataset at dataset/data.yaml.
"""

from pathlib import Path
import argparse

from ultralytics import YOLO


DEFAULT_DATA = "dataset/data.yaml"


def existing_file(path: str, description: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"{description} not found: {file_path}. "
            "Please create or provide the file before running this command."
        )
    return file_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8 on the project dataset.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to YOLOv8 data.yaml.")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model name or local .pt file.")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Input image size.")
    parser.add_argument("--project", default="runs/detect", help="Output project directory.")
    parser.add_argument("--name", default="train", help="Run name.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = existing_file(args.data, "Dataset config")

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()
