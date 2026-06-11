"""Evaluate a trained YOLOv8 detector."""

from pathlib import Path
import argparse

from ultralytics import YOLO


DEFAULT_DATA = "dataset/data.yaml"
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
    parser = argparse.ArgumentParser(description="Evaluate YOLOv8 model metrics.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to YOLOv8 data.yaml.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Path to trained best.pt.")
    parser.add_argument("--imgsz", type=int, default=640, help="Validation image size.")
    parser.add_argument("--split", default="val", choices=["val", "test"], help="Dataset split to evaluate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_path = existing_file(args.data, "Dataset config")
    model_path = existing_file(args.model, "Model weights")

    model = YOLO(str(model_path))
    metrics = model.val(data=str(data_path), imgsz=args.imgsz, split=args.split)

    print(f"Precision: {metrics.box.mp:.6f}")
    print(f"Recall: {metrics.box.mr:.6f}")
    print(f"mAP50: {metrics.box.map50:.6f}")
    print(f"mAP50-95: {metrics.box.map:.6f}")


if __name__ == "__main__":
    main()
