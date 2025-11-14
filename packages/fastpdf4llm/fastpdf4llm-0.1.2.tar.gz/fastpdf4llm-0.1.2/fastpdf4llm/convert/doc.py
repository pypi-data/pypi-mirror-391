from typing import Callable, Counter, Optional, Tuple

import pdfplumber
from loguru import logger

from fastpdf4llm.convert.page import PageConverter
from fastpdf4llm.models.parse_options import ParseOptions
from fastpdf4llm.models.progress import ProcessPhase, ProgressInfo, create_progress_info
from fastpdf4llm.utils.font import FontSizeClassifier, round_font_size


def report_progress(
    progress_info: ProgressInfo, progress_callback: Optional[Callable[[ProgressInfo], None]] = None
) -> None:
    """Report progress through the callback if it exists."""
    if progress_callback:
        progress_callback(progress_info)


def collect_statistics(
    pdf: pdfplumber.PDF,
    parse_options: ParseOptions,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
) -> Tuple[Counter, Counter]:
    """Collect font statistics from PDF with progress tracking."""
    total_pages = len(pdf.pages)
    font_size_text_count = Counter()

    for i, page in enumerate(pdf.pages):
        progress_info = create_progress_info(
            phase=ProcessPhase.ANALYSIS, current_page=i + 1, total_pages=total_pages, message="Analyzing"
        )
        report_progress(progress_info, progress_callback)

        tables = page.find_tables()
        non_table_content = page

        for table in tables:
            try:
                if (
                    table.bbox[0] >= 0
                    and table.bbox[1] >= 0
                    and table.bbox[2] <= page.bbox[2]
                    and table.bbox[3] <= page.bbox[3]
                ):
                    non_table_content = non_table_content.outside_bbox(table.bbox)
            except ValueError:
                continue

        # dedupe chars to avoid duplicate characters https://github.com/langchain-ai/langchain/pull/10165/files
        words = non_table_content.dedupe_chars().extract_words(
            extra_attrs=["size"], x_tolerance=parse_options.x_tolerance, y_tolerance=parse_options.y_tolerance
        )
        for word in words:
            word_size = round_font_size(word["size"])
            font_size_text_count[word_size] += len(word["text"])

    return font_size_text_count


def convert_doc(
    pdf_path: str,
    image_dir: Optional[str] = None,
    parse_options: Optional[ParseOptions] = None,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
) -> str:
    parse_options = parse_options or ParseOptions()
    md_content = ""
    with pdfplumber.open(pdf_path, unicode_norm="NFKD") as pdf:
        initial_progress = create_progress_info(
            phase=ProcessPhase.ANALYSIS, current_page=0, total_pages=len(pdf.pages), message="Starting PDF analysis"
        )
        report_progress(initial_progress, progress_callback)

        # Analyze font statistics
        font_size_text_count = collect_statistics(pdf, parse_options)
        if not font_size_text_count:
            logger.warning("No text found in the PDF.")
            return md_content
        classifier = FontSizeClassifier(font_size_text_count)

        # Report analysis completion
        analysis_complete = create_progress_info(
            phase=ProcessPhase.CONVERSION,
            current_page=0,
            total_pages=len(pdf.pages),
            message="Analysis complete, beginning content extraction",
        )
        report_progress(analysis_complete, progress_callback)

        total_pages = len(pdf.pages)

        for i, page in enumerate(pdf.pages, 1):
            progress_info = create_progress_info(
                phase=ProcessPhase.CONVERSION,
                current_page=i,
                total_pages=total_pages,
                message="Converting content to Markdown",
            )
            report_progress(progress_info, progress_callback)

            converter = PageConverter(
                page=page,
                parse_options=parse_options,
                size_to_level=classifier.size_to_level,
                normal_text_size=classifier.normal_text_size,
                image_dir=image_dir,
            )
            md_content += converter.to_markdown()
    return md_content
