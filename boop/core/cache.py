"""
Cache Management - Provides caching functionality for script metadata
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from boop.core.path import get_user_data_dir
from boop.core.log import logger


class MetadataCache:
    """Metadata cache manager using JSON file storage."""
    
    def __init__(self):
        """Initialize the metadata cache."""
        # Get user data directory (handles both development and bundled environments)
        user_data_dir = get_user_data_dir()
        
        # Cache directory in user data directory
        self.cache_dir = user_data_dir / "cache"
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file path
        self.cache_file = self.cache_dir / "metadata.json"
        
        # In-memory cache
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
        
        # Load cache from disk if it exists
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk into memory."""
        if not self.cache_file.exists():
            self._memory_cache = {}
            self._loaded = True
            return

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._memory_cache = json.load(f)
            self._loaded = True
        except Exception as e:
            logger.error(f"Error loading metadata cache: {e}", exc_info=True)
            self._memory_cache = {}
            self._loaded = True

    def _save_cache(self):
        """Save cache from memory to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._memory_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving metadata cache: {e}", exc_info=True)
    
    def get(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get metadata from cache.

        Args:
            file_path: Path to the script file

        Returns:
            Cached metadata dictionary or None if not found or outdated
        """
        if not self._loaded:
            self._load_cache()

        file_key = str(file_path.absolute())
        try:
            # Get cached data
            cached_data = self._memory_cache.get(file_key)
            if cached_data:
                # Check if file has changed
                file_mtime = file_path.stat().st_mtime
                if cached_data['mtime'] >= file_mtime:
                    return cached_data['metadata']
        except Exception as e:
            logger.warning(f"Error getting metadata from cache: {e}")
        return None
    
    def set(self, file_path: Path, metadata: Dict[str, Any]):
        """Set metadata in cache.

        Note: This method does NOT save to disk automatically.
        Call save() explicitly after batch operations.

        Args:
            file_path: Path to the script file
            metadata: Metadata dictionary to cache
        """
        if not self._loaded:
            self._load_cache()

        file_key = str(file_path.absolute())
        try:
            file_mtime = file_path.stat().st_mtime
            self._memory_cache[file_key] = {
                'mtime': file_mtime,
                'metadata': metadata
            }
            # Note: Removed automatic _save_cache() call
            # Caller should call save() explicitly after batch operations
        except Exception as e:
            logger.warning(f"Error setting metadata in cache: {e}")

    def save(self):
        """Save cache to disk. Call this after batch set() operations."""
        self._save_cache()
    
    def clear(self):
        """Clear all cache."""
        try:
            self._memory_cache = {}
            if self.cache_file.exists():
                self.cache_file.unlink()
            logger.info("Metadata cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing metadata cache: {e}", exc_info=True)
    
    def close(self):
        """Close the cache."""
        # Save cache to disk
        self._save_cache()
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all metadata from cache.

        Returns:
            Dictionary of all cached metadata, keyed by file path
        """
        if not self._loaded:
            self._load_cache()

        all_metadata = {}
        try:
            for file_key, cached_data in self._memory_cache.items():
                try:
                    if cached_data:
                        all_metadata[file_key] = cached_data['metadata']
                except Exception as e:
                    logger.warning(f"Error getting metadata for {file_key}: {e}")
        except Exception as e:
            logger.warning(f"Error getting all metadata: {e}")
        return all_metadata
