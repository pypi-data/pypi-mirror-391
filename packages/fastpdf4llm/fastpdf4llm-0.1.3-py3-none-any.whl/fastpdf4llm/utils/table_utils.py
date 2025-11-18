from typing import Optional

from pdfplumber.table import Table


def sanitize_cell(cell: Optional[str]) -> str:
    """Clean up table cell content."""
    if cell is None:
        return ""
    return " ".join(str(cell).split())


def is_table_empty(table: Table) -> bool:
    """
    Checks if the table is empty.

    An empty table is defined as:
    1. Having no cells
    2. All cells are empty (None, empty string, or whitespace)
    3. Table data (extracted content) is empty
    """
    try:
        # Check if table has no cells
        if not table.cells:
            return True

        def is_cell_empty(cell) -> bool:
            """
            Checks if a single cell is empty.

            - None is considered empty
            - Numeric types (int, float) are considered non-empty
            - For dictionaries, the 'text' key's stripped value determines emptiness
            - Strings are empty if stripped value is empty
            - Other types are evaluated by converting to string and stripping
            """
            if cell is None:
                return True

            if isinstance(cell, (int, float)):
                return False  # Numbers are always considered non-empty

            if isinstance(cell, dict):
                return not cell.get("text", "").strip()

            if isinstance(cell, str):
                return not cell.strip()

            try:
                return not str(cell).strip()
            except Exception:
                return True

        # Extract table data and check if it's empty
        table_data = table.extract()
        if not table_data:
            return True

        # Check if all rows are empty
        if all(not any(row) for row in table_data):
            return True

        # Check the actual content of cells
        return all(is_cell_empty(cell) for row in table_data for cell in row)

    except Exception:
        return False  # Default to considering the table non-empty in case of error


def table_to_markdown(table: Table, header: str = "###") -> str:
    """Convert a table to Markdown format."""
    unsanitized_table = table.extract()
    sanitized_table = [[sanitize_cell(cell) for cell in row] for row in unsanitized_table]

    if not sanitized_table:
        return ""

    markdown_lines = []

    # if sanitized_table[0] and sanitized_table[0][0].strip():
    #    markdown_lines.extend([f"{header}", ""])

    # Create table structure
    markdown_lines.extend(
        ["| " + " | ".join(sanitized_table[0]) + " |", "|" + "|".join(":---:" for _ in sanitized_table[0]) + "|"]
    )

    # Add data rows
    markdown_lines.extend("| " + " | ".join(row) + " |" for row in sanitized_table[1:])

    return "\n".join(markdown_lines) + "\n\n"
