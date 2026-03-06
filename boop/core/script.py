"""
Script Loader - Load and manage Python scripts from configured directories
"""
from pathlib import Path

from boop.config.settings import BoopConfig
from boop.core.cache import MetadataCache
from boop.core.script_metadata import ScriptMetadata
from boop.core.logging import logger


class ScriptManager:
    """Loads and manages Python scripts from configured directories."""
    
    def __init__(self, config: BoopConfig = None):
        self.config = config
        self._metadata_cache = MetadataCache()  # Use MetadataCache for caching
    
    def clear_metadata_cache(self):
        """Clear metadata cache."""
        self._metadata_cache.clear()
        logger.info("Metadata cache cleared successfully")

    def refresh_metadata_cache(self) -> int:
        """Refresh metadata cache by clearing and reloading.

        Returns:
            Number of scripts loaded
            
        Raises:
            Exception: If any error occurs during the refresh process
        """
        # Clear existing cache
        self.clear_metadata_cache()
        # Reload metadata
        total_scripts = self.load_metadata()
        logger.info(f"Metadata cache refreshed successfully. Loaded {total_scripts} scripts.")
        return total_scripts
    
    def load_metadata(self) -> int:
        """Load metadata for all scripts in configured directories.

        Returns:
            Number of scripts loaded
        """
        total_scripts = 0
        has_changes = False

        if not self.config:
            return total_scripts

        # Get script directories from config
        script_dirs = self.config.script_directories

        # Load metadata for all scripts in configured directories
        for script_dir in script_dirs:
            script_dir_path = Path(script_dir)
            if script_dir_path.exists() and script_dir_path.is_dir():
                for file_path in script_dir_path.glob("*.py"):
                    if file_path.name.startswith("_"):
                        continue

                    # Load metadata for the script
                    metadata = ScriptMetadata.from_file(file_path, self._metadata_cache)
                    if metadata:
                        total_scripts += 1
                        has_changes = True

        # Save cache to disk once after all scripts are loaded (batch write)
        if has_changes:
            self._metadata_cache.save()

        return total_scripts
    
    def get_all_metadata(self):
        """Get all cached metadata.
        
        Returns:
            Dictionary of all cached metadata
        """
        return self._metadata_cache.get_all()
    
    def get_metadata(self, file_path):
        """Get metadata for a specific script.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self._metadata_cache.get(file_path)
    
    def create_metadata_from_dict(self, metadata_dict, file_path):
        """Create ScriptMetadata object from dictionary.

        Args:
            metadata_dict: Metadata dictionary
            file_path: Path to the script file

        Returns:
            ScriptMetadata object or None if creation fails
        """
        try:
            return ScriptMetadata.from_dict(metadata_dict, Path(file_path))
        except Exception as e:
            logger.warning(f"Error creating metadata from dict: {e}")
            return None
