"""
fastuv - 快速 uv 安装器，预配置国内镜像源

通过 PyPI 分发的 uv 安装器，自动配置国内镜像，实现用户级别安装。
"""

__version__ = "0.1.0"
__author__ = "whillhill"
__email__ = "ooooofish@126.com"

from .cli import main

__all__ = ["main"]