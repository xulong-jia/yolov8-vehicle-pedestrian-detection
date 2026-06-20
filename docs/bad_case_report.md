# Bad Case Report

## Current Status

The project now has the minimum Bad Case foundation required by the YOLOv8
final execution manual:

- taxonomy exists in `docs/error_taxonomy.md`
- hard examples exist in `docs/hard_examples.md`
- error case gallery exists in `docs/error_case_gallery/README.md`
- v0.14.0 adds the unified `bad_cases.csv` schema in
  `docs/bad_cases_schema.md`

This report is a foundation document. It does not claim that a complete real
Bad Case dataset has already been collected or fully labeled.

## Bad Case Classification Summary

| Module group | Covered case types |
| --- | --- |
| detector | `false_positive`, `false_negative`, `class_confusion`, `localization_error`, `duplicate_detection` |
| tracker | `missed_track`, `id_switch`, `fragmented_track` |
| counter | `count_error`, `line_crossing_error` |
| roi | `roi_config_error` |
| event | `rule_error` |
| api / deployment / docs | `api_contract_error`, `deployment_issue`, `documentation_gap` |
| dataset | `data_quality_issue` |

## Relationship to Existing Modules

- detector Bad Cases map to image prediction and video prediction behavior.
- tracker Bad Cases map to ByteTrack `track_id` behavior and `tracks.csv`.
- counter, ROI, and event Bad Cases map to analytics rules and their CSV/JSONL
  outputs.
- API Bad Cases map to FastAPI endpoint contracts and response schemas.
- deployment Bad Cases map to Docker, mounted weights, and deployment docs.
- documentation Bad Cases capture missing or misleading operator guidance.

Video Analysis Center artifacts can be linked to Bad Cases with `video_id`,
`frame_index`, `timestamp_sec`, and `track_id`. Image-only cases can leave the
video and tracking fields empty.

## Existing Sources

- `docs/error_taxonomy.md` defines qualitative error categories.
- `docs/hard_examples.md` identifies representative cases for future review.
- `docs/error_case_gallery/README.md` describes selected lightweight examples.
- `docs/error_case_gallery/cases.csv` is a small hand-written gallery sample
  aligned to the `bad_cases.csv` schema.

The gallery and hard examples are sources for review. They are not a complete
`bad_cases.csv` dataset.

## Minimum Acceptance Criteria

- Bad Case schema exists and documents required fields.
- Bad Case taxonomy exists and is linked to the schema.
- Gallery and hard examples link back to the schema/report.
- Root-cause analysis is represented by `root_cause`.
- Regression intent is represented by `added_to_eval_set`.
- Large videos, weights, generated run directories, and bulk outputs remain
  outside Git.

## Current Limitations

- No full real Bad Case collection has been completed.
- No `/api/bad-cases` endpoint is implemented yet.
- No evaluation API is implemented yet.
- Existing gallery labels are qualitative and often count-based, not
  object-level IoU review.
- Selected examples are lightweight documentation artifacts, not a replacement
  for official detection, tracking, counting, ROI, or event metrics.

## Follow-Up Work

- Collect a reviewed real `bad_cases.csv` from detector, tracker, counter, ROI,
  event, API, deployment, and documentation failures.
- Add `/api/bad-cases` for creating and querying Bad Case records.
- Link Bad Cases to evaluation reports and Video Analysis Center summaries.
- Build a regression set from selected confirmed hard cases.
- Add evaluation API endpoints after the evaluation contract is fixed.
