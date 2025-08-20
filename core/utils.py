"""
Utility Functions untuk HPone

Fungsi-fungsi utility yang dibutuhkan oleh core modules.
"""

import re
from typing import List
import textwrap


def to_var_prefix(name: str) -> str:
    """Convert tool name to environment variable prefix."""
    # Replace non-alphanumeric chars with underscore, convert to uppercase
    prefix = re.sub(r'[^a-zA-Z0-9]', '_', name).upper()
    # Ensure it starts with a letter
    if prefix and not prefix[0].isalpha():
        prefix = 'TOOL_' + prefix
    return prefix


def _format_table(headers: List[str], rows: List[List[str]], max_width: int = 50) -> str:
    """
    Format data sebagai ASCII table dengan truncation.
    
    Args:
        headers: List header columns
        rows: List of rows (each row is list of strings)
        max_width: Maximum width untuk truncation
        
    Returns:
        Formatted table string
    """
    if not headers or not rows:
        return ""
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        # Start with header width
        max_width_col = len(header)
        # Check all rows for this column
        for row in rows:
            if i < len(row):
                max_width_col = max(max_width_col, len(str(row[i])))
        # Apply max_width limit
        max_width_col = min(max_width_col, max_width)
        col_widths.append(max_width_col)
    
    # Build separator line
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    # Build header row
    header_row = "|"
    for header, width in zip(headers, col_widths):
        header_row += f" {header:<{width}} |"
    
    # Build data rows with word-wrapping per cell
    data_rows = []
    for row in rows:
        # Prepare wrapped lines for each cell in the row
        wrapped_per_cell = []
        max_lines = 1
        for i in range(len(headers)):
            cell_value = str(row[i]) if i < len(row) else ""
            width = col_widths[i]
            # Wrap by words; ensure at least one empty line when value is empty
            wrapped_lines = textwrap.wrap(cell_value, width=width) if cell_value else [""]
            if not wrapped_lines:
                wrapped_lines = [""]
            wrapped_per_cell.append(wrapped_lines)
            if len(wrapped_lines) > max_lines:
                max_lines = len(wrapped_lines)

        # Emit visual lines for this logical row
        for line_idx in range(max_lines):
            line_str = "|"
            for i, width in enumerate(col_widths):
                lines = wrapped_per_cell[i]
                part = lines[line_idx] if line_idx < len(lines) else ""
                line_str += f" {part:<{width}} |"
            data_rows.append(line_str)
    
    # Combine all parts
    table = separator + "\n"
    table += header_row + "\n"
    table += separator + "\n"
    table += "\n".join(data_rows) + "\n"
    table += separator
    
    return table
