"""
PyTorch Model Inference Module for Oral Cancer Detection
Matches the training architecture from oral_cancer_detection_kaggle.ipynb
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
from pathlib import Path
import logging
import time

try:
    import timm
except ImportError:
    timm = None

logger = logging.getLogger(__name__)

# Device configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Model paths
BASE_DIR = Path(__file__).resolve().parent
REGNET_MODEL_PATH = BASE_DIR / 'regnet_y320_best.pth'
VGG16_MODEL_PATH = BASE_DIR / 'vgg16_best.pth'

# Image preprocessing (matches training)
IMAGE_SIZE = 224
TRANSFORM = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# Model architectures from training notebook
class RegNetY320Model(nn.Module):
    """RegNetY320 model with custom classifier (from training notebook)"""
    def __init__(self, num_classes=2, pretrained=False):
        super(RegNetY320Model, self).__init__()

        if timm is None:
            raise ImportError("timm library required. Install with: pip install timm")

        # Load pretrained RegNetY320
        self.backbone = timm.create_model('regnety_320', pretrained=pretrained)

        # Get number of features from backbone
        num_features = self.backbone.head.fc.in_features

        # Replace head with identity
        self.backbone.head.fc = nn.Identity()

        # Custom classifier
        self.classifier = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),

            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        features = self.backbone(x)
        output = self.classifier(features)
        return output


class VGG16Model(nn.Module):
    """VGG16 model with custom classifier (from training notebook)"""
    def __init__(self, num_classes=2, pretrained=False):
        super(VGG16Model, self).__init__()

        # Load pretrained VGG16
        self.backbone = models.vgg16(pretrained=pretrained)

        # Get number of features
        num_features = self.backbone.classifier[0].in_features

        # Replace classifier
        self.backbone.classifier = nn.Sequential(
            nn.Linear(num_features, 4096),
            nn.BatchNorm1d(4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),

            nn.Linear(4096, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),

            nn.Linear(1024, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


class OralCancerModel:
    """Wrapper class for oral cancer detection models"""

    def __init__(self, model_type='regnet'):
        self.model_type = model_type
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the PyTorch model with custom architecture"""
        try:
            if self.model_type == 'regnet':
                # Create RegNetY320 model with custom architecture
                self.model = RegNetY320Model(num_classes=2, pretrained=False)

                # Load trained weights
                checkpoint = torch.load(REGNET_MODEL_PATH, map_location=DEVICE)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)

            elif self.model_type == 'vgg16':
                # Create VGG16 model with custom architecture
                self.model = VGG16Model(num_classes=2, pretrained=False)

                # Load trained weights
                checkpoint = torch.load(VGG16_MODEL_PATH, map_location=DEVICE)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)

            else:
                raise ValueError(f"Unknown model type: {self.model_type}")

            # Move model to device and set to evaluation mode
            self.model = self.model.to(DEVICE)
            self.model.eval()

            logger.info(f"{self.model_type.upper()} model loaded successfully on {DEVICE}")

        except Exception as e:
            logger.error(f"Error loading {self.model_type} model: {e}")
            raise

    def predict(self, image_path):
        """
        Make prediction on an image

        Args:
            image_path: Path to the image file or PIL Image

        Returns:
            dict: Prediction results with class and confidence
        """
        try:
            start_time = time.time()

            # Load and preprocess image
            if isinstance(image_path, str) or isinstance(image_path, Path):
                image = Image.open(image_path).convert('RGB')
            else:
                image = image_path.convert('RGB')

            # Transform image
            image_tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

            # Make prediction
            with torch.no_grad():
                output = self.model(image_tensor)
                # Get probabilities using softmax (2-class output)
                probs = F.softmax(output, dim=1)
                predicted_class = torch.argmax(probs, dim=1).item()
                confidence = probs[0, predicted_class].item()

            # Determine class (0=Normal, 1=Cancer)
            prediction_class = 'Cancer' if predicted_class == 1 else 'Non-Cancer'

            processing_time = time.time() - start_time

            return {
                'prediction': prediction_class,
                'confidence': confidence,
                'raw_probability': probs[0, 1].item(),  # Probability of cancer class
                'processing_time': processing_time,
                'model': self.model_type.upper()
            }

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise


def predict_with_both_models(image_path):
    """
    Run prediction with both RegNet and VGG16 models

    Args:
        image_path: Path to the image file

    Returns:
        dict: Results from both models
    """
    results = {}

    try:
        # RegNetY320 prediction
        regnet_model = OralCancerModel(model_type='regnet')
        results['regnet'] = regnet_model.predict(image_path)
    except Exception as e:
        logger.error(f"RegNet prediction failed: {e}")
        results['regnet'] = None

    try:
        # VGG16 prediction
        vgg_model = OralCancerModel(model_type='vgg16')
        results['vgg16'] = vgg_model.predict(image_path)
    except Exception as e:
        logger.error(f"VGG16 prediction failed: {e}")
        results['vgg16'] = None

    return results


def get_model_info():
    """Get information about available models"""
    return {
        'regnet_y320': {
            'path': str(REGNET_MODEL_PATH),
            'exists': REGNET_MODEL_PATH.exists(),
            'size_mb': REGNET_MODEL_PATH.stat().st_size / (1024 * 1024) if REGNET_MODEL_PATH.exists() else 0
        },
        'vgg16': {
            'path': str(VGG16_MODEL_PATH),
            'exists': VGG16_MODEL_PATH.exists(),
            'size_mb': VGG16_MODEL_PATH.stat().st_size / (1024 * 1024) if VGG16_MODEL_PATH.exists() else 0
        },
        'device': str(DEVICE)
    }


if __name__ == '__main__':
    # Test the models
    print("Model Information:")
    print(get_model_info())
