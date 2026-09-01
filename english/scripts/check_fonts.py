"""Verify embedded-source font identities and required Unicode coverage."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "qa/MONOSPACE_FONT_QA.json"
FONT_DIR = ROOT / "source/fonts"
LICENSE = ROOT / "licenses/DejaVu-Font-License.txt"
COMMIT = "e055422f2643c8dc4718fb2269daeb3f707ccc4b"
EXPECTED_FONTS = (
    "DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf",
    "DejaVuSansMono-Oblique.ttf", "DejaVuSansMono-BoldOblique.ttf",
    "DejaVuSerif.ttf", "DejaVuSerif-Bold.ttf",
    "DejaVuSerif-Italic.ttf", "DejaVuSerif-BoldItalic.ttf",
)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_report() -> dict:
    units = sorted((ROOT / "source/units").glob("*.qmd"))
    if len(units) != 9:
        raise RuntimeError("Expected exactly nine unit sources")
    pattern = re.compile(r"(?ms)^(`{3,})([^\n]*)\n(.*?)^\1\s*$")
    blocks = [m.group(3) for path in units for m in pattern.finditer(path.read_text(encoding="utf-8"))
              if not m.group(2).strip().startswith("{=")]
    code = "\n".join(blocks)
    points = sorted({ord(char) for char in code if char not in "\r\n\t"})
    prime_occurrences = sum(path.read_text(encoding="utf-8").count("\u2032") for path in units)
    if not blocks or not points or prime_occurrences == 0:
        raise RuntimeError("Source character inventory is unexpectedly empty")
    rows, errors = [], []
    for name in EXPECTED_FONTS:
        path = FONT_DIR / name
        if not path.is_file():
            errors.append(f"Missing font: {name}")
            continue
        font = TTFont(path)
        cmap = {point for table in font["cmap"].tables for point in table.cmap}
        version = next((record.toUnicode() for record in font["name"].names if record.nameID == 5), None)
        missing = [f"U+{point:04X}" for point in points if point not in cmap]
        prime = 0x2032 in cmap
        fs_type = int(font["OS/2"].fsType)
        if version != "Version 2.35" or fs_type != 0 or missing or not prime:
            errors.append(f"Coverage or identity failure: {name}")
        rows.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                     "sha256": sha(path), "version": version, "fsType": fs_type,
                     "missing_fenced_code_points": missing, "covers_U+2032_PRIME": prime})
    config = (ROOT / "source/_quarto-pdf.yml").read_text(encoding="utf-8")
    if any(item not in config for item in ("mainfont: DejaVuSerif", "monofont: DejaVuSansMono", "Path=fonts/")):
        errors.append("PDF font configuration is incomplete")
    license_text = LICENSE.read_text(encoding="utf-8") if LICENSE.is_file() else ""
    complete_license = "Bitstream Vera Fonts Copyright" in license_text and "Arev Fonts Copyright" in license_text
    if not complete_license:
        errors.append("Complete DejaVu license notice is absent")
    return {
        "schema": "o017-english-font-qa-v1", "status": "FAIL" if errors else "PASS",
        "purpose": "Repair missing Unicode proof-diagram strokes/relations and PRIME labels without changing source text.",
        "source": {"project": "DejaVu Fonts", "version": "2.35", "commit": COMMIT,
                   "release_url": "https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_35",
                   "license_url": f"https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/{COMMIT}/dejavu-fonts/LICENSE",
                   "license_path": "licenses/DejaVu-Font-License.txt",
                   "license_sha256": sha(LICENSE) if LICENSE.is_file() else None},
        "source_inventory": {"unit_files": len(units), "fenced_blocks": len(blocks),
                             "fenced_characters": len(code), "distinct_renderable_code_points": len(points),
                             "U+2032_PRIME_occurrences": prime_occurrences},
        "configuration": {"mainfont": "DejaVuSerif", "monofont": "DejaVuSansMono",
                          "path": "source/fonts/", "configuration_path": "source/_quarto-pdf.yml"},
        "fonts": rows, "checks": {"all_expected_fonts_present": len(rows) == len(EXPECTED_FONTS),
            "all_fonts_version_2_35": all(row["version"] == "Version 2.35" for row in rows),
            "all_fonts_fsType_zero": all(row["fsType"] == 0 for row in rows),
            "all_fenced_code_points_covered": all(not row["missing_fenced_code_points"] for row in rows),
            "all_fonts_cover_U+2032_PRIME": all(row["covers_U+2032_PRIME"] for row in rows),
            "complete_license_notice_present": complete_license},
        "errors": errors,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif not REPORT.is_file() or json.loads(REPORT.read_text(encoding="utf-8")) != report:
        raise RuntimeError("Font QA receipt is absent or stale; run --write after an intentional font change")
    print(json.dumps({"status": report["status"], "fonts": len(report["fonts"]),
                      "code_points": report["source_inventory"]["distinct_renderable_code_points"]}))
    if report["status"] != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
