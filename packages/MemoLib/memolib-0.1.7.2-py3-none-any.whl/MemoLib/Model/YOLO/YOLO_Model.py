from ultralytics import YOLO
from ..IModel import IModel, eExportType
from ..eModel import eModelType, eModelTask
from os import path, makedirs
from threading import Event, Thread
from .utils import Utils
import torch
from ..MemoResult import MemoResult, MemoRect, MemoPrediction
import numpy as np
import cv2 as cv
import multiprocessing
import copy
import time

class CommunicateData:
    
    def __init__(self, logType, Msg):
         self.LogType = logType
         self.Message = Msg

class ReferingMultiProcessData:
    
    def __init__(self, stopEvent):
        self.StopEvent = stopEvent
    
    def SetCommunicationQueue(self, qLoggingMultiProcess):
        self.qLoggingMultiProcess : multiprocessing.Queue = qLoggingMultiProcess
        
    def _create_epoch_end_callback(self):
        
        def on_fit_epoch_end(trainer):    
            if(self.qLoggingMultiProcess is not None):
                if(self.StopEvent.is_set()):
                    trainer.stop_training = True
                    self.qLoggingMultiProcess.put(CommunicateData("Info", "Training stopped by user"))
                
                epoch = trainer.epoch + 1
                total_epochs = trainer.epochs
                metrics = trainer.metrics

                test_loss = metrics.get('val/cls_loss', 0)# + metrics.get('val/box_loss', 0)
                test_accuracy = metrics.get('metrics/mAP50-95(B)', 0) * 100  # Adjust based on what's available

                if epoch == 1:
                    self.best_acc = test_accuracy
                else:
                    if test_accuracy > self.best_acc:
                        self.best_acc = test_accuracy

                self.qLoggingMultiProcess.put(CommunicateData("Info", f'Epoch {epoch}/{total_epochs}, Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%'))
                print(f'Test Loss: {test_loss:.4f}, Accuracy: {test_accuracy:.2f}%, size: {self.qLoggingMultiProcess.qsize()}')
                
                if epoch == total_epochs:
                    self.qLoggingMultiProcess.put(CommunicateData("Info", f'Best Test Accuracy: {self.best_acc:.2f}%'))
        return on_fit_epoch_end

class MultiProcessForYolo:
    
    def __init__(self, qLoggingMultiProcess):
        self.qLoggingMultiProcess = qLoggingMultiProcess
    
    
    def StartTraining(self, model_path, data, epochs, imgsz, project, name, batch, 
                    exist_ok, stopEvent, augment_args ):
        
        referingData = ReferingMultiProcessData(stopEvent)
        referingData.SetCommunicationQueue(self.qLoggingMultiProcess)
        
        model = YOLO(model_path)
        model.add_callback("on_train_epoch_end", referingData._create_epoch_end_callback())
        model.train(data = data, epochs = epochs, imgsz = imgsz, 
                            project= project, name = name, batch= batch, 
                            exist_ok= exist_ok, close_mosaic=0,**augment_args) 
        stopEvent.set()

