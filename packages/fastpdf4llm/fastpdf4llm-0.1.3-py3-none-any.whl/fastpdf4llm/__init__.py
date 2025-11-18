import pathlib
from io import BufferedReader, BytesIO
from typing import Callable, Optional, Union

from fastpdf4llm.convert.doc import convert_doc
from fastpdf4llm.models.parse_options import ParseOptions
from fastpdf4llm.models.progress import ProgressInfo


def to_markdown(
    path_or_fp: Union[str, pathlib.Path, BufferedReader, BytesIO],
    extract_images: bool = True,
    image_dir: Optional[str] = None,
    parse_options: Optional[ParseOptions] = None,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
) -> str:
    return convert_doc(path_or_fp, extract_images, image_dir, parse_options, progress_callback)
