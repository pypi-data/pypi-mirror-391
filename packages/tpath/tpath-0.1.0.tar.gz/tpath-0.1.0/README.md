# TPath - Enhanced pathlib with Age and Size Utilities

TPath is a pathlib extension that provides first-class age and size functions for file operations using a lambda-based approach (instead of operator overloading like pathql). It allows you to get file ages and sizes in natural, expressive syntax.

## Installation

### Using uv (Recommended)
```bash
# Install directly from source
uv add git+https://github.com/yourusername/tpath.git

# Or for development
git clone https://github.com/yourusername/tpath.git
cd tpath
uv sync --dev
```

### Using pip
```bash
# Install from PyPI (when published)
pip install tpath

# Or install from source
pip install git+https://github.com/yourusername/tpath.git
```

## Quick Start

```python
from tpath import TPath

# Basic usage - works like pathlib.Path
path = TPath("my_file.txt")

# Age functionality
print(f"File is {path.age.days} days old")
print(f"File is {path.age.hours} hours old")
print(f"Modified {path.mtime.age.minutes} minutes ago")

# Size functionality  
print(f"File size: {path.size.mb} MB")
print(f"File size: {path.size.gib} GiB")

# Size parsing from strings
large_size = TPath.size.fromstr("1.5GB")
if path.size.bytes > large_size:
    print("This is a large file!")
```

## Key Features

- **Lambda-based design**: No operator overloading confusion
- **Full pathlib compatibility**: Drop-in replacement for pathlib.Path
- **Natural syntax**: path.age.days instead of path.age > days(7)
- **Comprehensive time units**: seconds, minutes, hours, days, weeks, months, years
- **Multiple size units**: bytes, KB/KiB, MB/MiB, GB/GiB, TB/TiB
- **String parsing**: Parse size strings like "1.5GB", "500MB"
- **Different time types**: Handle ctime, mtime, atime separately

## Development

This project uses uv for dependency management and packaging. See UV_GUIDE.md for detailed instructions.

```bash
# Install development dependencies
uv sync --dev

# Run tests  
uv run python -m pytest

# Build package
uv build

# Format code
uv run ruff format

# Lint code
uv run ruff check
```

## License

MIT License - see LICENSE file for details.
