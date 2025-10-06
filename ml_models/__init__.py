"""
ML Models Package for Oral Cancer Detection
"""
from .inference import OralCancerModel, predict_with_both_models, get_model_info

__all__ = ['OralCancerModel', 'predict_with_both_models', 'get_model_info']
