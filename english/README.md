# Traceable Mathematical Work

Complete English-access edition of the original O017 / D120 course, version
`en2026.08.31`. Public creator and licensor: **KokunoYumeto**. Produced with
**OpenAI Codex gpt-5.6-sol, Ultra** at the human creator's instruction.

The course covers reading mathematical arguments, tracing sources,
reconstructing proofs, citation and provenance, exposition, reproducible
computation, errata, refereeing, and a bounded community contribution.
It contains all nine units (`O017-U01` through `O017-U09`), 54 exercises,
54 answer guides, an introduction and glossary, and the full teaching and
assessment companion: 14 source files including five calibration dossiers.
This is a full translation of the original course, not a summary or another
translation of the already-English Turing Way and PyRSE donor books.

## Access and identity

- [English semantic HTML reader](https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/en/)
- [English PDF](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/releases/download/en-v2026.08.31/traceable-mathematical-work-en-2026.08.31.pdf)
- [English downloads](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/releases/tag/en-v2026.08.31)
- [Editable English source](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/tree/main/english)
  and [frozen source](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/tree/en-v2026.08.31/english)
- [Unchanged Indonesian reader](https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/)

These are the prepared release addresses. Availability and exact public-byte
identity are established by the separate publication receipts, not by the
presence of a URL here.

## What to download

The PDF is print-oriented and **untagged** (`tagged: false`); no PDF/UA
conformance is claimed. The semantic HTML reader is the primary accessible
surface, with native MathML, reflow, structured headings, and keyboard access.
The measured page count and embedded-font checks are in `qa/PDF_QA.json`.

`o017-d120-en-2026.08.31-reader-html.zip` contains the complete HTML site,
bundled runtime, teaching files, rights notices, and license texts. Extract it
and open `index.html`; if a browser restricts local search, serve the extracted
directory with `python -m http.server 8000 --bind 127.0.0.1` and open
`http://127.0.0.1:8000/`. Reading does not require a CDN or an account;
external citations still require internet access.

`o017-d120-en-2026.08.31-source.zip` contains editable source, the bilingual
backend, teaching material, build/check scripts, public documentation,
component notices, and compact QA. It excludes publication credentials,
private coordination, donor witness trees, build caches, and duplicate
rendered outputs. See `BUILD.md` for a standalone rebuild. Each ZIP contains
a `RELEASE_MANIFEST.json` with every payload filename, byte count, and SHA-256.
The loose `ENGLISH-SHA256SUMS.txt` covers the other release assets.

## Language-aware backend

Start with `backend/languages.json` and
`integration/ENGLISH_EDITION.json`. The backend keeps 319 neutral semantic
entities, 581 English semantic localizations, and all 581 Indonesian
localizations; it also supplies 147 English core localizations and 529 English
access locators. IDs and issued relation IDs remain stable. Missing English
translations are errors, not silent fallbacks to Indonesian. The preserved
upstream streams are in `backend/upstream-id-ID/`.

Historical artifact paths and hashes in the original record stream identify
the Indonesian release. For English bytes use the English manifests and
access locators. The archive preserves the Indonesian backend, not a second
copy of the Indonesian reader.

## Evidence and rights boundaries

Checks establish source closure, byte identity, schema validity, local links,
and mathematical witness outputs. They do not establish actual learner
performance, human peer review, credential eligibility, or real community
participation. All calibration people and events remain synthetic;
`credit_eligible` and `transmission_performed` remain false. The teaching
validator is not a complete authentic learner-submission assessment system.

Original expressive course and translation material is CC BY-SA 4.0;
bounded methodological donor content remains CC BY 4.0. Original software and
configuration are MIT; factual identifiers and measurements are CC0 where
possible. Runtime and embedded fonts retain their separate component terms.
Read `ENGLISH_EDITION_RIGHTS.md`, `LICENSES.md`, `THIRD_PARTY_NOTICES.md`, and
`licenses/`; there is no blanket license over all bundled bytes.

Use `CITATION.cff` to cite this edition. Source commits and selected-file
identities for donor adaptations are retained in `RELEASE_PROVENANCE.csv`.
