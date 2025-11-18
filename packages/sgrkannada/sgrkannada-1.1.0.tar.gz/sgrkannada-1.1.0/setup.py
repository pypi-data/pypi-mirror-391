from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Import and call the download function from the package
        try:
            from sgrkannada import clone_repository
            clone_repository()
        except Exception as e:
            print(f"Note: Files will be downloaded when you first import sgrkannada: {e}")

setup(
    name="sgrkannada",
    version="1.1.0",
    description="Install package that downloads the ML repository from sgrkannada/ML",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/sgrkannada/ML",
    py_modules=[],
    packages=find_packages(),
    install_requires=[
        "setuptools",
        "requests",
        "gdown",
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    python_requires=">=3.6",
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
    ],
)

