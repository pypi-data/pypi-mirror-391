# MemoLib

A Python library for machine learning model training and inference, supporting classification and object detection tasks.

## Features

- **Model Support**: EfficientNet (B0-B7, V2), YOLO models
- **Tasks**: Classification and Object Detection
- **Export**: Support for ONNX and OpenVINO formats
- **Training**: Built-in training pipeline with callbacks
- **Utilities**: Dataset format conversion, custom loss functions

## Installation

```bash
pip install MemoLib
```

## Quick Start

```python
from MemoLib import MemoModel, eModelTask, eClassifyModel

# Create a classification model
model = MemoModel(eModelTask.Classification, eClassifyModel.EfficientNetB0)

# Load weights and labels
model.LoadWeight("path/to/weights.pth")
model.LoadLabelName("path/to/labels.txt")

# Make predictions
result = model.Predict(image)
print(f"Prediction: {result.label}, Confidence: {result.confidence}")
```

## Modules

- **Model**: Core model classes and interfaces
- **DataSerializer**: Configuration and serialization utilities
- **DatasetFormatConvert**: Dataset format conversion tools
- **Loss**: Custom loss functions (FocalLoss)

## Requirements

- Python >= 3.8
- PyTorch >= 1.12.0
- OpenCV >= 4.5.0
- Other dependencies listed in pyproject.toml

## License

MIT License