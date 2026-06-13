# Day 6 50-Sample Image Inference and Error Analysis

## 1. Analysis Goal

Day 6 expands the qualitative image inference sample from 10 images to 50 images. The goal is to build a more stable pool of success examples, false-positive candidates, false-negative candidates, and class-confusion cases for README and project-report use.

## 2. Sample Source

- Image source: `dataset/test/images`
- Ground-truth labels: `dataset/test/labels`
- Class mapping: `dataset/data.yaml`
- Selection method: fixed random seed `42`
- Sample size: 50 images
- Selected image list: `docs/predictions/yolov8n_640_50epochs_50samples/selected_images.txt`

## 3. Model Configuration

- Model: YOLOv8n 640x640 50 epoch baseline
- Weights: `local_weights/yolov8n_640_50epochs/best.pt`

## 4. Inference Settings

- Runtime: local Mac CPU (`device=cpu`; CUDA and MPS unavailable)
- Confidence threshold: `0.25`
- Output directory: `docs/predictions/yolov8n_640_50epochs_50samples/`
- Outputs: 50 prediction visualization images and YOLO prediction labels under `labels/`

## 5. Overall Observations

| Case Type | Count | Notes |
| --- | ---: | --- |
| `likely_correct` | 28 | GT and prediction class counts match at image level; box quality still requires visual inspection. |
| `possible_false_positive` | 16 | At least one class has more predictions than GT; exact boxes require manual visual inspection. |
| `possible_false_negative` | 10 | At least one class has fewer predictions than GT; exact missed objects require manual visual inspection. |
| `possible_class_confusion` | 4 | Vehicle class-count shifts suggest possible Car / Truck / mini-truck confusion. |
| `possible_duplicate_boxes` | 14 | Prediction total exceeds GT total; duplicate-box status requires manual visual inspection. |
| `crowded_scene` | 22 | GT or prediction total is at least 4 objects, indicating a crowded or dense scene. |
| `small_object_difficulty` | 15 | At least one GT object has normalized area below 0.01; object-level impact requires visual inspection. |
| `needs_manual_review` | 23 | Count mismatch, vehicle shift, or small-object flag requires manual visual inspection. |


Overall, `28` of 50 images have matching GT and prediction class counts. `23` images are flagged for manual review because of count mismatches, vehicle class shifts, or small-object difficulty flags.

## 6. Successful Detection Cases

Recommended success-case candidates:

- `03e8bc2333105e66_jpg.rf.47db733d08b4019199ac9d2c7c0fcf80.jpg`: GT `Bus:1`, prediction `Bus:1`. no image-level count mismatch detected
- `0e568901d66ad81e46860b91cce2a7fe_jpg.rf.8c6f7ce142e9f3b3403d20c761ad1359.jpg`: GT `Bus:1`, prediction `Bus:1`. no image-level count mismatch detected
- `1c4915190a748798_jpg.rf.0c265452437e4c470eee04c6c8a24fc9.jpg`: GT `Bus:1`, prediction `Bus:1`. no image-level count mismatch detected
- `34910_png_jpg.rf.19d2a7325681540a581832591ad488aa.jpg`: GT `Motorcycle:1`, prediction `Motorcycle:1`. no image-level count mismatch detected
- `train_all_data-216-_jpg.rf.78e2be2c9ec27d3ccf537dbfc1db5b13.jpg`: GT `Person:1`, prediction `Person:1`. no image-level count mismatch detected

These images are good README candidates because their GT and prediction class counts match. Box placement and visual clarity still require manual visual inspection before final publication.

## 7. False Positive Candidate Cases

- `adit_mp4-2681_jpg.rf.d67b726ee41f513a805b2f4bc8883e58.jpg`: GT `Car:9; Truck:4; mini-truck:2`, prediction `Car:14; Truck:8; mini-truck:3`. possible false positives or duplicate boxes; requires manual visual inspection
- `train_all_data-76-_jpg.rf.9836117b1d78c2e79a4b56222f340e8d.jpg`: GT `Person:10`, prediction `Person:17`. possible false positives or duplicate boxes; requires manual visual inspection
- `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg`: GT `Car:5; Truck:5; mini-truck:2`, prediction `Car:7; Truck:5; mini-truck:4`. possible false positives or duplicate boxes; requires manual visual inspection
- `siang_15112021_1_mp4-300_jpg.rf.7aaec814ddbfeb4535dce7820779a800.jpg`: GT `Car:3; Truck:4`, prediction `Car:4; Truck:5; mini-truck:2`. possible false positives or duplicate boxes; requires manual visual inspection
- `adit_mp4-205_jpg.rf.dd1e533fc256eb68f835e6bbdf38264d.jpg`: GT `Bus:1; Car:6; Truck:4; mini-truck:4`, prediction `Bus:1; Car:7; Truck:5; mini-truck:3`. possible class confusion among Car / Truck / mini-truck; requires manual visual inspection

