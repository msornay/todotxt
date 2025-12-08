"""todotxt"""

import argparse

__version__ = "0.1.0"


def scan_todotxt(file):
    """Scan a todo.txt file."""
    pass


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("file", type=argparse.FileType("r"), help="todo.txt file")

    args = parser.parse_args()

    scan_todotxt(args.file)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
