"""
Decompilation module for converting .lfcalc files to Python code.

This module provides functionality to read a Leapfrog calculation set (.lfcalc file)
and generate Python code that would recreate the same calculation set using pollywog.

Phase 1: Direct conversion - generates Python code that exactly recreates the structure
without attempting to detect patterns or optimize the code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from .core import CalcSet, If, IfRow, Item


def _escape_string(s: str) -> str:
    """
    Escape a string for use in Python code.

    Args:
        s: String to escape

    Returns:
        Escaped string suitable for use in Python source code
    """
    # Escape backslashes and quotes
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    return s


def _format_expression_element(elem: Any, indent: int = 0) -> str:
    """
    Format a single expression element (string, If, IfRow) as Python code.

    Args:
        elem: Expression element to format
        indent: Current indentation level (spaces)

    Returns:
        Python code string representing the element
    """
    ind = " " * indent

    if isinstance(elem, str):
        return f'"{_escape_string(elem)}"'

    elif isinstance(elem, If):
        # Generate If(...) structure
        lines = ["If(["]

        # Format each row
        for row in elem.rows:
            if isinstance(row, IfRow):
                # Ensure condition and value are lists (handle legacy string case)
                from .utils import ensure_list

                condition = ensure_list(row.condition)
                value = ensure_list(row.value)

                # Format condition - if single string, output as string; otherwise as list
                if len(condition) == 1 and isinstance(condition[0], str):
                    cond_str = _format_expression_element(condition[0])
                else:
                    cond_parts = [_format_expression_element(c) for c in condition]
                    cond_str = "[" + ", ".join(cond_parts) + "]"

                # Format value - if single string, output as string; otherwise as list
                if len(value) == 1 and isinstance(value[0], str):
                    val_str = _format_expression_element(value[0])
                else:
                    val_parts = [_format_expression_element(v) for v in value]
                    val_str = "[" + ", ".join(val_parts) + "]"

                lines.append(f"{ind}    ({cond_str}, {val_str}),")
            else:
                # Shouldn't happen but handle gracefully
                lines.append(f"{ind}    {repr(row)},")

        # Format otherwise
        if elem.otherwise:
            otherwise_parts = [_format_expression_element(o) for o in elem.otherwise]
            otherwise_str = "[" + ", ".join(otherwise_parts) + "]"
            lines.append(f"{ind}], otherwise={otherwise_str})")
        else:
            lines.append(f"{ind}])")

        return "\n".join(lines)

    elif isinstance(elem, IfRow):
        # Shouldn't be used directly, but handle it
        return f"IfRow({elem.condition}, {elem.value})"

    else:
        # Fallback for unknown types
        return repr(elem)


def _format_expression(expression: list[Any], indent: int = 0) -> str:
    """
    Format an expression list as Python code.

    Args:
        expression: List of expression elements
        indent: Current indentation level (spaces)

    Returns:
        Python code string - either a single string or a list
    """
    # Filter out empty strings from expression
    expression = [e for e in expression if e != ""]

    if not expression:
        return '""'

    # If single string expression, return it directly
    if len(expression) == 1 and isinstance(expression[0], str):
        return f'"{_escape_string(expression[0])}"'

    # Multiple elements or contains If objects - return as list
    if len(expression) == 1 and isinstance(expression[0], If):
        # Single If - can be wrapped in list
        return "[" + _format_expression_element(expression[0], indent) + "]"

    # Multiple elements
    parts = [_format_expression_element(elem, indent) for elem in expression]

    # If all strings and fits on one line, format inline
    if all(isinstance(e, str) for e in expression):
        inline = "[" + ", ".join(parts) + "]"
        if len(inline) < 80:
            return inline

    # Multi-line format for complex expressions
    ind = " " * indent
    lines = ["["]
    for part in parts:
        if "\n" in part:
            # Multi-line element (like If)
            lines.append(f"{ind}    {part},")
        else:
            lines.append(f"{ind}    {part},")
    lines.append(f"{ind}]")
    return "\n".join(lines)


def _format_item(item: Item, indent: int = 4, detect_patterns: bool = True) -> str:
    """
    Format a single Item as Python code.

    Args:
        item: Item to format (Number, Category, Variable, Filter)
        indent: Current indentation level (spaces)
        detect_patterns: Whether to attempt pattern detection (default: True)

    Returns:
        Python code string creating the item
    """
    from .patterns import detect_pattern

    ind = " " * indent

    # Try pattern detection for Number items with single expression
    if (
        detect_patterns
        and type(item).__name__ == "Number"
        and len(item.expression) == 1
        and isinstance(item.expression[0], str)
    ):
        pattern_match = detect_pattern(item.expression[0])

        if pattern_match:
            # Generate helper function call
            helper_call = pattern_match.helper_code

            # Add name and comments
            params = [f'name="{_escape_string(item.name)}"']

            if item.comment_equation:
                params.append(f'comment="{_escape_string(item.comment_equation)}"')

            if item.comment_item:
                params.append(f'comment_item="{_escape_string(item.comment_item)}"')

            # Insert params into helper call (before closing paren)
            if params:
                params_str = ", " + ", ".join(params)
                helper_call = helper_call.rstrip(")") + params_str + ")"

            return helper_call

    # Fall back to direct expression formatting
    # Determine class name
    class_name = type(item).__name__

    # Format expression
    expr_str = _format_expression(item.expression, indent + 4)

    # Build parameter list
    params = [f'"{_escape_string(item.name)}"']

    # Add expression if not empty
    if item.expression:
        if "\n" in expr_str:
            # Multi-line expression
            params.append(f"\n{ind}    {expr_str}")
        else:
            params.append(expr_str)

    # Add comments if present
    if item.comment_equation:
        params.append(f'comment_equation="{_escape_string(item.comment_equation)}"')

    if item.comment_item:
        params.append(f'comment_item="{_escape_string(item.comment_item)}"')

    # Format the item
    if any("\n" in p for p in params):
        # Multi-line format
        return (
            f"{class_name}(\n{ind}    "
            + f",\n{ind}    ".join(p.strip() for p in params)
            + f"\n{ind})"
        )
    else:
        # Single line format
        return f"{class_name}(" + ", ".join(params) + ")"


def decompile_to_string(calcset: CalcSet) -> str:
    """
    Convert a CalcSet to Python code that would recreate it.

    Args:
        calcset: CalcSet instance to decompile

    Returns:
        Python source code as a string
    """
    lines = []

    # Header comment
    lines.append('"""')
    lines.append("Generated by pollywog.decomp")
    lines.append("")
    lines.append("This code recreates a Leapfrog calculation set (.lfcalc file)")
    lines.append("using pollywog. You can modify this code and re-run it to")
    lines.append("generate an updated .lfcalc file.")
    lines.append('"""')
    lines.append("")

    # Imports
    lines.append(
        "from pollywog.core import CalcSet, Category, Filter, If, Number, Variable"
    )
    lines.append("from pollywog.helpers import Average, Product, Sum, WeightedAverage")
    lines.append("")
    lines.append("")

    # CalcSet definition
    lines.append("calcset = CalcSet([")

    # Add each item
    for item in calcset.items:
        item_code = _format_item(item, indent=4)
        lines.append(f"    {item_code},")

    lines.append("])")
    lines.append("")
    lines.append("")

    # Footer - show how to export
    lines.append("# Export to .lfcalc file:")
    lines.append('# calcset.to_lfcalc("output.lfcalc")')

    return "\n".join(lines) + "\n"


def decompile(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    Decompile a .lfcalc file to Python code.

    Args:
        input_path: Path to the .lfcalc file to decompile
        output_path: Optional path to write the generated Python code.
                    If None, returns the code as a string without writing.

    Returns:
        Generated Python code as a string

    Example:
        >>> from pollywog.decomp import decompile
        >>>
        >>> # Generate Python code from .lfcalc
        >>> code = decompile("my_calcs.lfcalc", "my_calcs.py")
        >>>
        >>> # Or just get the code without writing
        >>> code = decompile("my_calcs.lfcalc")
        >>> print(code)
    """
    # Read the calcset
    calcset = CalcSet.read_lfcalc(input_path)

    # Generate Python code
    code = decompile_to_string(calcset)

    # Write to file if requested
    if output_path is not None:
        output_path = Path(output_path)
        output_path.write_text(code, encoding="utf-8")

    return code
