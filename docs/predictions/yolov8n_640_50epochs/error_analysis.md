# YOLOv8n 640x640 50 Epoch Image Error Analysis

## 1. Inference Batch

- Model weights: `local_weights/yolov8n_640_50epochs/best.pt`
- Source images: `dataset/test/images`
- Ground-truth labels: `dataset/test/labels`
- Prediction output: `docs/predictions/yolov8n_640_50epochs/`
- Selection: 10 test images sampled with fixed random seed `42`
- Classes: `Bus, Car, Motorcycle, Person, Truck, mini-truck`
- Runtime noted in inference summary: local Mac CPU

This report is a first-pass qualitative review based on image-level class counts from GT labels and prediction labels. It does not replace visual inspection of boxes.

## 2. Overall Observations Across 10 Images

- 7 of 10 images have matching GT and prediction class counts at the image level.
- 3 of 10 images need manual review because class counts differ or the scene is dense.
- The simple Bus examples matched GT counts.
- Most single-person or low-density Person examples matched GT counts.
- The main error candidates are dense traffic scenes and one crowded pedestrian scene.

| Image | Case Type | GT Summary | Prediction Summary | Manual Review |
| --- | --- | --- | --- | --- |
| `1c4915190a748798_jpg.rf.0c265452437e4c470eee04c6c8a24fc9.jpg` | likely_correct | Bus:1 | Bus:1 | false |
| `train_all_data-579-_jpg.rf.def4d2fd636b5555d589f4c811a318c8.jpg` | likely_correct | Person:1 | Person:1 | false |
| `train_all_data-384-_jpg.rf.38f6abd346046f3f733765041fccda76.jpg` | likely_correct; crowded_scene | Person:3 | Person:3 | false |
| `train_all_data-426-_jpg.rf.948a4e4975dde76f075dfc6bb093a03a.jpg` | likely_correct | Person:2 | Person:2 | false |
| `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg` | possible_false_negative; crowded_scene; needs_manual_review | Person:7 | Person:6 | true |
| `train_all_data-216-_jpg.rf.78e2be2c9ec27d3ccf537dbfc1db5b13.jpg` | likely_correct | Person:1 | Person:1 | false |
| `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg` | possible_class_confusion; possible_false_positive; crowded_scene; needs_manual_review | Car:5; Truck:5; mini-truck:2 | Car:7; Truck:5; mini-truck:4 | true |
| `train_all_data-544-_jpg.rf.166f9aad86cbdf07a978dabf01a4f39c.jpg` | likely_correct | Person:1 | Person:1 | false |
| `adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg` | possible_class_confusion; possible_false_positive; crowded_scene; needs_manual_review | Car:9; Truck:1; mini-truck:2 | Car:8; Truck:3; mini-truck:2 | true |
| `0e568901d66ad81e46860b91cce2a7fe_jpg.rf.8c6f7ce142e9f3b3403d20c761ad1359.jpg` | likely_correct | Bus:1 | Bus:1 | false |

## 3. Three Priority Manual Review Images

### `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg`

- GT count: Person:7
- Prediction count: Person:6
- Possible issue: Prediction has one fewer Person than GT; likely missed pedestrian in a crowded or partially occluded person scene.
- Visual spot-check: pedestrians are small, partially occluded, and clustered near the image edge; useful for discussing missed Person detections under crowding and perspective distortion.
- Recommended action: open `docs/predictions/yolov8n_640_50epochs/train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg` and compare it with the source image and GT label file.

### `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg`

- GT count: Car:5; Truck:5; mini-truck:2
- Prediction count: Car:7; Truck:5; mini-truck:4
- Possible issue: Prediction has more Car and mini-truck boxes than GT while Truck count matches; likely vehicle over-detection or class confusion in a dense traffic scene.
- Visual spot-check: dense highway traffic with overlapping labels and several small or distant vehicles; useful for checking Car/Truck/mini-truck confusion and possible duplicate boxes.
- Recommended action: open `docs/predictions/yolov8n_640_50epochs/adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg` and compare it with the source image and GT label file.

### `adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg`

- GT count: Car:9; Truck:1; mini-truck:2
- Prediction count: Car:8; Truck:3; mini-truck:2
- Possible issue: Prediction has fewer Cars but more Trucks than GT; likely Car/Truck confusion in a dense vehicle scene.
- Visual spot-check: multiple close vehicles and far-away small objects make this a strong candidate for Car versus Truck review.
- Recommended action: open `docs/predictions/yolov8n_640_50epochs/adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg` and compare it with the source image and GT label file.

## 4. Possible False Positive Types

- Extra Car or mini-truck predictions in dense traffic scenes.
- Duplicate boxes around the same vehicle, especially when adjacent vehicles overlap.
- Vehicle type over-detection where a larger vehicle region may be split into multiple smaller predictions.

## 5. Possible False Negative Types

- Missed Person in crowded scenes, especially when people overlap or only part of the body is visible.
- Missed Car in dense traffic when the model assigns the object to Truck instead.
- Potential small-object misses should be checked visually because image-level counts cannot identify box size or localization quality.

## 6. Class Confusion Observations

The clearest class-confusion candidates are `Car`, `Truck`, and `mini-truck`:

- `adit_mp4-2159...` has extra Cars and mini-trucks while Truck count matches.
- `adit_mp4-1696...` has fewer Cars and more Trucks than GT, suggesting Car/Truck confusion.
- These cases should be reviewed visually to decide whether the issue is true class confusion, duplicate boxes, annotation ambiguity, or reasonable predictions where GT labels are incomplete.

## 7. README Display Image Selection

Good README success-case candidates should show clean, easy-to-understand detections with matching GT and prediction counts:

- `1c4915190a748798_jpg.rf.0c265452437e4c470eee04c6c8a24fc9.jpg` for Bus detection.
- `0e568901d66ad81e46860b91cce2a7fe_jpg.rf.8c6f7ce142e9f3b3403d20c761ad1359.jpg` for another Bus detection.
- `train_all_data-384-_jpg.rf.38f6abd346046f3f733765041fccda76.jpg` for multi-person detection if the boxes look clean after visual review.

Good README error-analysis candidates:

- `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg` for dense vehicle false positive or class confusion discussion.
- `adit_mp4-1696_jpg.rf.ceeb4a9d3bc8fd3cf40947ea4e97f388.jpg` for Car/Truck confusion discussion.
- `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg` for possible missed Person in a crowded scene.

## 8. Scope Note

This is a small-sample qualitative analysis of 10 selected test images. It does not represent full test-set Precision, Recall, mAP50, or mAP50-95. Full metric claims should continue to use the saved YOLO validation outputs under `docs/colab_runs/yolov8n_640_50epochs/`.
