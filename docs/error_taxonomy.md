# Error Taxonomy

## Purpose

This document defines a shared error taxonomy for the YOLOv8 vehicle and pedestrian detection project. The goal is to make future error analysis, hard example mining, threshold review, and model improvement experiments more consistent.

The labels below are intended for qualitative review. They do not replace official validation metrics such as Precision, Recall, mAP50, or mAP50-95.

## Error Categories

### 1. False Positive

**Definition:** The model predicts an object that is not present in the ground-truth annotation or is not a valid target object.

**Typical examples:**

- Extra Person boxes in crowded pedestrian scenes.
- Extra Car, Truck, or mini-truck boxes in dense traffic.
- Background regions detected as vehicles or pedestrians.

**Possible causes:**

- Visually cluttered scenes.
- Incomplete or ambiguous annotations.
- Overlapping objects that are difficult to separate.
- Confidence threshold set too low for a strict visualization use case.

**Suggested actions:**

- Manually inspect high-confidence false-positive candidates.
- Compare results at different confidence thresholds.
- Check annotation completeness for crowded scenes.
- Add hard negative examples if the pattern is consistent.

### 2. False Negative

**Definition:** A ground-truth object is present but the model does not predict a matching box.

**Typical examples:**

- Missed Person instances in crowded or partially occluded scenes.
- Missed Bus or vehicle objects when they are small, distant, or partly truncated.
- Objects missed at higher confidence thresholds.

**Possible causes:**

- Small object size.
- Occlusion by other objects.
- Low visual contrast.
- Limited examples for difficult poses, scales, or viewpoints.

**Suggested actions:**

- Build a hard examples list for missed objects.
- Check whether labels are complete and consistent.
- Evaluate threshold trade-offs before increasing confidence.
- Consider targeted augmentation or larger image sizes in future experiments.

### 3. Class Confusion

**Definition:** The model detects an object but assigns the wrong class.

**Special focus: Car / Truck / mini-truck**

Car, Truck, and mini-truck can share similar shapes, sizes, camera angles, and traffic context. Count shifts among these classes are a recurring qualitative pattern in the current error gallery.

**Possible causes:**

- Visually similar vehicle shapes.
- Ambiguous class definitions.
- Class imbalance.
- Scale and perspective changes.
- Inconsistent annotations between Truck and mini-truck.

**Suggested actions:**

- Review class definitions and annotation examples.
- Inspect high-confusion vehicle pairs manually.
- Add more mini-truck and borderline vehicle examples.
- Compare YOLOv8n and larger models on the same split if weights are available.

### 4. Duplicate Boxes

**Definition:** The model predicts multiple boxes for the same object.

**Possible relation to NMS / crowded scenes:**

Duplicate boxes may appear when objects overlap, when the model is uncertain about object boundaries, or when non-maximum suppression does not fully merge nearby predictions.

**Suggested actions:**

- Inspect duplicate candidates in crowded scenes.
- Compare confidence and IoU threshold settings.
- Check whether apparent duplicates are actually adjacent objects.
- Keep duplicate candidates separate from confirmed false positives until manual review.

### 5. Small Object Difficulty

**Definition:** The model struggles with objects that occupy a small image area.

**Possible causes:**

- Limited pixel detail after resizing.
- Motion blur or compression artifacts.
- Distant traffic or pedestrians.
- Small objects mixed with dense background clutter.

**Suggested actions:**

- Review small-object examples manually.
- Try larger image sizes in future ablation experiments.
- Add targeted data augmentation for small objects.
- Track small-object cases separately from general false negatives.

### 6. Crowded Scene Difficulty

**Definition:** Detection quality degrades when many objects appear close together in the same image.

**Possible causes:**

- Heavy overlap between boxes.
- Occlusion.
- Similar object appearances.
- Annotation ambiguity in dense traffic or pedestrian scenes.

**Suggested actions:**

- Group crowded scenes as a dedicated review subset.
- Check for duplicate boxes and missed objects.
- Review NMS and confidence settings.
- Consider larger models or higher-resolution inference in future experiments.

### 7. Occlusion / Truncation

**Definition:** An object is partly hidden by another object or cut off by the image boundary.

**Possible causes:**

- Objects behind vehicles, poles, or pedestrians.
- Cropped objects at image edges.
- Traffic scenes with overlapping vehicles.
- Incomplete visual evidence for the class.

**Suggested actions:**

- Label occluded and truncated examples during manual review.
- Check whether annotations are consistent for partial objects.
- Add more examples of partial objects if they are important for the use case.
- Avoid treating every partial-object miss as a model failure without checking annotation policy.

### 8. Low Confidence Correct Detection

**Definition:** The model predicts a correct object, but with confidence close to the chosen threshold.

**Why this matters for threshold tuning:**

Increasing the confidence threshold may remove low-confidence false positives, but it can also remove correct detections. This is especially important for small, occluded, or visually ambiguous objects.

**Suggested actions:**

- Inspect correct low-confidence detections before raising thresholds.
- Compare threshold settings on a representative subset.
- Use Precision and Recall metrics when available instead of relying only on box counts.
- Document threshold choices by use case.

## Suggested Review Labels

- `likely_correct`
- `possible_false_positive`
- `possible_false_negative`
- `possible_class_confusion`
- `possible_duplicate_boxes`
- `crowded_scene`
- `small_object_difficulty`
- `occlusion_or_truncation`
- `low_confidence_correct_detection`
- `needs_manual_review`

## Bad Case Schema Alignment

`v0.14.0` introduces the mainline Bad Case schema in
`docs/bad_cases_schema.md`. The schema keeps error attribution explicit with a
`module` field and a controlled `case_type` field.

Allowed `module` values:

- `detector`
- `tracker`
- `counter`
- `roi`
- `event`
- `api`
- `streamlit`
- `dataset`
- `deployment`
- `documentation`

Allowed `case_type` values:

- `false_positive`
- `false_negative`
- `class_confusion`
- `localization_error`
- `duplicate_detection`
- `missed_track`
- `id_switch`
- `fragmented_track`
- `count_error`
- `line_crossing_error`
- `roi_config_error`
- `rule_error`
- `api_contract_error`
- `data_quality_issue`
- `deployment_issue`
- `documentation_gap`

This taxonomy remains qualitative. The schema provides the stable CSV contract
for future reviewed cases and API work.

## Related Files

- `docs/bad_cases_schema.md`
- `docs/bad_case_report.md`
- `docs/error_case_gallery/README.md`
- `docs/error_case_gallery/cases.csv`
- `docs/per_class_failure_analysis.md`
- `docs/confusion_matrix_interpretation.md`
