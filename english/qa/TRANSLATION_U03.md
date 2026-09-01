# Unit 3 English translation QA

Date: 2026-08-31. Scope: full learner-facing translation for the additive English edition, *Traceable Mathematical Work*. The Indonesian source remains unchanged.

## Exact artifacts

- Source: `source/units/03-merekonstruksi-pembuktian.qmd` in the O017 lane; 36,624 bytes; SHA-256 `b4e3ed7fac5d9a18c1c90df6a0da1cc5d7f9c309c2fe701ab6996e902793e1bf`.
- English: `english-edition/source/units/03-merekonstruksi-pembuktian.qmd`; 36,634 bytes; SHA-256 `0e33728b16690e8cadfed384dde7eea4886d03af1a517f933504e7e7da3f84f6`.
- Stable unit: `O017-U03`. The original filename is retained for cross-edition path compatibility. English language is inherited from the edition configuration.

## Completeness and parity checks

The complete source was read. The English version retains the seven-stage protocol, reconstruction worksheet, full compact-image proof, dependency graph, lemma contracts, two-way planning, minimality audit, invalid-shortcut cases, both compactness/continuity counterexamples, complete Hausdorff lemma proof and Sierpiński counterexample, gap register, audit exercise, all six exercises and all six guidance answers, the nine-part completion task, six-criterion rubric and passing conditions, B80/unit boundaries, and complete provenance and licensing statements. Nothing was abridged.

PowerShell regex checks on the two exact files yielded:

| Check | Indonesian | English | Result |
|---|---:|---:|---|
| Explicit anchors | 50 | 50 | Exact ordered identity |
| Stable unit/exercise/guidance identifiers | 13 | 13 | Exact ordered identity |
| Level 2/3 headings | 36 | 36 | Structure retained |
| Div/callout fences | 26 | 26 | Structure retained |
| Table rows, including headers/separators | 52 | 52 | Structure retained |
| Exercise anchors | 6 | 6 | Exact ordered identity |
| Guidance anchors | 6 | 6 | Exact ordered identity |
| Mathematical spans | 340 | 340 | Exact symbolic multiset after removing whitespace and normalizing only prose inside `\text{...}` |
| Mathematical prose clauses | 7 | 7 | All seven translated; surrounding notation unchanged |
| Fenced `text` blocks | 4 | 4 | Prose/diagram labels translated; mathematical notation and working identifiers retained |
| URLs | 1 | 1 | Exact ordered identity |

No executable code, machine output, hashes, donor quotations, or source-relative links occur in this unit. Thus no executable-code transformation or donor retranslation was performed. The four fenced blocks contain a lemma-contract notation, a dependency diagram, and two planning diagrams, not programs. Labels `D1`, `D2`, `P1`–`P5`, `C1`, `L1`, `L2`, `G-H`, `G-C`, and the cross-unit `D–A–K–J–T` label are preserved. Human-readable gap statuses are translated to `closed`, `conditional`, `unconfirmed`, and `rejected`; these are prose labels, not changed packet identifiers.

A bounded residual-language search for the central Indonesian terms found no untranslated occurrences in the English unit. Mathematical terminology distinguishes proof from empirical evidence and consistently uses quantifier, domain, preimage, image, open cover, finite subcover, continuity, compactness, dependency graph, lemma contract, hypothesis, assumption, and counterexample. The term “elementwise proof” renders the source's arguments that explicitly choose an element and witness.

## Rights and remaining integration

The original O017 contributor credit and CC BY-SA 4.0 license link are retained. The unit explicitly states that it contains no Turing Way or PyRSE excerpts/adaptations; that statement is preserved. No original-source mathematical defect was identified during this translation.

Content and structural checks pass. This subtask did not render, build, contact external parties, run Git, or publish. Whole-edition rendering, link checks, accessibility checks, learner/teaching integration, and release verification belong to the parent edition workflow.
