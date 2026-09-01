"""Seal and verify the complete English O017/D120 public release, without network access.

MIT; copyright 2026 KokunoYumeto. This script never publishes or reads credentials.
Use --check-inputs before packaging, --verify afterward, or --verify-archive ZIP.
"""
from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
from types import MappingProxyType
from typing import Callable, Mapping, Sequence
import unicodedata
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = ROOT.parent
VERSION = "en2026.08.31"
UNITS = [f"O017-U{n:02}" for n in range(1, 10)]
STAMP = (2026, 8, 31, 0, 0, 0)
PDF = "output/pdf/traceable-mathematical-work-en-2026.08.31.pdf"
SOURCE_ZIP = "release/o017-d120-en-2026.08.31-source.zip"
HTML_ZIP = "release/o017-d120-en-2026.08.31-reader-html.zip"
PACKAGE_QA = "qa/PACKAGE_QA.json"
RELEASE_PACKAGE_QA = "release/ENGLISH-RELEASE-PACKAGE-QA.json"
CHECKSUMS = "release/ENGLISH-SHA256SUMS.txt"
PUBLISH_MANIFEST = "release/PUBLISH_MANIFEST.json"
RESERVATION = "release/ZENODO_RESERVATION.json"
INDONESIAN_BASELINE = "controls/INDONESIAN_BASELINE.json"
MAX_PAYLOAD = 128 * 1024 * 1024
MAX_CONTAINER = MAX_PAYLOAD + 8 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 10_000
MAX_SNAPSHOT = 3 * MAX_CONTAINER
MAX_OUTPUT_SET = 2 * MAX_CONTAINER + 16 * 1024 * 1024
MAX_SIDECAR = 8 * 1024 * 1024
READ_CHUNK = 1024 * 1024

# These hashes bind the complete file-and-directory name surface of the active
# prepublication edition.  Packaging fails on an added, removed, renamed, or
# newly nested path; suffixes are never used to admit ambient files.
EXACT_TREE_INVENTORIES = {
    "source/units": (9, 0, "789b0dba35ed56833c0376e5e57bf67d8041fdc1dce282b397af82dcbb036c48"),
    "source/code": (4, 0, "cc500a4a543f449053bbde226138f84e8b50efd9e9cae714053a1c3822bb740c"),
    "source/fonts": (8, 0, "df094b1a164b01d3f61f8e848ae838e37d343e1d5a0e90451ef356076cfd408b"),
    "backend": (34, 1, "bf30280da3312eeac644fa5daae4eff965be1f42b3a9c94f82df0a33f9fbc7cc"),
    "delivery": (16, 3, "1c5bb1fa2f83111a334fa255051e534d406a27ec5345374db2420b3621b9d2af"),
    "licenses": (11, 0, "5c84a6f1edc4111d32762f1ac262146bb4dbdcbc5ba716ba8dc852a386a0cf7a"),
    "build/html": (64, 15, "f4ff9238f7e873d6c06927bb1eecc7a615a38e0badca4f8eb89b399d528c2f26"),
}
INDONESIAN_BASELINE_SHA256 = "ebc7b82904afc371958c0b98360e3c73507ce8c40502872c85eebbc2a6280930"
INDONESIAN_BASELINE_PATHS_SHA256 = "d0e01e146a2b351ee6a55117e5369d3ab5dbb680fb134226e3c3758dd8ce0da8"
INDONESIAN_BASELINE_FILE_COUNT = 61
WITNESS_BINDINGS = (
    (
        "source/code/verify_mst_uniqueness.py",
        "651f1c44f17385bc7ac44791634583a95a6ae86e05ef6c6ce1064052cd5dc761",
        "source/code/expected-output.txt",
        "d975260b0ca85297a8db7f303c760e0b80486103e09d76c8e089c019d7f55d51",
    ),
    (
        "source/code/u06_recurrence_witness.py",
        "9effb4dd4d17ce6b26fd108585ff0adc5110d8903c9c283b56a909613e7aa93d",
        "source/code/u06-expected-output.txt",
        "4c76da43510f9991b7197ddb0354a366136327b6d2ddfefb6516098eaa096112",
    ),
)

