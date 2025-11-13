"""Backend rendering engines for PyAndroid.

This module provides different rendering backends for PyAndroid applications.
Currently supports: Kivy (optional)
"""

try:
    from .kivy_backend import KivyRenderer
    __all__ = ['KivyRenderer']
except ImportError:
    # Kivy not available - this is okay for console-only mode
    KivyRenderer = None
    __all__ = []
