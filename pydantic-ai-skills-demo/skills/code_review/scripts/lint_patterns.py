"""
Simple pattern-based code analysis utilities.

This module provides basic static analysis helpers for detecting common
code quality issues. It is intended for demonstration purposes and is
NOT a replacement for proper linting tools like ruff, flake8, or pylint.

Usage:
    from skills.code_review.scripts.lint_patterns import (
        check_magic_numbers,
        check_deep_nesting,
        check_long_functions,
        analyze_file,
    )

    issues = analyze_file("path/to/code.py")
    for issue in issues:
        print(f"Line {issue['line']}: {issue['message']}")
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


def check_magic_numbers(code: str) -> List[Dict[str, any]]:
    """
    Check for magic numbers in code.

    Magic numbers are numeric literals that appear without explanation.
    Common exceptions like 0, 1, -1, 100 (percentages) are allowed.

    Args:
        code: Source code string to analyze

    Returns:
        List of issues found, each with 'line', 'column', 'message', 'severity'
    """
    issues: List[Dict[str, any]] = []

    # Numbers that are commonly acceptable
    allowed_numbers = {
        "0", "1", "2", "-1", "0.0", "1.0", "0.5",
        "100", "1000", "10",  # Common bases/percentages
        "60", "24", "365",  # Time-related
        "256", "255", "1024",  # Computing-related
    }

    # Pattern for numeric literals (excluding those in strings or comments)
    number_pattern = re.compile(r'\b(\d+\.?\d*)\b')

    lines = code.split('\n')
    for line_num, line in enumerate(lines, start=1):
        # Skip comments
        if line.strip().startswith('#'):
            continue

        # Skip lines that are likely constant definitions
        if re.match(r'^\s*[A-Z_]+\s*=', line):
            continue

        # Find numbers in the line
        for match in number_pattern.finditer(line):
            number = match.group(1)

            # Skip allowed numbers
            if number in allowed_numbers:
                continue

            # Skip if it looks like an index or simple arithmetic
            context = line[max(0, match.start() - 5):match.end() + 5]
            if re.search(r'[\[\]:]', context):
                continue

            issues.append({
                'line': line_num,
                'column': match.start() + 1,
                'message': f"Magic number '{number}' - consider using a named constant",
                'severity': 'warning',
                'rule': 'magic-number',
            })

    return issues


def check_deep_nesting(code: str, max_depth: int = 4) -> List[Dict[str, any]]:
    """
    Check for deeply nested code blocks.

    Deep nesting (more than max_depth levels) often indicates code that
    should be refactored using early returns or extracted functions.

    Args:
        code: Source code string to analyze
        max_depth: Maximum allowed nesting depth (default: 4)

    Returns:
        List of issues found
    """
    issues: List[Dict[str, any]] = []

    lines = code.split('\n')
    for line_num, line in enumerate(lines, start=1):
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Count leading spaces (assuming 4-space indent)
        leading_spaces = len(line) - len(line.lstrip())
        indent_level = leading_spaces // 4

        if indent_level > max_depth:
            issues.append({
                'line': line_num,
                'column': 1,
                'message': f"Deep nesting detected (level {indent_level}) - consider refactoring",
                'severity': 'warning',
                'rule': 'deep-nesting',
            })

    return issues


def check_long_functions(
    code: str,
    max_lines: int = 50,
    max_params: int = 5
) -> List[Dict[str, any]]:
    """
    Check for functions that are too long or have too many parameters.

    Long functions often do too much and should be split into smaller,
    focused functions.

    Args:
        code: Source code string to analyze
        max_lines: Maximum lines per function (default: 50)
        max_params: Maximum parameters per function (default: 5)

    Returns:
        List of issues found
    """
    issues: List[Dict[str, any]] = []

    # Pattern to match function definitions
    func_pattern = re.compile(
        r'^(\s*)(async\s+)?def\s+(\w+)\s*\((.*?)\)',
        re.MULTILINE | re.DOTALL
    )

    lines = code.split('\n')

    for match in func_pattern.finditer(code):
        func_indent = len(match.group(1))
        func_name = match.group(3)
        params_str = match.group(4)

        # Find line number of function start
        func_start_pos = match.start()
        func_line = code[:func_start_pos].count('\n') + 1

        # Count parameters (excluding self, cls)
        params = [p.strip() for p in params_str.split(',') if p.strip()]
        params = [p for p in params if not p.startswith(('self', 'cls'))]
        param_count = len(params)

        if param_count > max_params:
            issues.append({
                'line': func_line,
                'column': 1,
                'message': (
                    f"Function '{func_name}' has {param_count} parameters "
                    f"(max: {max_params}) - consider using a config object"
                ),
                'severity': 'warning',
                'rule': 'too-many-params',
            })

        # Count function lines (until next function or dedent)
        func_lines = 0
        in_function = False

        for i, line in enumerate(lines[func_line - 1:], start=func_line):
            stripped = line.strip()

            if i == func_line:
                in_function = True
                func_lines += 1
                continue

            if not in_function:
                continue

            # Check if we've exited the function (dedented or new function)
            current_indent = len(line) - len(line.lstrip()) if stripped else func_indent + 4
            if stripped and current_indent <= func_indent:
                break

            if stripped:  # Don't count blank lines
                func_lines += 1

        if func_lines > max_lines:
            issues.append({
                'line': func_line,
                'column': 1,
                'message': (
                    f"Function '{func_name}' is {func_lines} lines "
                    f"(max: {max_lines}) - consider splitting into smaller functions"
                ),
                'severity': 'warning',
                'rule': 'function-too-long',
            })

    return issues


def check_broad_exceptions(code: str) -> List[Dict[str, any]]:
    """
    Check for overly broad exception handling.

    Catching bare 'Exception' or using bare 'except:' can hide bugs
    and make debugging difficult.

    Args:
        code: Source code string to analyze

    Returns:
        List of issues found
    """
    issues: List[Dict[str, any]] = []

    lines = code.split('\n')
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Check for bare except
        if re.match(r'^except\s*:', stripped):
            issues.append({
                'line': line_num,
                'column': 1,
                'message': "Bare 'except:' catches all exceptions including KeyboardInterrupt",
                'severity': 'error',
                'rule': 'bare-except',
            })

        # Check for catching Exception (but allow if re-raising)
        elif re.match(r'^except\s+Exception\b', stripped):
            issues.append({
                'line': line_num,
                'column': 1,
                'message': "Catching 'Exception' is too broad - catch specific exceptions",
                'severity': 'warning',
                'rule': 'broad-exception',
            })

    return issues


def check_print_statements(code: str) -> List[Dict[str, any]]:
    """
    Check for print statements that should probably be logging.

    In production code, print statements should generally be replaced
    with proper logging.

    Args:
        code: Source code string to analyze

    Returns:
        List of issues found
    """
    issues: List[Dict[str, any]] = []

    # Pattern for print function calls
    print_pattern = re.compile(r'\bprint\s*\(')

    lines = code.split('\n')
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('#'):
            continue

        for match in print_pattern.finditer(line):
            issues.append({
                'line': line_num,
                'column': match.start() + 1,
                'message': "print() statement found - consider using logging instead",
                'severity': 'info',
                'rule': 'print-statement',
            })

    return issues


def analyze_file(file_path: str) -> List[Dict[str, any]]:
    """
    Run all checks on a Python file.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        List of all issues found, sorted by line number
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix != '.py':
        raise ValueError(f"Not a Python file: {file_path}")

    code = path.read_text(encoding='utf-8')

    all_issues: List[Dict[str, any]] = []

    # Run all checks
    all_issues.extend(check_magic_numbers(code))
    all_issues.extend(check_deep_nesting(code))
    all_issues.extend(check_long_functions(code))
    all_issues.extend(check_broad_exceptions(code))
    all_issues.extend(check_print_statements(code))

    # Sort by line number
    all_issues.sort(key=lambda x: (x['line'], x['column']))

    return all_issues


