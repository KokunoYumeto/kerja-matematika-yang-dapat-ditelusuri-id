# Standalone build and verification

Run commands from the root of the extracted English source ZIP (the directory
containing this file). Use an independent extraction directory without
unrelated adjacent `source/` or `backend/` trees. No original workspace, Git repository, account,
publication credential, or donor checkout is needed. All course/build inputs
are local. Install the toolchain first; package installation may require a
network connection. Once the listed tools, TeX packages, and fonts are present,
the reader build and its checks do not retrieve course content from the web.

## Locally tested tools

The producing Windows environment reported these versions on 2026-08-31:

| Tool | Observed version |
|---|---|
| CPython | 3.13.9 |
| Quarto | 1.9.37 |
| XeTeX | MiKTeX-XeTeX 4.18 (MiKTeX 26.5) |
| `pypdf` | 6.12.2 |
| `jsonschema` | 4.26.0 |
| Python zlib | compile-time 1.2.13; runtime 1.3.1 |

These are measured versions, not a claim that a container was run or that an
environment image was locked. Python dependency setup, if needed:

```text
python -m pip install pypdf==6.12.2 jsonschema==4.26.0
```

Quarto and XeLaTeX must be on `PATH`. The PDF uses `scrreprt`, the packages in
`source/pdf-header.tex`, and fonts recorded in
`licenses/FONT_COMPONENT_PROVENANCE.json`: Latin Modern text 2.004, Latin
Modern Math 1.959, Font Awesome 5 Free Solid 5.15.4, and AMSFonts 3.04/MSAM10.
The added DejaVu families are supplied in `source/fonts/` with
`licenses/DejaVu-Font-License.txt`; current configuration and
`qa/MONOSPACE_FONT_QA.json` identify their roles and checked character coverage.
TeX distributions with automatic package installation must be provisioned
before an offline build. An arbitrary fresh machine is not an offline toolchain.

## Build

```text
python scripts/english_backend.py --check
python delivery/validate_english_delivery.py
python scripts/build_english.py --pdf
```

The first command checks the exact generated backend against its frozen
inputs. After intentional edits to the translation maps, regenerate with
`python scripts/english_backend.py`, then rerun `--check`. The teaching check
writes `delivery/validation-standalone-report.json`. The build executes both
standard-library mathematical witnesses, compares their exact expected text,
renders all 11 HTML pages, applies the reader's accessibility adjustments,
checks local links and fragments, and renders/checks the complete PDF.

Outputs are `build/html/index.html` and
`output/pdf/traceable-mathematical-work-en-2026.08.31.pdf`. Without `--pdf`, the
builder only renders/checks HTML. `--check-only --pdf` checks existing rendered
outputs; it also reapplies HTML adjustments and rewrites QA, so it is not a
read-only operation. It is not a fresh build and does not rerun the
mathematical witnesses. Complete validators before sealing package hashes:
the teaching report includes a validation timestamp, and HTML assembly copies
the teaching files into the offline reader.

`controls/INDONESIAN_BASELINE.json` is the only included controls file: a
public, relative-path/hash inventory. The builder can additionally compare
original files if an Indonesian source tree happens to be present immediately
above the English directory. In a standalone extraction those original
comparisons are unavailable; that does not prevent an English build. The
frozen `backend/upstream-id-ID/` snapshot and its manifest are included and
are checked locally. `prepare_reuse.py` is a production bootstrap, not a
standalone requirement, and is deliberately absent from this archive.

## Repackage and verify

After completing a fresh build and the applicable visual/accessibility QA:

```text
python scripts/package_english.py --check-inputs
python scripts/package_english.py
python scripts/package_english.py --verify
```

Packaging uses an explicit public-file allowlist, checks existing QA and its
file hashes against current bytes, checks the two witness outputs, and writes
the source and offline-reader ZIPs plus English-labelled release files. It
does not publish anything or access authentication material. It refuses
unsafe paths and sensitive-looking material. `release/PUBLISH_MANIFEST.json`
is a local integration interface, not evidence of a completed publication.
The final visual receipts are `qa/HTML_VISUAL_QA.json` and
`qa/PDF_VISUAL_QA.json`; they must identify the checked HTML QA hash in
`html_qa_sha256` and the checked PDF hash in `pdf_sha256`, respectively. These
are evidence from the producing build, not automatically renewed by a rebuild.

To check either downloaded ZIP without rebuilding:

```text
python scripts/package_english.py --verify-archive path/to/downloaded.zip
```

Every payload is checked against the embedded `RELEASE_MANIFEST.json` for
exact entry name, byte count, and SHA-256; the manifest excludes itself to
avoid circular hashing. ZIP entries are lexicographically ordered, have a
fixed timestamp of 2026-08-31 00:00:00, fixed file permissions, and DEFLATE
level 9. The packager creates each ZIP twice in memory and requires identical
bytes before writing it. This guarantees repeatability for identical input
bytes with the producing Python/zlib runtime; it does not claim invariance
across every compression implementation. A validator timestamp or changed
QA file is a changed input.

The PDF is **not claimed to be bit-reproducible** across builds or machines.
Font/subset metadata, TeX versions, and other render details may alter bytes.
Check content, layout, font embedding, page count, and accessibility boundaries
again for a new render. The PDF is untagged; semantic HTML remains the primary
accessible surface. Neither automated QA nor synthetic calibration validates
real learner performance. Public-byte verification is a separate release
transaction, recorded separately from these local build/package results.
