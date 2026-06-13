# Next Experiment Plan

> This plan focuses on improving project completeness and report quality. It does not require blindly adding experiments. Training and large-scale inference should be run only when they provide clear comparison value.

## 1. Current Project Progress Summary

The project has completed the main YOLOv8 vehicle and pedestrian detection workflow:

- Dataset configuration is available at `dataset/data.yaml`.
- The dataset uses YOLOv8 format with train, validation, and test splits.
- Six classes are configured: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, and `mini-truck`.
- A YOLOv8n 416x416 10 epoch smoke test has been completed on Google Colab GPU.
- A YOLOv8n 640x640 50 epoch baseline has been completed on Google Colab GPU.
- Baseline result artifacts are saved under `docs/colab_runs/yolov8n_640_50epochs/`.
- The baseline local weight path is `local_weights/yolov8n_640_50epochs/best.pt`.
- Day 4 and Day 5 completed 10-sample image inference and error analysis.
- Day 6 expanded the qualitative image inference sample to 50 images.
- A Pexels-based video inference demo has been completed, with summary and key frames saved under `docs/video_demos/yolov8n_640_50epochs/`.

Current strongest baseline:

| Model | Image Size | Epochs | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| YOLOv8n | 640 | 50 | 0.81981 | 0.82768 | 0.86422 | 0.59102 |

## 2. Recommended Experiment Order

Recommended order:

1. Dataset class distribution statistics.
2. Formal validation of the current YOLOv8n `best.pt`.
3. Confidence threshold comparison for the current YOLOv8n baseline.
4. Full test set inference.
5. YOLOv8s 640x640 50 epoch comparison experiment.
6. Final experiment comparison table.

This order first strengthens the existing baseline evidence, then expands qualitative inference, and only then adds a larger model comparison.

## 3. Experiment Plan

### 3.1 Dataset Class Distribution Statistics

| Item | Plan |
| --- | --- |
| Purpose | Quantify the number of labels per class across train, validation, and test splits. This helps explain class imbalance and supports later error analysis, especially for `mini-truck`. |
| Input files | `dataset/data.yaml`, `dataset/train/labels/`, `dataset/valid/labels/`, `dataset/test/labels/` |
| Output files | `docs/dataset_class_distribution.csv`, `docs/dataset_class_distribution.md`, optional chart `docs/dataset_class_distribution.png` |
| Needs Colab GPU | No |
| Estimated time | Short |
| Recommended environment | Local Mac |
| Risks and notes | This is a lightweight statistics task. It should not modify dataset labels. If some label files are empty, count them separately instead of deleting or editing them. |

### 3.2 Formal Validation of Current YOLOv8n best.pt

| Item | Plan |
| --- | --- |
| Purpose | Re-run official YOLO validation using the existing `best.pt` to produce a clean validation record for the final report. This confirms the baseline metrics from the saved model, not only from the original training log. |
| Input files | `local_weights/yolov8n_640_50epochs/best.pt`, `dataset/data.yaml`, validation split from `dataset/valid/` |
| Output files | `docs/validation/yolov8n_640_50epochs/results.csv`, `docs/validation/yolov8n_640_50epochs/results.png`, `docs/validation/yolov8n_640_50epochs/confusion_matrix.png`, `docs/validation/yolov8n_640_50epochs/BoxPR_curve.png`, `docs/validation/yolov8n_640_50epochs/validation_summary.md` |
| Needs Colab GPU | Optional |
| Estimated time | Short to medium |
| Recommended environment | Colab GPU preferred for speed; local is acceptable if validation time is manageable. |
| Risks and notes | Do not overwrite existing `docs/colab_runs/yolov8n_640_50epochs/`. Save formal validation to a separate `docs/validation/` directory. Do not commit `.pt` files. |

### 3.3 Full Test Set Inference

| Item | Plan |
| --- | --- |
| Purpose | Run inference on the full test image split to create a stronger qualitative and quantitative error-analysis base than the current 50-sample subset. |
| Input files | `local_weights/yolov8n_640_50epochs/best.pt`, `dataset/test/images/`, `dataset/test/labels/`, `dataset/data.yaml` |
| Output files | `docs/predictions/yolov8n_640_50epochs_full_test/inference_summary.md`, `docs/predictions/yolov8n_640_50epochs_full_test/image_level_error_analysis.csv`, `docs/predictions/yolov8n_640_50epochs_full_test/error_case_summary.csv`, selected visualization images, prediction labels if file size is reasonable |
| Needs Colab GPU | Recommended if the test set has many images |
| Estimated time | Medium |
| Recommended environment | Colab GPU for large test set; local only for a small or sampled run. |
| Risks and notes | Full prediction visualizations can create many image files. Avoid committing excessive outputs. Consider committing summaries, CSVs, and selected representative images instead of every predicted image. |

### 3.4 YOLOv8s 640x640 50 Epoch Comparison Experiment

