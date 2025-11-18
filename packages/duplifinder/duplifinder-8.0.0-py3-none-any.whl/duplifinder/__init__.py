"""Duplifinder: Detect duplicate Python definitions across projects."""

from .__version__ import __version__

# Lazy attribute loading to avoid import errors during build
def __getattr__(name):
    if name == "Config":
        from .config import Config
        return Config
    if name == "EnhancedDefinitionVisitor":
        from .ast_visitor import EnhancedDefinitionVisitor
        return EnhancedDefinitionVisitor
    if name == "main":
        from . import main
        return main
    raise AttributeError(name)

__all__ = ["__version__", "Config", "EnhancedDefinitionVisitor", "main"]