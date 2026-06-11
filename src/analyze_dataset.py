"""Analyze a YOLOv8 dataset structure and label counts."""

from collections import Counter
from pathlib import Path
import argparse

import pandas as pd
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


def names_to_list(names: object) -> list[str]:
    if isinstance(names, dict):
        return [str(names[key]) for key in sorted(names, key=lambda value: int(value))]
    if isinstance(names, list):
        return [str(name) for name in names]
    raise ValueError("`names` must be a list or dictionary in data.yaml.")


def resolve_split_images(data_yaml: Path, data: dict, split: str) -> Path:
    key = "val" if split == "valid" else split
    configured = data.get(key) or data.get(split)
    if configured:
        images_dir = Path(configured)
        if not images_dir.is_absolute():
            images_dir = data_yaml.parent / images_dir
    else:
        images_dir = data_yaml.parent / split / "images"
    return images_dir


def count_split(images_dir: Path, names: list[str]) -> dict:
    labels_dir = images_dir.parent / "labels"
    image_count = len([path for path in images_dir.glob("*") if path.suffix.lower() in IMAGE_EXTENSIONS]) if images_dir.is_dir() else 0
    label_files = sorted(labels_dir.glob("*.txt")) if labels_dir.is_dir() else []

    class_counts: Counter[str] = Counter()
    box_count = 0
    for label_file in label_files:
        with label_file.open("r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 1:
                    continue
                class_id = int(float(parts[0]))
                class_name = names[class_id] if class_id < len(names) else str(class_id)
                class_counts[class_name] += 1
                box_count += 1

    return {
        "images_dir": str(images_dir),
        "labels_dir": str(labels_dir),
        "image_count": image_count,
        "label_file_count": len(label_files),
        "box_count": box_count,
        "class_counts": dict(class_counts),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze YOLOv8 dataset counts.")
    parser.add_argument("--data", default=DEFAULT_DATA, help="Path to YOLOv8 data.yaml.")
    parser.add_argument("--output", default="results/metrics/dataset_summary.csv", help="CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_yaml = existing_file(args.data, "Dataset config")
    data = load_data_yaml(data_yaml)
    names = names_to_list(data["names"])

    rows = []
    for split in ["train", "valid", "test"]:
        stats = count_split(resolve_split_images(data_yaml, data, split), names)
        row = {
            "split": split,
            "images_dir": stats["images_dir"],
            "labels_dir": stats["labels_dir"],
            "image_count": stats["image_count"],
            "label_file_count": stats["label_file_count"],
            "box_count": stats["box_count"],
        }
        for class_name in names:
            row[f"boxes_{class_name}"] = stats["class_counts"].get(class_name, 0)
        rows.append(row)

    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)
    print(f"Saved dataset summary: {output_path}")


if __name__ == "__main__":
    main()
