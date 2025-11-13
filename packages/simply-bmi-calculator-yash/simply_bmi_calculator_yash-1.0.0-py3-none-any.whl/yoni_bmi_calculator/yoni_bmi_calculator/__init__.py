"""
Yoni BMI Calculator - A simple and easy-to-use BMI (Body Mass Index) calculator package.

This package provides functions to calculate BMI using different unit systems
and includes BMI category classification.

Author: Yoni (via 23soni23)
Version: 1.0.0
"""

from .calculator import (
    calculate_bmi,
    calculate_bmi_metric,
    calculate_bmi_imperial,
    get_bmi_category,
    get_bmi_info,
    BMICategory
)

__version__ = "1.0.0"
__author__ = "Yoni"
__email__ = "23soni23@example.com"

__all__ = [
    "calculate_bmi",
    "calculate_bmi_metric", 
    "calculate_bmi_imperial",
    "get_bmi_category",
    "get_bmi_info",
    "BMICategory"
]