"""
pyobfus Pro Edition - Commercial Features

This module contains proprietary features for pyobfus Professional Edition.
Not included in the open-source Community Edition.

License: Proprietary - Commercial Use Only
Copyright 2025 Rong Zhu
"""

__version__ = "0.1.0"
__license__ = "Proprietary"

from .string_aes import StringAESEncryptor
from .anti_debug import AntiDebugInjector

__all__ = ["StringAESEncryptor", "AntiDebugInjector"]
