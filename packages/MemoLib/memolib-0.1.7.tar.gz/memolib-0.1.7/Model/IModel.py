from abc import ABC, abstractmethod
from .Data.ModelConfig import ModelConfig
from enum import Enum


class eExportType(Enum):
    All = 1
    onnx = 2,
    openvino = 3


class IModel(ABC):
    @abstractmethod
    def LoadWeight(self, weightPath: str): pass

    @abstractmethod
    def LoadLabelName(self, labelPath: str): pass

    @abstractmethod
    def Predict(self, img): pass

    @abstractmethod
    def BatchPredict(self, batchImg): pass

    @abstractmethod
    def Train(self, processParam, settingParam, trainingParam,
              modelConfig: ModelConfig, callbacks=None): pass

    @abstractmethod
    def Export(self, pathToPytorchModel: str, exportType: eExportType): pass

    @abstractmethod
    def StopTraining(self): pass