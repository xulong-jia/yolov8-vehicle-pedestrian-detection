# Confidence Threshold Analysis

## Purpose

This document summarizes how different confidence thresholds affect prediction volume for the YOLOv8n 640x640 50-epoch baseline. It is intended to support qualitative error analysis and threshold selection discussions.

This report does not run new inference and does not recompute official metrics.

## Source Data

The numbers below are existing project records for full test set inference at three confidence thresholds. The corresponding full summary artifact is referenced in project notes but may not be fully tracked in the repository.

Because this analysis only compares prediction volume, it should not be interpreted as a full Precision / Recall threshold benchmark.

## Summary Table

| Confidence | Predicted Images | Images with Detections | Images without Detections | Total Boxes | Avg Boxes per Image |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0.25 | 396 | 394 | 2 | 1847 | 4.66 |
| 0.40 | 396 | 391 | 5 | 1619 | 4.09 |
| 0.60 | 396 | 388 | 8 | 1328 | 3.35 |

## Observations

- Higher confidence thresholds reduce the total number of predicted boxes.
- Fewer predicted boxes may reduce false positives in visual demos or manual review workflows.
- Higher thresholds may also remove correct low-confidence detections and increase missed detections.
- The number of images without detections increases as the threshold rises.
- Threshold choice depends on the use case and should be interpreted together with qualitative examples and official metrics.

## Practical Recommendation

- Use `conf=0.25` for broader recall and qualitative review where missing objects is more costly.
- Use `conf=0.40` as a balanced candidate for manual inspection or demo settings.
- Use `conf=0.60` for stricter high-confidence visualization when fewer boxes are preferred.

These recommendations are not final optimal thresholds. A strict threshold benchmark would require recomputing Precision, Recall, and mAP at each threshold on the same evaluation split.

## Related Files

- `docs/model_card.md`
- `docs/per_class_failure_analysis.md`
- `docs/error_taxonomy.md`
- `docs/project_task_board.md`
