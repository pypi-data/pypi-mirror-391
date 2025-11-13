"""
OCR Processor Module
===================

Core OCR processing functionality extracted from the original scripts
and refactored for library use.
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional
from PIL import Image
import io
import threading
import gc

try:
    from paddleocr import PaddleOCR
except ImportError:
    raise ImportError(
        "PaddleOCR is required but not installed. "
        "Install with: pip install paddleocr"
    )


logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Core OCR processor for extracting text from pill bottle images.
    
    This class handles:
    - Image preprocessing
    - OCR text extraction using PaddleOCR
    - Result formatting and confidence scoring
    """
    
    def __init__(self, 
                 language: str = 'en',
                 use_angle_classification: bool = True,
                 max_dimension: int = 2048,
                 apply_clahe: bool = False,
                 clahe_clip_limit: float = 2.0,
                 clahe_tile_grid_size: int = 8,
                 reinit_per_request: bool = True):
        """
        Initialize the OCR processor.
        
        Args:
            language: OCR language code (e.g., 'en', 'ch', 'fr')
            use_angle_classification: Enable text angle detection
            max_dimension: Maximum dimension for image resizing  
            apply_clahe: Apply CLAHE enhancement for low quality images
            clahe_clip_limit: CLAHE clip limit
            clahe_tile_grid_size: CLAHE tile grid size
            reinit_per_request: Reinitialize PaddleOCR for each request to prevent state corruption
        """
        self.language = language
        self.use_angle_classification = use_angle_classification
        self.max_dimension = max_dimension
        self.apply_clahe = apply_clahe
        self.clahe_clip_limit = clahe_clip_limit
        self.clahe_tile_grid_size = clahe_tile_grid_size
        self.reinit_per_request = reinit_per_request
        
        # Thread lock for OCR operations
        self._ocr_lock = threading.Lock()
        
        # OCR instance - may be None if reinit_per_request is True
        self.ocr = None
        
        # Configuration for OCR initialization
        self._ocr_config = {
            'lang': language,
            'use_textline_orientation': use_angle_classification
        }
        
        logger.info(f"Initializing OCR Processor (reinit_per_request={reinit_per_request})...")
        
        # Initialize OCR instance if not using per-request reinitialization
        if not self.reinit_per_request:
            self._initialize_ocr()
        else:
            logger.info("PaddleOCR will be initialized per request to prevent state corruption")
    
    def _initialize_ocr(self):
        """Initialize or reinitialize the PaddleOCR instance."""
        try:
            # Try with show_log parameter first (older versions)
            try:
                self.ocr = PaddleOCR(
                    show_log=False,  # Suppress PaddleOCR logs
                    **self._ocr_config
                )
                logger.debug("PaddleOCR initialized successfully (with show_log parameter)")
            except (TypeError, ValueError) as e:
                if "show_log" in str(e):
                    # Fallback for newer versions that don't support show_log
                    logger.debug("show_log parameter not supported, trying without it...")
                    self.ocr = PaddleOCR(**self._ocr_config)
                    logger.debug("PaddleOCR initialized successfully (without show_log parameter)")
                else:
                    raise e
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise RuntimeError(f"OCR initialization failed: {str(e)}")
    
    def _cleanup_ocr(self):
        """Clean up OCR instance to free resources."""
        if self.ocr is not None:
            try:
                # Delete the OCR instance
                del self.ocr
                self.ocr = None
                
                # Force garbage collection to free C++ resources
                gc.collect()
                
                logger.debug("PaddleOCR instance cleaned up")
            except Exception as e:
                logger.warning(f"Error during OCR cleanup: {e}")
    
    def _get_ocr_instance(self):
        """
        Get an OCR instance, initializing fresh if reinit_per_request is enabled.
        
        Returns:
            PaddleOCR instance ready for use
        """
        with self._ocr_lock:
            if self.reinit_per_request:
                # Clean up existing instance if any
                self._cleanup_ocr()
                
                # Create fresh instance
                logger.debug("Creating fresh PaddleOCR instance for request")
                self._initialize_ocr()
            elif self.ocr is None:
                # Initialize if not yet created
                logger.debug("Initializing PaddleOCR instance")
                self._initialize_ocr()
            
            return self.ocr
    
    def preprocess_image(self, image_input: Union[str, bytes, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Preprocess image for optimal OCR results.
        
        Args:
            image_input: Image as file path, bytes, numpy array, or PIL Image
            
        Returns:
            Preprocessed RGB image as numpy array
            
        Raises:
            ValueError: If image cannot be loaded or processed
        """
        try:
            # Load image from different input types
            if isinstance(image_input, str):
                # File path
                img = cv2.imread(image_input)
                if img is None:
                    raise ValueError(f"Could not load image from path: {image_input}")
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
            elif isinstance(image_input, bytes):
                # Bytes data
                nparr = np.frombuffer(image_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    raise ValueError("Could not decode image from bytes")
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
            elif isinstance(image_input, np.ndarray):
                # Numpy array
                img_rgb = image_input.copy()
                if len(img_rgb.shape) == 3 and img_rgb.shape[2] == 3:
                    # Assume it's already RGB
                    pass
                else:
                    raise ValueError("Numpy array must be 3-channel RGB image")
                    
            elif isinstance(image_input, Image.Image):
                # PIL Image
                img_rgb = np.array(image_input.convert('RGB'))
                
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
            # Resize if image is too large
            original_shape = img_rgb.shape[:2]
            img_rgb = self._resize_image(img_rgb)
            
            # Apply CLAHE if enabled
            if self.apply_clahe:
                img_rgb = self._apply_clahe_enhancement(img_rgb)
            
            logger.debug(f"Preprocessed image: {original_shape} -> {img_rgb.shape[:2]}")
            return img_rgb
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            image: Input RGB image
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if max(height, width) > self.max_dimension:
            scale = self.max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            image = cv2.resize(
                image, 
                (new_width, new_height), 
                interpolation=cv2.INTER_AREA
            )
            
            logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        return image
    
    def _apply_clahe_enhancement(self, image: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
        
        Args:
            image: Input RGB image
            
        Returns:
            Enhanced image
        """
        # Convert RGB to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(
            clipLimit=self.clahe_clip_limit,
            tileGridSize=(self.clahe_tile_grid_size, self.clahe_tile_grid_size)
        )
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        logger.debug("Applied CLAHE enhancement")
        return enhanced
    
    def extract_text(self, image: np.ndarray) -> List[Dict]:
        """
        Extract text from preprocessed image using OCR.
        
        Args:
            image: Preprocessed RGB image array
            
        Returns:
            List of dictionaries containing detected text, confidence, and bounding boxes
        """
        ocr_instance = None
        try:
            # Get OCR instance (fresh if reinit_per_request is enabled)
            ocr_instance = self._get_ocr_instance()
            
            # Run PaddleOCR with a copy of the image to prevent memory issues
            image_copy = image.copy() if not self.reinit_per_request else image
            ocr_result = ocr_instance.predict(image_copy)
            
            # Process OCR results
            text_results = []
            
            if isinstance(ocr_result, list) and len(ocr_result) > 0:
                result_dict = ocr_result[0] if isinstance(ocr_result[0], dict) else {}
                
                # Extract components
                det_polys = result_dict.get('dt_polys', result_dict.get('det_polys', []))
                rec_texts = result_dict.get('rec_text', result_dict.get('rec_texts', []))
                rec_scores = result_dict.get('rec_score', result_dict.get('rec_scores', []))
                
                # Combine results
                for i, poly in enumerate(det_polys):
                    if i < len(rec_texts):
                        text = rec_texts[i] if rec_texts[i] else ""
                        confidence = float(rec_scores[i]) if i < len(rec_scores) else 0.0
                        
                        # Convert polygon to list of [x, y] coordinates
                        bbox = [[float(x), float(y)] for x, y in poly]
                        
                        text_results.append({
                            'text': text.strip(),
                            'confidence': round(confidence, 4),
                            'bbox': bbox
                        })
            
            # Filter out empty text
            text_results = [r for r in text_results if r['text']]
            
            logger.debug(f"Extracted {len(text_results)} text regions")
            return text_results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise RuntimeError(f"Text extraction failed: {str(e)}")
        finally:
            # Always clean up if using per-request reinitialization
            if self.reinit_per_request and ocr_instance is not None:
                self._cleanup_ocr()
    
    def process_single_image(self, 
                           image_input: Union[str, bytes, np.ndarray, Image.Image],
                           include_bbox: bool = True) -> Dict:
        """
        Process a single image end-to-end.
        
        Args:
            image_input: Image input in various formats
            include_bbox: Whether to include bounding box coordinates
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Preprocess
            processed_image = self.preprocess_image(image_input)
            
            # Extract text
            text_results = self.extract_text(processed_image)
            
            # Calculate statistics
            total_text_regions = len(text_results)
            avg_confidence = 0.0
            
            if text_results:
                avg_confidence = sum(r['confidence'] for r in text_results) / total_text_regions
            
            # Prepare output
            result = {
                'text_regions': total_text_regions,
                'average_confidence': round(avg_confidence, 4),
                'detected_text': text_results if include_bbox else [
                    {'text': r['text'], 'confidence': r['confidence']} 
                    for r in text_results
                ],
                'processing_info': {
                    'language': self.language,
                    'max_dimension': self.max_dimension,
                    'clahe_applied': self.apply_clahe
                }
            }
            
            logger.info(f"Processed image: {total_text_regions} text regions, "
                       f"avg confidence: {avg_confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Single image processing failed: {e}")
            raise
    
    def process_multiple_images(self, 
                              image_inputs: List[Union[str, bytes, np.ndarray, Image.Image]],
                              include_bbox: bool = True) -> List[Dict]:
        """
        Process multiple images in batch.
        
        Args:
            image_inputs: List of image inputs in various formats
            include_bbox: Whether to include bounding box coordinates
            
        Returns:
            List of processing results for each image
        """
        results = []
        
        for i, image_input in enumerate(image_inputs):
            try:
                logger.debug(f"Processing image {i+1}/{len(image_inputs)}")
                result = self.process_single_image(image_input, include_bbox)
                result['image_index'] = i
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process image {i+1}: {e}")
                # Add error result
                results.append({
                    'image_index': i,
                    'error': str(e),
                    'text_regions': 0,
                    'average_confidence': 0.0,
                    'detected_text': []
                })
        
        logger.info(f"Batch processed {len(image_inputs)} images, "
                   f"{len([r for r in results if 'error' not in r])} successful")
        
        return results
    
    def get_combined_text(self, text_results: List[Dict], 
                         min_confidence: float = 0.0) -> str:
        """
        Combine all detected text into a single string.
        
        Args:
            text_results: Results from extract_text()
            min_confidence: Minimum confidence threshold
            
        Returns:
            Combined text string
        """
        filtered_text = [
            r['text'] for r in text_results 
            if r['confidence'] >= min_confidence and r['text'].strip()
        ]
        
        return '\n'.join(filtered_text)
    
    def get_high_confidence_text(self, text_results: List[Dict], 
                               confidence_threshold: float = 0.8) -> List[Dict]:
        """
        Filter text results by confidence threshold.
        
        Args:
            text_results: Results from extract_text()
            confidence_threshold: Minimum confidence (0.0-1.0)
            
        Returns:
            Filtered text results
        """
        return [
            r for r in text_results 
            if r['confidence'] >= confidence_threshold
        ]
    
    def cleanup(self):
        """
        Public cleanup method to release OCR resources.
        
        Call this when you're done using the OCR processor to free up memory.
        This is automatically called if reinit_per_request=True.
        """
        logger.info("Cleaning up OCR processor resources")
        with self._ocr_lock:
            self._cleanup_ocr()
    
    def __del__(self):
        """Destructor to ensure cleanup on object deletion."""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during cleanup