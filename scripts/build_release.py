"""Build and verify deterministic public release archives for O017/D120."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import zipfile

from o017_pipeline import extension_release_paths, validate_extension_packages
from o017_specs import COURSE


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
HTML = BUILD / "html"
QA = ROOT / "qa"
RELEASE = ROOT / "release"
VERSION = "2026.08.24"
RELEASE_DATE = "2026-08-24"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
MANIFEST_NAME = "RELEASE_MANIFEST.json"
READER_NAME = f"o017-d120-id-{VERSION}-reader-html.zip"
SOURCE_NAME = f"o017-d120-id-{VERSION}-source-backend-evidence.zip"
PDF_NAME = f"kerja-matematika-yang-dapat-ditelusuri-id-{VERSION}.pdf"
PDF = ROOT / "output" / "pdf" / PDF_NAME
PDF_QA = QA / "PDF_QA.json"
PDF_VISUAL_QA = QA / "PDF_VISUAL_QA.md"
PDF_FONT_QA = QA / f"PDF_FONT_AND_TAG_AUDIT_{VERSION}.json"
PDF_FONT_QA_MD = QA / f"PDF_FONT_AND_TAG_AUDIT_{VERSION}.md"
PDF_ACCESSIBILITY_DISCLOSURE = QA / "PDF_ACCESSIBILITY_DISCLOSURE_PROPOSED.md"
FONT_PROVENANCE = ROOT / "licenses" / "FONT_COMPONENT_PROVENANCE.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def safe_name(name: str) -> None:
    logical = PurePosixPath(name)
    if (
        not name
        or "\\" in name
        or name.startswith("/")
        or name.endswith("/")
        or any(part in ("", ".", "..") for part in logical.parts)
        or ":" in logical.parts[0]
    ):
        fail(f"unsafe archive path: {name!r}")


def add_entry(entries: dict[str, Path], path: Path, logical: str | None = None) -> None:
    if not path.is_file():
        fail(f"release input is missing: {path}")
    name = logical or path.relative_to(ROOT).as_posix()
    safe_name(name)
    folded = name.casefold()
    if any(existing.casefold() == folded for existing in entries):
        fail(f"duplicate or case-colliding release path: {name}")
    entries[name] = path


def reader_entries() -> dict[str, Path]:
    entries: dict[str, Path] = {}
    for path in sorted(HTML.rglob("*"), key=lambda item: item.relative_to(HTML).as_posix()):
        if path.is_file():
            add_entry(entries, path, path.relative_to(HTML).as_posix())
    expected_pages = {
        "index.html",
        *[unit.html_relative_path.as_posix() for unit in COURSE.units],
        "wrapper/index.html",
    }
    actual_pages = {name for name in entries if name.endswith(".html")}
    if actual_pages != expected_pages:
        fail("reader archive is not the exact landing-page plus nine-unit closure")
    for required in (
        "LICENSES.md",
        "THIRD_PARTY_NOTICES.md",
        "licenses/MIT.txt",
        "licenses/APACHE-2.0.txt",
        "licenses/AMSFonts-3.04-OFL.txt",
        "licenses/AMSFonts-3.04-README.txt",
        "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt",
        "licenses/GUST-FONT-LICENSE-1.0.txt",
        "licenses/LATIN-MODERN-MATH-1.959-README.txt",
        "licenses/SIL-OFL-1.1.txt",
        "licenses/FONT_COMPONENT_PROVENANCE.json",
        "qa/PDF_ACCESSIBILITY_DISCLOSURE_PROPOSED.md",
        "licenses/AMSFonts-3.04-OFL.txt",
        "licenses/AMSFonts-3.04-README.txt",
        "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt",
        "licenses/GUST-FONT-LICENSE-1.0.txt",
        "licenses/LATIN-MODERN-MATH-1.959-README.txt",
        "licenses/SIL-OFL-1.1.txt",
        "licenses/FONT_COMPONENT_PROVENANCE.json",
    ):
        if required not in entries:
            fail(f"reader archive lacks required notice: {required}")
    return entries


def screenshot_paths(receipt: Path) -> set[Path]:
    value = json.loads(receipt.read_text(encoding="utf-8"))
    names: set[str] = set()

    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, nested in item.items():
                if key == "screenshot" and isinstance(nested, str):
                    names.add(nested)
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)

    walk(value)
    paths: set[Path] = set()
    for name in names:
        safe_name(name)
        if not name.startswith("qa/visual/"):
            fail(f"receipt references a screenshot outside qa/visual: {name}")
        path = ROOT / Path(name)
        if not path.is_file():
            fail(f"receipt screenshot is missing: {name}")
        paths.add(path)
    return paths


def source_entries() -> tuple[dict[str, Path], int]:
    entries: dict[str, Path] = {}
    for name in (
        "README.md",
        "LICENSES.md",
        "THIRD_PARTY_NOTICES.md",
        "CITATION.cff",
        "BUILD.md",
        "RELEASE_PROVENANCE.csv",
        "licenses/MIT.txt",
        "licenses/APACHE-2.0.txt",
        "licenses/AMSFonts-3.04-OFL.txt",
        "licenses/AMSFonts-3.04-README.txt",
        "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt",
        "licenses/GUST-FONT-LICENSE-1.0.txt",
        "licenses/LATIN-MODERN-MATH-1.959-README.txt",
        "licenses/SIL-OFL-1.1.txt",
        "licenses/FONT_COMPONENT_PROVENANCE.json",
        "integration/FONT_RIGHTS_MAP_ADDITIONS_DRAFT.csv",
        "qa/PDF_ACCESSIBILITY_DISCLOSURE_PROPOSED.md",
        "release/zenodo_metadata.json",
        "authority/SOURCE_FREEZE.json",
        "controls/SOURCE_FREEZE.md",
        "controls/SOURCE_RIGHTS_MANIFEST.csv",
        "controls/REQUIREMENTS_AND_NON_OVERLAP.md",
        "controls/TERMINOLOGY.csv",
        "controls/TERMINOLOGY_QA_RECHECK_2026.08.24.md",
        "authority/terminology_qa/arxiv_source/ARXIV_TEX_WITNESS_0807.4609v1.json",
        "source/_quarto.yml",
        "source/_quarto-pdf.yml",
        "source/pdf-header.tex",
        "source/index.qmd",
        "source/wrapper/index.qmd",
        "source/styles.css",
        "source/references.bib",
        "source/code/verify_mst_uniqueness.py",
        "source/code/expected-output.txt",
        "source/code/u06_recurrence_witness.py",
        "source/code/u06-expected-output.txt",
        "build/unit-01-mst-check.json",
        "backend/records.jsonl",
        "backend/relations.csv",
        "backend/relations-ledger.csv",
        "backend/schema.json",
        "backend/manifest.csv",
        f"output/pdf/{PDF_NAME}",
    ):
        add_entry(entries, ROOT / Path(name), name)
    for unit in COURSE.units:
        add_entry(entries, unit.source_path)
    for path in extension_release_paths():
        add_entry(entries, path)
    for name in (
        "build_and_admit.py",
        "o017_pipeline.py",
        "o017_specs.py",
        "render_candidate.py",
        "visual_qa_unit.cjs",
        "visual_qa_full_reader.cjs",
        "finalize_course.py",
        "qa_pdf.py",
        "audit_pdf_font_accessibility.py",
        "generate_font_component_provenance.py",
        "build_release.py",
    ):
        add_entry(entries, ROOT / "scripts" / name)

    receipt_names = [
        *[f"UNIT_{index:02d}_ADMISSION.md" for index in range(1, 10)],
        *[f"UNIT_{index:02d}_QA.json" for index in range(1, 10)],
        *[f"UNIT_{index:02d}_VISUAL_QA.json" for index in range(1, 10)],
        "FULL_READER_VISUAL_QA.json",
        "FULL_COURSE_QA.json",
        "FULL_COURSE_ADMISSION.md",
        "PDF_QA.json",
        "PDF_VISUAL_QA.md",
        f"PDF_FONT_AND_TAG_AUDIT_{VERSION}.json",
        f"PDF_FONT_AND_TAG_AUDIT_{VERSION}.md",
    ]
    screenshots: set[Path] = set()
    for name in receipt_names:
        path = QA / name
        add_entry(entries, path)
        if name.endswith("VISUAL_QA.json"):
            screenshots.update(screenshot_paths(path))
    for path in sorted(screenshots, key=lambda item: item.relative_to(ROOT).as_posix()):
        add_entry(entries, path)

    forbidden = (
        "authority/the-turing-way-",
        "authority/py-rse-",
        "source/.quarto/",
        "source/site_libs/",
        "source/code/__pycache__/",
        "scripts/__pycache__/",
        "controls/CURRENT_STATE.md",
        "controls/CURSOR.json",
        "controls/DECISIONS.jsonl",
        "scripts/build_and_admit_unit1.py",
        "scripts/visual_qa_unit1.cjs",
    )
    for name in entries:
        if any(name == prefix or name.startswith(prefix) for prefix in forbidden):
            fail(f"forbidden internal/transient path entered source archive: {name}")
    return entries, len(screenshots)


def manifest_payload(label: str, entries: dict[str, Path]) -> bytes:
    rows = []
    total = 0
    for name in sorted(entries):
        data = entries[name].read_bytes()
        rows.append({"path": name, "bytes": len(data), "sha256": sha256_bytes(data)})
        total += len(data)
    return json_bytes(
        {
            "schema": "o017-release-archive-manifest-v1",
            "archive": label,
            "release_version": VERSION,
            "manifest_excludes_itself": True,
            "file_count": len(rows),
            "total_uncompressed_bytes": total,
            "files": rows,
        }
    )


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits |= 0x800
    return info


def write_archive(path: Path, label: str, entries: dict[str, Path]) -> None:
    manifest = manifest_payload(label, entries)
    payloads = {name: source.read_bytes() for name, source in entries.items()}
    payloads[MANIFEST_NAME] = manifest
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(payloads):
            archive.writestr(zip_info(name), payloads[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def verify_archive(path: Path, label: str, entries: dict[str, Path]) -> dict[str, object]:
    expected_manifest = manifest_payload(label, entries)
    expected_names = sorted([*entries, MANIFEST_NAME])
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if names != expected_names or archive.testzip() is not None:
            fail(f"archive inventory or CRC failed: {path.name}")
        if len({name.casefold() for name in names}) != len(names):
            fail(f"archive contains a case collision: {path.name}")
        for info in archive.infolist():
            safe_name(info.filename)
            if info.date_time != FIXED_TIME:
                fail(f"archive timestamp is not fixed: {info.filename}")
        if archive.read(MANIFEST_NAME) != expected_manifest:
            fail(f"archive manifest differs from exact inputs: {path.name}")
        parsed = json.loads(expected_manifest)
        for row in parsed["files"]:
            data = archive.read(row["path"])
            if len(data) != row["bytes"] or sha256_bytes(data) != row["sha256"]:
                fail(f"archive member hash failed: {row['path']}")
    return {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "entry_count_including_manifest": len(expected_names),
        "payload_file_count": len(entries),
        "payload_bytes": sum(item.stat().st_size for item in entries.values()),
    }


def directory_inventory(path: Path) -> list[dict[str, object]]:
    return [
        {
            "path": item.relative_to(path).as_posix(),
            "bytes": item.stat().st_size,
            "sha256": sha256_file(item),
        }
        for item in sorted(path.rglob("*"), key=lambda value: value.relative_to(path).as_posix())
        if item.is_file()
    ]


def run_checked(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, encoding="utf-8", capture_output=True)
    if result.returncode:
        fail(f"fresh-extraction command failed ({' '.join(command)}):\n{result.stdout}\n{result.stderr}")
    return result


def fresh_extraction_check(source_archive: Path, temp: Path) -> dict[str, object]:
    fresh = temp / "fresh-source"
    fresh.mkdir()
    with zipfile.ZipFile(source_archive) as archive:
        for info in archive.infolist():
            safe_name(info.filename)
        archive.extractall(fresh)
    admit = run_checked([sys.executable, "scripts/build_and_admit.py", "--unit", "O017-U09"], fresh)
    final = run_checked([sys.executable, "scripts/finalize_course.py"], fresh)
    fresh_font_json = fresh / "qa" / ".fresh-font-audit.json"
    fresh_font_md = fresh / "qa" / ".fresh-font-audit.md"
    font_audit = run_checked(
        [
            sys.executable,
            "scripts/audit_pdf_font_accessibility.py",
            "--pdf",
            f"output/pdf/{PDF_NAME}",
            "--json-output",
            str(fresh_font_json),
            "--markdown-output",
            str(fresh_font_md),
        ],
        fresh,
    )
    observed_font = json.loads(fresh_font_json.read_text(encoding="utf-8"))
    expected_font = json.loads((fresh / PDF_FONT_QA.relative_to(ROOT)).read_text(encoding="utf-8"))
    for field in ("schema", "pdf", "logical_structure", "fonts"):
        if observed_font.get(field) != expected_font.get(field):
            fail(f"fresh extraction did not reproduce PDF font/tag field: {field}")
    font_provenance = run_checked(
        [
            sys.executable,
            "scripts/generate_font_component_provenance.py",
            "--pdf",
            f"output/pdf/{PDF_NAME}",
            "--audit",
            PDF_FONT_QA.relative_to(ROOT).as_posix(),
            "--check",
        ],
        fresh,
    )
    if directory_inventory(fresh / "build" / "html") != directory_inventory(HTML):
        fail("fresh extraction did not reproduce the exact reader tree")
    for name in (
        "records.jsonl",
        "relations.csv",
        "relations-ledger.csv",
        "schema.json",
        "manifest.csv",
        "semantic-wrapper-v1.baseline.json",
        "semantic-wrapper-v1.dataset.json",
        "semantic-wrapper-v1.localizations.jsonl",
        "semantic-wrapper-v1.records.jsonl",
        "semantic-wrapper-v1.relations-ledger.csv",
        "semantic-wrapper-v1.schema.json",
        "SEMANTIC_WRAPPER_V1.md",
    ):
        if (fresh / "backend" / name).read_bytes() != (ROOT / "backend" / name).read_bytes():
            fail(f"fresh extraction did not reproduce backend/{name}")
    for name in (
        "UNIT_09_QA.json",
        "UNIT_09_ADMISSION.md",
        "SEMANTIC_WRAPPER_QA.json",
        "FULL_COURSE_QA.json",
        "FULL_COURSE_ADMISSION.md",
    ):
        if (fresh / "qa" / name).read_bytes() != (QA / name).read_bytes():
            fail(f"fresh extraction did not reproduce qa/{name}")
    if directory_inventory(fresh / "delivery") != directory_inventory(ROOT / "delivery"):
        fail("fresh extraction did not preserve and validate the delivery package")
    if directory_inventory(fresh / "environment") != directory_inventory(ROOT / "environment"):
        fail("fresh extraction did not preserve the immutable environment package")
    return {
        "status": "PASS",
        "commands": [
            "python scripts/build_and_admit.py --unit O017-U09",
            "python scripts/finalize_course.py",
            f"python scripts/audit_pdf_font_accessibility.py --pdf output/pdf/{PDF_NAME} --json-output qa/.fresh-font-audit.json --markdown-output qa/.fresh-font-audit.md",
            f"python scripts/generate_font_component_provenance.py --pdf output/pdf/{PDF_NAME} --audit {PDF_FONT_QA.relative_to(ROOT).as_posix()} --check",
        ],
        "admission_stdout_sha256": sha256_bytes(admit.stdout.encode("utf-8")),
        "final_stdout_sha256": sha256_bytes(final.stdout.encode("utf-8")),
        "font_audit_stdout_sha256": sha256_bytes(font_audit.stdout.encode("utf-8")),
        "font_provenance_stdout_sha256": sha256_bytes(font_provenance.stdout.encode("utf-8")),
        "reader_tree": directory_inventory(HTML),
    }


def text_secret_scan(entries: dict[str, Path]) -> dict[str, object]:
    suffixes = {".md", ".txt", ".json", ".jsonl", ".csv", ".py", ".cjs", ".qmd", ".yml", ".yaml", ".bib"}
    # Split the literals so this verifier does not flag its own source text.
    patterns = (
        "gh" + "p_",
        "github" + "_pat_",
        "authorization:" + " bearer",
        '"access' + '_token"',
        "zenodo" + " token",
    )
    checked = 0
    for name, path in entries.items():
        if PurePosixPath(name).suffix.lower() not in suffixes and PurePosixPath(name).name != "Containerfile":
            continue
        checked += 1
        text = path.read_text(encoding="utf-8", errors="ignore").casefold()
        for pattern in patterns:
            if pattern in text:
                fail(f"credential marker found in public text input: {name}")
    return {"status": "PASS", "text_files_checked": checked, "patterns": list(patterns)}


def validate_full_course_qa(extension_validation: dict[str, object]) -> dict[str, object]:
    path = QA / "FULL_COURSE_QA.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    expected_units = [unit.id for unit in COURSE.units]
    if value.get("status") != "PASS" or value.get("units") != expected_units:
        fail("full-course admission is not the exact nine-unit PASS")
    if value.get("version") != VERSION or value.get("date") != RELEASE_DATE:
        fail("full-course admission is not bound to the release version/date")

    receipts = value.get("unit_receipts")
    visual_receipts = value.get("visual_receipts")
    if not isinstance(receipts, dict) or not isinstance(visual_receipts, dict):
        fail("full-course admission lacks unit or visual receipt hashes")
    for unit in COURSE.units:
        row = receipts.get(unit.id)
        if not isinstance(row, dict):
            fail(f"full-course admission lacks receipt for {unit.id}")
        expected = {
            "html_sha256": sha256_file(HTML / unit.html_relative_path),
            "source_sha256": sha256_file(unit.source_path),
            "qa_sha256": sha256_file(QA / f"UNIT_{unit.ordinal:02d}_QA.json"),
            "admission_sha256": sha256_file(QA / f"UNIT_{unit.ordinal:02d}_ADMISSION.md"),
        }
        for field, digest in expected.items():
            if row.get(field) != digest:
                fail(f"full-course admission has stale {field} for {unit.id}")
        visual = QA / f"UNIT_{unit.ordinal:02d}_VISUAL_QA.json"
        if visual_receipts.get(unit.id) != sha256_file(visual):
            fail(f"full-course admission has stale visual receipt for {unit.id}")

    full_visual = QA / "FULL_READER_VISUAL_QA.json"
    if value.get("full_reader_visual", {}).get("sha256") != sha256_file(full_visual):
        fail("full-course admission has a stale full-reader visual receipt")
    metadata = ROOT / "release" / "zenodo_metadata.json"
    if value.get("metadata", {}).get("sha256") != sha256_file(metadata):
        fail("full-course admission has stale Zenodo metadata")
    if value.get("extensions") != extension_validation:
        fail("full-course admission has stale delivery/backend/environment validation")
    return value


def validate_pdf() -> dict[str, object]:
    if not PDF.is_file():
        fail(f"release PDF is missing: {PDF}")
    if not all(
        path.is_file()
        for path in (
            PDF_QA,
            PDF_VISUAL_QA,
            PDF_FONT_QA,
            PDF_FONT_QA_MD,
            PDF_ACCESSIBILITY_DISCLOSURE,
            FONT_PROVENANCE,
        )
    ):
        fail("PDF machine, visual, font/tag, disclosure, or provenance evidence is missing")
    value = json.loads(PDF_QA.read_text(encoding="utf-8"))
    pdf = value.get("pdf")
    front = value.get("front_matter")
    if value.get("status") != "PASS" or not isinstance(pdf, dict) or not isinstance(front, dict):
        fail("PDF QA is not a PASS with PDF and front-matter evidence")
    digest = sha256_file(PDF)
    pages = pdf.get("pages")
    if not isinstance(pages, int) or pages <= 128:
        fail("PDF QA does not preserve the 128-page spine plus delivery wrapper")
    expected_pdf = {
        "path": PDF.relative_to(ROOT).as_posix(),
        "bytes": PDF.stat().st_size,
        "sha256": digest,
        "pages": pages,
    }
    for field, expected in expected_pdf.items():
        if pdf.get(field) != expected:
            fail(f"PDF QA has stale or invalid {field}")
    if pdf.get("page_size", {}).get("name") != "A4" or pdf.get("encrypted") is not False:
        fail("PDF QA does not establish an unencrypted A4 PDF")
    if value.get("date") != RELEASE_DATE or front.get("version") != VERSION:
        fail("PDF QA is not bound to the release version/date")
    if value.get("visual_qa") != PDF_VISUAL_QA.relative_to(ROOT).as_posix():
        fail("PDF QA points to the wrong visual receipt")
    visual = PDF_VISUAL_QA.read_text(encoding="utf-8")
    for marker in ("- Status: `PASS`", PDF_NAME, digest, f"{pages} A4 pages"):
        if marker not in visual:
            fail(f"PDF visual QA lacks required identity marker: {marker}")

    font_audit = json.loads(PDF_FONT_QA.read_text(encoding="utf-8"))
    audit_pdf = font_audit.get("pdf", {})
    logical = font_audit.get("logical_structure", {})
    fonts = font_audit.get("fonts", {})
    for field, expected in expected_pdf.items():
        if audit_pdf.get(field) != expected:
            fail(f"PDF font/tag audit has stale or invalid {field}")
    if (
        font_audit.get("schema") != "o017-pdf-font-tag-audit-v1"
        or logical.get("tagged") is not False
        or logical.get("catalog_has_struct_tree_root") is not False
        or fonts.get("all_embedded") is not True
        or fonts.get("font_objects") != 16
        or fonts.get("without_to_unicode") != 1
    ):
        fail("PDF font/tag audit does not prove the frozen untagged, fully embedded state")
    provenance = json.loads(FONT_PROVENANCE.read_text(encoding="utf-8"))
    if provenance.get("schema") != "o017-font-component-provenance-v2":
        fail("font component provenance is not v2")
    provenance_pdf = provenance.get("audited_pdf", {})
    for field in ("path", "bytes", "sha256", "pages"):
        if provenance_pdf.get(field) != expected_pdf[field]:
            fail(f"font component provenance has stale PDF {field}")
    component_ids = {row.get("resource_id") for row in provenance.get("components", [])}
    if component_ids != {
        "O017-FONT-LM-TEXT",
        "O017-FONT-LM-MATH",
        "O017-FONT-FA5FREE",
        "O017-FONT-MSAM10",
    }:
        fail("font component provenance is not the exact four-family closure")
    disclosure = PDF_ACCESSIBILITY_DISCLOSURE.read_text(encoding="utf-8")
    for marker in ("belum", "untagged", "PDF/UA", "HTML"):
        if marker not in disclosure:
            fail(f"PDF accessibility disclosure lacks required marker: {marker}")
    return {
        "filename": PDF_NAME,
        "source_path": PDF.relative_to(ROOT).as_posix(),
        "bytes": PDF.stat().st_size,
        "sha256": digest,
        "pages": pages,
        "page_size": "A4",
        "machine_qa": {
            "path": PDF_QA.relative_to(ROOT).as_posix(),
            "bytes": PDF_QA.stat().st_size,
            "sha256": sha256_file(PDF_QA),
        },
        "visual_qa": {
            "path": PDF_VISUAL_QA.relative_to(ROOT).as_posix(),
            "bytes": PDF_VISUAL_QA.stat().st_size,
            "sha256": sha256_file(PDF_VISUAL_QA),
        },
        "font_tag_audit": {
            "path": PDF_FONT_QA.relative_to(ROOT).as_posix(),
            "bytes": PDF_FONT_QA.stat().st_size,
            "sha256": sha256_file(PDF_FONT_QA),
            "tagged": False,
            "font_objects": 16,
        },
        "font_provenance": {
            "path": FONT_PROVENANCE.relative_to(ROOT).as_posix(),
            "bytes": FONT_PROVENANCE.stat().st_size,
            "sha256": sha256_file(FONT_PROVENANCE),
        },
        "accessibility_disclosure": {
            "path": PDF_ACCESSIBILITY_DISCLOSURE.relative_to(ROOT).as_posix(),
            "bytes": PDF_ACCESSIBILITY_DISCLOSURE.stat().st_size,
            "sha256": sha256_file(PDF_ACCESSIBILITY_DISCLOSURE),
        },
    }


def copy_release_document(name: str) -> Path:
    source = ROOT / name
    target = RELEASE / name
    shutil.copyfile(source, target)
    if source.read_bytes() != target.read_bytes():
        fail(f"loose release document copy differs: {name}")
    return target


def copy_release_pdf() -> Path:
    target = RELEASE / PDF_NAME
    shutil.copyfile(PDF, target)
    if PDF.read_bytes() != target.read_bytes():
        fail("loose release PDF copy differs from the validated PDF")
    return target


def main() -> None:
    extension_validation = validate_extension_packages()
    validate_full_course_qa(extension_validation)
    pdf_result = validate_pdf()
    reader = reader_entries()
    source, screenshot_count = source_entries()
    secret_scan = text_secret_scan(source)
    RELEASE.mkdir(parents=True, exist_ok=True)
    temp = RELEASE / f".build-release-{os.getpid()}"
    if temp.exists():
        fail(f"refusing to reuse release temp path: {temp}")
    temp.mkdir()
    try:
        archive_results: list[dict[str, object]] = []
        for name, label, entries in (
            (READER_NAME, "offline-html-reader", reader),
            (SOURCE_NAME, "source-backend-evidence", source),
        ):
            first = temp / f"first-{name}"
            second = temp / f"second-{name}"
            write_archive(first, label, entries)
            write_archive(second, label, entries)
            first_result = verify_archive(first, label, entries)
            second_result = verify_archive(second, label, entries)
            if first.read_bytes() != second.read_bytes() or first_result["sha256"] != second_result["sha256"]:
                fail(f"two deterministic archive builds differ: {name}")
            target = RELEASE / name
            os.replace(first, target)
            verified = verify_archive(target, label, entries)
            verified["second_build_sha256"] = second_result["sha256"]
            verified["byte_identical_builds"] = True
            archive_results.append(verified)

        fresh = fresh_extraction_check(RELEASE / SOURCE_NAME, temp)
        pdf_payload = copy_release_pdf()
        documents = [copy_release_document(name) for name in ("README.md", "LICENSES.md", "THIRD_PARTY_NOTICES.md", "CITATION.cff")]
        primary_payloads = [pdf_payload, RELEASE / READER_NAME, RELEASE / SOURCE_NAME, *documents]
        primary_inventory = [
            {"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in primary_payloads
        ]
        sums = "".join(f"{sha256_file(path)}  {path.name}\n" for path in primary_payloads).encode("utf-8")
        sums_path = RELEASE / "SHA256SUMS.txt"
        sums_path.write_bytes(sums)
        receipt = {
            "schema": "o017-release-package-qa-v1",
            "status": "PASS",
            "date": RELEASE_DATE,
            "version": VERSION,
            "edition_id": "O017-EDITION-01",
            "curriculum_selection": "separate from edition completion; no sunk-work inference",
            "archives": archive_results,
            "source_archive_screenshots_referenced": screenshot_count,
            "fresh_extraction": fresh,
            "credential_scan": secret_scan,
            "pdf": pdf_result,
            "primary_payloads": {
                "file_count": len(primary_payloads),
                "total_bytes": sum(path.stat().st_size for path in primary_payloads),
                "files": primary_inventory,
            },
            "expected_zenodo_upload_file_count": len(primary_payloads) + 2,
            "sha256sums": {
                "filename": sums_path.name,
                "bytes": sums_path.stat().st_size,
                "sha256": sha256_file(sums_path),
                "covered_file_count": len(primary_payloads),
                "first_filename": PDF_NAME,
            },
            "hard_exclusions": [
                "credentials and token files",
                "authority donor witness trees",
                "source/.quarto and generated source HTML/site_libs",
                "Python caches and transient render stages",
                "obsolete unit-specific build/browser scripts",
                "internal CURRENT_STATE, CURSOR, and DECISIONS controls",
                "stale determinism receipts and unreferenced screenshots",
            ],
        }
        receipt_path = RELEASE / "RELEASE_PACKAGE_QA.json"
        receipt_path.write_bytes(json_bytes(receipt))
        uploads = [*primary_payloads, sums_path, receipt_path]
        if uploads[0].name != PDF_NAME or len(uploads) != receipt["expected_zenodo_upload_file_count"]:
            fail("Zenodo payload order or file count is not the validated release plan")
        upload_manifest = {
            "schema": "o017-files-to-upload-v1",
            "destination": "Zenodo",
            "file_count": len(uploads),
            "pdf_first": True,
            "files": [
                {"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
                for path in uploads
            ],
        }
        (RELEASE / "FILES_TO_UPLOAD.json").write_bytes(json_bytes(upload_manifest))
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "archives": archive_results,
                    "fresh_extraction": fresh["status"],
                    "upload_files": len(uploads),
                    "release_receipt_sha256": sha256_file(receipt_path),
                    "files_to_upload_sha256": sha256_file(RELEASE / "FILES_TO_UPLOAD.json"),
                },
                sort_keys=True,
            )
        )
    finally:
        if temp.exists():
            shutil.rmtree(temp)


if __name__ == "__main__":
    main()
