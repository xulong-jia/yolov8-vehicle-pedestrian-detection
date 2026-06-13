# Day 5 Error Analysis Report

## 1. Analysis Goal

This Day 5 analysis organizes the existing Day 4 image inference results into report-ready error categories. The goal is to identify candidate success examples, candidate false positive / false negative examples, and class-confusion cases that can later be summarized in the README or a project report.

## 2. Sample Source

- Selected image list: `docs/predictions/yolov8n_640_50epochs/selected_images.txt`
- Prediction labels: `docs/predictions/yolov8n_640_50epochs/labels/`
- Ground-truth labels: `dataset/test/labels/`
- Class mapping: `dataset/data.yaml`
- Sample size: 10 images selected in Day 4 with fixed random seed `42`

No new sampling, retraining, or video inference was performed for this report.

## 3. Model Used

- Model: YOLOv8n 640x640 50 epoch baseline
- Weights: `local_weights/yolov8n_640_50epochs/best.pt`
- Day 4 output directory: `docs/predictions/yolov8n_640_50epochs/`

## 4. Statistical Method

The analysis compares YOLO-format class IDs from each ground-truth label file with the corresponding prediction label file. Counts are aggregated per class for each image, then mapped into case types from the existing Day 4 `error_analysis.csv`.

This is an image-level count comparison. It does not compute IoU, box matching, confidence calibration, or exact false-positive / false-negative locations. When count evidence is insufficient, the report uses `requires manual visual inspection`.

## 5. Overall Observations

| Case Type | Count | Notes |
| --- | ---: | --- |
| `likely_correct` | 7 | GT and prediction class counts match at image level; still inspect boxes manually. |
| `possible_false_positive` | 2 | Prediction count exceeds GT for at least one class; exact false positive location requires manual visual inspection. |
| `possible_false_negative` | 1 | Prediction count is lower than GT for at least one class; exact missed object location requires manual visual inspection. |
| `possible_class_confusion` | 2 | Class count shifts suggest possible confusion, especially Car / Truck / mini-truck. |
| `possible_duplicate_boxes` | 0 | Not assigned from label-count evidence alone; duplicate boxes require visual inspection. |
| `crowded_scene` | 4 | Scene has multiple nearby objects or dense traffic/person layout. |
| `small_object_difficulty` | 0 | Not assigned from label-count evidence alone; small-object status requires manual visual inspection. |
| `needs_manual_review` | 3 | Counts differ or case is flagged for qualitative review. |


Key observations:

- `7` of 10 images are likely correct at the image-level count stage.
- `3` of 10 images are flagged for manual review.
- The main vehicle issue is concentrated in dense traffic scenes where `Car`, `Truck`, and `mini-truck` counts shift between GT and prediction.
- The main Person issue is one crowded / occluded scene where the model predicts fewer persons than GT.

## 6. Successful Detection Cases

Recommended success examples for README or report use:

- `1c4915190a748798_jpg.rf.0c265452437e4c470eee04c6c8a24fc9.jpg`: GT `Bus:1`, prediction `Bus:1`. box localization quality requires manual visual inspection
- `train_all_data-384-_jpg.rf.38f6abd346046f3f733765041fccda76.jpg`: GT `Person:3`, prediction `Person:3`. box localization quality requires manual visual inspection
- `0e568901d66ad81e46860b91cce2a7fe_jpg.rf.8c6f7ce142e9f3b3403d20c761ad1359.jpg`: GT `Bus:1`, prediction `Bus:1`. box localization quality requires manual visual inspection

These are good candidates because GT and prediction class counts match. Before publishing them as success examples, visually confirm that boxes are well localized and not duplicated.

## 7. False Positive Candidates

- `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg`: GT `Car:5; Truck:5; mini-truck:2`, prediction `Car:7; Truck:5; mini-truck:4`. possible false positives and Car/Truck/mini-truck class confusion; possible duplicate boxes; requires manual visual inspection.
- `adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg`: GT `Car:9; Truck:1; mini-truck:2`, prediction `Car:8; Truck:3; mini-truck:2`. possible Car versus Truck class confusion; small or distant vehicles may contribute; requires manual visual inspection.

These are possible false positive cases based on extra predicted objects or class-count shifts. Exact false-positive boxes require manual visual inspection.

## 8. False Negative Candidates

- `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg`: GT `Person:7`, prediction `Person:6`. possible Person false negative; crowding or occlusion; requires manual visual inspection.

The current sample has one clear image-level false negative candidate. The exact missed person location requires manual visual inspection.

## 9. Class Confusion: Car / Truck / mini-truck

The strongest class-confusion candidates are:

- `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg`: GT `Car:5; Truck:5; mini-truck:2`, prediction `Car:7; Truck:5; mini-truck:4`.
- `adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg`: GT `Car:9; Truck:1; mini-truck:2`, prediction `Car:8; Truck:3; mini-truck:2`.

These patterns suggest possible confusion between visually similar vehicle categories. Because the current analysis is label-count based, the exact source of the confusion requires manual visual inspection.

## 10. Person Crowding / Occlusion

The key Person review case is:

- `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg`: GT `Person:7`, prediction `Person:6`.

This is a likely false negative candidate in a crowded or occluded Person scene. The exact missed person requires manual visual inspection.

## 11. Limitations

This report is based on only 10 selected images. It is useful for qualitative inspection and README examples, but it cannot replace full test-set Precision, Recall, mAP50, or mAP50-95. Full metric claims should continue to rely on the saved validation outputs under `docs/colab_runs/yolov8n_640_50epochs/`.

## 12. Next Improvement Suggestions

- Expand the inference sample beyond 10 images.
- Use class-balanced sampling so Bus, Car, Motorcycle, Person, Truck, and mini-truck are all represented.
- Add more data or augmentation focused on mini-truck and visually similar vehicle categories.
- Try a larger model such as YOLOv8s after the image-level error analysis is complete.
- Finish image error analysis before moving to video inference, so the video stage has clearer failure categories to watch for.
