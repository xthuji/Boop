"""
Script Loader - Load and manage Python scripts from configured directories
"""

import sys
import importlib.util
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from boop.config.settings import BoopConfig
from boop.core.script_metadata import ScriptMetadata
from boop.core.event import event_system


@dataclass
class LoadedScript:
    """A loaded script with its metadata and module."""
    metadata: ScriptMetadata
    module: object
    file_path: Path
    is_valid: bool = True
    error_message: str = ""


class ScriptManager:
    """Loads and manages Python scripts from configured directories."""
    
    def __init__(self, config: Optional[BoopConfig] = None):
        self.config = config
        self._scripts: Dict[str, LoadedScript] = {}
        self._module_cache: Dict[str, object] = {}
        self._file_mtimes: Dict[str, float] = {}  # Cache file modification times
        self._script_categories: Dict[str, List[LoadedScript]] = {}  # Cache scripts by category
    
    def load_scripts(self) -> int:
        """Load all scripts from configured directories."""
        if not self.config:
            return 0
        
        self._scripts.clear()
        self._module_cache.clear()
        self._file_mtimes.clear()
        self._script_categories.clear()
        
        print(f"Loading scripts from directories: {self.config.script_directories}")
        
        count = 0
        for script_dir in self.config.script_directories:
            script_dir_path = Path(script_dir)
            print(f"Checking directory: {script_dir_path}")
            print(f"Directory exists: {script_dir_path.exists()}")
            count += self._load_from_directory(script_dir_path)
        
        print(f"Loaded {count} scripts")
        print(f"Scripts in _scripts: {list(self._scripts.keys())}")
        
        # Build category index
        self._build_category_index()
        
        # Publish scripts loaded event
        event_system.publish('scripts_loaded', count=count)
        
        return count
    
    def _load_from_directory(self, directory: Path) -> int:
        """Load all scripts from a directory with file modification time check."""
        if not directory.exists():
            return 0
        
        print(f"Loading scripts from directory: {directory}")
        count = 0
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                print(f"Skipping file: {file_path.name}")
                continue
            
            print(f"Processing file: {file_path.name}")
            # Check if file has changed
            file_key = str(file_path.absolute())
            current_mtime = file_path.stat().st_mtime
            cached_mtime = self._file_mtimes.get(file_key)
            
            # Load script regardless of whether it has changed
            # This ensures scripts are added to the dictionary on first load
            loaded = self._load_script(file_path)
            if loaded and loaded.is_valid:
                print(f"Loaded script: {loaded.metadata.name}")
                self._scripts[loaded.metadata.name.lower()] = loaded
                self._file_mtimes[file_key] = current_mtime
                count += 1
            else:
                print(f"Failed to load script: {file_path.name}, error: {loaded.error_message if loaded else 'Unknown error'}")
        
        print(f"Loaded {count} scripts from directory: {directory}")
        return count
    
    def _build_category_index(self):
        """Build index of scripts by category."""
        self._script_categories.clear()
        
        for script in self._scripts.values():
            for tag in script.metadata.tags:
                if tag not in self._script_categories:
                    self._script_categories[tag] = []
                self._script_categories[tag].append(script)
    
    def get_scripts_by_category(self, category: str) -> List[LoadedScript]:
        """Get scripts by category."""
        return self._script_categories.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories."""
        return list(self._script_categories.keys())
    
    def _load_script(self, file_path: Path) -> Optional[LoadedScript]:
        """Load a single script file."""
        try:
            metadata = ScriptMetadata.from_file(file_path)
            if not metadata:
                return LoadedScript(
                    metadata=ScriptMetadata(file_path=file_path),
                    module=None,
                    file_path=file_path,
                    is_valid=False,
                    error_message="Failed to parse metadata"
                )
            
            module = self._load_module(file_path, metadata.module_name)
            if not module:
                return LoadedScript(
                    metadata=metadata,
                    module=None,
                    file_path=file_path,
                    is_valid=False,
                    error_message="Failed to load module"
                )
            
            if not hasattr(module, "main"):
                return LoadedScript(
                    metadata=metadata,
                    module=module,
                    file_path=file_path,
                    is_valid=False,
                    error_message="Missing main() function"
                )
            
            return LoadedScript(
                metadata=metadata,
                module=module,
                file_path=file_path,
                is_valid=True
            )
            
        except Exception as e:
            error_msg = str(e)
            event_system.publish('script_load_error', script_path=str(file_path), error=error_msg)
            return LoadedScript(
                metadata=ScriptMetadata(file_path=file_path),
                module=None,
                file_path=file_path,
                is_valid=False,
                error_message=error_msg
            )
    
    def _load_module(self, file_path: Path, module_name: str) -> Optional[object]:
        """Load a Python module from file."""
        try:
            cache_key = str(file_path.absolute())
            if cache_key in self._module_cache:
                return self._module_cache[cache_key]
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self._module_cache[cache_key] = module
            return module
            
        except Exception as e:
            print(f"Error loading module {file_path}: {e}")
            return None
    
    def get_script(self, name: str) -> Optional[LoadedScript]:
        """Get a loaded script by name (case-insensitive)."""
        return self._scripts.get(name.lower())
    
    def list_scripts(self) -> List[LoadedScript]:
        """Get all loaded scripts."""
        return list(self._scripts.values())
    
    def search_scripts(self, query: str) -> List[LoadedScript]:
        """Search for scripts matching a query."""
        if not query:
            return self.list_scripts()
        
        query_lower = query.lower()
        results = []
        
        for script in self._scripts.values():
            search_text = script.metadata.get_search_text().lower()
            if query_lower in search_text:
                results.append(script)
        
        results.sort(key=lambda s: s.metadata.bias, reverse=True)
        return results
    
    def get_script_names(self) -> List[str]:
        """Get all script names."""
        return [s.metadata.name for s in self._scripts.values()]
    
    def __len__(self):
        return len(self._scripts)
