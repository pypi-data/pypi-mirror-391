"""Custom exceptions for tree2fs library."""


class Tree2FSError(Exception):
    """Base exception for tree2fs library."""
    pass


class TreeParseError(Tree2FSError):
    """Exception raised when parsing tree file fails."""
    pass


class FilesystemBuildError(Tree2FSError):
    """Exception raised when building filesystem fails."""
    pass