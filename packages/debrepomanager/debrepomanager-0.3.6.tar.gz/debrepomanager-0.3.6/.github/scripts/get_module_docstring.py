#!/usr/bin/env python3
"""Helper script to extract the first line of a Python module's docstring."""

import ast
import sys


def get_first_line_docstring(filepath):
    """Extract the first line of the module docstring.

    Args:
        filepath: Path to the Python file

    Returns:
        First line of docstring or empty string if not found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            docstring = ast.get_docstring(tree)
            if docstring:
                return docstring.split('\n')[0]
    except Exception:
        pass
    return ""


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    result = get_first_line_docstring(sys.argv[1])
    print(result)