class YOLO_Model(IModel):

    def __init__(self, ModelType : eModelType):
        
        self.ModelType = ModelType
        self.model  = YOLO(ModelType.name.lower() + '.pt')  
        self.IsTraining = False
        
        self.StopEventMultiProc = multiprocessing.Event()
        self.StopTrainingEvent = Event()
        self.Device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device=self.Device)

    def LoadWeight(self, weightPath: str):   
        tempModel = YOLO(weightPath)
        tempModel.to(self.Device)
        tempModel.fuse()
        return tempModel

    def LoadLabelName(self, labelPath: str): 
        if path.exists(labelPath) and labelPath.endswith(".txt") :
            with open(labelPath, 'r') as file:
                lines = file.readlines()
                self.Classes = lines[0].split(' ')
                self.Classes = self.Classes[:-1]
                self.ClassesNumber = len(self.Classes)
        else:
            raise Exception("Does not support this class file format!")

    def Predict(self, img) -> MemoPrediction: 
        
        listMemoResult = []
        with torch.no_grad():  
            results =  self.model.predict(img)

            for rs in results:
                rects = rs.boxes.xywh.cpu().numpy()
                confs = rs.boxes.conf.cpu().numpy()
                class_ids=rs.boxes.cls.cpu().numpy()
                
                for (rect, conf, class_id) in zip(rects, confs, class_ids):
                    memoRect = MemoRect((int)(rect[0]), (int)(rect[1]), (int)(rect[2]), (int)(rect[3]))
                    try:
                        memoRs = MemoResult(self.Classes[(int)(class_id)], (int)(class_id), conf, memoRect)
                    
                        listMemoResult.append(memoRs)
                    except:

                        raise Exception(f"============================Index: {class_id}. {','.join(map(str, self.Classes))}")

        pred = MemoPrediction(eModelTask.Detection, listMemoResult)       
            
        return pred
    
    def SetPredictImageSize(self, ImageSize: int = 224): pass
    
    
    def StopTraining(self):
        self.StopEventMultiProc.set()
        self.StopTrainingEvent.wait()
    
    def BatchPredict(self, batchImg): pass    
    
    
    def Train(self, processParams, settingParams, trainingParams, modelConfig,callbacks =None): 
        try:    
            if(self.IsTraining == False):

                self.ProcessName = processParams["process_name"]
                self.IsTraining = True
                
                dataPath = settingParams['DataPath']
                imgSize = settingParams['ImageSize']
                batchSize = settingParams['BatchSize']

                augment_args = {
                    'flipud': trainingParams["FlipUD"]["Value"],
                    'fliplr': trainingParams["FlipLR"]["Value"],
                    'degrees': trainingParams["Degrees"]["Value"],
                    'translate': trainingParams["Translate"]["Value"],
                    'scale': trainingParams["Scale"]["Value"],
                    'shear': trainingParams["Shear"]["Value"],
                    'perspective': trainingParams["Perspective"]["Value"],
                    'erasing': trainingParams["Erasing"]["Value"],
                    'copy_paste': trainingParams["CopyPaste"]["Value"],
                    'mixup': trainingParams["Mixup"]["Value"],
                    'mosaic': trainingParams["Mosaic"]["Value"],
                }
                
                saveFolder = path.join("TrainResult", self.ProcessName)
                if(path.exists(saveFolder) == False): makedirs(saveFolder, exist_ok= True)
                modelConfig.Save(path.join(saveFolder, "ModelConfig.json"))
                
                config = Utils.load_yaml(dataPath)
                
                self.Classes = config.get("names")
                with open(path.join(saveFolder , "memo_classes.txt"), 'w') as out:
                    for className in config.get("names"):
                        out.write(className + " ")
                    out.close()
                    
                self.ClassesNumber = config.get('nc')
                
                self.callbacks = callbacks
                
                epochs = settingParams['Epochs']
                procName = self.ProcessName
                
                qLoggingMultiProcess = multiprocessing.Queue()
                multiProcessForYolo = MultiProcessForYolo(qLoggingMultiProcess)
                
                threadReadData = Thread(target=self.__GetCallBackFromMultiProc, args=(qLoggingMultiProcess, ))
                threadReadData.start()
                
                ProcessYolo = multiprocessing.Process(
                    target = MultiProcessForYolo.StartTraining, args=(multiProcessForYolo,
                        self.ModelType.name.lower() + '.pt',  
                        dataPath, epochs, imgSize, "TrainResult", procName, batchSize,
                        True, self.StopEventMultiProc, augment_args))

                ProcessYolo.start()
                
                ProcessYolo.join()
                threadReadData.join()
                time.sleep(5)
                
                if(callbacks != None):
                    callbacks("Info", "complete")
                
                self.Export(path.join("TrainResult", self.ProcessName, "Weights", "last.pt"), eExportType.All)
                self.Export(path.join("TrainResult", self.ProcessName, "Weights", "best.pt"), eExportType.All)

                pathSaveConfig = path.join("TrainResult", processParams["process_name"])
                modelConfig.Save(path.join(pathSaveConfig, "ModelConfig.json"))
                self.StopTrainingEvent.set()
                self.StopEventMultiProc.set()

        except Exception as ex:
            self.IsTraining = False
            if(callbacks != None):
                print(f"Failed to prepare training augmentation or access DataPath: {str(ex)}")
                callbacks("Error",f"There is an error while create training section:{str(ex)}")
            else:
                self.callbacks("Error",f"There is an error while create training section:{str(ex)}")
            raise Exception(f"Failed to prepare training augmentation or access DataPath: {str(ex)}")

    def __GetCallBackFromMultiProc(self, qLoggingMultiProcess):
        
        while not self.StopEventMultiProc.is_set():
            if(qLoggingMultiProcess.qsize() > 0):
                data: CommunicateData = qLoggingMultiProcess.get()
                if(self.callbacks is not None):
                    self.callbacks(data.LogType, data.Message)
            else:
                time.sleep(1)

    def Export(self, pathToPytorchModel: str ,exportType : eExportType): 
        
        tempModel = YOLO(pathToPytorchModel)

        match exportType:
            case eExportType.onnx:
                tempModel.export(format="onnx")
            case eExportType.openvino: 
                tempModel.export(format="openvino")
            case eExportType.All:
                self.Export(pathToPytorchModel, eExportType.onnx)
                self.Export(pathToPytorchModel, eExportType.openvino)

        del tempModel