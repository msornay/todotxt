"""Command-line interface for todotxt."""

import argparse

from todotxt import scan_todotxt


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.add_argument("file", type=argparse.FileType("r"), help="todo.txt file")

    args = parser.parse_args()

    scan_todotxt(args.file)

    return 0