GATES = (
    "qa/SOURCE_CLOSURE.json", "qa/HTML_QA.json", "qa/PDF_QA.json",
    "qa/ENGLISH_BACKEND_QA.json", "qa/PDF_VISUAL_QA.json",
    "qa/HTML_VISUAL_QA.json", "delivery/validation-standalone-report.json",
    "qa/MONOSPACE_FONT_QA.json",
)
ROOT_PUBLIC = (
    "README.md", "BUILD.md", "CITATION.cff", "ENGLISH_EDITION_RIGHTS.md",
    "LICENSES.md", "THIRD_PARTY_NOTICES.md", "RELEASE_PROVENANCE.csv",
    "integration/ENGLISH_EDITION.json", "controls/INDONESIAN_BASELINE.json",
    "scripts/build_english.py", "scripts/english_backend.py",
    "scripts/package_english.py", "scripts/check_fonts.py",
)
SOURCE_FIXED = (
    "source/index.qmd", "source/_quarto.yml", "source/_quarto-pdf.yml",
    "source/styles.css", "source/references.bib", "source/pdf-header.tex",
    "source/wrapper/index.qmd",
)
PUBLIC_QA = (
    "qa/SOURCE_CLOSURE.json", "qa/HTML_QA.json", "qa/PDF_QA.json",
    "qa/ENGLISH_BACKEND_QA.json", "qa/PDF_VISUAL_QA.json",
    "qa/HTML_VISUAL_QA.json", "qa/MONOSPACE_FONT_QA.json",
    "qa/REUSE_AND_BASELINE.json", "qa/TEACHING_TRANSLATION.md",
    "qa/TRANSLATION_U01_U02.md", "qa/TRANSLATION_U03.md",
    "qa/TRANSLATION_U04.md", "qa/TRANSLATION_U05.md",
    "qa/TRANSLATION_U06.md", "qa/TRANSLATION_U07.md",
    "qa/TRANSLATION_U08.md", "qa/TRANSLATION_U09.md",
)
LOOSE_COPIES = (
    ("README.md", "ENGLISH-README.md"),
    ("BUILD.md", "ENGLISH-BUILD.md"),
    ("LICENSES.md", "ENGLISH-LICENSES.md"),
    ("ENGLISH_EDITION_RIGHTS.md", "ENGLISH-EDITION-RIGHTS.md"),
    ("THIRD_PARTY_NOTICES.md", "ENGLISH-THIRD-PARTY-NOTICES.md"),
    ("CITATION.cff", "ENGLISH-CITATION.cff"),
    ("integration/ENGLISH_EDITION.json", "ENGLISH-INTEGRATION.json"),
)
TEXT_SUFFIXES = {
    ".md", ".json", ".jsonl", ".csv", ".qmd", ".py", ".txt",
    ".yml", ".yaml", ".css", ".html", ".js", ".cff", ".bib", ".tex",
}
ARCHIVE_KINDS = {"editable-source-and-backend", "offline-semantic-html", "self-test"}
FORBIDDEN_SUFFIXES = {
    ".log", ".map", ".tmp", ".temp", ".bak", ".old", ".orig", ".rej",
    ".swp", ".swo", ".pyc", ".pyo", ".pem", ".key", ".pfx", ".p12",
    ".kdb", ".kdbx", ".env", ".png", ".jpg", ".jpeg", ".gif", ".webp",
}
FORBIDDEN_COMPONENTS = {
    ".git", ".hg", ".svn", ".quarto", ".cache", "__pycache__", "node_modules",
    "cache", "caches", "tmp", "temp", "logs", "screenshots", "screenshot",
    "screen-captures", "screen-capture", "render-intermediates",
}
SENSITIVE_FILENAME_TOKENS = {
    "credential", "credentials", "secret", "secrets", "password", "passwords",
    "passwd", "token", "tokens", "cookie", "cookies", "session", "sessions",
    "privatekey", "keystore", "authkey", "apikey",
}
NONPUBLIC_FILENAME_TOKENS = {
    "log", "logs", "trace", "traces", "screenshot", "screenshots",
    "screenrecording", "screenrecordings", "cache", "caches", "temp", "tmp",
}
WINDOWS_DEVICE = re.compile(
    r"^(?:CON|PRN|AUX|NUL|CLOCK\$|CONIN\$|CONOUT\$|COM[1-9]|LPT[1-9])(?:\..*)?$",
    re.IGNORECASE,
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

LOOSE_RELEASE_PATHS = tuple("release/" + filename for _original, filename in LOOSE_COPIES)
CHECKSUM_TARGETS = (PDF, SOURCE_ZIP, HTML_ZIP, *LOOSE_RELEASE_PATHS, RELEASE_PACKAGE_QA)
RELEASE_ASSETS = (*CHECKSUM_TARGETS, CHECKSUMS)
GENERATED_OUTPUTS = (
    SOURCE_ZIP, HTML_ZIP, *LOOSE_RELEASE_PATHS, PACKAGE_QA,
    RELEASE_PACKAGE_QA, CHECKSUMS, PUBLISH_MANIFEST,
)
GENERATED_RELEASE_PATHS = tuple(name for name in GENERATED_OUTPUTS if name.startswith("release/"))
EXPECTED_RELEASE_NAMES = frozenset(
    [PurePosixPath(name).name for name in GENERATED_RELEASE_PATHS]
    + [PurePosixPath(RESERVATION).name]
)
PRIVATE_RELEASE_SIDECARS = frozenset({
    "GITHUB_PUBLICATION_RECEIPT.json",
    "ZENODO_PUBLICATION_RECEIPT.json",
})
RESERVATION_BINDING_RE = re.compile(r"^ZENODO_RESERVATION_FINAL_BINDING_([0-9a-f]{16})\.json$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jbytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _duplicate_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def parse_json(data: bytes, label: str) -> object:
    def reject_constant(value: str) -> None:
        raise RuntimeError(f"Non-finite JSON value in {label}: {value}")

    try:
        return json.loads(
            data.decode("utf-8-sig"), object_pairs_hook=_duplicate_object,
            parse_constant=reject_constant,
        )
    except RuntimeError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Invalid JSON in {label}: {error}") from error


def require_dict(value: object, label: str) -> dict:
    if type(value) is not dict:
        raise RuntimeError(f"Expected JSON object: {label}")
    return value


def require_list(value: object, label: str) -> list:
    if type(value) is not list:
        raise RuntimeError(f"Expected JSON array: {label}")
    return value


def safe_name(name: str) -> str:
    if type(name) is not str or not name or "\\" in name or "\x00" in name:
        raise RuntimeError("Unsafe relative package path")
    if (
        name.startswith("/") or name.endswith("/") or len(name) > 240
        or len(name.encode("utf-16-le")) // 2 > 240
    ):
        raise RuntimeError("Unsafe or non-portable relative package path")
    parts = name.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise RuntimeError("Unsafe relative package path")
    for part in parts:
        if part[-1] in (".", " "):
            raise RuntimeError("Windows-nonportable trailing character in package path")
        if any(ord(character) < 32 or character in '<>:"|?*' for character in part):
            raise RuntimeError("Windows-invalid character in package path")
        normalized = unicodedata.normalize("NFKC", part)
        if WINDOWS_DEVICE.fullmatch(normalized):
            raise RuntimeError("Windows device name in package path")
        if len(part.encode("utf-16-le")) // 2 > 255:
            raise RuntimeError("Windows-nonportable path component length")
    return name


def portable_key(name: str) -> str:
    safe_name(name)
    return "/".join(unicodedata.normalize("NFC", part).casefold() for part in name.split("/"))


def assert_unique_names(names: Sequence[str], label: str) -> None:
    exact: set[str] = set()
    portable: dict[str, str] = {}
    for name in names:
        safe_name(name)
        if name in exact:
            raise RuntimeError(f"Duplicate {label} name: {name}")
        exact.add(name)
        key = portable_key(name)
        if key in portable:
            raise RuntimeError(f"Windows/Unicode-colliding {label} names: {portable[key]} and {name}")
        portable[key] = name
    keys = set(portable)
    for key in keys:
        parts = key.split("/")
        for end in range(1, len(parts)):
            if "/".join(parts[:end]) in keys:
                raise RuntimeError(f"File/directory-prefix collision in {label}: {key}")


def reject_forbidden_public_path(name: str) -> None:
    safe_name(name)
    parts = [unicodedata.normalize("NFKC", part).casefold() for part in name.split("/")]
    if any(part.startswith(".") or part in FORBIDDEN_COMPONENTS for part in parts):
        raise RuntimeError(f"Cache, temporary, hidden, log, or screenshot path is not public input: {name}")
    filename = parts[-1]
    if filename.endswith("~") or PurePosixPath(filename).suffix in FORBIDDEN_SUFFIXES:
        raise RuntimeError(f"Forbidden public-input file type: {name}")
    tokens = set(filter(None, re.split(r"[^a-z0-9]+", filename)))
    if tokens & SENSITIVE_FILENAME_TOKENS:
        raise RuntimeError(f"Credential-like filename is not public input: {name}")
    if tokens & NONPUBLIC_FILENAME_TOKENS:
        raise RuntimeError(f"Log, trace, screenshot, cache, or temporary filename is not public input: {name}")


def is_reparse_path(path: Path) -> bool:
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _rooted_local(root: Path, name: str, label: str) -> Path:
    safe_name(name)
    path = root.joinpath(*PurePosixPath(name).parts)
    cursor = root
    for part in PurePosixPath(name).parts:
        cursor /= part
        if is_reparse_path(cursor):
            raise RuntimeError(f"Symbolic links, junctions, and reparse points are not {label} paths: {name}")
    if not path.resolve(strict=False).is_relative_to(root.resolve()):
        raise RuntimeError(f"{label.capitalize()} path leaves its root: {name}")
    return path


def local(name: str) -> Path:
    return _rooted_local(ROOT, name, "package")


def parent_local(name: str) -> Path:
    return _rooted_local(PARENT_ROOT, name, "Indonesian-baseline parent")


def _stat_identity(value: os.stat_result) -> tuple[int, int, int, int]:
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def _read_path_stable(path: Path, label: str, max_bytes: int, collect: bool) -> bytes | tuple[int, str]:
    if type(max_bytes) is not int or isinstance(max_bytes, bool) or max_bytes < 0:
        raise RuntimeError("Invalid bounded-read byte limit")
    if is_reparse_path(path):
        raise RuntimeError(f"Reparse path cannot be read: {label}")
    try:
        before = path.stat()
    except FileNotFoundError as error:
        raise RuntimeError(f"Missing package input: {label}") from error
    if not stat.S_ISREG(before.st_mode):
        raise RuntimeError(f"Package input is not a regular file: {label}")
    if before.st_size > max_bytes:
        raise RuntimeError(f"Package input exceeds its pre-read byte limit: {label}")
    chunks: list[bytes] = []
    count = 0
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        opened = os.fstat(handle.fileno())
        if _stat_identity(opened) != _stat_identity(before):
            raise RuntimeError(f"Package input changed before it was read: {label}")
        while True:
            request = min(READ_CHUNK, max_bytes - count + 1)
            chunk = handle.read(request)
            if not chunk:
                break
            count += len(chunk)
            if count > max_bytes:
                raise RuntimeError(f"Package input exceeds its streamed byte limit: {label}")
            hasher.update(chunk)
            if collect:
                chunks.append(chunk)
        closed = os.fstat(handle.fileno())
    after = path.stat()
    if (
        _stat_identity(before) != _stat_identity(opened)
        or _stat_identity(opened) != _stat_identity(closed)
        or _stat_identity(closed) != _stat_identity(after)
        or count != after.st_size
        or is_reparse_path(path)
    ):
        raise RuntimeError(f"Package input changed while it was read: {label}")
    if collect:
        return b"".join(chunks)
    return count, hasher.hexdigest()


def read_live_stable(name: str, max_bytes: int = MAX_CONTAINER) -> bytes:
    result = _read_path_stable(local(name), name, max_bytes, True)
    if type(result) is not bytes:
        raise RuntimeError("Internal bounded-read mode mismatch")
    return result


def identity_live(name: str, max_bytes: int = MAX_CONTAINER) -> tuple[int, str]:
    result = _read_path_stable(local(name), name, max_bytes, False)
    if type(result) is not tuple:
        raise RuntimeError("Internal bounded-read mode mismatch")
    return result


def parent_identity_live(name: str, max_bytes: int = MAX_CONTAINER) -> tuple[int, str]:
    result = _read_path_stable(parent_local(name), f"parent/{name}", max_bytes, False)
    if type(result) is not tuple:
        raise RuntimeError("Internal bounded-read mode mismatch")
    return result


def read_external_stable(path: Path, max_bytes: int) -> bytes:
    result = _read_path_stable(path.resolve(strict=False), str(path), max_bytes, True)
    if type(result) is not bytes:
        raise RuntimeError("Internal bounded-read mode mismatch")
    return result


def row_bytes(name: str, data: bytes) -> dict:
    safe_name(name)
    return {"path": name, "bytes": len(data), "sha256": digest(data)}


def obj(reader: Callable[[str], bytes], name: str) -> dict:
    return require_dict(parse_json(reader(name), name), name)


def check_row(item: object, reader: Callable[[str], bytes], prefix: str = "") -> str:
    record = require_dict(item, "file identity row")
    path, byte_count, sha256 = record.get("path"), record.get("bytes"), record.get("sha256")
    if type(path) is not str or type(byte_count) is not int or isinstance(byte_count, bool):
        raise RuntimeError("Malformed file identity row")
    if byte_count < 0 or type(sha256) is not str or not SHA256_RE.fullmatch(sha256):
        raise RuntimeError("Malformed file identity row")
    name = prefix + path
    data = reader(name)
    if len(data) != byte_count or digest(data) != sha256:
        raise RuntimeError(f"Stale or damaged QA input: {name}")
    return name


def public_text_check(name: str, data: bytes) -> None:
    if PurePosixPath(name).suffix.lower() not in TEXT_SUFFIXES:
        return
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise RuntimeError(f"Public text input is not UTF-8: {name}") from error
    patterns = (
        r"[A-Za-z]:[\\/](?:Users|home)[\\/]", r"/(?:Users|home)/[^/\s]+/",
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
        r"\bAKIA[0-9A-Z]{16}\b", r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
        r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----",
        r"(?i)\b(?:access[_-]?token|api[_-]?key|client[_-]?secret|password|authorization)\s*[=:]\s*[\"']?[A-Za-z0-9_./+=-]{20,}",
        r"(?i)\bauthorization\s*:\s*bearer\s+[A-Za-z0-9_./+=-]{20,}",
    )
    if any(re.search(pattern, text) for pattern in patterns):
        raise RuntimeError(f"Sensitive-looking material in public input: {name}")
    local_identity = Path.home().name
    if local_identity.casefold() not in {"root", "user", "runner", "build", "default", "public"}:
        if re.search(r"(?<![\w-])" + re.escape(local_identity) + r"(?![\w-])", text, re.I):
            raise RuntimeError(f"Local account identity in public input: {name}")


def scan_exact_tree(directory: str) -> list[str]:
    if directory not in EXACT_TREE_INVENTORIES:
        raise RuntimeError(f"No pinned package inventory exists for: {directory}")
    base = local(directory)
    if not base.is_dir():
        raise RuntimeError(f"Missing package directory: {directory}")
    found: list[str] = []
    inventory_rows: list[dict[str, str]] = []
    for current, directories, files in os.walk(base, topdown=True, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for child in directories:
            candidate = current_path / child
            relative = candidate.relative_to(ROOT).as_posix()
            if is_reparse_path(candidate):
                raise RuntimeError(f"Symbolic link, junction, or reparse point inside package directory: {relative}")
            if not candidate.is_dir():
                raise RuntimeError(f"Non-directory package tree entry: {relative}")
            reject_forbidden_public_path(relative)
            inventory_rows.append({"path": relative, "kind": "directory"})
        for filename in files:
            candidate = current_path / filename
            relative = candidate.relative_to(ROOT).as_posix()
            if is_reparse_path(candidate) or not candidate.is_file():
                raise RuntimeError(f"Non-regular package input: {relative}")
            reject_forbidden_public_path(relative)
            found.append(relative)
            inventory_rows.append({"path": relative, "kind": "file"})
    assert_unique_names(found, f"{directory} inventory")
    found.sort()
    inventory_rows.sort(key=lambda item: (item["path"], item["kind"]))
    expected_files, expected_directories, expected_sha256 = EXACT_TREE_INVENTORIES[directory]
    actual_directories = len(inventory_rows) - len(found)
    if (
        len(found) != expected_files
        or actual_directories != expected_directories
        or digest(jbytes(inventory_rows)) != expected_sha256
    ):
        raise RuntimeError(f"Exact pinned package tree inventory differs: {directory}")
    return found


def source_names() -> list[str]:
    names = set(ROOT_PUBLIC + SOURCE_FIXED + PUBLIC_QA)
    for directory in ("source/units", "source/code", "source/fonts", "backend", "delivery", "licenses"):
        names.update(scan_exact_tree(directory))
    result = sorted(names)
    for name in result:
        reject_forbidden_public_path(name)
    assert_unique_names(result, "source payload")
    units = [name for name in result if name.startswith("source/units/")]
    if len(units) != 9 or any(PurePosixPath(name).suffix != ".qmd" for name in units):
        raise RuntimeError("Source archive must contain exactly nine unit source files")
    return result


def html_names() -> list[str]:
    names = scan_exact_tree("build/html")
    if not names:
        raise RuntimeError("HTML reader is empty")
    if len([name for name in names if name.endswith(".html")]) != 11:
        raise RuntimeError("HTML reader must contain exactly eleven HTML pages")
    return names


def _validate_sanitized_sidecar(name: str, data: bytes) -> None:
    public_text_check("release/" + name, data)
    value = require_dict(parse_json(data, "release/" + name), "release sidecar")
    if value.get("credentials_stored") is not False:
        raise RuntimeError(f"Release sidecar is not explicitly credential-free: {name}")
    expected_schema = {
        "GITHUB_PUBLICATION_RECEIPT.json": "o017-english-github-receipt-v1",
        "ZENODO_PUBLICATION_RECEIPT.json": "o017-english-zenodo-receipt-v1",
    }[name]
    if value.get("schema") != expected_schema or str(value.get("status", "")).upper() != "PASS":
        raise RuntimeError(f"Release publication receipt has an invalid schema/status: {name}")


def _check_live_identity(record: object, expected_path: str, label: str) -> None:
    row = require_dict(record, label)
    if row.get("path") != expected_path:
        raise RuntimeError(f"{label} path differs")
    actual = identity_live(expected_path, MAX_CONTAINER)
    if row.get("bytes") != actual[0] or row.get("sha256") != actual[1]:
        raise RuntimeError(f"{label} identity is stale")


def _validate_reservation_binding(name: str, data: bytes) -> None:
    public_text_check("release/" + name, data)
    value = require_dict(parse_json(data, "release/" + name), "reservation binding")
    if (
        value.get("schema") != "o017-english-zenodo-reservation-final-binding-v1"
        or str(value.get("status", "")).upper() != "PASS"
        or value.get("credentials_stored") is not False
    ):
        raise RuntimeError("Reservation binding has an invalid schema/status/privacy boundary")
    _check_live_identity(value.get("publication_manifest"), PUBLISH_MANIFEST, "reservation manifest binding")
    _check_live_identity(value.get("package_qa"), PACKAGE_QA, "reservation package-QA binding")
    _check_live_identity(value.get("reservation"), RESERVATION, "reservation receipt binding")
    rows = require_list(value.get("required_final_qa"), "reservation required final QA")
    checked: list[str] = []
    for item in rows:
        record = require_dict(item, "reservation required final-QA row")
        path = record.get("path")
        if type(path) is not str:
            raise RuntimeError("Reservation final-QA row has no path")
        _check_live_identity(record, path, "reservation final-QA binding")
        checked.append(path)
    assert_unique_names(checked, "reservation final-QA binding")
    if set(checked) != set(GATES):
        raise RuntimeError("Reservation binding does not cover the exact final QA gates")


def release_inventory(require_complete: bool) -> frozenset[str]:
    base = local("release")
    if not base.is_dir():
        raise RuntimeError("Release directory is absent")
    names: list[str] = []
    for path in sorted(base.iterdir(), key=lambda item: item.name.casefold()):
        if is_reparse_path(path) or not path.is_file():
            raise RuntimeError(f"Release directory contains a non-regular entry: {path.name}")
        safe_name(path.name)
        names.append(path.name)
    assert_unique_names(names, "release-directory")
    inventory = frozenset(names)
    reservation_name = PurePosixPath(RESERVATION).name
    if reservation_name not in inventory:
        raise RuntimeError("The existing Zenodo reservation transaction state is absent")
    binding_names = {name for name in inventory if RESERVATION_BINDING_RE.fullmatch(name)}
    if len(binding_names) > 1:
        raise RuntimeError("More than one reservation-binding sidecar is present")
    allowed = set(EXPECTED_RELEASE_NAMES) | set(PRIVATE_RELEASE_SIDECARS)
    if binding_names:
        if PurePosixPath(PUBLISH_MANIFEST).name not in inventory:
            raise RuntimeError("Reservation-binding sidecar exists without a package manifest")
        manifest_sha256 = identity_live(PUBLISH_MANIFEST, MAX_SIDECAR)[1]
        expected_binding = f"ZENODO_RESERVATION_FINAL_BINDING_{manifest_sha256[:16]}.json"
        if binding_names != {expected_binding}:
            raise RuntimeError("Reservation-binding filename is not addressed by the current manifest hash")
        allowed.add(expected_binding)
    unexpected = inventory - allowed
    if unexpected:
        raise RuntimeError(f"Unexpected release-directory entries: {sorted(unexpected)}")
    if require_complete and not EXPECTED_RELEASE_NAMES.issubset(inventory):
        raise RuntimeError(f"Release inventory is incomplete: {sorted(EXPECTED_RELEASE_NAMES - inventory)}")
    for name in sorted(inventory & PRIVATE_RELEASE_SIDECARS):
        _validate_sanitized_sidecar(name, read_live_stable("release/" + name, MAX_SIDECAR))
    for name in binding_names:
        _validate_reservation_binding(name, read_live_stable("release/" + name, MAX_SIDECAR))
    return inventory


def validate_indonesian_baseline(
    data: bytes, identity_reader: Callable[[str, int], tuple[int, str]],
) -> Mapping[str, tuple[int, str]]:
    if digest(data) != INDONESIAN_BASELINE_SHA256:
        raise RuntimeError("Indonesian baseline receipt differs from the pinned edition receipt")
    value = require_dict(parse_json(data, INDONESIAN_BASELINE), INDONESIAN_BASELINE)
    if set(value) != {"schema", "files"} or value.get("schema") != "o017-en-indonesian-baseline-v1":
        raise RuntimeError("Indonesian baseline schema surface differs")
    rows = require_list(value.get("files"), "Indonesian baseline files")
    if len(rows) != INDONESIAN_BASELINE_FILE_COUNT:
        raise RuntimeError("Indonesian baseline file count differs")
    paths: list[str] = []
    expected: dict[str, tuple[int, str]] = {}
    total = 0
    for item in rows:
        record = require_dict(item, "Indonesian baseline row")
        if set(record) != {"path", "bytes", "sha256"}:
            raise RuntimeError("Indonesian baseline row has an unexpected schema surface")
        path, byte_count, sha256 = record.get("path"), record.get("bytes"), record.get("sha256")
        if (
            type(path) is not str
            or type(byte_count) is not int or isinstance(byte_count, bool) or byte_count < 0
            or type(sha256) is not str or SHA256_RE.fullmatch(sha256) is None
        ):
            raise RuntimeError("Malformed Indonesian baseline file identity")
        safe_name(path)
        paths.append(path)
        if total + byte_count > MAX_PAYLOAD:
            raise RuntimeError("Indonesian baseline exceeds its aggregate byte budget")
        total += byte_count
        actual = identity_reader(path, min(byte_count, MAX_CONTAINER))
        if actual != (byte_count, sha256):
            raise RuntimeError(f"Independently verified Indonesian parent identity differs: {path}")
        expected[path] = actual
    assert_unique_names(paths, "Indonesian baseline")
    if digest(jbytes(paths)) != INDONESIAN_BASELINE_PATHS_SHA256:
        raise RuntimeError("Indonesian baseline exact parent path inventory differs")
    if len(expected) != len(rows):
        raise RuntimeError("Indonesian baseline contains duplicate parent paths")
    return MappingProxyType(expected)


@dataclass(frozen=True)
class InputSnapshot:
    files: Mapping[str, bytes]
    source_files: tuple[str, ...]
    html_files: tuple[str, ...]
    reservation_bytes: bytes
    pre_release_names: frozenset[str]
    prior_outputs: Mapping[str, tuple[int, str] | None]
    baseline_identities: Mapping[str, tuple[int, str]]

    def read(self, name: str) -> bytes:
        safe_name(name)
        try:
            return self.files[name]
        except KeyError as error:
            raise RuntimeError(f"File was not admitted to the immutable input snapshot: {name}") from error

    def assert_inputs_unchanged(self) -> None:
        if tuple(source_names()) != self.source_files or tuple(html_names()) != self.html_files:
            raise RuntimeError("Package input inventory changed after snapshot capture")
        for name, expected in self.files.items():
            current = identity_live(name, MAX_CONTAINER)
            if current != (len(expected), digest(expected)):
                raise RuntimeError(f"Package input changed after snapshot capture: {name}")

    def assert_baseline_unchanged(self) -> None:
        for name, expected in self.baseline_identities.items():
            if parent_identity_live(name, min(expected[0], MAX_CONTAINER)) != expected:
                raise RuntimeError(f"Indonesian parent baseline changed during packaging: {name}")

    def assert_reservation_unchanged(self) -> None:
        current = read_live_stable(RESERVATION, MAX_SIDECAR)
        if len(current) != len(self.reservation_bytes) or digest(current) != digest(self.reservation_bytes):
            raise RuntimeError("Zenodo reservation transaction state changed during packaging")

    def assert_output_prestate_unchanged(self) -> None:
        if release_inventory(require_complete=False) != self.pre_release_names:
            raise RuntimeError("Release output inventory changed during packaging")
        for name, expected in self.prior_outputs.items():
            path = local(name)
            if expected is None:
                if path.exists():
                    raise RuntimeError(f"Package output appeared concurrently: {name}")
            else:
                if identity_live(name, MAX_CONTAINER) != expected:
                    raise RuntimeError(f"Existing package output changed concurrently: {name}")


def capture_snapshot(require_complete_release: bool = False) -> InputSnapshot:
    pre_release_names = release_inventory(require_complete=require_complete_release)
    reservation = read_live_stable(RESERVATION, MAX_SIDECAR)
    sources, html = tuple(source_names()), tuple(html_names())
    admitted = sorted(set(sources) | set(html) | {PDF} | set(GATES))
    if RESERVATION in admitted or any(name in GENERATED_OUTPUTS for name in admitted):
        raise RuntimeError("Transaction state or generated output leaked into the immutable public snapshot")
    assert_unique_names(admitted, "input snapshot")
    files: dict[str, bytes] = {}
    snapshot_bytes = 0
    for name in admitted:
        remaining = MAX_SNAPSHOT - snapshot_bytes
        if remaining < 0:
            raise RuntimeError("Immutable input snapshot exceeds its aggregate byte budget")
        data = read_live_stable(name, min(MAX_CONTAINER, remaining))
        snapshot_bytes += len(data)
        files[name] = data
    baseline_identities = validate_indonesian_baseline(
        files[INDONESIAN_BASELINE], parent_identity_live,
    )
    prior: dict[str, tuple[int, str] | None] = {}
    for name in GENERATED_OUTPUTS:
        path = local(name)
        if path.exists():
            prior[name] = identity_live(name, MAX_CONTAINER)
        else:
            prior[name] = None
    snapshot = InputSnapshot(
        MappingProxyType(files), sources, html, reservation, pre_release_names,
        MappingProxyType(prior), baseline_identities,
    )
    snapshot.assert_inputs_unchanged()
    snapshot.assert_baseline_unchanged()
    snapshot.assert_reservation_unchanged()
    return snapshot


def load_payload(reader: Callable[[str], bytes], names: Sequence[str], strip: str = "") -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    arcnames: list[str] = []
    for name in names:
        data = reader(name)
        public_text_check(name, data)
        arcname = safe_name(name[len(strip):] if strip else name)
        reject_forbidden_public_path(arcname)
        arcnames.append(arcname)
        result[arcname] = data
    assert_unique_names(arcnames, "archive payload")
    if len(result) != len(names):
        raise RuntimeError("Duplicate archive payload path")
    if sum(map(len, result.values())) > MAX_PAYLOAD:
        raise RuntimeError("Package exceeds the bounded 128 MiB payload budget")
    return result


def _gate_pass(gate: dict, name: str) -> None:
    status_value = gate.get("status")
    if type(status_value) is not str or status_value.upper() != "PASS":
        raise RuntimeError(f"Required QA gate is not PASS: {name}")
    if "errors" in gate and gate["errors"] != []:
        raise RuntimeError(f"Required QA gate contains errors: {name}")


def _unique_checked_rows(rows: object, reader: Callable[[str], bytes], label: str, prefix: str = "") -> list[str]:
    checked = [check_row(item, reader, prefix) for item in require_list(rows, label)]
    assert_unique_names(checked, label)
    return checked


def validate_witness_receipts(snapshot: InputSnapshot) -> list[dict]:
    """Validate pinned, precomputed witnesses without executing packaged code."""
    result: list[dict] = []
    for script, script_sha256, expected, expected_sha256 in WITNESS_BINDINGS:
        script_data, expected_data = snapshot.read(script), snapshot.read(expected)
        expected_identities = {
            script: (len(script_data), script_sha256),
            expected: (len(expected_data), expected_sha256),
        }
        for name, identity in expected_identities.items():
            actual = (len(snapshot.read(name)), digest(snapshot.read(name)))
            if actual != identity or snapshot.baseline_identities.get(name) != identity:
                raise RuntimeError(f"Pinned witness/baseline receipt identity differs: {name}")
        # The receipt's output is data, not authority.  Validate its format too,
        # while the SHA-256 binding above remains the authoritative identity.
        if expected.endswith("u06-expected-output.txt"):
            witness_output = require_dict(parse_json(expected_data, expected), "recurrence witness output")
            summary = require_dict(witness_output.get("summary"), "recurrence witness summary")
            if summary.get("all_records_valid") is not True or summary.get("tamper_control_detected") is not True:
                raise RuntimeError("Recurrence witness receipt does not record a deterministic PASS")
        elif expected_data.decode("utf-8-sig").splitlines() != [
            "k4_distinct_weight_assignments_checked: 720",
            "k4_uniqueness_violations: 0",
            "equal_weight_triangle_mst_count: 3",
        ]:
            raise RuntimeError("MST witness receipt does not record the pinned result")
        result.append({
            "receipt": INDONESIAN_BASELINE,
            "script": {"path": script, "bytes": len(script_data), "sha256": script_sha256},
            "inputs": [],
            "output": {"path": expected, "bytes": len(expected_data), "sha256": expected_sha256},
            "status": "PASS",
            "execution_performed_during_packaging": False,
        })
    return result


def validate_inputs(snapshot: InputSnapshot) -> dict:
    reader = snapshot.read
    gates = {name: obj(reader, name) for name in GATES}
    for name, gate in gates.items():
        _gate_pass(gate, name)

    source = gates["qa/SOURCE_CLOSURE.json"]
    if (source.get("unit_count"), source.get("exercise_count"), source.get("guidance_count")) != (9, 54, 54):
        raise RuntimeError("Course coverage gate differs from 9 units / 54 exercises / 54 guides")
    units = require_list(source.get("units"), "source-closure units")
    if len(units) != 9 or [require_dict(unit, "source unit").get("unit_id") for unit in units] != UNITS:
        raise RuntimeError("Unit IDs differ from the complete original course")
    unit_paths = _unique_checked_rows(units, reader, "source-closure unit rows")
    expected_units = [name for name in snapshot.source_files if name.startswith("source/units/")]
    if set(unit_paths) != set(expected_units):
        raise RuntimeError("Source-closure unit inventory differs from the source archive")
    for unit in units:
        record = require_dict(unit, "source unit")
        if record.get("exercises") != 6 or record.get("guidance_answers") != 6:
            raise RuntimeError("Every unit must bind six exercises and six answer guides")
        if type(record.get("original_sha256")) is not str or not SHA256_RE.fullmatch(record["original_sha256"]):
            raise RuntimeError("Source-closure unit lacks a valid original-source binding")
    if source.get("indonesian_baseline_preserved") is not True:
        raise RuntimeError("Indonesian source baseline is not marked preserved")

    html = gates["qa/HTML_QA.json"]
    pages = require_list(html.get("pages"), "HTML QA pages")
    checked_pages = _unique_checked_rows(pages, reader, "HTML QA pages", "build/html/")
    expected_pages = [name for name in snapshot.html_files if name.endswith(".html")]
    if html.get("html_pages") != 11 or set(checked_pages) != set(expected_pages):
        raise RuntimeError("HTML QA page inventory is not the exact eleven-page reader")
    if type(html.get("native_mathml_count")) is not int or html["native_mathml_count"] < 1:
        raise RuntimeError("Native MathML coverage is absent")
    if sum(require_dict(page, "HTML page").get("mathml", -1) for page in pages) != html["native_mathml_count"]:
        raise RuntimeError("HTML QA MathML total is internally inconsistent")
    if any(require_dict(page, "HTML page").get("language") != "en" for page in pages):
        raise RuntimeError("HTML QA includes a non-English page")

    html_visual = gates["qa/HTML_VISUAL_QA.json"]
    if html_visual.get("html_qa_sha256") != digest(reader("qa/HTML_QA.json")):
        raise RuntimeError("HTML visual QA is not bound to the current HTML QA hash")
    if html_visual.get("pages") != 11 or html_visual.get("viewportWidths") != [390, 1440]:
        raise RuntimeError("HTML visual QA does not cover the exact pages and viewports")
    if html_visual.get("unsafeOverflowCount") != 0:
        raise RuntimeError("HTML visual QA reports unsafe overflow")
    observations = require_list(html_visual.get("observations"), "HTML visual observations")
    expected_observations: dict[tuple[str, int], int] = {}
    for page in pages:
        record = require_dict(page, "HTML page")
        path = record["path"]
        visual_path = "/" if path == "index.html" else "/wrapper/" if path == "wrapper/index.html" else "/" + path
        for viewport in (390, 1440):
            expected_observations[(visual_path, viewport)] = record["mathml"]
    actual_observations: dict[tuple[str, int], int] = {}
    for observation in observations:
        record = require_dict(observation, "HTML visual observation")
        key = (record.get("path"), record.get("viewport"))
        if key in actual_observations or record.get("lang") != "en" or record.get("unsafe") != []:
            raise RuntimeError("HTML visual QA observation is duplicated, unsafe, or non-English")
        if type(record.get("mathml")) is not int or type(record.get("mainWidth")) is not int or record["mainWidth"] <= 0:
            raise RuntimeError("Malformed HTML visual QA observation")
        actual_observations[key] = record["mathml"]
    if actual_observations != expected_observations:
        raise RuntimeError("HTML visual QA is not closed over every page/viewport pair")

    pdf = gates["qa/PDF_QA.json"]
    check_row(pdf, reader)
    if pdf.get("path") != PDF or pdf.get("pages") != 144 or pdf.get("tagged") is not False:
        raise RuntimeError("PDF identity/accessibility boundary differs from this release")
    if pdf.get("accessible_surface") != "English semantic HTML":
        raise RuntimeError("PDF QA does not identify the semantic HTML accessibility surface")
    fonts = require_dict(pdf.get("fonts"), "PDF font inventory")
    if not fonts or any(require_dict(value, "PDF font row").get("embedded") is not True for value in fonts.values()):
        raise RuntimeError("PDF QA does not establish embedded fonts")

    pdf_visual = gates["qa/PDF_VISUAL_QA.json"]
    if (
        pdf_visual.get("pdf") != PDF or pdf_visual.get("sha256") != pdf["sha256"]
        or pdf_visual.get("pdf_sha256") != pdf["sha256"]
        or pdf_visual.get("bytes") != pdf["bytes"] or pdf_visual.get("pages") != pdf["pages"]
    ):
        raise RuntimeError("PDF visual QA is not bound to the current PDF identity")
    render = require_dict(pdf_visual.get("render"), "PDF visual render")
    geometry = require_dict(pdf_visual.get("geometry"), "PDF visual geometry")
    visual_review = require_dict(pdf_visual.get("visual_review"), "PDF visual review")
    if render.get("pages_rendered") != pdf["pages"] or render.get("source_unchanged") is not True:
        raise RuntimeError("PDF visual render is incomplete or stale")
    for key in ("words_outside_page", "pages_with_replacement_characters", "invalid_glyphs_by_page"):
        if geometry.get(key) != []:
            raise RuntimeError(f"PDF visual geometry gate reports defects: {key}")
    if str(visual_review.get("status", "")).upper() != "PASS" or visual_review.get("defects") != []:
        raise RuntimeError("PDF visual review is not a clean final PASS")
    inspected_pages = require_list(visual_review.get("pages_inspected"), "PDF pages inspected")
    if (
        not inspected_pages or any(type(page) is not int or isinstance(page, bool) or not 1 <= page <= pdf["pages"] for page in inspected_pages)
        or len(inspected_pages) != len(set(inspected_pages))
    ):
        raise RuntimeError("PDF visual review does not record inspected pages")

    backend = gates["qa/ENGLISH_BACKEND_QA.json"]
    if backend.get("schema") != "o017-english-backend-qa-v1":
        raise RuntimeError("Backend QA schema differs")
    backend_checks = require_dict(backend.get("checks"), "backend checks")
    if not backend_checks or any(value is not True for value in backend_checks.values()):
        raise RuntimeError("Backend QA has an incomplete check")
    if backend.get("source_locator_errors") != [] or backend.get("unfinished_translation_fields") != []:
        raise RuntimeError("Backend QA reports source-locator or translation errors")
    dataset_name = "backend/english-backend.dataset.json"
    dataset = obj(reader, dataset_name)
    if backend.get("dataset_sha256") != digest(reader(dataset_name)):
        raise RuntimeError("Backend QA references a different dataset")
    backend_rows: list[str] = []
    for key in ("inputs", "outputs"):
        backend_rows.extend(_unique_checked_rows(dataset.get(key), reader, f"backend dataset {key}"))
    backend_rows.extend(_unique_checked_rows(
        dataset.get("preserved_upstream_files"), reader, "preserved upstream files",
        "backend/upstream-id-ID/",
    ))
    assert_unique_names(backend_rows, "backend dataset file identities")
    counts = require_dict(backend.get("counts"), "backend counts")
    for key in ("english_semantic_localizations", "indonesian_semantic_localizations_preserved"):
        if counts.get(key) != 581:
            raise RuntimeError("Incomplete bilingual semantic localization coverage")

    teaching = gates["delivery/validation-standalone-report.json"]
    teaching_files = _unique_checked_rows(teaching.get("files"), reader, "teaching validation files")
    if len(teaching_files) != 14 or teaching.get("credit_awarded") is not False:
        raise RuntimeError("Teaching inventory or calibration boundary differs")
    if teaching.get("network_or_contact_performed") is not False:
        raise RuntimeError("Teaching validation unexpectedly performed network/contact activity")
    calibration = obj(reader, "delivery/calibration/calibration-package.json")
    if (
        calibration.get("credit_eligible") is not False
        or calibration.get("synthetic_personas") is not True
        or require_dict(calibration.get("contact_control"), "calibration contact control").get("transmission_performed") is not False
    ):
        raise RuntimeError("Calibration must remain synthetic, local, and non-credit")

    font_gate = gates["qa/MONOSPACE_FONT_QA.json"]
    if font_gate.get("schema") != "o017-english-font-qa-v1":
        raise RuntimeError("Monospace font QA schema differs")
    font_checks = require_dict(font_gate.get("checks"), "font checks")
    if not font_checks or any(value is not True for value in font_checks.values()):
        raise RuntimeError("Monospace font QA has an incomplete check")
    font_rows = require_list(font_gate.get("fonts"), "font rows")
    if len(font_rows) != 8:
        raise RuntimeError("Monospace font QA must bind the exact eight-font inventory")
    checked_fonts = _unique_checked_rows(font_rows, reader, "font rows")
    expected_fonts = [name for name in snapshot.source_files if name.startswith("source/fonts/") and name.endswith((".ttf", ".otf"))]
    if set(checked_fonts) != set(expected_fonts):
        raise RuntimeError("Monospace font QA inventory differs from packaged fonts")
    for font in font_rows:
        record = require_dict(font, "font row")
        if record.get("fsType") != 0 or record.get("missing_fenced_code_points") != [] or record.get("covers_U+2032_PRIME") is not True:
            raise RuntimeError("Monospace font QA row violates embedding or coverage requirements")
    font_source = require_dict(font_gate.get("source"), "font source")
    license_name = font_source.get("license_path")
    if type(license_name) is not str or digest(reader(license_name)) != font_source.get("license_sha256"):
        raise RuntimeError("Monospace font QA license binding differs")
    font_configuration = require_dict(font_gate.get("configuration"), "font configuration")
    if (
        font_configuration.get("mainfont") != "DejaVuSerif"
        or font_configuration.get("monofont") != "DejaVuSansMono"
        or font_configuration.get("path") != "source/fonts/"
        or font_configuration.get("configuration_path") != "source/_quarto-pdf.yml"
    ):
        raise RuntimeError("Monospace font QA is not bound to the active PDF configuration")
    embedded_font_names = "\n".join(fonts)
    if not all(marker in embedded_font_names for marker in ("DejaVuSerif", "DejaVuSansMono")):
        raise RuntimeError("PDF QA does not confirm the font families governed by the font gate")

    integration = obj(reader, "integration/ENGLISH_EDITION.json")
    if integration.get("units") != UNITS or integration.get("language") != "en":
        raise RuntimeError("Central integration identity differs from this edition")
    coverage = require_dict(integration.get("coverage"), "integration coverage")
    for key in (
        "semantic_entities", "english_semantic_localizations",
        "indonesian_semantic_localizations_preserved", "english_core_localizations",
        "english_access_locators",
    ):
        if coverage.get(key) != counts.get(key):
            raise RuntimeError(f"Central integration coverage is stale: {key}")

    witnesses = validate_witness_receipts(snapshot)
    return {
        "gates": [row_bytes(name, reader(name)) for name in GATES],
        "pdf_pages": pdf["pages"], "html_pages": html["html_pages"],
        "witnesses": witnesses,
        "indonesian_baseline": {
            "path": INDONESIAN_BASELINE,
            "bytes": len(reader(INDONESIAN_BASELINE)),
            "sha256": digest(reader(INDONESIAN_BASELINE)),
            "parent_files_independently_verified": len(snapshot.baseline_identities),
            "parent_manifest_sha256": digest(jbytes([
                {"path": name, "bytes": identity[0], "sha256": identity[1]}
                for name, identity in snapshot.baseline_identities.items()
            ])),
        },
    }


def archive_bytes(payload: Mapping[str, bytes], kind: str) -> bytes:
    if kind not in ARCHIVE_KINDS:
        raise RuntimeError(f"Unknown archive kind: {kind}")
    names = list(payload)
    assert_unique_names(names, "archive payload")
    try:
        assert_unique_names([*names, "RELEASE_MANIFEST.json"], "complete archive")
    except RuntimeError as error:
        raise RuntimeError("Payload collides with the generated archive manifest") from error
    if len(names) + 1 > MAX_ARCHIVE_ENTRIES or sum(map(len, payload.values())) > MAX_PAYLOAD:
        raise RuntimeError("Archive payload exceeds its bounded entry or byte budget")
    for name in names:
        reject_forbidden_public_path(name)
    manifest = {
        "schema": "o017-english-archive-v1", "version": VERSION,
        "language": "en", "kind": kind, "compression": "stored",
        "units": UNITS, "manifest_scope": "Every payload entry; this manifest excludes itself",
        "files": [row_bytes(name, data) for name, data in sorted(payload.items())],
    }
    complete = dict(payload)
    complete["RELEASE_MANIFEST.json"] = jbytes(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        archive.comment = b""
        for name, data in sorted(complete.items()):
            info = zipfile.ZipInfo(safe_name(name), STAMP)
            info.create_system = 3
            info.create_version = 20
            info.extract_version = 20
            info.external_attr = 0o100644 << 16
            info.internal_attr = 0
            info.compress_type = zipfile.ZIP_STORED
            info.extra = b""
            info.comment = b""
            archive.writestr(info, data)
    return buffer.getvalue()


def verify_archive(data: bytes, expected_kind: str | None = None) -> dict:
    if len(data) > MAX_CONTAINER:
        raise RuntimeError("Archive compressed bytes exceed the bounded verification budget")
    payloads: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(data), "r", allowZip64=False) as archive:
        if archive.comment != b"":
            raise RuntimeError("Archive-level ZIP comment is forbidden")
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) > MAX_ARCHIVE_ENTRIES or names != sorted(names):
            raise RuntimeError("Archive entry count or order differs")
        assert_unique_names(names, "ZIP entry")
        if "RELEASE_MANIFEST.json" not in names:
            raise RuntimeError("Archive manifest is absent")
        if sum(info.file_size for info in infos) > MAX_CONTAINER:
            raise RuntimeError("Archive exceeds bounded verification budget")
        for info in infos:
            safe_name(info.filename)
            mode = info.external_attr >> 16
            if (
                info.orig_filename != info.filename or info.is_dir() or not stat.S_ISREG(mode)
                or mode != 0o100644 or info.external_attr != 0o100644 << 16
            ):
                raise RuntimeError("Archive contains a truncated, non-regular, or non-0644 entry")
            if (
                info.create_system != 3 or info.create_version != 20 or info.extract_version != 20
                or info.date_time != STAMP or info.compress_type != zipfile.ZIP_STORED
            ):
                raise RuntimeError("Archive platform, version, timestamp, or compression metadata is not deterministic")
            if info.comment != b"" or info.extra != b"" or info.internal_attr != 0:
                raise RuntimeError("Archive entry comments, extras, or internal attributes are forbidden")
            if info.flag_bits & ~0x800:
                raise RuntimeError("Archive entry uses an unexpected ZIP flag")
        if archive.testzip() is not None:
            raise RuntimeError("Archive CRC verification failed")
        manifest_data = archive.read("RELEASE_MANIFEST.json")
        manifest = require_dict(parse_json(manifest_data, "archive RELEASE_MANIFEST.json"), "archive manifest")
        exact_keys = {"schema", "version", "language", "kind", "compression", "units", "manifest_scope", "files"}
        if set(manifest) != exact_keys:
            raise RuntimeError("Archive manifest has an unexpected schema surface")
        kind = manifest.get("kind")
        if (
            manifest.get("schema") != "o017-english-archive-v1"
            or manifest.get("language") != "en" or manifest.get("version") != VERSION
            or manifest.get("units") != UNITS or manifest.get("compression") != "stored"
            or manifest.get("manifest_scope") != "Every payload entry; this manifest excludes itself"
            or kind not in ARCHIVE_KINDS or (expected_kind is not None and kind != expected_kind)
        ):
            raise RuntimeError("Archive manifest identity or kind differs from this edition")
        manifest_files = require_list(manifest.get("files"), "archive manifest files")
        manifest_names: list[str] = []
        for item in manifest_files:
            record = require_dict(item, "archive manifest row")
            if set(record) != {"path", "bytes", "sha256"} or type(record.get("path")) is not str:
                raise RuntimeError("Malformed archive manifest row")
            manifest_names.append(record["path"])
        assert_unique_names(manifest_names, "archive manifest")
        if set(names) != set(manifest_names) | {"RELEASE_MANIFEST.json"}:
            raise RuntimeError("Archive inventory differs from its manifest in either direction")
        for name in manifest_names:
            reject_forbidden_public_path(name)
            payloads[name] = archive.read(name)
        if sum(map(len, payloads.values())) > MAX_PAYLOAD:
            raise RuntimeError("Archive payload exceeds the bounded 128 MiB payload budget")
        expected_rows = [row_bytes(name, payload) for name, payload in sorted(payloads.items())]
        if manifest_files != expected_rows or manifest_data != jbytes({**manifest, "files": expected_rows}):
            raise RuntimeError("Archive payload identities or manifest JSON are not canonical")
    rebuilt = archive_bytes(payloads, kind)
    if rebuilt != data:
        raise RuntimeError("Archive bytes are not the canonical deterministic generation")
    return {
        "status": "PASS", "kind": kind, "compression": "stored",
        "entries": len(payloads) + 1, "payload_entries": len(payloads),
        "uncompressed_payload_bytes": sum(map(len, payloads.values())),
        "bytes": len(data), "sha256": digest(data),
        "canonical_rebuild_identical": True,
    }


def snapshot_manifest_sha256(snapshot: InputSnapshot) -> str:
    return digest(jbytes([row_bytes(name, data) for name, data in sorted(snapshot.files.items())]))


def payload_manifest_sha256(payload: Mapping[str, bytes]) -> str:
    return digest(jbytes([row_bytes(name, data) for name, data in sorted(payload.items())]))


def make_package_qa(
    snapshot: InputSnapshot, evidence: dict, source_payload: Mapping[str, bytes],
    html_payload: Mapping[str, bytes], archive_records: list[dict],
) -> dict:
    return {
        "schema": "o017-english-package-qa-v1", "status": "PASS",
        "version": VERSION, "language": "en", "units": UNITS,
        "coverage": {
            "units": 9, "exercises": 54, "answer_guides": 54,
            "teaching_source_files": 14, "calibration_dossiers": 5,
            "english_semantic_localizations": 581,
            "indonesian_semantic_localizations_preserved": 581,
        },
        "input_evidence": evidence,
        "input_snapshot": {
            "files": len(snapshot.files), "manifest_sha256": snapshot_manifest_sha256(snapshot),
            "source_inventory_sha256": digest(jbytes(list(snapshot.source_files))),
            "html_inventory_sha256": digest(jbytes(list(snapshot.html_files))),
            "reservation_transaction_state_excluded": True,
        },
        "archives": archive_records,
        "source_payload_files": len(source_payload), "html_payload_files": len(html_payload),
        "source_input_manifest_sha256": payload_manifest_sha256(source_payload),
        "html_input_manifest_sha256": payload_manifest_sha256(html_payload),
        "checks": {
            "exact_allowlisted_public_inputs": True, "public_text_privacy_scan": True,
            "immutable_exact_input_snapshot": True, "single_coherent_generation": True,
            "atomic_final_file_replacement": True, "exact_release_inventory": True,
            "bidirectional_checksum_closure": True, "portable_collision_free_names": True,
            "archive_inventory_bytes_and_sha256": True, "archive_fixed_metadata_and_order": True,
            "archive_identical_second_generation": True, "archive_canonical_rebuild": True,
            "mathematical_witness_outputs": True, "fresh_required_qa_hashes": True,
            "all_final_gates_revalidated": True, "bilingual_backend_snapshot_preserved": True,
        },
        "exclusions": [
            "private controls except the public Indonesian hash baseline",
            "credentials and authentication material", "publication tooling and Zenodo transaction state",
            "donor witness trees", "build caches and temporary files", "source maps",
            "render intermediates and visual screenshots", "local logs",
        ],
        "claim_boundary": {
            "public_release_verified": False, "container_run_claimed": False,
            "pdf_bit_reproducible_claimed": False, "pdf_tagged": False,
            "primary_accessible_surface": "semantic HTML with native MathML",
            "learner_performance_validated": False,
        },
        "errors": [],
    }


def combined_reader(snapshot: InputSnapshot, outputs: Mapping[str, bytes]) -> Callable[[str], bytes]:
    def read(name: str) -> bytes:
        safe_name(name)
        return outputs[name] if name in outputs else snapshot.read(name)
    return read


def publish_specs(source_files: Sequence[str], html_files: Sequence[str]) -> list[tuple[str, str | None, str | None]]:
    specs: list[tuple[str, str | None, str | None]] = []
    for name in RELEASE_ASSETS:
        release_name = PurePosixPath(name).name
        repo_path = "english/" + name if name.startswith("release/ENGLISH-") else None
        specs.append((name, release_name, repo_path))
    specs.extend((name, None, "english/" + name) for name in source_files)
    specs.extend((name, None, "en/" + name[len("build/html/"):]) for name in html_files)
    specs.append((PACKAGE_QA, None, "english/qa/PACKAGE_QA.json"))
    assert_unique_names([path for path, _release, _repo in specs], "publish-manifest input")
    assert_unique_names([name for _path, name, _repo in specs if name is not None], "release asset")
    assert_unique_names([name for _path, _release, name in specs if name is not None], "repository destination")
    return specs


def make_publish_manifest(snapshot: InputSnapshot, outputs: Mapping[str, bytes]) -> dict:
    reader = combined_reader(snapshot, outputs)
    files: list[dict] = []
    for path, release_name, repo_path in publish_specs(snapshot.source_files, snapshot.html_files):
        item = row_bytes(path, reader(path))
        if release_name is not None:
            item["release_name"] = release_name
        if repo_path is not None:
            item["repo_path"] = repo_path
        files.append(item)
    return {
        "schema": "o017-english-publish-manifest-v1", "status": "PASS",
        "language": "en", "version": VERSION, "units": UNITS,
        "publication_verified": False, "package_qa_sha256": digest(outputs[PACKAGE_QA]),
        "input_snapshot_manifest_sha256": snapshot_manifest_sha256(snapshot), "files": files,
    }


def make_checksums(snapshot: InputSnapshot, outputs: Mapping[str, bytes]) -> bytes:
    reader = combined_reader(snapshot, outputs)
    return "".join(
        f"{digest(reader(name))}  {PurePosixPath(name).name}\n" for name in CHECKSUM_TARGETS
    ).encode("ascii")


def parse_checksums(data: bytes) -> list[tuple[str, str]]:
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as error:
        raise RuntimeError("Release checksum file is not ASCII") from error
    if not text or not text.endswith("\n") or "\r" in text:
        raise RuntimeError("Release checksum file must use canonical LF-terminated lines")
    rows: list[tuple[str, str]] = []
    names: list[str] = []
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\\r\n]+)", line)
        if match is None:
            raise RuntimeError("Malformed release checksum line")
        sha256, filename = match.groups()
        safe_name(filename)
        names.append(filename)
        rows.append((filename, sha256))
    assert_unique_names(names, "checksum")
    return rows