| Item | Plan |
| --- | --- |
| Purpose | Compare YOLOv8n against a larger YOLOv8s model to evaluate whether a modest model-size increase improves Precision, Recall, mAP50, and mAP50-95. |
| Input files | `dataset/data.yaml`, train/validation/test splits under `dataset/` |
| Output files | `docs/colab_runs/yolov8s_640_50epochs/results.csv`, `docs/colab_runs/yolov8s_640_50epochs/results.png`, `docs/colab_runs/yolov8s_640_50epochs/confusion_matrix.png`, `docs/colab_runs/yolov8s_640_50epochs/BoxPR_curve.png`, `docs/colab_runs/yolov8s_640_50epochs/args.yaml`, `docs/colab_runs/yolov8s_640_50epochs/yolov8s_640_50epochs_summary.md` |
| Needs Colab GPU | Yes |
| Estimated time | Long |
| Recommended environment | Google Colab GPU |
| Risks and notes | This should not be run locally on CPU. Keep `best.pt` and `last.pt` under `local_weights/yolov8s_640_50epochs/` or Colab storage, not GitHub. Only commit lightweight plots, CSVs, summaries, and selected result images. |

### 3.5 Confidence Threshold Comparison: conf=0.25 / 0.40 / 0.60

| Item | Plan |
| --- | --- |
| Purpose | Understand the tradeoff between false positives and false negatives at different confidence thresholds using the current YOLOv8n baseline. |
| Input files | `local_weights/yolov8n_640_50epochs/best.pt`, `dataset/test/images/`, `dataset/test/labels/`, `dataset/data.yaml` |
| Output files | `docs/confidence_threshold_comparison/yolov8n_640_50epochs/conf_025/`, `docs/confidence_threshold_comparison/yolov8n_640_50epochs/conf_040/`, `docs/confidence_threshold_comparison/yolov8n_640_50epochs/conf_060/`, `docs/confidence_threshold_comparison/yolov8n_640_50epochs/threshold_comparison.csv`, `docs/confidence_threshold_comparison/yolov8n_640_50epochs/threshold_comparison.md` |
| Needs Colab GPU | Optional for sampled inference; recommended for full test set inference |
| Estimated time | Medium |
| Recommended environment | Local for small fixed samples; Colab GPU for full test split. |
| Risks and notes | Use the same image set for all thresholds. Do not compare threshold results from different samples. Keep large image outputs out of Git unless explicitly selected for documentation. |

### 3.6 Experiment Comparison Table

| Item | Plan |
| --- | --- |
| Purpose | Consolidate all meaningful experiments into one table for README, final report, and PPT. |
| Input files | `README.md`, `docs/colab_runs/yolov8n_416_10epochs/results.csv`, `docs/colab_runs/yolov8n_640_50epochs/results.csv`, future YOLOv8s results, future validation and threshold comparison summaries |
| Output files | `docs/experiment_comparison.md`, `docs/experiment_comparison.csv` |
| Needs Colab GPU | No |
| Estimated time | Short |
| Recommended environment | Local Mac |
| Risks and notes | Do not mix qualitative image inference counts with official validation metrics. Keep Precision, Recall, mAP50, and mAP50-95 in metric columns, and put qualitative analysis in separate notes. |

## 4. Local vs Colab Guidance

Local Mac is suitable for:

- Dataset class distribution statistics.
- Documentation and report writing.
- Reading and summarizing existing CSV and Markdown outputs.
- Small fixed-sample image checks.
- Curating representative images for README or PPT.

Google Colab GPU is recommended or required for:

- YOLOv8s 640x640 50 epoch training.
- Any new full training run.
- Full test set inference if the test set is large.
- Large video inference jobs.
- Repeated threshold inference over the full test set.

## 5. Risk Control Checklist

- Do not commit `.pt`, `.pth`, `.onnx`, or other weight files.
- Do not commit full `dataset/train/`, `dataset/valid/`, or `dataset/test/`.
- Do not overwrite existing `docs/colab_runs/yolov8n_640_50epochs/` artifacts.
- Do not move or modify `local_weights/`.
- Do not move or modify the dataset during analysis.
- Keep original videos and large inferred videos local unless file size and license are explicitly approved.
- For every new experiment, write a short summary file that records model, data source, environment, parameters, outputs, and limitations.
- Treat sampled image error analysis as qualitative evidence, not as a replacement for full validation metrics.

## 6. Suggested Completion Criteria

The project is ready for final report and PPT once the following are available:

- Dataset class distribution summary.
- Formal validation summary for YOLOv8n 640x640 50 epoch `best.pt`.
- Existing Day 6 50-sample inference and error analysis.
- Existing video inference summary and key frames.
- One consolidated experiment comparison table.

YOLOv8s and confidence-threshold comparison are useful enhancements, but they should be treated as optional if time or Colab quota is limited.
