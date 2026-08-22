"""Command-line entry point for the course-wide O017 admission pipeline."""

from __future__ import annotations

import argparse
import json

from o017_pipeline import admit_unit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", required=True, help="locale-neutral unit ID, for example O017-U01")
    args = parser.parse_args()
    print(json.dumps(admit_unit(args.unit), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
