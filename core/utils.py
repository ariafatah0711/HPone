"""
Utility Functions untuk HPone

Fungsi-fungsi utility yang dibutuhkan oleh core modules.
"""

import re
from typing import List


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
    
    # Build data rows
    data_rows = []
    for row in rows:
        row_str = "|"
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            cell_str = str(cell)
            # Truncate if too long
            if len(cell_str) > width:
                cell_str = "..." + cell_str[-(width-3):]
            row_str += f" {cell_str:<{width}} |"
        data_rows.append(row_str)
    
    # Combine all parts
    table = separator + "\n"
    table += header_row + "\n"
    table += separator + "\n"
    table += "\n".join(data_rows) + "\n"
    table += separator
    
    return table