def format_issues(issues: List[Dict[str, any]], file_path: str = "") -> str:
    """
    Format issues into a readable report.

    Args:
        issues: List of issues from analyze_file
        file_path: Optional file path for context

    Returns:
        Formatted string report
    """
    if not issues:
        return "No issues found."

    lines = []
    if file_path:
        lines.append(f"Analysis of {file_path}")
        lines.append("=" * (len(file_path) + 12))
        lines.append("")

    # Group by severity
    by_severity = {'error': [], 'warning': [], 'info': []}
    for issue in issues:
        by_severity[issue['severity']].append(issue)

    for severity in ['error', 'warning', 'info']:
        severity_issues = by_severity[severity]
        if not severity_issues:
            continue

        lines.append(f"{severity.upper()}S ({len(severity_issues)}):")
        lines.append("-" * 40)
        for issue in severity_issues:
            lines.append(
                f"  Line {issue['line']}: [{issue['rule']}] {issue['message']}"
            )
        lines.append("")

    lines.append(f"Total: {len(issues)} issue(s) found")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python lint_patterns.py <file.py>")
        sys.exit(1)

    target_file = sys.argv[1]

    try:
        issues = analyze_file(target_file)
        print(format_issues(issues, target_file))
        sys.exit(1 if any(i['severity'] == 'error' for i in issues) else 0)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