These are count-based candidates. Exact false-positive locations require manual visual inspection.

## 8. False Negative Candidate Cases

- `adit_mp4-205_jpg.rf.dd1e533fc256eb68f835e6bbdf38264d.jpg`: GT `Bus:1; Car:6; Truck:4; mini-truck:4`, prediction `Bus:1; Car:7; Truck:5; mini-truck:3`. possible class confusion among Car / Truck / mini-truck; requires manual visual inspection

These are count-based candidates. Exact missed-object locations require manual visual inspection.

## 9. Class Confusion: Car / Truck / mini-truck

- `adit_mp4-205_jpg.rf.dd1e533fc256eb68f835e6bbdf38264d.jpg`: GT `Bus:1; Car:6; Truck:4; mini-truck:4`, prediction `Bus:1; Car:7; Truck:5; mini-truck:3`. possible class confusion among Car / Truck / mini-truck; requires manual visual inspection

The class-confusion flag is assigned only from class-count shifts in vehicle classes. It does not prove exact object-level confusion; it requires manual visual inspection.

## 10. Person Crowding / Occlusion

- `train_all_data-76-_jpg.rf.9836117b1d78c2e79a4b56222f340e8d.jpg`: GT `Person:10`, prediction `Person:17`. possible false positives or duplicate boxes; requires manual visual inspection
- `train_all_data-452-_jpg.rf.47ba3b5cb80a216004d5dd27b33600de.jpg`: GT `Person:9`, prediction `Person:10`. possible false positives or duplicate boxes; requires manual visual inspection
- `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg`: GT `Person:7`, prediction `Person:6`. possible false negatives; requires manual visual inspection
- `train_all_data-420-_jpg.rf.decc75d13fb3f37ea5c20532a53723a3.jpg`: GT `Person:5`, prediction `Person:6`. possible false positives or duplicate boxes; requires manual visual inspection
- `train_all_data-516-_jpg.rf.7f22529632a59b16c5450f5b8f073bbf.jpg`: GT `Person:5`, prediction `Person:3`. possible false negatives; requires manual visual inspection

Person crowding and occlusion cannot be confirmed from label counts alone. Each listed sample requires manual visual inspection.

## 11. Comparison With Day 5 10-Sample Analysis

Day 6 is more stable than Day 5 because it uses 50 images instead of 10, reducing the chance that a single image dominates the qualitative conclusions. The broader sample gives more examples for README and report selection.

| Case Type | Day 5 Count (10 images) | Day 6 Count (50 images) |
| --- | ---: | ---: |
| `likely_correct` | 7 | 28 |
| `possible_false_positive` | 2 | 16 |
| `possible_false_negative` | 1 | 10 |
| `possible_class_confusion` | 2 | 4 |
| `possible_duplicate_boxes` | 0 | 14 |
| `crowded_scene` | 4 | 22 |
| `small_object_difficulty` | 0 | 15 |
| `needs_manual_review` | 3 | 23 |

Even with 50 images, this is still a qualitative sample and not a replacement for full validation metrics.

## 12. Limitations

The 50-image sample is still a qualitative subset. It does not replace full test-set Precision, Recall, mAP50, or mAP50-95. Count-based comparison also cannot locate exact false-positive boxes, exact missed objects, or exact duplicate boxes. Those findings require manual visual inspection.

## 13. Next Recommendations

- Run video inference after the image-level error categories are clear.
- Compare against a larger model such as YOLOv8s.
- Add data or augmentation for visually similar vehicle categories, especially mini-truck.
- Use class-balanced sampling for future image batches.
- Continue separating qualitative examples from full test-set metric claims.
