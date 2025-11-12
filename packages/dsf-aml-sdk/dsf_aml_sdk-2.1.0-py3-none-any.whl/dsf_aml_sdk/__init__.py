# ============================================
# dsf_aml_sdk/__init__.py
# ============================================
"""DSF AML SDK - Adaptive Machine Learning with Knowledge Distillation"""

__version__ = '2.1.0'
__author__ = 'https://dsfuptech.cloud'
__email__ = 'contacto@dsfuptech.cloud'

from .client import AMLSDK
from .exceptions import AMLSDKError, ValidationError, LicenseError, APIError, RateLimitError
from .models import Field, Config, EvaluationResult, DistillationResult

__all__ = [
    'AMLSDK',
    'Field',
    'Config',
    'EvaluationResult',
    'DistillationResult',
    'AMLSDKError',
    'ValidationError',
    'LicenseError',
    'APIError',
    'RateLimitError'
]