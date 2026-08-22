# Reproducible build

Release version: `2026.08.22`.

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

## Reader and backend

From the extracted release root, run:

```text
python scripts/build_and_admit.py --unit O017-U09
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

The resulting 128-page A4 book is
`output/pdf/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.22.pdf`.
The title page carries the version DOI, concept DOI, HTML reader URL, GitHub
source URL, production disclosure, and the controlling rights-file pointer.
The PDF profile uses the same ten QMD files as the HTML reader and preserves
the nine unit numbers in source order.

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
python scripts/build_release.py
```

The release builder uses an explicit allowlist, fixed ZIP timestamps,
deterministic entry order, path-safety checks, per-entry SHA-256 verification,
and a second byte-identical build before emitting the release receipt.

Start the offline reader at `build/html/index.html` after a local static server
or by extracting the published HTML archive and opening `index.html`.
