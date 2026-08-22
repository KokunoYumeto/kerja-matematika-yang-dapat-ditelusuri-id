"""Check the isolated HTML/PDF rebuild produced by rebuild_and_verify.sh."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from pypdf import PdfReader


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_rebuild.py STAGE_ROOT")
    stage = Path(sys.argv[1]).resolve()
    html_root = stage / "build" / "html"
    pdf_candidates = sorted((stage / "output" / "pdf").glob("*.pdf"))
    if len(pdf_candidates) != 1:
        raise RuntimeError(f"expected one rebuilt PDF, observed {pdf_candidates!r}")
    pdf = pdf_candidates[0]
    html_files = sorted(html_root.rglob("*.html"))
    required_html = {
        html_root / "index.html",
        *(html_root / "units" / name for name in (
            "01-membaca-argumen.html",
            "02-menelusuri-sumber.html",
            "03-merekonstruksi-pembuktian.html",
            "04-sitasi-provenance-catatan-sumber.html",
            "05-eksposisi-matematika.html",
            "06-komputasi-dapat-direproduksi.html",
            "07-errata-koreksi-batas-kepastian.html",
            "08-seminar-penelaah-tanggapan-kritik.html",
            "09-kontribusi-komunitas-portofolio.html",
        )),
        html_root / "wrapper" / "index.html",
    }
    missing_html = sorted(str(path) for path in required_html if not path.is_file())
    if missing_html:
        raise RuntimeError(f"required HTML pages missing: {missing_html}")
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if 'lang="id-ID"' not in text:
            raise RuntimeError(f"missing id-ID identity: {path}")
    unit_pages = sorted((html_root / "units").glob("*.html"))
    if len(unit_pages) != 9:
        raise RuntimeError(f"expected nine unit pages, observed {len(unit_pages)}")
    if not all("<math" in path.read_text(encoding="utf-8") for path in unit_pages):
        raise RuntimeError("one or more rendered units lacks native MathML")

    reader = PdfReader(pdf)
    if reader.is_encrypted or len(reader.pages) < 128:
        raise RuntimeError("rebuilt PDF is encrypted or lost pages from the preserved edition")
    if any(not (page.extract_text() or "").strip() for page in reader.pages):
        raise RuntimeError("one or more rebuilt PDF pages has no extractable text")

    payload = {
        "status": "PASS",
        "stage": str(stage),
        "html": {
            "pages": len(html_files),
            "native_mathml_unit_pages": len(unit_pages),
            "bytes": sum(path.stat().st_size for path in html_root.rglob("*") if path.is_file()),
        },
        "pdf": {
            "path": str(pdf),
            "pages": len(reader.pages),
            "bytes": pdf.stat().st_size,
            "sha256": digest(pdf),
            "all_pages_have_extractable_text": True,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
