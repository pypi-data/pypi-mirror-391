from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simply-bmi-calculator-yash",
    version="1.0.0",
    author="Yash",
    author_email="yash@example.com",
    description="A comprehensive BMI calculator with health interpretations and unit conversions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/23soni23/simply-bmi-calculator-yash",
    project_urls={
        "Bug Tracker": "https://github.com/23soni23/simply-bmi-calculator-yash/issues",
        "Documentation": "https://github.com/23soni23/simply-bmi-calculator-yash#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - pure Python implementation
    ],
    keywords="bmi calculator health fitness body mass index weight height metric imperial",
    include_package_data=True,
    zip_safe=False,
)