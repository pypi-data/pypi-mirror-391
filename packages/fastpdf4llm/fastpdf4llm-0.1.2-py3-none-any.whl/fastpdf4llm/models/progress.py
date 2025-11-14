from enum import Enum

from pydantic import BaseModel


class ProcessPhase(Enum):
    ANALYSIS = "analysis"
    CONVERSION = "conversion"


class ProgressInfo(BaseModel):
    """Progress information for PDF processing."""

    phase: ProcessPhase
    current_page: int
    total_pages: int
    percentage: float
    message: str


def create_progress_info(phase: ProcessPhase, current_page: int, total_pages: int, message: str) -> ProgressInfo:
    """Create a ProgressInfo object with calculated percentage."""
    if phase == ProcessPhase.ANALYSIS:
        # Analysis phase goes from 0% to 70%
        total_percentage = (current_page / total_pages) * 70
    else:
        # Conversion phase goes from 70% to 100%
        # Start at 70% and progress through remaining 30%
        total_percentage = 70 + ((current_page / total_pages) * 30)

    return ProgressInfo(
        phase=phase, current_page=current_page, total_pages=total_pages, percentage=total_percentage, message=message
    )
