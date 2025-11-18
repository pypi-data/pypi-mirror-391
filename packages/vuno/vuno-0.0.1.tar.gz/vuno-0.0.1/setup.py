"""
Setup configuration for vuno-python.
"""

from setuptools import setup, find_packages
import os

# Read version from package
version = {}
with open(os.path.join("vuno", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vuno",
    version=version.get('__version__', '0.0.1'),
    author="zaqar",
    author_email="hakobyanzaqar3@gmail.com",
    description="A terminal text editor written in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vuno",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Editors",
    ],
    python_requires=">=3.7",
    install_requires=[
        "prompt_toolkit>=3.0.36",
    ],
    entry_points={
        "console_scripts": [
            "vuno=vuno:main",
        ],
    },
)