def verify_checksum_closure(manifest: dict, checksum_data: bytes) -> None:
    release_rows: dict[str, dict] = {}
    for item in require_list(manifest.get("files"), "publish manifest files"):
        record = require_dict(item, "publish manifest row")
        release_name = record.get("release_name")
        if release_name is not None:
            if type(release_name) is not str or release_name in release_rows:
                raise RuntimeError("Malformed or duplicate release asset name")
            release_rows[release_name] = record
    checksum_name = PurePosixPath(CHECKSUMS).name
    expected_names = [PurePosixPath(name).name for name in CHECKSUM_TARGETS]
    if set(release_rows) != set(expected_names) | {checksum_name}:
        raise RuntimeError("Publish manifest release assets differ from the exact expected inventory")
    parsed = parse_checksums(checksum_data)
    if [name for name, _sha in parsed] != expected_names:
        raise RuntimeError("Checksum file does not cover the exact release assets in canonical order")
    for name, sha256 in parsed:
        if release_rows[name].get("sha256") != sha256:
            raise RuntimeError(f"Checksum-to-manifest binding differs: {name}")
    if checksum_name not in release_rows:
        raise RuntimeError("Checksum file itself is not bound by the publish manifest")


def archive_records_from(outputs: Mapping[str, bytes]) -> list[dict]:
    result: list[dict] = []
    for path, kind in ((SOURCE_ZIP, "editable-source-and-backend"), (HTML_ZIP, "offline-semantic-html")):
        record = verify_archive(outputs[path], kind)
        record.update({"path": path, "identical_second_generation": True})
        result.append(record)
    return result


