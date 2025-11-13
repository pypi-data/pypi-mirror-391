"""
Configuration Management Module
==============================

Handles configuration loading, validation, and management for the BottleOCR library.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import logging


logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages configuration settings for the BottleOCR library.
    
    Supports loading from:
    - Environment variables
    - JSON files  
    - YAML files
    - Dictionary input
    - Default values
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        'auth': {
            'server_url': 'http://54.226.83.55',
            'timeout_seconds': 30,
            'cache_ttl_seconds': 300,
            'mock_mode': False
        },
        'ocr': {
            'language': 'en',
            'use_angle_classification': True,
            'max_dimension': 2048,
            'apply_clahe': False,
            'clahe_clip_limit': 2.0,
            'clahe_tile_grid_size': 8
        },
        'extraction': {
            'model': 'gpt-4o',
            'temperature': 0.1,
            'max_tokens': 2000,
            'enabled': True,
            'mock_mode': False
        },
        'processing': {
            'max_images_per_request': 10,
            'timeout_seconds': 120,
            'include_bbox': True,
            'min_confidence_threshold': 0.0
        },
        'output': {
            'format': 'json',
            'pretty_print': True,
            'include_metadata': True
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    def __init__(self, config_source: Optional[Union[str, Dict, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_source: Configuration source (file path, dict, or None for defaults)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_source:
            self.load_config(config_source)
        
        # Override with environment variables
        self._load_from_environment()
        
        logger.debug("ConfigManager initialized")
    
    def load_config(self, source: Union[str, Dict, Path]):
        """
        Load configuration from various sources.
        
        Args:
            source: Configuration source
            
        Raises:
            ValueError: If source cannot be loaded or parsed
        """
        if isinstance(source, dict):
            self._merge_config(source)
            logger.info("Loaded configuration from dictionary")
            
        elif isinstance(source, (str, Path)):
            config_path = Path(source)
            
            if not config_path.exists():
                raise ValueError(f"Configuration file not found: {config_path}")
            
            if config_path.suffix.lower() == '.json':
                self._load_json_config(config_path)
            elif config_path.suffix.lower() in ['.yaml', '.yml']:
                self._load_yaml_config(config_path)
            else:
                raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        else:
            raise ValueError(f"Unsupported config source type: {type(source)}")
    
    def _load_json_config(self, config_path: Path):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            self._merge_config(config_data)
            logger.info(f"Loaded configuration from JSON: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load JSON config {config_path}: {e}")
    
    def _load_yaml_config(self, config_path: Path):
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            self._merge_config(config_data)
            logger.info(f"Loaded configuration from YAML: {config_path}")
        except ImportError:
            raise ValueError("PyYAML package required for YAML config files. Install with: pip install PyYAML")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load YAML config {config_path}: {e}")
    
    def _load_from_environment(self):
        """Load configuration overrides from environment variables."""
        env_mappings = {
            'BOTTLE_OCR_AUTH_SERVER_URL': ('auth', 'server_url'),
            'BOTTLE_OCR_AUTH_TIMEOUT': ('auth', 'timeout_seconds'),
            'BOTTLE_OCR_AUTH_MOCK': ('auth', 'mock_mode'),
            'BOTTLE_OCR_OCR_LANGUAGE': ('ocr', 'language'),
            'BOTTLE_OCR_OCR_MAX_DIMENSION': ('ocr', 'max_dimension'),
            'BOTTLE_OCR_OCR_CLAHE': ('ocr', 'apply_clahe'),
            'BOTTLE_OCR_EXTRACTION_MODEL': ('extraction', 'model'),
            'BOTTLE_OCR_EXTRACTION_TEMPERATURE': ('extraction', 'temperature'),
            'BOTTLE_OCR_EXTRACTION_MOCK': ('extraction', 'mock_mode'),
            'BOTTLE_OCR_MAX_IMAGES': ('processing', 'max_images_per_request'),
            'BOTTLE_OCR_TIMEOUT': ('processing', 'timeout_seconds'),
            'BOTTLE_OCR_LOG_LEVEL': ('logging', 'level'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(value, section, key)
                self.set(f"{section}.{key}", converted_value)
                logger.debug(f"Set {section}.{key} from env var {env_var}")
    
    def _convert_env_value(self, value: str, section: str, key: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if key in ['mock_mode', 'use_angle_classification', 'apply_clahe', 'enabled', 'pretty_print', 'include_metadata', 'include_bbox']:
            return value.lower() in ['true', '1', 'yes', 'on']
        
        # Integer conversion
        if key in ['timeout_seconds', 'cache_ttl_seconds', 'max_dimension', 'clahe_tile_grid_size', 
                   'max_tokens', 'max_images_per_request']:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {section}.{key}: {value}")
                return value
        
        # Float conversion
        if key in ['clahe_clip_limit', 'temperature', 'min_confidence_threshold']:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Invalid float value for {section}.{key}: {value}")
                return value
        
        # String (default)
        return value
    
    def _merge_config(self, new_config: Dict):
        """Recursively merge new configuration with existing config."""
        def merge_dicts(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dicts(base[key], value)
                else:
                    base[key] = value
        
        merge_dicts(self.config, new_config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'auth.server_url')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path
            value: Value to set
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the final value
        config_ref[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
            
        Returns:
            Dictionary with section configuration
        """
        return self.config.get(section, {}).copy()
    
    def update_section(self, section: str, updates: Dict):
        """
        Update entire configuration section.
        
        Args:
            section: Section name
            updates: Dictionary with updates
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(updates)
    
    def to_dict(self) -> Dict:
        """Get full configuration as dictionary."""
        return self.config.copy()
    
    def to_json(self, indent: int = 2) -> str:
        """Get configuration as JSON string."""
        return json.dumps(self.config, indent=indent)
    
    def save_to_file(self, file_path: Union[str, Path], format: str = 'json'):
        """
        Save configuration to file.
        
        Args:
            file_path: Output file path
            format: File format ('json' or 'yaml')
        """
        file_path = Path(file_path)
        
        if format.lower() == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        elif format.lower() in ['yaml', 'yml']:
            try:
                import yaml
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
            except ImportError:
                raise ValueError("PyYAML package required for YAML output. Install with: pip install PyYAML")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Configuration saved to: {file_path}")
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []
        
        # Validate required sections
        required_sections = ['auth', 'ocr', 'processing']
        for section in required_sections:
            if section not in self.config:
                issues.append(f"Missing required section: {section}")
        
        # Validate auth section
        auth_config = self.config.get('auth', {})
        if 'server_url' not in auth_config or not auth_config['server_url']:
            issues.append("Missing auth.server_url")
        
        # Validate OCR section
        ocr_config = self.config.get('ocr', {})
        max_dim = ocr_config.get('max_dimension', 2048)
        if not isinstance(max_dim, int) or max_dim < 100 or max_dim > 8192:
            issues.append("ocr.max_dimension must be integer between 100 and 8192")
        
        # Validate processing limits
        processing_config = self.config.get('processing', {})
        max_images = processing_config.get('max_images_per_request', 10)
        if not isinstance(max_images, int) or max_images < 1 or max_images > 50:
            issues.append("processing.max_images_per_request must be integer between 1 and 50")
        
        return issues
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"ConfigManager({len(self.config)} sections)"


# Convenience function for quick config creation
def load_config(source: Optional[Union[str, Dict, Path]] = None) -> ConfigManager:
    """
    Create and return a configured ConfigManager instance.
    
    Args:
        source: Configuration source (file path, dict, or None)
        
    Returns:
        Configured ConfigManager instance
    """
    return ConfigManager(source)