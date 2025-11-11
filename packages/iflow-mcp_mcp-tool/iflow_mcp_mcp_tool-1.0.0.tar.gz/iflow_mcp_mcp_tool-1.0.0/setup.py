'''
Author: Mr.Car
Date: 2025-03-21 14:41:56
'''
from setuptools import setup, find_packages

setup(
    name="weather-server",
    version="1.0.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "fastmcp>=0.4.1,<0.5.0",
        "httpx>=0.28.1,<0.29.0",
        "python-dotenv>=1.0.1,<2.0.0",
        "pinyin>=0.4.0,<0.5.0",
    ],
    python_requires=">=3.12.0",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: MIT License",
    ],
    author="Mr.Car",
    author_email="534192336car@gmail.com",
    description="一个基于 FastMCP 的天气查询服务",
    long_description=open("readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="weather, mcp, fastmcp, api",
    project_urls={
        "Source": "https://github.com/yourusername/weather-server",
        "Bug Reports": "https://github.com/yourusername/weather-server/issues",
    },
) 