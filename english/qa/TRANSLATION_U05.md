# O017-U05 English translation QA

Date: 2026-08-31. Scope: the full original O017 Unit 5, as an additive English
edition; the Indonesian source was read completely and not modified.

## Exact inputs and outputs

- Input: Indonesian source edition `source/units/05-eksposisi-matematika.qmd`
- Input bytes: 37,364.
- Input SHA-256: `ef5779b009bf1fe32b66af53ea64a89fd7eb51a240f7288bc4328c64d16a7006`.
- Output: English edition `source/units/05-eksposisi-matematika.qmd`
- Output bytes: 37,671.
- Output SHA-256: `9114bde359ec9030f96eb66ba4b49e94f018cc15664c4ff7a5dad3b9b3a6fee5`.
- Stable unit ID: `O017-U05`; basename and every stable anchor retained.
- Book language is inherited from the English edition configuration. No
  unit-level language override or Indonesian project setting was introduced.

## Coverage and parity

All learner-facing prose, front matter, headings, callout titles, table cells,
accessibility labels, worked cases, six exercises, their six complete guidance
answers, seven synthetic packet items, all eleven completion requirements,
rubric, boundaries, and component rights were translated without abridgment.

Deterministic source/English comparisons passed:

| Check | Indonesian | English | Result |
|---|---:|---:|---|
| Stable anchors | 57 | 57 | Identical sequence |
| Markdown link destinations | 13 | 13 | Identical sequence |
| Citation-key occurrences | 4 | 4 | Identical sequence |
| Backtick-delimited literals | 45 | 45 | Identical sequence |
| Inline/display math spans | 184 | 184 | Identical normalized sequence |
| Level-2/level-3 headings | 27 | 27 | Count and structural order retained |
| Fenced-div openings/closures | 18/18 | 18/18 | Balanced; structural attributes retained |
| Markdown table rows | 45 | 45 | Count and table order retained |
| Exercise IDs | 6 | 6 | E01–E06 retained |
| Guidance IDs | 6 | 6 | H01–H06 retained |
| Synthetic packet items | 7 | 7 | All DEF/LEM/EXM/CTR IDs retained |

The math comparison ignores whitespace and translates only the two textual
conjunctions `\text{ dan }` and `\text{dan}` to `\text{ and }` and
`\text{and}`. No mathematical symbol, value, domain, quantifier, inequality,
factorization, or formula structure changed. The exact factorization
`30031=59\cdot509`, geometric-sum identity, domain exclusion, polynomial
packet, and counterexamples retain their mathematical content.

All relative/local crosslinks, URLs, frozen commit identifiers, donor paths,
and citation keys are unchanged. There were no executable code blocks or
literal donor quotations to retranslate. The synthetic-packet label is
explicit and no fictional author, DOI, year, or page has been supplied.

## Translation decisions and one editorial repair

- Use “mathematical exposition,” “proof,” “evidence,” “assumptions,”
  “dependency,” “lemma,” “claim,” “notation,” and “counterexample” consistently.
- Render the contract field `Bukti masuk` as “Admitted results,” following its
  explicit definition as results that may be used without being proved again.
- Preserve the literal metadata sentinel `tidak diketahui` and add the
  learner-facing gloss “unknown”; this keeps literal parity without leaving
  its meaning unexplained to English readers.
- The source preflight question 7 asks whether unsupported nodes remain,
  although the following paragraph treats every “no” as a failing answer.
  The English version repairs only this question's polarity: “Does the
  dependency audit confirm that no unsupported nodes remain?” This aligns
  the checklist with its surrounding instruction and changes no mathematics
  or assessment requirement. The Indonesian file is untouched.
- The provenance paragraph now explicitly calls this a translation of the
  original Indonesian O017 material. CC BY-SA 4.0 for original material,
  CC BY 4.0 for the bounded Turing Way conceptual adaptation, donor credits,
  non-endorsement, and the statement that PyRSE is not adapted in this unit
  remain explicit. No already-English donor passage was translated again.

## Remaining validation boundary

Source-level translation and structural/math parity are complete. No build,
render, Git operation, network request, upstream contact, or publication was
performed in this subtask. Whole-book HTML/PDF rendering, internal-link
resolution, and final publication checks belong to the parent integration
step. No remaining Unit 5 translation blocker was found.
