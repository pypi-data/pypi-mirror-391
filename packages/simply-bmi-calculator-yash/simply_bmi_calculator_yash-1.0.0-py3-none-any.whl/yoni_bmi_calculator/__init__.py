"""
Simply BMI Calculator (Yash) - A simple and comprehensive BMI calculation package

This package provides easy-to-use functions for calculating Body Mass Index (BMI)
and interpreting the results with health category classifications.

Author: Yash
Version: 1.0.0
"""

from .bmi_calculator import (
    calculate_bmi,
    interpret_bmi,
    get_ideal_weight_range,
    bmi_with_interpretation,
    convert_units
)

__version__ = "1.0.0"
__author__ = "Yash"
__email__ = "yash@example.com"

__all__ = [
    "calculate_bmi",
    "interpret_bmi", 
    "get_ideal_weight_range",
    "bmi_with_interpretation",
    "convert_units"
]