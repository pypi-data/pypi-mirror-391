import hashlib
import os
import re
from io import BytesIO
from typing import Dict, List, Optional

from loguru import logger
from pdfplumber.page import Page
from pdfplumber.table import Table

from fastpdf4llm.models.constants import DEFAULT_IMAGE_SAVE_DIR
from fastpdf4llm.models.content import Content, sort_content
from fastpdf4llm.models.line import Line, LineType
from fastpdf4llm.models.parse_options import ParseOptions
from fastpdf4llm.utils.font import is_bold_font, round_font_size
from fastpdf4llm.utils.number_utils import is_hierarchical_number
from fastpdf4llm.utils.table_utils import is_table_empty, table_to_markdown


def is_english(text):
    # 正则匹配：仅允许英文字母(a-z, A-Z)、数字(0-9)、常见标点和空格
    pattern = r"^[a-zA-Z0-9\s.,!?\'\"()\-:;]+$"
    return bool(re.fullmatch(pattern, text))


class PageConverter:
    def __init__(
        self,
        page: Page,
        parse_options: ParseOptions,
        size_to_level: Dict[float, str],
        normal_text_size: float,
        extract_images: bool = True,
        image_dir: Optional[str] = None,
    ):
        self.page = page
        self.size_to_level = size_to_level
        self.normal_text_size = normal_text_size
        self.extract_images = extract_images
        self.image_dir = image_dir or DEFAULT_IMAGE_SAVE_DIR
        self.text_content_area = self.page
        self.parse_options = parse_options
        if self.extract_images:
            os.makedirs(self.image_dir, exist_ok=True)

    def _is_valid_table(self, table: Table) -> bool:
        """Check if table bounds are within page bounds."""
        page_bbox = self.page.bbox
        table_bbox = table.bbox

        return (
            table_bbox[0] >= 0
            and table_bbox[1] >= 0
            and table_bbox[2] <= page_bbox[2]
            and table_bbox[3] <= page_bbox[3]
        )

    def extract_contents(self) -> List[Content]:
        contents: List[Content] = []
        tables = self.page.dedupe_chars().find_tables()
        valid_tables = [table for table in tables if self._is_valid_table(table)]

        media_contents = []
        # Extract non-table content
        for table in valid_tables:
            if is_table_empty(table):
                continue

            try:
                self.text_content_area = self.text_content_area.outside_bbox(table.bbox)
            except ValueError:
                logger.warning(f"Table {table.bbox} is not within the text content area.")
                continue

            word = {
                "text": table_to_markdown(table),
                "x0": table.bbox[0],
                "x1": table.bbox[2],
                "top": table.bbox[1],
                "bottom": table.bbox[3],
                "fontname": "",
                "size": self.normal_text_size,
            }
            logger.info(f"Table to markdown: {word['text']}")

            media_contents.append(
                Content(
                    lines=[
                        Line(
                            words=[word],
                            left=table.bbox[0],
                            right=table.bbox[2],
                            top=table.bbox[1],
                            bottom=table.bbox[3],
                            type=LineType.TABLE,
                        )
                    ],
                    left=table.bbox[0],
                    right=table.bbox[2],
                    top=table.bbox[1],
                    bottom=table.bbox[3],
                )
            )

        if self.extract_images:
            for image in self.page.images:
                image_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])

                try:
                    # 按照固定尺寸剪切出来，直接使用“stream”的bytes会加载报错 https://github.com/jsvine/pdfplumber/discussions/496
                    image_page = self.page.crop(image_bbox)
                    img_obj = image_page.to_image(width=image["width"])
                    image_bytes_io = BytesIO()
                    img_obj.save(image_bytes_io, format="PNG")
                    image_bytes = image_bytes_io.getvalue()

                    # 写入文件
                    image_md5 = hashlib.md5(image_bytes).hexdigest()
                    image_path = os.path.join(self.image_dir, f"{image_md5}.png")
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                        logger.info(f"Save image to {image_path} successfully.")

                    word = {
                        "text": f"![]({image_path})\n\n",
                        "x0": image["x0"],
                        "x1": image["x1"],
                        "top": image["top"],
                        "bottom": image["bottom"],
                        "fontname": "",
                        "size": self.normal_text_size,
                    }

                    media_contents.append(
                        Content(
                            lines=[
                                Line(
                                    words=[word],
                                    left=image["x0"],
                                    right=image["x1"],
                                    top=image["top"],
                                    bottom=image["bottom"],
                                    type=LineType.IMAGE,
                                )
                            ],
                            left=image["x0"],
                            right=image["x1"],
                            top=image["top"],
                            bottom=image["bottom"],
                        )
                    )

                except Exception as ex:
                    logger.warning(f"Parse image failed: {ex}")
                    continue

                try:
                    self.text_content_area = self.text_content_area.outside_bbox(image_bbox)
                except ValueError as ex:
                    logger.warning(f"Image is not within the text content area. {ex}")
                    continue

        # Process text content with font information
        cur_line = None
        page_width = self.page.width
        for word in self.text_content_area.dedupe_chars().extract_words(extra_attrs=["size", "fontname"]):
            if cur_line and cur_line.should_merge(
                word["x0"], word["x1"], word["top"], word["bottom"], self.parse_options
            ):
                cur_line.merge(word)
            else:
                if cur_line:
                    for sub_line in cur_line.split(page_width=page_width):
                        if contents and contents[-1].should_add(sub_line):
                            contents[-1].add_line(sub_line)
                        else:
                            contents.append(
                                Content(
                                    lines=[sub_line],
                                    left=sub_line.left,
                                    right=sub_line.right,
                                    top=sub_line.top,
                                    bottom=sub_line.bottom,
                                )
                            )

                rounded_size = round_font_size(word["size"])
                level = "" if rounded_size == self.normal_text_size else self.size_to_level.get(rounded_size, "")

                cur_line = Line(
                    words=[word],
                    left=word["x0"],
                    right=word["x1"],
                    top=word["top"],
                    bottom=word["bottom"],
                    level=level,
                    type=LineType.TEXT,
                )

        if cur_line:
            for sub_line in cur_line.split(page_width=page_width):
                if contents and contents[-1].should_add(sub_line):
                    contents[-1].add_line(sub_line)
                else:
                    contents.append(
                        Content(
                            lines=[sub_line],
                            left=sub_line.left,
                            right=sub_line.right,
                            top=sub_line.top,
                            bottom=sub_line.bottom,
                        )
                    )

        contents.extend(media_contents)
        contents = sort_content(contents)
        final_contents = []
        visited = [False] * len(contents)
        for i in range(len(contents)):
            if visited[i]:
                continue

            content = contents[i]
            new_merged = True
            while new_merged:
                new_merged = False
                for j in range(i + 1, len(contents)):
                    if visited[j]:
                        continue
                    if content.should_merge(contents[j], self.parse_options):
                        content.merge(contents[j], self.parse_options)
                        visited[j] = True
                        new_merged = True

            final_contents.append(content)
            visited[i] = True

        final_contents = sort_content(final_contents)

        return final_contents

    def should_break_line(self, text: str) -> bool:
        if re.search(r"[:：.?!。？！….]\s*$", text) and not re.search(r"\d\.$", text):
            return True

        return False

    # Process text with mixed styles
    def to_markdown(self) -> str:
        contents = self.extract_contents()

        md_content = ""
        for content in contents:
            content_markdown = ""
            max_line_end = -1
            last_line_level = ""
            last_line_bottom = 0
            for line in content.lines:
                max_line_end = max(max_line_end, line.right)
            for line in content.lines:
                line_bold = False

                if line.type == LineType.TEXT:
                    if not line.words:
                        continue

                    non_bold_width = 0
                    bold_width = 0
                    for word in line.words:
                        if is_bold_font(word["fontname"]):
                            bold_width += word["x1"] - word["x0"]
                        else:
                            non_bold_width += word["x1"] - word["x0"]

                    line_bold = bold_width > non_bold_width

                    try:
                        current_bbox = (line.left, line.top, line.right, line.bottom)
                        span_text = (
                            self.text_content_area.within_bbox(current_bbox)
                            .dedupe_chars()
                            .extract_text(
                                x_tolerance=self.parse_options.x_tolerance, y_tolerance=self.parse_options.y_tolerance
                            )
                            .strip()
                        )
                    except Exception:
                        logger.warning(f"Failed to find span {current_bbox}.")
                        continue

                    # 序号开头，直接添加换行
                    line_is_hierarchical = is_hierarchical_number(span_text)
                    if line_is_hierarchical and not content_markdown.endswith("\n\n"):
                        content_markdown = content_markdown.rstrip("\n") + "\n\n"

                    line_markdown = f"**{span_text}**" if line_bold else span_text

                    if line_bold or line.right < max_line_end * 0.9 or line.level:
                        should_break_line = True
                    else:
                        should_break_line = self.should_break_line(span_text)

                    if should_break_line:
                        line_markdown += "\n\n"

                    if line.level:
                        if (
                            last_line_level == line.level
                            and line.top > last_line_bottom
                            and line.top - last_line_bottom < 0.5 * (line.bottom - line.top)
                        ):
                            content_markdown = content_markdown.rstrip("\n")
                            if is_english(line_markdown):
                                line_markdown = " " + line_markdown
                        else:
                            line_markdown = f"{line.level} {line_markdown}"
                else:
                    line_markdown = "\n" + line.words[0]["text"]

                last_line_level = line.level
                last_line_bottom = line.bottom

                if line_markdown:
                    content_markdown += line_markdown

            if content_markdown:
                if content_markdown.endswith("\n\n"):
                    md_content += content_markdown
                elif content_markdown.endswith("\n"):
                    md_content += content_markdown + "\n"
                else:
                    md_content += content_markdown + "\n\n"

        return md_content
