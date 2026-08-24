# PDF visual QA - O017/D120 edition 2026.08.24

- Status: `PASS`
- PDF: `output/pdf/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.24.pdf`
- PDF SHA-256: `2bfda5d095913829da095ac930d8f1aa61613bfb46c2375970183cb77acdefbb`
- Extent: 133 A4 pages
- Renderer: Poppler `pdftoppm`, PNG at 110 dpi for every page
- Coverage: all 133 pages were inspected through seven ordered contact sheets.
  Pages 1, 2, 7, 8, 12, 20, 30, 42, 44, 45, 58, 71, 83, and 99-106 were
  additionally inspected at original image detail. Two independent regression
  checks covered proof endings on pages 12, 20, 30, 44, and 71 and the
  reflowed Unit 8 material on pages 99-106.

The title page visibly contains the version DOI, concept DOI, live semantic
HTML reader URL, GitHub source URL, Zenodo record URL, exact production
disclosure, untagged-PDF limitation, and rights-map pointer. The terminology
and production-provenance callout on page 8 is legible and names the official
arXiv TeX witness without importing its text or figures. The table of contents
begins with the unnumbered edition preface. Unit 1 through Unit 9 remain
Chapters 1 through 9 in source order, followed by the separately named
delivery wrapper.

The first rendered candidate exposed two layout classes that were corrected
before this receipt was issued. Explicit `\\square` tokens were removed from
five Pandoc proof blocks so pages 12, 20, 30, 44, and 71 now show exactly one
right-aligned proof-end marker. The ten-column Unit 8 seminar template and
worked notes, plus the seven-column response matrix, were reflowed as a
two-column field template and full-width structured records. Pages 99-106 now
have no cross-column collisions, overlapping headers, or unreadably narrow
cells.

No rendered page is blank. No heading, paragraph, formula, table, code block,
callout, header, footer, page number, URL, or bibliography entry is clipped
outside the A4 page. The 24 mm left and right margins produce a centered,
full-width text block. Long hashes, commits, paths, and IDs break within the
page. Dense tables remain inside the page; code and long identifiers wrap or
use their allocated columns. Color links remain legible against the white
background. Sparse pages are intentional unit-end or recto transitions. The
delivery wrapper is one Chapter 10 rather than multiple accidental chapters.

The rendered PNGs and contact sheets are temporary inspection surfaces, not
release artifacts. Machine-readable identity, outline, annotation, page-size,
text, physical-page text bounds, font, and tag checks are recorded in
`qa/PDF_QA.json` and `qa/PDF_FONT_AND_TAG_AUDIT_2026.08.24.json`.
