from pydantic import BaseModel


class ParseOptions(BaseModel):
    x_tolerance: float = 3  # pdfplumber's x_tolerance, used to control spacing between words
    y_tolerance: float = 3  # pdfplumber's y_tolerance, used to control spacing between lines
