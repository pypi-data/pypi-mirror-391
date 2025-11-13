from enum import Enum


class eModelType(Enum):
    pass

class eDetectionModel(eModelType):
    YoloV5n = 0
    YoloV5s = 1
    YoloV5m = 2
    YoloV5l = 3
    YoloV5x = 4
    YoloV8n = 5
    YoloV8s = 6
    YoloV8m = 7
    YoloV8l = 8
    YoloV8x = 9
    YOlo12n = 10
    YOlo12s = 11
    YOlo12m = 12
    YOlo12l = 13
    YOlo12x = 14

class eClassifyModel(eModelType):
    EfficientNetB0 = 1
    EfficientNetB1 = 2
    EfficientNetB2 = 3
    EfficientNetB3 = 4
    EfficientNetB4 = 5
    EfficientNetB5 = 6
    EfficientNetB6 = 7
    EfficientNetB7 = 8
    EfficientNet_V2_S = 9
    EfficientNet_V2_L = 10
    EfficientNet_V2_M = 11
    
class eModelTask(Enum):
    Detection = 1
    Classification = 2

    

