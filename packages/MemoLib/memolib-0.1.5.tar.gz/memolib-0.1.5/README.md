# MemoLib

[![PyPI version](https://badge.fury.io/py/MemoLib.svg)](https://badge.fury.io/py/MemoLib)
[![Python Version](https://img.shields.io/pypi/pyversions/MemoLib.svg)](https://pypi.org/project/MemoLib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/memolib)](https://pepy.tech/project/memolib)

A comprehensive Python library for machine learning model training and inference, supporting both classification and object detection tasks with state-of-the-art models.

## Features

- **Multiple Model Architectures**
  - EfficientNet (B0-B7, EfficientNetV2)
  - YOLO series for object detection

- **Flexible Task Support**
  - Image Classification
  - Object Detection

- **Export Capabilities**
  - ONNX format for cross-platform deployment
  - OpenVINO format for Intel hardware optimization

- **Training Pipeline**
  - Built-in training loops with customizable callbacks
  - Support for custom loss functions (FocalLoss, etc.)
  - Easy model configuration via YAML/JSON

- **Utilities**
  - Dataset format conversion tools
  - Data serialization and configuration management
  - Image preprocessing and augmentation

## Installation

Install MemoLib using pip:

```bash
pip install MemoLib
```

For development with optional dependencies:

```bash
# With OpenVINO support
pip install MemoLib[openvino]

# All optional dependencies
pip install MemoLib[all]

# Development tools
pip install MemoLib[dev]
```

## Quick Start

### Classification Example

```python
from MemoLib import MemoModel, eModelTask, eClassifyModel

# Create a classification model (EfficientNet-B0)
model = MemoModel(eModelTask.Classification, eClassifyModel.EfficientNetB0)

# Load pretrained weights and class labels
model.LoadWeight("path/to/weights.pth")
model.LoadLabelName("path/to/labels.txt")

# Make predictions on an image
result = model.Predict("path/to/image.jpg")
print(f"Prediction: {result.label}")
print(f"Confidence: {result.confidence:.2f}")
```

### Object Detection Example

```python
from MemoLib import MemoModel, eModelTask, eDetectModel

# Create a YOLO detection model
model = MemoModel(eModelTask.ObjectDetection, eDetectModel.YOLOv8)

# Load weights
model.LoadWeight("yolov8n.pt")

# Detect objects in image
results = model.Predict("path/to/image.jpg")
for detection in results:
    print(f"Class: {detection.label}, Confidence: {detection.confidence:.2f}")
    print(f"BBox: {detection.bbox}")
```

### Model Export

```python
# Export to ONNX
model.ExportToONNX("model.onnx")

# Export to OpenVINO (requires openvino package)
model.ExportToOpenVINO("model.xml")
```

## Package Structure

```
MemoLib/
├── Model/              # Core model implementations
│   ├── Data/          # Data loading and preprocessing
│   ├── EfficientNet/  # EfficientNet model variants
│   └── YOLO/          # YOLO detection models
├── DataSerializer/     # Configuration management
├── DatasetFormatConvert/  # Dataset conversion utilities
└── Loss/              # Custom loss functions (FocalLoss, etc.)
```

## Supported Models

### Classification
- EfficientNet-B0 to B7
- EfficientNetV2-S, M, L

### Object Detection
- YOLOv5
- YOLOv8
- YOLOv9
- YOLO11

## Requirements

- Python >= 3.8
- PyTorch >= 1.12.0
- TorchVision >= 0.13.0
- OpenCV >= 4.5.0
- Ultralytics >= 8.0.0
- EfficientNet-PyTorch >= 0.7.0

See [pyproject.toml](pyproject.toml) for full dependency list.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Issues

If you encounter any problems or have suggestions, please [open an issue](https://github.com/NghiaKTHP/MemoLib/issues).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**NghiaKTHP**
- GitHub: [@NghiaKTHP](https://github.com/NghiaKTHP)
- PyPI: [MemoLib](https://pypi.org/project/MemoLib/)

## Changelog

### Version 0.1.5
- Added GitHub repository links
- Improved documentation
- Updated package metadata

### Version 0.1.4
- Initial PyPI release
- Support for EfficientNet and YOLO models
- ONNX and OpenVINO export capabilities