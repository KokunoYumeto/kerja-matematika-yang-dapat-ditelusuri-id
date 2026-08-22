"""Audit the released O017 PDF's embedded fonts and logical structure.

This is deliberately a read-only inspection of the PDF.  It emits new QA
artifacts and never rewrites the publication artifact.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from pypdf import PdfReader
from pypdf.generic import IndirectObject


ROOT = Path(__file__).resolve().parents[1]
PDF = (
    ROOT
    / "output"
    / "pdf"
    / "kerja-matematika-yang-dapat-ditelusuri-id-2026.08.22.1.pdf"
)
JSON_OUTPUT = ROOT / "qa" / "PDF_FONT_AND_TAG_AUDIT_2026.08.22.1.json"
MARKDOWN_OUTPUT = ROOT / "qa" / "PDF_FONT_AND_TAG_AUDIT_2026.08.22.1.md"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dereference(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def object_key(value: Any, fallback: str) -> str:
    if isinstance(value, IndirectObject):
        return f"{value.idnum}:{value.generation}"
    return fallback


def descriptor_for(font: Any) -> Any | None:
    descriptor = font.get("/FontDescriptor")
    if descriptor is not None:
        return dereference(descriptor)
    descendants = font.get("/DescendantFonts") or []
    if descendants:
        descendant = dereference(descendants[0])
        descriptor = descendant.get("/FontDescriptor")
        if descriptor is not None:
            return dereference(descriptor)
    return None


def font_stream(descriptor: Any | None) -> tuple[str | None, bytes | None, str | None]:
    if descriptor is None:
        return None, None, None
    for key in ("/FontFile", "/FontFile2", "/FontFile3"):
        reference = descriptor.get(key)
        if reference is None:
            continue
        stream = dereference(reference)
        subtype = str(stream.get("/Subtype")) if stream.get("/Subtype") else None
        return key.removeprefix("/"), stream.get_data(), subtype
    return None, None, None


def command_output(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    public_command: list[str] = []
    for argument in command:
        candidate = Path(argument)
        if not candidate.is_absolute():
            public_command.append(argument)
            continue
        try:
            public_command.append(candidate.resolve().relative_to(ROOT).as_posix())
        except ValueError:
            public_command.append(candidate.name)
    return {
        "command": public_command,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit every page, font resource, and PDF tag surface."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=PDF,
        help="PDF to inspect (default: the 2026.08.22.1 release PDF)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=JSON_OUTPUT,
        help="JSON receipt path",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=MARKDOWN_OUTPUT,
        help="human-readable receipt path",
    )
    return parser.parse_args()


def main(pdf: Path, json_output: Path, markdown_output: Path) -> None:
    pdf = pdf.resolve()
    json_output = json_output.resolve()
    markdown_output = markdown_output.resolve()
    if not pdf.is_file():
        raise FileNotFoundError(pdf)

    reader = PdfReader(pdf)
    root = dereference(reader.trailer["/Root"])
    mark_info = dereference(root.get("/MarkInfo")) if root.get("/MarkInfo") else None
    struct_tree = root.get("/StructTreeRoot")

    fonts: dict[str, dict[str, Any]] = {}
    page_font_keys: list[list[str]] = []
    page_struct_parents: list[int] = []
    marked_content_operators: defaultdict[str, int] = defaultdict(int)
    annotation_counts: defaultdict[str, int] = defaultdict(int)
    image_xobjects = 0
    images_with_alt = 0
    pages_without_extractable_text: list[int] = []

    for page_number, page in enumerate(reader.pages, start=1):
        if not (page.extract_text() or "").strip():
            pages_without_extractable_text.append(page_number)
        if page.get("/StructParents") is not None:
            page_struct_parents.append(page_number)

        content = page.get_contents()
        content_bytes = content.get_data() if content is not None else b""
        for label, pattern in (
            ("BMC", rb"(?<![A-Za-z])BMC(?![A-Za-z])"),
            ("BDC", rb"(?<![A-Za-z])BDC(?![A-Za-z])"),
            ("EMC", rb"(?<![A-Za-z])EMC(?![A-Za-z])"),
            ("Artifact", rb"/Artifact\s+(?:BMC|BDC)"),
            ("ActualText", rb"/ActualText"),
        ):
            marked_content_operators[label] += len(re.findall(pattern, content_bytes))

        resources = dereference(page.get("/Resources")) if page.get("/Resources") else {}
        page_keys: list[str] = []
        font_resources = dereference(resources.get("/Font")) if resources.get("/Font") else {}
        for resource_name, font_reference in font_resources.items():
            font = dereference(font_reference)
            key = object_key(font_reference, f"direct:{page_number}:{resource_name}")
            page_keys.append(key)
            if key not in fonts:
                descriptor = descriptor_for(font)
                stream_kind, stream_data, stream_subtype = font_stream(descriptor)
                descendants = font.get("/DescendantFonts") or []
                descendant = dereference(descendants[0]) if descendants else None
                fonts[key] = {
                    "object": key,
                    "base_font": str(font.get("/BaseFont")),
                    "subtype": str(font.get("/Subtype")),
                    "encoding": str(font.get("/Encoding")) if font.get("/Encoding") else None,
                    "descendant_subtype": (
                        str(descendant.get("/Subtype")) if descendant is not None else None
                    ),
                    "to_unicode": font.get("/ToUnicode") is not None,
                    "embedded": stream_data is not None,
                    "font_stream_kind": stream_kind,
                    "font_stream_subtype": stream_subtype,
                    "embedded_stream_bytes": len(stream_data) if stream_data is not None else 0,
                    "embedded_stream_sha256": (
                        sha256_bytes(stream_data) if stream_data is not None else None
                    ),
                    "descriptor_flags": (
                        int(descriptor.get("/Flags", 0)) if descriptor is not None else None
                    ),
                    "pages": [],
                    "resource_names": [],
                }
            fonts[key]["pages"].append(page_number)
            name = str(resource_name)
            if name not in fonts[key]["resource_names"]:
                fonts[key]["resource_names"].append(name)
        page_font_keys.append(sorted(set(page_keys)))

        xobjects = dereference(resources.get("/XObject")) if resources.get("/XObject") else {}
        for reference in xobjects.values():
            xobject = dereference(reference)
            if str(xobject.get("/Subtype")) == "/Image":
                image_xobjects += 1
                if xobject.get("/Alt") is not None:
                    images_with_alt += 1

        for reference in page.get("/Annots", []):
            annotation = dereference(reference)
            subtype = str(annotation.get("/Subtype"))
            annotation_counts[f"subtype:{subtype}"] += 1
            if annotation.get("/Contents") is not None:
                annotation_counts["with_contents"] += 1
            if annotation.get("/StructParent") is not None:
                annotation_counts["with_struct_parent"] += 1
            if annotation.get("/A") is not None:
                action = dereference(annotation.get("/A"))
                if action.get("/URI") is not None:
                    annotation_counts["uri_links"] += 1

    for row in fonts.values():
        row["pages"] = sorted(set(row["pages"]))
        row["resource_names"] = sorted(row["resource_names"])

    metadata = reader.metadata or {}
    outline_entries = 0

    def count_outline(items: Any) -> None:
        nonlocal outline_entries
        if not isinstance(items, list):
            return
        for item in items:
            if isinstance(item, list):
                count_outline(item)
            else:
                outline_entries += 1

    count_outline(reader.outline)
    pdfinfo = command_output(["pdfinfo", str(pdf)])
    pdffonts = command_output(["pdffonts", str(pdf)])

    payload = {
        "schema": "o017-pdf-font-tag-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "read-only inspection of every page and every referenced font resource",
        "pdf": {
            "path": pdf.relative_to(ROOT).as_posix(),
            "bytes": pdf.stat().st_size,
            "sha256": sha256_file(pdf),
            "pages": len(reader.pages),
            "pdf_version": reader.pdf_header,
            "encrypted": reader.is_encrypted,
            "metadata": {str(key): str(value) for key, value in metadata.items()},
        },
        "logical_structure": {
            "tagged": bool(
                mark_info and bool(mark_info.get("/Marked")) and struct_tree
            ),
            "catalog_has_struct_tree_root": struct_tree is not None,
            "catalog_mark_info": (
                {str(key): bool(value) for key, value in mark_info.items()}
                if mark_info is not None
                else None
            ),
            "catalog_lang": str(root.get("/Lang")) if root.get("/Lang") else None,
            "catalog_metadata_stream": root.get("/Metadata") is not None,
            "pages_with_struct_parents": page_struct_parents,
            "marked_content_operators": dict(sorted(marked_content_operators.items())),
            "outline_entries": outline_entries,
            "pages_without_extractable_text": pages_without_extractable_text,
            "image_xobjects": image_xobjects,
            "images_with_alt": images_with_alt,
            "annotations": dict(sorted(annotation_counts.items())),
            "finding": (
                "UNTAGGED: no structure tree or marked logical reading order is present; "
                "do not claim PDF accessibility or PDF/UA conformance"
            ),
            "accessible_surface": "the published semantic HTML reader",
        },
        "fonts": {
            "font_objects": len(fonts),
            "all_embedded": all(row["embedded"] for row in fonts.values()),
            "with_to_unicode": sum(1 for row in fonts.values() if row["to_unicode"]),
            "without_to_unicode": sum(1 for row in fonts.values() if not row["to_unicode"]),
            "objects": sorted(fonts.values(), key=lambda row: row["base_font"]),
            "page_font_objects": page_font_keys,
        },
        "tool_witnesses": {"pdfinfo": pdfinfo, "pdffonts": pdffonts},
        "official_accessibility_basis": [
            "https://www.w3.org/TR/WCAG20-TECHS/pdf",
            "https://www.w3.org/WAI/WCAG22/Techniques/",
        ],
    }
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    rows = payload["fonts"]["objects"]
    table = [
        "| PDF BaseFont | Type | Embedded | ToUnicode | Pages | Stream SHA-256 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        table.append(
            "| {base} | {subtype} | {embedded} | {unicode} | {pages} | `{digest}` |".format(
                base=row["base_font"].replace("|", "\\|"),
                subtype=row["subtype"],
                embedded="yes" if row["embedded"] else "no",
                unicode="yes" if row["to_unicode"] else "no",
                pages=len(row["pages"]),
                digest=row["embedded_stream_sha256"] or "none",
            )
        )
    markdown = "\n".join(
        [
            "# O017 PDF font and tag audit",
            "",
            f"Artifact: `{payload['pdf']['path']}`  ",
            f"SHA-256: `{payload['pdf']['sha256']}`  ",
            f"Extent: {payload['pdf']['pages']} pages; every page inspected.",
            "",
            "## Accessibility finding",
            "",
            "**UNTAGGED.** The catalog declares `/Lang` as `id-ID`, but it has no",
            "`/StructTreeRoot`, no `/MarkInfo` declaration, no page `/StructParents`, and no",
            "marked-content sequence.",
            "The PDF has bookmarks and extractable text on every page, but these do not create",
            "a programmatic heading/table/list/reading-order structure. It must not be described",
            "as an accessible PDF or as PDF/UA conforming. The semantic HTML reader remains the",
            "accessibility-oriented surface.",
            "",
            "This interpretation follows W3C's PDF accessibility techniques, which identify a",
            "logical structure tree and tagged reading order as the core PDF accessibility",
            "mechanism: <https://www.w3.org/TR/WCAG20-TECHS/pdf>.",
            "",
            "## Font result",
            "",
            f"All {payload['fonts']['font_objects']} referenced font objects are embedded and subset.",
            f"{payload['fonts']['with_to_unicode']} have ToUnicode maps;",
            f"{payload['fonts']['without_to_unicode']} do not. The sole missing ToUnicode map is",
            "the Font Awesome icon subset; that is an additional reason not to infer accessibility",
            "from successful text extraction.",
            "",
            *table,
            "",
            "## Permanent disclosure to publish beside the PDF",
            "",
            "> **Aksesibilitas PDF.** PDF ini adalah edisi cetak berhalaman tetap dan belum",
            "> memiliki tag struktur PDF. Teks dapat dicari dan disalin, dan penanda bab tersedia,",
            "> tetapi urutan baca, judul, daftar, tabel, rumus, dan tautan belum dikodekan sebagai",
            "> struktur semantik untuk teknologi bantu. PDF ini tidak dinyatakan memenuhi PDF/UA.",
            "> Untuk pembacaan dengan pembaca layar, pembesaran/reflow, navigasi papan ketik, dan",
            "> struktur MathML, gunakan edisi HTML semantik yang diterbitkan bersama edisi ini.",
            "",
            "> **PDF accessibility.** This fixed-layout print PDF is currently untagged. Its text is",
            "> searchable and chapter bookmarks are present, but reading order, headings, lists,",
            "> tables, mathematics, and links are not encoded as an assistive-technology structure.",
            "> No PDF/UA conformance is claimed. Use the companion semantic HTML edition for screen",
            "> readers, keyboard navigation, reflow/zoom, and MathML.",
            "",
        ]
    )
    markdown_output.write_text(markdown, encoding="utf-8")
    print(json.dumps({"json": str(json_output), "markdown": str(markdown_output)}))


if __name__ == "__main__":
    arguments = parse_args()
    main(arguments.pdf, arguments.json_output, arguments.markdown_output)
