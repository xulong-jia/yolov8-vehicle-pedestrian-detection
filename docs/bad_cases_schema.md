# Bad Case Schema

This document defines the mainline Bad Case data contract required by the
YOLOv8 final execution manual. It is a schema foundation for future review,
regression, and API work; it does not represent a complete real-world error
set.

`bad_cases.csv` should stay lightweight and review-driven. Do not generate or
commit bulk prediction outputs as Bad Case data.

## bad_cases.csv Required Fields

| Field | Required | Description |
| --- | --- | --- |
| `case_id` | yes | Stable unique ID, for example `BC-0001`. |
| `module` | yes | Error attribution module. |
| `case_type` | yes | Error type. |
| `image_name` | yes | Image sample name; may be empty for video-only cases. |
| `video_id` | yes | Video ID; may be empty for image-only cases. |
| `frame_index` | yes | Frame number; may be empty for image-only cases. |
| `timestamp_sec` | yes | Video timestamp in seconds; may be empty for image-only cases. |
| `track_id` | yes | Tracking ID; may be empty when no track is involved. |
| `expected_result` | yes | Human-expected result. |
| `actual_result` | yes | Model or system output. |
| `root_cause` | yes | Initial root-cause analysis. |
| `tags` | yes | Comma-separated labels. |
| `snapshot_path` | yes | Screenshot or example path; may be empty. |
| `added_to_eval_set` | yes | `yes` or `no`. |
| `created_at` | yes | UTC creation timestamp. |

## reviewed_bad_cases.csv Extension

`docs/error_case_gallery/reviewed_bad_cases.csv` is a small reviewed sample
collection for demonstration and manual review. It uses the same required
fields as `bad_cases.csv` and adds:

| Field | Required | Description |
| --- | --- | --- |
| `review_status` | yes | Manual review state. The current documented sample uses `reviewed`. |
| `reviewer_note` | yes | Short reviewer note explaining why the case is useful. |

The reviewed sample is intentionally small, metadata-only, and limited to
existing lightweight gallery images. It is not a production-scale Bad Case
dataset and does not include new large images, videos, generated outputs, or
model artifacts.

## Local Collection Paths

The runtime Bad Case service writes metadata-only records to ignored local
paths by default:

- `local_outputs/bad_cases/bad_cases.csv`
- `local_outputs/bad_cases/bad_cases.jsonl`

These files are collection artifacts and must not be committed. They can be
reviewed, filtered, and later promoted into a deliberately small documented
sample if needed.

## Allowed module

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

## Allowed case_type

- `false_positive`
- `false_negative`
- `class_confusion`
- `localization_error`
- `duplicate_detection`
- `missed_track`
- `id_switch`
- `fragmented_track`
- `track_lost`
- `count_error`
- `line_crossing_error`
- `roi_membership_error`
- `roi_config_error`
- `rule_error`
- `threshold_error`
- `api_contract_error`
- `data_quality_issue`
- `deployment_issue`
- `documentation_gap`

## Recommended tags

- `small_object`
- `occlusion`
- `motion_blur`
- `crowded_scene`
- `night_scene`
- `low_resolution`
- `reflection`
- `unusual_viewpoint`
- `bus_person_overlap`
- `long_stay`
- `roi_boundary`
- `line_boundary`
- `synthetic_case`
- `real_video_case`
- `needs_relabeling`
- `needs_threshold_tuning`
- `needs_tracking_tuning`
- `added_to_regression`

## Minimal CSV Example

```csv
case_id,module,case_type,image_name,video_id,frame_index,timestamp_sec,track_id,expected_result,actual_result,root_cause,tags,snapshot_path,added_to_eval_set
BC-0001,detector,false_positive,sample.jpg,,,,,No extra Person,Extra Person box,crowded scene and low threshold,"crowded_scene,needs_threshold_tuning",docs/error_case_gallery/images/sample.jpg,no
```

## Asset Policy

- `snapshot_path` should point only to small documentation examples under
  `docs/error_case_gallery/`, or to an external/local path described in text.
- Do not commit large images, videos, model weights, generated run directories,
  or local output directories as Bad Case evidence.
- `added_to_eval_set` is only a review marker. It does not automatically copy
  data into a dataset split or regression set.
- `/api/bad-cases` supports lightweight metadata create/list operations.
- Full reviewed Bad Case collection and evaluation API endpoints remain future
  phases.

## Related Files

- `docs/bad_case_report.md`
- `docs/error_taxonomy.md`
- `docs/hard_examples.md`
- `docs/error_case_gallery/README.md`
- `docs/error_case_gallery/cases.csv`
- `docs/error_case_gallery/reviewed_bad_cases.csv`
