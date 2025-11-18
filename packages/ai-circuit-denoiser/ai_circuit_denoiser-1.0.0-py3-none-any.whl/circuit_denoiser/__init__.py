"""
AI Circuit Denoiser - A deep learning-based tool for circuit signal denoising.
"""

__version__ = "1.0.0"
__author__ = "Michael Zhou"
__email__ = "your-email@example.com"

# 导入主要类以便可以直接从包中访问
from .denoiser_engine import DenoiserEngine
from .model import UNet1D

# 明确导出这些类
__all__ = ["DenoiserEngine", "UNet1D"]
