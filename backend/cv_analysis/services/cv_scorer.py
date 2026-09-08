"""Backward-compatible wrapper for CV scoring.

This module keeps the historical import path working while the actual
implementation lives in cv_analyzer.py.
"""

from .cv_analyzer import calculate_cv_score

__all__ = ["calculate_cv_score"]
