# Video Analytics GT Templates

This document defines lightweight Ground Truth templates for future manual
tracking, counting, ROI, and event evaluation. These templates are contracts for
small reviewed CSV files; they are not generated prediction artifacts and they
do not require real YOLO or ByteTrack execution.

Recommended local working path:

- `local_outputs/evaluation/gt/`

Do not commit local GT drafts, large videos, generated prediction CSV files, or
bulk evaluation outputs unless a deliberately small documentation sample is
approved.

## Tracking GT Template

Use this template when object identity is manually reviewed across frames.

```csv
video_id,frame_index,timestamp_sec,gt_track_id,class_name,xmin,ymin,xmax,ymax,visibility,notes
demo,1,0.033,gt_1,Person,100,120,150,220,visible,example row
```

Recommended columns:

- `video_id`
- `frame_index`
- `timestamp_sec`
- `gt_track_id`
- `class_name`
- `xmin`
- `ymin`
- `xmax`
- `ymax`
- `visibility`
- `notes`

`src.evaluation.video_eval_scaffold` currently reports engineering tracking
metrics from prediction tracks. IDF1/MOTA style metrics require this GT template
and are intentionally marked `gt_required_for_idf1=true` until a reviewed GT set
exists.

## Counting GT Template

Use this template for line-count or aggregate count comparison.

```csv
video_id,line_id,class_name,direction,count,notes
demo,crosswalk_line,Person,forward,12,example row
```

Minimum fields used by the scaffold:

- `count`

Recommended fields:

- `video_id`
- `line_id`
- `class_name`
- `direction`
- `count`
- `notes`

The scaffold reports `gt_count`, `pred_count`, `abs_error`, and `MAE`.

## ROI GT Template

Use this template for frame-level ROI occupancy comparison.

```csv
video_id,roi_id,frame_index,class_name,count,notes
demo,crosswalk_roi,10,Person,3,example row
```

Minimum fields used by the scaffold:

- `video_id`
- `roi_id`
- `frame_index`
- `count`

The scaffold reports `frame_count_mae` and `compared_rows`.

## Event GT Template

Use this template for reviewed event occurrence comparison.

```csv
event_id,event_type,video_id,frame_index,timestamp_sec,track_id,class_name,roi_id,line_id,severity,notes
gt_evt_1,wrong_direction,demo,90,3.0,12,Person,,crosswalk_line,warning,example row
```

For the current scaffold, JSONL is also supported for predicted and GT event
inputs. CSV event inputs are also supported for small reviewed samples. The
minimal matching rule is:

- same `event_type`
- absolute `timestamp_sec` difference within the configured time window

The scaffold reports `gt_events`, `pred_events`, `matched_events`, `precision`,
and `recall`.

## Evaluation CLI

```bash
python -m src.evaluation.video_eval_scaffold \
  --pred-tracks /tmp/run/tracks.csv \
  --pred-count-events /tmp/run/count_events.csv \
  --pred-roi-counts /tmp/run/roi_frame_counts.csv \
  --pred-events /tmp/run/events.jsonl \
  --gt-count-events /tmp/gt/count_events.csv \
  --gt-roi-counts /tmp/gt/roi_frame_counts.csv \
  --gt-events /tmp/gt/events.jsonl \
  --output-dir /tmp/eval_scaffold
```

Outputs:

- `evaluation_summary.json`
- `counting_metrics.csv`
- `roi_metrics.csv`
- `event_metrics.csv`
- `tracking_metrics.csv`

Keep these outputs local unless a small reviewed sample is intentionally added
as documentation.

## Reviewed GT Sample Pack

`v1.7.0-gt-quantitative-evaluation` adds a small reviewed sample pack under:

- `docs/evaluation/reviewed_gt_samples/`
- `docs/evaluation/reviewed_gt_eval_result/`
- `docs/evaluation/reviewed_gt_eval_result.md`

The sample pack includes lightweight CSV files for counting, ROI, events, and
tracking. It demonstrates a reviewable GT-to-prediction-to-metrics loop using
`src.evaluation.video_eval_scaffold`.

The reviewed sample result is:

- counting: `gt_count=9`, `pred_count=10`, `abs_error=1`, `MAE=1.0`
- ROI: `compared_rows=4`, `frame_count_mae=1.0`
- events: `gt_events=3`, `pred_events=4`, `matched_events=2`,
  `precision=0.5`, `recall=0.6666666666666666`
- tracking: `track_count=5`, `avg_track_length=2.0`,
  `short_track_ratio=0.6`, `gt_required_for_idf1=true`

This is not a large benchmark, does not include complete MOT IDF1/MOTA, and
does not replace production GT evaluation.
