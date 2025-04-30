# CPTK - CSV Process Tool Kit (CSV处理工具包)

__version__ = '0.1.0'

from .splitter import CSVSplitterConverter
from .cli import main

__all__ = ['CSVSplitterConverter', 'main']