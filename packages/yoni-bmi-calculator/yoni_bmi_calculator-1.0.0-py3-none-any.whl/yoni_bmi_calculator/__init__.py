"""
Yoni BMI Calculator - A simple and comprehensive BMI calculation package

This package provides easy-to-use functions for calculating Body Mass Index (BMI)
and interpreting the results with health category classifications.

Author: Yoni
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
__author__ = "Yoni"
__email__ = "yoni@example.com"

__all__ = [
    "calculate_bmi",
    "interpret_bmi", 
    "get_ideal_weight_range",
    "bmi_with_interpretation",
    "convert_units"
]