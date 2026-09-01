# Unit 4 English translation QA

Date: 2026-08-31.

## Scope and identities

- Source: `source/units/04-sitasi-provenance-catatan-sumber.qmd` in the O017 lane.
- Source bytes: 38,589.
- Source SHA-256: `47547d4d18db7d3719b14ce3914a017d5ef741f01fc31f928365fe1cb0f1fcbb`.
- English output: `english-edition/source/units/04-sitasi-provenance-catatan-sumber.qmd`.
- English output bytes: 39,213.
- English output SHA-256: `881dce3e71429dd1090067d6d8bcf93949ac952460474f5a7c6b7905fd9ad697`.
- Scope: the full original Unit 4, not an abstract or shortened treatment. The Indonesian source is unchanged.

## Content and terminology

All 30 section/subsection headings, learning outcomes, callouts, worked integral case, source and decision records, six exercises, six answer-guidance entries, matrix-norm completion task, rubric, boundaries, and rights notes are translated. Both explanatory text diagrams have English natural-language labels. Synthetic classroom-object labels, partial-packet scope, uncertainty, non-execution status, and the distinction between sufficient and necessary conditions remain explicit.

Terminology consistently distinguishes citation, evidence provenance, computational provenance, mathematical proof, source notebook, normalized claim, locator, work, version, and copy. The work-versus-version citation distinction is preserved without inventing a DOI for the synthetic packet. Evidence is not equated with mathematical proof, and numerical output is not elevated to a universal proof.

The machine field name `status_pelaksanaan_ulang` is deliberately retained for schema compatibility, with an English explanation of rerun status. User-facing status words are translated, including accepted, rejected, qualified, unknown, not applicable, and not yet executed. The inherited stable anchor `o017-u04-six-tables` is retained even though the accurate heading says seven tables.

The provenance section identifies the original Indonesian material and this English translation, retaining O017 contributor credit, the CC BY-SA 4.0 license, both frozen donor commits, donor authors, separate CC BY 4.0 rights, and non-endorsement statements. No already-English donor was translated again; this unit contains bounded conceptual adaptations rather than copied donor passages.

## Deterministic parity checks

- 50 explicit anchors in each file; exact ID multiset match.
- 27 stable `O017-U04-*` ID occurrences in each file; exact multiset match, including all six exercise and all six guidance IDs.
- 4 citation keys and 5 URLs in each file; unchanged.
- 63 mathematical expressions in each file; exact ordered parity after the sole natural-language mathematical-text change `\text{untuk setiap }` to `\text{for every }`. All symbols, hypotheses, bounds, quantifiers, integrals, matrix entries, and norm expressions otherwise match byte-for-byte within the extracted math.
- 30 headings and 40 opening/closing colon-fence lines in each file.
- All 51 relationship-token occurrences within inline code match in order. A whole-prose relationship-word scan has two additional English occurrences because ordinary prose now says “corrects”; there are no new machine relationships.
- Inline-code comparison finds only 23 user-facing status-string translations; all other inline-code identifiers, schema keys, source paths, example records, timestamps, and relationship statements are unchanged.
- Targeted residual Indonesian-prose scan returned no matches; deliberately retained machine keys and source basenames remain language-independent compatibility references.

## Outcome and limits

Source-to-English completeness and structural/mathematical parity pass. No unresolved translation issue was found. No build, Git command, network access, upstream contact, or publication was performed by this unit worker. Rendering, cross-unit links, language-wide terminology integration, and publication are assigned to the main edition process.
