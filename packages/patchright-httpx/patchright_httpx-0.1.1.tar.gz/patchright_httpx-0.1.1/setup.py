"""
setup.py - Patchright HTTPX 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="patchright-httpx",
    version="0.1.0",
    author="Color_Fox",
    author_email="",
    description="一个使用 Patchright 封装的类 HTTPX 风格的 HTTP 请求库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Color_Fox/patchright-httpx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "patchright>=1.0.0",
    ],
    keywords="http httpx requests browser playwright patchright automation",
)


