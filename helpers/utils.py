"""
Utility Functions untuk HPone

Fungsi-fungsi utility yang digunakan di berbagai tempat.
"""

import re
from typing import List


def to_var_prefix(tool_name: str) -> str:
    """Konversi nama tool menjadi prefix ENV uppercase yang aman: cowrie -> COWRIE."""
    upper = tool_name.strip().upper()
    return re.sub(r"[^A-Z0-9]+", "_", upper).strip("_")


def _format_table(headers: List[str], rows: List[List[str]], max_width: int = 30) -> str:
    # Hitung lebar maksimal untuk setiap kolom
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)
            # Truncate cell yang terlalu panjang
            if len(cell_str) > max_width:
                cell_str = cell_str[:max_width-3] + "..."
            if len(cell_str) > widths[i]:
                widths[i] = len(cell_str)
    
    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    out_lines: List[str] = []
    out_lines.append(sep)
    header_line = "|" + "|".join([" " + headers[i].ljust(widths[i]) + " " for i in range(len(headers))]) + "|"
    out_lines.append(header_line)
    out_lines.append(sep)
    
    for row in rows:
        line_parts = []
        for i, cell in enumerate(row):
            cell_str = str(cell)
            # Truncate cell yang terlalu panjang
            if len(cell_str) > max_width:
                cell_str = cell_str[:max_width-3] + "..."
            line_parts.append(" " + cell_str.ljust(widths[i]) + " ")
        line = "|" + "|".join(line_parts) + "|"
        out_lines.append(line)
    
    out_lines.append(sep)
    return "\n".join(out_lines)
