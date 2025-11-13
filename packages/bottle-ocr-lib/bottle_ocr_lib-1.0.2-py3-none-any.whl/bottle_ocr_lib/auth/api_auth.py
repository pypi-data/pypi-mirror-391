"""
API Key Authentication Module
============================

This module handles API key validation against a remote authentication server.
"""

import requests
import time
import hashlib
import logging
import json
import base64
import platform
from typing import Dict, Optional, Tuple
from urllib.parse import urljoin

from ..utils.license_cache import LicenseCache


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when API key authentication fails."""
    pass


class APIKeyValidator:
    """
    Validates API keys against a remote authentication server.
    
    This class handles:
    - API key validation
    - Rate limiting checks
    - Usage quota verification
    - Cached validation results
    """
    
    def __init__(self, auth_server_url: str, timeout: int = 30, 
                 cache_enabled: bool = True, cache_hours: int = 24):
        """
        Initialize the API key validator.
        
        Args:
            auth_server_url: URL of the authentication server
            timeout: Request timeout in seconds
            cache_enabled: Whether to use persistent license caching
            cache_hours: Hours to cache valid licenses
        """
        self.auth_server_url = auth_server_url.rstrip('/')
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.cache_hours = cache_hours
        
        # Initialize persistent cache
        if cache_enabled:
            self.license_cache = LicenseCache()
        else:
            self.license_cache = None
        
        # Keep legacy in-memory cache for backward compatibility
        self._cache = {}  # Simple in-memory cache for validation results
        self._cache_ttl = 300  # 5 minutes cache TTL
        
        logger.info(f"Initialized APIKeyValidator with server: {self.auth_server_url}, persistent cache: {cache_enabled}")
    
    def validate_api_key(self, api_key: str, service: str = "ocr", 
                        force_refresh: bool = False) -> Dict:
        """
        Validate an API key against the remote server with persistent caching.
        
        Args:
            api_key: The API key to validate
            service: The service being requested (default: "ocr")
            force_refresh: Force server validation even if cached
            
        Returns:
            Dict containing validation result and user info
            
        Raises:
            AuthenticationError: If API key is invalid or validation fails
        """
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key cannot be empty")
        
        # Check persistent cache first (unless force refresh requested)
        if not force_refresh and self.cache_enabled and self.license_cache:
            cached_result = self.license_cache.get_cached_license(api_key, self.cache_hours)
            if cached_result:
                # Convert cached result to expected format
                result = {
                    'valid': True,
                    'openai_api_key': cached_result.get('openai_key'),
                    'user_id': cached_result.get('user_id', 'cached_user'),
                    'plan': cached_result.get('plan', 'standard'),
                    'expires_at': cached_result.get('expires_at', 0),
                    'cached': True
                }
                logger.info("Using persistent cached license validation")
                return result
        
        # Fallback to legacy in-memory cache
        cache_key = self._get_cache_key(api_key, service)
        if not force_refresh:
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                logger.debug("Using legacy cached validation result")
                return cached_result
        
        # Validate with remote server
        try:
            result = self._validate_with_server(api_key, service)
            
            # Cache successful validation
            if result.get('valid', False):
                # Cache in legacy cache
                self._cache_result(cache_key, result)
                
                # Cache in persistent cache if enabled
                if self.cache_enabled and self.license_cache:
                    cache_data = {
                        'openai_key': result.get('openai_api_key'),
                        'user_id': result.get('user_id'),
                        'plan': result.get('plan'),
                        'validated_at': int(time.time()),
                        'expires_at': result.get('expires_at', 0)
                    }
                    self.license_cache.cache_license(api_key, cache_data)
                    logger.debug("License validation cached persistently")
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to connect to authentication server: {e}")
            raise AuthenticationError(f"Authentication server unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            raise AuthenticationError(f"Validation failed: {str(e)}")
    
    def _validate_with_server(self, api_key: str, service: str) -> Dict:
        """
        Perform license validation with the remote server and retrieve OpenAI API key.
        
        This method validates the API key with your server and receives an encoded
        OpenAI API key that allows the library to run locally without further
        server communication.
        
        Args:
            api_key: API key to validate
            service: Service being requested
            
        Returns:
            Validation result dictionary with decoded OpenAI API key
        """
        endpoint = urljoin(self.auth_server_url, '/validate')
        
        # Include system information for license validation
        import platform
        import sys
        
        payload = {
            'api_key': api_key,
            'service': service,
            'timestamp': int(time.time()),
            'client_version': '1.0.0',
            'system_info': {
                'python_version': sys.version,
                'platform': platform.platform(),
                'machine': platform.machine()
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BottleOCR-Library/1.0.0',
            'X-Client-Type': 'python-sdk',
            'X-License-Request': 'true'
        }
        
        logger.debug(f"Requesting license validation from server: {endpoint}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        # Handle different response codes
        if response.status_code == 200:
            result = response.json()
            if result.get('valid', False):
                logger.info("License validation successful")
                
                # Decode the OpenAI API key from server response
                encoded_openai_key = result.get('encoded_openai_key')
                if encoded_openai_key:
                    try:
                        decoded_key = self._decode_openai_key(encoded_openai_key, api_key)
                        result['openai_api_key'] = decoded_key
                        logger.info("OpenAI API key decoded successfully - library now runs locally")
                    except Exception as e:
                        logger.error(f"Failed to decode OpenAI API key: {e}")
                        raise AuthenticationError("License validation failed - invalid key encoding")
                else:
                    logger.warning("No OpenAI API key provided by server")
                
                return result
            else:
                error_msg = result.get('error', 'Invalid API key')
                logger.warning(f"License validation failed: {error_msg}")
                raise AuthenticationError(error_msg)
        
        elif response.status_code == 401:
            logger.warning("License authentication failed - invalid API key")
            raise AuthenticationError("Invalid API key - please check your license")
        
        elif response.status_code == 402:
            logger.warning("License expired or payment required")
            raise AuthenticationError("License expired or payment required. Please renew your subscription.")
        
        elif response.status_code == 429:
            logger.warning("Rate limit exceeded")
            raise AuthenticationError("Too many validation requests. Please try again later.")
        
        elif response.status_code == 403:
            logger.warning("License access forbidden")
            raise AuthenticationError("License access forbidden. Please contact support.")
        
        else:
            logger.error(f"Unexpected response from license server: {response.status_code}")
            try:
                error_detail = response.json().get('error', 'Unknown error')
            except:
                error_detail = f"HTTP {response.status_code}"
            raise AuthenticationError(f"License server error: {error_detail}")
    
    def _decode_openai_key(self, encoded_key: str, api_key: str) -> str:
        """
        Decode the OpenAI API key using the client API key as the decoding key.
        
        Args:
            encoded_key: Base64 encoded OpenAI API key from server
            api_key: Client API key used as decoding key
            
        Returns:
            Decoded OpenAI API key
        """
        import base64
        import hashlib
        
        try:
            # Create decoding key from API key bytes (matches server encoding)
            decoding_key = api_key.encode('utf-8')
            
            # Decode base64
            encoded_bytes = base64.b64decode(encoded_key.encode())
            
            # Simple XOR decoding to match server encoding
            decoded_bytes = bytearray()
            for i, byte in enumerate(encoded_bytes):
                decoded_bytes.append(byte ^ decoding_key[i % len(decoding_key)])
            
            decoded_key = decoded_bytes.decode('utf-8')
            
            # Validate OpenAI key format (starts with 'sk-')
            if not decoded_key.startswith('sk-'):
                raise ValueError("Invalid OpenAI API key format")
            
            return decoded_key
            
        except Exception as e:
            logger.error(f"OpenAI key decoding failed: {e}")
            raise ValueError("Failed to decode OpenAI API key")
    
    def check_usage_limits(self, validation_result: Dict) -> Tuple[bool, str]:
        """
        Check if the user has exceeded usage limits.
        
        Args:
            validation_result: Result from validate_api_key()
            
        Returns:
            Tuple of (allowed, message)
        """
        usage_info = validation_result.get('usage', {})
        limits = validation_result.get('limits', {})
        
        # Check daily request limit
        daily_requests = usage_info.get('daily_requests', 0)
        daily_limit = limits.get('daily_requests', float('inf'))
        
        if daily_requests >= daily_limit:
            return False, f"Daily request limit exceeded ({daily_requests}/{daily_limit})"
        
        # Check monthly request limit
        monthly_requests = usage_info.get('monthly_requests', 0)
        monthly_limit = limits.get('monthly_requests', float('inf'))
        
        if monthly_requests >= monthly_limit:
            return False, f"Monthly request limit exceeded ({monthly_requests}/{monthly_limit})"
        
        # Check rate limiting
        if validation_result.get('rate_limited', False):
            return False, "Rate limited. Please wait before making another request."
        
        return True, "Usage within limits"
    
    def get_user_info(self, validation_result: Dict) -> Dict:
        """
        Extract user information from validation result.
        
        Args:
            validation_result: Result from validate_api_key()
            
        Returns:
            Dictionary with user information
        """
        return {
            'user_id': validation_result.get('user_id'),
            'plan': validation_result.get('plan', 'unknown'),
            'permissions': validation_result.get('permissions', []),
            'usage': validation_result.get('usage', {}),
            'limits': validation_result.get('limits', {}),
        }
    
    def _get_cache_key(self, api_key: str, service: str) -> str:
        """Generate a cache key for the API key and service."""
        key_hash = hashlib.sha256(f"{api_key}:{service}".encode()).hexdigest()[:16]
        return f"auth_{key_hash}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached validation result if still valid."""
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            if time.time() - cached_data['timestamp'] < self._cache_ttl:
                return cached_data['result']
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache a validation result."""
        self._cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def clear_cache(self):
        """Clear all cached validation results."""
        self._cache.clear()
        logger.info("Authentication cache cleared")
    
    def invalidate_license_cache(self, api_key: str) -> bool:
        """
        Invalidate cached license for a specific API key.
        
        Args:
            api_key: API key to invalidate
            
        Returns:
            True if cache was invalidated, False if not found
        """
        if self.cache_enabled and self.license_cache:
            return self.license_cache.invalidate_license(api_key)
        return False
    
    def clear_license_cache(self) -> int:
        """
        Clear all persistent license cache.
        
        Returns:
            Number of cache entries removed
        """
        if self.cache_enabled and self.license_cache:
            return self.license_cache.clear_all_cache()
        return 0
    
    def get_cache_info(self) -> Dict:
        """
        Get information about the license cache.
        
        Returns:
            Dictionary with cache statistics
        """
        if self.cache_enabled and self.license_cache:
            return self.license_cache.get_cache_info()
        else:
            return {
                'cache_enabled': False,
                'message': 'Persistent cache is disabled'
            }
    
    def cleanup_expired_cache(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        if self.cache_enabled and self.license_cache:
            return self.license_cache.cleanup_expired_cache(self.cache_hours)
        return 0


class MockAPIKeyValidator(APIKeyValidator):
    """
    Mock validator for testing and development.
    
    This class simulates license validation and provides a mock OpenAI API key.
    Use only for development and testing!
    """
    
    def __init__(self):
        """Initialize mock validator."""
        super().__init__("http://mock-server", timeout=1)
        self.valid_keys = {
            'test-key-123': {
                'user_id': 'test-user-1',
                'plan': 'basic',
                'permissions': ['ocr', 'prescription_extraction'],
                'usage': {'daily_requests': 5, 'monthly_requests': 150},
                'limits': {'daily_requests': 100, 'monthly_requests': 1000},
                'license_type': 'development',
                'expires_at': int(time.time()) + (30 * 24 * 3600)  # 30 days from now
            },
            'premium-key-456': {
                'user_id': 'premium-user-1', 
                'plan': 'premium',
                'permissions': ['ocr', 'prescription_extraction', 'batch_processing'],
                'usage': {'daily_requests': 25, 'monthly_requests': 500},
                'limits': {'daily_requests': 1000, 'monthly_requests': 10000},
                'license_type': 'commercial',
                'expires_at': int(time.time()) + (365 * 24 * 3600)  # 1 year from now
            }
        }
        logger.warning("Using MockAPIKeyValidator - FOR DEVELOPMENT ONLY!")
    
    def _validate_with_server(self, api_key: str, service: str) -> Dict:
        """Mock validation that simulates license validation with OpenAI key delivery."""
        time.sleep(0.2)  # Simulate network delay
        
        if api_key in self.valid_keys:
            user_data = self.valid_keys[api_key].copy()
            
            # Simulate encoded OpenAI API key from server
            mock_openai_key = "sk-mock-openai-key-for-development-only"
            encoded_key = self._encode_openai_key(mock_openai_key, api_key)
            
            result = {
                'valid': True,
                'service': service,
                'timestamp': int(time.time()),
                'encoded_openai_key': encoded_key,
                'license_validated': True,
                'local_processing_enabled': True,
                **user_data
            }
            
            # Decode the key to simulate the full process
            decoded_key = self._decode_openai_key(encoded_key, api_key)
            result['openai_api_key'] = decoded_key
            
            logger.info(f"Mock license validation successful for {user_data['license_type']} license")
            return result
        else:
            raise AuthenticationError("Invalid API key")
    
    def _encode_openai_key(self, openai_key: str, api_key: str) -> str:
        """Mock encoding of OpenAI API key (matches server encoding)."""
        import base64
        
        # XOR encoding with API key as seed (matches server)
        key_bytes = openai_key.encode('utf-8')
        seed_bytes = api_key.encode('utf-8')
        
        encoded = bytearray()
        for i, byte in enumerate(key_bytes):
            seed_byte = seed_bytes[i % len(seed_bytes)]
            encoded.append(byte ^ seed_byte)
        
        # Base64 encode the result
        return base64.b64encode(encoded).decode('utf-8')


# Convenience function for quick validation
def validate_api_key(api_key: str, auth_server_url: str = None, mock: bool = False) -> Dict:
    """
    Convenience function for API key validation.
    
    Args:
        api_key: API key to validate
        auth_server_url: Authentication server URL (optional)
        mock: Use mock validator for testing (default: False)
        
    Returns:
        Validation result dictionary
        
    Raises:
        AuthenticationError: If validation fails
    """
    if mock:
        validator = MockAPIKeyValidator()
    else:
        if not auth_server_url:
            auth_server_url = "https://api.bottleocr.com/validate"
        validator = APIKeyValidator(auth_server_url)
    
    return validator.validate_api_key(api_key)