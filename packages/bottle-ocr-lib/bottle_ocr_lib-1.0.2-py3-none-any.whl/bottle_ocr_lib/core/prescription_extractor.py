"""
Prescription Extractor Module
============================

Extracts structured prescription information from OCR text using OpenAI GPT-4o.
This module is optional and requires an OpenAI API key.
"""

import json
import logging
from typing import Dict, List, Optional
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


logger = logging.getLogger(__name__)


class PrescriptionExtractor:
    """
    Extracts structured prescription information from OCR text using AI.
    
    This class uses OpenAI's GPT-4o model to parse OCR text and extract
    specific prescription fields like drug name, dosage, pharmacy info, etc.
    """
    
    # Standard prescription schema
    PRESCRIPTION_SCHEMA = {
        "pharmacy_name": "",
        "pharmacy_address": "",
        "pharmacy_phone": "",
        "patient_name": "",
        "prescription_number": "",
        "drug_name": "",
        "drug_strength": "",
        "dosage_form": "",
        "directions_for_use": "",
        "quantity_dispensed": "",
        "date_filled": "",
        "refills_remaining": "",
        "prescriber_name": "",
        "warning_labels": "",
        "storage_instructions": "",
        "expiration_date": "",
        "manufacturer": "",
        "description_of_pill": ""
    }
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 model: str = "gpt-4o",
                 temperature: float = 0.1,
                 max_tokens: int = 2000):
        """
        Initialize the prescription extractor.
        
        Args:
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: OpenAI model to use
            temperature: Generation temperature (lower = more consistent)
            max_tokens: Maximum tokens in response
            
        Raises:
            ImportError: If OpenAI package not installed
            ValueError: If no API key provided
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package required for prescription extraction. "
                "Install with: pip install openai"
            )
        
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Pass as parameter or set OPENAI_API_KEY environment variable"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Initialized PrescriptionExtractor with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"OpenAI initialization failed: {str(e)}")
    
    def extract_prescription_info(self, ocr_text_data: List[Dict]) -> Dict:
        """
        Extract prescription information from OCR text data.
        
        Args:
            ocr_text_data: List of OCR results with 'text' and 'confidence' fields
            
        Returns:
            Dictionary with extracted prescription fields
            
        Raises:
            RuntimeError: If extraction fails
        """
        try:
            # Combine OCR text
            combined_text = self._prepare_ocr_text(ocr_text_data)
            
            if not combined_text.strip():
                logger.warning("No OCR text provided for extraction")
                return self.PRESCRIPTION_SCHEMA.copy()
            
            # Build extraction prompt
            prompt = self._build_extraction_prompt(combined_text)
            
            # Call OpenAI API
            logger.debug("Sending request to OpenAI API")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            extracted_data = json.loads(result_text)
            
            # Validate and fill missing fields
            prescription_data = self._validate_and_fill_schema(extracted_data)
            
            logger.info("Successfully extracted prescription information")
            return prescription_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            raise RuntimeError(f"Invalid JSON response from AI model: {str(e)}")
        except Exception as e:
            logger.error(f"Prescription extraction failed: {e}")
            raise RuntimeError(f"Extraction failed: {str(e)}")
    
    def _prepare_ocr_text(self, ocr_text_data: List[Dict]) -> str:
        """
        Prepare OCR text for extraction prompt.
        
        Args:
            ocr_text_data: List of OCR results
            
        Returns:
            Formatted text string
        """
        text_lines = []
        
        for item in ocr_text_data:
            text = item.get('text', '').strip()
            confidence = item.get('confidence', 0.0)
            
            if text:
                # Include confidence score for context
                text_lines.append(f"{text} (confidence: {confidence:.2f})")
        
        return '\n'.join(text_lines)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI model."""
        return """You are an expert at extracting structured information from OCR text from prescription medication labels. 

Your task is to analyze OCR text from pill bottle images and extract specific prescription information into a structured JSON format.

Guidelines:
- Extract information accurately from the provided OCR text
- If a field cannot be determined from the text, leave it as an empty string ""
- Be conservative - only extract information you are confident about
- Pay attention to OCR confidence scores - lower confidence text may contain errors
- Common OCR errors: O/0 confusion, l/1 confusion, similar looking letters
- Return ONLY valid JSON in the exact schema format requested"""
    
    def _build_extraction_prompt(self, ocr_text: str) -> str:
        """
        Build the extraction prompt with OCR text and schema.
        
        Args:
            ocr_text: Combined OCR text
            
        Returns:
            Formatted prompt string
        """
        schema_json = json.dumps(self.PRESCRIPTION_SCHEMA, indent=2)
        
        return f"""Please extract prescription information from the following OCR text and return it as a JSON object matching this exact schema:

{schema_json}

Field descriptions:
- pharmacy_name: Name of the pharmacy (e.g., "CVS PHARMACY", "WALGREENS")
- pharmacy_address: Pharmacy address including city, state, zip
- pharmacy_phone: Pharmacy phone number
- patient_name: Patient's full name
- prescription_number: Prescription/RX number
- drug_name: Medication name (generic or brand)
- drug_strength: Dosage strength (e.g., "10mg", "250mg/5ml")
- dosage_form: Form of medication (tablet, capsule, liquid, etc.)
- directions_for_use: How to take the medication
- quantity_dispensed: Number of pills/amount dispensed
- date_filled: Date prescription was filled
- refills_remaining: Number of refills left
- prescriber_name: Doctor's name
- warning_labels: Any warning or cautionary text
- storage_instructions: Storage requirements
- expiration_date: Expiration date
- manufacturer: Drug manufacturer name
- description_of_pill: Physical description (color, shape, markings)

OCR Text from Prescription Label:
{ocr_text}

Extract the information and return ONLY the JSON object with the filled fields. If information cannot be determined, use empty string ""."""
    
    def _validate_and_fill_schema(self, extracted_data: Dict) -> Dict:
        """
        Validate extracted data and ensure all schema fields are present.
        
        Args:
            extracted_data: Raw extracted data from AI
            
        Returns:
            Validated prescription data with all schema fields
        """
        result = self.PRESCRIPTION_SCHEMA.copy()
        
        # Fill in extracted values
        for key, value in extracted_data.items():
            if key in result:
                # Clean and validate the value
                if isinstance(value, str):
                    result[key] = value.strip()
                else:
                    result[key] = str(value).strip() if value is not None else ""
        
        return result
    
    def extract_from_multiple_sources(self, 
                                    ocr_results_list: List[List[Dict]]) -> Dict:
        """
        Extract prescription info from multiple OCR sources (e.g., multiple images).
        
        Args:
            ocr_results_list: List of OCR results from different sources
            
        Returns:
            Combined prescription information
        """
        # Combine all OCR text
        all_text_data = []
        for ocr_results in ocr_results_list:
            all_text_data.extend(ocr_results)
        
        return self.extract_prescription_info(all_text_data)
    
    def get_extraction_confidence(self, prescription_data: Dict) -> Dict:
        """
        Analyze the confidence of extracted prescription data.
        
        Args:
            prescription_data: Extracted prescription information
            
        Returns:
            Dictionary with confidence metrics
        """
        filled_fields = sum(1 for value in prescription_data.values() if value.strip())
        total_fields = len(self.PRESCRIPTION_SCHEMA)
        completeness = filled_fields / total_fields
        
        # Key fields that are typically required
        key_fields = ['drug_name', 'pharmacy_name', 'patient_name', 'directions_for_use']
        key_fields_filled = sum(1 for field in key_fields if prescription_data.get(field, '').strip())
        key_completeness = key_fields_filled / len(key_fields)
        
        return {
            'total_fields_filled': filled_fields,
            'total_fields': total_fields,
            'completeness_percentage': round(completeness * 100, 1),
            'key_fields_filled': key_fields_filled,
            'key_fields_total': len(key_fields),
            'key_completeness_percentage': round(key_completeness * 100, 1),
            'missing_key_fields': [
                field for field in key_fields 
                if not prescription_data.get(field, '').strip()
            ]
        }


