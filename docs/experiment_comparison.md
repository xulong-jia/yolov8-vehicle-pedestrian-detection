# Experiment Comparison

## Sources

- YOLOv8n official test validation: `docs/evaluation/yolov8n_640_50epochs_official/summary.md`
- YOLOv8s validation result: `docs/experiments/yolov8s_640_50epochs/summary.md`

## Overall Comparison Table

| Model | imgsz | Epochs | Split | Images | Instances | Precision | Recall | mAP50 | mAP50-95 | Training time | Model size | Weight committed |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| YOLOv8n | 640 | 50 | test | 396 | 1642 | 0.841 | 0.816 | 0.859 | 0.582 | n/a | n/a | No |
| YOLOv8s | 640 | 50 | val | 791 | 3731 | 0.839 | 0.841 | 0.877 | 0.604 | 0.999 hours | about 22.5 MB | No |

## Important Fairness Note

- The YOLOv8n result is official test split validation.
- The YOLOv8s result is validation split training result.
- Therefore this is a supplementary model comparison, not a strict same-split benchmark.

Because the evaluated splits are different, this comparison should be used to understand model-capacity trends, not to claim that YOLOv8s definitively outperforms YOLOv8n on the official test split.

## Interpretation

YOLOv8s has higher mAP50 and mAP50-95 in its validation result:

- YOLOv8n official test mAP50: `0.859`
- YOLOv8s validation mAP50: `0.877`
- YOLOv8n official test mAP50-95: `0.582`
- YOLOv8s validation mAP50-95: `0.604`

YOLOv8s also has higher recall in its validation result:

- YOLOv8n official test Recall: `0.816`
- YOLOv8s validation Recall: `0.841`

The tradeoff is cost. YOLOv8s is larger, with an estimated model size of about `22.5 MB`, and its 50 epoch Colab training run took `0.999 hours`. YOLOv8n remains the lighter baseline and is easier to run locally for small-scale inference.

Since the splits differ, do not claim YOLOv8s definitely outperforms YOLOv8n on the official test split.

## YOLOv8s Per-Class Metrics

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| Bus | 0.875 | 0.807 | 0.860 | 0.662 |
| Car | 0.837 | 0.796 | 0.841 | 0.511 |
| Motorcycle | 0.925 | 0.984 | 0.987 | 0.730 |
| Person | 0.929 | 0.898 | 0.955 | 0.621 |
| Truck | 0.785 | 0.839 | 0.872 | 0.595 |
| mini-truck | 0.683 | 0.722 | 0.747 | 0.506 |

## Per-Class Observations

- `Motorcycle` and `Person` are the strongest classes in the YOLOv8s validation result.
- `mini-truck` remains the weakest and most challenging class.
- `Truck`, `Car`, and `mini-truck` may share visual similarity and can cause class confusion, especially in dense traffic scenes or small-object cases.

## Recommended Conclusion for Final Report

YOLOv8n remains the lightweight baseline for this project. It has official test split validation results and is practical for local small-scale inference.

YOLOv8s provides evidence that a larger model may improve detection quality, especially in recall and mAP50-95, but it requires official test split validation for strict confirmation.

## Recommended Next Step

If more time is available, run YOLOv8s `split=test` validation using YOLOv8s `best.pt`.

Since YOLOv8s `best.pt` is not currently preserved in GitHub, this would require keeping or downloading the weight after training, or retraining YOLOv8s on Google Colab GPU.

## Strict Same-Split Test Comparison

YOLOv8s now has official test split metrics from the retrained model. The strict same-split comparison is documented in [`docs/strict_model_comparison.md`](strict_model_comparison.md).

| Model | Split | imgsz | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| YOLOv8n 640 50 epochs | test | 640 | 0.841 | 0.816 | 0.859 | 0.582 |
| YOLOv8s 640 50 epochs retrain | test | 640 | 0.865 | 0.838 | 0.876 | 0.601 |

Strict same-split deltas for YOLOv8s over YOLOv8n:

- Precision: `+0.024`
- Recall: `+0.022`
- mAP50: `+0.017`
- mAP50-95: `+0.019`

The earlier YOLOv8s validation-only comparison remains as a historical supplementary result. The strict test split comparison should be used when discussing model-to-model performance on the aligned official test protocol.
