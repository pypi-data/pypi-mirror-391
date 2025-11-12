"""Tree node structure for directory tree representation."""

from pathlib import Path
from typing import List, Optional
from .file_item import FileItem


class Node:
    """Node in a tree structure representing a file or directory.
    
    Attributes:
        data: FileItem containing file/directory information
        children: List of child nodes
        parent: Reference to parent node (optional)
    """
    
    def __init__(self, data: FileItem, parent: Optional['Node'] = None):
        """Initialize a tree node.
        
        Args:
            data: FileItem containing node data
            parent: Optional parent node reference
        """
        self.data = data
        self.children: List['Node'] = []
        self.parent = parent
    
    def add_child(self, child: 'Node') -> None:
        """Add a child node to this node.
        
        Args:
            child: Child node to add
        """
        self.children.append(child)
        child.parent = self
    
    def remove_child(self, child: 'Node') -> bool:
        """Remove a child node from this node.
        
        Args:
            child: Child node to remove
            
        Returns:
            True if child was removed, False if not found
        """
        try:
            self.children.remove(child)
            child.parent = None
            return True
        except ValueError:
            return False
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (has no children).
        
        Returns:
            True if leaf node, False otherwise
        """
        return len(self.children) == 0
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root node (has no parent).
        
        Returns:
            True if root node, False otherwise
        """
        return self.parent is None
    
    @property
    def degree(self) -> int:
        """Get the degree of this node (number of children).
        
        Returns:
            Number of children
        """
        return len(self.children)
    
    @property
    def height(self) -> int:
        """Calculate the height of the subtree rooted at this node.
        
        Returns:
            Height of subtree
        """
        if self.is_leaf:
            return 0
        return 1 + max(child.height for child in self.children)
    
    @property
    def depth(self) -> int:
        """Calculate the depth of this node in the tree.
        
        Returns:
            Depth from root (root = 0)
        """
        if self.is_root:
            return 0
        return 1 + self.parent.depth
    
    def get_path_components(self) -> List[str]:
        """Get the path from root to this node.
        
        Returns:
            List of FileItems from root to this node
        """
        path = []
        current = self
        while current is not None:
            path.append(current.data.name)
            current = current.parent
        return list(reversed(path))
    
    def get_full_path(self) -> Path:
        """Get the full filesystem path for this node.
        
        Args:
            base_dir: Base directory to prepend
            
        Returns:
            Full Path object
        """
        components = self.get_path_components()
        return Path(*components)
    
    def __str__(self) -> str:
        """String representation of the node.
        
        Returns:
            Filename of the node
        """
        return str(self.data.name)
    
    def __repr__(self) -> str:
        """Detailed string representation.
        
        Returns:
            Detailed node information
        """
        return f"Node(data={self.data.name}, level={self.data.level}, children={len(self.children)})"