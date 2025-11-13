# 🏥 BottleOCR Library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Professional OCR and AI-powered prescription extraction library with secure license validation and local processing capabilities.

## ✨ Features

- 🔍 **High-Accuracy OCR** - Advanced PaddleOCR text extraction
- 🤖 **AI-Powered Analysis** - OpenAI GPT-4 prescription data extraction  
- 🔐 **Secure License System** - One-time server validation, then local processing
- 🖼️ **Multi-Format Support** - JPEG, PNG, TIFF, BMP, PDF, numpy arrays, PIL Images
- ⚡ **Batch Processing** - Process multiple images efficiently
- 💾 **Smart Caching** - Offline operation after initial validation
- 🛠️ **Easy Integration** - Simple API with comprehensive documentation
- 📊 **Structured Output** - 18+ prescription fields extracted automatically

## 🚀 Quick Start

### Installation

```bash
pip install bottle-ocr-lib
```

### Basic Usage

```python
from bottle_ocr_lib import BottleOCR

# Initialize with your API key (validates once, then works offline)
ocr = BottleOCR(api_key="your-api-key-here")

# Process prescription bottle images
result = ocr.process_single_image("prescription_bottle.jpg")

# Access extracted prescription data
prescription = result['prescription']
print(f"💊 Medication: {prescription['medication_name']}")
print(f"💉 Dosage: {prescription['dosage']}")
print(f"👤 Patient: {prescription['patient_name']}")
print(f"🏥 Pharmacy: {prescription['pharmacy_name']}")
```

### Batch Processing

```python
# Process multiple images at once
results = ocr.process_images([
    "bottle_front.jpg",
    "bottle_back.jpg", 
    "label_close_up.png"
])

for i, result in enumerate(results['images']):
    if result['status'] == 'success':
        prescription = result['prescription']
        print(f"Image {i+1}: {prescription['medication_name']}")
```

## 🔐 License System

BottleOCR uses a secure validation system enabling **complete local processing**:

1. **Initial Validation**: Your API key validates with our server (one-time only)
2. **Encoded Key Delivery**: Server provides encrypted OpenAI API key
3. **Local Processing**: All subsequent operations run offline on your machine
4. **Smart Caching**: No repeated server communication required

```python
# First run: Server validation + local caching
ocr = BottleOCR(api_key="your-key")  # ✅ Online validation

# All future runs: Instant startup from cache  
ocr = BottleOCR(api_key="your-key")  # ✅ Offline, instant
results = ocr.process_images(images)  # ✅ 100% local processing
```

## 📊 Extracted Prescription Data

The library extracts comprehensive prescription information:

| Field | Description | Example |
|-------|-------------|---------|
| `medication_name` | Drug name | "Amoxicillin" |
| `dosage` | Strength/amount | "500mg" |
| `quantity_dispensed` | Amount given | "30 capsules" |
| `patient_name` | Patient name | "John Doe" |
| `prescriber_name` | Doctor name | "Dr. Smith" |
| `pharmacy_name` | Pharmacy name | "Main St Pharmacy" |
| `prescription_date` | Fill date | "2024-10-25" |
| `expiration_date` | Expiry date | "2025-10-25" |
| `directions_for_use` | Instructions | "Take twice daily" |
| `refills_remaining` | Refills left | "2" |
| `rx_number` | Prescription # | "RX7654321" |
| `ndc_number` | NDC code | "12345-678-90" |
| `lot_number` | Lot number | "ABC123" |
| `manufacturer` | Drug maker | "Generic Co" |
| `warning_labels` | Warnings | "May cause drowsiness" |
| `storage_instructions` | Storage | "Store at room temp" |
| `dosage_form` | Form type | "Capsule" |
| `description_of_pill` | Appearance | "Blue oval tablet" |

## 🖥️ Command Line Interface

```bash
# Process single image
bottle-ocr process image.jpg --api-key your-key

# Process multiple images
bottle-ocr batch *.jpg --output results.json --api-key your-key

# Get account information
bottle-ocr info --api-key your-key

# Validate images without processing
bottle-ocr validate image1.jpg image2.jpg --api-key your-key
```

## ⚙️ Configuration

### Environment Variables
```bash
export BOTTLEOCR_API_KEY="your-api-key"
```

### Custom Configuration
```python
config = {
    "ocr": {
        "language": "en",
        "confidence_threshold": 0.8,
        "use_gpu": True
    },
    "extraction": {
        "model": "gpt-4",
        "temperature": 0.1
    }
}

ocr = BottleOCR(api_key="your-key", config=config)
```

## 📝 Complete Example

```python
from bottle_ocr_lib import BottleOCR
from bottle_ocr_lib.utils.exceptions import AuthenticationError, ValidationError

try:
    # Initialize (validates license once)
    ocr = BottleOCR(api_key="your-api-key")
    
    # Process images (works offline after validation)
    results = ocr.process_images([
        "prescription1.jpg",
        "bottle_label.png"
    ])
    
    # Extract prescription information
    for i, result in enumerate(results['images']):
        if result['status'] == 'success':
            p = result['prescription']
            print(f"""
Image {i+1}:
  Medication: {p['medication_name']}
  Dosage: {p['dosage']}
  Patient: {p['patient_name']}
  Instructions: {p['directions_for_use']}
  Refills: {p['refills_remaining']}
            """)
        else:
            print(f"Image {i+1} failed: {result['error']}")
            
except AuthenticationError as e:
    print(f"❌ License validation failed: {e}")
except ValidationError as e:
    print(f"❌ Invalid input: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## 🔧 Requirements

- **Python**: 3.8 or higher
- **Platform**: Windows, macOS, Linux
- **Dependencies**: Automatically installed
  - PaddleOCR >= 2.7.0
  - OpenAI >= 1.0.0
  - OpenCV >= 4.5.0
  - Pillow >= 8.0.0
  - PyYAML >= 5.4.0

## 🆘 Getting an API Key

1. **Sign up**: Visit [bottleocr.com](https://bottleocr.com) to create an account
2. **Choose Plan**: Select the subscription that fits your needs
3. **Get Key**: Receive your API key via email after signup
4. **Start Processing**: Use your key to process prescription images immediately

## 📖 Documentation & Support

- 📚 **Examples**: See `examples/` directory for complete usage patterns
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/bottle-ocr-lib/issues)
- 💬 **Support**: support@bottleocr.com
- 📖 **API Docs**: Comprehensive docstrings in all methods

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Why Choose BottleOCR?

- ✅ **Production Ready** - Battle-tested accuracy and reliability
- ✅ **Privacy First** - Your data stays on your machine after validation
- ✅ **Developer Friendly** - Simple API, great documentation, quick setup
- ✅ **Cost Effective** - Pay once, process locally forever
- ✅ **Scalable** - Handle single images or large batch processing
- ✅ **Secure** - Encrypted license validation with local operation

---

**Ready to extract prescription data professionally? [Get your API key today!](https://bottleocr.com)** 🚀