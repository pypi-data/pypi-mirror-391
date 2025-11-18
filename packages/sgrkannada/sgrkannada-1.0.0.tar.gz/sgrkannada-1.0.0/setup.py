from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        self.clone_repository()

    def clone_repository(self):
        """Clone the GitHub repository to home directory."""
        repo_url = "https://github.com/sgrkannada/ML.git"
        
        # Always use home directory
        home_dir = os.path.expanduser("~")
        target_dir = os.path.join(home_dir, "ML")
        
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: git is not installed. Please install git to clone the repository.")
            print(f"Alternatively, you can manually download from: {repo_url}")
            return
        
        # Clone the repository if it doesn't exist
        if not os.path.exists(target_dir):
            print(f"Cloning repository {repo_url} to {target_dir}...")
            try:
                # Get the parent directory for cloning
                parent_dir = os.path.dirname(target_dir)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                
                subprocess.run(
                    ["git", "clone", repo_url, target_dir],
                    check=True,
                    cwd=parent_dir
                )
                print(f"Successfully cloned repository to {target_dir}")
            except subprocess.CalledProcessError as e:
                print(f"Error cloning repository: {e}")
                print(f"Please manually clone from: {repo_url}")
        else:
            print(f"Directory {target_dir} already exists. Skipping clone.")
            print("If you want to update, please delete the directory and reinstall.")

setup(
    name="sgrkannada",
    version="1.0.0",
    description="Install package that downloads the ML repository from sgrkannada/ML",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/sgrkannada/ML",
    py_modules=[],
    packages=find_packages(),
    install_requires=[
        "setuptools",
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

