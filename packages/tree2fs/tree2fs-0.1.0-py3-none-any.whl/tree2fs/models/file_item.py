"""File item data model for representing files and directories."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class FileItem(BaseModel):
    """Represents a file or directory in the tree structure.
    
    Attributes:
        filename: Name of the file or directory
        level: Depth level in the directory hierarchy (0-based)
    """
    model_config = ConfigDict(validate_assignment=True, frozen=True)
    
    filename: str
    level: int = Field(ge=0, description="Level in directory hierarchy (0-based)")
    comment: str = ""
    line_number: int = 0
    
    @field_validator('filename')
    def filename_must_be_valid(cls, v: str) -> str:
        """Validate filename doesn't contain invalid characters.
        
        Args:
            v: Filename to validate
            
        Returns:
            Validated filename
            
        Raises:
            ValueError: If filename is invalid
        """
        if not v or v.isspace():
            raise ValueError('Filename cannot be empty or whitespace')
        
        # Check for invalid characters in filenames
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in v for char in invalid_chars):
            raise ValueError(f'Filename contains invalid characters: {invalid_chars}')
        
        return v
    
    @property
    def is_directory(self) -> bool:
        """Check if this represents a directory.
        
        Returns:
            True if this is a directory, False otherwise
        """
        return '.' not in self.filename or self.filename.endswith('/')
    
    @property
    def name(self) -> str:
        """Get the clean name without trailing slash.
        
        Returns:
            Filename without trailing slash
        """
        return self.filename.rstrip('/')
    
    @property
    def extension(self) -> Optional[str]:
        """Get file extension if applicable.
        
        Returns:
            File extension without the dot, or None for directories
        """
        if self.is_directory:
            return None
        return self.filename.split('.')[-1] if '.' in self.filename else None
    
    @property
    def name_without_extension(self) -> str:
        """Get filename without extension.
        
        Returns:
            Filename without extension
        """
        if self.is_directory:
            return self.filename.rstrip('/')
        return '.'.join(self.filename.split('.')[:-1]) if '.' in self.filename else self.filename
    
    def get_indented_display(self, indent_char: str = "  ") -> str:
        """Get formatted string with proper indentation.
        
        Args:
            indent_char: Character(s) to use for indentation
            
        Returns:
            Indented string representation
        """
        return f"{indent_char * self.level}{self.filename}"
    
    def __str__(self) -> str:
        return self.name
