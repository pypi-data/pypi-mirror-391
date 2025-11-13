"""
BMI Calculator Module

This module provides functions to calculate Body Mass Index (BMI) and interpret the results.
It supports different unit systems and provides comprehensive health category interpretations.
"""

def calculate_bmi(weight, height, unit_system="metric"):
    """
    Calculate Body Mass Index (BMI)
    
    Args:
        weight (float): Weight in kg (metric) or pounds (imperial)
        height (float): Height in meters (metric) or inches (imperial)  
        unit_system (str): "metric" or "imperial" (default: "metric")
        
    Returns:
        float: BMI value rounded to 2 decimal places
        
    Raises:
        ValueError: If weight or height are not positive numbers
        ValueError: If unit_system is not "metric" or "imperial"
    """
    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be positive numbers")
        
    if unit_system not in ["metric", "imperial"]:
        raise ValueError("Unit system must be 'metric' or 'imperial'")
    
    if unit_system == "imperial":
        # Convert imperial to metric: weight(lbs) * 0.453592, height(inches) * 0.0254
        weight = weight * 0.453592
        height = height * 0.0254
    
    bmi = weight / (height ** 2)
    return round(bmi, 2)


def interpret_bmi(bmi):
    """
    Interpret BMI value and return health category
    
    Args:
        bmi (float): BMI value
        
    Returns:
        dict: Dictionary containing category, description, and health advice
    """
    if bmi < 18.5:
        return {
            "category": "Underweight",
            "description": "Below normal weight",
            "advice": "Consider consulting a healthcare provider about healthy weight gain strategies.",
            "risk": "May indicate malnutrition or other health issues"
        }
    elif 18.5 <= bmi < 25:
        return {
            "category": "Normal weight", 
            "description": "Healthy weight range",
            "advice": "Maintain current lifestyle with balanced diet and regular exercise.",
            "risk": "Lowest risk for weight-related health problems"
        }
    elif 25 <= bmi < 30:
        return {
            "category": "Overweight",
            "description": "Above normal weight",
            "advice": "Consider lifestyle changes including diet and exercise modifications.",
            "risk": "Increased risk of cardiovascular disease and diabetes"
        }
    else:  # bmi >= 30
        return {
            "category": "Obese",
            "description": "Significantly above normal weight", 
            "advice": "Strongly recommend consulting healthcare provider for weight management plan.",
            "risk": "High risk of serious health complications"
        }


def get_ideal_weight_range(height, unit_system="metric"):
    """
    Calculate ideal weight range for given height (BMI 18.5-24.9)
    
    Args:
        height (float): Height in meters (metric) or inches (imperial)
        unit_system (str): "metric" or "imperial" (default: "metric")
        
    Returns:
        dict: Dictionary with min and max ideal weights
    """
    if height <= 0:
        raise ValueError("Height must be a positive number")
        
    if unit_system not in ["metric", "imperial"]:
        raise ValueError("Unit system must be 'metric' or 'imperial'")
    
    # Convert to metric if needed
    height_m = height
    if unit_system == "imperial":
        height_m = height * 0.0254
    
    # Calculate ideal weight range (BMI 18.5 to 24.9)
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    
    # Convert back to original unit system if needed
    if unit_system == "imperial":
        min_weight = min_weight / 0.453592  # Convert to pounds
        max_weight = max_weight / 0.453592
        unit = "lbs"
    else:
        unit = "kg"
    
    return {
        "min_weight": round(min_weight, 1),
        "max_weight": round(max_weight, 1),
        "unit": unit
    }


def bmi_with_interpretation(weight, height, unit_system="metric"):
    """
    Calculate BMI and return complete analysis with interpretation
    
    Args:
        weight (float): Weight in kg (metric) or pounds (imperial)
        height (float): Height in meters (metric) or inches (imperial)
        unit_system (str): "metric" or "imperial" (default: "metric")
        
    Returns:
        dict: Complete BMI analysis with interpretation and recommendations
    """
    bmi = calculate_bmi(weight, height, unit_system)
    interpretation = interpret_bmi(bmi)
    ideal_range = get_ideal_weight_range(height, unit_system)
    
    return {
        "bmi": bmi,
        "weight": weight,
        "height": height,
        "unit_system": unit_system,
        "interpretation": interpretation,
        "ideal_weight_range": ideal_range
    }


def convert_units(value, from_unit, to_unit):
    """
    Convert between different units
    
    Args:
        value (float): Value to convert
        from_unit (str): Source unit ("kg", "lbs", "m", "in", "cm", "ft")
        to_unit (str): Target unit ("kg", "lbs", "m", "in", "cm", "ft")
        
    Returns:
        float: Converted value rounded to appropriate decimal places
    """
    # Weight conversions
    if from_unit == "kg" and to_unit == "lbs":
        return round(value / 0.453592, 1)
    elif from_unit == "lbs" and to_unit == "kg":
        return round(value * 0.453592, 1)
    
    # Height conversions
    elif from_unit == "m" and to_unit == "in":
        return round(value / 0.0254, 1)
    elif from_unit == "in" and to_unit == "m":
        return round(value * 0.0254, 3)
    elif from_unit == "cm" and to_unit == "m":
        return round(value / 100, 3)
    elif from_unit == "m" and to_unit == "cm":
        return round(value * 100, 1)
    elif from_unit == "cm" and to_unit == "in":
        return round(value / 2.54, 1)
    elif from_unit == "in" and to_unit == "cm":
        return round(value * 2.54, 1)
    elif from_unit == "ft" and to_unit == "m":
        return round(value * 0.3048, 3)
    elif from_unit == "m" and to_unit == "ft":
        return round(value / 0.3048, 1)
    elif from_unit == "ft" and to_unit == "in":
        return round(value * 12, 1)
    elif from_unit == "in" and to_unit == "ft":
        return round(value / 12, 2)
    else:
        if from_unit == to_unit:
            return value
        else:
            raise ValueError(f"Conversion from {from_unit} to {to_unit} is not supported")