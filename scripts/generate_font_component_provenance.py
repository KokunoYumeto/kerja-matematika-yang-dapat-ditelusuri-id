"""Regenerate O017 embedded-font provenance from an exact PDF audit.

The generator is deliberately closed over the four font families whose
authority and licenses were independently frozen for this edition. Unknown or
missing families, unembedded fonts, stale audit/PDF identities, malformed font
streams, and changed local notice files are hard failures.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROVENANCE = ROOT / "licenses" / "FONT_COMPONENT_PROVENANCE.json"
DEFAULT_RIGHTS_MAP = ROOT / "integration" / "FONT_RIGHTS_MAP_ADDITIONS_DRAFT.csv"

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
SUBSET_PREFIX = re.compile(r"^/?[A-Z]{6}\+")

LOCAL_AUTHORITIES = {
    "licenses/GUST-FONT-LICENSE-1.0.txt": {
        "bytes": 1378,
        "sha256": "2f9a825a9e7dba348e1ae6948205adcd642bffbb424b39887b65eba9a954c74e",
    },
    "licenses/LATIN-MODERN-MATH-1.959-README.txt": {
        "bytes": 4589,
        "sha256": "31fe626862783454878e4fb82192d92f30a62fa46d2d547bdde7aa92a3ada90a",
    },
    "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt": {
        "bytes": 1549,
        "sha256": "465b9cc2950960b0f70cca23b57f10a463f0d4a05df30a8aa3b3d43fded5b0c5",
    },
    "licenses/SIL-OFL-1.1.txt": {
        "bytes": 4600,
        "sha256": "82585c35736ce06aae32a5678143b93b4714ac1a670f72f0aea9effefbb6f20c",
    },
    "licenses/AMSFonts-3.04-README.txt": {
        "bytes": 14650,
        "sha256": "17ca44f214cb44fd3cc8d29e4da90f28ad8850938eb4c242cb80e62baea0a24e",
    },
    "licenses/AMSFonts-3.04-OFL.txt": {
        "bytes": 12521,
        "sha256": "c3bf4641d82fcfcaf9fe0b1cf02fc05dd8e9ff064ddda4b58bc1f658717f2465",
    },
}

COMPONENTS: dict[str, dict[str, Any]] = {
    "O017-FONT-LM-TEXT": {
        "component": "Latin Modern text fonts",
        "version": "2.004",
        "copyright_notice": (
            "Copyright 2003, 2009 B. Jackowski and J. M. Nowacki "
            "(on behalf of TeX users groups)."
        ),
        "license": (
            "GUST Font License 1.0: LPPL 1.3c or later, plus the nonbinding "
            "font/file-name change request"
        ),
        "official_package": "https://ctan.org/pkg/lm",
        "official_license_url": (
            "https://www.tug.org/fonts/licenses/GUST-FONT-LICENSE.txt"
        ),
        "official_license_download_bytes": 1377,
        "official_license_download_sha256": (
            "49ea6cb9257bbee0a3979c48a774cd221550ac1c20c95549efe45fc99cc18050"
        ),
        "local_license": "licenses/GUST-FONT-LICENSE-1.0.txt",
        "local_license_bytes": 1378,
        "local_license_sha256": (
            "2f9a825a9e7dba348e1ae6948205adcd642bffbb424b39887b65eba9a954c74e"
        ),
        "local_transformation": (
            "Official UTF-8 text preserved verbatim with one terminal LF added."
        ),
        "rights_repository": "https://ctan.org/pkg/lm",
        "rights_commit": "2.004",
        "rights_license": (
            "GUST Font License 1.0: LPPL 1.3c or later plus nonbinding "
            "name-change request"
        ),
        "rights_local_authority": "licenses/GUST-FONT-LICENSE-1.0.txt",
    },
    "O017-FONT-LM-MATH": {
        "component": "Latin Modern Math",
        "version": "1.959",
        "copyright_notice": (
            "Copyright 2012--2014 for the Latin Modern math extensions by "
            "B. Jackowski, P. Strzelczyk and P. Pianowski (on behalf of TeX "
            "Users Groups)."
        ),
        "license": (
            "GUST Font License 1.0: LPPL 1.3c or later, plus the nonbinding "
            "font/file-name change request"
        ),
        "official_package": "https://ctan.org/pkg/lm-math",
        "official_readme_url": "https://mirrors.ctan.org/fonts/lm-math/README",
        "official_readme_download_bytes": 4588,
        "official_readme_download_sha256": (
            "e6fdd5fb44b656146fa988d191f58901c09a347d3f4fbaa3b45b24a6ad7ec30b"
        ),
        "local_readme": "licenses/LATIN-MODERN-MATH-1.959-README.txt",
        "local_readme_bytes": 4589,
        "local_readme_sha256": (
            "31fe626862783454878e4fb82192d92f30a62fa46d2d547bdde7aa92a3ada90a"
        ),
        "local_readme_transformation": (
            "Official UTF-8 text preserved verbatim with one terminal LF added."
        ),
        "local_license": "licenses/GUST-FONT-LICENSE-1.0.txt",
        "local_license_sha256": (
            "2f9a825a9e7dba348e1ae6948205adcd642bffbb424b39887b65eba9a954c74e"
        ),
        "rights_repository": "https://ctan.org/pkg/lm-math",
        "rights_commit": "1.959",
        "rights_license": (
            "GUST Font License 1.0: LPPL 1.3c or later plus nonbinding "
            "name-change request"
        ),
        "rights_local_authority": "licenses/LATIN-MODERN-MATH-1.959-README.txt",
    },
    "O017-FONT-FA5FREE": {
        "component": "Font Awesome 5 Free Solid font",
        "version": "5.15.4",
        "copyright_notice": "Copyright (c) Font Awesome.",
        "license": "SIL Open Font License 1.1 for the font file",
        "official_release": (
            "https://github.com/FortAwesome/Font-Awesome/tree/5.15.4"
        ),
        "official_component_license_url": (
            "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/"
            "5.15.4/LICENSE.txt"
        ),
        "official_component_license_download_bytes": 1548,
        "official_component_license_download_sha256": (
            "e779748dfe75e84f974df3c7bc07f842011a100159158b0f1f49b2f2a5a515cb"
        ),
        "local_component_license": (
            "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt"
        ),
        "local_component_license_bytes": 1549,
        "local_component_license_sha256": (
            "465b9cc2950960b0f70cca23b57f10a463f0d4a05df30a8aa3b3d43fded5b0c5"
        ),
        "local_component_license_transformation": (
            "Official UTF-8 text preserved verbatim with one terminal LF added."
        ),
        "official_ofl_url": "https://openfontlicense.org/documents/OFL.txt",
        "official_ofl_download_bytes": 4599,
        "official_ofl_download_sha256": (
            "1d361a8f8e8ce6e68457dcd93fb56e162e6baa3bbb7e7573a290d44399f6b57e"
        ),
        "local_ofl": "licenses/SIL-OFL-1.1.txt",
        "local_ofl_bytes": 4600,
        "local_ofl_sha256": (
            "82585c35736ce06aae32a5678143b93b4714ac1a670f72f0aea9effefbb6f20c"
        ),
        "local_ofl_transformation": (
            "Official UTF-8 text preserved verbatim with one terminal LF added."
        ),
        "rights_repository": "https://github.com/FortAwesome/Font-Awesome",
        "rights_commit": "5.15.4",
        "rights_license": "SIL Open Font License 1.1",
        "rights_local_authority": (
            "licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt"
        ),
    },
    "O017-FONT-MSAM10": {
        "component": "AMSFonts MSAM10 Type 1 font",
        "version": "003.002 (within AMSFonts 3.04)",
        "copyright_notice": (
            "Copyright (c) 1997, 2009, American Mathematical Society "
            "(http://www.ams.org). All Rights Reserved."
        ),
        "reserved_font_name": "msam10",
        "license": "SIL Open Font License 1.1",
        "official_package": "https://ctan.org/pkg/amsfonts",
        "official_readme_url": "https://mirrors.ctan.org/fonts/amsfonts/README",
        "official_readme_download_bytes": 14649,
        "official_readme_download_sha256": (
            "2e2ced3494d3e5f04345804b85c1acb67c23bdd742f3e71f8772f768a59ed451"
        ),
        "local_readme": "licenses/AMSFonts-3.04-README.txt",
        "local_readme_bytes": 14650,
        "local_readme_sha256": (
            "17ca44f214cb44fd3cc8d29e4da90f28ad8850938eb4c242cb80e62baea0a24e"
        ),
        "official_package_ofl_url": (
            "https://mirrors.ctan.org/fonts/amsfonts/doc/OFL.txt"
        ),
        "official_package_ofl_download_bytes": 12520,
        "official_package_ofl_download_sha256": (
            "aa783fdd47e92743bafe79277ac4067d20339344dc5b64a09c2d0f869b2999dc"
        ),
        "local_package_ofl": "licenses/AMSFonts-3.04-OFL.txt",
        "local_package_ofl_bytes": 12521,
        "local_package_ofl_sha256": (
            "c3bf4641d82fcfcaf9fe0b1cf02fc05dd8e9ff064ddda4b58bc1f658717f2465"
        ),
        "local_text_transformation": (
            "Each official UTF-8 text was preserved verbatim with one terminal LF "
            "added."
        ),
        "rights_repository": "https://ctan.org/pkg/amsfonts",
        "rights_commit": "003.002 (AMSFonts 3.04)",
        "rights_license": "SIL Open Font License 1.1",
        "rights_local_authority": "licenses/AMSFonts-3.04-OFL.txt",
    },
}

COMPONENT_ORDER = tuple(COMPONENTS)
RIGHTS_FIELDS = (
    "resource_id",
    "title",
    "repository",
    "commit",
    "tree",
    "license",
    "role",
    "status",
    "selected_files",
    "selected_bytes",
    "selected_manifest_sha256",
    "local_authority",
    "release_bundled",
    "release_evidence",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_path(value: Path) -> Path:
    return value.resolve() if value.is_absolute() else (Path.cwd() / value).resolve()


def require_output_in_root(path: Path) -> None:
    if path != ROOT and ROOT not in path.parents:
        raise RuntimeError(f"output must remain inside edition root: {path}")


def verify_local_authorities() -> None:
    for relative, expected in LOCAL_AUTHORITIES.items():
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"missing frozen local authority: {relative}")
        actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if actual != expected:
            raise RuntimeError(
                f"changed frozen local authority {relative}: "
                f"expected {expected}, observed {actual}"
            )


def classify(base_font: str) -> str:
    normalized = SUBSET_PREFIX.sub("", base_font)
    if normalized.startswith(("LMRoman", "LMMono", "LMSans")):
        return "O017-FONT-LM-TEXT"
    if normalized.startswith("LatinModernMath"):
        return "O017-FONT-LM-MATH"
    if normalized.startswith("FontAwesome5Free-Solid"):
        return "O017-FONT-FA5FREE"
    if normalized == "MSAM10" or normalized.startswith("MSAM10-"):
        return "O017-FONT-MSAM10"
    raise RuntimeError(f"unknown embedded font family: {base_font!r}")


def validate_and_group(
    pdf: Path, audit_path: Path, audit: dict[str, Any]
) -> tuple[str, dict[str, list[dict[str, Any]]]]:
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    actual_pdf = {
        "bytes": pdf.stat().st_size,
        "sha256": sha256_file(pdf),
    }
    audit_pdf = audit.get("pdf")
    if not isinstance(audit_pdf, dict):
        raise RuntimeError("audit has no PDF identity object")
    for field, value in actual_pdf.items():
        if audit_pdf.get(field) != value:
            raise RuntimeError(
                f"audit/PDF {field} mismatch: audit={audit_pdf.get(field)!r}, "
                f"actual={value!r}"
            )
    pdf_display = display_path(pdf)
    if audit_pdf.get("path") != pdf_display:
        raise RuntimeError(
            f"audit/PDF path mismatch: audit={audit_pdf.get('path')!r}, "
            f"actual={pdf_display!r}"
        )

    fonts = audit.get("fonts")
    if not isinstance(fonts, dict) or not isinstance(fonts.get("objects"), list):
        raise RuntimeError("audit has no font object list")
    objects = fonts["objects"]
    if fonts.get("font_objects") != len(objects):
        raise RuntimeError("audit font-object count disagrees with its object list")
    if not objects or fonts.get("all_embedded") is not True:
        raise RuntimeError("audit does not prove a nonempty, fully embedded font set")

    groups: dict[str, list[dict[str, Any]]] = {
        component_id: [] for component_id in COMPONENT_ORDER
    }
    seen_objects: set[str] = set()
    for row in objects:
        if not isinstance(row, dict):
            raise RuntimeError("malformed font-object row")
        base_font = row.get("base_font")
        object_id = row.get("object")
        stream_bytes = row.get("embedded_stream_bytes")
        stream_hash = row.get("embedded_stream_sha256")
        if not isinstance(base_font, str) or not base_font.startswith("/"):
            raise RuntimeError(f"malformed PDF BaseFont: {base_font!r}")
        if not isinstance(object_id, str) or object_id in seen_objects:
            raise RuntimeError(f"missing or duplicate font object identity: {object_id!r}")
        seen_objects.add(object_id)
        if row.get("embedded") is not True:
            raise RuntimeError(f"unembedded font object: {base_font}")
        if not isinstance(stream_bytes, int) or isinstance(stream_bytes, bool) or stream_bytes <= 0:
            raise RuntimeError(f"invalid embedded stream size for {base_font}: {stream_bytes!r}")
        if not isinstance(stream_hash, str) or not HEX_SHA256.fullmatch(stream_hash):
            raise RuntimeError(f"invalid embedded stream hash for {base_font}: {stream_hash!r}")
        groups[classify(base_font)].append(row)

    missing = [component_id for component_id, rows in groups.items() if not rows]
    if missing:
        raise RuntimeError(f"missing frozen embedded font families: {missing}")
    return display_path(audit_path), groups


def component_manifest(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    ordered = sorted(
        rows,
        key=lambda row: (
            row["base_font"],
            row["embedded_stream_sha256"],
            row["object"],
        ),
    )
    canonical = "".join(
        f"{row['base_font']}\t{row['embedded_stream_bytes']}\t"
        f"{row['embedded_stream_sha256']}\n"
        for row in ordered
    ).encode("utf-8")
    streams = [
        {
            "object": row["object"],
            "base_font": row["base_font"],
            "embedded_stream_bytes": row["embedded_stream_bytes"],
            "embedded_stream_sha256": row["embedded_stream_sha256"],
            "to_unicode": bool(row.get("to_unicode")),
        }
        for row in ordered
    ]
    return streams, sha256_bytes(canonical)


def generate(
    pdf: Path, audit_path: Path, audit: dict[str, Any]
) -> tuple[bytes, bytes, dict[str, Any]]:
    audit_display, groups = validate_and_group(pdf, audit_path, audit)
    pdf_identity = audit["pdf"]
    component_rows: list[dict[str, Any]] = []
    rights_rows: list[dict[str, Any]] = []

    for component_id in COMPONENT_ORDER:
        facts = COMPONENTS[component_id]
        streams, component_hash = component_manifest(groups[component_id])
        component: dict[str, Any] = {
            "resource_id": component_id,
            "component": facts["component"],
            "version": facts["version"],
            "embedded_pdf_objects": len(streams),
            "embedded_stream_bytes": sum(
                row["embedded_stream_bytes"] for row in streams
            ),
            "component_manifest_sha256": component_hash,
            "base_fonts": [row["base_font"] for row in streams],
            "embedded_streams": streams,
        }
        component.update(
            {
                key: value
                for key, value in facts.items()
                if not key.startswith("rights_")
                and key not in {"component", "version"}
            }
        )
        component_rows.append(component)
        rights_rows.append(
            {
                "resource_id": component_id,
                "title": facts["component"],
                "repository": facts["rights_repository"],
                "commit": facts["rights_commit"],
                "tree": "",
                "license": facts["rights_license"],
                "role": "embedded PDF font component",
                "status": "FONT_RIGHTS_FROZEN",
                "selected_files": str(len(streams)),
                "selected_bytes": str(component["embedded_stream_bytes"]),
                "selected_manifest_sha256": component_hash,
                "local_authority": facts["rights_local_authority"],
                "release_bundled": "true",
                "release_evidence": (
                    "licenses/FONT_COMPONENT_PROVENANCE.json; " + audit_display
                ),
            }
        )

    provenance = {
        "schema": "o017-font-component-provenance-v2",
        "audited_pdf": {
            "path": display_path(pdf),
            "bytes": pdf_identity["bytes"],
            "sha256": pdf_identity["sha256"],
            "pages": pdf_identity["pages"],
            "font_objects": audit["fonts"]["font_objects"],
            "all_embedded": True,
            "full_audit": audit_display,
        },
        "component_manifest_algorithm": (
            "Sort by PDF BaseFont, embedded stream SHA-256, then PDF object "
            "identity; for each object encode BaseFont, TAB, embedded stream byte "
            "count, TAB, embedded stream SHA-256, LF as UTF-8; SHA-256 the "
            "concatenation."
        ),
        "components": component_rows,
        "official_accessibility_sources": [
            "https://www.w3.org/TR/WCAG20-TECHS/pdf",
            "https://www.w3.org/WAI/WCAG22/Techniques/",
        ],
    }
    provenance_bytes = (
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=RIGHTS_FIELDS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(rights_rows)
    rights_bytes = csv_buffer.getvalue().encode("utf-8")
    summary = {
        "pdf": display_path(pdf),
        "pdf_sha256": pdf_identity["sha256"],
        "audit": audit_display,
        "components": {
            row["resource_id"]: {
                "objects": row["embedded_pdf_objects"],
                "bytes": row["embedded_stream_bytes"],
                "manifest_sha256": row["component_manifest_sha256"],
            }
            for row in component_rows
        },
    }
    return provenance_bytes, rights_bytes, summary


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def check_exact(path: Path, expected: bytes) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing generated output: {display_path(path)}")
    actual = path.read_bytes()
    if actual != expected:
        raise RuntimeError(
            f"generated output drift: {display_path(path)}; "
            f"expected sha256={sha256_bytes(expected)}, "
            f"observed sha256={sha256_bytes(actual)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate fail-closed font provenance and copy-ready rights-map rows "
            "for one exact O017 PDF/audit pair."
        )
    )
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument(
        "--provenance-output", type=Path, default=DEFAULT_PROVENANCE
    )
    parser.add_argument("--rights-map-output", type=Path, default=DEFAULT_RIGHTS_MAP)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare both outputs byte-for-byte and write nothing",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_args()
    pdf = resolve_path(arguments.pdf)
    audit_path = resolve_path(arguments.audit)
    provenance_output = resolve_path(arguments.provenance_output)
    rights_output = resolve_path(arguments.rights_map_output)
    require_output_in_root(provenance_output)
    require_output_in_root(rights_output)
    if not audit_path.is_file():
        raise FileNotFoundError(audit_path)

    verify_local_authorities()
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    provenance, rights, summary = generate(pdf, audit_path, audit)

    if arguments.check:
        check_exact(provenance_output, provenance)
        check_exact(rights_output, rights)
        mode = "check"
    else:
        atomic_write(provenance_output, provenance)
        atomic_write(rights_output, rights)
        mode = "write"

    result = {
        "status": "PASS",
        "mode": mode,
        **summary,
        "outputs": {
            "provenance": {
                "path": display_path(provenance_output),
                "bytes": len(provenance),
                "sha256": sha256_bytes(provenance),
            },
            "rights_map": {
                "path": display_path(rights_output),
                "bytes": len(rights),
                "sha256": sha256_bytes(rights),
            },
        },
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
