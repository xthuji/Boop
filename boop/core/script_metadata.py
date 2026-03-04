"""
Script Metadata - Parse and manage script metadata from script files
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ScriptMetadata:
    """Script metadata class."""
    
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    icon: str = ""
    help: str = ""
    author: str = ""
    api: int = 1
    file_path: Optional[Path] = None
    module_name: str = ""
    bias: int = 0
    
    @classmethod
    def from_file(cls, file_path: Path) -> Optional['ScriptMetadata']:
        """Parse metadata from a script file.
        
        Args:
            file_path: Path to the script file
            
        Returns:
            ScriptMetadata object or None if parsing fails
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract JSON from comments
            # Check for Python docstring format (double quotes)
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if not docstring_match:
                # Check for Python docstring format (single quotes)
                docstring_match = re.search(r"'''(.*?)'''", content, re.DOTALL)
            if not docstring_match:
                # Check for JavaScript comment format
                docstring_match = re.search(r'/\*\*(.*?)\*\*/', content, re.DOTALL)
            
            if docstring_match:
                json_str = docstring_match.group(1)
                try:
                    metadata_dict = json.loads(json_str)
                    return cls.from_dict(metadata_dict, file_path)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: create minimal metadata
            return cls(
                name=file_path.stem.replace('_', ' ').title(),
                description=f"Script from {file_path.name}",
                dependencies=[],
                file_path=file_path,
                module_name=f"script_{file_path.stem}"
            )
            
        except Exception as e:
            print(f"Error parsing metadata from {file_path}: {e}")
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
            author=data.get('author', ''),
            api=data.get('api', 1),
            file_path=file_path,
            module_name=f"script_{file_path.stem}",
            bias=data.get('bias', 0)
        )
    
    def get_search_text(self) -> str:
        """Get text for search indexing.
        
        Returns:
            Combined text for search
        """
        return f"{self.name} {self.description} {' '.join(self.tags)} {self.author}"
