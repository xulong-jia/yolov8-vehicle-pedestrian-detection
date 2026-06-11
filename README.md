# YOLOv8 Vehicle and Pedestrian Detection

## 项目简介

本项目基于 YOLOv8 构建车辆与行人目标检测系统，目标是完成从数据集准备、模型训练、模型评估到图片和视频推理的完整可复现实验流程。当前阶段为 Day 1 项目初始化，只提供规范项目骨架和可运行脚本入口，不包含数据集、训练权重或实验指标。

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
YOLOv8/
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

正式实验版本：

```bash
python src/train.py --model yolov8n.pt --epochs 50 --imgsz 640
```

## 评估命令

```bash
python src/evaluate.py --model runs/detect/train/weights/best.pt --data dataset/data.yaml
```

## 图片推理命令

```bash
python src/predict_image.py --source dataset/test/images --model runs/detect/train/weights/best.pt
```

## 视频推理命令

```bash
python src/predict_video.py --source demo_video.mp4 --model runs/detect/train/weights/best.pt
```

## 数据集检查命令

```bash
python src/analyze_dataset.py --data dataset/data.yaml
python src/visualize_dataset.py --data dataset/data.yaml --split train --num-samples 5
```

## 实验记录

| 实验 | 模型 | imgsz | epochs | conf | Precision | Recall | mAP50 | mAP50-95 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Exp1 | YOLOv8n | 416 | 30 | 0.25 | 待填 | 待填 | 待填 | 待填 | 快速基线 |
| Exp2 | YOLOv8n | 640 | 50 | 0.25 | 待填 | 待填 | 待填 | 待填 | 正式模型 |
| Exp3 | YOLOv8s | 640 | 50 | 0.25 | 待填 | 待填 | 待填 | 待填 | 对比模型 |
| Exp4 | YOLOv8n | 640 | 50 | 0.50 | 待填 | 待填 | 待填 | 待填 | 阈值对比 |

## 后续计划

- Day 2：下载 YOLOv8 格式数据集，检查 `data.yaml`、图片和标签是否匹配。
- Day 2：统计 train/valid/test 图片数量和各类别标注框数量。
- Day 2：生成标注可视化样例并保存到 `docs/screenshots/`。
- Day 3：使用 YOLOv8n 跑通小规模训练，再进行正式训练。
- Day 4：评估模型并记录 Precision、Recall、mAP50、mAP50-95。
- Day 5：完成图片推理结果保存。
- Day 6：完成视频推理结果保存。
- Day 7：补充实验对比、误检漏检分析、最终 README 和简历描述。
