# sgrkannada

A Python package that automatically downloads the ML repository from [sgrkannada/ML](https://github.com/sgrkannada/ML) when installed.

## Installation

```bash
pip install sgrkannada
```

After installation, the repository will be cloned to your home directory in a folder named `ML`. **All files download as-is (not as a zip file)** - you'll get the exact same file structure as the GitHub repository.

## Requirements

- Python 3.6+
- Git (must be installed and available in PATH)

## How it works

When you run `pip install sgrkannada`, the package will:
1. Install the package itself
2. Automatically clone the `sgrkannada/ML` repository to your home directory

## Usage

After installation, you can access the cloned repository in the `ML` folder in your home directory.

**Download locations:**
- Windows: `C:\Users\<YourUsername>\ML`
- Linux/Mac: `~/ML`

**Note:** All files are downloaded as-is (not compressed). You'll get the exact same files and folder structure from the GitHub repository.

```python
import sgrkannada
repo_path = sgrkannada.get_repo_path()
print(f"Repository cloned to: {repo_path}")
```

## Development

To install in development mode:

```bash
pip install -e .
```

## License

MIT License

