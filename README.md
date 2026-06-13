# YOLOv8 Vehicle and Pedestrian Detection

## 项目简介

本项目基于 YOLOv8 构建车辆与行人目标检测系统，目标是完成从数据集准备、模型训练、模型评估到图片和视频推理的完整可复现实验流程。当前已完成项目初始化、数据集检查、异常 label 清洗、Colab 10 epoch 快速训练验证和 YOLOv8n 640x640 50 epoch baseline。

## 技术栈

- Python
- Ultralytics YOLOv8
- OpenCV
- NumPy
- Matplotlib
- Pandas
- Roboflow
- PyYAML

## 目录结构

```text
yolov8-vehicle-pedestrian-detection/
  dataset/
    README.md
    data.yaml
    train/
      images/
      labels/
    valid/
      images/
      labels/
    test/
      images/
      labels/
  src/
    train.py
    evaluate.py
    predict_image.py
    predict_video.py
    visualize_dataset.py
    analyze_dataset.py
  results/
    images/
    videos/
    metrics/
  notebooks/
  docs/
    screenshots/
    colab_runs/
  README.md
  requirements.txt
  .gitignore
```

## 数据集说明

数据集需要使用 YOLOv8 格式，建议从 Roboflow 选择公开车辆与行人检测数据集并导出为 YOLOv8 格式。数据集不提交到 Git 仓库，下载后放入 `dataset/` 目录。

预期结构：

```text
dataset/
  data.yaml
  train/images/
  train/labels/
  valid/images/
  valid/labels/
  test/images/
  test/labels/
```

`dataset/data.yaml` 必须包含 `names` 字段，用于说明类别名称。

