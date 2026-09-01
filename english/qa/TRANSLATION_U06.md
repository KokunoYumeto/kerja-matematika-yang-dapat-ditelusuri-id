# O017-U06 English translation QA

Date: 2026-08-31. Scope: complete English translation of Unit 6 for the additive English edition of *Traceable Mathematical Work*. The Indonesian edition and source were not changed.

## Exact inputs and output

- Source: `source/units/06-komputasi-dapat-direproduksi.qmd`, 43,409 bytes; SHA-256 `56715993b49ffb98cab9b4bf4a5bff85be040f1a85ba2484b83e536f81c09f0e`.
- English output: `english-edition/source/units/06-komputasi-dapat-direproduksi.qmd`, 44,127 bytes; SHA-256 `2314edfc4f037f90061c3b4ca93d08e99a2c217c4ee9b6afa372cd190281f6b2`.
- Source was read in full, in three bounded chunks after an initial truncated read. The source hash was recomputed after translation and remained unchanged.

## Completeness and invariants

All prose, headings, callout titles, accessibility labels, tables, claim levels, protocols, worked cases, exercise prompts, guidance answers, the completion task, the rubric, and provenance/rights text were translated without abridgment. English language configuration and course title are inherited from the edition-level build configuration.

Deterministic ordered comparisons between source and English output passed for:

| Invariant | Source | English | Result |
|---|---:|---:|---|
| Explicit anchors | 50 | 50 | Exact ordered match |
| Stable O017-U06 identifier occurrences | 85 | 85 | Exact ordered match |
| Inline/display mathematical expressions | 59 | 59 | Exact ordered match |
| Fenced literal-output blocks | 1 | 1 | Exact content match after CRLF/LF normalization |
| Markdown link targets | 13 | 13 | Exact ordered match |
| Citation keys | 4 | 4 | Exact ordered match |
| SHA-256 literals | 6 | 6 | Exact ordered match |
| Heading markers | 34 | 34 | Same ordered hierarchy |
| Table rows | 82 | 82 | Same count |
| Fenced div/callout markers | 34 | 34 | Same count |

Additional presence checks: all six exercise anchors, all six guidance anchors, all twelve checklist items, and all twelve accessibility labels are present. A bounded residual-language search found no occurrences of the selected Indonesian heading/common-prose terms. The preserved Indonesian source basename is intentional for stable crosslinks.

## Mathematical and evidential distinctions

- `RUN`, `REPEAT`, `IMPL`, `FINITE`, and `UNIVERSAL` remain distinct. Repeatability of a particular trajectory is not presented as validation of a distribution, an implementation, or a universal theorem.
- Exact finite checking on `1..24`, implementation validity, and the separate inductive proof of Cassini's identity retain their original limits.
- The recurrence, initial conditions, every line of the proof, the prime-polynomial counterexample, numerical thresholds, literal outputs, and hashes were preserved. Decimal/thousands punctuation in prose was localized to English without changing values.
- The 2026-08-21 run records remain explicitly historical observations. No new execution, replication, environment observation, or build was claimed or performed in this translation task.
- The English literal-output block was reused verbatim. The already-English donor material was not translated again; the unit's original Indonesian contextual adaptation was translated. Its provenance now explicitly identifies that relationship.
- Donor authors, frozen commits/trees, source-closure counts, citation keys, component rights, and non-endorsement were retained. Unit prose stays CC BY-SA 4.0; the linked witness code remains MIT and its expected-output data remains CC0.

## Two narrow source-language clarifications

1. Guidance H01 says `audit bunyi`, whose literal word choice is inappropriate for checker logic. The English text uses an audit of checker B's **soundness and independence**, preserving the mathematically intended requirement.
2. In the audit matrix, the missing-record mutation is expected to be rejected. The source's next cell says that if it passes, the checker `gagal tertutup terhadap kehilangan kasus`, a wording inconsistent with the earlier explicit fail-closed rule. The English reads **the checker fails to reject missing cases**. This is the direct logical consequence of the stated test; no claim, test, or mathematical content was changed.

No other source issues required a change. No builds, Git commands, network access, upstream contact, or publication were performed. Edition-level rendering, copied-code link resolution, and integrated build QA remain the parent integration task.
