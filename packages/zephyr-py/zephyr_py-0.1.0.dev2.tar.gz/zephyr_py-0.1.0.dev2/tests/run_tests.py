#!/usr/bin/env python3
"""
Test runner for Zephyr authentication system.

Provides a comprehensive test runner with different test categories and reporting.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(
    category: str = "all",
    verbose: bool = False,
    coverage: bool = False,
    parallel: bool = False,
    markers: str = None,
    pattern: str = None,
) -> int:
    """
    Run tests with specified options.

    Args:
        category: Test category to run (all, unit, integration, security)
        verbose: Enable verbose output
        coverage: Enable coverage reporting
        parallel: Run tests in parallel
        markers: Pytest markers to filter tests
        pattern: Test pattern to match

    Returns:
        Exit code from pytest
    """
    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test directory
    cmd.append("tests/")

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add coverage
    if coverage:
        cmd.extend(["--cov=zephyr", "--cov-report=html", "--cov-report=term"])

    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])

    # Add markers
    if markers:
        cmd.extend(["-m", markers])

    # Add pattern
    if pattern:
        cmd.extend(["-k", pattern])

    # Category-specific options
    if category == "unit":
        cmd.extend(["-m", "unit"])
    elif category == "integration":
        cmd.extend(["-m", "integration"])
    elif category == "security":
        cmd.extend(["-m", "security"])
    elif category == "fast":
        cmd.extend(["-m", "not slow"])

    # Add test discovery options
    cmd.extend(
        [
            "--tb=short",  # Short traceback format
            "--strict-markers",  # Strict marker checking
            "--disable-warnings",  # Disable warnings for cleaner output
        ]
    )

    print(f"Running tests with command: {' '.join(cmd)}")
    print("-" * 60)

    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Zephyr Authentication System Test Runner")

    parser.add_argument(
        "category",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "security", "fast"],
        help="Test category to run (default: all)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("-c", "--coverage", action="store_true", help="Enable coverage reporting")

    parser.add_argument("-p", "--parallel", action="store_true", help="Run tests in parallel")

    parser.add_argument("-m", "--markers", type=str, help="Pytest markers to filter tests")

    parser.add_argument("-k", "--pattern", type=str, help="Test pattern to match")

    parser.add_argument("--list-tests", action="store_true", help="List all available tests")

    args = parser.parse_args()

    # List tests if requested
    if args.list_tests:
        cmd = ["python", "-m", "pytest", "tests/", "--collect-only", "-q"]
        subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        return 0

    # Run tests
    exit_code = run_tests(
        category=args.category,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel,
        markers=args.markers,
        pattern=args.pattern,
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
