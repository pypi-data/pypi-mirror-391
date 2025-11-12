from abc import ABC
from .eModel import eModelType, eDetectionModel, eClassifyModel, eModelTask
from .EfficientNet import EfficientNetModel
from .YOLO.YOLO_Model import YOLO_Model
from .IModel import IModel, eExportType
from .MemoResult import MemoResult, MemoPrediction
from .Data.ModelConfig import ModelConfig
import os


class MemoModel(ABC):

    def __InitModel(self, modelTask: eModelTask, modelType):
        """Initialize model based on task and model type"""

        print(f"Initializing model with task: {modelTask}, model: {modelType}, model type: {type(modelType)}")

        # Handle the case where modelType is already the correct enum type
        if modelTask == eModelTask.Classification:
            # If modelType is already eClassifyModel, use it directly
            if isinstance(modelType, eClassifyModel):
                typedModelType = modelType
            else:
                # If it's an integer or eModelType, convert it
                if hasattr(modelType, 'value'):
                    model_value = modelType.value
                else:
                    model_value = modelType
                typedModelType = eClassifyModel(model_value)

            print(f"Classification model type: {typedModelType}")

            match typedModelType:
                case eClassifyModel.EfficientNetB0:
                    self.Model = EfficientNetModel.B0()
                case eClassifyModel.EfficientNetB1:
                    self.Model = EfficientNetModel.B1()
                case eClassifyModel.EfficientNetB2:
                    self.Model = EfficientNetModel.B2()
                case eClassifyModel.EfficientNetB3:
                    self.Model = EfficientNetModel.B3()
                case eClassifyModel.EfficientNetB4:
                    self.Model = EfficientNetModel.B4()
                case eClassifyModel.EfficientNetB5:
                    self.Model = EfficientNetModel.B5()
                case eClassifyModel.EfficientNetB6:
                    self.Model = EfficientNetModel.B6()
                case eClassifyModel.EfficientNetB7:
                    self.Model = EfficientNetModel.B7()
                    
                case eClassifyModel.EfficientNet_V2_S:
                    self.Model = EfficientNetModel.V2_S()
                case eClassifyModel.EfficientNet_V2_M:
                    self.Model = EfficientNetModel.V2_M()
                case eClassifyModel.EfficientNet_V2_L:
                    self.Model = EfficientNetModel.V2_L()
                case _:
                    raise ValueError(
                        f"Unknown classification model: {typedModelType}")

        elif modelTask == eModelTask.Detection:
            # If modelType is already eDetectionModel, use it directly
            if isinstance(modelType, eDetectionModel):
                typedModelType = modelType
            else:
                # If it's an integer or eModelType, convert it
                if hasattr(modelType, 'value'):
                    model_value = modelType.value
                else:
                    model_value = modelType
                typedModelType = eDetectionModel(model_value)

            print(f"Detection model type: {typedModelType}")
            self.Model = YOLO_Model(typedModelType)

        else:
            raise ValueError(f"Unknown model task: {modelTask}")

    def __init__(self, modelTask: eModelTask, modelType: eModelType, ):

        self.ModelType = modelType
        self.ModelTask = modelTask
        self.__InitModel(modelTask, modelType)
        self.IsLoaded = False

    def Train(self, processParam, settingParams, trainingParam, callbacks=None):
       
        try:
            mdConfig = ModelConfig(self.ModelTask.name, self.ModelType.name, settingParams["ImageSize"])
            self.Model.Train(processParam, settingParams,
                             trainingParam, mdConfig, callbacks)
            
            return True
        except Exception as ex:
            print(ex)
            return False
        pass
        
    def Predict(self, img) -> MemoPrediction:
        try:
            return self.Model.Predict(img)
        except Exception as ex:

            raise Exception(f"Error while predict: {ex}")
        
    def BatchPredict(self, listImg):
        try:
            return self.Model.BatchPredict(listImg)

        except Exception as ex:
            print(ex)
            raise Exception(ex)

    # def SetPredictImageSize(self, Size):
    #     self.Model.SetPredictImageSize(Size)
        
    # def LoadLabelName(self, classPath):
    #     self.Model.LoadLabelName(classPath)

    # def LoadWeight(self, weightPath):
    #     self.Model.model = self.Model.LoadWeight(weightPath)

    def LoadModel(self, classPath: str, weightPath: str, Size: int):
        try:
            self.Model.LoadLabelName(classPath)
            self.Model.model = self.Model.LoadWeight(weightPath)
            if hasattr(self.Model, 'SetPredictImageSize'):
                self.Model.SetPredictImageSize(Size)
            self.IsLoaded = True
            
        except Exception as ex:
            self.IsLoaded = False
            raise Exception(f"Exception in LoadModel: {ex}")

    def Export(self, pathToPytorchModel, exportType : eExportType):
        self.Model.Export(pathToPytorchModel, exportType)

    def StopTraining(self):
        self.Model.StopTraining()