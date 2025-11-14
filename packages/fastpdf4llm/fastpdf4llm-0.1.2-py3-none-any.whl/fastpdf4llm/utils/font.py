from collections import Counter
from typing import Dict, List, Optional, Tuple

from loguru import logger


def round_font_size(size: float) -> float:
    """Round font size to one decimal place."""
    return round(size, 1)


def get_fontname(fontname: Optional[str]) -> Optional[str]:
    if not fontname:
        return None

    plus_index = fontname.find("+")
    if plus_index == -1:
        return fontname

    return fontname[plus_index + 1 :]


def is_same_font(fontname1: Optional[str], fontname2: Optional[str]) -> bool:
    if not fontname1 or not fontname2:
        return False

    fname1 = get_fontname(fontname1)
    fname2 = get_fontname(fontname2)
    return fname1.lower() == fname2.lower()


def is_bold_font(fontname: Optional[str]) -> bool:
    """
    Determine if a font is bold based on its name.
    Uses stricter rules to prevent over-detection of bold text.
    """
    if not fontname:
        return False

    # Convert font name to lowercase for comparison
    fontname_lower = fontname.lower()

    # Common bold font name patterns
    bold_indicators = {
        "bold",  # Most common indicator
        "-bold",  # Often used with hyphen
        ".bold",  # Sometimes used with dot
        " bold",  # Used with space
    }

    # Exclude certain terms that might contain 'bold' but aren't necessarily bold
    exclude_terms = {
        "semibold",  # Usually lighter than true bold
        "demibold",  # Usually lighter than true bold
        "book",  # Regular weight
        "light",  # Light weight
        "regular",  # Regular weight
    }

    # First check if any exclusion terms are in the font name
    if any(term in fontname_lower for term in exclude_terms):
        return False

    # Then check for bold indicators
    return any(indicator in fontname_lower for indicator in bold_indicators)


class FontSizeClassifier:
    def __init__(self, font_size_counts: Counter):
        # Round font sizes when initializing
        # Create new Counter with rounded font sizes
        rounded_counts = Counter()
        for size, count in font_size_counts.items():
            rounded_counts[round_font_size(size)] += count
        self.font_size_counts = rounded_counts
        self.size_to_level: Dict[float, str] = {}
        self.normal_text_size: float = 0

        self._classify()

    def _calculate_size_ratios(self, larger_sizes: List[float]) -> Tuple[float, float]:
        """Calculate average ratio and standard deviation between consecutive font sizes."""
        if not larger_sizes:
            return 0, 0

        size_ratios = [larger_sizes[i] / larger_sizes[i + 1] for i in range(len(larger_sizes) - 1)]

        if not size_ratios:
            return larger_sizes[0], 0

        avg_ratio = sum(size_ratios) / len(size_ratios)
        ratio_std = (sum((r - avg_ratio) ** 2 for r in size_ratios) / len(size_ratios)) ** 0.5

        return avg_ratio, ratio_std

    def _classify(self) -> None:
        """Classify font sizes into heading levels."""
        if not self.font_size_counts:
            return

        unique_sizes = sorted(self.font_size_counts.keys(), reverse=True)
        if len(unique_sizes) <= 1:
            logger.warning(f"Only one size found, using it as normal text size: {unique_sizes[0]}.")
            self.normal_text_size = unique_sizes[0]
            return

        normal_text_candidate = self.font_size_counts.most_common(1)[0][0]
        normal_text_weight = self.font_size_counts[normal_text_candidate]
        for size, weight in self.font_size_counts.items():
            if (
                size > normal_text_candidate
                and weight >= normal_text_weight * 0.4
                and size < normal_text_candidate * 1.6
            ):
                normal_text_candidate = size

        self.normal_text_size = normal_text_candidate
        larger_sizes = [size for size in unique_sizes if size > self.normal_text_size]

        if not larger_sizes:
            logger.warning(f"No larger sizes found, using normal text size {self.normal_text_size}.")
            return

        avg_ratio, ratio_std = self._calculate_size_ratios(larger_sizes)
        if avg_ratio == 0:
            logger.warning(f"Average ratio is 0 for {larger_sizes}, using normal text size {self.normal_text_size}.")
            return

        min_diff_ratio = max(1.02, min(1.15, avg_ratio - ratio_std))

        # Identify headers
        heading_sizes = []
        current_size = max(larger_sizes)
        heading_sizes.append(current_size)

        for size in larger_sizes[1:]:
            ratio = current_size / size
            if ratio >= min_diff_ratio:
                heading_sizes.append(size)
                current_size = size
                if len(heading_sizes) >= 6:
                    break

        # Map sizes to markdown header levels
        levels = ["#", "##", "###", "####", "#####", "######"]
        self.size_to_level = dict(zip(heading_sizes, levels))
        last_heading = "#"
        for size in larger_sizes[1:]:
            if size not in self.size_to_level:
                self.size_to_level[size] = last_heading

            last_heading = self.size_to_level[size]
        logger.info(f"Normal text size: {self.normal_text_size}")
        logger.info(f"Heading sizes to markdown header levels mapping: {self.size_to_level}")
