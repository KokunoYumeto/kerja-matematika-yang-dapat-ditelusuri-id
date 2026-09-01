# Unit 9 English translation QA

Date: 2026-08-31. Status: complete source translation; deterministic source
parity passed. Rendering and release integration remain the parent lane's
work and are not claimed here.

## Scope and identities

Translated the entire original Indonesian Unit 9 into English for *Traceable
Mathematical Work*. No pre-existing English donor text occurs in this unit;
the source explicitly identifies all its pedagogical content as original O017
material. No donor was retranslated or newly imported.

- Source: `source/units/09-kontribusi-komunitas-portofolio.qmd`
- Source bytes: 44,755
- Source SHA-256: `ad914ff7c17775ca3a9d0724d07b35157fdb47237dc1749363ff152b32cd554e`
- English: `english-edition/source/units/09-kontribusi-komunitas-portofolio.qmd`
- English bytes: 45,502
- English SHA-256: `494577f6a5363c8bc006cca130ddb9433aa65768b2cac4fc2937f1977d35853b`
- Stable unit identifier: `O017-U09`
- Language is inherited from the English edition configuration, as assigned.

Paths are relative to the unchanged O017 source-edition root; the additive
English subtree is shown explicitly.

## Checks performed

The source was read completely in bounded line ranges. PowerShell regex
comparisons then checked exact ordered sequence parity between the actual
source and English files for the following items:

| Check | Source | English | Result |
|---|---:|---:|---|
| Explicit anchors | 49 | 49 | Exact ordered equality |
| Stable `O017-U09` ID occurrences | 35 | 35 | Exact ordered equality |
| Inline/display mathematical spans | 82 | 82 | Exact ordered equality, including deliberately false source equations |
| Markdown link targets | 17 | 17 | Exact ordered equality |
| Inline machine/status code spans | 4 | 4 | Exact ordered equality |
| Heading levels | 31 | 31 | Exact ordered equality |
| Markdown table lines | 100 | 100 | Count/structure parity |
| Colon-fence markers | 36 | 36 | Count/structure parity |
| Exercise anchors | 6 | 6 | All E01–E06 present |
| Guidance anchors | 6 | 6 | All H01–H06 present |

Additional checks:

- Every internal fragment link resolves to an anchor in the translated file.
- All 12 package-checklist items are retained.
- All 14 capstone requirements are retained.
- The eight-criterion rubric, 14/16 pass threshold, four mandatory maximum-score
  criteria, and revision-trigger exceptions are retained.
- The one outgoing example draft contains 84 whitespace-delimited words,
  including its title, below both the worked destination's 150-word limit and
  Exercise E05's 120-word limit. It remains explicitly unsent.
- There are no executable fenced code blocks, output snapshots, or embedded
  checksum strings in the source unit. No execution-equivalence claim is
  therefore required for this unit.
- The Indonesian source file's final hash matches its initial hash; it was
  not edited.

## Translation decisions and boundaries

All prose, headings, descriptions, callout titles, accessible table labels,
table content, synthetic target text, diagnoses, patch explanations, example
drafts, exercises, detailed answer guidance, capstone, and rubric were
translated without abridgment.

The code values `published=true`, `merged=unknown`, `diterbitkan`, and
`digabung` remain byte-identical. The last two now have explanatory English
glosses outside their code spans. The synthetic version label `1.2-sintetis`
also remains unchanged as an identifier, with a contextual English gloss.
Dates, source/destination IDs, mathematical expressions, links, the CC BY-SA
4.0 license, and O017 contributor attribution are preserved.

The provenance section explicitly distinguishes the original Indonesian
material from its English translation. It does not claim that a third-party
English book supplied this original unit.

The unit's worked case remains entirely synthetic. Prepared, submitted,
acknowledged, accepted, merged, and published remain separately evidenced
event predicates; no external event is inferred from another. The example
package stops at locally prepared status. The conditional sign-off is
translated into English and remains a conditional teaching example, not a
claim that anything was sent. No contact, issue, message, review, merge, or
publication was performed by this subtask.

No unresolved translation or mathematical-parity issue was found. No build,
network request, Git operation, source mutation, or publication was performed.
