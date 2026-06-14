# Per-Class Failure Analysis

## Purpose

This document summarizes the main failure modes for the six detection classes in the project. It is based on existing qualitative analysis and tracked project documents, without running new training or inference.

## Source Materials

- `docs/error_case_gallery/README.md`
- `docs/error_case_gallery/cases.csv`
- `docs/predictions/yolov8n_640_50epochs/`
- `docs/predictions/yolov8n_640_50epochs_50samples/`
- `docs/model_card.md`
- `docs/experiment_comparison.md`

## Class-by-Class Notes

### Bus

- Observed behavior: Bus examples include successful single-object detections and missed-count candidates in qualitative samples.
- Common failure modes: missed buses in crowded or small-object scenes.
- Likely causes: scale variation, partial visibility, and scene density.
- Possible improvements: add more varied bus examples, inspect missed bus cases, and include hard examples in future analysis.

### Car

- Observed behavior: Cars are common in dense traffic samples and often appear near visually similar vehicle classes.
- Common failure modes: false positives, duplicate boxes, and confusion with `Truck` or `mini-truck`.
- Likely causes: dense scenes, partial occlusion, similar vehicle shape, and small object size.
- Possible improvements: improve vehicle class definitions, add hard examples for dense traffic, and evaluate threshold settings.

### Motorcycle

- Observed behavior: Motorcycle is described as relatively strong in current model notes and available comparison materials.
- Common failure modes: small-object misses and possible duplicate detections in crowded scenes.
- Likely causes: small scale, motion blur, occlusion, and overlapping objects.
- Possible improvements: inspect small motorcycle examples and include more difficult viewpoints if expanding the dataset.

### Person

- Observed behavior: Person is described as relatively strong, but crowded person scenes appear in the error gallery.
- Common failure modes: false positives, false negatives, and duplicate boxes in crowded or occluded scenes.
- Likely causes: overlapping people, occlusion, small object size, and pose variation.
- Possible improvements: add crowded-scene examples, review annotation consistency, and tune thresholds for crowded scenes.

### Truck

- Observed behavior: Truck appears in dense traffic samples with frequent interaction with `Car` and `mini-truck`.
- Common failure modes: class confusion with `Car` and `mini-truck`, plus duplicate boxes in dense scenes.
- Likely causes: similar vehicle shape, ambiguous scale, and partial occlusion.
- Possible improvements: define clearer visual boundaries between vehicle categories and build a hard examples list for vehicle confusion.

### mini-truck

- Observed behavior: mini-truck is described as the most challenging class in current project notes.
- Common failure modes: confusion with `Car` or `Truck`, missed detections, and extra predictions in dense vehicle scenes.
- Likely causes: visual similarity to larger trucks and cars, smaller object size, and class imbalance.
- Possible improvements: collect more mini-truck examples, review class definitions, use targeted augmentation, and compare larger models on the same split.

## Cross-Class Confusions

### Car vs Truck

`Car` and `Truck` may be confused when vehicles are partially visible, far from the camera, or similar in shape from the camera angle.

### Truck vs mini-truck

`Truck` and `mini-truck` confusion is expected when scale is ambiguous or when vehicle bodies have similar box-like shapes.

### Car vs mini-truck

`Car` and `mini-truck` confusion can appear in dense traffic scenes where object scale, perspective, and partial occlusion reduce visual detail.

## Scene-Level Factors

- crowded scenes
- small objects
- occlusion
- perspective and scale variation
- similar vehicle shapes

## Improvement Ideas

- more balanced data
- hard example mining
- better class definitions
- threshold tuning
- larger model comparison
- image size ablation
- targeted augmentation
