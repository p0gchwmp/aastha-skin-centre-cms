"""Aastha website application package.

The extension import swaps the conservative first-release stream classes for
subclasses that retain every existing block and add the advanced no-code block
library. It runs before ``home.models`` constructs its StreamField instances.
"""

from . import blocks as _blocks
from .editor_extensions import (
    ExtendedPageAdditionStreamBlock,
    ExtendedPageBodyStreamBlock,
)

_blocks.PageBodyStreamBlock = ExtendedPageBodyStreamBlock
_blocks.PageAdditionStreamBlock = ExtendedPageAdditionStreamBlock

__all__ = [
    "ExtendedPageAdditionStreamBlock",
    "ExtendedPageBodyStreamBlock",
]
