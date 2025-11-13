"""
Bottle OCR Library
==================

A Python library for extracting text from pill bottle images using OCR with API key authentication.

Basic Usage:
    >>> from bottle_ocr_lib import BottleOCR
    >>> 
    >>> # Initialize with your API key
    >>> ocr = BottleOCR(api_key="your-api-key-here")
    >>> 
    >>> # Process images
    >>> result = ocr.process_images(['image1.jpg', 'image2.jpg'])
    >>> print(result['prescription'])

Author: BottleOCR Team
Version: 1.0.0
"""

__version__ = "1.0.2"
__author__ = "Michael Crosson"
__email__ = "michael@bottleocr.com"

# Main imports for easy access
from .core.ocr_processor import OCRProcessor
from .core.prescription_extractor import PrescriptionExtractor
from .auth.api_auth import APIKeyValidator
from .bottle_ocr import BottleOCR

# Public API
__all__ = [
    'BottleOCR',
    'OCRProcessor', 
    'PrescriptionExtractor',
    'APIKeyValidator',
]

# Library configuration defaults
DEFAULT_CONFIG = {
    'auth_server_url': 'http://54.226.83.55',
    'ocr_language': 'en',
    'max_image_dimension': 2048,
    'use_angle_classification': True,
    'output_format': 'json',
    'timeout_seconds': 30,
    'max_images_per_request': 10,
}