# Component rights and licenses

Release identity: `O017-EDITION-01`, version `2026.08.24`.

The public rights-holder and licensor identity for protectable original output is
**KokunoYumeto**. The edition was produced with OpenAI Codex gpt-5.6-sol, Ultra.
under the human creator’s
direction; Codex is identified as the production system, not as a copyright owner or legal
licensor. In earlier internal controls, “O017 contributors” refers to this
directed production process. This disclosure does not claim human peer review,
institutional endorsement, or authorship of cited classical mathematics.

Rights are assigned per component. No blanket license is asserted over every
byte in either archive.

## Public-path rights map

Archive-relative paths below are controlling. Paths beginning `build/html/` in
the live tree become their flattened counterparts in the offline-reader ZIP:
for example `build/html/index.html` becomes `index.html`. Flattening does not
change a component’s license.

| Public path or class | Rights treatment |
|---|---|
| `source/index.qmd`, `source/units/*.qmd`, `source/wrapper/index.qmd`, `delivery/README.md`, `delivery/calibration/*.md`, and expressive delivery definitions | Original reader and delivery-wrapper expression: CC BY-SA 4.0, subject to the preserved CC BY 4.0 donor attributions below. Calibration cases are examples, not claims of real learner completion or external participation. |
| `index.html`, `units/*.html`, `wrapper/index.html`, `delivery/**`, `search.json` and live-tree `build/html/` counterparts | Corresponding expressive reader and delivery-wrapper output: CC BY-SA 4.0, subject to donor attribution and the runtime exceptions below. Factual manifest fields remain factual. |
| `output/pdf/*.pdf` and the loose release PDF | Corresponding expressive reader output: CC BY-SA 4.0, subject to the preserved donor attributions. Embedded/subset font programs are separate components under the GUST Font License 1.0 or SIL OFL 1.1 as identified below; the reader license does not relicense them. Bibliographic facts and identifiers remain factual. |
| `backend/records.jsonl`, `backend/semantic-wrapper-v1.records.jsonl`, `backend/semantic-wrapper-v1.localizations.jsonl`, `backend/semantic-wrapper-v1.dataset.json`, and `backend/SEMANTIC_WRAPPER_V1.md` | File as a whole: CC BY-SA 4.0 because labels, descriptions, rubrics, and localized text are expressive; embedded free facts remain free facts. |
| `README.md`, `BUILD.md`, `CITATION.cff`, `release/zenodo_metadata.json` | Original explanatory, citation, and descriptive expression: CC BY-SA 4.0; purely factual fields are also dedicated under CC0 as stated below. |
| `controls/SOURCE_FREEZE.md`, `controls/REQUIREMENTS_AND_NON_OVERLAP.md`, `controls/TERMINOLOGY.csv` | Original analytical prose, classifications, and terminology choices: CC BY-SA 4.0. |
| `qa/*_ADMISSION.md`, `qa/*_QA.json`, `qa/*_VISUAL_QA.json`, `qa/PDF_VISUAL_QA.md`, and standalone public `RELEASE_PACKAGE_QA.json` | File as a whole: CC BY-SA 4.0 where it contains narrative or reader-witness expression; purely factual fields are also CC0. |
| `qa/visual/**/*.png` | Composite render evidence: original reader expression is CC BY-SA 4.0; donor text and browser-runtime elements retain their component terms described below. |
| `scripts/*`, `source/code/*`, flattened `code/*`, `source/_quarto.yml`, `source/_quarto-pdf.yml`, `source/pdf-header.tex`, `source/styles.css`, flattened `styles.css`, `.nojekyll`, `.gitignore`, `backend/*.schema.json`, `backend/schema.json`, `delivery/schema/*.json`, and `environment/Containerfile`, `environment/*.py`, `environment/*.sh` | Original software, configuration, styling, and schema: MIT; purely factual expected-output and lock fields are also covered by the CC0 dedication below. |
| `backend/relations.csv`, `backend/relations-ledger.csv`, `backend/semantic-wrapper-v1.relations-ledger.csv`, `backend/semantic-wrapper-v1.baseline.json`, `backend/manifest.csv`, `delivery/FILE_MANIFEST.csv`, `delivery/VALIDATION.json`, `environment/OCI_IMAGE_LOCK.json`, `environment/requirements.lock.txt`, `build/unit-01-mst-check.json`, `source/references.bib`, `authority/SOURCE_FREEZE.json`, `controls/SOURCE_RIGHTS_MANIFEST.csv`, `RELEASE_PROVENANCE.csv`, `qa/PDF_QA.json`, archive `RELEASE_MANIFEST.json`, `SHA256SUMS.txt`, and purely factual receipt fields | CC0 1.0 to the extent they consist of identifiers, bibliographic facts, hashes, measurements, relations, manifests, lock data, or execution results. |
| `site_libs/*` and live-tree `build/html/site_libs/*` | Third-party MIT or Apache-2.0 runtime; see `THIRD_PARTY_NOTICES.md`. |
| `LICENSES.md`, `THIRD_PARTY_NOTICES.md`, the font-license and notice texts in `licenses/`, `licenses/FONT_COMPONENT_PROVENANCE.json`, and `qa/PDF_FONT_AND_TAG_AUDIT_*.{json,md}` | Redistribution-required legal, provenance, notice, and factual audit material. Original explanation is CC BY-SA 4.0; factual measurements are CC0 where possible; canonical license texts, copyright notices, font programs, and third-party notices are not relicensed. |

