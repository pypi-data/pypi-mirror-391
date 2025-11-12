
import torch
import torch.nn as nn
import torch.nn.functional as F

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = nn.CrossEntropyLoss(reduction='none')(inputs, targets)
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss

class StandardCrossEntropy:
    def __init__(self):
        self.criterion = nn.CrossEntropyLoss()
    
    def __call__(self, inputs, targets):
        return self.criterion(inputs, targets)

class BinaryCrossEntropy:
    def __init__(self, weight=None):
        self.criterion = nn.BCEWithLogitsLoss(weight=weight)
    
    def __call__(self, logits, targets):
        # Convert logits [batch, 2] → single output [batch, 1]
        # Take logits for positive class (class 1)
        binary_logits = logits[:, 1] - logits[:, 0]  # Log odds ratio
        targets_float = targets.float()
        return self.criterion(binary_logits, targets_float)
    
class LabelSmoothingCrossEntropy(nn.Module):
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
        
    def forward(self, inputs, targets):
        log_prob = F.log_softmax(inputs, dim=-1)
        nll_loss = -log_prob.gather(dim=-1, index=targets.unsqueeze(1))
        nll_loss = nll_loss.squeeze(1)
        smooth_loss = -log_prob.mean(dim=-1)
        loss = (1.0 - self.smoothing) * nll_loss + self.smoothing * smooth_loss
        return loss.mean()

class MarginLoss(nn.Module):
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin
        
    def forward(self, inputs, targets):
        # Convert to binary problem: positive vs negative scores
        positive_scores = inputs[range(len(targets)), targets]
        negative_scores = inputs[range(len(targets)), 1 - targets]  # For binary case
        
        losses = F.relu(self.margin - positive_scores + negative_scores)
        return losses.mean()

class DiceLoss(nn.Module):
    def __init__(self, smooth=1e-6):
        super().__init__()
        self.smooth = smooth
        
    def forward(self, inputs, targets):
        probs = F.softmax(inputs, dim=1)
        targets_one_hot = F.one_hot(targets, num_classes=inputs.size(1)).float()
        
        intersection = (probs * targets_one_hot).sum()
        union = probs.sum() + targets_one_hot.sum()
        
        dice = (2.0 * intersection + self.smooth) / (union + self.smooth)
        return 1 - dice