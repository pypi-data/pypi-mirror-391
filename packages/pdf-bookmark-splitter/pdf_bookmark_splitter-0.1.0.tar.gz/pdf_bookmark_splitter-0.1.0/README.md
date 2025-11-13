# PDF Bookmark Splitter

A Python utility that splits a PDF file into multiple files based on its bookmarks.

## Features

- Splits PDF files using existing bookmarks
- Creates separate PDF files for each bookmark
- Maintains original PDF quality
- Preserves bookmark hierarchy

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- PyPDF (automatically installed with package)

## Installation

### Using uv (Recommended)

This project uses `uv` for dependency management. First, install uv:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then clone and set up the project:

```bash
git clone https://github.com/leejss/pdf-bookmark-splitter.git
cd pdf-bookmark-splitter
uv sync
```

### Using pip (Alternative)

You can also install with pip:

```bash
pip install git+https://github.com/leejss/pdf-bookmark-splitter.git
```

## Usage

### With uv

```bash
uv run pdf-split input.pdf --output-dir chapters
```

### With pip installation

```bash
pdf-split input.pdf --output-dir chapters
```

### Options

- `--output-dir`: Directory to save split PDF files (default: `chapters`)

### Example

```bash
# Split PDF and save to 'output' directory
uv run pdf-split book.pdf --output-dir output
```

This will create separate PDF files in the specified directory, named according to the top-level bookmarks in the input PDF.