class MockPrescriptionExtractor(PrescriptionExtractor):
    """
    Mock extractor for testing without requiring OpenAI API.
    
    This class simulates prescription extraction for development and testing.
    Use only for development!
    """
    
    def __init__(self):
        """Initialize mock extractor."""
        # Don't call parent __init__ to avoid OpenAI client initialization
        self.model = "mock-model"
        self.temperature = 0.1
        self.max_tokens = 2000
        logger.warning("Using MockPrescriptionExtractor - FOR DEVELOPMENT ONLY!")
    
    def extract_prescription_info(self, ocr_text_data: List[Dict]) -> Dict:
        """Mock extraction that returns sample data."""
        # Simulate processing time
        import time
        time.sleep(0.5)
        
        # Return sample prescription data
        return {
            "pharmacy_name": "MOCK PHARMACY",
            "pharmacy_address": "123 MAIN ST, ANYTOWN, ST 12345",
            "pharmacy_phone": "(555) 123-4567",
            "patient_name": "JOHN DOE",
            "prescription_number": "1234567",
            "drug_name": "LISINOPRIL",
            "drug_strength": "10MG",
            "dosage_form": "tablet",
            "directions_for_use": "TAKE 1 TABLET BY MOUTH DAILY",
            "quantity_dispensed": "30",
            "date_filled": "10/19/2025",
            "refills_remaining": "2",
            "prescriber_name": "Dr. Jane Smith",
            "warning_labels": "MAY CAUSE DIZZINESS",
            "storage_instructions": "STORE AT ROOM TEMPERATURE",
            "expiration_date": "10/19/2026",
            "manufacturer": "TEVA PHARMACEUTICALS",
            "description_of_pill": "WHITE ROUND TABLET"
        }