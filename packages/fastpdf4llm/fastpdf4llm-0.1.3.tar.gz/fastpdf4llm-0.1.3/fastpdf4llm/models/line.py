from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from fastpdf4llm.models.constants import MAX_WIDTH_GAP_SIZE
from fastpdf4llm.models.parse_options import ParseOptions


class LineType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"


class Line(BaseModel):
    words: List[Dict[str, Any]]
    left: float
    right: float
    top: float
    bottom: float
    level: Optional[str] = None
    type: LineType = LineType.TEXT

    def should_merge(self, left: float, right: float, top: float, bottom: float, parse_options: ParseOptions) -> bool:
        # 同一行
        if abs(self.top - top) > parse_options.y_tolerance:
            return False

        return True

    def merge(self, word: Dict[str, Any]):
        self.left = min(self.left, word["x0"])
        self.right = max(self.right, word["x1"])
        self.top = min(self.top, word["top"])
        self.bottom = max(self.bottom, word["bottom"])

        if not self.words:
            self.words = [word]
        else:
            # 距离接近且字体相同，直接合并
            if word["x0"] - self.words[-1]["x1"] < MAX_WIDTH_GAP_SIZE:
                self.words[-1]["top"] = min(self.words[-1]["top"], word["top"])
                self.words[-1]["bottom"] = max(self.words[-1]["bottom"], word["bottom"])
                self.words[-1]["x0"] = min(self.words[-1]["x0"], word["x0"])
                self.words[-1]["x1"] = max(self.words[-1]["x1"], word["x1"])
                self.words[-1]["text"] += "++" + word["text"]
            else:
                self.words.append(word)

    def split(self, page_width: float) -> List["Line"]:
        if len(self.words) >= 4 or len(self.words) <= 1 or self.right - self.left < page_width * 0.4:
            return [self]

        # 如果最后一个字符的x坐标小于页面宽度的一半，则不拆分
        if self.words[-1]["x0"] < page_width * 0.5:
            return [self]

        # 2 列或者3列的情况，拆分
        return [
            Line(
                words=[word],
                left=word["x0"],
                right=word["x1"],
                top=word["top"],
                bottom=word["bottom"],
                level=self.level,
                type=self.type,
            )
            for word in self.words
        ]
