"""Course-wide deterministic build and per-unit admission pipeline for O017.

The pipeline renders every registered unit, reruns every registered unit's
static gates, emits one aggregate locale-neutral backend, and writes the
requested unit's hash-bound receipt.  Unit-specific facts live in
``o017_specs.py``; this module does not allocate identifiers.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable, Mapping
from urllib.parse import unquote, urlsplit

from o017_specs import COURSE, CourseSpec, RelationSpec, UnitSpec, record


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
BUILD = ROOT / "build"
HTML_ROOT = BUILD / "html"
BACKEND = ROOT / "backend"
QA = ROOT / "qa"
INDEX_RELATIVE_PATH = Path("index.html")


def fail(message: str) -> None:
    raise RuntimeError(message)


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            value.update(chunk)
    return value.hexdigest()


def digest_bytes(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def canonical_rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def compact_jsonl(records: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record_value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record_value in records
    ).encode("utf-8")


def csv_payload(header: tuple[str, ...], rows: Iterable[Iterable[Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run_checked(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        fail(
            f"command failed ({result.returncode}): {command!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


@dataclass(frozen=True)
class HtmlDocument:
    path: Path
    ids: frozenset[str]
    refs: tuple[tuple[str, str], ...]
    language: str | None
    text: str


class ReaderParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []
        self.language: str | None = None
        self.text_parts: list[str] = []
        self.inert_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "template"}:
            self.inert_depth += 1
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        if values.get("id"):
            self.ids.add(str(values["id"]))
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.refs.append((attribute, value))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "template"} and self.inert_depth:
            self.inert_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.inert_depth:
            self.text_parts.append(data)


def parse_html(path: Path) -> HtmlDocument:
    parser = ReaderParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return HtmlDocument(
        path=path,
        ids=frozenset(parser.ids),
        refs=tuple(parser.refs),
        language=parser.language,
        text=" ".join(" ".join(parser.text_parts).split()),
    )


def verify_local_links(documents: Mapping[Path, HtmlDocument]) -> tuple[int, int]:
    checked = 0
    fragments = 0
    for document in documents.values():
        for attribute, raw in document.refs:
            split = urlsplit(raw)
            if split.scheme or split.netloc or raw.startswith(("mailto:", "data:", "javascript:")):
                continue
            if not split.path and not split.fragment:
                continue
            decoded = unquote(split.path)
            target = (document.path.parent / decoded).resolve() if decoded else document.path
            if split.path.endswith("/"):
                target = target / "index.html"
            if split.path and not target.exists():
                fail(f"missing local {attribute} target in {document.path}: {raw}")
            checked += 1
            if split.fragment:
                fragments += 1
                if target.suffix.lower() in {".html", ".htm"}:
                    target_doc = documents.get(target)
                    if target_doc is None:
                        target_doc = parse_html(target)
                    if split.fragment not in target_doc.ids:
                        fail(f"missing fragment #{split.fragment} from {document.path} to {target}")
    return checked, fragments


def finalize_html_outputs(paths: Iterable[Path]) -> None:
    skip_link = (
        '<a class="o017-skip-link" href="#quarto-document-content">'
        "Langsung ke isi utama</a>"
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if skip_link not in text:
            text, count = re.subn(r"(<body\b[^>]*>)", rf"\1\n{skip_link}", text, count=1)
            if count != 1:
                fail(f"could not insert skip link into {path}")
        text = text.replace(
            'aria-controls="navbarCollapse" role="menu"',
            'aria-controls="navbarCollapse"',
        )
        text = text.replace(
            '<nav id="TOC" role="doc-toc" class="toc-active">',
            '<nav id="TOC" role="doc-toc" class="toc-active" aria-labelledby="toc-title">',
        )
        text = re.sub(
            r'<h2 id="toc-title">([^<]+)</h2>',
            r'<div id="toc-title" class="h2">\1</div>',
            text,
            count=1,
        )
        text = re.sub(
            r'<div class="(o017-(?:table|math)-scroll)"(?![^>]*\brole=)([^>]*)>',
            r'<div class="\1" role="region"\2>',
            text,
        )
        text = re.sub(
            r'(<div class="o017-table-scroll"[^>]*aria-label="([^"]+)"[^>]*>\s*<table)'
            r'(?![^>]*\baria-label=)([^>]*)>',
            r'\1 aria-label="\2"\3>',
            text,
        )
        if re.search(r'<(?:script|link)\b[^>]+(?:src|href)=["\']https://', text):
            fail(f"remote runtime dependency remains in {path}")
        write_bytes(path, text.encode("utf-8"))


def verify_offline_css(paths: Iterable[Path]) -> None:
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r'(?:@import\s*|url\()["\']?https?://', text, flags=re.IGNORECASE):
            fail(f"remote stylesheet dependency remains in {path}")


@dataclass(frozen=True)
class UnitCheck:
    unit: UnitSpec
    html_path: Path
    document: HtmlDocument
    computation_results: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class BackendBuild:
    records_payload: bytes
    relations_payload: bytes
    relations_ledger_payload: bytes
    schema_payload: bytes
    record_count: int
    relation_count: int
    active_relation_count: int
    superseded_relation_count: int
    stable_relation_map_sha256: str
    active_relation_map_sha256: str
    relation_ledger_sha256: str
    unit_records_sha256: Mapping[str, str]
    unit_relations_sha256: Mapping[str, str]


def relation_map_payload(relations: Iterable[RelationSpec]) -> bytes:
    return "".join(
        f"{item.id}\t{item.source}\t{item.predicate}\t{item.target}\n"
        for item in sorted(relations, key=lambda value: value.id)
    ).encode("utf-8")


def relation_record(value: RelationSpec) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "source": value.source,
        "predicate": value.predicate,
        "target": value.target,
        "status": value.status,
    }
    if value.evidence_kind is not None:
        fields["evidence_kind"] = value.evidence_kind
    if value.superseded_by is not None:
        fields["superseded_by"] = value.superseded_by
    if value.correction_id is not None:
        fields["correction_id"] = value.correction_id
    return record("relation", value.id, **fields)


def id_type_payload(records: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        f"{value['id']}\t{value['entity_type']}\n"
        for value in sorted(records, key=lambda item: str(item["id"]))
    ).encode("utf-8")


def build_backend(
    course: CourseSpec,
    unit_hashes: Mapping[str, Mapping[str, str]],
) -> BackendBuild:
    records = [dict(value) for value in course.common_records]
    unit_record_sets: dict[str, tuple[dict[str, Any], ...]] = {}
    for unit in course.units:
        unit_records = unit.records_factory(unit_hashes[unit.id])
        unit_record_sets[unit.id] = unit_records
        records.extend(dict(value) for value in unit_records)

    relations = [*course.common_relations]
    for unit in course.units:
        if unit.id != "O017-U01":
            relation_prefix = f"{unit.id}-REL-"
            misnamespaced = sorted(
                item.id for item in unit.relations if not item.id.startswith(relation_prefix)
            )
            if misnamespaced:
                fail(f"unit relation IDs are not namespaced for {unit.id}: {misnamespaced}")
        if unit.id == "O017-U02" and any(
            item.evidence_kind is None for item in unit.relations
        ):
            fail("Unit 2 relations must distinguish their evidence kind")
        relations.extend(unit.relations)

    relation_ids = [item.id for item in relations]
    if len(set(relation_ids)) != len(relation_ids):
        fail("duplicate explicit relation ID")
    relation_triples = [(item.source, item.predicate, item.target) for item in relations]
    if len(set(relation_triples)) != len(relation_triples):
        fail("duplicate backend relation triple")
    relation_by_id = {item.id: item for item in relations}
    for item in relations:
        if item.status not in {"active", "superseded"}:
            fail(f"unsupported relation status for {item.id}: {item.status}")
        if item.status == "active" and (item.superseded_by or item.correction_id):
            fail(f"active relation declares supersession metadata: {item.id}")
        if item.status == "superseded":
            if not item.superseded_by or not item.correction_id:
                fail(f"superseded relation lacks replacement/correction: {item.id}")
            replacement = relation_by_id.get(item.superseded_by)
            if replacement is None or replacement.status != "active":
                fail(f"superseded relation has invalid active replacement: {item.id}")
            if replacement.source != item.source or replacement.predicate != item.predicate:
                fail(f"replacement changes relation subject or predicate: {item.id}")
            if replacement.target == item.target:
                fail(f"replacement does not correct relation target: {item.id}")

    entity_ids = {value["id"] for value in records}
    if len(entity_ids) != len(records):
        duplicates = sorted(
            identifier
            for identifier in entity_ids
            if sum(value["id"] == identifier for value in records) > 1
        )
        fail(f"duplicate backend record ID: {duplicates}")
    dangling = sorted(
        {endpoint for item in relations for endpoint in (item.source, item.target)} - entity_ids
    )
    if dangling:
        fail(f"dangling backend relation endpoints: {dangling}")

    for value in records:
        if value.get("schema") != "o017-backend-record-v1":
            fail(f"wrong record schema for {value.get('id')}")
        if value.get("entity_type") not in course.entity_classes:
            fail(f"unsupported entity type for {value.get('id')}")
        identifier = str(value.get("id", ""))
        pid = str(value.get("pid", ""))
        classroom_identifier = identifier.startswith("PID-KELAS-") or pid.startswith(
            "PID-KELAS-"
        )
        if classroom_identifier and (
            value.get("synthetic") is not True or value.get("public_pid") is not False
        ):
            fail(f"classroom identifier lacks synthetic/non-public disclosure: {identifier}")
        if value.get("entity_type") == "source" and value.get("synthetic") is True:
            dimensions = value.get("authority_dimensions")
            expected_dimensions = {
                "proximity",
                "version_traceability",
                "provenance",
                "locator",
                "support",
            }
            if not isinstance(dimensions, dict) or set(dimensions) != expected_dimensions:
                fail(f"synthetic source lacks complete authority dimensions: {identifier}")
            unresolved = value.get("unresolved_fields")
            if not isinstance(unresolved, list) or any(
                not isinstance(field, str) or not field for field in unresolved
            ):
                fail(f"synthetic source has invalid unresolved_fields: {identifier}")
            if len(set(unresolved)) != len(unresolved):
                fail(f"synthetic source repeats an unresolved field: {identifier}")

    for item in relations:
        if item.predicate == "likely-used-version" and item.evidence_kind != "inference":
            fail(f"likely-used-version relation is not marked as inference: {item.id}")

    triples = {
        (item.source, item.predicate, item.target)
        for item in relations
        if item.status == "active"
    }
    by_id = {value["id"]: value for value in records}
    active_identifies: dict[str, list[RelationSpec]] = {}
    for item in relations:
        if item.status == "active" and item.predicate == "identifies":
            active_identifies.setdefault(item.source, []).append(item)
    supported_identity_scopes = {
        "repository-commit",
        "published-book",
        "published-release",
    }
    for citation in records:
        if citation.get("entity_type") != "citation" or "identity_scope" not in citation:
            continue
        citation_id = str(citation["id"])
        scope = citation.get("identity_scope")
        if scope not in supported_identity_scopes:
            fail(f"unsupported citation identity scope for {citation_id}: {scope}")
        identifying = active_identifies.get(citation_id, [])
        if len(identifying) != 1:
            fail(f"scoped citation must have exactly one active identity target: {citation_id}")
        target = by_id[identifying[0].target]
        if target.get("entity_type") != "source" or target.get("identity_scope") != scope:
            fail(f"citation/source identity scopes do not match: {identifying[0].id}")
        if scope == "repository-commit":
            citation_commit = str(citation.get("commit", ""))
            target_commit = str(target.get("commit", ""))
            if (
                len(citation_commit) != 40
                or any(char not in "0123456789abcdef" for char in citation_commit)
                or citation_commit != target_commit
            ):
                fail(f"repository-commit identity mismatch: {identifying[0].id}")
        elif scope == "published-book":
            if not citation.get("isbn") or citation.get("isbn") != target.get("isbn"):
                fail(f"published-book identity mismatch: {identifying[0].id}")
        elif scope == "published-release":
            if not citation.get("version") or citation.get("version") != target.get("version"):
                fail(f"published-release version mismatch: {identifying[0].id}")
            if citation.get("doi_scope") != target.get("doi_scope"):
                fail(f"published-release DOI scope mismatch: {identifying[0].id}")
            if citation.get("doi") != target.get("concept_doi"):
                fail(f"published-release concept DOI mismatch: {identifying[0].id}")

    declared_correction_pairs: set[tuple[str, str]] = set()
    for item in relations:
        if item.status != "superseded":
            continue
        correction = by_id.get(str(item.correction_id))
        if (
            correction is None
            or correction.get("entity_type") != "correction"
            or correction.get("correction_kind") != "relation-supersession"
            or correction.get("status") != "applied"
        ):
            fail(f"superseded relation lacks an applied correction record: {item.id}")
        replacements = correction.get("replacements")
        expected_pair = {
            "issued_relation_id": item.id,
            "replacement_relation_id": item.superseded_by,
        }
        if not isinstance(replacements, list) or expected_pair not in replacements:
            fail(f"correction record does not bind the supersession pair: {item.id}")
        declared_correction_pairs.add((item.id, str(item.superseded_by)))
    recorded_correction_pairs: set[tuple[str, str]] = set()
    for value in records:
        if value.get("correction_kind") != "relation-supersession":
            continue
        replacements = value.get("replacements")
        if not isinstance(replacements, list):
            fail(f"relation-supersession correction lacks replacements: {value['id']}")
        for replacement in replacements:
            if not isinstance(replacement, dict) or set(replacement) != {
                "issued_relation_id",
                "replacement_relation_id",
            }:
                fail(f"invalid relation-supersession pair in {value['id']}")
            recorded_correction_pairs.add(
                (
                    str(replacement["issued_relation_id"]),
                    str(replacement["replacement_relation_id"]),
                )
            )
    if recorded_correction_pairs != declared_correction_pairs:
        fail("correction records and superseded relation mappings differ")
    for unit in course.units:
        for exercise_id, solution_id in unit.exercise_solution_pairs:
            if by_id.get(exercise_id, {}).get("entity_type") != "exercise":
                fail(f"missing exercise record {exercise_id}")
            if by_id.get(solution_id, {}).get("entity_type") != "solution":
                fail(f"missing solution record {solution_id}")
            if (exercise_id, "guided-by", solution_id) not in triples:
                fail(f"missing exercise-guidance relation {exercise_id} -> {solution_id}")

    for value in records:
        identifier = value["id"]
        entity_type = value["entity_type"]
        if entity_type == "source" and value.get("identity_scope") in supported_identity_scopes:
            if not any(
                item.status == "active"
                and item.source == identifier
                and item.predicate == "governed-by"
                for item in relations
            ):
                fail(f"scoped source identity lacks an active rights relation: {identifier}")
        if entity_type == "asset":
            if not any(item.source == identifier and item.predicate == "licensed-by" for item in relations):
                fail(f"asset lacks component-rights relation: {identifier}")

    records.extend(relation_record(item) for item in relations)
    records.sort(key=lambda value: value["id"])
    if len({value["id"] for value in records}) != len(records):
        fail("relation ID collides with an entity record ID")

    records_payload = compact_jsonl(records)
    active_relations = tuple(item for item in relations if item.status == "active")
    relations_payload = csv_payload(
        ("source", "predicate", "target"),
        (
            (
                item.source,
                item.predicate,
                item.target,
            )
            for item in sorted(
                active_relations,
                key=lambda value: (value.source, value.predicate, value.target, value.id),
            )
        ),
    )
    relations_ledger_payload = csv_payload(
        (
            "id",
            "source",
            "predicate",
            "target",
            "status",
            "evidence_kind",
            "superseded_by",
            "correction_id",
        ),
        (
            (
                item.id,
                item.source,
                item.predicate,
                item.target,
                item.status,
                item.evidence_kind or "",
                item.superseded_by or "",
                item.correction_id or "",
            )
            for item in sorted(relations, key=lambda value: value.id)
        ),
    )
    if any(
        f"{item.source},{item.predicate},{item.target}".encode("utf-8")
        in relations_payload
        for item in relations
        if item.status == "superseded"
    ):
        fail("active relations.csv contains a superseded triple")
    for item in relations:
        if item.status == "superseded" and item.id.encode("utf-8") not in relations_ledger_payload:
            fail(f"issued ledger dropped superseded relation: {item.id}")
    schema = {
        "schema": "o017-backend-envelope-v2",
        "encoding": "UTF-8",
        "record_serialization": "one canonical compact JSON object per LF-terminated line",
        "id_policy": "stable locale-neutral IDs; locale is an edition/field property",
        "entity_classes": list(course.entity_classes),
        "relation_columns": ["source", "predicate", "target"],
        "relation_ledger_columns": [
            "id", "source", "predicate", "target", "status", "evidence_kind",
            "superseded_by", "correction_id",
        ],
        "relation_count_semantics": "relation_count is the number of all issued relations retained in records.jsonl and relations-ledger.csv",
        "relation_status_policy": "superseded relations preserve their issued ID/triple in the ledger and records, while relations.csv exposes only the active semantic graph",
    }
    unit_records_sha256 = {
        unit.id: digest_bytes(
            compact_jsonl(sorted(unit_record_sets[unit.id], key=lambda value: value["id"]))
        )
        for unit in course.units
    }
    unit_relations_sha256 = {
        unit.id: digest_bytes(relation_map_payload(unit.relations)) for unit in course.units
    }
    for unit in course.units:
        if unit.expected_relation_map_sha256:
            actual = unit_relations_sha256[unit.id]
            if actual != unit.expected_relation_map_sha256:
                fail(
                    f"issued relation mapping changed for {unit.id}: "
                    f"expected {unit.expected_relation_map_sha256}, got {actual}"
                )
        if unit.expected_id_type_sha256:
            baseline_records: list[Mapping[str, Any]] = []
            if unit.id_type_baseline_includes_common:
                baseline_records.extend(course.common_records)
            baseline_records.extend(unit_record_sets[unit.id])
            baseline_records.extend(relation_record(item) for item in unit.relations)
            actual = digest_bytes(id_type_payload(baseline_records))
            if actual != unit.expected_id_type_sha256:
                fail(
                    f"issued ID/type mapping changed for {unit.id}: "
                    f"expected {unit.expected_id_type_sha256}, got {actual}"
                )
    return BackendBuild(
        records_payload=records_payload,
        relations_payload=relations_payload,
        relations_ledger_payload=relations_ledger_payload,
        schema_payload=json_bytes(schema),
        record_count=len(records),
        relation_count=len(relations),
        active_relation_count=len(active_relations),
        superseded_relation_count=sum(item.status == "superseded" for item in relations),
        stable_relation_map_sha256=digest_bytes(relation_map_payload(relations)),
        active_relation_map_sha256=digest_bytes(relation_map_payload(active_relations)),
        relation_ledger_sha256=digest_bytes(relations_ledger_payload),
        unit_records_sha256=unit_records_sha256,
        unit_relations_sha256=unit_relations_sha256,
    )


@dataclass(frozen=True)
class ManifestItem:
    logical_path: str
    payload: bytes


def manifest_item_from_path(path: Path, logical_path: str | None = None) -> ManifestItem:
    if not path.is_file():
        fail(f"manifest input is not a file: {path}")
    return ManifestItem(logical_path or canonical_rel(path), path.read_bytes())


def build_manifest(items: Iterable[ManifestItem]) -> tuple[bytes, int]:
    values = list(items)
    folded = [value.logical_path.casefold() for value in values]
    if len(set(folded)) != len(folded):
        fail("manifest contains duplicate or case-colliding logical paths")
    ordered = sorted(values, key=lambda value: value.logical_path.casefold())
    rows = (
        (value.logical_path, len(value.payload), digest_bytes(value.payload)) for value in ordered
    )
    return csv_payload(("path", "bytes", "sha256"), rows), len(ordered)


def reader_tree_evidence(html_root: Path) -> dict[str, Any]:
    files = sorted(
        (path for path in html_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(html_root).as_posix().casefold(),
    )
    manifest = "".join(
        f"{path.relative_to(html_root).as_posix()}\t{path.stat().st_size}\t{digest(path)}\n"
        for path in files
    ).encode("utf-8")
    return {
        "files": len(files),
        "bytes": sum(path.stat().st_size for path in files),
        "manifestSha256": digest_bytes(manifest),
    }


def validate_visual_receipt(unit: UnitSpec, html_hash: str, html_root: Path) -> dict[str, Any] | None:
    if not unit.visual_qa_filename:
        return None
    path = QA / unit.visual_qa_filename
    if not path.is_file():
        fail(f"visual QA receipt missing: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    if (
        unit.visual_qa_script_filename == "visual_qa_unit.cjs"
        and report.get("schema") != "o017-unit-visual-qa-v2"
    ):
        fail("visual QA receipt uses the obsolete generic evidence schema")
    if report.get("status") != "PASS":
        fail(f"visual QA receipt is not PASS: {path}")
    if report.get("unit_html_sha256") != html_hash:
        fail("visual QA receipt is stale for the rendered unit HTML")
    if report.get("console_errors") or report.get("page_errors"):
        fail("visual QA receipt contains browser errors")
    if report.get("reader_tree") != reader_tree_evidence(html_root):
        fail("visual QA receipt reader-tree evidence is stale")
    if not unit.visual_qa_script_filename:
        fail(f"visual QA script is not declared for {unit.id}")
    script_path = ROOT / "scripts" / unit.visual_qa_script_filename
    if not script_path.is_file() or report.get("visual_qa_script_sha256") != digest(script_path):
        fail("visual QA script hash does not match its receipt")
    for viewport in ("desktop", "mobile"):
        evidence = report.get(viewport)
        if not isinstance(evidence, dict):
            fail(f"visual QA receipt lacks {viewport} evidence")
        coverage = evidence.get("visualCoverage")
        if not isinstance(coverage, dict) or coverage.get("coverageComplete") is not True:
            fail(f"visual QA lacks complete tiled coverage at {viewport}")
        tiles = coverage.get("tiles")
        if not isinstance(tiles, list) or not tiles:
            fail(f"visual QA lacks viewport tiles at {viewport}")
        if coverage.get("tileCount") != len(tiles):
            fail(f"visual QA tile count mismatch at {viewport}")
        if tiles[0].get("coveredStart") != 0:
            fail(f"visual QA does not begin at document top at {viewport}")
        if tiles[-1].get("coveredEnd") != coverage.get("documentHeight"):
            fail(f"visual QA does not reach document bottom at {viewport}")
        previous_end = 0
        tile_hashes: list[str] = []
        for tile in tiles:
            if tile.get("coveredStart", previous_end + 1) > previous_end:
                fail(f"visual QA has a coverage gap at {viewport}")
            screenshot = ROOT / str(tile.get("screenshot", ""))
            try:
                screenshot.resolve().relative_to(ROOT.resolve())
            except ValueError:
                fail(f"visual QA screenshot escapes task root: {screenshot}")
            screenshot_hash = tile.get("screenshotSha256")
            if not screenshot.is_file() or digest(screenshot) != screenshot_hash:
                fail(f"visual QA screenshot hash mismatch: {screenshot}")
            tile_hashes.append(str(screenshot_hash))
            previous_end = int(tile.get("coveredEnd", 0))
        if len(set(tile_hashes)) != len(tile_hashes):
            fail(f"visual QA contains duplicate viewport tiles at {viewport}")
        if evidence.get("bodyScrollWidth", 0) > evidence.get("viewportWidth", 0) + 1:
            fail(f"visual QA reports horizontal body overflow at {viewport}")
        if evidence.get("documentScrollWidth", 0) > evidence.get("viewportWidth", 0) + 1:
            fail(f"visual QA reports horizontal document overflow at {viewport}")
        if evidence.get("remoteRuntimeRequests"):
            fail(f"visual QA reports remote runtime requests at {viewport}")
        table_regions = evidence.get("tableScrolls")
        math_regions = evidence.get("mathScrolls")
        if not isinstance(table_regions, list) or not isinstance(math_regions, list):
            fail(f"visual QA lacks scroll-region semantics at {viewport}")
        for region in [*table_regions, *math_regions]:
            if (
                region.get("role") != "region"
                or region.get("tabIndex") != "0"
                or not region.get("ariaLabel")
            ):
                fail(f"visual QA has an unnamed or non-focusable region at {viewport}")
        for region in table_regions:
            if region.get("tableAriaLabel") != region.get("ariaLabel"):
                fail(f"visual QA has an unnamed table at {viewport}")
        wide_regions = [
            region
            for region in [*table_regions, *math_regions]
            if region.get("scrollWidth", 0) > region.get("clientWidth", 0) + 1
        ]
        horizontal = evidence.get("horizontalScrollEvidence")
        if not isinstance(horizontal, list) or len(horizontal) != len(wide_regions):
            fail(f"visual QA horizontal-region count mismatch at {viewport}")
        expected_keys = {
            (str(region.get("regionKind")), int(region.get("regionIndex", -1)))
            for region in wide_regions
        }
        observed_keys = {
            (str(region.get("regionKind")), int(region.get("regionIndex", -1)))
            for region in horizontal
        }
        if observed_keys != expected_keys:
            fail(f"visual QA horizontal-region identities mismatch at {viewport}")
        for region in horizontal:
            horizontal_tiles = region.get("tiles")
            if (
                region.get("coverageComplete") is not True
                or not isinstance(horizontal_tiles, list)
                or not horizontal_tiles
                or region.get("tileCount") != len(horizontal_tiles)
                or horizontal_tiles[0].get("coveredStart") != 0
                or horizontal_tiles[-1].get("coveredEnd") != region.get("scrollWidth")
            ):
                fail(f"visual QA lacks complete horizontal coverage at {viewport}")
            prior_end = 0
            horizontal_hashes: list[str] = []
            for tile in horizontal_tiles:
                if tile.get("coveredStart", prior_end + 1) > prior_end:
                    fail(f"visual QA has a horizontal evidence gap at {viewport}")
                screenshot = ROOT / str(tile.get("screenshot", ""))
                try:
                    screenshot.resolve().relative_to(ROOT.resolve())
                except ValueError:
                    fail(f"horizontal screenshot escapes task root: {screenshot}")
                screenshot_hash = str(tile.get("screenshotSha256", ""))
                if not screenshot.is_file() or digest(screenshot) != screenshot_hash:
                    fail(f"horizontal screenshot hash mismatch: {screenshot}")
                horizontal_hashes.append(screenshot_hash)
                prior_end = int(tile.get("coveredEnd", 0))
            if len(set(horizontal_hashes)) != len(horizontal_hashes):
                fail(f"visual QA contains duplicate horizontal tiles at {viewport}")
    return {"path": path, "report": report, "sha256": digest(path)}


def find_quarto() -> str:
    quarto = shutil.which("quarto")
    if quarto:
        return quarto
    candidate = Path(r"C:\Program Files\Quarto\bin\quarto.exe")
    if not candidate.is_file():
        fail("Quarto executable not found")
    return str(candidate)


def render_stage(quarto: str) -> tuple[Path, subprocess.CompletedProcess[str]]:
    stage = BUILD / f".o017-html-stage-{os.getpid()}"
    if stage.exists():
        fail(f"refusing to reuse existing render stage: {stage}")
    relative_output = Path("..") / "build" / stage.name
    render = run_checked(
        [quarto, "render", "--output-dir", relative_output.as_posix()],
        SOURCE,
    )
    if not stage.is_dir():
        fail("Quarto did not create the staged reader")
    return stage, render


def install_reader_release_files(html_root: Path) -> None:
    for source_path, relative_path in (
        (ROOT / "LICENSES.md", Path("LICENSES.md")),
        (ROOT / "THIRD_PARTY_NOTICES.md", Path("THIRD_PARTY_NOTICES.md")),
        (ROOT / "licenses" / "MIT.txt", Path("licenses/MIT.txt")),
        (ROOT / "licenses" / "APACHE-2.0.txt", Path("licenses/APACHE-2.0.txt")),
    ):
        if not source_path.is_file():
            fail(f"reader release file missing: {source_path}")
        write_bytes(html_root / relative_path, source_path.read_bytes())


def promote_html(stage: Path) -> None:
    backup = BUILD / f".o017-html-backup-{os.getpid()}"
    if backup.exists():
        fail(f"refusing to reuse existing HTML backup path: {backup}")
    moved_live = False
    try:
        if HTML_ROOT.exists():
            os.replace(HTML_ROOT, backup)
            moved_live = True
        os.replace(stage, HTML_ROOT)
    except BaseException:
        if moved_live and backup.exists() and not HTML_ROOT.exists():
            os.replace(backup, HTML_ROOT)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def check_unit(
    unit: UnitSpec,
    html_root: Path,
    documents: Mapping[Path, HtmlDocument],
    computation_results: tuple[Mapping[str, Any], ...],
) -> UnitCheck:
    html_path = html_root / unit.html_relative_path
    if not html_path.is_file():
        fail(f"rendered unit page missing: {html_path}")
    document = documents[html_path.resolve()]
    if document.language != "id-ID":
        fail(f"reader HTML language is not id-ID for {unit.id}")
    missing_sections = sorted(unit.required_section_ids - set(document.ids))
    if missing_sections:
        fail(f"{unit.id} missing required section IDs: {missing_sections}")
    missing_entities = sorted(unit.required_entity_fragments - set(document.ids))
    if missing_entities:
        fail(f"{unit.id} backend-addressable fragments missing: {missing_entities}")
    html_text = html_path.read_text(encoding="utf-8")
    if "<math" not in html_text:
        fail(f"native MathML was not emitted for {unit.id}")
    if 'class="o017-skip-link"' not in html_text:
        fail(f"skip-to-content link was not emitted for {unit.id}")
    if 'role="menu"' in html_text:
        fail(f"navbar button retains invalid menu role for {unit.id}")
    for exercise_id, solution_id in unit.exercise_solution_pairs:
        if exercise_id not in document.text or solution_id not in document.text:
            fail(f"rendered exercise/guidance labels missing: {exercise_id}, {solution_id}")
    lowered = document.text.casefold()
    for forbidden in ("todo", "tbd", "lorem ipsum", "placeholder"):
        if re.search(rf"\b{re.escape(forbidden)}\b", lowered):
            fail(f"{unit.id} contains unresolved placeholder marker: {forbidden}")
    for computation in unit.computations:
        code_copy = html_root / "code" / computation.code_path.name
        if not code_copy.is_file() or digest(code_copy) != digest(computation.code_path):
            fail(f"reader code asset is missing or differs for {unit.id}")
    return UnitCheck(unit, html_path, document, computation_results)


def run_computations(unit: UnitSpec) -> tuple[Mapping[str, Any], ...]:
    results: list[Mapping[str, Any]] = []
    for computation in unit.computations:
        for required in (computation.code_path, computation.expected_stdout_path):
            if not required.is_file():
                fail(f"required computation input missing: {required}")
        if (
            computation.expected_code_sha256
            and digest(computation.code_path) != computation.expected_code_sha256
        ):
            fail(f"computation code hash lock changed for {unit.id}")
        if (
            computation.expected_stdout_sha256
            and digest(computation.expected_stdout_path)
            != computation.expected_stdout_sha256
        ):
            fail(f"computation oracle hash lock changed for {unit.id}")
        execution = run_checked([sys.executable, str(computation.code_path)], ROOT)
        if execution.stdout.strip() != computation.expected_stdout_path.read_text(encoding="utf-8").strip():
            fail(f"computational stdout differs for {unit.id}")
        if not computation.result_path.is_file():
            fail(f"computation result missing for {unit.id}: {computation.result_path}")
        result = json.loads(computation.result_path.read_text(encoding="utf-8"))
        if result != dict(computation.expected_result):
            fail(f"unexpected mathematical result for {unit.id}: {result!r}")
        results.append(result)
    return tuple(results)


def unit_hashes(unit: UnitSpec, html_path: Path) -> dict[str, str]:
    hashes = {"html": digest(html_path)}
    for index, computation in enumerate(unit.computations, start=1):
        hashes[f"code:{index}"] = digest(computation.code_path)
        hashes[f"result:{index}"] = digest(computation.result_path)
    if len(unit.computations) == 1:
        hashes["code"] = hashes["code:1"]
        hashes["result"] = hashes["result:1"]
    return hashes


def admission_text(
    check: UnitCheck,
    backend: BackendBuild,
    manifest_hash: str,
    manifest_rows: int,
    local_links: int,
    fragments: int,
    qa_hash: str,
    visual: Mapping[str, Any] | None,
) -> bytes:
    unit = check.unit
    lines = [
        f"# Unit {unit.ordinal} Admission — O017/D120",
        "",
        "Status: **PASS / UNIT_ADMITTED**  ",
        "Date: 2026-08-22",
        "",
    ]
    if unit.id == "O017-U01":
        lines.extend(
            [
                "Unit 1 is admitted as original Indonesian bridge material. It contains a complete proof reconstruction, assumption audit, finite computational check, six exercises, six corresponding guidance entries, a completion memo, citations, and component-rights declarations.",
                "",
            ]
        )
    lines.extend(
        [
            "## Bound evidence",
            "",
            f"- Unit source: `{digest(unit.source_path)}`",
            f"- Unit HTML: `{digest(check.html_path)}` ({check.html_path.stat().st_size:,} bytes)",
            f"- Bibliography: `{digest(SOURCE / 'references.bib')}`",
        ]
    )
    if unit.computations:
        lines.append(f"- Computation result: `{digest(unit.computations[0].result_path)}`")
    lines.extend(
        [
            f"- Backend manifest: `{manifest_hash}` ({manifest_rows} rows)",
            f"- Backend: {backend.record_count} records and {backend.relation_count} issued relations ({backend.active_relation_count} active, {backend.superseded_relation_count} superseded)",
            f"- Stable relation-ID map: `{backend.stable_relation_map_sha256}`",
            f"- Active relation-ID map: `{backend.active_relation_map_sha256}`",
            f"- Issued relation ledger: `{backend.relation_ledger_sha256}`",
            f"- Unit backend records: `{backend.unit_records_sha256[unit.id]}`",
            f"- Unit backend relations: `{backend.unit_relations_sha256[unit.id]}`",
            f"- Reader local-link closure: {local_links} links, {fragments} fragments, zero missing targets",
            f"- Static QA: `{qa_hash}`",
        ]
    )
    if visual is not None:
        report = visual["report"]
        tree = report["reader_tree"]
        lines.extend(
            [
                f"- Browser QA: `{visual['sha256']}`",
                f"- Reader tree: {tree['files']} files / {tree['bytes']:,} bytes; canonical manifest",
                f"  `{tree['manifestSha256']}`",
                "- Browser result: desktop and mobile PASS; zero console/page errors, remote",
                "  runtime requests, missing alternatives, or horizontal overflow",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"This admission closes Unit {unit.ordinal} only. The O017 course goal remains active until every declared unit and the full reader/backend package are complete.",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def admit_unit(unit_id: str, course: CourseSpec = COURSE) -> dict[str, Any]:
    units_by_id = {unit.id: unit for unit in course.units}
    if len(units_by_id) != len(course.units):
        fail("duplicate registered unit ID")
    if unit_id not in units_by_id:
        fail(f"unit is not registered: {unit_id}")
    for required in (
        SOURCE / "_quarto.yml",
        SOURCE / "index.qmd",
        SOURCE / "styles.css",
        SOURCE / "references.bib",
        ROOT / "LICENSES.md",
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "licenses" / "MIT.txt",
        ROOT / "licenses" / "APACHE-2.0.txt",
        ROOT / "authority" / "SOURCE_FREEZE.json",
        ROOT / "controls" / "SOURCE_RIGHTS_MANIFEST.csv",
    ):
        if not required.is_file():
            fail(f"required course input missing: {required}")
    for unit in course.units:
        if not unit.source_path.is_file():
            fail(f"required unit source missing: {unit.source_path}")
        if unit.expected_source_sha256:
            actual_source_hash = digest(unit.source_path)
            if actual_source_hash != unit.expected_source_sha256:
                fail(
                    f"unit source changed for {unit.id}: expected "
                    f"{unit.expected_source_sha256}, got {actual_source_hash}"
                )

    computation_results = {unit.id: run_computations(unit) for unit in course.units}
    quarto = find_quarto()
    stage: Path | None = None
    try:
        stage, render = render_stage(quarto)
        install_reader_release_files(stage)
        index_path = stage / INDEX_RELATIVE_PATH
        if not index_path.is_file():
            fail("Quarto did not produce the reader index")
        html_paths = sorted(stage.rglob("*.html"), key=lambda path: path.relative_to(stage).as_posix().casefold())
        finalize_html_outputs(html_paths)
        verify_offline_css(stage.rglob("*.css"))
        documents = {path.resolve(): parse_html(path) for path in html_paths}
        if documents[index_path.resolve()].language != "id-ID":
            fail("reader index HTML language is not id-ID")
        checks = {
            unit.id: check_unit(unit, stage, documents, computation_results[unit.id])
            for unit in course.units
        }
        local_links, fragments = verify_local_links(documents)
        hashes = {unit.id: unit_hashes(unit, checks[unit.id].html_path) for unit in course.units}
        backend = build_backend(course, hashes)

        manifest_items = [
            manifest_item_from_path(SOURCE / "_quarto.yml"),
            manifest_item_from_path(SOURCE / "index.qmd"),
            manifest_item_from_path(SOURCE / "styles.css"),
            manifest_item_from_path(SOURCE / "references.bib"),
            manifest_item_from_path(ROOT / "LICENSES.md"),
            manifest_item_from_path(ROOT / "THIRD_PARTY_NOTICES.md"),
            manifest_item_from_path(ROOT / "licenses" / "MIT.txt"),
            manifest_item_from_path(ROOT / "licenses" / "APACHE-2.0.txt"),
            manifest_item_from_path(ROOT / "authority" / "SOURCE_FREEZE.json"),
            manifest_item_from_path(ROOT / "controls" / "SOURCE_RIGHTS_MANIFEST.csv"),
        ]
        for unit in course.units:
            manifest_items.append(manifest_item_from_path(unit.source_path))
            manifest_items.extend(manifest_item_from_path(path) for path in unit.manifest_inputs)
            manifest_items.extend(
                manifest_item_from_path(computation.result_path)
                for computation in unit.computations
            )
        manifest_items.extend(
            manifest_item_from_path(
                path,
                f"build/html/{path.relative_to(stage).as_posix()}",
            )
            for path in stage.rglob("*")
            if path.is_file()
        )
        manifest_items.extend(
            (
                ManifestItem("backend/records.jsonl", backend.records_payload),
                ManifestItem("backend/relations.csv", backend.relations_payload),
                ManifestItem("backend/relations-ledger.csv", backend.relations_ledger_payload),
                ManifestItem("backend/schema.json", backend.schema_payload),
            )
        )
        manifest_payload, manifest_rows = build_manifest(manifest_items)
        manifest_hash = digest_bytes(manifest_payload)

        target = units_by_id[unit_id]
        target_check = checks[unit_id]
        visual = validate_visual_receipt(target, digest(target_check.html_path), stage)
        result_values = computation_results[unit_id]
        computation_value: Any
        if len(result_values) == 1:
            computation_value = result_values[0]
        else:
            computation_value = list(result_values)
        qa = {
            "schema": "o017-unit-admission-v1",
            "lane_id": course.lane_id,
            "unit_id": target.id,
            "status": "PASS",
            "date": "2026-08-22",
            "inputs": {
                canonical_rel(target.source_path): digest(target.source_path),
                **{
                    canonical_rel(path): digest(path)
                    for path in target.manifest_inputs
                },
                "LICENSES.md": digest(ROOT / "LICENSES.md"),
                "THIRD_PARTY_NOTICES.md": digest(ROOT / "THIRD_PARTY_NOTICES.md"),
                "licenses/MIT.txt": digest(ROOT / "licenses" / "MIT.txt"),
                "licenses/APACHE-2.0.txt": digest(ROOT / "licenses" / "APACHE-2.0.txt"),
                "authority/SOURCE_FREEZE.json": digest(ROOT / "authority" / "SOURCE_FREEZE.json"),
                "controls/SOURCE_RIGHTS_MANIFEST.csv": digest(
                    ROOT / "controls" / "SOURCE_RIGHTS_MANIFEST.csv"
                ),
            },
            "computation": computation_value,
            "reader": {
                "html_files": len(html_paths),
                "unit_html_bytes": target_check.html_path.stat().st_size,
                "unit_html_sha256": digest(target_check.html_path),
                "language": target_check.document.language,
                "required_section_ids": len(target.required_section_ids),
                "backend_addressable_fragments": len(target.required_entity_fragments),
                "exercise_labels": len(target.exercise_solution_pairs),
                "guidance_labels": len(target.exercise_solution_pairs),
                "local_links_checked": local_links,
                "fragment_links_checked": fragments,
                "missing_local_targets": 0,
                "unresolved_placeholders": 0,
                "remote_runtime_dependencies": 0,
                "math_rendering": "native MathML",
                "skip_link": True,
            },
            "backend": {
                "record_count": backend.record_count,
                "relation_count": backend.relation_count,
                "issued_relation_count": backend.relation_count,
                "active_relation_count": backend.active_relation_count,
                "superseded_relation_count": backend.superseded_relation_count,
                "manifest_rows": manifest_rows,
                "manifest_sha256": manifest_hash,
                "entity_classes_supported": list(course.entity_classes),
                "registered_units": [unit.id for unit in course.units],
                "stable_relation_map_sha256": backend.stable_relation_map_sha256,
                "active_relation_map_sha256": backend.active_relation_map_sha256,
                "relation_ledger_sha256": backend.relation_ledger_sha256,
                "unit_records_sha256": backend.unit_records_sha256[target.id],
                "unit_relations_sha256": backend.unit_relations_sha256[target.id],
            },
            "toolchain": {
                "python": sys.version.split()[0],
                "quarto": run_checked([quarto, "--version"], ROOT).stdout.strip(),
            },
            "scope_notes": list(target.scope_notes),
        }
        qa_payload = json_bytes(qa)
        qa_hash = digest_bytes(qa_payload)
        admission_payload = admission_text(
            target_check,
            backend,
            manifest_hash,
            manifest_rows,
            local_links,
            fragments,
            qa_hash,
            visual,
        )

        promote_html(stage)
        stage = None
        write_bytes(BACKEND / "records.jsonl", backend.records_payload)
        write_bytes(BACKEND / "relations.csv", backend.relations_payload)
        write_bytes(BACKEND / "relations-ledger.csv", backend.relations_ledger_payload)
        write_bytes(BACKEND / "schema.json", backend.schema_payload)
        write_bytes(BACKEND / "manifest.csv", manifest_payload)
        write_bytes(QA / target.qa_filename, qa_payload)
        write_bytes(QA / target.admission_filename, admission_payload)

        for logical, payload in (
            (BACKEND / "records.jsonl", backend.records_payload),
            (BACKEND / "relations.csv", backend.relations_payload),
            (BACKEND / "relations-ledger.csv", backend.relations_ledger_payload),
            (BACKEND / "schema.json", backend.schema_payload),
            (BACKEND / "manifest.csv", manifest_payload),
            (QA / target.qa_filename, qa_payload),
            (QA / target.admission_filename, admission_payload),
        ):
            if digest(logical) != digest_bytes(payload):
                fail(f"promoted output differs from staged bytes: {logical}")

        return {
            "status": "PASS",
            "unit": target.id,
            "registered_units": [unit.id for unit in course.units],
            "unit_html_sha256": digest(HTML_ROOT / target.html_relative_path),
            "backend_manifest_sha256": manifest_hash,
            "stable_relation_map_sha256": backend.stable_relation_map_sha256,
            "qa_sha256": digest(QA / target.qa_filename),
            "admission_sha256": digest(QA / target.admission_filename),
            "quarto_stdout": render.stdout.strip(),
        }
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
