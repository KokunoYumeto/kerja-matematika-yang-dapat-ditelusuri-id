"""Emit a finite, exact witness for Cassini's Fibonacci identity.

The JSON certifies only the indices 1 through 24.  Re-running this program is
reproducible empirical evidence about the implementation and those indices; it
is not a proof of the universal identity for every positive integer.
"""

from __future__ import annotations

from hashlib import sha256
import json
import sys
from typing import Any


INDEX_MIN = 1
INDEX_MAX = 24


def canonical_json(value: Any) -> bytes:
    """Return the package's canonical JSON encoding, without a trailing LF."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def fibonacci_values(last_index: int) -> list[int]:
    values = [0, 1]
    while len(values) <= last_index:
        values.append(values[-1] + values[-2])
    return values


def make_records() -> list[dict[str, int]]:
    values = fibonacci_values(INDEX_MAX + 1)
    return [
        {
            "f_n": values[index],
            "f_next": values[index + 1],
            "f_prev": values[index - 1],
            "lhs": values[index - 1] * values[index + 1] - values[index] ** 2,
            "n": index,
            "rhs": -1 if index % 2 else 1,
        }
        for index in range(INDEX_MIN, INDEX_MAX + 1)
    ]


def records_are_valid(records: list[dict[str, int]]) -> bool:
    expected_keys = {"f_n", "f_next", "f_prev", "lhs", "n", "rhs"}
    if type(records) is not list:
        return False
    for record in records:
        if type(record) is not dict or set(record) != expected_keys:
            return False
        if any(type(value) is not int for value in record.values()):
            return False

    if [record["n"] for record in records] != list(
        range(INDEX_MIN, INDEX_MAX + 1)
    ):
        return False

    for position, record in enumerate(records):
        if record["f_next"] != record["f_n"] + record["f_prev"]:
            return False
        if record["lhs"] != record["f_prev"] * record["f_next"] - record["f_n"] ** 2:
            return False
        if record["rhs"] != (-1 if record["n"] % 2 else 1):
            return False
        if record["lhs"] != record["rhs"]:
            return False
        if position and record["f_prev"] != records[position - 1]["f_n"]:
            return False
        if position and record["f_n"] != records[position - 1]["f_next"]:
            return False

    return records[0]["f_prev"] == 0 and records[0]["f_n"] == 1


def tamper_control_is_detected(records: list[dict[str, int]]) -> bool:
    altered = [record.copy() for record in records]
    altered[7]["f_n"] += 1
    return not records_are_valid(altered)


def main() -> None:
    records = make_records()
    result = {
        "arithmetic": "exact integers",
        "finite_scope": {"index_max": INDEX_MAX, "index_min": INDEX_MIN},
        "records": records,
        "records_sha256": sha256(canonical_json(records)).hexdigest(),
        "schema": "o017-u06-recurrence-witness-v1",
        "statement": "F[n-1]*F[n+1]-F[n]^2=(-1)^n",
        "summary": {
            "all_records_valid": records_are_valid(records),
            "record_count": len(records),
            "tamper_control_detected": tamper_control_is_detected(records),
        },
        "universal_status": "not established by this finite computation",
    }
    sys.stdout.buffer.write(canonical_json(result) + b"\n")


if __name__ == "__main__":
    main()
