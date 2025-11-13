#!/usr/bin/env python3
"""
Velora - Simple file sharing and chat over TCP sockets
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Velora - Simple file sharing and chat over TCP sockets"

setup(
    name="velora-chat",
    version="1.0.1",
    description="Simple file sharing and chat over TCP sockets",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Pavan Sai Tanguturi",
    author_email="pavansai.tanguturi@gmail.com",
    url="https://github.com/pavansai-tanguturi/Velora",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    entry_points={
        "console_scripts": [
            "velora=velora.cli:main",
            "velora-chat=velora.cli:chat_main",
            "velora-share=velora.cli:share_main",
            "velora-server=velora.cli:server_main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="chat file-sharing tcp sockets networking p2p",
    project_urls={
        "Bug Reports": "https://github.com/pavansai-tanguturi/Velora/issues",
        "Source": "https://github.com/pavansai-tanguturi/Velora",
        "Documentation": "https://github.com/pavansai-tanguturi/Velora#readme",
    },
)
