# Unit 7 English translation QA

Date: 2026-08-31. Scope: additive English edition of original O017 Unit 7.

## Files and hashes

- Source: `source/units/07-errata-koreksi-batas-kepastian.qmd`
- Source bytes: 52,178.
- Source SHA-256: `dac211708a859a8bf93f800395ff252caa4554c30c0f3994356ab98fa6a24c91`.
- English: `english-edition/source/units/07-errata-koreksi-batas-kepastian.qmd`
- English bytes: 53,041.
- English SHA-256: `6e2b7f387afc44b4b8cd2a9e30b8825206a0c75c30b7e3cde03f8eb1b80ccc65`.

## Completeness

Read the entire Indonesian source in four bounded line ranges before writing.
Translated every heading, paragraph, table, callout title, accessibility label,
learning outcome, worked connectedness case, proof, local synthetic erratum
draft, six-sentence template, uncertainty ledger, protocol, checklist, all six
exercises, all six complete guidance answers, final synthetic packet, all twelve
completion requirements, and the full rubric. This is not an abridgment.

All disclaimers that packets are synthetic and drafts are local and unsent
remain explicit. Statements of uncertainty, severity, confidence, and evidence
boundaries retain their distinctions. No report was sent and no external source
or donor was contacted. This unit contains no external donor prose and no
executable code.

## Deterministic parity checks

- 62 explicit anchors in each file: identical names and order.
- 49 O017-U07 identifier occurrences in each file: identical values and order.
- 39 level-two/level-three headings in each file.
- 98 Markdown table rows in each file.
- 48 fenced-div delimiter lines in each file.
- 135 mathematical spans in each file: identical after whitespace
  normalization and the single prose-only LaTeX translation below.
- One fenced text relationship diagram in each file: identical content.
- Seven Markdown link targets in each file: identical values and order.
- 179 inline-code spans in each file; every machine identifier, formula-adjacent
  status enum, revision, synthetic version label, command-like input, and
  recorded computational output retained. Only the six reader-facing status
  descriptions listed below were translated.
- Six exercise anchors X01–X06 and six answer anchors H01–H06 retained.
- The `gridmax.py@r1`/`gridmax.py@r2` mismatch, `step=0.01`, `[0,1]`, and
  `argmax_grid=0.99` remain unchanged; no fabricated execution was added.

## Deliberate translation-only differences

The display formula joining the sets U and V changes `\text{dan}` to
`\text{and}`. Its mathematical symbols and relationships are unchanged.

Reader-facing status descriptions in inline-code style are translated as
follows; these are prose examples, not stable IDs or executed code:

| Indonesian | English |
|---|---|
| `C3 ditetapkan` | `C3 established` |
| `terbuka` | `open` |
| `sedang diuji` | `under-test` |
| `ditutup-didukung` | `closed-supported` |
| `ditutup-tidak dapat dipastikan` | `closed-undetermined` |
| `belum diketahui` | `unknown` |

The immutable synthetic version labels `1.0-sintetis` and `1.2-sintetis`
remain unchanged. Synthetic work titles are translated while their work IDs
are retained. The provenance section explicitly distinguishes the original
Indonesian O017 material from this English translation and preserves O017
contributor credit, 2026, and CC BY-SA 4.0.

## Remaining integration work

No unit-local semantic or structural defect was found in the translation.
Rendering, whole-book cross-reference checks, publication, and release QA are
the parent task's integration responsibilities; no build, Git operation,
network request, or publication was performed by this bounded unit task.