## Original reader expression — CC BY-SA 4.0

The original components identified above are made available under the Creative
Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0),
<https://creativecommons.org/licenses/by-sa/4.0/>.

Attribution: “KokunoYumeto, *Kerja Matematika yang Dapat Ditelusuri*, O017/D120
Bahasa Indonesia edition, version 2026.08.24; produced with OpenAI Codex gpt-5.6-sol, Ultra.” State
changes and preserve this license. Classical mathematical facts and theorems
are not claimed as original.

Units 2, 4, 5, and 6 contain bounded methodological adaptations from the donor
works listed below. Their in-reader provenance sections preserve creator,
immutable source version, CC BY 4.0 license, change notice, and non-endorsement
boundary. The resulting unit text is distributed under CC BY-SA 4.0, which is
compatible with the donors’ CC BY 4.0 terms, while donor attribution remains
mandatory.

## Render-evidence screenshots

Every `qa/visual/**/*.png` in the public source/evidence archive is derived
from the corresponding composite HTML page. Original O017 expression visible
in those screenshots is CC BY-SA 4.0. Donor-adapted text visible in screenshots
retains its CC BY 4.0 attribution and change-notice requirements. Quarto and
bundled browser-runtime elements retain the MIT or Apache-2.0 terms identified
in `THIRD_PARTY_NOTICES.md`. Redistribute screenshots together with
`LICENSES.md`, `THIRD_PARTY_NOTICES.md`, and `RELEASE_PROVENANCE.csv`; this
classification does not relicense donor or runtime material.

## Original software and schema — MIT

Copyright © 2026 KokunoYumeto.

The original software, configuration, styling, and schema paths identified in
the table are licensed under the MIT License. The full permission and warranty
text is in `licenses/MIT.txt`; the copyright notice above must be retained.

## Generated factual data — CC0 1.0

The factual components and fields identified in the table are dedicated, to the
extent legally possible, under CC0 1.0 Universal,
<https://creativecommons.org/publicdomain/zero/1.0/>. A CC0 factual field inside
an otherwise expressive JSON or Markdown file does not change the file-level
CC BY-SA treatment required for its expressive parts. Quoted reader text and
other expressive witness strings retain the same reader and donor terms as
their source.

## Frozen methodological donors — CC BY 4.0

- *The Turing Way*: selected methodological content is CC BY 4.0; software and
  infrastructure are MIT where stated. Preserve “Copyright © The Turing Way
  Community,”
  commit `c98a0e6ca47450456cca7c5eedda2d5ee131d1ce`, the license/change
  notice, applicable Scriberia figure credits, relevant DOIs, and the nested
  René Bekkers attribution.
- *Research Software Engineering with Python*: selected prose is CC BY 4.0.
  Preserve all six authors, commit
  `62217e6606842ab9752fcf8e73954d1eb4a3cf07`, the license link, and the
  translation/adaptation notice. Preserve its MIT notice if code is copied.

The public release does not bundle the frozen donor witness trees. Exact
repositories, commits, trees, selected-file hashes, licenses, and adapted units
are recorded in `RELEASE_PROVENANCE.csv`. Local `authority/` donor witnesses
remain under their own notices and are never relicensed by this file.

## Rendered HTML runtime

The offline HTML reader is a composite. Reader expression follows the rules
above; bundled Quarto, Bootstrap, search, positioning, tooltip, navigation, and
icon runtimes retain their own MIT or Apache-2.0 licenses. Exact versions,
paths, copyright notices, official sources, and full license texts are in
`THIRD_PARTY_NOTICES.md` and `licenses/`.

## Embedded PDF fonts

The PDF embeds subsets of four separately licensed font components. Embedding
does not relicense a font under CC BY-SA, MIT, or CC0.

- **Latin Modern text v2.004** — Copyright 2003, 2009 B. Jackowski and
  J. M. Nowacki (on behalf of TeX users groups). GUST Font License 1.0:
  LPPL 1.3c or later plus its nonbinding font/file-name change request. Full
  text: `licenses/GUST-FONT-LICENSE-1.0.txt`.
- **Latin Modern Math v1.959** — Copyright 2012–2014 B. Jackowski,
  P. Strzelczyk, and P. Pianowski (on behalf of TeX Users Groups). GUST Font
  License 1.0. Package notice: `licenses/LATIN-MODERN-MATH-1.959-README.txt`;
  full license: `licenses/GUST-FONT-LICENSE-1.0.txt`.
- **Font Awesome 5 Free Solid v5.15.4 font** — Copyright © Font Awesome.
  SIL Open Font License 1.1 for the font file. Component notice:
  `licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt`; OFL text:
  `licenses/SIL-OFL-1.1.txt`.
- **AMSFonts MSAM10 Type 1 v003.002 (AMSFonts 3.04)** — Copyright © 1997,
  2009 American Mathematical Society. SIL Open Font License 1.1; `msam10` is a
  Reserved Font Name. Package notice and license:
  `licenses/AMSFonts-3.04-README.txt` and `licenses/AMSFonts-3.04-OFL.txt`.

Exact embedded objects, versions, official sources, and hashes are frozen in
`licenses/FONT_COMPONENT_PROVENANCE.json`. Preserve that manifest and the
listed notices with every PDF redistribution.

## No additional grant

Names, marks, canonical legal text, and third-party attribution statements are
not relicensed. No license in this package implies endorsement by donor
communities, authors, OpenAI, Quarto, Posit, or any upstream maintainer.
