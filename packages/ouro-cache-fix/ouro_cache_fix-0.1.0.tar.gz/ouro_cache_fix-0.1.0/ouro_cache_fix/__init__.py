"""
Ouro Cache Fix
==============

Custom cache implementation for ByteDance/Ouro-1.4B models.

Fixes the KV cache bug that causes IndexError when using use_cache=True
with Universal Transformer architecture.

Example:
    >>> from ouro_cache_fix import UniversalTransformerCache
    >>> cache = UniversalTransformerCache()
    >>> outputs = model.generate(..., past_key_values=cache, use_cache=True)
"""

from importlib.metadata import version, PackageNotFoundError

from .universal_transformer_cache import UniversalTransformerCache, load_ouro_with_custom_cache

try:
    __version__ = version("ouro-cache-fix")
except PackageNotFoundError:
    # Package not installed, fallback for development
    __version__ = "0.0.0.dev"

__author__ = "Edwin Villacis"
__all__ = ["UniversalTransformerCache", "load_ouro_with_custom_cache"]
