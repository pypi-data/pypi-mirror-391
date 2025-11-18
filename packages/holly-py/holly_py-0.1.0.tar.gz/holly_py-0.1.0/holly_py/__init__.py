"""
Holly-Py Package
一个简单的示例 Python 包，用于演示如何创建和发布 Python 包
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import greet, HelloWorld

__all__ = ["greet", "HelloWorld", "__version__"]

