# Report Assets Index

## Purpose

This file indexes lightweight assets that can be used in reports, documentation, and project demonstrations. It lists existing paths and intended use without copying images or generating new artifacts.

## Dataset Assets

| Asset | Status | Use |
| --- | --- | --- |
| `docs/dataset_distribution.md` | Available | Dataset split and annotation distribution summary |
| `docs/dataset_distribution.csv` | Available | Machine-readable dataset distribution table |
| `docs/dataset_distribution.png` | Available | Dataset distribution figure |

## Training and Evaluation Assets

| Asset | Status | Use |
| --- | --- | --- |
| `docs/colab_runs/yolov8n_416_10epochs/` | Available | YOLOv8n smoke test plots and metrics |
| `docs/colab_runs/yolov8n_640_50epochs/` | Available | YOLOv8n 640x640 50-epoch baseline plots and metrics |
| `docs/experiments/yolov8s_640_50epochs/summary.md` | Available | YOLOv8s supplementary validation summary |
| `docs/experiment_comparison.md` | Available | Human-readable model comparison |
| `docs/experiment_comparison.csv` | Available | Machine-readable model comparison |

Official test validation, full test inference, and confidence threshold comparison summaries are referenced in project notes but not currently tracked, and should be restored or recreated later.

## Error Analysis Assets

| Asset | Status | Use |
| --- | --- | --- |
| `docs/predictions/yolov8n_640_50epochs/` | Available | 10-sample image inference and error analysis |
| `docs/predictions/yolov8n_640_50epochs_50samples/` | Available | 50-sample image inference and error analysis |
| `docs/error_case_gallery/README.md` | Available | Qualitative error case gallery guide |
| `docs/error_case_gallery/cases.csv` | Available | Error case metadata |
| `docs/error_case_gallery/images/` | Available | Selected lightweight prediction images |

## Video Demo Assets

| Asset | Status | Use |
| --- | --- | --- |
| `docs/video_demos/yolov8n_640_50epochs/video_inference_summary.md` | Available | Video inference summary |
| `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_start.jpg` | Available | Start key frame |
| `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_middle.jpg` | Available | Middle key frame |
| `docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_end.jpg` | Available | End key frame |

The large AVI video is local/ignored and should not be committed.

## Streamlit Demo Assets

| Asset | Status | Use |
| --- | --- | --- |
| `app.py` | Available | Local Streamlit image detection demo |
| `docs/streamlit_demo.md` | Available | Streamlit demo usage guide |

## Governance Docs

| Asset | Status | Use |
| --- | --- | --- |
| `docs/model_card.md` | Available | Model scope, metrics, limitations, and weight policy |
| `docs/dataset_card.md` | Available | Dataset source, split, distribution, and limitations |
| `docs/model_weight_policy.md` | Available | Weight storage and Git safety policy |
| `docs/project_task_board.md` | Available | Long-term task board |
| `docs/project_roadmap.md` | Available | Long-term project roadmap |

## Missing or To-Be-Restored Assets

- official test validation tracked summary
- full test inference tracked summary
- confidence threshold comparison tracked summary