## 环境安装步骤

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
yolo checks
```

## 训练命令

快速跑通版本：

```bash
python src/train.py --model yolov8n.pt --epochs 10 --imgsz 416
```

Colab GPU 快速验证版本：

```bash
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=10 imgsz=416 project=runs/detect name=yolov8n_416_10epochs device=0
```

正式实验版本：

```bash
python src/train.py --model yolov8n.pt --epochs 50 --imgsz 640
```

## 评估命令

```bash
python src/evaluate.py --model local_weights/yolov8n_640_50epochs/best.pt --data dataset/data.yaml
```

## 图片推理命令

```bash
python src/predict_image.py --source dataset/test/images --model local_weights/yolov8n_640_50epochs/best.pt
```

## 视频推理命令

```bash
python src/predict_video.py --source demo_video.mp4 --model local_weights/yolov8n_640_50epochs/best.pt
```

## 权重文件说明

模型权重文件不上传 GitHub。评估和推理前，需要将正式 baseline 的 `best.pt` 放到：

```text
local_weights/yolov8n_640_50epochs/best.pt
```

GitHub 仓库只保存代码、配置、README 和展示结果图，不保存完整数据集、训练输出目录或 `.pt` 权重文件。

## 数据集检查命令

```bash
python src/analyze_dataset.py --data dataset/data.yaml
python src/visualize_dataset.py --data dataset/data.yaml --split train --num-samples 5
```

## 实验记录

| 实验 | 模型 | imgsz | epochs | conf | Precision | Recall | mAP50 | mAP50-95 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Smoke Test | YOLOv8n | 416 | 10 | 默认 | 0.786 | 0.749 | 0.797 | 0.511 | Colab Tesla T4 快速训练验证，不是最终正式模型 |
| Baseline | YOLOv8n | 640 | 50 | 默认 | 0.81981 | 0.82768 | 0.86422 | 0.59102 | Colab Tesla T4 正式 baseline |

## Colab 10 Epoch Smoke Test

该实验用于验证数据集、训练命令和 YOLOv8 训练流程可以跑通，不作为最终正式模型结论。

- 模型：YOLOv8n
- 输入尺寸：416
- 训练轮数：10 epochs
- 训练环境：Google Colab Tesla T4 GPU
- 训练时间：0.098 hours
- 结果文件：`docs/colab_runs/yolov8n_416_10epochs/`
- 本地权重：`local_weights/yolov8n_416_10epochs/`，该目录不提交到 GitHub

训练命令：

```bash
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=10 imgsz=416 project=runs/detect name=yolov8n_416_10epochs device=0
```

指标：

| Model | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | --- | --- | --- |
| YOLOv8n 416 10 epochs | 0.786 | 0.749 | 0.797 | 0.511 |

简要分析：从本次 smoke test 的类别表现看，Motorcycle 和 Person 表现较好；mini-truck 表现较弱，可能与样本量、类别相似性或小目标有关。后续需要在正式 baseline 中继续结合混淆矩阵、PR 曲线和误检漏检样例分析。

## YOLOv8n 640x640 50 Epoch Baseline

该实验作为当前正式 baseline，用于记录 YOLOv8n 在 640x640 输入尺寸和 50 epoch 设置下的性能。

- 模型：YOLOv8n
- 输入尺寸：640
- 训练轮数：50 epochs
- 训练环境：Google Colab Tesla T4 GPU
- 训练时间：0.756 hours
- 结果文件：`docs/colab_runs/yolov8n_640_50epochs/`
- 本地权重：`local_weights/yolov8n_640_50epochs/`，该目录不提交到 GitHub

训练命令：

```bash
yolo detect train data=dataset/data.yaml model=yolov8n.pt epochs=50 imgsz=640 project=runs name=yolov8n_640_50epochs device=0
```

指标：

| Model | Precision | Recall | mAP50 | mAP50-95 |
| --- | --- | --- | --- | --- |
| YOLOv8n 640 50 epochs | 0.81981 | 0.82768 | 0.86422 | 0.59102 |

## Inference and Error Analysis

本阶段基于 YOLOv8n 640x640 50 epoch baseline 权重进行小批量图片推理和初版误检漏检分析。

- 使用模型：YOLOv8n 640x640 50 epoch baseline
- 权重路径：`local_weights/yolov8n_640_50epochs/best.pt`
- 推理样本：从 `dataset/test/images` 使用固定随机种子 `42` 随机选择 10 张图片
- 输出目录：`docs/predictions/yolov8n_640_50epochs/`

输出目录包含：

- 10 张预测可视化图片
- `labels/` 预测标签
- `selected_images.txt`
- `inference_summary.md`
- `error_analysis.csv`
- `error_analysis.md`

相关分析文件：

- [Inference summary](docs/predictions/yolov8n_640_50epochs/inference_summary.md)
- [Error analysis report](docs/predictions/yolov8n_640_50epochs/error_analysis.md)
- [Error analysis CSV](docs/predictions/yolov8n_640_50epochs/error_analysis.csv)
- [Day 5 systematic error analysis report](docs/predictions/yolov8n_640_50epochs/day5_error_analysis_report.md)
- [Day 5 error case summary CSV](docs/predictions/yolov8n_640_50epochs/error_case_summary.csv)
- [Day 5 image-level error analysis CSV](docs/predictions/yolov8n_640_50epochs/image_level_error_analysis.csv)

Day 5 系统误差分析基于 Day 4 的 10 张图片推理结果，对每张图片的 GT label 和 prediction label 做数量级对比，并整理出可用于 README 或项目报告的成功案例、误检候选、漏检候选和类别混淆候选。

| Case type | Count |
| --- | ---: |
| likely_correct | 7 |
| possible_false_positive | 2 |
| possible_false_negative | 1 |
| possible_class_confusion | 2 |
| possible_duplicate_boxes | 0 |
| crowded_scene | 4 |
| small_object_difficulty | 0 |
| needs_manual_review | 3 |

Day 6 将图片推理样本从 10 张扩大到 50 张，继续使用固定随机种子 `42` 和同一 baseline 权重，形成更稳定的定性误差分析材料。

- Day 6 输出目录：`docs/predictions/yolov8n_640_50epochs_50samples/`

Day 6 分析文件：

- [Day 6 inference summary](docs/predictions/yolov8n_640_50epochs_50samples/inference_summary.md)
- [Day 6 50-sample error analysis report](docs/predictions/yolov8n_640_50epochs_50samples/day6_50sample_error_analysis_report.md)
- [Day 6 error case summary CSV](docs/predictions/yolov8n_640_50epochs_50samples/error_case_summary.csv)
- [Day 6 image-level error analysis CSV](docs/predictions/yolov8n_640_50epochs_50samples/image_level_error_analysis.csv)
- [Day 6 selected images](docs/predictions/yolov8n_640_50epochs_50samples/selected_images.txt)

Day 6 50 张样本统计：

| Case type | Count |
| --- | ---: |
| likely_correct | 28 |
| possible_false_positive | 16 |
| possible_false_negative | 10 |
| possible_class_confusion | 4 |
| possible_duplicate_boxes | 14 |
| crowded_scene | 22 |
| small_object_difficulty | 15 |
| needs_manual_review | 23 |

Day 6 的 50 张图片分析比 10 张样本更稳定，但仍属于定性误差分析，不替代完整测试集 mAP、Precision 或 Recall。

初步误差分析重点：

- 密集车流中 `Car` / `Truck` / `mini-truck` 容易出现类别混淆。
- 拥挤或遮挡的 `Person` 场景存在漏检。
- 该分析基于 10 张图片的小样本定性观察，不代表完整测试集指标。

## Video Inference Demo

本阶段使用外部公开视频素材完成 YOLOv8 视频推理 demo，用于展示模型在连续街景视频上的定性检测效果。

- 使用模型：YOLOv8n 640x640 50 epoch baseline
- 权重路径：`local_weights/yolov8n_640_50epochs/best.pt`
- 视频来源：Pexels external video source
- 视频来源记录：`local_videos/README.video_sources.md`
- 推理环境：Google Colab GPU
- 推理参数：`imgsz=640`，`conf=0.25`，`device=0`
- 输出目录：`docs/video_demos/yolov8n_640_50epochs/`

相关文件：

- [Video inference summary](docs/video_demos/yolov8n_640_50epochs/video_inference_summary.md)
- [Start frame](docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_start.jpg)
- [Middle frame](docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_middle.jpg)
- [End frame](docs/video_demos/yolov8n_640_50epochs/frames/pexels_crosswalk_traffic_demo_end.jpg)

视频文件说明：

- 原始视频不提交 GitHub。
- 完整推理输出 AVI 约 404MB，保留本地，不提交 GitHub。
- GitHub 只提交 summary 和关键帧截图。
- 视频 demo 是定性展示，不代表完整测试集指标。

## 后续计划

- Day 4：评估模型并记录 Precision、Recall、mAP50、mAP50-95。
- Day 5：完成图片推理结果保存。
- Day 6：完成视频推理结果保存。
- Day 7：补充实验对比、误检漏检分析、最终 README 和简历描述。
- 可选实验计划：YOLOv8n 416x416 30 epoch 快速基线、YOLOv8s 640x640 50 epoch 对比、YOLOv8n 640x640 不同置信度阈值对比。
- 下一步：基于 YOLOv8n 640x640 50 epoch baseline 做图片推理、视频推理和误检漏检分析。
