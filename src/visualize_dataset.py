"""Visualize YOLO-format labels for a few dataset samples."""

from pathlib import Path
import argparse
import random

import cv2
import yaml


DEFAULT_DATA = "dataset/data.yaml"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def existing_file(path: str, description: str) -> Path:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"{description} not found: {file_path}. "
            "Please create or provide the file before running this command."
        )
    return file_path


def load_data_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if "names" not in data:
        raise ValueError(f"`names` field is missing in {path}.")
    return data


def resolve_split_images(data_yaml: Path, data: dict, split: str) -> Path:
    split_key = "val" if split == "valid" else split
    configured = data.get(split_key) or data.get(split)
    if configured:
        images_dir = Path(configured)
        if not images_dir.is_absolute():
            images_dir = data_yaml.parent / images_dir
    else:
        images_dir = data_yaml.parent / split / "images"

    if not images_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found for split '{split}': {images_dir}")
    return images_dir


def names_to_list(names: object) -> list[str]:
    if isinstance(names, dict):
        return [str(names[key]) for key in sorted(names, key=lambda value: int(value))]
    if isinstance(names, list):
        return [str(name) for name in names]
    raise ValueError("`names` must be a list or dictionary in data.yaml.")


def draw_yolo_labels(image_path: Path, label_path: Path, names: list[str], output_path: Path) -> None:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Failed to read image: {image_path}")

    height, width = image.shape[:2]
    if label_path.is_file():
        with label_path.open("r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                class_id, x_center, y_center, box_width, box_height = map(float, parts)
                left = int((x_center - box_width / 2) * width)
                top = int((y_center - box_height / 2) * height)
                right = int((x_center + box_width / 2) * width)
                bottom = int((y_center + box_height / 2) * height)
                label = names[int(class_id)] if int(class_id) < len(names) else str(int(class_id))

                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(
                    image,
                    label,
                    (left, max(top - 8, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize YOLOv8 dataset labels.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to YOLOv8 data.yaml.")
    parser.add_argument("--split", default="train", choices=["train", "valid", "val", "test"], help="Dataset split.")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples to visualize.")
    parser.add_argument("--output", default="docs/screenshots", help="Output directory for visualized samples.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_yaml = existing_file(args.data, "Dataset config")
    data = load_data_yaml(data_yaml)
    names = names_to_list(data["names"])
    images_dir = resolve_split_images(data_yaml, data, args.split)
    labels_dir = images_dir.parent / "labels"

    images = sorted(path for path in images_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
    if not images:
        raise FileNotFoundError(f"No image files found in {images_dir}.")

    random.seed(args.seed)
    selected = random.sample(images, min(args.num_samples, len(images)))
    for image_path in selected:
        label_path = labels_dir / f"{image_path.stem}.txt"
        output_path = Path(args.output) / f"{args.split}_{image_path.name}"
        draw_yolo_labels(image_path, label_path, names, output_path)
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
