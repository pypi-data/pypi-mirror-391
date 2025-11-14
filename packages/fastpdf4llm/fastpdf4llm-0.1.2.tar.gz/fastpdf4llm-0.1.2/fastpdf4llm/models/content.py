from typing import List

from pydantic import BaseModel

from fastpdf4llm.models.constants import MAX_HEIGHT_GAP_SIZE, MAX_WIDTH_GAP_SIZE
from fastpdf4llm.models.line import Line, LineType
from fastpdf4llm.models.parse_options import ParseOptions

"""
Content 表示一个内容块，包含一个或多个行，行之间可能存在间隙，行之间可能存在合并
"""


class Content(BaseModel):
    lines: List[Line]
    left: float
    right: float
    top: float
    bottom: float

    def __str__(self):
        text = "====\n".join(["-".join([word["text"] for word in line.words]) for line in self.lines])
        return f"Content Block {self.left} - {self.right} - {self.top} - {self.bottom}:\n{text}\n===============\n\n"

    def __lt__(self, other: "Content"):
        return self.top < other.top

    def add_line(self, line: Line):
        self.lines.append(line)
        self.left = min(self.left, line.left)
        self.right = max(self.right, line.right)
        self.top = min(self.top, line.top)
        self.bottom = max(self.bottom, line.bottom)

    def should_add(self, line: Line) -> bool:
        if line.top > self.bottom and line.top - self.bottom > MAX_HEIGHT_GAP_SIZE:
            return False

        if line.left > self.right and line.left - self.right > MAX_WIDTH_GAP_SIZE:
            return False

        if line.right < self.left and self.left - line.right > MAX_WIDTH_GAP_SIZE:
            return False

        if line.bottom < self.top and self.top - line.bottom > MAX_HEIGHT_GAP_SIZE:
            return False

        return True

    def should_merge(self, other: "Content", parse_options: ParseOptions) -> bool:
        if self.lines[0].type != other.lines[0].type and self.lines[0].type != LineType.TEXT:
            return False

        # 特殊情况，同一行合并
        if (
            abs(self.top - other.top) < parse_options.y_tolerance
            and len(self.lines) <= 1
            and len(other.lines) <= 1
            and self.lines[0].type == other.lines[0].type
            and self.lines[0].type == LineType.TEXT
        ):
            return True

        if self.top > other.bottom and self.top - other.bottom > MAX_HEIGHT_GAP_SIZE:
            return False

        if self.bottom < other.top and other.top - self.bottom > MAX_HEIGHT_GAP_SIZE:
            return False

        if self.left > other.right and self.left - other.right > MAX_WIDTH_GAP_SIZE:
            return False

        if self.right < other.left and other.left - self.right > MAX_WIDTH_GAP_SIZE:
            return False

        return True

    def merge(self, other: "Content", parse_options: ParseOptions):
        if (
            abs(self.top - other.top) < 3
            and len(self.lines) <= 1
            and len(other.lines) <= 1
            and self.lines[0].type == other.lines[0].type
            and self.lines[0].type == LineType.TEXT
        ):
            for word in other.lines[0].words:
                if self.lines[0].should_merge(word["x0"], word["x1"], word["top"], word["bottom"], parse_options):
                    self.lines[0].merge(word)
                else:
                    self.lines[0].words.append(word)
        else:
            self.lines.extend(other.lines)
        self.left = min(self.left, other.left)
        self.right = max(self.right, other.right)
        self.top = min(self.top, other.top)
        self.bottom = max(self.bottom, other.bottom)


def sort_content(contents: List[Content]) -> List[Content]:
    # 按从上到下冒泡排序
    contents = sorted(contents)
    for i in range(len(contents)):
        for j in range(i - 1, 0, -1):
            if contents[j].left > contents[i].right and contents[j].left - contents[i].right > MAX_WIDTH_GAP_SIZE:
                contents[i], contents[j] = contents[j], contents[i]
            else:
                # 找个每一个block的前序block即停止
                break

    return contents
