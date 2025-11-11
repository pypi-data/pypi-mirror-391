"""
Serverless Devs - Python 安装包
通过 pip 安装 Serverless Devs 官方工具（自动安装最新版本）
"""

__version__ = "1.0.2"
__author__ = "Serverless Devs"
__url__ = "https://www.serverless-devs.com/"

from .installer import install_serverless_devs

__all__ = ['install_serverless_devs']
