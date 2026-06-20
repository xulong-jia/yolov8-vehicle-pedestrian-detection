# Bad Case Report

## Current Status

The project now has the minimum Bad Case foundation required by the YOLOv8
final execution manual:

- taxonomy exists in `docs/error_taxonomy.md`
- hard examples exist in `docs/hard_examples.md`
- error case gallery exists in `docs/error_case_gallery/README.md`
- v0.14.0 adds the unified `bad_cases.csv` schema in
  `docs/bad_cases_schema.md`
- the current scaffold adds metadata-only Bad Case collection through
  `src/services/bad_case_service.py` and `/api/bad-cases`

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
- `docs/error_case_gallery/reviewed_bad_cases.csv` is a small reviewed sample
  collection with 24 metadata-only cases across detector, tracker, counter,
  ROI, and event modules.

The gallery and hard examples are sources for review. They are not a complete
`bad_cases.csv` dataset.

## Reviewed Sample Collection

`v1.6.0-reviewed-bad-case-collection` adds a small reviewed Bad Case sample
collection for demonstration, report review, and later evaluation planning. It
is deliberately bounded:

- 24 reviewed records.
- Modules covered: detector, tracker, counter, ROI, and event.
- Case types covered include `false_positive`, `false_negative`,
  `class_confusion`, `id_switch`, `track_lost`, `count_error`,
  `roi_membership_error`, `roi_config_error`, `rule_error`, and
  `threshold_error`.
- Snapshot paths reuse existing lightweight files under
  `docs/error_case_gallery/images/`.
- No new large images, videos, weights, generated CSV/JSON/JSONL outputs, or
  local run directories are committed.

This reviewed sample is suitable for explaining taxonomy, schema fields,
root-cause notes, reviewer notes, and how selected cases can be marked for a
future evaluation set. It is not a large production Bad Case dataset and is not
a substitute for a reviewed GT quantitative evaluation.

## Minimum Acceptance Criteria

- Bad Case schema exists and documents required fields.
- Bad Case taxonomy exists and is linked to the schema.
- Gallery and hard examples link back to the schema/report.
- Small reviewed Bad Case sample exists in
  `docs/error_case_gallery/reviewed_bad_cases.csv`.
- Root-cause analysis is represented by `root_cause`.
- Regression intent is represented by `added_to_eval_set`.
- Metadata-only collection can write local ignored CSV/JSONL records.
- `/api/bad-cases` can create and list Bad Case metadata records.
- Large videos, weights, generated run directories, and bulk outputs remain
  outside Git.

## Current Limitations

- A small reviewed Bad Case sample exists, but no large production-scale Bad
  Case collection has been completed.
- `/api/bad-cases` is metadata-only and does not upload large files.
- No evaluation API is implemented yet.
- Existing gallery labels are qualitative and often count-based, not
  object-level IoU review.
- Selected examples are lightweight documentation artifacts, not a replacement
  for official detection, tracking, counting, ROI, or event metrics.

## Follow-Up Work

- Expand the reviewed sample into a larger real `bad_cases.csv` from detector,
  tracker, counter, ROI, event, API, deployment, and documentation failures.
- Link Bad Cases to evaluation reports and Video Analysis Center summaries.
- Build a regression set from selected confirmed hard cases.
- Add evaluation API endpoints after the evaluation contract is fixed.
