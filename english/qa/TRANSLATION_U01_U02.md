# English translation QA — Units 1 and 2

Date: 2026-08-31. Scope: the complete learner-facing Units O017-U01 and O017-U02
for the additive English edition, *Traceable Mathematical Work*. The Indonesian
files remain unchanged. This record covers text and structural QA only; the
main production task owns rendering, publication, and release readback.

## Exact inputs and outputs

Paths below are relative to the O017 lane root,
`outputs/01a0216a-4b9f-7d30-a376-60e4e3859979/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `source/units/01-membaca-argumen.qmd` | 11540 | `0d149ca6565236a18448a262493ee21d96d4010a4c8750a6a09bcf3de488d688` |
| `english-edition/source/units/01-membaca-argumen.qmd` | 11679 | `dd9691a8d74b5ec24ebd126e42cd994877ee917b6868fa3cc22bb723cdd07bcc` |
| `source/units/02-menelusuri-sumber.qmd` | 24219 | `7da45e3e3fb2c9c25e7dd10bdb5eb108846c1443dd3f3e66418e0c07bdb94d9a` |
| `english-edition/source/units/02-menelusuri-sumber.qmd` | 24416 | `a705bc1f4bb50d386574962ec82e32f819df5956906dc1ca0e5885a4334b6da9` |

Both exact Indonesian input files were read in full. Every section was
translated, including front matter, outcomes, prerequisites, prose, tables,
callout titles, accessibility labels, synthetic examples, proofs, exercises,
answer guidance, completion tasks, Unit 2's assessment rubric, boundaries,
provenance, licences, and donor credits. No section was summarised or omitted.

## Deterministic parity checks

Ordered token sequences were compared case-sensitively after normalising CRLF
to LF. Counts below are equal on both sides; every listed sequence matched
exactly, not merely as an unordered set.

| Check | Unit 1 | Unit 2 | Result |
|---|---:|---:|---|
| Explicit anchors | 30 | 47 | exact match |
| Inline/display mathematical expressions | 67 | 35 | exact match |
| Fenced code/output blocks | 1 | 0 | exact match |
| Citation groups | 3 | 4 | exact match |
| Markdown link targets | 1 | 5 | exact match |
| Inline code tokens, including paths and synthetic IDs | 1 | 34 | exact match |
| Exercise IDs | 6 | 6 | exact match |
| Guidance-answer IDs | 6 | 6 | exact match |

The Unit 1 expected computational output is unchanged: 720 distinct-weight
assignments, zero uniqueness violations, and three minimum spanning trees for
the equal-weight triangle. This check compares the expected-output block; it
does not claim a fresh execution of the program.

## Translation decisions and semantic review

- D/A/K/J/T, D1–D3, A1–A3, K1/K2, J1, T1–T4, exercise/guidance IDs, and all
  `PID-KELAS-...` simulation identifiers remain unchanged. Short explanatory
  sentences clarify that the Indonesian letter codes and synthetic identifiers
  are retained across editions.
- Technical terms include **minimum spanning tree**, **connected graph**,
  **symmetric difference**, **counterexample**, **proof obligation**,
  **provenance**, **source authority**, **absolute convergence**, **pointwise
  limit**, and **uniform limit**.
- Proof and empirical evidence remain explicitly distinct. The finite K4
  experiment is not promoted to a general proof. The source artifact's evidence
  about wording is not promoted to evidence that the mathematical claim is true.
- The minimum spanning tree proof preserves the choice of the minimum-weight
  edge over the entire symmetric difference, the cycle argument locating the
  exchanged edge, and the strict inequality obtained from distinct weights.
- Unit 2 preserves the alternating-series counterexample, the absolute-
  convergence comparison proof, and the complete pointwise/uniform-limit
  assessment with its epsilon/3 scaffold.
- Synthetic titles and dates are translated for readability; the underlying
  simulation identifiers, chronology, and factual/inferential distinctions are
  retained. No synthetic record is represented as a registered DOI.
- Unit 2's provenance wording explicitly identifies the connective text as
  original Indonesian material translated here. Original author/community
  credits, commit identities, exact donor paths, URLs, non-endorsement text,
  and the CC BY/CC BY-SA distinction remain intact.
- The task translated original O017 prose and its existing adapted exposition;
  it did not retranslate any already-English donor source or alter donor files.

No semantic correction or content reduction was required. No network,
upstream-contact, Git, build, or publication action was performed in this
bounded translation subtask. The next executable action is integration and
rendered-reader QA by the main production task.
