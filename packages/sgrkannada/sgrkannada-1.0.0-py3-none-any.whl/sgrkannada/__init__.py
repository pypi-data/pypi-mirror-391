"""
sgrkannada - A package that downloads the ML repository from sgrkannada/ML
"""

__version__ = "1.0.0"
__author__ = "Your Name"

def get_repo_path():
    """Get the path to the cloned ML repository."""
    import os
    home_dir = os.path.expanduser("~")
    repo_path = os.path.join(home_dir, "ML")
    return repo_path

