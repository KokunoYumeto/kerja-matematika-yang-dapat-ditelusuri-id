#!/usr/bin/env python3
"""Validate O017's locale-neutral semantic/assessment wrapper in full."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

import generate_semantic_wrapper as generator


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
QA_PATH = ROOT / "qa" / "SEMANTIC_WRAPPER_QA.json"
REQUIRED_ENTITY_TYPES = {
    "learning_outcome",
    "competency",
    "assessment",
    "rubric",
    "criterion",
    "submission",
    "attempt",
    "evaluator",
    "evidence",
    "result",
    "credential_state",
}
FORBIDDEN_LOCALIZED_FIELDS = {
    "title",
    "label",
    "description",
    "instructions",
    "text",
    "locale",
    "language",
    "html_fragment",
}
RELATION_HEADER = [
    "id",
    "source",
    "predicate",
    "target",
    "status",
    "evidence_kind",
    "superseded_by",
    "correction_id",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def require(condition: bool, message: str, checks: list[str] | None = None) -> None:
    if not condition:
        fail(message)
    if checks is not None:
        checks.append(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_line(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path.name}:{number}: invalid JSON: {exc}")
        if canonical_line(record) != (line + "\n").encode("utf-8"):
            fail(f"{path.name}:{number}: noncanonical JSON serialization")
        records.append(record)
    return records


def file_identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def validate_schema_records(
    validator: Draft202012Validator,
    records: list[dict[str, Any]],
    localizations: list[dict[str, Any]],
) -> None:
    for group_name, group in (("records", records), ("localizations", localizations)):
        for index, record in enumerate(group, 1):
            errors = sorted(validator.iter_errors(record), key=lambda error: list(error.absolute_path))
            if errors:
                detail = "; ".join(error.message for error in errors[:4])
                fail(f"schema validation failed for {group_name} line {index} ({record.get('id')}): {detail}")


def negative_schema_tests(
    validator: Draft202012Validator,
    records: list[dict[str, Any]],
    localizations: list[dict[str, Any]],
) -> list[str]:
    tests: list[tuple[str, dict[str, Any]]] = []

    localized_semantic = deepcopy(records[0])
    localized_semantic["title"] = "field that must not be in a neutral record"
    tests.append(("reject_locale_bound_title_on_semantic_record", localized_semantic))

    wrong_locale = deepcopy(localizations[0])
    wrong_locale["locale"] = "en-US"
    tests.append(("reject_wrong_locale_identity", wrong_locale))

    fragment_as_id = deepcopy(records[0])
    fragment_as_id["id"] = "o017-u01-outcomes"
    tests.append(("reject_renderer_fragment_as_semantic_id", fragment_as_id))

    criterion = deepcopy(next(record for record in records if record["entity_type"] == "criterion"))
    del criterion["rubric_id"]
    tests.append(("reject_incomplete_criterion", criterion))

    accepted: list[str] = []
    for name, invalid_record in tests:
        if not list(validator.iter_errors(invalid_record)):
            fail(f"negative schema test unexpectedly accepted: {name}")
        accepted.append(name)
    return accepted


def validate_locators(records: list[dict[str, Any]]) -> tuple[int, int]:
    locator_count = 0
    authentic_bound_ids: set[str] = set()
    required_authentic_roles = {"assessment_prompt", "rubric", "calibration_exemplar", "form_template"}
    for record in records:
        authentic_roles: set[str] = set()
        for locator in record.get("locators", []):
            locator_count += 1
            if locator["canonical_identity"] is not False:
                fail(f"canonical locator flag is not false: {record['id']}")
            path = ROOT / locator["path"]
            if not path.is_file():
                fail(f"locator path missing: {record['id']} -> {locator['path']}")
            text = path.read_text(encoding="utf-8")
            fragment = locator["fragment"]
            if f"{{#{fragment}}}" not in text and f'id="{fragment}"' not in text:
                fail(f"locator fragment missing: {record['id']} -> {locator['path']}#{fragment}")
            if record["entity_type"] == "assessment" and record["assessment_kind"] == "authentic_delivery":
                authentic_roles.add(locator["role"])
        if record["entity_type"] == "assessment" and record["assessment_kind"] == "authentic_delivery":
            if authentic_roles and authentic_roles != required_authentic_roles:
                fail(f"incomplete authentic locator role set: {record['id']} -> {sorted(authentic_roles)}")
            if authentic_roles == required_authentic_roles:
                authentic_bound_ids.add(record["id"])
    return locator_count, len(authentic_bound_ids)


def collect_delivery_ids(value: Any) -> set[str]:
    identifiers: set[str] = set()
    if isinstance(value, dict):
        for child in value.values():
            identifiers.update(collect_delivery_ids(child))
    elif isinstance(value, list):
        for child in value:
            identifiers.update(collect_delivery_ids(child))
    elif isinstance(value, str) and value.startswith("O017-WRAP-") and " " not in value:
        identifiers.add(value)
    return identifiers


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-qa", action="store_true", help="write deterministic QA evidence")
    args = parser.parse_args(list(argv) if argv is not None else None)

    checks: list[str] = []
    baseline = json.loads(generator.BASELINE_PATH.read_text(encoding="utf-8"))
    generator.verify_baseline(baseline)
    checks.append(
        "historical backend ID set and stable record fields are unchanged; the ten permitted "
        "version-specific records match the current .1 reader"
    )

    schema = json.loads(generator.SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    checks.append("JSON Schema is valid Draft 2020-12")

    records = load_jsonl(generator.RECORDS_PATH)
    localizations = load_jsonl(generator.LOCALIZATIONS_PATH)
    validate_schema_records(validator, records, localizations)
    checks.append("every semantic and localized record validates against the enforceable schema")

    if [record["id"] for record in records] != sorted(record["id"] for record in records):
        fail("semantic records are not sorted by stable ID")
    if [record["id"] for record in localizations] != sorted(record["id"] for record in localizations):
        fail("localized records are not sorted by stable ID")
    checks.append("record streams use canonical JSONL and stable-ID ordering")

    semantic_ids = [record["id"] for record in records]
    localization_ids = [record["id"] for record in localizations]
    if len(semantic_ids) != len(set(semantic_ids)):
        fail("duplicate semantic ID")
    if len(localization_ids) != len(set(localization_ids)):
        fail("duplicate localization ID")
    if set(semantic_ids) & set(localization_ids):
        fail("semantic/localization ID collision")

    baseline_records = load_jsonl(ROOT / "backend" / "records.jsonl")
    baseline_ids = {record["id"] for record in baseline_records}
    if baseline_ids & set(semantic_ids + localization_ids):
        fail("wrapper ID collides with pre-existing backend ID")
    checks.append("all wrapper IDs are unique and do not collide with the 1,787 preserved IDs")

    entity_counts = Counter(record["entity_type"] for record in records)
    if set(entity_counts) != REQUIRED_ENTITY_TYPES:
        fail(f"entity class closure differs: {sorted(entity_counts)}")
    if any(entity_counts[kind] < 1 for kind in REQUIRED_ENTITY_TYPES):
        fail("a required semantic entity class is empty")
    checks.append("all eleven mandated semantic entity classes have concrete records")

    localization_by_id = {record["id"]: record for record in localizations}
    semantic_by_id = {record["id"]: record for record in records}
    for record in records:
        forbidden = FORBIDDEN_LOCALIZED_FIELDS & set(record)
        if forbidden:
            fail(f"locale-bound fields on neutral record {record['id']}: {sorted(forbidden)}")
        for loc_id in record["localization_ids"]:
            if loc_id not in localization_by_id:
                fail(f"unresolved localization {loc_id} on {record['id']}")
            localized = localization_by_id[loc_id]
            if localized["subject_id"] != record["id"]:
                fail(f"localization subject mismatch: {loc_id}")
            if localized["locale"] != "id-ID" or localized["language"] != "id":
                fail(f"locale identity mismatch: {loc_id}")
    for localized in localizations:
        if localized["subject_id"] not in semantic_by_id:
            fail(f"orphan localization: {localized['id']}")
    checks.append("all human-language text is explicit id-ID/id localization attached to a neutral subject")

    locator_count, authentic_bound_count = validate_locators(records)
    if authentic_bound_count != 5:
        fail(f"expected all five authentic assessment locator bundles, found {authentic_bound_count}")
    checks.append("all renderer fragments are verified noncanonical locators to existing files/fragments")

    outcomes = [record for record in records if record["entity_type"] == "learning_outcome"]
    if len(outcomes) != 71:
        fail(f"expected 71 learning outcomes, found {len(outcomes)}")
    outcomes_by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in outcomes:
        outcomes_by_unit[outcome["unit_id"]].append(outcome)
    if set(outcomes_by_unit) != {f"O017-U{unit:02d}" for unit in range(1, 10)}:
        fail("learning outcome unit closure mismatch")
    for unit_id, unit_outcomes in outcomes_by_unit.items():
        sequences = sorted(item["sequence"] for item in unit_outcomes)
        if sequences != list(range(1, len(sequences) + 1)):
            fail(f"noncontiguous outcome sequence for {unit_id}")
    checks.append("71 published outcomes map contiguously to all nine preserved unit IDs")

    assessments = [record for record in records if record["entity_type"] == "assessment"]
    authentic = [record for record in assessments if record["assessment_kind"] == "authentic_delivery"]
    coursebook = [record for record in assessments if record["assessment_kind"] != "authentic_delivery"]
    if len(assessments) != 14 or len(coursebook) != 9 or len(authentic) != 5:
        fail("assessment family counts must be 9 coursebook + 5 authentic")
    if any(not record["required"] or not record["noncompensable"] for record in assessments):
        fail("every assessment must be required and noncompensable")
    if any(not record["calibration_exemplar_required"] for record in authentic):
        fail("every authentic assessment must require a calibration exemplar")
    checks.append("nine coursebook and five authentic assessments are required and noncompensable")

    for assessment in assessments:
        for key in (
            "rubric_id",
            "submission_template_id",
            "attempt_template_id",
            "result_template_id",
        ):
            if assessment[key] not in semantic_by_id:
                fail(f"unresolved {key} on {assessment['id']}")
        for key in ("competency_ids", "outcome_ids", "evaluator_role_ids", "evidence_spec_ids"):
            unresolved = set(assessment[key]) - set(semantic_by_id)
            if unresolved:
                fail(f"unresolved {key} on {assessment['id']}: {sorted(unresolved)}")

    rubrics = [record for record in records if record["entity_type"] == "rubric"]
    criteria = [record for record in records if record["entity_type"] == "criterion"]
    for rubric in rubrics:
        if semantic_by_id[rubric["assessment_id"]]["rubric_id"] != rubric["id"]:
            fail(f"rubric inverse link mismatch: {rubric['id']}")
        if any(identifier not in semantic_by_id for identifier in rubric["criterion_ids"]):
            fail(f"rubric criterion reference unresolved: {rubric['id']}")
        if rubric["scoring"]["mode"] == "numeric_threshold_with_gates":
            if rubric["scoring"]["maximum_total"] != 2 * len(rubric["criterion_ids"]):
                fail(f"numeric rubric maximum mismatch: {rubric['id']}")
            if not set(rubric["scoring"]["required_full_score_criterion_ids"]).issubset(rubric["criterion_ids"]):
                fail(f"numeric rubric gate is not one of its criteria: {rubric['id']}")
    checks.append("rubric, criterion, evidence, submission, attempt, evaluator, and result references close")

    community = semantic_by_id["O017-ASMT-BOUNDED-COMMUNITY-TRANSACTION"]
    if community["external_action_authority"] != "separate_specific_human_authorization_required":
        fail("community transaction lacks separate authority gate")
    if set(community["completion_modes"]) != {"community_transaction", "externally_reviewed_local"}:
        fail("community transaction completion branches are not exact")
    local_complete = semantic_by_id["O017-CREDENTIAL-STATE-COMPLETE-EXTERNALLY-REVIEWED-LOCAL"]
    community_complete = semantic_by_id["O017-CREDENTIAL-STATE-COMPLETE-COMMUNITY-TRANSACTION-EVIDENCED"]
    all_assessment_ids = {record["id"] for record in assessments}
    if set(local_complete["required_assessment_ids"]) != all_assessment_ids:
        fail("externally reviewed local terminal state does not require all assessments")
    if set(community_complete["required_assessment_ids"]) != all_assessment_ids:
        fail("community terminal state does not require all assessments")
    if local_complete["claims_external_participation"] or local_complete["external_event_required"]:
        fail("externally reviewed local branch falsely claims an external event")
    if not community_complete["claims_external_participation"] or not community_complete["external_event_required"]:
        fail("community branch does not require evidenced external participation")
    checks.append("credential branches distinguish externally_reviewed_local from evidenced community transaction")

    if any(record["record_state"] != "template" for record in records if record["entity_type"] in {"submission", "attempt", "evidence", "result"}):
        fail("current operational records must be templates, not learner instances")
    if any(record["record_state"] != "state_definition" for record in records if record["entity_type"] == "credential_state"):
        fail("credential records must be state definitions, not assertions")
    checks.append("zero learner attempts, submissions, results, or credential assertions are claimed")

    relation_header, relation_rows = read_csv(generator.RELATIONS_PATH)
    if relation_header != RELATION_HEADER:
        fail("wrapper relation ledger header mismatch")
    expected_relation_ids = [f"O017-WRAP-REL-{index:04d}" for index in range(1, len(relation_rows) + 1)]
    if [row["id"] for row in relation_rows] != expected_relation_ids:
        fail("wrapper relation IDs are not contiguous in issued order")
    if any(row["status"] != "active" or row["superseded_by"] or row["correction_id"] for row in relation_rows):
        fail("initial wrapper ledger contains a non-active or correction row")
    core_relation_count = 1636
    if len(relation_rows) <= core_relation_count:
        fail("delivery crosswalk extension is absent from the wrapper ledger")
    if any(row["evidence_kind"].endswith("crosswalk") for row in relation_rows[:core_relation_count]):
        fail("delivery crosswalk was inserted into the frozen core relation prefix")
    if any(not row["evidence_kind"].endswith("crosswalk") for row in relation_rows[core_relation_count:]):
        fail("non-crosswalk relation was appended after the frozen core relation prefix")
    core_stream = io.StringIO(newline="")
    core_writer = csv.DictWriter(core_stream, fieldnames=RELATION_HEADER, lineterminator="\n")
    core_writer.writeheader()
    core_writer.writerows(relation_rows[:core_relation_count])
    core_relation_prefix_sha256 = sha256_bytes(core_stream.getvalue().encode("utf-8"))
    triples = [(row["source"], row["predicate"], row["target"]) for row in relation_rows]
    if len(triples) != len(set(triples)):
        fail("duplicate triple in wrapper relation ledger")
    delivery_definitions = json.loads((ROOT / generator.DELIVERY_DEFINITIONS_PATH).read_text(encoding="utf-8"))
    calibration_package = json.loads(
        (ROOT / generator.DELIVERY_CALIBRATION_PACKAGE_PATH).read_text(encoding="utf-8")
    )
    delivery_ids = collect_delivery_ids(delivery_definitions) | collect_delivery_ids(calibration_package)
    endpoint_ids = baseline_ids | set(semantic_ids) | set(localization_ids) | delivery_ids
    for row in relation_rows:
        if row["source"] not in endpoint_ids or row["target"] not in endpoint_ids:
            fail(f"unresolved wrapper relation endpoint: {row['id']}")
    with (ROOT / "backend" / "relations.csv").open(encoding="utf-8", newline="") as stream:
        baseline_active = {(row["source"], row["predicate"], row["target"]) for row in csv.DictReader(stream)}
    if baseline_active & set(triples):
        fail("wrapper relation duplicates an active pre-existing triple")
    triple_set = set(triples)
    delivery_assessments = {
        item["assessment_id"]: item for item in delivery_definitions["assessment_families"]
    }
    for slug, (delivery_id, calibration_id, _) in generator.DELIVERY_BINDINGS.items():
        semantic_assessment_id = f"O017-ASMT-{slug}"
        semantic_rubric_id = f"O017-RUBRIC-{slug}"
        if (semantic_assessment_id, "implemented-by-delivery-definition", delivery_id) not in triple_set:
            fail(f"missing delivery assessment crosswalk: {semantic_assessment_id}")
        if (semantic_assessment_id, "has-calibration-exemplar", calibration_id) not in triple_set:
            fail(f"missing calibration crosswalk: {semantic_assessment_id}")
        for gate_id in delivery_assessments[delivery_id]["required_gate_ids"]:
            if (semantic_rubric_id, "incorporates-delivery-gate", gate_id) not in triple_set:
                fail(f"missing delivery gate crosswalk: {semantic_rubric_id} -> {gate_id}")
    if calibration_package["credit_eligible"] is not False or calibration_package["synthetic_personas"] is not True:
        fail("calibration package truth boundary changed")
    if any(item["actual_completion_claim"] is not False for item in calibration_package["exemplars"]):
        fail("a calibration exemplar makes an actual completion claim")
    delivery_validation = json.loads((ROOT / "delivery" / "VALIDATION.json").read_text(encoding="utf-8"))
    if delivery_validation.get("status") != "PASS" or delivery_validation.get("errors") != []:
        fail("delivery package validation is not a clean PASS")
    checks.append(f"{len(relation_rows):,} new relation rows are unique, endpoint-closed, contiguous, and separate from the preserved ledger")
    checks.append("five neutral assessments crosswalk to delivery definitions, gates, evidence types, and calibration-only exemplars")

    expected_payloads, expected_dataset = generator.build_payloads()
    for relative, expected in expected_payloads.items():
        if (ROOT / relative).read_bytes() != expected:
            fail(f"deterministic generator replay differs: {relative}")
    checks.append("deterministic generator replay reproduces every wrapper byte")

    dataset = json.loads(generator.DATASET_PATH.read_text(encoding="utf-8"))
    if dataset != expected_dataset:
        fail("dataset envelope differs from generated model")
    for item in dataset["files"]:
        path = ROOT / item["path"]
        payload = path.read_bytes()
        if len(payload) != item["bytes"] or sha256_bytes(payload) != item["sha256"]:
            fail(f"dataset inventory mismatch: {item['path']}")
    checks.append("dataset inventory counts, byte lengths, and SHA-256 identities replay")

    negative_tests = negative_schema_tests(validator, records, localizations)
    checks.append("negative tests prove rejection of localized semantic fields, wrong locale, fragment IDs, and incomplete criteria")

    qa_files = [
        generator.BASELINE_PATH,
        generator.SCHEMA_PATH,
        generator.RECORDS_PATH,
        generator.LOCALIZATIONS_PATH,
        generator.RELATIONS_PATH,
        generator.DATASET_PATH,
        ROOT / "backend" / "SEMANTIC_WRAPPER_V1.md",
        ROOT / "scripts" / "generate_semantic_wrapper.py",
        ROOT / "scripts" / "validate_semantic_wrapper.py",
    ]
    qa = {
        "schema": "o017-semantic-wrapper-qa-v1",
        "status": "pass",
        "model_version": generator.MODEL_VERSION,
        "release_version": generator.RELEASE_VERSION,
        "counts": {
            "preserved_backend_records": len(baseline_records),
            "preserved_issued_relations": baseline["files"]["backend/relations-ledger.csv"]["relation_count"],
            "semantic_records": len(records),
            "localized_text_records": len(localizations),
            "wrapper_relations_issued": len(relation_rows),
            "locators_verified": locator_count,
            "authentic_assessment_locator_bindings": authentic_bound_count,
            "by_entity_type": dict(sorted(entity_counts.items())),
        },
        "checks": checks,
        "negative_schema_tests": negative_tests,
        "baseline_invariants": {
            "historical_record_stream_sha256": baseline["files"]["backend/records.jsonl"]["sha256"],
            "current_record_stream_sha256": sha256_bytes(
                (ROOT / "backend" / "records.jsonl").read_bytes()
            ),
            "stable_record_projection_sha256": generator.HISTORICAL_STABLE_RECORD_PROJECTION_SHA256,
            "permitted_version_specific_record_fields": {
                record_id: sorted(fields)
                for record_id, fields in sorted(generator.PERMITTED_BASELINE_RECORD_DELTAS.items())
            },
            "issued_relation_ledger_sha256": baseline["files"]["backend/relations-ledger.csv"]["sha256"],
            "issued_relation_map_sha256": baseline["files"]["backend/relations-ledger.csv"]["issued_map_sha256"],
            "existing_ledger_rewritten": False,
            "wrapper_core_relation_prefix_count": core_relation_count,
            "wrapper_core_relation_prefix_sha256": core_relation_prefix_sha256,
            "delivery_crosswalk_rows_appended": len(relation_rows) - core_relation_count,
        },
        "claim_boundary": {
            "learner_submission_instances": 0,
            "learner_attempt_instances": 0,
            "learner_result_instances": 0,
            "credential_assertion_instances": 0,
            "community_participation_claimed_for_any_learner": False,
        },
        "integration": {
            "semantic_model_complete": True,
            "published_unit_locators_bound": True,
            "authentic_delivery_locators_bound": authentic_bound_count == 5,
            "remaining_requirement": None,
        },
        "files": [file_identity(path) for path in qa_files],
    }
    qa_payload = generator.canonical_json(qa, pretty=True)
    if args.write_qa:
        QA_PATH.write_bytes(qa_payload)

    print(
        f"PASS: {len(records)} semantic records, {len(localizations)} id-ID localizations, "
        f"{len(relation_rows)} append-only wrapper relations, {locator_count} verified locators"
    )
    if authentic_bound_count == 0:
        print("INTEGRATION: authentic delivery/calibration source locators remain to be bound")
    if args.write_qa:
        print(f"QA: {QA_PATH.relative_to(ROOT).as_posix()} {len(qa_payload)} bytes {sha256_bytes(qa_payload)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
