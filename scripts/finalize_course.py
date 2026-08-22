"""Validate and admit the complete nine-unit O017 reader without publishing it."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re

from o017_pipeline import (
    BACKEND,
    COURSE,
    HTML_ROOT,
    QA,
    ROOT,
    SOURCE,
    build_backend,
    check_unit,
    digest,
    digest_bytes,
    json_bytes,
    parse_html,
    reader_tree_evidence,
    run_computations,
    unit_hashes,
    validate_extension_packages,
    validate_visual_receipt,
    verify_local_links,
    verify_offline_css,
    write_bytes,
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def verify_manifest(path: Path) -> tuple[int, int, str]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    if not rows or set(rows[0]) != {"path", "bytes", "sha256"}:
        fail("backend manifest header is invalid")
    folded: set[str] = set()
    total = 0
    for row in rows:
        logical = row["path"]
        if logical.casefold() in folded:
            fail(f"duplicate or case-colliding manifest path: {logical}")
        folded.add(logical.casefold())
        target = (ROOT / Path(logical)).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"manifest path escapes task root: {logical}")
        if not target.is_file():
            fail(f"manifest file is missing: {logical}")
        expected_bytes = int(row["bytes"])
        if target.stat().st_size != expected_bytes or digest(target) != row["sha256"]:
            fail(f"manifest byte/hash mismatch: {logical}")
        total += expected_bytes
    return len(rows), total, digest(path)


def verify_full_visual(tree: dict[str, object]) -> dict[str, object]:
    path = QA / "FULL_READER_VISUAL_QA.json"
    if not path.is_file():
        fail("full-reader browser receipt is missing")
    report = json.loads(path.read_text(encoding="utf-8"))
    expected_pages = [
        "index.html",
        *[unit.html_relative_path.as_posix() for unit in COURSE.units],
        "wrapper/index.html",
    ]
    expected_legal = {
        "LICENSES.md": ROOT / "LICENSES.md",
        "THIRD_PARTY_NOTICES.md": ROOT / "THIRD_PARTY_NOTICES.md",
        "licenses/MIT.txt": ROOT / "licenses" / "MIT.txt",
        "licenses/APACHE-2.0.txt": ROOT / "licenses" / "APACHE-2.0.txt",
        "licenses/AMSFonts-3.04-OFL.txt": ROOT / "licenses" / "AMSFonts-3.04-OFL.txt",
        "licenses/AMSFonts-3.04-README.txt": ROOT / "licenses" / "AMSFonts-3.04-README.txt",
        "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt": ROOT
        / "licenses"
        / "FONT-AWESOME-FREE-5.15.4-LICENSE.txt",
        "licenses/GUST-FONT-LICENSE-1.0.txt": ROOT / "licenses" / "GUST-FONT-LICENSE-1.0.txt",
        "licenses/LATIN-MODERN-MATH-1.959-README.txt": ROOT
        / "licenses"
        / "LATIN-MODERN-MATH-1.959-README.txt",
        "licenses/SIL-OFL-1.1.txt": ROOT / "licenses" / "SIL-OFL-1.1.txt",
        "licenses/FONT_COMPONENT_PROVENANCE.json": ROOT
        / "licenses"
        / "FONT_COMPONENT_PROVENANCE.json",
    }
    if report.get("schema") != "o017-full-reader-visual-qa-v2" or report.get("status") != "PASS":
        fail("full-reader browser receipt is not PASS v2")
    if report.get("pages") != expected_pages or report.get("reader_tree") != tree:
        fail("full-reader browser receipt is stale for the final tree")
    script = ROOT / "scripts" / "visual_qa_full_reader.cjs"
    if report.get("visual_qa_script_sha256") != digest(script):
        fail("full-reader browser script hash is stale")
    if report.get("console_errors") or report.get("page_errors"):
        fail("full-reader browser receipt contains errors")
    legal_rows = {item["path"]: item for item in report.get("legal_files", [])}
    if set(legal_rows) != set(expected_legal):
        fail("full-reader browser receipt has an incomplete legal-file set")
    for logical, source in expected_legal.items():
        target = HTML_ROOT / logical
        row = legal_rows[logical]
        if (
            not target.is_file()
            or target.read_bytes() != source.read_bytes()
            or row.get("bytes") != target.stat().st_size
            or row.get("sha256") != digest(target)
        ):
            fail(f"reader legal file differs: {logical}")
    checks = report.get("checks", {})
    for viewport in ("desktop", "mobile"):
        values = checks.get(viewport, {})
        if any(page not in values for page in expected_pages):
            fail(f"full-reader browser receipt lacks {viewport} page coverage")
        for page in expected_pages:
            item = values[page]
            if (
                item.get("language") != "id-ID"
                or item.get("imagesWithoutAlt") != 0
                or item.get("skipLinks") != 1
                or item.get("remoteRuntimeRequests")
                or item.get("bodyScrollWidth", 0) > item.get("viewportWidth", 0) + 1
                or item.get("documentScrollWidth", 0) > item.get("viewportWidth", 0) + 1
                or "o017-skip-link" not in str(item.get("firstTab", {}).get("className", "")).split()
            ):
                fail(f"full-reader {viewport} accessibility check failed: {page}")
        for coverage_name, label in (
            ("indexVisualCoverage", "landing-page"),
            ("wrapperVisualCoverage", "delivery-wrapper"),
        ):
            coverage = values.get(coverage_name, {})
            tiles = coverage.get("tiles", [])
            if coverage.get("coverageComplete") is not True or coverage.get("tileCount") != len(tiles) or not tiles:
                fail(f"{label} visual coverage is incomplete at {viewport}")
            for tile in tiles:
                screenshot = ROOT / tile["screenshot"]
                if not screenshot.is_file() or digest(screenshot) != tile["screenshotSha256"]:
                    fail(f"{label} screenshot mismatch: {screenshot}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
        "toolchain": report["toolchain"],
    }


def verify_release_metadata() -> dict[str, object]:
    path = ROOT / "release" / "zenodo_metadata.json"
    value = json.loads(path.read_text(encoding="utf-8"))["metadata"]
    expected = {
        "upload_type": "publication",
        "publication_type": "book",
        "publication_date": "2026-08-22",
        "language": "ind",
        "license": "other-open",
        "access_right": "open",
        "version": "2026.08.22.1",
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            fail(f"Zenodo metadata {key} is not frozen")
    if value.get("creators") != [{"name": "KokunoYumeto"}]:
        fail("Zenodo creator identity is not the declared release identity")
    if value.get("contributors") != [{"name": "OpenAI Codex gpt-5.6-sol, Ultra", "type": "Other"}]:
        fail("Zenodo production-system disclosure is not frozen")
    if "Curriculum admission remains a separate decision" not in value.get("description", ""):
        fail("Zenodo metadata lacks the curriculum-admission separation")
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


def main() -> None:
    if [unit.id for unit in COURSE.units] != [f"O017-U{index:02d}" for index in range(1, 10)]:
        fail("registered course is not the exact nine-unit sequence")
    for unit in COURSE.units:
        if unit.expected_source_sha256 and digest(unit.source_path) != unit.expected_source_sha256:
            fail(f"source lock changed: {unit.id}")

    extension_validation = validate_extension_packages()

    html_paths = sorted(HTML_ROOT.rglob("*.html"), key=lambda item: item.relative_to(HTML_ROOT).as_posix())
    expected_html = {
        Path("index.html"),
        *[unit.html_relative_path for unit in COURSE.units],
        Path("wrapper/index.html"),
    }
    if {path.relative_to(HTML_ROOT) for path in html_paths} != expected_html:
        fail("final reader does not contain exactly the landing page and nine unit HTML pages")
    verify_offline_css(HTML_ROOT.rglob("*.css"))
    documents = {path.resolve(): parse_html(path) for path in html_paths}
    computations = {unit.id: run_computations(unit) for unit in COURSE.units}
    checks = {
        unit.id: check_unit(unit, HTML_ROOT, documents, computations[unit.id])
        for unit in COURSE.units
    }
    local_links, fragments = verify_local_links(documents)
    hashes = {unit.id: unit_hashes(unit, checks[unit.id].html_path) for unit in COURSE.units}
    backend = build_backend(COURSE, hashes)
    expected_backend = {
        "records.jsonl": backend.records_payload,
        "relations.csv": backend.relations_payload,
        "relations-ledger.csv": backend.relations_ledger_payload,
        "schema.json": backend.schema_payload,
    }
    for filename, payload in expected_backend.items():
        path = BACKEND / filename
        if not path.is_file() or path.read_bytes() != payload:
            fail(f"live backend differs from deterministic reconstruction: {filename}")

    manifest_rows, manifest_bytes, manifest_sha = verify_manifest(BACKEND / "manifest.csv")
    tree = reader_tree_evidence(HTML_ROOT)
    exercises = sum(len(unit.exercise_solution_pairs) for unit in COURSE.units)
    if exercises != 54:
        fail("course does not expose exactly 54 exercise-guidance pairs")

    visual_receipts: dict[str, object] = {}
    unit_receipts: dict[str, object] = {}
    for unit in COURSE.units:
        html_hash = digest(HTML_ROOT / unit.html_relative_path)
        visual = validate_visual_receipt(unit, html_hash, HTML_ROOT)
        if visual is None:
            fail(f"unit visual receipt is missing: {unit.id}")
        qa_path = QA / unit.qa_filename
        admission_path = QA / unit.admission_filename
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        if (
            qa.get("status") != "PASS"
            or qa.get("reader", {}).get("unit_html_sha256") != html_hash
            or qa.get("backend", {}).get("manifest_sha256") != manifest_sha
            or qa.get("backend", {}).get("stable_relation_map_sha256") != backend.stable_relation_map_sha256
            or qa.get("backend", {}).get("registered_units") != [item.id for item in COURSE.units]
        ):
            fail(f"unit admission receipt is stale: {unit.id}")
        admission = admission_path.read_text(encoding="utf-8")
        for required_hash in (html_hash, manifest_sha, visual["sha256"], tree["manifestSha256"]):
            if required_hash not in admission:
                fail(f"unit admission Markdown is not bound to current evidence: {unit.id}")
        visual_receipts[unit.id] = visual["sha256"]
        unit_receipts[unit.id] = {
            "source_sha256": digest(unit.source_path),
            "html_sha256": html_hash,
            "qa_sha256": digest(qa_path),
            "admission_sha256": digest(admission_path),
        }

    full_visual = verify_full_visual(tree)
    cursor_path = ROOT / "controls" / "CURSOR.json"
    if cursor_path.is_file():
        cursor = json.loads(cursor_path.read_text(encoding="utf-8-sig"))
        if cursor.get("admitted_units") != [unit.id for unit in COURSE.units] or cursor.get("active_unit") is not None:
            fail("durable cursor does not close the nine-unit sequence")
    decisions_path = ROOT / "controls" / "DECISIONS.jsonl"
    if decisions_path.is_file():
        decisions = [
            json.loads(line)
            for line in decisions_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not any(item.get("id") == "O017-DEC-0017" for item in decisions):
            fail("durable decision ledger does not contain the Unit 9 admission decision")
    source_freeze_text = (ROOT / "controls" / "SOURCE_FREEZE.md").read_text(encoding="utf-8")
    if "independent of how much production work is already complete" not in re.sub(r"\s+", " ", source_freeze_text):
        fail("curriculum-spine rationale is not independent of sunk work")

    records = [json.loads(line) for line in (BACKEND / "records.jsonl").read_text(encoding="utf-8").splitlines()]
    edition = next((item for item in records if item.get("id") == "O017-EDITION-01"), None)
    if (
        not edition
        or edition.get("status") != "release-candidate"
        or edition.get("creator") != "KokunoYumeto"
        or edition.get("production_system") != "OpenAI Codex gpt-5.6-sol, Ultra"
    ):
        fail("backend edition is not a transparent release candidate")

    bibliography = (SOURCE / "references.bib").read_text(encoding="utf-8")
    bibliography_keys = set(re.findall(r"(?m)^@[A-Za-z]+\{([^,]+),", bibliography))
    cited_keys: set[str] = set()
    for path in [
        SOURCE / "index.qmd",
        *[unit.source_path for unit in COURSE.units],
        SOURCE / "wrapper" / "index.qmd",
    ]:
        source_text = path.read_text(encoding="utf-8")
        for group in re.findall(r"\[([^\]]*@[A-Za-z0-9:_./+-]+[^\]]*)\]", source_text):
            cited_keys.update(re.findall(r"@([A-Za-z0-9:_./+-]+)", group))
    unresolved_citations = sorted(cited_keys - bibliography_keys)
    if unresolved_citations:
        fail(f"unresolved citation keys: {unresolved_citations}")

    release_metadata = verify_release_metadata()
    provenance_rows = list(csv.DictReader((ROOT / "RELEASE_PROVENANCE.csv").read_text(encoding="utf-8").splitlines()))
    if len(provenance_rows) != 3 or any(row["bundled"] != "false" for row in provenance_rows[1:]):
        fail("release provenance does not explicitly exclude donor witness trees")
    font_provenance_path = ROOT / "licenses" / "FONT_COMPONENT_PROVENANCE.json"
    font_provenance = json.loads(font_provenance_path.read_text(encoding="utf-8"))
    font_components = {
        row["resource_id"]: row for row in font_provenance.get("components", [])
    }
    expected_font_ids = {
        "O017-FONT-LM-TEXT",
        "O017-FONT-LM-MATH",
        "O017-FONT-FA5FREE",
        "O017-FONT-MSAM10",
    }
    if font_provenance.get("schema") != "o017-font-component-provenance-v2" or set(font_components) != expected_font_ids:
        fail("font provenance is not the exact four-component v2 closure")
    rights_manifest_path = ROOT / "controls" / "SOURCE_RIGHTS_MANIFEST.csv"
    rights_rows = {
        row["resource_id"]: row
        for row in csv.DictReader(rights_manifest_path.read_text(encoding="utf-8").splitlines())
    }
    if not expected_font_ids.issubset(rights_rows):
        fail("source-rights manifest lacks one or more embedded font components")
    for resource_id, component in font_components.items():
        row = rights_rows[resource_id]
        if (
            int(row["selected_files"]) != component["embedded_pdf_objects"]
            or int(row["selected_bytes"]) != component["embedded_stream_bytes"]
            or row["selected_manifest_sha256"] != component["component_manifest_sha256"]
            or "PDF_FONT_AND_TAG_AUDIT_2026.08.22.1.json" not in row["release_evidence"]
        ):
            fail(f"source-rights manifest is stale for {resource_id}")

    qa = {
        "schema": "o017-full-course-admission-v2",
        "status": "PASS",
        "date": "2026-08-22",
        "lane_id": COURSE.lane_id,
        "edition_id": "O017-EDITION-01",
        "version": "2026.08.22.1",
        "creator": "KokunoYumeto",
        "production_system": "OpenAI Codex gpt-5.6-sol, Ultra",
        "curriculum_selection": "separate decision; this receipt admits the edition, not the 40-course corpus choice",
        "units": [unit.id for unit in COURSE.units],
        "unit_receipts": unit_receipts,
        "visual_receipts": visual_receipts,
        "full_reader_visual": full_visual,
        "reader": {
            **tree,
            "html_pages": len(html_paths),
            "local_links_checked": local_links,
            "fragment_links_checked": fragments,
            "exercise_guidance_pairs": exercises,
            "unresolved_citations": unresolved_citations,
            "remote_runtime_dependencies": 0,
            "language": "id-ID",
            "math_rendering": "native MathML",
        },
        "backend": {
            "record_count": backend.record_count,
            "issued_relation_count": backend.relation_count,
            "active_relation_count": backend.active_relation_count,
            "superseded_relation_count": backend.superseded_relation_count,
            "stable_relation_map_sha256": backend.stable_relation_map_sha256,
            "active_relation_map_sha256": backend.active_relation_map_sha256,
            "relation_ledger_sha256": backend.relation_ledger_sha256,
            "manifest_rows": manifest_rows,
            "manifest_input_bytes": manifest_bytes,
            "manifest_sha256": manifest_sha,
        },
        "extensions": extension_validation,
        "rights": {
            "LICENSES.md": digest(ROOT / "LICENSES.md"),
            "THIRD_PARTY_NOTICES.md": digest(ROOT / "THIRD_PARTY_NOTICES.md"),
            "licenses/MIT.txt": digest(ROOT / "licenses" / "MIT.txt"),
            "licenses/APACHE-2.0.txt": digest(ROOT / "licenses" / "APACHE-2.0.txt"),
            "licenses/FONT_COMPONENT_PROVENANCE.json": digest(font_provenance_path),
            "controls/SOURCE_RIGHTS_MANIFEST.csv": digest(rights_manifest_path),
            "font_component_ids": sorted(expected_font_ids),
            "RELEASE_PROVENANCE.csv": digest(ROOT / "RELEASE_PROVENANCE.csv"),
            "donor_witness_trees_bundled": False,
            "unauthorized_external_contact_claims": 0,
        },
        "metadata": release_metadata,
    }
    payload = json_bytes(qa)
    qa_hash = digest_bytes(payload)
    admission = "\n".join(
        [
            "# Full-course admission — O017/D120",
            "",
            "Status: **PASS / FULL_READER_BUILT**  ",
            "Date: 2026-08-22",
            "",
            f"- Units: 9 admitted; 54 exercise–guidance pairs; authentic-delivery wrapper included",
            f"- Reader: {tree['files']} files / {tree['bytes']:,} bytes; tree `{tree['manifestSha256']}`",
            f"- Links: {local_links} local / {fragments} fragments; zero missing targets",
            f"- Backend: {backend.record_count} records / {backend.relation_count} issued relations; stable map `{backend.stable_relation_map_sha256}`",
            f"- Backend manifest: {manifest_rows} rows; `{manifest_sha}`",
            f"- Full browser QA: `{full_visual['sha256']}`",
            f"- Full static/rights/backend receipt: `{qa_hash}`",
            "",
            "This admits the complete edition as a release candidate. Curriculum selection remains a separate decision. Publication is not complete until the Zenodo record and every public file pass unauthenticated byte readback.",
            "",
        ]
    ).encode("utf-8")
    write_bytes(QA / "FULL_COURSE_QA.json", payload)
    write_bytes(QA / "FULL_COURSE_ADMISSION.md", admission)
    print(
        json.dumps(
            {
                "status": "PASS",
                "qa_sha256": digest(QA / "FULL_COURSE_QA.json"),
                "admission_sha256": digest(QA / "FULL_COURSE_ADMISSION.md"),
                "reader_tree": tree,
                "backend_manifest_sha256": manifest_sha,
                "stable_relation_map_sha256": backend.stable_relation_map_sha256,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
