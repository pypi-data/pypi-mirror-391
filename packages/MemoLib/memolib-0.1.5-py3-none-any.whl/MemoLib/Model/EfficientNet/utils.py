from torchvision import transforms
import yaml
import torch.nn as nn

class EfficientNetWithFeatures(nn.Module):
    """
    Universal wrapper for EfficientNet models that outputs both classification and feature maps
    Works with: B0, B1, B2, B3, B4, B5, B6, B7, V2_S, V2_M, V2_L
    Perfect for Faster-CAM in C#!

    This wrapper automatically detects the model architecture and wraps it to output:
    - logits: Classification output (B, num_classes)
    - features: Feature maps from last layer (B, C, H, W)
    """
    def __init__(self, model):
        super().__init__()

        # Store the original model components
        self.features = model.features
        self.avgpool = model.avgpool
        self.classifier = model.classifier

        # Detect model type for debugging
        model_name = model.__class__.__name__
        print(f"Wrapped model: {model_name}")

    def forward(self, x):
        # Extract features from last convolutional layer
        features = self.features(x)  # Shape: (B, C, H, W)

        # Classification path
        x = self.avgpool(features)
        x = torch.flatten(x, 1)
        logits = self.classifier(x)  # Shape: (B, num_classes)

        # Return both: classification logits AND feature maps
        return logits, features


class Utils:



    def PrepareTrain_Augmentation(settingParams, TrainingParams):
            
        transform_list = [transforms.Resize(((int)(settingParams['ImageSize']), (int)(settingParams['ImageSize'])))]
        
        if TrainingParams['FlipLR']['Value'] > 0:
            transform_list.append(transforms.RandomHorizontalFlip(p=TrainingParams['FlipLR']['Value']))  # 50% chance

        if TrainingParams['FlipUD']['Value'] > 0:
            transform_list.append(transforms.RandomVerticalFlip(p=TrainingParams['FlipUD']['Value']))  # 0% chance

        if TrainingParams['Degrees']['Value'] > 0:
            transform_list.append(transforms.RandomRotation(degrees=TrainingParams['Degrees']['Value']))  # 0 degrees

        if TrainingParams['Translate']['Value'] > 0:
            translate = TrainingParams['Translate']['Value']
            transform_list.append(transforms.RandomAffine(degrees=0, translate=(translate, translate)))  # Translate by 0.1

        if TrainingParams['Scale']['Value'] > 0:
            scale = TrainingParams['Scale']['Value']
            transform_list.append(transforms.RandomAffine(degrees=0, scale=(1-scale, 1+scale)))  # Scale by ±0.5

        if TrainingParams['Shear']['Value'] > 0:
            transform_list.append(transforms.RandomAffine(degrees=0, shear=TrainingParams['Shear']['Value']))  # 0 shear

        if TrainingParams['Perspective']['Value'] > 0:
            transform_list.append(transforms.RandomPerspective(distortion_scale=TrainingParams['Perspective']['Value'], p=0.5))  # 0 perspective

        if TrainingParams['Erasing']['Value'] > 0:
            transform_list.append(transforms.RandomErasing(p=TrainingParams['Erasing']['Value'], scale=(0.02, 0.33), ratio=(0.3, 3.3)))  # 40% chance

        
        if( TrainingParams["ColorJitterBrightness"]['Value'] > 0 or  
           TrainingParams["ColorJitterContrast"]['Value'] > 0 or
           TrainingParams["ColorJitterSaturation"]['Value'] > 0):
            
            transform_list.append(transforms.ColorJitter(brightness=TrainingParams["ColorJitterBrightness"]['Value'],
                                                         saturation=TrainingParams["ColorJitterSaturation"]['Value'],
                                                         contrast=TrainingParams["ColorJitterContrast"]['Value']))
        
        
        # # HSV adjustments (torchvision doesn't support direct HSV, so use ColorJitter)
        # if any(TrainingParams[key]['Value'] > 0 for key in ['Hsv_h', 'Hsv_s', 'Hsv_v']):
        #     transform_list.append(transforms.ColorJitter(
        #         hue=TrainingParams['Hsv_h']['Value'],  # Hue shift
        #         saturation=TrainingParams['Hsv_s']['Value'],  # Saturation shift
        #         brightness=TrainingParams['Hsv_v']['Value']  # Value/Brightness shift
        #     ))


        Train_Transform = transforms.Compose(transform_list)

        return Train_Transform

    def load_yaml(file_path):
        """Load and parse a YAML file."""
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    
    def get_input_shape(model, default_hw=(224, 224)):
        """
        Extract the input shape of a PyTorch model as a tuple of numbers.
        Args:
            model: PyTorch model (nn.Module)
            default_hw: Tuple of (height, width) for CNNs if not specified (default: (224, 224))
        Returns:
            Tuple of integers representing input shape (excluding batch dimension)
        """
        # Get the first layer
        for module in model.modules():
            if isinstance(module, (nn.Conv2d, nn.Linear, nn.LSTM, nn.GRU)):
                first_layer = module
                break
        else:
            raise ValueError("No recognizable layer (Conv2d, Linear, LSTM, GRU) found in model")

        if isinstance(first_layer, nn.Conv2d):
            # For CNNs: (channels, height, width)
            return (first_layer.in_channels,) + default_hw
        elif isinstance(first_layer, nn.Linear):
            # For linear layers: (input_features,)
            return (first_layer.in_features,)
        elif isinstance(first_layer, (nn.LSTM, nn.GRU)):
            # For RNNs: (sequence_length, input_size)
            # sequence_length is often variable, so we return input_size
            return (None, first_layer.input_size)  # None for variable sequence length
        else:
            raise ValueError("Unsupported layer type")