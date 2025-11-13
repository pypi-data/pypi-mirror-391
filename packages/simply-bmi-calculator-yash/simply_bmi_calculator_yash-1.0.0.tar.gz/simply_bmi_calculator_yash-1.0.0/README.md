# 🏥 Simply BMI Calculator (Yash)

[![PyPI version](https://badge.fury.io/py/simply-bmi-calculator-yash.svg)](https://badge.fury.io/py/simply-bmi-calculator-yash)
[![Python versions](https://img.shields.io/pypi/pyversions/simply-bmi-calculator-yash.svg)](https://pypi.org/project/simply-bmi-calculator-yash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive and easy-to-use BMI (Body Mass Index) calculator package that supports both metric and imperial units, provides health interpretations, and offers additional utilities for weight management.

## ✨ Features

- 🧮 **Accurate BMI Calculation**: Calculate BMI using metric (kg/m) or imperial (lbs/inches) units
- 📊 **Health Interpretations**: Get detailed health category analysis with recommendations
- 🎯 **Ideal Weight Range**: Calculate ideal weight range for any height
- 🔄 **Unit Conversions**: Convert between different weight and height units
- 💡 **Health Advice**: Receive personalized health advice based on BMI results
- 🚀 **Easy to Use**: Simple, intuitive API for developers
- 📱 **Lightweight**: No external dependencies, pure Python implementation

## 🚀 Installation

Install the package using pip:

```bash
pip install simply-bmi-calculator-yash
```

## 📖 Quick Start

```python
from yoni_bmi_calculator import calculate_bmi, bmi_with_interpretation

# Basic BMI calculation (metric)
bmi = calculate_bmi(weight=70, height=1.75)  # 70 kg, 1.75 m
print(f"Your BMI is: {bmi}")  # Output: Your BMI is: 22.86

# Complete analysis with interpretation
result = bmi_with_interpretation(weight=70, height=1.75)
print(f"BMI: {result['bmi']}")
print(f"Category: {result['interpretation']['category']}")
print(f"Advice: {result['interpretation']['advice']}")
```

## 📚 Detailed Usage Examples

### 1. Basic BMI Calculation

```python
from yoni_bmi_calculator import calculate_bmi

# Metric system (kg, meters)
bmi_metric = calculate_bmi(weight=70, height=1.75, unit_system="metric")
print(f"BMI (metric): {bmi_metric}")

# Imperial system (pounds, inches)  
bmi_imperial = calculate_bmi(weight=154, height=69, unit_system="imperial")
print(f"BMI (imperial): {bmi_imperial}")
```

### 2. BMI Interpretation

```python
from yoni_bmi_calculator import interpret_bmi

bmi = 22.86
interpretation = interpret_bmi(bmi)

print(f"Category: {interpretation['category']}")
print(f"Description: {interpretation['description']}")
print(f"Health Advice: {interpretation['advice']}")
print(f"Risk Level: {interpretation['risk']}")
```

### 3. Complete BMI Analysis

```python
from yoni_bmi_calculator import bmi_with_interpretation

# Get complete analysis
analysis = bmi_with_interpretation(weight=70, height=1.75, unit_system="metric")

print(f"📊 BMI Analysis Results:")
print(f"BMI Score: {analysis['bmi']}")
print(f"Category: {analysis['interpretation']['category']}")
print(f"Health Status: {analysis['interpretation']['description']}")
print(f"Recommendation: {analysis['interpretation']['advice']}")

# Ideal weight range
ideal = analysis['ideal_weight_range']
print(f"💡 Ideal Weight Range: {ideal['min_weight']}-{ideal['max_weight']} {ideal['unit']}")
```

### 4. Ideal Weight Range Calculator

```python
from yoni_bmi_calculator import get_ideal_weight_range

# For someone who is 1.75m tall
ideal_range = get_ideal_weight_range(height=1.75, unit_system="metric")
print(f"Ideal weight range: {ideal_range['min_weight']}-{ideal_range['max_weight']} {ideal_range['unit']}")

# For someone who is 69 inches tall
ideal_range_imperial = get_ideal_weight_range(height=69, unit_system="imperial")
print(f"Ideal weight range: {ideal_range_imperial['min_weight']}-{ideal_range_imperial['max_weight']} {ideal_range_imperial['unit']}")
```

### 5. Unit Conversions

```python
from yoni_bmi_calculator import convert_units

# Weight conversions
kg_to_lbs = convert_units(70, "kg", "lbs")
print(f"70 kg = {kg_to_lbs} lbs")

# Height conversions
m_to_inches = convert_units(1.75, "m", "in")  
print(f"1.75 m = {m_to_inches} inches")

cm_to_feet = convert_units(175, "cm", "ft")
print(f"175 cm = {cm_to_feet} feet")
```

## 🎯 BMI Categories

The calculator uses the standard WHO BMI categories:

| BMI Range | Category | Health Risk |
|-----------|----------|-------------|
| < 18.5 | Underweight | May indicate malnutrition |
| 18.5 - 24.9 | Normal weight | Lowest risk |
| 25.0 - 29.9 | Overweight | Increased risk |
| ≥ 30.0 | Obese | High risk |

## 🔧 API Reference

### Core Functions

#### `calculate_bmi(weight, height, unit_system="metric")`
Calculate BMI from weight and height.

**Parameters:**
- `weight` (float): Weight in kg (metric) or pounds (imperial)
- `height` (float): Height in meters (metric) or inches (imperial)
- `unit_system` (str): "metric" or "imperial" (default: "metric")

**Returns:** BMI value (float)

#### `interpret_bmi(bmi)`
Get health interpretation for a BMI value.

**Parameters:**
- `bmi` (float): BMI value

**Returns:** Dictionary with category, description, advice, and risk information

#### `bmi_with_interpretation(weight, height, unit_system="metric")`
Calculate BMI and return complete analysis.

**Parameters:**
- `weight` (float): Weight in kg (metric) or pounds (imperial)
- `height` (float): Height in meters (metric) or inches (imperial)  
- `unit_system` (str): "metric" or "imperial" (default: "metric")

**Returns:** Complete analysis dictionary

#### `get_ideal_weight_range(height, unit_system="metric")`
Calculate ideal weight range for given height.

**Parameters:**
- `height` (float): Height in meters (metric) or inches (imperial)
- `unit_system` (str): "metric" or "imperial" (default: "metric")

**Returns:** Dictionary with min/max ideal weights

#### `convert_units(value, from_unit, to_unit)`
Convert between different units.

**Supported conversions:**
- Weight: kg ↔ lbs
- Height: m ↔ in ↔ cm ↔ ft

## 🏥 Health Disclaimer

**Important:** This BMI calculator is for informational purposes only and should not replace professional medical advice. BMI is a screening tool and may not be accurate for:

- Athletes with high muscle mass
- Pregnant women
- Children and adolescents
- Elderly individuals
- People with certain medical conditions

Always consult with healthcare professionals for personalized health assessments.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Yoni** - *Initial work*

## 🔗 Links

- [PyPI Project](https://pypi.org/project/yoni-bmi-calculator/)
- [GitHub Repository](https://github.com/23soni23/yoni-bmi-calculator)
- [Issue Tracker](https://github.com/23soni23/yoni-bmi-calculator/issues)

## 🆕 Version History

- **1.0.0** - Initial release with core BMI calculation and interpretation features

---

**Made with ❤️ for health and fitness enthusiasts!**