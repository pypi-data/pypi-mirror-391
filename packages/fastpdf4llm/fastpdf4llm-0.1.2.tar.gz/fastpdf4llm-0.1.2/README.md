# 🚀 fastpdf4llm: PDF to LLM-Ready Markdown in Seconds


[![CI](https://github.com/moria97/fastpdf4llm/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/moria97/fastpdf4llm/actions/workflows/ci.yml)


A fast and efficient PDF to Markdown converter optimized for LLM (Large Language Model) processing. This tool intelligently extracts text, tables, and images from PDF files and converts them into well-structured Markdown format.

## Features

- 🚀 **Fast Processing**: Efficient PDF parsing and conversion
- 📊 **Table Extraction**: Automatically detects and converts tables to Markdown format
- 🖼️ **Image Support**: Extracts and saves images from PDFs
- 📝 **Smart Formatting**: Intelligently identifies headings based on font sizes
- 📈 **Progress Tracking**: Built-in progress callback support
- 🎯 **LLM Optimized**: Output format optimized for LLM consumption
- 📜 **Free & Open Source**: MIT licensed, free to use for commercial and personal projects


## Examples

See the `examples/` directory for more usage examples:

- `financial_report_cn/`: Converting financial reports with tables and images
  - [Example output: 平安财报2016.md](https://github.com/moria97/fastpdf4llm/blob/main/examples/financial_report_cn/平安财报2016.md)
- `table_data/`: Converting PDFs with complex tables
  - [Example output: national-capitals.md](https://github.com/moria97/fastpdf4llm/blob/main/examples/table_data/national-capitals.md)
- `car_user_manual/`: Converting car user manuals with extensive images and structured content
  - [Example output: tesla_model3_user_manual.pdf.md](https://github.com/moria97/fastpdf4llm/blob/main/examples/car_user_manual/tesla_model3_user_manual.pdf.md)


## Installation

### Using Poetry (Recommended)

```bash
poetry add fastpdf4llm
```

### Using pip

```bash
pip install fastpdf4llm
```

## Quick Start

### Basic Usage

```python
from fastpdf4llm import to_markdown

# Convert PDF to Markdown
markdown_content = to_markdown("path/to/your/document.pdf")

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)
```

### With Custom Image Directory

```python
from fastpdf4llm import to_markdown

# Specify custom directory for extracted images
markdown_content = to_markdown(
    "path/to/your/document.pdf",
    image_dir="./images"
)
```

### With Progress Callback

```python
from fastpdf4llm import to_markdown, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"{progress.phase.value}: {progress.current_page}/{progress.total_pages} "
          f"({progress.percentage:.1f}%) - {progress.message}")

markdown_content = to_markdown(
    "path/to/your/document.pdf",
    progress_callback=progress_callback
)
```

### With Custom Parse Options

```python
from fastpdf4llm import to_markdown
from fastpdf4llm.models.parse_options import ParseOptions

# Customize parsing options for better text extraction
parse_options = ParseOptions(
    x_tolerance=3,  # Control spacing between words (default: 3)
    y_tolerance=3   # Control spacing between lines (default: 3)
)

markdown_content = to_markdown(
    "path/to/your/document.pdf",
    parse_options=parse_options
)
```

### Combined Usage

```python
from fastpdf4llm import to_markdown, ProgressInfo
from fastpdf4llm.models.parse_options import ParseOptions

def progress_callback(progress: ProgressInfo):
    print(f"Progress: {progress.percentage:.1f}%")

parse_options = ParseOptions(x_tolerance=5, y_tolerance=5)

markdown_content = to_markdown(
    "path/to/your/document.pdf",
    image_dir="./images",
    parse_options=parse_options,
    progress_callback=progress_callback
)
```

## API Reference

### `to_markdown`

Convert a PDF file to Markdown format.

**Parameters:**

- `pdf_path` (str): Path to the PDF file to convert
- `image_dir` (Optional[str]): Directory to save extracted images. Defaults to `./tmp/images/`
- `parse_options` (Optional[ParseOptions]): Parsing options to control text extraction. Defaults to `ParseOptions(x_tolerance=3, y_tolerance=3)`
- `progress_callback` (Optional[Callable[[ProgressInfo], None]]): Callback function for progress updates

**Returns:**

- `str`: Markdown content of the PDF

**Example:**

```python
from fastpdf4llm import to_markdown, ProgressInfo
from typing import Callable

def on_progress(progress: ProgressInfo):
    print(f"Progress: {progress.percentage:.1f}%")

content = to_markdown(
    pdf_path="document.pdf",
    image_dir="./output_images",
    progress_callback=on_progress
)
```

### `ParseOptions`

Parsing options to customize PDF text extraction behavior.

**Attributes:**

- `x_tolerance` (float): Controls spacing tolerance between words horizontally. Default: `3`
  - Lower values: More strict word separation (better for well-formatted PDFs)
  - Higher values: More lenient word grouping (better for PDFs with irregular spacing)
- `y_tolerance` (float): Controls spacing tolerance between lines vertically. Default: `3`
  - Lower values: More strict line separation
  - Higher values: More lenient line grouping

**Example:**

```python
from fastpdf4llm.models.parse_options import ParseOptions

# For PDFs with tight spacing
tight_options = ParseOptions(x_tolerance=1, y_tolerance=1)

# For PDFs with loose spacing
loose_options = ParseOptions(x_tolerance=5, y_tolerance=5)

markdown_content = to_markdown("document.pdf", parse_options=tight_options)
```

### `ProgressInfo`

Progress information model for tracking conversion progress.

**Attributes:**

- `phase` (ProcessPhase): Current processing phase (`ANALYSIS` or `CONVERSION`)
- `current_page` (int): Current page being processed
- `total_pages` (int): Total number of pages in the PDF
- `percentage` (float): Overall progress percentage (0-100)
- `message` (str): Status message

## How It Works

1. **Analysis Phase**: Analyzes the PDF to identify font sizes and determine heading hierarchy
2. **Conversion Phase**: Extracts text, tables, and images, converting them to Markdown format
3. **Smart Formatting**: Automatically detects headings based on font size analysis
4. **Table Detection**: Identifies and converts tables to Markdown table format
5. **Image Extraction**: Extracts images and saves them to the specified directory
6. **Configurable Parsing**: Adjustable tolerance settings for optimal text extraction from various PDF layouts


## Requirements

- Python >= 3.9
- pdfplumber >= 0.11.3
- loguru >= 0.7.0
- pydantic >= 2.0.0

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/moria97/fastpdf4llm.git
cd fastpdf4llm

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
# Format code
poetry run ruff format .

# Lint code
poetry run ruff check .
```

## Acknowledgements

This project is inspired by the [pdf2markdown4llm](https://github.com/HawkClaws/pdf2markdown4llm/tree/main) project by HawkClaws. We appreciate their work on PDF to Markdown conversion for LLM applications.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Yue Fei - [feiyue297@qq.com](mailto:feiyue297@qq.com)

## Repository

[https://github.com/moria97/fastpdf4llm](https://github.com/moria97/fastpdf4llm)

