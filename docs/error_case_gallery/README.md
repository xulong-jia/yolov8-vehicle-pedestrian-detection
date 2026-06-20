# Error Case Gallery

## Gallery Purpose

This gallery collects representative prediction images from the Day 6 50-sample YOLOv8n image inference run. It is intended for final report and PPT use, where a small number of clear examples can explain common model behaviors and error patterns.

The gallery uses existing predicted images only. It does not copy original dataset images and does not run new inference.

## Source

- Prediction directory: `docs/predictions/yolov8n_640_50epochs_50samples/`
- Day 6 report: `docs/predictions/yolov8n_640_50epochs_50samples/day6_50sample_error_analysis_report.md`
- Image-level analysis: `docs/predictions/yolov8n_640_50epochs_50samples/image_level_error_analysis.csv`
- Case summary: `docs/predictions/yolov8n_640_50epochs_50samples/error_case_summary.csv`

## How Cases Were Selected

Cases were selected to cover both successful detections and common qualitative error categories:

- `likely_correct`
- `possible_false_positive`
- `possible_false_negative`
- `possible_class_confusion`
- `possible_duplicate_boxes`
- `crowded_scene`
- `small_object_difficulty`
- Car / Truck / mini-truck confusion candidates

The labels are based on Day 6 image-level GT and prediction count comparisons. Exact object-level false positives, false negatives, duplicate boxes, and class confusion still require manual visual inspection.

## Bad Case Schema Alignment

The gallery table is aligned with the mainline Bad Case schema in
`docs/bad_cases_schema.md`. Gallery examples should use the same fields as
future `bad_cases.csv` records, including `module`, `case_type`, `root_cause`,
`tags`, `snapshot_path`, and `added_to_eval_set`.

The gallery is intentionally lightweight. Do not commit large images, videos,
model weights, `runs/`, or `local_outputs/` as evidence. Use small
documentation examples under `docs/error_case_gallery/images/` or external/local
paths described in text.

## Case Table

| Case | Image | Category | Suggested Caption |
| --- | --- | --- | --- |
| case_01 | `1c4915190a748798_jpg.rf.0c265452437e4c470eee04c6c8a24fc9.jpg` | likely_correct | Successful bus detection with matching GT and prediction count. |
| case_02 | `34910_png_jpg.rf.19d2a7325681540a581832591ad488aa.jpg` | likely_correct | Successful motorcycle detection with matching GT and prediction count. |
| case_03 | `train_all_data-76-_jpg.rf.9836117b1d78c2e79a4b56222f340e8d.jpg` | possible_false_positive; possible_duplicate_boxes; crowded_scene | Crowded person scene with extra predicted Person boxes. |
| case_04 | `train_all_data-453-_jpg.rf.4c2304c507aca33a59aaf5b10b827d01.jpg` | possible_false_negative; crowded_scene; small_object_difficulty | Crowded person scene with one fewer predicted Person than GT. |
| case_05 | `adit_mp4-205_jpg.rf.dd1e533fc256eb68f835e6bbdf38264d.jpg` | possible_class_confusion; crowded_scene; small_object_difficulty | Dense traffic case with possible Car, Truck, and mini-truck confusion. |
| case_06 | `adit_mp4-2681_jpg.rf.d67b726ee41f513a805b2f4bc8883e58.jpg` | possible_false_positive; possible_duplicate_boxes; crowded_scene; small_object_difficulty | Dense traffic case with many extra vehicle predictions. |
| case_07 | `adit_mp4-2159_jpg.rf.7b25c0dec528514c7a9ada98995d55f0.jpg` | possible_false_positive; possible_duplicate_boxes; crowded_scene; small_object_difficulty; mini-truck_truck_car_confusion | Dense vehicle scene with possible extra Car and mini-truck predictions. |
| case_08 | `ea3829da1bcc87ac_jpg.rf.7624b15ed6641b72a7e9cec61dc8d7a2.jpg` | possible_false_negative; crowded_scene; small_object_difficulty | Bus scene with fewer predicted Bus boxes than GT. |

## Short Interpretation

The successful examples show that the YOLOv8n baseline can detect clear single-object cases such as buses and motorcycles.

The error and difficulty cases concentrate around dense traffic, crowded person scenes, small objects, and visually similar vehicle classes. In particular, Car / Truck / mini-truck count shifts appear in multiple dense-traffic samples and are useful for explaining why the dataset may benefit from more balanced examples or a larger model.

## Qualitative Analysis Note

This gallery is qualitative analysis only. It is not official metric evaluation and should not be used as a replacement for Precision, Recall, mAP50, or mAP50-95.

## Limitations

- Case categories are based on image-level count comparison, not object-level IoU matching.
- Exact false-positive boxes, missed objects, duplicate boxes, and class-confusion locations require manual visual inspection.
- The selected examples come from a 50-image sample, not the full test set.
- Some predictions may be reasonable even when GT labels are incomplete or ambiguous.

## Related Files

- `docs/bad_cases_schema.md`
- `docs/bad_case_report.md`
- `docs/error_taxonomy.md`
- `docs/hard_examples.md`