def verify_release_data(snapshot: InputSnapshot, outputs: Mapping[str, bytes], evidence: dict) -> dict:
    if set(outputs) != set(GENERATED_OUTPUTS):
        raise RuntimeError("Generated output map differs from the exact package inventory")
    archive_records = archive_records_from(outputs)
    source_payload = load_payload(snapshot.read, snapshot.source_files)
    html_payload = load_payload(snapshot.read, snapshot.html_files, "build/html/")
    expected_qa = make_package_qa(snapshot, evidence, source_payload, html_payload, archive_records)
    expected_qa_bytes = jbytes(expected_qa)
    for name in (PACKAGE_QA, RELEASE_PACKAGE_QA):
        parsed = require_dict(parse_json(outputs[name], name), name)
        if parsed != expected_qa or outputs[name] != expected_qa_bytes:
            raise RuntimeError(f"Package QA is not the canonical binding of all final gates: {name}")
    if outputs[PACKAGE_QA] != outputs[RELEASE_PACKAGE_QA]:
        raise RuntimeError("Repository and release copies of package QA differ")

    manifest = require_dict(parse_json(outputs[PUBLISH_MANIFEST], PUBLISH_MANIFEST), PUBLISH_MANIFEST)
    expected_manifest = make_publish_manifest(snapshot, outputs)
    if manifest != expected_manifest or outputs[PUBLISH_MANIFEST] != jbytes(expected_manifest):
        raise RuntimeError("Publish manifest differs from the exact generated inventory")
    if not manifest["files"] or manifest["files"][0]["path"] != PDF:
        raise RuntimeError("First release asset must be the English PDF")
    verify_checksum_closure(manifest, outputs[CHECKSUMS])
    if outputs[CHECKSUMS] != make_checksums(snapshot, outputs):
        raise RuntimeError("Checksum bytes differ from the canonical bidirectional closure")

    reader = combined_reader(snapshot, outputs)
    for item in manifest["files"]:
        check_row(item, reader)
    paths = [item["path"] for item in manifest["files"]]
    repo_paths = [item["repo_path"] for item in manifest["files"] if "repo_path" in item]
    release_names = [item["release_name"] for item in manifest["files"] if "release_name" in item]
    assert_unique_names(paths, "publish path")
    assert_unique_names(repo_paths, "repository destination")
    assert_unique_names(release_names, "release asset")
    if any(not path.startswith(("en/", "english/")) for path in repo_paths):
        raise RuntimeError("Repository destination violates the additive English boundary")
    if RESERVATION in paths or PurePosixPath(RESERVATION).name in release_names:
        raise RuntimeError("Zenodo reservation transaction state leaked into package inventory")
    return {
        "status": "PASS", "files": len(paths), "release_assets": len(release_names),
        "archives": archive_records, "public_release_verified": False,
    }


