# Image Size Ablation

## Scope

- Model: custom YOLOv8n 640x640 50 epochs `best.pt`
- Dataset config: `dataset/data.yaml`
- Split: official test split
- Test images: 396
- Image sizes compared: 416, 512, 640
- Task: validation metrics only
- No training was performed
- No model weights or full validation runs are committed

## Environment

- Timestamp: `2026-06-16T11:50:46`
- GPU: `Tesla T4`
- Torch: `2.11.0+cu128`
- Device: `cuda:0`

## Results

| Image Size | Precision | Recall | mAP50 | mAP50-95 | Run Dir |
| ---: | ---: | ---: | ---: | ---: | --- |
| 416 | 0.834 | 0.792 | 0.855 | 0.576 | `/content/yolov8-vehicle-pedestrian-detection/runs/detect/runs/detect/val_yolov8n_ablation_imgsz_416` |
| 512 | 0.825 | 0.830 | 0.863 | 0.582 | `/content/yolov8-vehicle-pedestrian-detection/runs/detect/runs/detect/val_yolov8n_ablation_imgsz_512` |
| 640 | 0.841 | 0.816 | 0.859 | 0.582 | `/content/yolov8-vehicle-pedestrian-detection/runs/detect/runs/detect/val_yolov8n_ablation_imgsz_640` |

## Interpretation

- Best mAP50-95 in this ablation: image size `512` with mAP50-95 `0.582`.
- Best mAP50 in this ablation: image size `512` with mAP50 `0.863`.
- Larger image sizes usually preserve more small-object detail, but may cost more inference time.
- This ablation compares evaluation image size only; it does not retrain the model at different image sizes.

## Related Context

- Previous YOLOv8n official test at 640: P 0.841, R 0.816, mAP50 0.859, mAP50-95 0.582
- PyTorch Colab T4 speed benchmark at 640: YOLOv8n 11.562 ms/image, 86.49 FPS
- ONNX Runtime CUDA benchmark at 640: YOLOv8n 10.994 ms/image, 90.96 FPS

## Caveats

- This is validation-only; no training was performed.
- This does not compare separately trained 416/512/640 models.
- Full `runs/` outputs are local/Colab artifacts and are not committed.
- Dataset splits and weights remain local-only artifacts.

## Output Files

- `docs/image_size_ablation.md`
- `docs/image_size_ablation.csv`
- `docs/image_size_ablation_raw.json`
