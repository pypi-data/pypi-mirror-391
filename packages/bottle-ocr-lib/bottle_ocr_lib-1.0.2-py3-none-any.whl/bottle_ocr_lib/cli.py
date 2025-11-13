#!/usr/bin/env python3
"""
Command Line Interface for BottleOCR Library
============================================

Provides command-line access to BottleOCR functionality.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
import logging

from .bottle_ocr import BottleOCR
from .utils.exceptions import BottleOCRError


def setup_logging(level: str = 'INFO'):
    """Setup logging for CLI."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def process_command(args) -> int:
    """
    Process images using the OCR library.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        # Initialize BottleOCR
        ocr = BottleOCR(
            api_key=args.api_key,
            mock_mode=args.mock,
            enable_extraction=args.extract,
            openai_api_key=args.openai_key
        )
        
        # Collect image files
        image_files = []
        for path_str in args.images:
            path = Path(path_str)
            
            if path.is_file():
                image_files.append(str(path))
            elif path.is_dir():
                # Add all image files in directory
                for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    image_files.extend([str(f) for f in path.glob(f'*{ext}')])
                    image_files.extend([str(f) for f in path.glob(f'*{ext.upper()}')])
            else:
                print(f"Warning: Path not found: {path}", file=sys.stderr)
        
        if not image_files:
            print("Error: No image files found", file=sys.stderr)
            return 1
        
        print(f"Processing {len(image_files)} image(s)...")
        
        # Process images
        result = ocr.process_images(
            images=image_files,
            include_bbox=args.include_bbox,
            extract_prescription=args.extract,
            output_format='dict'
        )
        
        # Save or print results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to: {output_path}")
        else:
            # Print to stdout
            if args.format == 'json':
                print(json.dumps(result, indent=2))
            elif args.format == 'text':
                text_output = ocr._format_text_output(result)
                print(text_output)
            else:
                # Summary format
                print(f"Processing completed successfully!")
                print(f"  Images processed: {result['processing_info']['successful_images']}/{result['processing_info']['total_images']}")
                print(f"  Processing time: {result['processing_info']['processing_time_seconds']}s")
                print(f"  Total text regions: {result['processing_info']['total_text_regions']}")
                
                if result.get('prescription') and result['prescription']['drug_name']:
                    print(f"\\nPrescription extracted:")
                    print(f"  Drug: {result['prescription']['drug_name']} {result['prescription']['drug_strength']}")
                    print(f"  Pharmacy: {result['prescription']['pharmacy_name']}")
                    print(f"  Patient: {result['prescription']['patient_name']}")
        
        return 0
        
    except BottleOCRError as e:
        print(f"BottleOCR Error: {e.message}", file=sys.stderr)
        if args.debug:
            print(f"Error code: {e.error_code}", file=sys.stderr)
            if e.details:
                print(f"Details: {e.details}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def validate_command(args) -> int:
    """
    Validate images without processing them.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        ocr = BottleOCR(
            api_key=args.api_key,
            mock_mode=args.mock
        )
        
        # Collect image files
        image_files = []
        for path_str in args.images:
            path = Path(path_str)
            if path.is_file():
                image_files.append(str(path))
            else:
                print(f"Warning: File not found: {path}", file=sys.stderr)
        
        if not image_files:
            print("Error: No image files found", file=sys.stderr)
            return 1
        
        # Validate images
        result = ocr.validate_images(image_files)
        
        if result['status'] == 'valid':
            print("✅ All images are valid!")
            summary = result['summary']
            print(f"  Total images: {summary['total_images']}")
            print(f"  Total size: {summary['total_size_mb']} MB")
            print(f"  Formats: {', '.join(summary['unique_formats'])}")
            return 0
        else:
            print(f"❌ Validation failed: {result['error']}", file=sys.stderr)
            return 1
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def info_command(args) -> int:
    """
    Display information about the BottleOCR library.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 = success)
    """
    try:
        from . import __version__
        
        print(f"BottleOCR Library v{__version__}")
        print("=====================================")
        
        if args.api_key:
            # Show user info if API key provided
            try:
                ocr = BottleOCR(api_key=args.api_key, mock_mode=args.mock)
                user_info = ocr.get_user_info()
                
                print(f"\\nUser Information:")
                print(f"  User ID: {user_info['user_id']}")
                print(f"  Plan: {user_info['plan']}")
                
                usage = user_info.get('usage', {})
                limits = user_info.get('limits', {})
                
                if usage:
                    print(f"\\nUsage:")
                    print(f"  Daily requests: {usage.get('daily_requests', 0)}/{limits.get('daily_requests', '∞')}")
                    print(f"  Monthly requests: {usage.get('monthly_requests', 0)}/{limits.get('monthly_requests', '∞')}")
                
            except Exception as e:
                print(f"\\nCould not retrieve user info: {e}")
        
        # Show supported languages
        print(f"\\nSupported OCR Languages:")
        languages = ['en (English)', 'ch_sim (Chinese Simplified)', 'ch_tra (Chinese Traditional)', 
                    'fr (French)', 'german (German)', 'korean (Korean)', 'japan (Japanese)']
        for lang in languages:
            print(f"  - {lang}")
        
        # Show prescription schema
        print(f"\\nPrescription Fields Extracted:")
        schema_descriptions = {
            "pharmacy_name": "Pharmacy name",
            "pharmacy_address": "Pharmacy address",
            "pharmacy_phone": "Pharmacy phone number", 
            "patient_name": "Patient's full name",
            "prescription_number": "Prescription/RX number",
            "drug_name": "Medication name",
            "drug_strength": "Dosage strength",
            "directions_for_use": "Usage instructions",
            "quantity_dispensed": "Amount dispensed",
            "date_filled": "Date filled",
            "prescriber_name": "Doctor's name",
            "expiration_date": "Expiration date"
        }
        
        for field, desc in schema_descriptions.items():
            print(f"  - {field}: {desc}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='bottle-ocr',
        description='BottleOCR Library - Extract prescription information from pill bottle images'
    )
    
    # Global arguments
    parser.add_argument('--api-key', 
                       help='BottleOCR API key (or set BOTTLE_OCR_API_KEY env var)')
    parser.add_argument('--openai-key',
                       help='OpenAI API key for prescription extraction (or set OPENAI_API_KEY env var)')
    parser.add_argument('--mock', action='store_true',
                       help='Use mock services for development/testing')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', 
                                          help='Process images and extract prescription information')
    process_parser.add_argument('images', nargs='+',
                               help='Image files or directories to process')
    process_parser.add_argument('--output', '-o',
                               help='Output file path (default: print to stdout)')
    process_parser.add_argument('--format', choices=['json', 'text', 'summary'], default='summary',
                               help='Output format')
    process_parser.add_argument('--extract', action='store_true', default=True,
                               help='Enable prescription extraction (default: True)')
    process_parser.add_argument('--no-extract', dest='extract', action='store_false',
                               help='Disable prescription extraction')
    process_parser.add_argument('--include-bbox', action='store_true', default=True,
                               help='Include bounding box coordinates (default: True)')
    process_parser.add_argument('--no-bbox', dest='include_bbox', action='store_false',
                               help='Exclude bounding box coordinates')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate',
                                           help='Validate images without processing')
    validate_parser.add_argument('images', nargs='+',
                                help='Image files to validate')
    
    # Info command
    info_parser = subparsers.add_parser('info',
                                       help='Display library and user information')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level if not args.debug else 'DEBUG')
    
    # Get API key from environment if not provided
    if not args.api_key:
        import os
        args.api_key = os.getenv('BOTTLE_OCR_API_KEY')
    
    # Check API key for commands that need it
    if args.command in ['process', 'validate'] and not args.api_key and not args.mock:
        print("Error: API key required. Use --api-key or set BOTTLE_OCR_API_KEY environment variable", 
              file=sys.stderr)
        return 1
    
    # Execute command
    if args.command == 'process':
        return process_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    elif args.command == 'info':
        return info_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())