def build_outputs(snapshot: InputSnapshot, evidence: dict) -> tuple[dict[str, bytes], dict]:
    source_payload = load_payload(snapshot.read, snapshot.source_files)
    html_payload = load_payload(snapshot.read, snapshot.html_files, "build/html/")
    outputs: dict[str, bytes] = {}
    archive_records: list[dict] = []
    for path, payload, kind in (
        (SOURCE_ZIP, source_payload, "editable-source-and-backend"),
        (HTML_ZIP, html_payload, "offline-semantic-html"),
    ):
        first, second = archive_bytes(payload, kind), archive_bytes(payload, kind)
        if first != second:
            raise RuntimeError("Repeated deterministic ZIP generation differs")
        outputs[path] = first
        record = verify_archive(first, kind)
        record.update({"path": path, "identical_second_generation": True})
        archive_records.append(record)
    for original, filename in LOOSE_COPIES:
        outputs["release/" + filename] = snapshot.read(original)
    qa_data = jbytes(make_package_qa(snapshot, evidence, source_payload, html_payload, archive_records))
    outputs[PACKAGE_QA] = qa_data
    outputs[RELEASE_PACKAGE_QA] = qa_data
    outputs[CHECKSUMS] = make_checksums(snapshot, outputs)
    outputs[PUBLISH_MANIFEST] = jbytes(make_publish_manifest(snapshot, outputs))
    return outputs, verify_release_data(snapshot, outputs, evidence)


