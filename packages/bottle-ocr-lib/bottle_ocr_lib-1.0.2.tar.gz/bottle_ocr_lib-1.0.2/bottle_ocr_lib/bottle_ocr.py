"""
Main BottleOCR Library Interface
===============================

This is the primary interface that users will interact with.
It provides a simple, easy-to-use API for OCR and prescription extraction.
"""

import logging
import os
import time
from typing import Dict, List, Union, Optional, Any, TYPE_CHECKING
from pathlib import Path
import uuid

# Import for type hints only
if TYPE_CHECKING:
    import numpy as np
    from PIL import Image

from .auth.api_auth import APIKeyValidator, MockAPIKeyValidator, AuthenticationError
from .core.ocr_processor import OCRProcessor
from .core.prescription_extractor import PrescriptionExtractor, MockPrescriptionExtractor
from .utils.config import ConfigManager
from .utils.validation import InputValidator, ValidationError
from .utils.exceptions import (
    BottleOCRError, 
    OCRProcessingError, 
    ExtractionError,
    ConfigurationError,
    RateLimitError,
    QuotaExceededError
)


logger = logging.getLogger(__name__)


class BottleOCR:
    """
    Main interface for the BottleOCR library.
    
    This class provides a simple, unified interface for:
    - API key authentication
    - Image preprocessing and OCR
    - Prescription information extraction
    - Result formatting and validation
    
    Example Usage:
        >>> from bottle_ocr_lib import BottleOCR
        >>> 
        >>> # Initialize with API key
        >>> ocr = BottleOCR(api_key="your-api-key-here")
        >>> 
        >>> # Process images
        >>> result = ocr.process_images(['image1.jpg', 'image2.jpg'])
        >>> 
        >>> # Access prescription data
        >>> prescription = result['prescription']
        >>> print(f"Drug: {prescription['drug_name']}")
    """
    
    def __init__(self, 
                 api_key: str,
                 config: Optional[Union[Dict, str, Path]] = None,
                 mock_mode: bool = False,
                 enable_extraction: bool = True,
                 openai_api_key: Optional[str] = None):
        """
        Initialize BottleOCR instance.
        
        Args:
            api_key: Your BottleOCR API key
            config: Configuration dict, file path, or ConfigManager instance
            mock_mode: Use mock services for development (default: False)
            enable_extraction: Enable AI prescription extraction (default: True)
            openai_api_key: OpenAI API key for prescription extraction
            
        Raises:
            ConfigurationError: If configuration is invalid
            AuthenticationError: If API key validation fails
        """
        self.session_id = str(uuid.uuid4())
        self.mock_mode = mock_mode
        self.enable_extraction = enable_extraction
        self.api_key = api_key  # Store the API key
        
        logger.info(f"Initializing BottleOCR (session: {self.session_id[:8]}...)")
        
        try:
            # Load configuration
            if isinstance(config, ConfigManager):
                self.config = config
            else:
                self.config = ConfigManager(config)
            
            # Override mock mode from config if specified
            if self.config.get('auth.mock_mode', False) or self.config.get('extraction.mock_mode', False):
                self.mock_mode = True
                logger.warning("Mock mode enabled via configuration")
            
            # Validate configuration
            config_issues = self.config.validate()
            if config_issues:
                raise ConfigurationError(f"Configuration validation failed: {'; '.join(config_issues)}")
            
            # Initialize components
            self._initialize_authentication(api_key)
            self._initialize_ocr_processor()
            # Pass the OpenAI key from license validation to extractor
            license_openai_key = self.validation_result.get('openai_api_key')
            self._initialize_extraction(openai_api_key or license_openai_key)
            self._initialize_validator()
            
            logger.info("BottleOCR initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize BottleOCR: {e}")
            raise
    
    def _initialize_authentication(self, api_key: str):
        """Initialize API key authentication."""
        try:
            if self.mock_mode:
                self.auth_validator = MockAPIKeyValidator()
                logger.warning("Using mock authentication - FOR DEVELOPMENT ONLY")
            else:
                auth_config = self.config.get_section('auth')
                
                # Get auth server URL from config, environment, or use default
                auth_server_url = (
                    auth_config.get('server_url') or 
                    os.getenv('BOTTLEOCR_AUTH_SERVER') or
                    'http://54.226.83.55'  # Our deployed EC2 license server
                )
                
                self.auth_validator = APIKeyValidator(
                    auth_server_url=auth_server_url,
                    timeout=auth_config['timeout_seconds']
                )
                logger.info(f"Using authentication server: {auth_server_url}")
            
            # Validate API key immediately
            self.validation_result = self.auth_validator.validate_api_key(api_key, service="ocr")
            
            # Check usage limits
            allowed, message = self.auth_validator.check_usage_limits(self.validation_result)
            if not allowed:
                if "rate limit" in message.lower():
                    raise RateLimitError(message)
                else:
                    raise QuotaExceededError(message)
            
            self.user_info = self.auth_validator.get_user_info(self.validation_result)
            
            logger.info(f"Authentication successful for user: {self.user_info['user_id']}")
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Authentication initialization failed: {e}")
            raise AuthenticationError(f"Authentication setup failed: {str(e)}")
    
    def _initialize_ocr_processor(self):
        """Initialize OCR processor."""
        try:
            ocr_config = self.config.get_section('ocr')
            
            self.ocr_processor = OCRProcessor(
                language=ocr_config['language'],
                use_angle_classification=ocr_config['use_angle_classification'],
                max_dimension=ocr_config['max_dimension'],
                apply_clahe=ocr_config['apply_clahe'],
                clahe_clip_limit=ocr_config['clahe_clip_limit'],
                clahe_tile_grid_size=ocr_config['clahe_tile_grid_size'],
                reinit_per_request=True  # Always reinitialize to prevent state corruption
            )
            
            logger.info("OCR processor initialized with per-request reinitialization")
            
        except Exception as e:
            logger.error(f"OCR processor initialization failed: {e}")
            raise OCRProcessingError(f"Failed to initialize OCR: {str(e)}")
    
    def _initialize_extraction(self, openai_api_key: Optional[str]):
        """Initialize prescription extraction."""
        if not self.enable_extraction:
            self.prescription_extractor = None
            logger.info("Prescription extraction disabled")
            return
        
        try:
            extraction_config = self.config.get_section('extraction')
            
            if self.mock_mode or extraction_config.get('mock_mode', False):
                self.prescription_extractor = MockPrescriptionExtractor()
                logger.warning("Using mock prescription extraction - FOR DEVELOPMENT ONLY")
            else:
                self.prescription_extractor = PrescriptionExtractor(
                    openai_api_key=openai_api_key,
                    model=extraction_config['model'],
                    temperature=extraction_config['temperature'],
                    max_tokens=extraction_config['max_tokens']
                )
            
            logger.info("Prescription extractor initialized")
            
        except Exception as e:
            logger.error(f"Prescription extractor initialization failed: {e}")
            if self.enable_extraction:
                raise ExtractionError(f"Failed to initialize extraction: {str(e)}")
    
    def _initialize_validator(self):
        """Initialize input validator."""
        processing_config = self.config.get_section('processing')
        self.validator = InputValidator(
            max_images_per_request=processing_config['max_images_per_request']
        )
        logger.debug("Input validator initialized")
    
    def process_images(self, 
                      images: List[Union[str, bytes, 'np.ndarray', 'Image.Image']],
                      include_bbox: Optional[bool] = None,
                      extract_prescription: Optional[bool] = None,
                      output_format: str = 'json') -> Dict[str, Any]:
        """
        Process images and extract prescription information.
        
        Args:
            images: List of images (file paths, bytes, numpy arrays, or PIL Images)
            include_bbox: Include bounding box coordinates (default: from config)
            extract_prescription: Enable prescription extraction (default: from config)
            output_format: Output format ('json', 'dict', or 'text')
            
        Returns:
            Dictionary with OCR results and prescription information
            
        Raises:
            ValidationError: If input validation fails
            OCRProcessingError: If OCR processing fails
            ExtractionError: If prescription extraction fails
        """
        start_time = time.time()
        
        logger.info(f"Processing {len(images)} images (session: {self.session_id[:8]}...)")
        
        try:
            # Validate inputs
            self.validator.validate_output_format(output_format)
            validation_results = self.validator.validate_image_list(images)
            
            # Use config defaults if not specified
            if include_bbox is None:
                include_bbox = self.config.get('processing.include_bbox', True)
            
            if extract_prescription is None:
                extract_prescription = self.enable_extraction
            
            # Process images with OCR
            logger.debug("Starting OCR processing")
            ocr_results = self.ocr_processor.process_multiple_images(
                images, 
                include_bbox=include_bbox
            )
            
            # Extract prescription information if enabled
            prescription_data = None
            extraction_confidence = None
            
            if extract_prescription and self.prescription_extractor:
                logger.debug("Starting prescription extraction")
                
                # Combine all text data
                all_text_data = []
                for result in ocr_results:
                    if 'error' not in result:
                        all_text_data.extend(result['detected_text'])
                
                if all_text_data:
                    prescription_data = self.prescription_extractor.extract_prescription_info(all_text_data)
                    extraction_confidence = self.prescription_extractor.get_extraction_confidence(prescription_data)
                else:
                    logger.warning("No text data available for prescription extraction")
            
            # Calculate processing statistics
            processing_time = time.time() - start_time
            successful_images = len([r for r in ocr_results if 'error' not in r])
            total_text_regions = sum(r.get('text_regions', 0) for r in ocr_results if 'error' not in r)
            
            # Build response
            response = {
                'session_id': self.session_id,
                'status': 'success',
                'processing_info': {
                    'total_images': len(images),
                    'successful_images': successful_images,
                    'failed_images': len(images) - successful_images,
                    'total_text_regions': total_text_regions,
                    'processing_time_seconds': round(processing_time, 2),
                    'extraction_enabled': extract_prescription,
                    'include_bbox': include_bbox
                },
                'images': ocr_results,
                'prescription': prescription_data,
                'extraction_confidence': extraction_confidence,
                'user_info': {
                    'user_id': self.user_info['user_id'],
                    'plan': self.user_info['plan'],
                    'usage': self.user_info['usage']
                }
            }
            
            # Format output
            if output_format == 'json':
                import json
                return json.dumps(response, indent=2) if self.config.get('output.pretty_print', True) else json.dumps(response)
            elif output_format == 'dict':
                return response
            elif output_format == 'text':
                return self._format_text_output(response)
            
            logger.info(f"Processing completed in {processing_time:.2f}s: {successful_images}/{len(images)} successful")
            return response
            
        except (ValidationError, OCRProcessingError, ExtractionError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            raise BottleOCRError(f"Processing failed: {str(e)}")
    
    def process_single_image(self, 
                           image: Union[str, bytes, 'np.ndarray', 'Image.Image'],
                           **kwargs) -> Dict[str, Any]:
        """
        Convenience method to process a single image.
        
        Args:
            image: Single image input
            **kwargs: Additional arguments passed to process_images()
            
        Returns:
            Processing result for the single image
        """
        result = self.process_images([image], **kwargs)
        
        if isinstance(result, str):  # JSON format
            import json
            result = json.loads(result)
        
        # Return simplified result for single image
        if result['processing_info']['successful_images'] > 0:
            image_result = result['images'][0]
            return {
                'session_id': result['session_id'],
                'status': 'success',
                'image_result': image_result,
                'prescription': result.get('prescription'),
                'extraction_confidence': result.get('extraction_confidence'),
                'processing_time_seconds': result['processing_info']['processing_time_seconds']
            }
        else:
            error_info = result['images'][0] if result['images'] else {'error': 'Unknown error'}
            raise OCRProcessingError(f"Image processing failed: {error_info.get('error', 'Unknown error')}")
    
    def _format_text_output(self, response: Dict) -> str:
        """Format response as human-readable text."""
        lines = [
            f"BottleOCR Processing Results",
            f"Session: {response['session_id']}",
            f"Status: {response['status']}",
            f"",
            f"Processing Summary:",
            f"  Total Images: {response['processing_info']['total_images']}",
            f"  Successful: {response['processing_info']['successful_images']}",
            f"  Failed: {response['processing_info']['failed_images']}",
            f"  Total Text Regions: {response['processing_info']['total_text_regions']}",
            f"  Processing Time: {response['processing_info']['processing_time_seconds']}s",
            f""
        ]
        
        # Add prescription information if available
        if response.get('prescription'):
            lines.extend([
                f"Prescription Information:",
                f"  Drug Name: {response['prescription']['drug_name']}",
                f"  Drug Strength: {response['prescription']['drug_strength']}",
                f"  Pharmacy: {response['prescription']['pharmacy_name']}",
                f"  Patient: {response['prescription']['patient_name']}",
                f"  Directions: {response['prescription']['directions_for_use']}",
                f""
            ])
        
        # Add OCR results summary
        lines.append("OCR Results:")
        for i, img_result in enumerate(response['images']):
            if 'error' in img_result:
                lines.append(f"  Image {i+1}: ERROR - {img_result['error']}")
            else:
                lines.append(f"  Image {i+1}: {img_result['text_regions']} text regions, "
                           f"avg confidence: {img_result['average_confidence']:.2f}")
        
        return '\n'.join(lines)
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            Dictionary with user information and usage statistics
        """
        return self.user_info.copy()
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported OCR languages.
        
        Returns:
            List of language codes
        """
        # This would typically come from PaddleOCR or your API
        return ['en', 'ch_sim', 'ch_tra', 'fr', 'german', 'korean', 'japan']
    
    def get_prescription_schema(self) -> Dict[str, str]:
        """
        Get the prescription data schema.
        
        Returns:
            Dictionary with field names and descriptions
        """
        if self.prescription_extractor:
            schema = self.prescription_extractor.PRESCRIPTION_SCHEMA.copy()
            
            # Add field descriptions
            descriptions = {
                "pharmacy_name": "Name of the pharmacy",
                "pharmacy_address": "Pharmacy address including city, state, zip",
                "pharmacy_phone": "Pharmacy phone number",
                "patient_name": "Patient's full name",
                "prescription_number": "Prescription/RX number",
                "drug_name": "Medication name (generic or brand)",
                "drug_strength": "Dosage strength (e.g., '10mg', '250mg/5ml')",
                "dosage_form": "Form of medication (tablet, capsule, liquid, etc.)",
                "directions_for_use": "How to take the medication",
                "quantity_dispensed": "Number of pills/amount dispensed",
                "date_filled": "Date prescription was filled",
                "refills_remaining": "Number of refills left",
                "prescriber_name": "Doctor's name",
                "warning_labels": "Any warning or cautionary text",
                "storage_instructions": "Storage requirements",
                "expiration_date": "Expiration date",
                "manufacturer": "Drug manufacturer name",
                "description_of_pill": "Physical description (color, shape, markings)"
            }
            
            return {field: descriptions.get(field, "") for field in schema.keys()}
        
        return {}
    
    def validate_images(self, images: List[Union[str, bytes, 'np.ndarray', 'Image.Image']]) -> Dict[str, Any]:
        """
        Validate images without processing them.
        
        Args:
            images: List of images to validate
            
        Returns:
            Validation results and summary
        """
        try:
            validation_results = self.validator.validate_image_list(images)
            summary = self.validator.get_validation_summary(validation_results)
            
            return {
                'status': 'valid',
                'summary': summary,
                'details': validation_results
            }
            
        except ValidationError as e:
            return {
                'status': 'invalid',
                'error': str(e),
                'summary': None,
                'details': []
            }
    
    def get_authentication_info(self) -> Dict[str, Any]:
        """
        Get authentication and license information.
        
        Returns:
            Dictionary with authentication details
        """
        return {
            'user_id': self.user_info.get('user_id'),
            'plan': self.user_info.get('plan'),
            'permissions': self.user_info.get('permissions', []),
            'openai_key': bool(self.validation_result.get('openai_api_key')),
            'cached': self.user_info.get('cached', False),
            'expires_at': self.user_info.get('expires_at', 0),
            'mock_mode': self.mock_mode
        }
    
    def invalidate_license_cache(self) -> bool:
        """
        Invalidate the cached license for this API key.
        
        Returns:
            True if cache was invalidated, False if not found
        """
        if hasattr(self.auth_validator, 'invalidate_license_cache'):
            return self.auth_validator.invalidate_license_cache(self.api_key)
        return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the license cache.
        
        Returns:
            Dictionary with cache statistics
        """
        if hasattr(self.auth_validator, 'get_cache_info'):
            return self.auth_validator.get_cache_info()
        return {'cache_enabled': False}
    
    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        if hasattr(self.auth_validator, 'cleanup_expired_cache'):
            return self.auth_validator.cleanup_expired_cache()
        return 0
    
    def __repr__(self) -> str:
        """String representation of BottleOCR instance."""
        return (f"BottleOCR(user={self.user_info['user_id']}, "
                f"plan={self.user_info['plan']}, "
                f"mock_mode={self.mock_mode})")


# Convenience functions for quick usage
def process_images(api_key: str, 
                  images: List[Union[str, bytes, 'np.ndarray', 'Image.Image']],
                  **kwargs) -> Dict[str, Any]:
    """
    Convenience function to process images with minimal setup.
    
    Args:
        api_key: BottleOCR API key
        images: List of images to process
        **kwargs: Additional arguments
        
    Returns:
        Processing results
    """
    ocr = BottleOCR(api_key=api_key)
    return ocr.process_images(images, **kwargs)


def process_single_image(api_key: str, 
                        image: Union[str, bytes, 'np.ndarray', 'Image.Image'],
                        **kwargs) -> Dict[str, Any]:
    """
    Convenience function to process a single image with minimal setup.
    
    Args:
        api_key: BottleOCR API key
        image: Single image to process
        **kwargs: Additional arguments
        
    Returns:
        Processing results
    """
    ocr = BottleOCR(api_key=api_key)
    return ocr.process_single_image(image, **kwargs)