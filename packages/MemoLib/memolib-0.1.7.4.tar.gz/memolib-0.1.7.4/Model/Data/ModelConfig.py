from ...DataSerializer.ConfigClasses import Parent_Config

class ModelConfig(Parent_Config):
    def __init__(self, ModelTask: str = "", ModelType: str = "", ImageSize :int = 224, **kwargs):

        self.ModelType = ModelType
        self.ModelTask = ModelTask
        self.ImageSize = ImageSize
        
        super().__init__(**kwargs)
    def __repr__(self):
        return f"ModelConfig(ModelType={self.ModelType}, ModelTask={self.ModelTask}, ImageSize ={self.ImageSize})"