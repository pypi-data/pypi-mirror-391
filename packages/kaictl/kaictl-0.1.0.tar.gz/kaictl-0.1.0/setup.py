#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="kaictl",
    version="0.1.0",
    description="Kubernetes Natural Language Agent - Translate natural language to kubectl commands",
    author="KaiCTL Contributors",
    url="https://github.com/yourusername/kaictl",
    license="MIT",
    py_modules=["kaictl"],
    entry_points={
        "console_scripts": [
            "kaictl=kaictl:main",
        ],
    },
    install_requires=[
        "requests>=2.28.0",
        "anthropic>=0.7.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
    ],
)
