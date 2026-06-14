# Dataset Card

## Dataset Overview

- Dataset source: Roboflow vehicle-pedestrian detection dataset
- Task: object detection
- Format: YOLOv8
- Classes: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, `mini-truck`

## Dataset Splits

| Split | Images |
| --- | ---: |
| train | 2770 |
| validation | 791 |
| test | 396 |
| total | 3957 |

## Annotation Distribution

The table below is based on `docs/dataset_distribution.md` and `docs/dataset_distribution.csv`.

| Class | train | validation | test | total |
| --- | ---: | ---: | ---: | ---: |
| Bus | 843 | 242 | 146 | 1231 |
| Car | 4369 | 1197 | 479 | 6045 |
| Motorcycle | 792 | 249 | 104 | 1145 |
| Person | 4646 | 1332 | 613 | 6591 |
| Truck | 1628 | 409 | 186 | 2223 |
| mini-truck | 1101 | 302 | 114 | 1517 |

## Label Quality Checks

The dataset distribution artifacts report:

- no empty labels
- no missing labels
- no orphan labels
- no invalid class IDs
- polygon-like invalid labels were converted to bounding boxes where needed

## Dataset Storage Policy

- Full dataset images and labels are not tracked in Git.
- `dataset/train/`, `dataset/valid/`, and `dataset/test/` are ignored.
- Only `dataset/data.yaml` and lightweight metadata/docs are tracked.

## Known Dataset Limitations

- Class imbalance is present across the six classes.
- Small-object difficulty appears in qualitative error analysis.
- Crowded traffic scenes can make object separation difficult.
- `Car`, `Truck`, and `mini-truck` have visual similarity and may be confused.
- The dataset may contain domain bias from its source collection.
- Performance may not generalize to all traffic scenes.

## Related Files

- `dataset/data.yaml`
- `docs/dataset_distribution.md`
- `docs/dataset_distribution.csv`
- `docs/dataset_distribution.png`
- `docs/model_card.md`
- `docs/project_task_board.md`
