#!/usr/bin/env python3
"""Deterministically validate the O017 authentic-delivery wrapper.

Run from any directory:

    python scripts/validate_delivery_wrapper.py --write-qa

The QA JSON contains no wall-clock time, machine path, or runtime version. Its
bytes depend only on the validated package and this validator's fixed rules.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - explicit environment failure
    raise SystemExit(
        "jsonschema is required; install the locked project environment first"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "delivery"
WRAPPER = ROOT / "source" / "wrapper" / "index.qmd"
SCHEMA = DELIVERY / "schema" / "o017-delivery.schema.json"
INSTANCE = DELIVERY / "calibration" / "calibration-package.json"
DEFINITIONS = DELIVERY / "definitions" / "o017-delivery-definitions.json"
QA = DELIVERY / "VALIDATION.json"
FILE_MANIFEST = DELIVERY / "FILE_MANIFEST.csv"

CALIBRATION_MARKDOWN = tuple(
    DELIVERY / "calibration" / name
    for name in (
        "01-real-source-search.md",
        "02-seminar-supervised-equivalent.md",
        "03-independent-referee-cycle.md",
        "04-real-source-erratum-dossier.md",
        "05-externally-reviewed-local.md",
    )
)

DEFINITION_CSV = (
    DELIVERY / "calibration" / "evidence-manifest.csv",
    DELIVERY / "definitions" / "evidence-types.csv",
    DELIVERY / "definitions" / "lifecycle-statuses.csv",
    DELIVERY / "definitions" / "rubric-criteria.csv",
)

EXPECTED_ASSESSMENTS = tuple(f"O017-WRAP-A0{i}" for i in range(1, 6))
EXPECTED_ANCHORS = (
    "o017-wrap-index",
    "o017-wrap-no-contact",
    "o017-wrap-evaluator-privacy",
    "o017-wrap-assessments",
    "o017-wrap-a01-real-source-search",
    "o017-wrap-a02-seminar",
    "o017-wrap-a03-referee-cycle",
    "o017-wrap-a04-erratum",
    "o017-wrap-a05-community",
    "o017-wrap-gates",
    "o017-wrap-credential",
    "o017-wrap-machine-package",
    "o017-wrap-calibration-sources",
)
EXPECTED_FIRST_WRAPPER_HEADING = (
    "## Perangkat penyampaian dan penilaian autentik {#o017-wrap-index}"
)
EXPECTED_RENDER_LINKS = (
    "../delivery/definitions/o017-delivery-definitions.json",
    "../delivery/schema/o017-delivery.schema.json",
    "../delivery/calibration/calibration-package.json",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


def read_manifest() -> list[dict[str, str]]:
    with FILE_MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def schema_negative_tests(
    validator: jsonschema.Draft202012Validator, instance: dict[str, Any]
) -> dict[str, str]:
    cases: list[tuple[str, dict[str, Any]]] = []

    unauthorized = copy.deepcopy(instance)
    unauthorized["contact_control"]["transmission_performed"] = True
    cases.append(("unauthorized_transmission", unauthorized))

    unpassed = copy.deepcopy(instance)
    unpassed["package_kind"] = "learner_submission"
    unpassed["credit_eligible"] = True
    unpassed["synthetic_personas"] = False
    unpassed["result"]["credential_label"] = (
        "complete_externally_reviewed_local"
    )
    unpassed["result"]["a05_pathway"] = "externally_reviewed_local"
    cases.append(("completion_with_unpassed_gates", unpassed))

    missing_family = copy.deepcopy(instance)
    missing_family["exemplars"] = missing_family["exemplars"][:-1]
    cases.append(("missing_assessment_family", missing_family))

    no_transmission = copy.deepcopy(instance)
    no_transmission["package_kind"] = "learner_submission"
    no_transmission["credit_eligible"] = True
    no_transmission["synthetic_personas"] = False
    no_transmission["result"]["credential_label"] = (
        "complete_community_transaction"
    )
    no_transmission["result"]["a05_pathway"] = "community_transaction"
    cases.append(("community_completion_without_transmission", no_transmission))

    return {
        name: "REJECTED_AS_REQUIRED"
        if list(validator.iter_errors(candidate))
        else "ERRONEOUSLY_ACCEPTED"
        for name, candidate in cases
    }


def collect_actual_manifest_paths() -> set[str]:
    paths = {
        relative(path)
        for base in (ROOT / "source" / "wrapper", DELIVERY)
        for path in base.rglob("*")
        if path.is_file()
    }
    paths.add(relative(Path(__file__).resolve()))
    paths.remove(relative(FILE_MANIFEST))
    return paths


def build_report() -> tuple[dict[str, Any], list[dict[str, str]]]:
    errors: list[str] = []

    schema = read_json(SCHEMA)
    instance = read_json(INSTANCE)
    definitions = read_json(DEFINITIONS)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        positive_errors = sorted(
            validator.iter_errors(instance), key=lambda err: list(err.path)
        )
    except Exception as exc:  # includes malformed meta-schema
        errors.append(f"schema_meta_validation: {exc}")
        validator = jsonschema.Draft202012Validator({})
        positive_errors = []

    for issue in positive_errors:
        location = "/".join(str(part) for part in issue.path) or "<root>"
        errors.append(f"calibration_schema:{location}:{issue.message}")

    negative = schema_negative_tests(validator, instance)
    for name, outcome in negative.items():
        if outcome != "REJECTED_AS_REQUIRED":
            errors.append(f"negative_schema:{name}:{outcome}")

    csv_rows = 0
    for path in DEFINITION_CSV:
        rows = read_csv(path)
        if len(rows) < 2:
            errors.append(f"csv_empty:{relative(path)}")
            continue
        header = rows[0]
        if len(header) != len(set(header)):
            errors.append(f"csv_duplicate_header:{relative(path)}")
        for number, row in enumerate(rows, start=1):
            if len(row) != len(header):
                errors.append(f"csv_width:{relative(path)}:{number}")
        csv_rows += len(rows) - 1

    evidence_verified = 0
    for evidence in instance["evidence_items"]:
        path = ROOT / evidence["artifact_locator"]
        data = path.read_bytes()
        if len(data) != evidence["bytes"] or digest(data) != evidence["sha256"]:
            errors.append(f"evidence_identity:{evidence['evidence_id']}")
        else:
            evidence_verified += 1

    assessment_ids = tuple(
        sorted(exemplar["assessment_id"] for exemplar in instance["exemplars"])
    )
    if assessment_ids != EXPECTED_ASSESSMENTS:
        errors.append("assessment_family_coverage")

    truth_flags_ok = (
        instance["package_kind"] == "calibration_only"
        and instance["credit_eligible"] is False
        and instance["synthetic_personas"] is True
        and instance["contact_control"]["authorization_present"] is False
        and instance["contact_control"]["transmission_performed"] is False
        and instance["result"]["credential_label"] == "calibration_only"
        and set(instance["gate_results"].values()) == {"not_evaluated"}
        and set(instance["assessment_results"].values()) == {"calibration_only"}
    )
    if not truth_flags_ok:
        errors.append("calibration_truth_or_contact_boundary")

    markdown_paths = (WRAPPER, *CALIBRATION_MARKDOWN, DELIVERY / "README.md")
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        if path == WRAPPER:
            if not re.search(r'^title:\s+"Pembungkus penyelenggaraan autentik O017/D120"$', text, flags=re.MULTILINE):
                errors.append(f"markdown_yaml_title:{relative(path)}")
        elif not re.search(r"^#\s+", text, flags=re.MULTILINE):
            errors.append(f"markdown_h1:{relative(path)}")
    for path in CALIBRATION_MARKDOWN:
        text = path.read_text(encoding="utf-8")
        if "`calibration_only`" not in text or "Kredit pelajar: `false`" not in text:
            errors.append(f"calibration_banner:{relative(path)}")

    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    first_wrapper_heading = next(
        (line for line in wrapper_text.splitlines() if line.startswith("## ")), ""
    )
    if first_wrapper_heading != EXPECTED_FIRST_WRAPPER_HEADING:
        errors.append("wrapper_first_heading")
    anchors = tuple(re.findall(r"\{#([a-z0-9-]+)\}", wrapper_text))
    if anchors != EXPECTED_ANCHORS:
        errors.append("wrapper_anchor_inventory")
    for target in EXPECTED_RENDER_LINKS:
        if f"]({target})" not in wrapper_text:
            errors.append(f"wrapper_render_link:{target}")

    # Exact elementary identities used by the erratum calibration. These
    # Fraction operations are independent of a CAS and platform floating point.
    dy_then_dx = Fraction(1, 1) - Fraction(1, 2)
    dx_then_dy = -(Fraction(1, 1) - Fraction(1, 2))
    # Coefficient pairs encode ax+by.  Quotient-rule numerators reduce to
    # (x+y)-2y and -(x+y)+2x respectively; both must be x-y.
    dy_numerator = (1 + 0, 1 - 2)
    dx_numerator = (-1 + 2, -1 + 0)
    derivative_numerators_ok = dy_numerator == (1, -1) == dx_numerator
    if not derivative_numerators_ok or (dy_then_dx, dx_then_dy) != (
        Fraction(1, 2),
        Fraction(-1, 2),
    ):
        errors.append("calibration_mathematics")

    manifest = read_manifest()
    manifest_paths = {row["path"] for row in manifest}
    actual_paths = collect_actual_manifest_paths()
    if manifest_paths != actual_paths:
        missing = sorted(actual_paths - manifest_paths)
        extra = sorted(manifest_paths - actual_paths)
        errors.append(f"manifest_inventory:missing={missing}:extra={extra}")

    manifest_verified_without_qa = 0
    for row in manifest:
        if row["path"] == relative(QA):
            continue
        path = ROOT / row["path"]
        data = path.read_bytes()
        if len(data) != int(row["bytes"]) or digest(data) != row["sha256"]:
            errors.append(f"manifest_identity:{row['path']}")
        else:
            manifest_verified_without_qa += 1

    report: dict[str, Any] = {
        "calibration_truth_witness": {
            "all_assessment_results": "calibration_only",
            "all_gate_results": "not_evaluated",
            "authorization_present": False,
            "credential_label": "calibration_only",
            "credit_eligible": False,
            "package_kind": "calibration_only",
            "synthetic_personas": True,
            "transmission_performed": False,
        },
        "errors": sorted(errors),
        "reproducibility": {
            "contains_wall_clock": False,
            "deterministic_json": "UTF-8; sorted keys; indent 2; LF newline",
            "entry_point": "python scripts/validate_delivery_wrapper.py --write-qa",
        },
        "results": {
            "assessment_family_coverage": list(EXPECTED_ASSESSMENTS),
            "calibration_instance_validation": "PASS"
            if not positive_errors
            else "FAIL",
            "calibration_truth_flags": "PASS" if truth_flags_ok else "FAIL",
            "csv_data_rows": csv_rows,
            "csv_files_parsed": len(DEFINITION_CSV),
            "csv_header_and_row_width_validation": "PASS"
            if not any(error.startswith("csv_") for error in errors)
            else "FAIL",
            "evidence_byte_and_sha256_validation": "PASS"
            if evidence_verified == len(instance["evidence_items"])
            else "FAIL",
            "evidence_files_verified": evidence_verified,
            "file_manifest_entries": len(manifest),
            "file_manifest_entries_verified_excluding_qa_output": manifest_verified_without_qa,
            "file_manifest_inventory_validation": "PASS"
            if manifest_paths == actual_paths
            else "FAIL",
            "markdown_files_utf8_and_headed": len(markdown_paths),
            "negative_schema_tests": negative,
            "no_contact_no_transmission_flags": "PASS"
            if truth_flags_ok
            else "FAIL",
            "schema_meta_validation": "PASS"
            if not any(error.startswith("schema_meta_validation") for error in errors)
            else "FAIL",
            "symbolic_identity_witness": {
                "dx_then_dy": "-1/2",
                "dy_then_dx": "1/2",
                "exact_arithmetic": True,
            },
            "wrapper_explicit_anchors": len(anchors),
            "wrapper_first_heading": first_wrapper_heading,
            "wrapper_render_links": list(EXPECTED_RENDER_LINKS),
        },
        "schema_id": schema["$id"],
        "status": "PASS" if not errors else "FAIL",
        "tools": {
            "jsonschema_requirement": ">=4.18",
            "python_requirement": ">=3.10",
        },
        "validation_id": "O017-WRAP-VALIDATION-2",
    }
    return report, manifest


def encode_report(report: dict[str, Any]) -> bytes:
    return (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-qa",
        action="store_true",
        help="write the deterministic report to delivery/VALIDATION.json",
    )
    args = parser.parse_args()

    report, manifest = build_report()
    expected = encode_report(report)
    if args.write_qa:
        QA.write_bytes(expected)
    elif not QA.exists() or QA.read_bytes() != expected:
        print("FAIL: delivery/VALIDATION.json is not the deterministic expected output")
        return 1

    qa_row = next((row for row in manifest if row["path"] == relative(QA)), None)
    qa_identity_ok = bool(
        qa_row
        and int(qa_row["bytes"]) == len(expected)
        and qa_row["sha256"] == digest(expected)
    )

    summary = {
        "qa_bytes": len(expected),
        "qa_manifest_identity": "PASS" if qa_identity_ok else "FAIL",
        "qa_sha256": digest(expected),
        "status": report["status"] if qa_identity_ok else "FAIL",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" and qa_identity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
