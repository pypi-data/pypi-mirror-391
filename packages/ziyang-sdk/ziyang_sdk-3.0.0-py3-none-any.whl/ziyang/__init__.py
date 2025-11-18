# src/ziyang/__init__.py

"""Ziyang SDK v3 - 紫阳智库算力测试SDK."""

from .benchmark import BenchmarkResult, PerformanceTracker
from .core import ZiyangSDK
from .math_core import CosmicMath
from .optimization import PerformanceOptimizer

__all__ = [
    "BenchmarkResult",
    "CosmicMath",
    "PerformanceOptimizer",
    "PerformanceTracker",
    "ZiyangSDK",
]

__version__ = "3.0.0"
