"""
Input Validation Module
======================

Validates inputs for the BottleOCR library to ensure proper types and ranges.
"""

import os
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
import logging
from PIL import Image
import numpy as np


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """
    Validates inputs for BottleOCR operations.
    
    Handles validation of:
    - API keys
    - Image inputs
    - Configuration parameters
    - File paths
    """
    
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Maximum file sizes (in bytes)
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_IMAGE_SIZE = 100  # 100 bytes
    
    def __init__(self, max_images_per_request: int = 10):
        """
        Initialize validator.
        
        Args:
            max_images_per_request: Maximum number of images per request
        """
        self.max_images_per_request = max_images_per_request
        logger.debug(f"InputValidator initialized with max_images={max_images_per_request}")
    
    def validate_api_key(self, api_key: str) -> str:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Cleaned API key
            
        Raises:
            ValidationError: If API key is invalid
        """
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        if not isinstance(api_key, str):
            raise ValidationError("API key must be a string")
        
        api_key = api_key.strip()
        
        if len(api_key) < 8:
            raise ValidationError("API key must be at least 8 characters long")
        
        if len(api_key) > 200:
            raise ValidationError("API key is too long (max 200 characters)")
        
        # Basic format validation (adjust based on your API key format)
        if not api_key.replace('-', '').replace('_', '').isalnum():
            raise ValidationError("API key contains invalid characters")
        
        logger.debug(f"API key validated (length: {len(api_key)})")
        return api_key
    
    def validate_image_input(self, image_input: Union[str, bytes, np.ndarray, Image.Image]) -> Dict[str, Any]:
        """
        Validate a single image input.
        
        Args:
            image_input: Image in various formats
            
        Returns:
            Dictionary with validation results and metadata
            
        Raises:
            ValidationError: If image is invalid
        """
        validation_result = {
            'input_type': type(image_input).__name__,
            'size_bytes': 0,
            'dimensions': None,
            'format': None,
            'valid': False
        }
        
        try:
            if isinstance(image_input, str):
                # File path
                validation_result.update(self._validate_image_path(image_input))
                
            elif isinstance(image_input, bytes):
                # Bytes data
                validation_result.update(self._validate_image_bytes(image_input))
                
            elif isinstance(image_input, np.ndarray):
                # Numpy array
                validation_result.update(self._validate_image_array(image_input))
                
            elif isinstance(image_input, Image.Image):
                # PIL Image
                validation_result.update(self._validate_pil_image(image_input))
                
            else:
                raise ValidationError(f"Unsupported image input type: {type(image_input)}")
            
            validation_result['valid'] = True
            logger.debug(f"Image validation passed: {validation_result['input_type']}")
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            validation_result['error'] = str(e)
            raise ValidationError(f"Invalid image input: {str(e)}")
        
        return validation_result
    
    def _validate_image_path(self, file_path: str) -> Dict[str, Any]:
        """Validate image file path."""
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"Image file not found: {file_path}")
        
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in self.SUPPORTED_IMAGE_FORMATS:
            raise ValidationError(
                f"Unsupported image format: {path.suffix}. "
                f"Supported formats: {', '.join(self.SUPPORTED_IMAGE_FORMATS)}"
            )
        
        # Check file size
        size_bytes = path.stat().st_size
        
        if size_bytes < self.MIN_IMAGE_SIZE:
            raise ValidationError(f"Image file too small: {size_bytes} bytes")
        
        if size_bytes > self.MAX_IMAGE_SIZE:
            raise ValidationError(
                f"Image file too large: {size_bytes} bytes (max: {self.MAX_IMAGE_SIZE})"
            )
        
        # Try to open image to validate format
        try:
            with Image.open(path) as img:
                dimensions = img.size
                format_name = img.format
        except Exception as e:
            raise ValidationError(f"Cannot open image file: {str(e)}")
        
        return {
            'size_bytes': size_bytes,
            'dimensions': dimensions,
            'format': format_name,
            'path': str(path.resolve())
        }
    
    def _validate_image_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """Validate image bytes data."""
        size_bytes = len(image_bytes)
        
        if size_bytes < self.MIN_IMAGE_SIZE:
            raise ValidationError(f"Image data too small: {size_bytes} bytes")
        
        if size_bytes > self.MAX_IMAGE_SIZE:
            raise ValidationError(
                f"Image data too large: {size_bytes} bytes (max: {self.MAX_IMAGE_SIZE})"
            )
        
        # Try to decode image
        try:
            import io
            with Image.open(io.BytesIO(image_bytes)) as img:
                dimensions = img.size
                format_name = img.format
        except Exception as e:
            raise ValidationError(f"Cannot decode image bytes: {str(e)}")
        
        return {
            'size_bytes': size_bytes,
            'dimensions': dimensions,
            'format': format_name
        }
    
    def _validate_image_array(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Validate numpy image array."""
        if len(image_array.shape) not in [2, 3]:
            raise ValidationError(
                f"Image array must be 2D or 3D, got {len(image_array.shape)}D"
            )
        
        if len(image_array.shape) == 3:
            height, width, channels = image_array.shape
            if channels not in [1, 3, 4]:
                raise ValidationError(
                    f"Image array must have 1, 3, or 4 channels, got {channels}"
                )
        else:
            height, width = image_array.shape
            channels = 1
        
        # Check dimensions
        if height < 10 or width < 10:
            raise ValidationError(f"Image too small: {width}x{height} (min: 10x10)")
        
        if height > 10000 or width > 10000:
            raise ValidationError(f"Image too large: {width}x{height} (max: 10000x10000)")
        
        # Estimate size
        size_bytes = image_array.nbytes
        
        return {
            'size_bytes': size_bytes,
            'dimensions': (width, height),
            'format': f'numpy_{image_array.dtype}',
            'channels': channels
        }
    
    def _validate_pil_image(self, pil_image: Image.Image) -> Dict[str, Any]:
        """Validate PIL Image."""
        dimensions = pil_image.size
        width, height = dimensions
        
        # Check dimensions
        if height < 10 or width < 10:
            raise ValidationError(f"Image too small: {width}x{height} (min: 10x10)")
        
        if height > 10000 or width > 10000:
            raise ValidationError(f"Image too large: {width}x{height} (max: 10000x10000)")
        
        # Estimate size (rough calculation)
        channels = len(pil_image.getbands())
        size_bytes = width * height * channels
        
        return {
            'size_bytes': size_bytes,
            'dimensions': dimensions,
            'format': pil_image.format or 'PIL',
            'mode': pil_image.mode,
            'channels': channels
        }
    
    def validate_image_list(self, image_list: List[Union[str, bytes, np.ndarray, Image.Image]]) -> List[Dict]:
        """
        Validate a list of images.
        
        Args:
            image_list: List of images in various formats
            
        Returns:
            List of validation results
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(image_list, (list, tuple)):
            raise ValidationError("Image input must be a list or tuple")
        
        if len(image_list) == 0:
            raise ValidationError("Image list cannot be empty")
        
        if len(image_list) > self.max_images_per_request:
            raise ValidationError(
                f"Too many images: {len(image_list)} (max: {self.max_images_per_request})"
            )
        
        validation_results = []
        total_size = 0
        
        for i, image_input in enumerate(image_list):
            try:
                result = self.validate_image_input(image_input)
                result['index'] = i
                validation_results.append(result)
                total_size += result['size_bytes']
                
            except ValidationError as e:
                logger.error(f"Image {i+1} validation failed: {e}")
                raise ValidationError(f"Image {i+1} validation failed: {str(e)}")
        
        # Check total size
        max_total_size = self.MAX_IMAGE_SIZE * len(image_list)
        if total_size > max_total_size:
            raise ValidationError(
                f"Total image data too large: {total_size} bytes (max: {max_total_size})"
            )
        
        logger.info(f"Validated {len(image_list)} images, total size: {total_size} bytes")
        return validation_results
    
    def validate_config_parameter(self, param_name: str, value: Any, expected_type: type, 
                                 min_value: Optional[Union[int, float]] = None,
                                 max_value: Optional[Union[int, float]] = None,
                                 allowed_values: Optional[List[Any]] = None) -> Any:
        """
        Validate a configuration parameter.
        
        Args:
            param_name: Parameter name for error messages
            value: Value to validate
            expected_type: Expected type
            min_value: Minimum value (for numeric types)
            max_value: Maximum value (for numeric types)
            allowed_values: List of allowed values
            
        Returns:
            Validated value
            
        Raises:
            ValidationError: If validation fails
        """
        # Type check
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Parameter '{param_name}' must be {expected_type.__name__}, got {type(value).__name__}"
            )
        
        # Range check for numeric types
        if expected_type in [int, float] and (min_value is not None or max_value is not None):
            if min_value is not None and value < min_value:
                raise ValidationError(f"Parameter '{param_name}' must be >= {min_value}, got {value}")
            
            if max_value is not None and value > max_value:
                raise ValidationError(f"Parameter '{param_name}' must be <= {max_value}, got {value}")
        
        # Allowed values check
        if allowed_values is not None and value not in allowed_values:
            raise ValidationError(
                f"Parameter '{param_name}' must be one of {allowed_values}, got {value}"
            )
        
        return value
    
    def validate_output_format(self, format_name: str) -> str:
        """
        Validate output format.
        
        Args:
            format_name: Output format name
            
        Returns:
            Validated format name
            
        Raises:
            ValidationError: If format is invalid
        """
        allowed_formats = ['json', 'dict', 'text']
        
        if not isinstance(format_name, str):
            raise ValidationError("Output format must be a string")
        
        format_name = format_name.lower().strip()
        
        if format_name not in allowed_formats:
            raise ValidationError(
                f"Unsupported output format: {format_name}. "
                f"Supported formats: {', '.join(allowed_formats)}"
            )
        
        return format_name
    
    def get_validation_summary(self, validation_results: List[Dict]) -> Dict[str, Any]:
        """
        Generate summary from validation results.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Summary dictionary
        """
        total_images = len(validation_results)
        valid_images = len([r for r in validation_results if r.get('valid', False)])
        total_size = sum(r.get('size_bytes', 0) for r in validation_results)
        
        dimensions = [r.get('dimensions') for r in validation_results if r.get('dimensions')]
        formats = [r.get('format') for r in validation_results if r.get('format')]
        
        return {
            'total_images': total_images,
            'valid_images': valid_images,
            'invalid_images': total_images - valid_images,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'average_size_bytes': total_size // total_images if total_images > 0 else 0,
            'unique_formats': list(set(formats)),
            'dimension_range': {
                'min_width': min([d[0] for d in dimensions]) if dimensions else None,
                'max_width': max([d[0] for d in dimensions]) if dimensions else None,
                'min_height': min([d[1] for d in dimensions]) if dimensions else None,
                'max_height': max([d[1] for d in dimensions]) if dimensions else None,
            } if dimensions else None
        }