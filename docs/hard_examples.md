# Hard Examples

## Purpose

Hard examples are representative cases that should receive extra attention during future review and model comparison. They are useful for:

- manual review
- targeted data cleaning
- hard example mining
- future model comparison

The current list is qualitative. It is based on existing gallery cases and does not introduce new inference results.

## Source

- `docs/error_case_gallery/cases.csv`
- `docs/error_case_gallery/images/`
- `docs/error_taxonomy.md`

The current `docs/hard_examples.csv` is derived from the 8 confirmed cases in `docs/error_case_gallery/cases.csv`.

## How to Use

- Inspect high-risk cases manually.
- Group examples by error type before planning improvements.
- Verify labels if original annotations are available.
- Use these cases for future validation and qualitative comparison.
- Do not automatically add these cases to training without checking label quality and dataset policy.

## Hard Example Summary

The current hard examples cover:

- false positive candidates
- false negative candidates
- class confusion candidates
- duplicate box candidates
- crowded scene difficulty
- small object difficulty
- positive reference cases for likely correct detection

Key patterns include crowded Person scenes, dense traffic scenes, and Car / Truck / mini-truck confusion candidates. Exact object-level errors still require manual visual inspection because the source labels are based on image-level count comparisons.

## Files

- Hard examples table: `docs/hard_examples.csv`
- Error taxonomy: `docs/error_taxonomy.md`
- Gallery case table: `docs/error_case_gallery/cases.csv`
- Gallery images: `docs/error_case_gallery/images/`

## Safety Note

Do not commit the full dataset, model weights, large generated predictions, videos, or full `runs/` outputs to Git. Keep hard example tracking lightweight and documentation-focused unless a future task explicitly creates a reviewed small artifact.
