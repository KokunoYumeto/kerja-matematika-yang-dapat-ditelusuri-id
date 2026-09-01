#!/usr/bin/env python3
"""Build/check the additive English O017 backend without editing Indonesian inputs.

Run from any directory: python english_backend.py [--check] [--allow-incomplete-sources].
The first build snapshots only the explicitly enumerated upstream backend files.
Later builds verify those immutable bytes before reusing them. A packaged English
edition is self-contained: it rebuilds from backend/upstream-id-ID plus the three
authored translation maps and English source files.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "backend"
UP = B / "upstream-id-ID"
ORIGINAL = ROOT.parent / "backend"
NAMES = (
    "schema.json", "records.jsonl", "relations.csv", "relations-ledger.csv",
    "semantic-wrapper-v1.schema.json", "semantic-wrapper-v1.records.jsonl",
    "semantic-wrapper-v1.localizations.jsonl", "semantic-wrapper-v1.relations-ledger.csv",
    "semantic-wrapper-v1.baseline.json", "semantic-wrapper-v1.dataset.json",
    "SEMANTIC_WRAPPER_V1.md",
)
UNIT_FILES = (
    "01-membaca-argumen.qmd", "02-menelusuri-sumber.qmd",
    "03-merekonstruksi-pembuktian.qmd", "04-sitasi-provenance-catatan-sumber.qmd",
    "05-eksposisi-matematika.qmd", "06-komputasi-dapat-direproduksi.qmd",
    "07-errata-koreksi-batas-kepastian.qmd", "08-seminar-penelaah-tanggapan-kritik.qmd",
    "09-kontribusi-komunitas-portofolio.qmd",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def obj(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def jbytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def jlbytes(value) -> bytes:
    return b"".join((json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8") for v in value)


def csvbytes(values, fields) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(values)
    return output.getvalue().encode("utf-8")


def enid(value: str) -> str:
    assert value.startswith("O017-L10N-ID-")
    return value.replace("O017-L10N-ID-", "O017-L10N-EN-", 1)


def prepare_snapshot(check: bool):
    path = B / "upstream-id-ID.manifest.json"
    if not path.exists():
        if check:
            raise RuntimeError("Missing immutable upstream snapshot; build once first")
        UP.mkdir(parents=True, exist_ok=True)
        entries = []
        for name in NAMES:
            data = (ORIGINAL / name).read_bytes()
            destination = UP / name
            if destination.exists() and destination.read_bytes() != data:
                raise RuntimeError(f"Refusing to overwrite differing upstream snapshot: {name}")
            destination.write_bytes(data)
            entries.append({"path": name, "bytes": len(data), "sha256": sha(data)})
        path.write_bytes(jbytes({"schema": "o017-english-upstream-snapshot-v1", "files": entries}))
    frozen = obj(path)
    assert {x["path"] for x in frozen["files"]} == set(NAMES)
    for entry in frozen["files"]:
        data = (UP / entry["path"]).read_bytes()
        assert len(data) == entry["bytes"] and sha(data) == entry["sha256"], entry["path"]
        original_path = ORIGINAL / entry["path"]
        if original_path.exists():
            assert original_path.read_bytes() == data, f"Original differs from frozen snapshot: {entry['path']}"
    return frozen


def all_translations(localizations):
    translated = {}
    for name in ("translations-a.json", "translations-b.json"):
        shard = obj(B / name)
        assert not set(translated).intersection(shard), "Duplicate authored translation keys"
        translated.update(shard)
    originals = {r["id"]: r for r in localizations}
    assert not (set(translated) - set(originals)), "Translation key absent from original"
    # Shared source strings get one consistent translation; evidence definitions
    # intentionally repeat the corresponding criterion, rather than abridging it.
    text_map = {}
    for key, text in translated.items():
        source = originals[key]["text"]
        if source in text_map:
            assert text_map[source] == text, f"Inconsistent translation: {key}"
        text_map[source] = text
    for row in localizations:
        key = row["id"]
        if key in translated:
            continue
        if row["text"] in text_map:
            translated[key] = text_map[row["text"]]
        elif key.startswith("O017-L10N-ID-EVIDENCE-"):
            crit = key.replace("-EVIDENCE-", "-CRIT-", 1)
            if row["field"] == "description":
                crit = crit.removesuffix("-DESCRIPTION") + "-CRITERION-TEXT"
                translated[key] = translated[crit]
            elif row["field"] == "label":
                translated[key] = "Evidence for " + translated[crit]
            else:
                raise RuntimeError(key)
        elif "-RESULT-TEMPLATE-" in key:
            if row["field"] == "instructions":
                translated[key] = "Keep the status, evaluator, rubric basis, evidence, and unresolved issues; external statuses must have event evidence."
            else:
                assessment = key.replace("-RESULT-TEMPLATE-", "-ASMT-", 1)
                translated[key] = "Assessment result — " + translated[assessment]
        elif "-SUBMISSION-TEMPLATE-" in key:
            if row["field"] == "instructions":
                translated[key] = "Use new attempt and evidence IDs; preserve all previous versions and do not overwrite artifacts or statuses."
            else:
                assessment = key.replace("-SUBMISSION-TEMPLATE-", "-ASMT-", 1)
                translated[key] = "Submission package — " + translated[assessment]
        elif "-RUBRIC-" in key:
            if row["field"] == "pass_rule":
                translated[key] = "All mandatory criteria must be met; one unmet criterion requires revision."
            else:
                assessment = key.replace("-RUBRIC-", "-ASMT-", 1)
                translated[key] = "Rubric — " + translated[assessment]
        else:
            raise RuntimeError(f"Untranslated localization: {key}")
    assert len(translated) == len(localizations) == 581
    assert all(isinstance(x, str) and x.strip() for x in translated.values())
    return translated


def build(check=False, allow_incomplete=False):
    frozen = prepare_snapshot(check)
    neutral = rows(UP / "semantic-wrapper-v1.records.jsonl")
    original_l10n = rows(UP / "semantic-wrapper-v1.localizations.jsonl")
    core = rows(UP / "records.jsonl")
    translations = all_translations(original_l10n)
    english = [{**r, "id": enid(r["id"]), "locale": "en", "language": "en", "text": translations[r["id"]]} for r in original_l10n]
    for source, target in zip(original_l10n, english):
        for pattern in (r"\$[^$]+\$", r"`[^`]+`"):
            assert re.findall(pattern, source["text"]) == re.findall(pattern, target["text"]), f"Mathematics/code token mismatch: {source['id']}"
    bilingual = []
    english_selection = []
    for record in neutral:
        bilingual.append({**record, "localization_ids": record["localization_ids"] + [enid(x) for x in record["localization_ids"]]})
        english_selection.append({**record, "localization_ids": [enid(x) for x in record["localization_ids"]]})
    schema = obj(UP / "semantic-wrapper-v1.schema.json")
    schema["$id"] = "urn:o017:semantic-wrapper:v1:english-access"
    schema["title"] = "O017 semantic wrapper v1, additive English-access schema"
    schema["$defs"]["localization_id"]["pattern"] = "^O017-L10N-(?:ID|EN)-[A-Z0-9][A-Z0-9-]*$"
    lp = schema["$defs"]["localized_text"]["properties"]
    lp["locale"] = {"enum": ["id-ID", "en"]}
    lp["language"] = {"enum": ["id", "en"]}
    schema["$defs"]["localized_text"]["allOf"] = [
        {"if": {"properties": {"locale": {"const": "en"}}}, "then": {"properties": {"language": {"const": "en"}, "id": {"pattern": "^O017-L10N-EN-"}}}},
        {"if": {"properties": {"locale": {"const": "id-ID"}}}, "then": {"properties": {"language": {"const": "id"}, "id": {"pattern": "^O017-L10N-ID-"}}}},
    ]
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for record in bilingual + english_selection + original_l10n + english:
        validator.validate(record)
    invalid = copy.deepcopy(english[0]); invalid["language"] = "id"
    assert list(validator.iter_errors(invalid)), "Cross-language mismatch was not rejected"

    # Core labels and titles are additive localized fields, not rewrites of
    # historical edition/artifact/QA records or a laundering of their old hashes.
    core_map = obj(B / "core-translations.json")
    core_l10n = []
    for record in core:
        for field in ("title", "label_id", "preferred_id"):
            if field not in record:
                continue
            original_text = record[field]
            if field in ("label_id", "preferred_id") or original_text in core_map:
                assert original_text in core_map, f"Missing core translation: {record['id']} {field}"
                text = core_map[original_text]
                disposition = "translated_original"
            else:
                text = original_text
                disposition = "reused_existing_english"
            core_l10n.append({
                "schema": "o017-core-localization-v1", "id": f"O017-CORE-L10N-EN-{record['id']}-{field.upper().replace('_', '-')}",
                "subject_id": record["id"], "field": field, "locale": "en", "language": "en", "text": text,
                "source_text": original_text, "source_language": "en" if disposition == "reused_existing_english" else "id",
                "disposition": disposition,
            })
    core_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:o017:core-localization:v1:en",
        "title": "English localization of an existing O017 core title or label",
        "type": "object", "additionalProperties": False,
        "required": ["schema", "id", "subject_id", "field", "locale", "language", "text", "source_text", "source_language", "disposition"],
        "properties": {
            "schema": {"const": "o017-core-localization-v1"},
            "id": {"type": "string", "pattern": "^O017-CORE-L10N-EN-[A-Z0-9-]+$"},
            "subject_id": {"type": "string", "minLength": 1},
            "field": {"enum": ["title", "label_id", "preferred_id"]},
            "locale": {"const": "en"}, "language": {"const": "en"},
            "text": {"type": "string", "minLength": 1}, "source_text": {"type": "string", "minLength": 1},
            "source_language": {"enum": ["en", "id"]},
            "disposition": {"enum": ["translated_original", "reused_existing_english"]},
        },
        "allOf": [{"if": {"properties": {"disposition": {"const": "reused_existing_english"}}}, "then": {"properties": {"source_language": {"const": "en"}}}, "else": {"properties": {"source_language": {"const": "id"}}}}],
    }
    Draft202012Validator.check_schema(core_schema)
    core_validator = Draft202012Validator(core_schema)
    for record in core_l10n:
        core_validator.validate(record)
        assert record["subject_id"] in {r["id"] for r in core}

    source_cache = {}
    source_errors = []
    for number, filename in enumerate(UNIT_FILES, 1):
        path = ROOT / "source" / "units" / filename
        if path.exists():
            source_cache[f"O017-U{number:02d}"] = path.read_text(encoding="utf-8-sig")
        else:
            source_errors.append(f"Missing source/units/{filename}")
    core_access = []
    for record in core:
        unit = record.get("unit") or (record["id"] if record["entity_type"] == "unit" else None)
        if unit not in {f"O017-U{x:02d}" for x in range(1, 10)}:
            continue
        if "html_fragment" not in record and record["entity_type"] != "unit":
            continue
        filename = UNIT_FILES[int(unit[-2:]) - 1]
        fragment = record.get("html_fragment", "")
        if fragment and unit in source_cache and not re.search(r"[#{]" + re.escape(fragment) + r"(?:[\s}.\"]|$)", source_cache[unit]):
            source_errors.append(f"Missing core anchor {record['id']} {fragment}")
        core_access.append({"subject_id": record["id"], "unit_id": unit, "locale": "en", "source_path": "source/units/" + filename,
                            "reader_path": "build/html/units/" + filename.replace(".qmd", ".html"), "fragment": fragment, "canonical_identity": False})
    for record in english_selection:
        for locator in record.get("locators", []):
            path = ROOT / locator["path"]
            if not path.exists():
                source_errors.append("Missing semantic locator file " + locator["path"])
            elif not re.search(r"[#{]" + re.escape(locator["fragment"]) + r"(?:[\s}.\"]|$)", path.read_text(encoding="utf-8-sig")):
                source_errors.append("Missing semantic anchor " + locator["path"] + "#" + locator["fragment"])
    source_errors = sorted(set(source_errors))
    if source_errors and not allow_incomplete:
        raise RuntimeError("English source locator checks failed: " + "; ".join(source_errors))

    crosswalk = [{"subject_id": r["subject_id"], "field": r["field"], "id_ID_localization_id": r["id"], "en_localization_id": enid(r["id"])} for r in original_l10n]
    new_relations = [{"id": "O017-EN-REL-" + r["id"].removeprefix("O017-L10N-ID-"), "source": r["subject_id"], "predicate": "has-localized-text", "target": enid(r["id"]), "status": "active"} for r in original_l10n]
    original_relations = list(csv.DictReader(io.StringIO((UP / "semantic-wrapper-v1.relations-ledger.csv").read_text(encoding="utf-8-sig"))))
    core_relations = list(csv.DictReader(io.StringIO((UP / "relations-ledger.csv").read_text(encoding="utf-8-sig"))))
    assert len({r["id"] for r in neutral}) == len(neutral) == 319
    assert {r["id"] for r in neutral} == {r["id"] for r in english_selection}
    assert {r["subject_id"] for r in english} == {r["subject_id"] for r in original_l10n}
    assert len({r["id"] for r in english}) == len(english) == 581
    assert all({k: v for k, v in a.items() if k != "localization_ids"} == {k: v for k, v in b.items() if k != "localization_ids"} for a, b in zip(neutral, english_selection))
    semantic_ids = {r["id"] for r in neutral}
    core_ids = {r["id"] for r in core}
    known = semantic_ids | core_ids | {r["id"] for r in original_l10n + english}
    # Original delivery crosswalk endpoints are intentionally external to the
    # semantic stream, and retain their issued delivery IDs unchanged.
    delivery_ids = {r[x] for r in original_relations for x in ("source", "target") if r[x].startswith("O017-WRAP-")}
    assert all(r["source"] in known | delivery_ids and r["target"] in known | delivery_ids for r in original_relations)
    assert all(r["source"] in known and r["target"] in known for r in new_relations)

    outputs = {
        "backend/semantic-wrapper-v1.schema.json": jbytes(schema),
        "backend/semantic-wrapper-v1.records.jsonl": jlbytes(bilingual),
        "backend/semantic-wrapper-v1.records.en.jsonl": jlbytes(english_selection),
        "backend/semantic-wrapper-v1.localizations.en.jsonl": jlbytes(english),
        "backend/semantic-wrapper-v1.localizations.jsonl": (UP / "semantic-wrapper-v1.localizations.jsonl").read_bytes() + jlbytes(english),
        "backend/semantic-wrapper-v1.localizations.id-ID.jsonl": (UP / "semantic-wrapper-v1.localizations.jsonl").read_bytes(),
        "backend/semantic-wrapper-v1.relations-ledger.csv": (UP / "semantic-wrapper-v1.relations-ledger.csv").read_bytes(),
        "backend/relations.csv": (UP / "relations.csv").read_bytes(),
        "backend/relations-ledger.csv": (UP / "relations-ledger.csv").read_bytes(),
        "backend/records.jsonl": (UP / "records.jsonl").read_bytes(),
        "backend/schema.json": (UP / "schema.json").read_bytes(),
        "backend/core-localizations.en.jsonl": jlbytes(core_l10n),
        "backend/core-localizations.schema.json": jbytes(core_schema),
        "backend/english-access-locators.jsonl": jlbytes(core_access),
        "backend/localization-crosswalk.csv": csvbytes(crosswalk, ["subject_id", "field", "id_ID_localization_id", "en_localization_id"]),
        "backend/english-localization-relations.csv": csvbytes(new_relations, ["id", "source", "predicate", "target", "status"]),
    }
    language_index = {
        "schema": "o017-language-selection-v1", "course_id": "O017-D120", "default_locale": "en",
        "semantic_entities_are_locale_neutral": True,
        "locales": {
            "en": {"semantic_records": "backend/semantic-wrapper-v1.records.en.jsonl", "semantic_text": "backend/semantic-wrapper-v1.localizations.en.jsonl", "core_text": "backend/core-localizations.en.jsonl", "locators": "backend/english-access-locators.jsonl", "reader": "build/html/index.html", "source": "source/index.qmd"},
            "id-ID": {"semantic_records": "backend/upstream-id-ID/semantic-wrapper-v1.records.jsonl", "semantic_text": "backend/semantic-wrapper-v1.localizations.id-ID.jsonl", "preserved_original_record_stream": "backend/upstream-id-ID/records.jsonl", "reader_is_outside_english_package": True},
        },
        "crosswalk": "backend/localization-crosswalk.csv", "missing_translation_behavior": "error; never silently fall back to another language",
        "historical_artifact_hashes": "Original records.jsonl artifact paths and hashes identify the Indonesian release only; use English manifest and access locators for this edition.",
    }
    outputs["backend/languages.json"] = jbytes(language_index)
    dataset = {
        "schema": "o017-english-backend-dataset-v1", "course_id": "O017-D120", "locale": "en",
        "counts": {"core_records_preserved": len(core), "semantic_entities": len(neutral), "english_semantic_localizations": len(english), "indonesian_semantic_localizations_preserved": len(original_l10n), "english_core_localizations": len(core_l10n), "core_relation_ids_preserved": len(core_relations), "semantic_relation_ids_preserved": len(original_relations), "additive_english_localization_relations": len(new_relations), "english_access_locators": len(core_access)},
        "claim_boundary": {"original_indonesian_edition_unchanged": True, "definitions_and_templates_only": True, "learner_completion_instances": 0, "donor_english_retranslated": False, "semantic_ids_fully_localized": True, "partial_unit_mapping_only": False},
        "inputs": [{"path": "backend/" + n, "bytes": (B / n).stat().st_size, "sha256": sha((B / n).read_bytes())} for n in ("translations-a.json", "translations-b.json", "core-translations.json", "upstream-id-ID.manifest.json")],
        "preserved_upstream_files": frozen["files"],
        "outputs": [{"path": p, "bytes": len(d), "sha256": sha(d)} for p, d in sorted(outputs.items())],
    }
    outputs["backend/english-backend.dataset.json"] = jbytes(dataset)
    qa = {
        "schema": "o017-english-backend-qa-v1", "status": "pass" if not source_errors else "incomplete-source-locators",
        "checks": {"immutable_upstream_hashes": True, "neutral_semantic_id_parity": True, "neutral_semantic_fields_unchanged": True, "issued_relation_ids_and_bytes_preserved": True, "all_581_localizations_have_english_equivalents": True, "all_581_indonesian_localizations_preserved": True, "all_core_titles_concepts_and_terms_localized_or_existing_english": True, "schema_metavalidation": True, "all_semantic_and_localization_rows_validate": True, "locale_mismatch_negative_test": True, "inline_mathematics_and_code_tokens_preserved": True, "relation_endpoint_resolution": True, "english_source_locators": not source_errors},
        "counts": dataset["counts"], "source_locator_errors": source_errors,
        "unfinished_translation_fields": [], "reader_html_render_verification": "performed by release QA, not this source/backend check",
        "dataset_sha256": sha(outputs["backend/english-backend.dataset.json"]),
    }
    outputs["qa/ENGLISH_BACKEND_QA.json"] = jbytes(qa)
    for relative, data in outputs.items():
        destination = ROOT / relative
        if check:
            assert destination.read_bytes() == data, f"Generated bytes differ: {relative}"
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    print(json.dumps({"status": qa["status"], "mode": "check" if check else "build", "counts": qa["counts"], "source_locator_errors": source_errors}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--allow-incomplete-sources", action="store_true", help="Development only: emit explicit incomplete-source QA; not release-pass")
    args = parser.parse_args()
    build(args.check, args.allow_incomplete_sources)
