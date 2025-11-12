"""tree2fs - Convert tree-formatted text into filesystem structures.

This library provides tools to parse tree-formatted text files and create
corresponding directory structures on the filesystem.

Basic usage:
    >>> from tree2fs import TreeParser, FilesystemBuilder
    >>> from pathlib import Path
    >>> 
    >>> parser = TreeParser()
    >>> root, _ = parser.build_tree(Path("tree.txt"))
    >>> 
    >>> builder = FilesystemBuilder(Path("."))
    >>> builder.build(root)
"""

from .__version__ import (
    __version__,
    __author__,
    __email__,
    __license__,
    __description__
)

from .models import FileItem, Node
from .parser import TreeParser
from .builder import FilesystemBuilder
from .exceptions import Tree2FSError, TreeParseError, FilesystemBuildError

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__description__',
    # Main classes
    'FileItem',
    'Node',
    'TreeParser',
    'FilesystemBuilder',
    # Exceptions
    'Tree2FSError',
    'TreeParseError',
    'FilesystemBuildError',
]


def create_from_tree(
    tree_file: str,
    base_dir: str = ".",
    dry_run: bool = False,
    verbose: bool = False,
    skip_root: bool = True
) -> dict:
    """Convenience function to create filesystem from tree file.
    
    Args:
        tree_file: Path to tree file
        base_dir: Base directory to create structure in
        dry_run: If True, don't actually create files
        verbose: If True, print detailed output
        skip_root: If True, skip creating root directory
        
    Returns:
        Dictionary with creation statistics
        
    Example:
        >>> from tree2fs import create_from_tree
        >>> stats = create_from_tree("my_tree.txt", verbose=True)
        >>> print(f"Created {stats['total']} items")
    """
    from pathlib import Path
    
    parser = TreeParser()
    root, root_name = parser.build_tree(Path(tree_file), skip_root=skip_root)
    
    # Check if we should skip root
    base_path = Path(base_dir)
    should_skip = False
    if skip_root and root_name and base_path.name == root_name:
        should_skip = True
    
    builder = FilesystemBuilder(base_path, dry_run=dry_run, verbose=verbose)
    builder.build(root, skip_root=should_skip)
    
    return builder.get_summary()