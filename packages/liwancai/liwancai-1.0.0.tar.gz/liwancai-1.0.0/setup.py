# -*- coding: utf-8 -*-
"""
liwancai包的安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README内容作为long_description
long_description = """
liwancai的个人工具包

这个包包含了数据分析、日志处理、数据库连接等常用功能模块。

主要模块包括：
- EQDBLinks: 数据库连接相关功能
- EQStructure: 数据结构定义
- EQUseApi: API调用封装
- Functions: 通用工具函数
- MainBase: 基础类
- THSFuncs: 同花顺相关功能
"""

# 定义依赖项
install_requires = [
    "numpy>=1.16.0",
    "pandas>=0.24.0",
    "logbook>=1.5.3",
    "requests>=2.22.0",
    "tqdm>=4.32.0",
    "prettytable>=0.7.2",
    "toml>=0.10.0",
    "pymysql>=1.0.0",
    "sshtunnel>=0.4.0"
]

setup(
    name="liwancai",
    version="1.0.0",
    description="liwancai的个人工具包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liwancai",
    author_email="liwancai@example.com",
    url="https://github.com/liwancai/liwancai",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    python_requires=">=3.6",
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    keywords="tools utilities data-analysis logging database"
)