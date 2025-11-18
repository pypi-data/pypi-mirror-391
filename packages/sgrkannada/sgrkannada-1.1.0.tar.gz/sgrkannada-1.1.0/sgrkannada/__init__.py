"""
sgrkannada - A package that downloads the ML repository from sgrkannada/ML
"""

__version__ = "1.1.0"
__author__ = "Your Name"

import os
import subprocess
import shutil
import sys

# Google Drive folder ID
GOOGLE_DRIVE_FOLDER_ID = "1cp1_CI3of4K3cQL_E-bxrXubPJMf2696"
GOOGLE_DRIVE_FOLDER_URL = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"

# File mapping: Google Drive file IDs (we'll use gdown to download by folder)
FILES_TO_DOWNLOAD = [
    "california_housing.csv",
    "heart.csv",
    "insurance.csv",
    "Program 1.ipynb",
    "Program 2.ipynb",
    "Program 3.ipynb"
]

def download_from_google_drive(target_dir, overwrite=True):
    """Download files from Google Drive folder."""
    try:
        import gdown
    except ImportError:
        print("Installing gdown library...")
        import subprocess as sp
        sp.check_call([sys.executable, "-m", "pip", "install", "gdown", "-q"])
        import gdown
    
    print(f"Downloading files from Google Drive to {target_dir}...")
    
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    elif overwrite:
        # Remove existing directory to overwrite
        shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)
    
    # Download entire folder using gdown
    try:
        # gdown can download entire folders - use the folder URL
        folder_url = f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}?usp=sharing"
        gdown.download_folder(folder_url, output=target_dir, quiet=False, use_cookies=False)
        print(f"Successfully downloaded files to {target_dir}")
        return True
    except Exception as e:
        print(f"Error downloading from Google Drive with gdown: {e}")
        print("Trying alternative method...")
        # Alternative: Try downloading folder as zip
        return download_files_individually(target_dir, overwrite)

def download_files_individually(target_dir, overwrite=True):
    """Download files individually from Google Drive using folder zip download."""
    try:
        import requests
        import zipfile
        import tempfile
    except ImportError:
        print("Installing required libraries...")
        import subprocess as sp
        sp.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        import requests
        import zipfile
        import tempfile
    
    print("Attempting to download folder as zip from Google Drive...")
    
    # Google Drive folder zip download URL
    zip_url = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FOLDER_ID}"
    
    try:
        # Download the folder as zip
        session = requests.Session()
        response = session.get(zip_url, stream=True, allow_redirects=True)
        
        if response.status_code == 200:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            # Extract zip to target directory
            with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # Clean up temp file
            os.remove(tmp_file_path)
            print(f"Successfully downloaded and extracted files to {target_dir}")
            return True
        else:
            print(f"Failed to download: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Alternative download method failed: {e}")
        print(f"Please manually download from: {GOOGLE_DRIVE_FOLDER_URL}")
        return False

def clone_repository():
    """Clone from GitHub or download from Google Drive to both Downloads and home directory."""
    repo_url = "https://github.com/sgrkannada/ML.git"
    home_dir = os.path.expanduser("~")
    
    # Target directories: both Downloads and home directory
    downloads_dir = os.path.join(home_dir, "Downloads")
    target_dirs = []
    
    if os.path.exists(downloads_dir):
        target_dirs.append(os.path.join(downloads_dir, "ML"))
    target_dirs.append(os.path.join(home_dir, "ML"))
    
    git_available = False
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True, timeout=5)
        git_available = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("Git is not installed. Will download from Google Drive instead.")
    
    success = False
    
    # Try GitHub first if git is available
    if git_available:
        for target_dir in target_dirs:
            try:
                # Remove existing directory to overwrite
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                
                print(f"Cloning repository {repo_url} to {target_dir}...")
                parent_dir = os.path.dirname(target_dir)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
                
                subprocess.run(
                    ["git", "clone", repo_url, target_dir],
                    check=True,
                    cwd=parent_dir,
                    timeout=300
                )
                print(f"Successfully cloned repository to {target_dir}")
                success = True
            except Exception as e:
                print(f"Error cloning to {target_dir}: {e}")
    
    # If git failed or not available, use Google Drive
    if not success:
        print("Downloading from Google Drive...")
        for target_dir in target_dirs:
            try:
                download_from_google_drive(target_dir, overwrite=True)
                success = True
            except Exception as e:
                print(f"Error downloading to {target_dir}: {e}")
    
    return target_dirs[0] if target_dirs else os.path.join(home_dir, "ML")

def get_repo_path():
    """Get the path to the downloaded ML repository (prefers Downloads, then home)."""
    home_dir = os.path.expanduser("~")
    downloads_dir = os.path.join(home_dir, "Downloads", "ML")
    home_ml_dir = os.path.join(home_dir, "ML")
    
    # Return Downloads if it exists, otherwise home directory
    if os.path.exists(downloads_dir):
        return downloads_dir
    return home_ml_dir

# Automatically download repository when package is imported
try:
    clone_repository()
except Exception as e:
    print(f"Warning: Could not download repository automatically: {e}")
    print(f"You can manually download from: {GOOGLE_DRIVE_FOLDER_URL}")

