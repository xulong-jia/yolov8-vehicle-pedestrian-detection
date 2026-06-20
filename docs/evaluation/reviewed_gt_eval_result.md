# Reviewed GT Evaluation Result

## Scope

`v1.7.0-gt-quantitative-evaluation` adds a small reviewed GT quantitative
evaluation sample pack. It demonstrates the full lightweight loop:

1. reviewed GT CSV samples
2. reviewed prediction CSV samples
3. `src.evaluation.video_eval_scaffold`
4. metrics CSV files
5. `evaluation_summary.json`
6. this reviewed result report

This is a small documentation-grade sample, not a production benchmark. It does
not run YOLO, ByteTrack, DeepSORT, Docker, analytics, rendering, or any
large-scale inference. It does not add model weights, videos, large images,
`runs`, `local_outputs`, sqlite files, or runtime artifacts.

## Input Samples

Reviewed sample inputs live under
`docs/evaluation/reviewed_gt_samples/`:

- `counting_gt.csv`
- `counting_pred.csv`
- `roi_gt.csv`
- `roi_pred.csv`
- `event_gt.csv`
- `event_pred.csv`
- `tracking_gt.csv`
- `tracking_pred.csv`

The rows are intentionally small and reference reviewed Bad Case contexts such
as `RBC-0011`, `RBC-0014`, and `RBC-0019` in reviewer notes. They do not
reference `local_outputs`, `local_weights`, `runs`, absolute file paths,
weights, videos, or zip archives.

## Reproduction Command

```bash
python -m src.evaluation.video_eval_scaffold \
  --pred-tracks docs/evaluation/reviewed_gt_samples/tracking_pred.csv \
  --pred-count-events docs/evaluation/reviewed_gt_samples/counting_pred.csv \
  --pred-roi-counts docs/evaluation/reviewed_gt_samples/roi_pred.csv \
  --pred-events docs/evaluation/reviewed_gt_samples/event_pred.csv \
  --gt-tracks docs/evaluation/reviewed_gt_samples/tracking_gt.csv \
  --gt-count-events docs/evaluation/reviewed_gt_samples/counting_gt.csv \
  --gt-roi-counts docs/evaluation/reviewed_gt_samples/roi_gt.csv \
  --gt-events docs/evaluation/reviewed_gt_samples/event_gt.csv \
  --output-dir docs/evaluation/reviewed_gt_eval_result
```

The committed result files are lightweight reviewed sample artifacts:

- `docs/evaluation/reviewed_gt_eval_result/evaluation_summary.json`
- `docs/evaluation/reviewed_gt_eval_result/counting_metrics.csv`
- `docs/evaluation/reviewed_gt_eval_result/roi_metrics.csv`
- `docs/evaluation/reviewed_gt_eval_result/event_metrics.csv`
- `docs/evaluation/reviewed_gt_eval_result/tracking_metrics.csv`

## Metrics Summary

| Metric group | Result |
| --- | --- |
| counting | `gt_count=9`, `pred_count=10`, `abs_error=1`, `MAE=1.0` |
| ROI | `compared_rows=4`, `frame_count_mae=1.0` |
| events | `gt_events=3`, `pred_events=4`, `matched_events=2`, `precision=0.5`, `recall=0.6666666666666666` |
| tracking | `track_count=5`, `avg_track_length=2.0`, `short_track_ratio=0.6`, `gt_required_for_idf1=true` |

## Event Matching Rule

The event scaffold uses a minimal reviewed-sample rule:

- same `event_type`
- `timestamp_sec` within `1.0` second

This is sufficient for a small sample sanity check. It is not a replacement for
a production event evaluation protocol.

## Tracking Metric Limitation

The tracking output reports engineering metrics only:

- `track_count`
- `avg_track_length`
- `short_track_ratio`

The summary explicitly keeps `gt_required_for_idf1=true`. Full MOT metrics such
as IDF1 or MOTA are not implemented in this phase and require a larger reviewed
tracking GT set plus a formal matching protocol.

## Interpretation

The sample proves that reviewed GT rows and prediction rows can flow through the
current evaluation scaffold and produce parseable metrics. It is useful for
final demonstration, report review, and future evaluation planning.

It does not claim:

- large-scale GT quantitative evaluation
- production benchmark status
- complete MOT IDF1/MOTA
- full real video validation
- model performance improvement
