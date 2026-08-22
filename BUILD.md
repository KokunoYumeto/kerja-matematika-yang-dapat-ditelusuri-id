# Reproducible build

Release version: `2026.08.22.1`.

## Pinned witnessed toolchain

- Python 3.13.9
- Quarto 1.9.37
- Node.js 24.19.0 for browser QA
- Playwright 1.62.1
- Microsoft Edge 151.0.4129.93
- MiKTeX 26.5 with XeLaTeX for the A4 PDF

The reader build itself requires Python and Quarto. Node, Playwright, and an
installed Chromium-family browser are required only to reproduce the visual QA
receipts. No Git checkout and no network access are needed to build the reader
from the release source archive.

## Immutable container rebuild

The executable environment authority is `environment/Containerfile` together
with `environment/OCI_IMAGE_LOCK.json` and `environment/requirements.lock.txt`.
The base is the official Quarto Full 1.9.37 image fixed by manifest digest
`sha256:f8a77fcebc054dff1ca887e1789feaaf65cd0e572c00dd81dff58aa1570323de`;
the portable CPython 3.13.9 archive and pypdf 6.12.2 wheel are independently
SHA-256 pinned.

From the extracted edition root on an x86-64 Docker/Podman host:

```sh
docker build --pull=false --file environment/Containerfile --tag o017-rebuild:2026.08.22.1 .
docker run --rm --network none --volume "$PWD:/work:ro" o017-rebuild:2026.08.22.1 bash /work/environment/rebuild_and_verify.sh /work
```

The image build validates Quarto, Python, pypdf, XeLaTeX, the required LaTeX
packages, and all four font families. The offline run uses an isolated temporary
stage, checks both mathematical witnesses, renders the 11-page HTML surface
(index, nine units, and delivery wrapper), renders the PDF, opens every PDF
page, checks Indonesian identity and native MathML, and removes the stage. See
`environment/REBUILD_ENVIRONMENT.md`.

This proves a rebuildable content/tool closure, not cross-engine byte identity.
The local release PDF uses MiKTeX 26.5; the immutable Linux image uses the
TinyTeX bytes in the digest-pinned Quarto image, so PDF timestamps,
compression, font subset names, and hashes can differ. The bounded isolated
host-equivalent smoke test passed; Docker/Podman was unavailable on the release
host, so the OCI image itself was not locally constructed.

## Reader and backend

From the extracted release root, run:

```text
python scripts/build_and_admit.py --unit O017-U09
python scripts/validate_delivery_wrapper.py --write-qa
python scripts/generate_semantic_wrapper.py --check
python scripts/validate_semantic_wrapper.py --write-qa
python environment/verify_environment.py
```

This command executes the declared mathematical computations, renders all nine
units into a staged directory, verifies all source locks, anchors, local links,
assets, exercise–guidance pairs, native MathML, offline runtime closure, stable
backend identities and relations, then atomically promotes `build/html/` and
the backend files.

## PDF book

From `source/`, run the profile-specific book build:

```text
quarto render --profile pdf --to pdf
```

The resulting A4 book is
`output/pdf/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.22.1.pdf`.
The title page carries the version DOI, concept DOI, HTML reader URL, GitHub
source URL, production disclosure, and the controlling rights-file pointer.
The PDF profile uses the landing page, the same nine unit QMD files as the HTML
reader, and the separately identified delivery wrapper in source order.

## Browser evidence

Make Playwright resolvable by Node in the local environment, then run each unit
through the common final-tree script:

```text
node scripts/visual_qa_unit.cjs O017-U01
node scripts/visual_qa_unit.cjs O017-U02
node scripts/visual_qa_unit.cjs O017-U03
node scripts/visual_qa_unit.cjs O017-U04
node scripts/visual_qa_unit.cjs O017-U05
node scripts/visual_qa_unit.cjs O017-U06
node scripts/visual_qa_unit.cjs O017-U07
node scripts/visual_qa_unit.cjs O017-U08
node scripts/visual_qa_unit.cjs O017-U09
node scripts/visual_qa_full_reader.cjs
```

Visual receipts are evidence for this release, not a prerequisite for ordinary
reading or rebuilding.

## Final and release gates

```text
python scripts/finalize_course.py
python scripts/qa_pdf.py
python scripts/audit_pdf_font_accessibility.py
python scripts/build_release.py
```

The release builder uses an explicit allowlist, fixed ZIP timestamps,
deterministic entry order, path-safety checks, per-entry SHA-256 verification,
and a second byte-identical build before emitting the release receipt.

Start the offline reader at `build/html/index.html` after a local static server
or by extracting the published HTML archive and opening `index.html`.
