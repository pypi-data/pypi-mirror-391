"""
License Cache System
===================

Manages local caching of license validation results to minimize server requests.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict
import logging


logger = logging.getLogger(__name__)


class LicenseCache:
    """
    Manages local caching of license validation results.
    
    This class stores validated licenses locally to avoid repeated server requests.
    The cache includes expiration and integrity checking.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize license cache.
        
        Args:
            cache_dir: Directory for cache files (default: user's cache directory)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use system-appropriate cache directory
            if os.name == 'nt':  # Windows
                cache_base = Path(os.getenv('LOCALAPPDATA', os.path.expanduser('~')))
            else:  # Unix/Linux/Mac
                cache_base = Path(os.getenv('XDG_CACHE_HOME', os.path.expanduser('~/.cache')))
            
            self.cache_dir = cache_base / 'bottle_ocr_lib'
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"License cache directory: {self.cache_dir}")
    
    def _get_cache_file_path(self, api_key: str) -> Path:
        """Get cache file path for a specific API key."""
        # Hash the API key for security (don't store raw key)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return self.cache_dir / f"license_{key_hash}.json"
    
    def _create_cache_entry(self, api_key: str, validation_result: Dict) -> Dict:
        """Create a cache entry with integrity checking."""
        # Add cache metadata
        cache_entry = {
            'cached_at': int(time.time()),
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest(),
            'validation_result': validation_result,
            'version': '1.0.0'
        }
        
        # Create integrity hash
        cache_content = json.dumps(cache_entry['validation_result'], sort_keys=True)
        integrity_hash = hashlib.sha256(f"{cache_content}{api_key}".encode()).hexdigest()
        cache_entry['integrity_hash'] = integrity_hash
        
        return cache_entry
    
    def _verify_cache_entry(self, cache_entry: Dict, api_key: str) -> bool:
        """Verify the integrity of a cache entry."""
        try:
            # Check API key hash
            expected_hash = hashlib.sha256(api_key.encode()).hexdigest()
            if cache_entry.get('api_key_hash') != expected_hash:
                logger.warning("Cache entry API key hash mismatch")
                return False
            
            # Check integrity hash
            cache_content = json.dumps(cache_entry['validation_result'], sort_keys=True)
            expected_integrity = hashlib.sha256(f"{cache_content}{api_key}".encode()).hexdigest()
            if cache_entry.get('integrity_hash') != expected_integrity:
                logger.warning("Cache entry integrity hash mismatch")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache entry verification failed: {e}")
            return False
    
    def get_cached_license(self, api_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """
        Get cached license validation result.
        
        Args:
            api_key: API key to look up
            max_age_hours: Maximum age of cache entry in hours
            
        Returns:
            Cached validation result or None if not found/expired
        """
        cache_file = self._get_cache_file_path(api_key)
        
        if not cache_file.exists():
            logger.debug("No cache file found for API key")
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_entry = json.load(f)
            
            # Verify integrity
            if not self._verify_cache_entry(cache_entry, api_key):
                logger.warning("Cache entry failed verification, removing")
                cache_file.unlink(missing_ok=True)
                return None
            
            # Check age
            cached_at = cache_entry.get('cached_at', 0)
            age_seconds = time.time() - cached_at
            max_age_seconds = max_age_hours * 3600
            
            if age_seconds > max_age_seconds:
                logger.debug(f"Cache entry expired ({age_seconds/3600:.1f} hours old)")
                cache_file.unlink(missing_ok=True)
                return None
            
            # Check license expiration
            validation_result = cache_entry['validation_result']
            expires_at = validation_result.get('expires_at', 0)
            if expires_at > 0 and time.time() > expires_at:
                logger.warning("Cached license has expired")
                cache_file.unlink(missing_ok=True)
                return None
            
            logger.info(f"Using cached license validation (age: {age_seconds/3600:.1f} hours)")
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to read cache file: {e}")
            cache_file.unlink(missing_ok=True)
            return None
    
    def cache_license(self, api_key: str, validation_result: Dict) -> bool:
        """
        Cache a license validation result.
        
        Args:
            api_key: API key
            validation_result: Validation result to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            cache_entry = self._create_cache_entry(api_key, validation_result)
            cache_file = self._get_cache_file_path(api_key)
            
            with open(cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
            
            logger.debug(f"License cached successfully: {cache_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache license: {e}")
            return False
    
    def invalidate_license(self, api_key: str) -> bool:
        """
        Remove cached license for a specific API key.
        
        Args:
            api_key: API key to invalidate
            
        Returns:
            True if cache was removed, False if not found
        """
        cache_file = self._get_cache_file_path(api_key)
        
        if cache_file.exists():
            cache_file.unlink()
            logger.info("Cached license invalidated")
            return True
        else:
            logger.debug("No cached license to invalidate")
            return False
    
    def clear_all_cache(self) -> int:
        """
        Clear all cached licenses.
        
        Returns:
            Number of cache files removed
        """
        removed_count = 0
        
        try:
            for cache_file in self.cache_dir.glob("license_*.json"):
                cache_file.unlink()
                removed_count += 1
            
            logger.info(f"Cleared {removed_count} cached licenses")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
        
        return removed_count
    
    def get_cache_info(self) -> Dict:
        """
        Get information about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            cache_files = list(self.cache_dir.glob("license_*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            # Analyze cache entries
            valid_entries = 0
            expired_entries = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        cache_entry = json.load(f)
                    
                    cached_at = cache_entry.get('cached_at', 0)
                    age_hours = (time.time() - cached_at) / 3600
                    
                    if age_hours <= 24:  # Default max age
                        valid_entries += 1
                    else:
                        expired_entries += 1
                        
                except Exception:
                    expired_entries += 1
            
            return {
                'cache_directory': str(self.cache_dir),
                'total_entries': len(cache_files),
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'total_size_bytes': total_size,
                'total_size_kb': round(total_size / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
            return {
                'cache_directory': str(self.cache_dir),
                'error': str(e)
            }
    
    def cleanup_expired_cache(self, max_age_hours: int = 24) -> int:
        """
        Remove expired cache entries.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of entries removed
        """
        removed_count = 0
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        try:
            for cache_file in self.cache_dir.glob("license_*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        cache_entry = json.load(f)
                    
                    cached_at = cache_entry.get('cached_at', 0)
                    if current_time - cached_at > max_age_seconds:
                        cache_file.unlink()
                        removed_count += 1
                        
                except Exception:
                    # Remove corrupted cache files
                    cache_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
        
        return removed_count