"""
Script Metadata - Parse and manage script metadata from script files
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from app.core.log import logger


@dataclass
class ScriptMetadata:
    """Script metadata class."""
    
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    icon: str = ""
    help: str = ""
    file_path: Optional[Path] = None
    module_name: str = ""
    bias: int = 0
    filename: str = ""
    
    @classmethod
    def from_file(cls, file_path: Path, cache: Optional['MetadataCache'] = None) -> Optional['ScriptMetadata']:
        """Parse metadata from a script file.
        
        Args:
            file_path: Path to the script file
            cache: Optional metadata cache
            
        Returns:
            ScriptMetadata object or None if parsing fails
        """
        try:
            # Check cache first
            if cache:
                cached_metadata = cache.get(file_path)
                if cached_metadata:
                    return cls.from_dict(cached_metadata, file_path)
            
            # Read file content
            content = file_path.read_text(encoding='utf-8')
            
            # Extract metadata from docstring at the beginning of the file
            metadata_dict = None
            
            # Look for docstring after shebang and encoding lines
            # Check for Python docstring format (single quotes)
            docstring_match = re.search(r"^(?:\s*#[^\n]*\n*)*\s*'''(.*?)'''", content, re.DOTALL)
            if not docstring_match:
                # Check for Python docstring format (double quotes)
                docstring_match = re.search(r'^(?:\s*#[^\n]*\n*)*\s*"""(.*?)"""', content, re.DOTALL)
            
            if docstring_match:
                json_str = docstring_match.group(1).strip()
                try:
                    metadata_dict = json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Create metadata
            if metadata_dict:
                metadata = cls.from_dict(metadata_dict, file_path)
            else:
                # Fallback: create minimal metadata
                metadata = cls(
                    name=file_path.stem.replace('_', ' ').title(),
                    description=f"Script from {file_path.name}",
                    dependencies=[],
                    file_path=file_path,
                    module_name=f"script_{file_path.stem}",
                    filename=file_path.name
                )
            
            # Save to cache
            if cache:
                cache.set(file_path, metadata.to_dict())
            
            return metadata

        except Exception as e:
            logger.error(f"Error parsing metadata from {file_path}: {e}", exc_info=True)
            return None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], file_path: Path) -> 'ScriptMetadata':
        """Create metadata from dictionary.
        
        Args:
            data: Dictionary with metadata
            file_path: Path to the script file
            
        Returns:
            ScriptMetadata object
        """
        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]
        
        dependencies = data.get('dependencies', [])
        if isinstance(dependencies, str):
            dependencies = [dep.strip() for dep in dependencies.split(',')]
        
        return cls(
            name=data.get('name', file_path.stem.replace('_', ' ').title()),
            description=data.get('description', ''),
            tags=tags,
            dependencies=dependencies,
            icon=data.get('icon', ''),
            help=data.get('help', ''),
            file_path=file_path,
            module_name=f"script_{file_path.stem}",
            bias=data.get('bias', 0),
            filename=file_path.name
        )
    
    def get_search_text(self) -> str:
        """Get text for search indexing.
        
        Returns:
            Combined text for search
        """
        return f"{self.name} {self.description} {' '.join(self.tags)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary.
        
        Returns:
            Dictionary representation of metadata
        """
        return {
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'icon': self.icon,
            'help': self.help,
            'module_name': self.module_name,
            'bias': self.bias,
            'filename': self.filename
        }


