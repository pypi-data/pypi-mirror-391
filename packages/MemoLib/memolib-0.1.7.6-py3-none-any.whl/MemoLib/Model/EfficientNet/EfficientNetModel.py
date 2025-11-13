from ..IModel import IModel, eExportType
import torch.nn as nn
from torchvision import models, transforms
from os import path, makedirs
import cv2 as cv
import torch
from .utils import Utils, EfficientNetWithFeatures
from ...Loss.FocalLoss import FocalLoss, BinaryCrossEntropy, StandardCrossEntropy
from torchvision import datasets
from torch import optim
import copy
from threading import Thread, Event
from torch.utils.data import DataLoader, random_split
import copy
from ..Data.ModelConfig import ModelConfig
from ..MemoResult import MemoResult, MemoPrediction
from ..eModel import eModelTask
import datetime
import torchvision
try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

class B0(IModel):
    def __init__(self,  Pretrained = True):
        self.Transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.Device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.efficientnet_b0(pretrained= Pretrained)  
        self.IsTraining = False
        
        self.IsStopTraining = False
        self.StopTrainingEvent = Event()
        
    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b0(pretrained=False)  
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

    def LoadLabelName(self, labelPath: str): 
        if path.exists(labelPath) and labelPath.endswith(".txt") :
            with open(labelPath, 'r') as file:
                lines = file.readlines()
                self.Classes = lines[0].split(' ')
                self.Classes = self.Classes[:-1]
                self.ClassesNumber = len(self.Classes)
        else:
            raise Exception("Does not support this class file format!")

    def Train(self, processParams, settingParams, trainingParams, modelConfig ,callbacks = None):
       
        try:
            if(self.IsTraining == False):
                
                self.ProcessName = processParams["process_name"]
                self.IsTraining = True
                self.Train_Transform = Utils.PrepareTrain_Augmentation(settingParams, trainingParams)

                if not any(isinstance(t, transforms.ToTensor) for t in self.Train_Transform.transforms):
                    self.Train_Transform.transforms.append(transforms.ToTensor())
                    self.Train_Transform.transforms.append(
                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    )

                dataPath = settingParams['DataPath']
                config = Utils.load_yaml(dataPath)
                self.ClassesNumber = config.get('nc')

                saveFolder = path.join("TrainResult", self.ProcessName)
                if(path.exists(saveFolder) == False): makedirs(saveFolder, exist_ok= True)
                with open(path.join(saveFolder , "memo_classes.txt"), 'w') as out:
                    for className in config['names']:
                        out.write(className + " ")
                    out.close()
                    
                modelConfig.Save(path.join(saveFolder, "ModelConfig.json"))
                
                imgSize = settingParams['ImageSize']
                batchSize = settingParams["BatchSize"]

                self.Transform = transforms.Compose([
                #    transforms.ToPILImage(),
                    transforms.Resize((imgSize, imgSize)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    ])

                train_dataset = datasets.ImageFolder( config.get('train'), transform=self.Train_Transform)
                val_dataset = datasets.ImageFolder(config.get('val'), transform=self.Transform)
                
                countLayer = 0
                
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                tensorboard_dir = path.join(saveFolder, "tensorboard_logs", f"run_{timestamp}")
                makedirs(tensorboard_dir, exist_ok=True)
                    
                if trainingParams["FreezeLayers"]['Value'] == 0:
                    for param in self.model.parameters():
                        param.requires_grad = False
                else:
                    for param in self.model.parameters():
                        param.requires_grad = False
                        countLayer +=1
                        if(countLayer == trainingParams["FreezeLayers"]['Value']): break

                self.model.classifier = nn.Sequential(
                    nn.Dropout(p=0.3),
                    nn.Linear(self.model.classifier[1].in_features, self.ClassesNumber))

                self.model = self.model.to(self.Device)
                    
                # criterion = FocalLoss(alpha=0.75, gamma=2.0)
                if(self.ClassesNumber <= 2):
                    criterion = BinaryCrossEntropy()
                else:
                    criterion = StandardCrossEntropy()
            
                optimizer = optim.Adam(self.model.classifier.parameters(), lr= settingParams["WarmupLearningRate"]) #lr=1e-3
                train_loader = DataLoader(train_dataset, batch_size=batchSize, shuffle=True)
                test_loader = DataLoader(val_dataset, batch_size=batchSize, shuffle=False)

                self.callbacks = callbacks
                trainThread = Thread(target=self.__train_model, args=(train_loader, test_loader, criterion, optimizer, settingParams, trainingParams))
                trainThread.setName("TrainThread") 
                trainThread.start()

        except Exception as ex:
            self.IsTraining = False
            
            if(callbacks != None):
                print(f"Failed to prepare training augmentation or access DataPath: {str(ex)}")
                callbacks("Error",f"There is an error while create training section:{str(ex)}")
            else:
                self.callbacks("Error",f"There is an error while create training section:{str(ex)}")
            # raise Exception(f"Failed to prepare training augmentation or access DataPath: {str(ex)}")

    def _get_current_lr(self, optimizer):
            """Get current learning rate from optimizer"""
            return optimizer.param_groups[0]['lr']

    def _log_lr_change(self, old_lr, new_lr):
        """Log learning rate changes"""
        if old_lr != new_lr:
            message = f"Learning rate reduced: {old_lr:.6f} -> {new_lr:.6f}"
            print(message)
            if self.callbacks is not None:
                self.callbacks("Info", message)

    def __train_model(self, train_loader, test_loader, criterion, optimizer, settingParams, trainingParams):

        try:
            
            num_epochs = settingParams['Epochs']
            
            best_acc = 0.0
            min_test_loss = 100.0
            bestModel = None
            scheduler = None
            
            # Early stopping parameters
            early_stop_patience = trainingParams["Patience"]["Value"]  # Stop after 10 epochs of no improvement
            early_stop_counter = 0
            best_val_loss = float('inf')

            for epoch in range(num_epochs):
                print(f'Epoch {epoch+1}/{num_epochs}')
                print('-' * 10)

                #train
                self.model.train()
                running_loss = 0.0
                correct = 0
                total = 0

                for images, labels in train_loader:
                    images, labels = images.to(self.Device), labels.to(self.Device)
                    optimizer.zero_grad()
                    outputs = self.model(images)
                    loss = criterion(outputs, labels)
                    loss.backward()
                    optimizer.step()

                    running_loss += loss.item() * images.size(0)
                    _, predicted = torch.max(outputs, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                epoch_loss = running_loss / len(train_loader.dataset)
                epoch_acc = 100 * correct / total
                print(f'Train Loss: {epoch_loss:.4f}, Train Accuracy: {epoch_acc:.2f}%')

                # Eval
                self.model.eval()
                test_loss = 0.0
                correct = 0
                total = 0

                with torch.no_grad():
                    for images, labels in test_loader:
                        images, labels = images.to(self.Device), labels.to(self.Device)
                        outputs = self.model(images)
                        loss = criterion(outputs, labels)
                        test_loss += loss.item() * images.size(0)
                        _, predicted = torch.max(outputs, 1)
                        total += labels.size(0)
                        correct += (predicted == labels).sum().item()

                epoch_test_loss = test_loss / len(test_loader.dataset)
                test_acc = 100 * correct / total
                
                if(self.callbacks != None):
                    self.callbacks("Info",f'Epoch {epoch+1}/{num_epochs}, Test Loss: {epoch_test_loss:.4f}, Test Accuracy: {test_acc:.2f}%')
                    print(f'Test Loss: {epoch_test_loss:.4f},  Accuracy: {test_acc:.2f}%')
                
                # Early stopping check
                if(early_stop_patience > 0):
                    if epoch_test_loss < best_val_loss:
                        best_val_loss = epoch_test_loss
                        early_stop_counter = 0
                        print(f'Validation loss improved to {best_val_loss:.4f}')
                    else:
                        early_stop_counter += 1
                        print(f'No improvement in validation loss for {early_stop_counter} epochs')
                        self.callbacks("Info",f'No improvement in validation loss for {early_stop_counter} epochs')
                        
                        if early_stop_counter >= early_stop_patience:
                            print(f'Early stopping triggered after {early_stop_patience} epochs of no improvement')
                            if(self.callbacks != None):
                                self.callbacks("Info", f'Early stopping triggered after {early_stop_patience} epochs of no improvement')
                                # self.callbacks("Info",f'Early stopping triggered after {early_stop_patience} epochs of no improvement')
                            break
                    
                # Lưu mô hình tốt nhất
                if(test_loss < min_test_loss):
                    min_test_loss = test_loss
                    minLossModel = copy.deepcopy(self.model)
                    self.__saveModel(minLossModel, "min_loss.pth")

                if test_acc > best_acc:
                    best_acc = test_acc
                
                # best_model_wts = copy.deepcopy(self.model.state_dict())
                    bestModel = copy.deepcopy(self.model)
                    self.__saveModel(bestModel, "best.pth")
                
                if(epoch + 1 == trainingParams["WarmupEpochs"]['Value']):
                    
                    unfreezelayer = trainingParams["UnfreezeLayers"]['Value']
                    
                    if(unfreezelayer == 0):
                        for param in self.model.features.parameters():
                            param.requires_grad = True
                    else:
                        for param in self.model.features[-unfreezelayer:].parameters():
                            param.requires_grad = True

                    optimizer = optim.Adam(self.model.parameters(), lr = settingParams["LearningRate"]) #1e-4
                    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.9, patience=5)

                if scheduler is not None:
                    old_lr = self._get_current_lr(optimizer)
                    scheduler.step(epoch_test_loss)
                    new_lr = self._get_current_lr(optimizer)
                    self._log_lr_change(old_lr, new_lr)

                if self.IsStopTraining:
                    break
                
            # Final callback with completion message and best accuracy
            if(self.callbacks != None):
                self.callbacks("Info",f'Best Test Accuracy: {best_acc:.2f}%')
            print(f'Best Test Accuracy: {best_acc:.2f}%')
            
            # Load best model
            self.__saveModel(self.model, "last.pth")

            if hasattr(self.model, 'cpu'):  
                self.model = self.model.cpu()

            del self.model
            self.model = None
            torch.cuda.empty_cache()

            self.Export(path.join("TrainResult", self.ProcessName, "Weights", "last.pth"), eExportType.openvino, settingParams['ImageSize'])
            self.Export(path.join("TrainResult", self.ProcessName, "Weights", "best.pth"), eExportType.openvino, settingParams['ImageSize'])
            
            self.Export(path.join("TrainResult", self.ProcessName, "Weights", "last.pth"), eExportType.onnx, settingParams['ImageSize'])
            self.Export(path.join("TrainResult", self.ProcessName, "Weights", "best.pth"), eExportType.onnxm, settingParams['ImageSize'])

            
            # Signal training completion
            
            self.IsTraining = False
            self.StopTrainingEvent.set()



        except Exception as ex:
            
            print(f"Exception: {str(ex)}")
            if(self.callbacks != None):
                self.callbacks("Error", f"Training error: {str(ex)}")
            
            self.IsTraining = False
        
    def __saveModel(self, model, modelName):

        pathSaveModel = path.join("TrainResult", self.ProcessName, "Weights", modelName)
        dir_to_create = path.dirname(pathSaveModel)
        makedirs(dir_to_create, exist_ok=True) 
        torch.save(model.state_dict(), pathSaveModel)

    
    def StopTraining(self):
        
        self.IsStopTraining = True
        self.StopTrainingEvent.wait()
        self.IsStopTraining = False
        
    def SetPredictImageSize(self, ImageSize: int = 224):
        self.Transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((ImageSize, ImageSize)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                    ])

    def Predict(self, img):
        if(self.IsTraining == False):
            with torch.no_grad():
                self.model = self.model.to(self.Device)
                img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

                # Apply transformations
                img_tensor = self.Transform(img_rgb).unsqueeze(0).to(self.Device)
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                _, predicted = torch.max(outputs, 1)
                predicted_class = predicted.item()
                confidence = probabilities[0][predicted_class].item()

                rs = MemoResult(self.Classes[predicted_class], predicted_class, confidence)
                
                
            return MemoPrediction(eModelTask.Classification, [rs])
        else:
            return None
    
    def BatchPredict(self, listImg):

        batchImage = []
        for img in listImg:
            img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            img_tensor = self.Transform(img_rgb)
            batchImage.append(img_tensor)
        
        batch_tensor = torch.stack(batchImage)
        batch_tensor = batch_tensor.to(self.Device)

        with torch.no_grad():
            outputs = self.model(batch_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(outputs, dim=1)

        predictions = predictions.cpu().numpy()
        probabilities = probabilities.cpu().numpy()

        ListResult = []
        for i in range(len(predictions)):
            pred_class = predictions[i]
            confidence = probabilities[i][pred_class]
            rs = MemoResult(self.Classes[pred_class], pred_class, confidence)
            
            ListResult.append(MemoPrediction(eModelTask.Classification, [rs]))
            
        return ListResult

    def Export(self, pathToPytorchModel: str, exportType : eExportType, exportImageSize: int = 224):         
        
        tempModel = self.LoadWeight(pathToPytorchModel)
        pathExport = pathToPytorchModel.split('.')[0]

        inputShape = Utils.get_input_shape(tempModel)
        dummy_input = torch.randn(1, inputShape[0], exportImageSize, exportImageSize).to(self.Device)
        if(tempModel != None):
            
            match exportType:
                case exportType.onnx:
                    
                    tempModelHM = EfficientNetWithFeatures(tempModel)
                    pathExportHeatMap = pathExport + "HM.onnx"
                    
                    torch.onnx.export(
                        tempModelHM,
                        dummy_input,
                        pathExportHeatMap,
                        input_names=['input'],
                        output_names=['output', 'features'],  
                        dynamic_axes={
                            'input': {
                              0: 'batch_size',
                            },
                            'output': {0: 'batch_size'},
                            'features': {
                                0: 'batch_size',
                            }
                        },
                        opset_version=13
                    )
                    
                    
                    pathExport += ".onnx"
                    
                    
                    torch.onnx.export(
                        tempModel,                     # Model to export
                        dummy_input,               # Dummy input for tracing
                        pathExport,              # Output file name
                        input_names=['input'],     # Name for input layer
                        output_names=['output'],   # Name for output layer
                        dynamic_axes={             # Support variable batch size
                            'input': {0: 'batch_size'},
                            'output': {0: 'batch_size'}
                        },
                        opset_version=13           # ONNX opset version (adjust if needed)
                        )



                                       
                case eExportType.openvino:
                        if not OPENVINO_AVAILABLE:
                            print("Warning: OpenVINO is not installed. Install with: pip install MemoLib[openvino]")
                            return
                        pathExport += ".xml"
                        ov_model = ov.convert_model(
                            tempModel,
                            example_input=dummy_input,
                            input=dummy_input.shape
                        )

                        ov.save_model(ov_model, pathExport)
                        
                        # ov_model = mo.convert_model(
                        # tempModel, 
                        # example_input=dummy_input,
                        # input_shape=dummy_input.shape()
                        # )
                        # ov.save_model(ov_model, pathExport)
        

        if hasattr(tempModel, 'cpu'):  
            tempModel = tempModel.cpu()

        del tempModel
        tempModel = None
        torch.cuda.empty_cache()

class B1(B0):

    def __init__(self):
        super().__init__() 
        self.model = models.efficientnet_b1(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b1(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")
        
class B2(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b2(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b2(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")
        
class B3(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b3(pretrained=False)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b3(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )
            
            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

class B4(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b4(pretrained=False)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b4(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

class B5(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b5(pretrained=False)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b5(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

class B6(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b6(pretrained=False)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b6(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

class B7(B0):
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_b7(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_b7(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")
    
class V2_S(B0):
    
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_v2_s(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 

        if(path.exists(weightPath)):
            tempModel = models.efficientnet_v2_s(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")
        
class V2_M(B0):
    
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_v2_m(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 
        if(path.exists(weightPath)):
            tempModel = models.efficientnet_v2_m(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")

class V2_L(B0):
    
    def __init__(self):
        super().__init__()
        self.model = models.efficientnet_v2_l(pretrained=True)  # Load without pretrained weights

    def LoadWeight(self, weightPath: str): 
        if(path.exists(weightPath)):
            tempModel = models.efficientnet_v2_l(pretrained=False)  # Load without pretrained weights
            tempModel.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(tempModel.classifier[1].in_features, self.ClassesNumber)
            )

            tempModel.load_state_dict(torch.load(weightPath, map_location=self.Device))
            tempModel.to(self.Device)
            tempModel.eval()
            
            return tempModel

        else:
            raise Exception("Not found weight path!")
        
        