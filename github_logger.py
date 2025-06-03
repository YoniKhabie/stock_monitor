"""
GitHub Actions Logging Utilities for Python

Provides helper functions to produce annotated log messages that appear
nicely in GitHub Actions logs, including errors, warnings, notices, and
collapsible groups.

Usage:
    from github_logger import (
        log,
        log_error,
        log_warning,
        log_notice,
        log_group_start,
        log_group_end
    )

    log("This is a basic log message")

    log_group_start("Starting SMA Analysis")
    percentage = get_percentage_above_sma()
    log_notice(f"{percentage}% of stocks are above their 20-day SMA")
    log_group_end()

    try:
        raise ValueError("Something went wrong")
    except Exception as e:
        log_error(f"Exception occurred: {e}", file="analyzer.py", line=42, col=5)

Functions:
    log(message: str)
        Prints a basic log message.

    log_error(message: str, file: str = "", line: int = 0, col: int = 0)
        Prints an error annotation. Optionally includes file, line, and column info.

    log_warning(message: str, file: str = "", line: int = 0)
        Prints a warning annotation. Optionally includes file and line info.

    log_notice(message: str)
        Prints a notice annotation.

    log_group_start(name: str)
        Starts a collapsible log group with the given name.

    log_group_end()
        Ends the current log group.
"""

def log(message: str):
    print(message)

def log_error(message: str, file: str = "", line: int = 0, col: int = 0):
    location = f"file={file},line={line},col={col}" if file else ""
    print(f"::error {location}::{message}")

def log_warning(message: str, file: str = "", line: int = 0):
    location = f"file={file},line={line}" if file else ""
    print(f"::warning {location}::{message}")

def log_notice(message: str):
    print(f"::notice::{message}")

def log_group_start(name: str):
    print(f"::group::{name}")

def log_group_end():
    print("::endgroup::")
