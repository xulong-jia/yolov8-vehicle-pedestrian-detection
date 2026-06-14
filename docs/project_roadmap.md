# Project Roadmap

## Current Status

The project currently includes:

- YOLOv8n baseline training
- YOLOv8n official test split validation metrics are recorded, but some summary artifacts are not currently tracked in repository
- full test inference metrics are recorded, but some summary artifacts are not currently tracked in repository
- confidence threshold comparison metrics are recorded, but some summary artifacts are not currently tracked in repository
- YOLOv8s supplementary validation result
- experiment comparison
- video demo
- Streamlit demo
- qualitative error case gallery
- model card
- dataset card
- model weight policy
- bilingual project task board

## Phase 1 — Documentation and Governance

- model card: done
- dataset card: done
- model weight policy: done
- project roadmap: this file
- report assets index: planned in this batch

## Phase 2 — Evaluation and Analysis

- per-class failure analysis
- confusion matrix interpretation
- error taxonomy v2
- hard examples list
- threshold analysis report
- restore or recreate missing tracked summaries for official test validation, full test inference, and confidence threshold comparison

## Phase 3 — Demo and UX

- Streamlit sample selector
- downloadable prediction CSV
- better Streamlit error messages
- demo screenshots

## Phase 4 — Engineering and Reproducibility

- GitHub Actions Python syntax check
- Makefile
- local setup check script
- batch prediction CLI
- basic unit tests
- config file

## Phase 5 — Deployment and Serving

- FastAPI inference service
- API docs
- local deployment guide
- Dockerfile without weights
- model loading strategy

## Phase 6 — Optional Future Experiments

- YOLOv8s official same-split test validation if weight is available
- strict YOLOv8n vs YOLOv8s comparison
- image size ablation
- YOLOv8m experiment
- ONNX export guide
- inference speed benchmark

## Repository Safety Rules

Do not commit:

- weights
- full dataset
- large videos
- full runs outputs
- ONNX exports

## Related Files

- `docs/project_task_board.md`
- `docs/model_card.md`
- `docs/dataset_card.md`
- `docs/model_weight_policy.md`
- `README.md`
