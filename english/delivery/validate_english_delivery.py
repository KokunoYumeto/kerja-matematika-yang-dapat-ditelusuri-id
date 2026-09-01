"""Bounded validator for the O017 English authentic-delivery teaching package.

No network access, external contact, recursive enumeration, or learner-credit
award occurs. --refresh-manifest changes only the two local derived evidence
inventories. An optional explicitly supplied Indonesian root permits a
structural translation comparison without being needed by a standalone reader.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "source/wrapper/index.qmd",
    "delivery/README.md",
    "delivery/definitions/o017-delivery-definitions.json",
    "delivery/definitions/rubric-criteria.csv",
    "delivery/definitions/evidence-types.csv",
    "delivery/definitions/lifecycle-statuses.csv",
    "delivery/schema/o017-delivery.schema.json",
    "delivery/calibration/01-real-source-search.md",
    "delivery/calibration/02-seminar-supervised-equivalent.md",
    "delivery/calibration/03-independent-referee-cycle.md",
    "delivery/calibration/04-real-source-erratum-dossier.md",
    "delivery/calibration/05-externally-reviewed-local.md",
    "delivery/calibration/calibration-package.json",
    "delivery/calibration/evidence-manifest.csv",
]
DOSSIERS = FILES[7:12]
PACKAGE = ROOT / FILES[12]
MANIFEST = ROOT / FILES[13]
ID_RE = re.compile(r"O017-WRAP-[A-Z0-9-]+")
ANCHOR_RE = re.compile(r"\{#([^\s}]+)")
INLINE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
URL_RE = re.compile(r"https?://[^\s<>]+")
MANIFEST_FIELDS = [
    "evidence_id", "assessment_id", "artifact_locator", "bytes", "sha256",
    "verification_status", "synthetic_calibration", "credit_eligible",
    "transmission_performed", "rights_statement",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")


def checked_local_artifact(locator: str) -> Path:
    if locator not in DOSSIERS:
        raise ValueError(f"Unregistered dossier locator: {locator!r}")
    path = (ROOT / locator).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Artifact escapes the English-edition root")
    return path


def refresh_manifest(package) -> None:
    rows = []
    for item in package["evidence_items"]:
        content = checked_local_artifact(item["artifact_locator"]).read_bytes()
        item["bytes"] = len(content)
        item["sha256"] = digest(content)
        rows.append({
            "evidence_id": item["evidence_id"],
            "assessment_id": item["assessment_id"],
            "artifact_locator": item["artifact_locator"],
            "bytes": item["bytes"],
            "sha256": item["sha256"],
            "verification_status": item["verification_status"],
            "synthetic_calibration": "true",
            "credit_eligible": "false",
            "transmission_performed": "false",
            "rights_statement": item["rights_statement"],
        })
    dump_json(PACKAGE, package)
    with MANIFEST.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_csv(path: Path):
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8-sig"))))
    if not rows or len(rows[0]) != len(set(rows[0])):
        raise ValueError(f"Missing or duplicate CSV headers: {path.name}")
    if any(len(row) != len(rows[0]) for row in rows[1:]):
        raise ValueError(f"Uneven CSV row width: {path.name}")
    return rows[0], [dict(zip(rows[0], row)) for row in rows[1:]]


def compare_original(original_root: Path, errors: list[str], checks: dict) -> None:
    original_root = original_root.resolve()
    compared = []
    for relative in [FILES[0], *DOSSIERS]:
        original = (original_root / relative).read_text(encoding="utf-8-sig")
        english = (ROOT / relative).read_text(encoding="utf-8-sig")
        for label, left, right in [
            ("stable IDs", set(ID_RE.findall(original)), set(ID_RE.findall(english))),
            ("explicit anchors", ANCHOR_RE.findall(original), ANCHOR_RE.findall(english)),
            ("inline code", collections.Counter(INLINE_RE.findall(original)),
             collections.Counter(INLINE_RE.findall(english))),
            ("URLs", set(URL_RE.findall(original)), set(URL_RE.findall(english))),
            ("heading count", len(re.findall(r"^#{1,6} ", original, re.M)),
             len(re.findall(r"^#{1,6} ", english, re.M))),
        ]:
            if left != right:
                errors.append(f"Translation mismatch ({label}): {relative}")
        if relative in DOSSIERS[2:4]:
            fenced = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)
            if fenced.findall(original) != fenced.findall(english):
                errors.append(f"Mathematical fenced-code mismatch: {relative}")
        compared.append(relative)

    original_schema = read_json(original_root / FILES[6])
    original_schema["properties"]["locale"]["const"] = "en"
    if original_schema != read_json(ROOT / FILES[6]):
        errors.append("Schema changed beyond the localized locale constraint")

    original_defs = read_json(original_root / FILES[2])
    english_defs = read_json(ROOT / FILES[2])
    original_defs["default_locale"] = "en"
    for group in ("assessment_families", "noncompensable_gates"):
        for source, translated in zip(original_defs[group], english_defs[group]):
            source["label_id"] = translated["label_id"]
            if "pass_condition_id" in source:
                source["pass_condition_id"] = translated["pass_condition_id"]
    if original_defs != english_defs:
        errors.append("Definitions changed beyond human-readable text and locale")

    original_package = read_json(original_root / FILES[12])
    english_package = read_json(PACKAGE)
    original_package["locale"] = "en"
    original_package["contact_control"]["notes_id"] = english_package["contact_control"]["notes_id"]
    for source, translated in zip(original_package["exemplars"], english_package["exemplars"]):
        for key in ("summary_id", "limitations_id"):
            source[key] = translated[key]
    for source, translated in zip(original_package["evidence_items"], english_package["evidence_items"]):
        for key in ("bytes", "sha256"):
            source[key] = translated[key]
    for key in ("decision_id", "limitations_id"):
        original_package["result"][key] = english_package["result"][key]
    if original_package != english_package:
        errors.append("Calibration package changed beyond translation, locale, and hashes")

    translatable_csv_fields = {
        FILES[3]: {"locale", "label", "requirement", "pass_evidence"},
        FILES[4]: {"locale", "label", "description", "verification_rule"},
        FILES[5]: {"locale", "definition", "minimum_evidence"},
    }
    for relative, allowed in translatable_csv_fields.items():
        original_header, original_rows = parse_csv(original_root / relative)
        english_header, english_rows = parse_csv(ROOT / relative)
        if original_header != english_header or len(original_rows) != len(english_rows):
            errors.append(f"CSV structure mismatch: {relative}")
            continue
        for source, translated in zip(original_rows, english_rows):
            for key in allowed:
                source[key] = translated[key]
            if source != translated:
                errors.append(f"Non-text CSV field changed: {relative}: {source}")

    checks["indonesian_structure_comparison"] = {
        "performed": True,
        "markdown_files": compared,
        "ids_anchors_inline_code_urls_heading_counts": "checked",
        "a03_a04_mathematical_fenced_code": "identical",
        "schema_nonlocale_changes": "none permitted",
        "definitions_and_package_nontranslation_changes": "none permitted",
        "csv_machine_columns": "checked",
    }


def validate(original_root: Path | None) -> dict:
    errors: list[str] = []
    checks: dict = {}
    inventory = []
    for relative in FILES:
        data = (ROOT / relative).read_bytes()
        text = data.decode("utf-8-sig", errors="strict")
        if not text.strip():
            errors.append(f"Empty file: {relative}")
        inventory.append({"path": relative, "bytes": len(data), "sha256": digest(data)})
        if relative.endswith((".md", ".qmd")):
            anchors = ANCHOR_RE.findall(text)
            if len(anchors) != len(set(anchors)):
                errors.append(f"Duplicate explicit anchors: {relative}")
            if re.search(r"^#{1,6}\s*$", text, re.M):
                errors.append(f"Empty heading: {relative}")
            if relative in DOSSIERS and ("calibration_only" not in text or "`false`" not in text):
                errors.append(f"Missing calibration labels: {relative}")

    package = read_json(PACKAGE)
    schema = read_json(ROOT / FILES[6])
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(package), key=lambda e: str(list(e.path))):
        errors.append(f"Schema at {list(error.path)}: {error.message}")
    checks["json_schema_draft_2020_12"] = "checked"

    fixed_assertions = [
        (package["package_kind"] == "calibration_only", "package_kind"),
        (package["credit_eligible"] is False, "credit_eligible"),
        (package["synthetic_personas"] is True, "synthetic_personas"),
        (package["contact_control"]["authorization_present"] is False, "authorization_present"),
        (package["contact_control"]["transmission_performed"] is False, "transmission_performed"),
        (package["result"]["credential_label"] == "calibration_only", "credential_label"),
        (package["community_lifecycle"]["current_state"] == "prepared", "community_state"),
        (package["locale"] == "en", "locale"),
        (all(e["human_status"] == "synthetic_persona" for e in package["evaluators"]), "synthetic_evaluators"),
        (all(not e["external_event"] for e in package["community_lifecycle"]["events"]), "no_external_events"),
        (all(not e["actual_completion_claim"] for e in package["exemplars"]), "no_completion_claims"),
    ]
    for passed, name in fixed_assertions:
        if not passed:
            errors.append(f"Calibration assertion failed: {name}")
    checks["calibration_assertions"] = len(fixed_assertions)

    definitions = read_json(ROOT / FILES[2])
    evidence_ids = {item["evidence_id"] for item in package["evidence_items"]}
    source_ids = {item["source_id"] for item in package["sources"]}
    evaluator_ids = {item["evaluator_id"] for item in package["evaluators"]}
    if len(evidence_ids) != 5:
        errors.append("Evidence inventory must have five unique dossiers")
    for exemplar in package["exemplars"]:
        for field, available in (("evidence_ids", evidence_ids), ("source_ids", source_ids), ("evaluator_ids", evaluator_ids)):
            if not set(exemplar[field]).issubset(available):
                errors.append(f"Unresolved {field}: {exemplar['exemplar_id']}")
    if {a["assessment_id"] for a in definitions["assessment_families"]} != set(package["assessment_results"]):
        errors.append("Assessment family inventory differs")
    if {g["gate_id"] for g in definitions["noncompensable_gates"]} != set(package["gate_results"]):
        errors.append("Gate inventory differs")
    checks["id_references"] = "checked"

    csv_counts = {}
    for relative in (FILES[3], FILES[4], FILES[5], FILES[13]):
        headers, rows = parse_csv(ROOT / relative)
        csv_counts[relative] = len(rows)
        if "locale" in headers and any(row["locale"] != "en" for row in rows):
            errors.append(f"Non-English CSV locale: {relative}")
    headers, rows = parse_csv(MANIFEST)
    if headers != MANIFEST_FIELDS:
        errors.append("Evidence manifest headers differ from the contract")
    if len(rows) != 5 or {row["evidence_id"] for row in rows} != evidence_ids:
        errors.append("Evidence manifest dossier inventory differs")
    manifest_by_id = {row["evidence_id"]: row for row in rows}
    for item in package["evidence_items"]:
        data = checked_local_artifact(item["artifact_locator"]).read_bytes()
        if item["bytes"] != len(data) or item["sha256"] != digest(data):
            errors.append(f"Dossier bytes/hash mismatch: {item['artifact_locator']}")
        row = manifest_by_id.get(item["evidence_id"], {})
        for key in ("assessment_id", "artifact_locator", "bytes", "sha256", "verification_status", "rights_statement"):
            if row.get(key) != str(item[key]):
                errors.append(f"Manifest/package mismatch: {item['evidence_id']}: {key}")
        if (row.get("synthetic_calibration"), row.get("credit_eligible"), row.get("transmission_performed")) != ("true", "false", "false"):
            errors.append(f"Manifest calibration flags incorrect: {item['evidence_id']}")
    checks["csv_row_counts"] = csv_counts
    checks["dossier_byte_and_sha256_checks"] = len(package["evidence_items"])

    if original_root is not None:
        compare_original(original_root, errors, checks)
    else:
        checks["indonesian_structure_comparison"] = {"performed": False}

    return {
        "validation_id": "O017-EN-TEACHING-VALIDATION-1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not errors else "fail",
        "scope": "English teaching wrapper and calibration package only; not an authentic learner completion assessment",
        "network_or_contact_performed": False,
        "credit_awarded": False,
        "checks": checks,
        "errors": errors,
        "files": inventory,
        "known_inherited_limitations": [
            "The schema's exemplar and evidence definitions are calibration-specific; this validator does not establish a complete authentic learner-submission model.",
            "Historical source-retrieval witnesses are preserved from the Indonesian edition; no fresh network retrieval was performed for this translation.",
            "Text and formula preservation checks are not a rendered PDF, screen-reader, or semantic re-proof audit.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--compare-indonesian", type=Path)
    args = parser.parse_args()
    if args.refresh_manifest:
        refresh_manifest(read_json(PACKAGE))
    report = validate(args.compare_indonesian)
    report_name = "validation-report.json" if args.compare_indonesian else "validation-standalone-report.json"
    dump_json(ROOT / "delivery" / report_name, report)
    print(json.dumps({"status": report["status"], "files": len(report["files"]),
                      "errors": report["errors"], "report": "delivery/" + report_name}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
