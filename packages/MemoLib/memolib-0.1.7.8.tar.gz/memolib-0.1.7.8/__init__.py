"""
MemoLib - A Python library for machine learning model training and inference
"""

try:
    from importlib.metadata import version, metadata

    __version__ = version("MemoLib")
    _meta = metadata("MemoLib")
    __description__ = _meta["Summary"]
    __license__ = _meta["License"]
    __author__ = _meta["Author"]
    __email__ = _meta["Author-email"]
except Exception:
    # Fallback values if package is not installed
    __version__ = "0.1.7"
    __description__ = "A Python library for machine learning model training and inference"
    __license__ = "MIT"
    __author__ = "NghiaPham"
    __email__ = "nghiaphamkthp2401@gmail.com"

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