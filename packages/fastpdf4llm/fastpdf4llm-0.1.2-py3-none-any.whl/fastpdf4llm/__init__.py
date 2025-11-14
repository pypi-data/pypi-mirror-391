from typing import Callable, Optional

from fastpdf4llm.convert.doc import convert_doc
from fastpdf4llm.models.parse_options import ParseOptions
from fastpdf4llm.models.progress import ProgressInfo


def to_markdown(
    pdf_path: str,
    image_dir: Optional[str] = None,
    parse_options: Optional[ParseOptions] = None,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
) -> str:
    return convert_doc(pdf_path, image_dir, parse_options, progress_callback)
