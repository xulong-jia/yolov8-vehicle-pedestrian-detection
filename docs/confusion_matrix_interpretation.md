# Confusion Matrix Interpretation

## Purpose

This document explains how to interpret confusion matrices for this vehicle and pedestrian detection project, with a focus on class confusion patterns observed in the project materials.

## Available Materials

- `docs/model_card.md`
- `docs/error_case_gallery/README.md`
- `docs/experiment_comparison.md`

The official confusion matrix image is not currently tracked in this repository and should be restored or recreated later.

## How to Read the Confusion Matrix

- Diagonal entries represent predictions where the predicted class matches the ground-truth class.
- Off-diagonal entries represent class confusion, where one class is predicted as another.
- False positives are detections that do not match a ground-truth object.
- False negatives are ground-truth objects that the model fails to detect.
- A normalized confusion matrix shows proportions rather than raw counts, making it easier to compare classes with different numbers of examples.

## Expected Confusion Patterns

- `Car` / `Truck` / `mini-truck` confusion is expected because these classes share visual features.
- Small objects may be missed and effectively counted as background errors.
- Crowded scenes can cause duplicate boxes or incorrect boxes.
- Visually similar vehicles can be confused when object size, viewpoint, or occlusion reduces detail.

## Interpretation Notes by Class

### Bus

Bus detections are expected to be easier when the object is large and clearly visible. Misses may occur when buses are small, occluded, or embedded in dense traffic.

### Car

Cars are frequent in traffic scenes. Confusion with `Truck` or `mini-truck` can occur when scale and shape are ambiguous.

### Motorcycle

Motorcycle is described as relatively strong in current project notes. Errors may still occur for small, occluded, or crowded motorcycle cases.

### Person

Person can perform well in clear scenes, but crowded or occluded person scenes can produce false positives, false negatives, or duplicate boxes.

### Truck

Truck can be confused with `Car` or `mini-truck`, especially in dense traffic or when only part of the vehicle is visible.

### mini-truck

mini-truck is a challenging class. It may be confused with both `Car` and `Truck` because of similar shape and ambiguous scale.

## Practical Actions

- inspect high-confusion class pairs
- build hard example list
- collect more mini-truck examples
- check annotation consistency
- compare confidence thresholds
- run same-split validation for future models
