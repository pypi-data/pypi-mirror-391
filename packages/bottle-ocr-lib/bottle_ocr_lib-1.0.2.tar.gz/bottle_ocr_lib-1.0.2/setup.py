#!/usr/bin/env python3
"""
Setup configuration for Bottle OCR Library
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements_path = this_directory / "requirements.txt"
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [
        line.strip() 
        for line in f 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="bottle-ocr-lib",
    version="1.0.2",
    author="Michael Crosson",
    author_email="michael@bottleocr.com",
    description="Professional OCR and AI-powered prescription extraction library with secure license validation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelCrosson/bottle-ocr-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'flake8>=4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'bottle-ocr=bottle_ocr_lib.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'bottle_ocr_lib': ['config/*.json', 'config/*.yaml'],
    },
)