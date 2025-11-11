"""
MemoLib - A Python library for machine learning model training and inference
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .Model import MemoModel, IModel, eExportType, MemoResult, MemoPrediction, ModelConfig
from .Model.eModel import eModelType, eDetectionModel, eClassifyModel, eModelTask
from .DataSerializer import *
from .DatasetFormatConvert import *
from .Loss import *

__all__ = [
    "MemoModel",
    "IModel",
    "eExportType",
    "MemoResult",
    "MemoPrediction",
    "ModelConfig",
    "eModelType",
    "eDetectionModel",
    "eClassifyModel",
    "eModelTask"
]