def _write_staged(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _capture_output_bytes() -> dict[str, bytes]:
    return {name: read_live_stable(name) for name in GENERATED_OUTPUTS}


def _rollback_outputs(stage: Path, committed: list[str], existed: set[str]) -> None:
    failures: list[str] = []
    for name in reversed(committed):
        target = local(name)
        backup = stage / "previous" / Path(*PurePosixPath(name).parts)
        try:
            if name in existed:
                os.replace(backup, target)
            elif target.exists():
                target.unlink()
        except OSError as error:
            failures.append(f"{name}: {error}")
    if failures:
        raise RuntimeError("Package rollback failed: " + "; ".join(failures))


@contextlib.contextmanager
def exclusive_package_lock():
    lock_path = ROOT / ".package-english.lock"
    descriptor: int | None = None
    identity: tuple[int, int] | None = None
    try:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as error:
            raise RuntimeError("Another packaging or release-verification transaction is active") from error
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        lock_stat = os.fstat(descriptor)
        identity = (lock_stat.st_dev, lock_stat.st_ino)
        yield
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if identity is not None:
            try:
                path_stat = lock_path.stat()
                if (path_stat.st_dev, path_stat.st_ino) == identity:
                    lock_path.unlink()
            except FileNotFoundError:
                pass


def commit_outputs(snapshot: InputSnapshot, outputs: Mapping[str, bytes], evidence: dict) -> None:
    stage = Path(tempfile.mkdtemp(prefix=".package-english-stage-", dir=ROOT))
    committed: list[str] = []
    existed: set[str] = set()
    try:
        staged_root = stage / "new"
        for name, data in outputs.items():
            _write_staged(staged_root / Path(*PurePosixPath(name).parts), data)
        staged_names = sorted(
            path.relative_to(staged_root).as_posix() for path in staged_root.rglob("*") if path.is_file()
        )
        if staged_names != sorted(GENERATED_OUTPUTS):
            raise RuntimeError("Immutable staging inventory differs from the exact generated outputs")
        for name, expected in outputs.items():
            if (staged_root / Path(*PurePosixPath(name).parts)).read_bytes() != expected:
                raise RuntimeError(f"Immutable staging bytes changed: {name}")

        snapshot.assert_inputs_unchanged()
        snapshot.assert_reservation_unchanged()
        snapshot.assert_output_prestate_unchanged()
        for name in GENERATED_OUTPUTS:
            target = local(name)
            if target.exists():
                existed.add(name)
                backup = stage / "previous" / Path(*PurePosixPath(name).parts)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(target, backup)
                if read_live_stable(name) != backup.read_bytes():
                    raise RuntimeError(f"Could not freeze prior output for rollback: {name}")

        # Withdraw the previous commit marker before touching its governed files.
        # The new canonical manifest is installed last, so an observer sees either
        # the old complete generation or no committed generation, never a false
        # assertion that a mixed generation is complete.
        if PUBLISH_MANIFEST in existed:
            withdrawn = stage / "withdrawn" / Path(*PurePosixPath(PUBLISH_MANIFEST).parts)
            withdrawn.parent.mkdir(parents=True, exist_ok=True)
            os.replace(local(PUBLISH_MANIFEST), withdrawn)
            committed.append(PUBLISH_MANIFEST)

        commit_order = [name for name in GENERATED_OUTPUTS if name != PUBLISH_MANIFEST] + [PUBLISH_MANIFEST]
        for name in commit_order:
            target = local(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_root / Path(*PurePosixPath(name).parts), target)
            if name not in committed:
                committed.append(name)

        if release_inventory(require_complete=True) != EXPECTED_RELEASE_NAMES:
            raise RuntimeError("Final release-directory inventory differs")
        snapshot.assert_reservation_unchanged()
        actual = _capture_output_bytes()
        if actual != dict(outputs):
            raise RuntimeError("Atomic final replacements differ from the staged coherent generation")
        verify_release_data(snapshot, actual, evidence)
        snapshot.assert_inputs_unchanged()
        snapshot.assert_reservation_unchanged()
    except Exception:
        if committed:
            _rollback_outputs(stage, committed, existed)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def package() -> dict:
    with exclusive_package_lock():
        snapshot = capture_snapshot(require_complete_release=False)
        evidence = validate_inputs(snapshot)
        outputs, verified = build_outputs(snapshot, evidence)
        commit_outputs(snapshot, outputs, evidence)
        archives = verified["archives"]
        return {
            "status": "PASS", "release_assets": len(RELEASE_ASSETS),
            "repository_files": sum(
                repo_path is not None
                for _path, _release_name, repo_path in publish_specs(snapshot.source_files, snapshot.html_files)
            ),
            "source_zip_bytes": archives[0]["bytes"], "html_zip_bytes": archives[1]["bytes"],
            "manifest": PUBLISH_MANIFEST, "public_release_verified": False,
        }


def verify_release() -> dict:
    with exclusive_package_lock():
        snapshot = capture_snapshot(require_complete_release=True)
        evidence = validate_inputs(snapshot)
        outputs = _capture_output_bytes()
        result = verify_release_data(snapshot, outputs, evidence)
        snapshot.assert_inputs_unchanged()
        snapshot.assert_reservation_unchanged()
        # The validator admits only the exact canonical outputs plus the
        # manifest-addressed reservation binding and sanitized publication
        # receipts.  Those private sidecars are intentionally outside the
        # public package closure, so requiring equality with the public base
        # inventory here would make a correctly bound release unverifiable.
        release_inventory(require_complete=True)
        return result


def _expect_runtime_error(action: Callable[[], object], label: str) -> None:
    try:
        action()
    except RuntimeError:
        return
    raise RuntimeError(f"Negative self-test did not fail: {label}")


def self_test() -> dict:
    invalid = (
        "../x", "/x", "a/../x", "a\\x", "a//x", "C:/x", "a/./x",
        "CON", "con.txt", "aux/readme.txt", "LPT9.md", "COM1/data",
        "CONIN$", "conout$.txt", "trailing./x", "space /x", "bad?.txt",
        "control\x01.txt", "COM\u00b9.txt", "CLOCK$.txt", "\U0001f600" * 121,
    )
    for name in invalid:
        _expect_runtime_error(lambda name=name: safe_name(name), f"unsafe path {name!r}")
    _expect_runtime_error(lambda: assert_unique_names(["A/file.txt", "a/file.txt"], "fixture"), "casefold collision")
    _expect_runtime_error(
        lambda: assert_unique_names(["caf\u00e9.txt", "cafe\u0301.txt"], "fixture"),
        "Unicode-normalization collision",
    )
    _expect_runtime_error(
        lambda: assert_unique_names(["file", "file/child.txt"], "fixture"),
        "file/directory-prefix collision",
    )
    _expect_runtime_error(
        lambda: parse_json(b'{"status":"PASS","status":"FAIL"}', "duplicate fixture"),
        "duplicate JSON key",
    )
    _expect_runtime_error(
        lambda: parse_checksums(("0" * 64 + "  A.txt\n" + "1" * 64 + "  a.txt\n").encode("ascii")),
        "checksum portable collision",
    )
    _expect_runtime_error(
        lambda: verify_checksum_closure({"files": []}, ("0" * 64 + "  incomplete.txt\n").encode("ascii")),
        "incomplete checksum closure",
    )

    sample = {"source/example.qmd": b"# Sample\n", "licenses/MIT.txt": b"test fixture\n"}
    _expect_runtime_error(
        lambda: archive_bytes({"release_manifest.json": b"collision\n"}, "self-test"),
        "generated archive-manifest portable collision",
    )
    first, second = archive_bytes(sample, "self-test"), archive_bytes(sample, "self-test")
    if first != second:
        raise RuntimeError("ZIP repeatability self-test failed")
    result = verify_archive(first, "self-test")
    commented = io.BytesIO(first)
    with zipfile.ZipFile(commented, "a") as archive:
        archive.comment = b"forbidden"
    _expect_runtime_error(lambda: verify_archive(commented.getvalue(), "self-test"), "ZIP comment")
    _expect_runtime_error(
        lambda: verify_archive(first, "offline-semantic-html"),
        "archive kind substitution",
    )
    result.update({
        "unsafe_path_negative_tests": len(invalid), "portable_collision_negative_tests": 4,
        "strict_json_negative_tests": 1, "checksum_closure_negative_tests": 2,
        "zip_metadata_and_kind_negative_tests": 2,
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check-inputs", action="store_true", help="Check final QA and public inputs without creating packages")
    group.add_argument("--verify", action="store_true", help="Verify already-created local release bytes")
    group.add_argument("--verify-archive", type=Path, help="Verify one ZIP against its embedded manifest")
    group.add_argument("--self-test", action="store_true", help="Run in-memory archive, JSON, checksum, and path tests only")
    args = parser.parse_args()
    if args.verify_archive:
        result = verify_archive(args.verify_archive.read_bytes())
    elif args.verify:
        result = verify_release()
    elif args.check_inputs:
        snapshot = capture_snapshot(require_complete_release=False)
        evidence = validate_inputs(snapshot)
        source = load_payload(snapshot.read, snapshot.source_files)
        html = load_payload(snapshot.read, snapshot.html_files, "build/html/")
        result = {"status": "PASS", "source_files": len(source), "html_files": len(html), "evidence": evidence}
    elif args.self_test:
        result = self_test()
    else:
        result = package()
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
