# Dataset Guide

本项目需要使用 YOLOv8 格式的数据集。建议从 Roboflow 导出 YOLOv8 格式后，将数据放入当前 `dataset/` 目录。

## 必需结构

```text
dataset/
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
```

## data.yaml 要求

`data.yaml` 需要包含 YOLOv8 可识别的路径和类别信息，尤其必须包含 `names` 字段。

示例：

```yaml
train: train/images
val: valid/images
test: test/images

names:
  0: person
  1: car
  2: bus
  3: truck
```

不要在没有真实数据和训练结果的情况下填写实验指标。
