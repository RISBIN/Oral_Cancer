# ML Models Directory

This directory contains the trained PyTorch models for oral cancer detection.

## Required Model Files

The following model files are required but **not included in this repository** due to their large size:

- `regnet_y320_best.pth` (547 MB) - RegNetY320 trained model
- `vgg16_best.pth` (464 MB) - VGG16 trained model

## How to Obtain Models

### Option 1: Download Pre-trained Models
Contact the repository maintainer or check the releases page for download links.

### Option 2: Train Your Own Models
Use the Jupyter notebook `oral_cancer_detection_kaggle.ipynb` to train the models:

1. Prepare your oral cancer dataset
2. Run the training notebook
3. Models will be saved as `.pth` files in this directory

## Model Architecture

### RegNetY320 Model
```python
- Backbone: timm.create_model('regnety_320')
- Classifier:
  - Linear(3712, 512) + BatchNorm + ReLU + Dropout(0.5)
  - Linear(512, 256) + BatchNorm + ReLU + Dropout(0.3)
  - Linear(256, 2)
- Output: 2 classes (Normal, Cancer)
```

### VGG16 Model
```python
- Backbone: torchvision.models.vgg16
- Classifier:
  - Linear(25088, 4096) + BatchNorm + ReLU + Dropout(0.5)
  - Linear(4096, 1024) + BatchNorm + ReLU + Dropout(0.3)
  - Linear(1024, 2)
- Output: 2 classes (Normal, Cancer)
```

## Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| RegNetY320 | 89.4% | - | - | - | - |
| VGG16 | 73.7% | - | - | - | - |

## Usage

Models are automatically loaded by the Django application:

```python
from ml_models import predict_with_both_models

results = predict_with_both_models(image_path)
# Returns predictions from both models
```

## Dependencies

```bash
pip install torch==2.1.0 torchvision==0.16.0 timm==1.0.20
```

## Notes

- Models use CPU by default (CUDA support available)
- Image preprocessing: 224x224, normalized with ImageNet stats
- Inference time: ~10 seconds for both models (first run includes loading time)
