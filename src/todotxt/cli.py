"""Command-line interface for todotxt."""

import argparse


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version="0.1.0")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return 0
