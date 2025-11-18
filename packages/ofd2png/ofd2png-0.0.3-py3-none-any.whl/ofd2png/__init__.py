"""ofd2png package public API

对外导出：OFDToPNG, convert_file, convert_folder
"""
from .converter import OFDToPNG, convert_file, convert_folder
import os

__all__ = ["OFDToPNG", "convert_file", "convert_folder", "__version__"]

__version__ = "0.0.3"
