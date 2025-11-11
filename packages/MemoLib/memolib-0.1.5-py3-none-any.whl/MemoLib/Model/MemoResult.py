from dataclasses import dataclass
from .eModel import eModelTask

@dataclass
class MemoRect:
    @property
    def X(self):
        return self._X

    @property
    def Y(self):
        return self._Y

    @property
    def Width(self):
        return self._Width

    @property
    def Height(self):
        return self._Height

    def __init__(self, x : int, y: int, w: int, h: int):
        self._X = x
        self._Y = y
        self._Width = w
        self._Height = h


@dataclass
class MemoResult:
    @property
    def ClassName(self) -> str: 
        return self._className

    @property
    def ClassIndex(self) -> int:
        return self._classIndex

    @property
    def Rect(self) -> MemoRect:
        return self._Rect

    @property
    def Score(self) -> float:
        return self._Score

    def __init__(self, className: str, classIndex: int, score: float ,rect: MemoRect = None):
        self._className = className
        self._classIndex = classIndex
        self._Score = score
        self._Rect = rect


@dataclass
class MemoPrediction:
    
    @property
    def PredictionResult(self) -> list[MemoResult]:
        return self._PredictionResult
    
    @property
    def Task(self) -> eModelTask:
        return self._Task
    
    def __init__(self, modelTask: eModelTask, predictionResult : list[MemoResult]):
        self._Task = modelTask
        self._PredictionResult = predictionResult