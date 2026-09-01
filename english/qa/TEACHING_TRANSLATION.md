# English teaching-material translation and validation

Course: *Traceable Mathematical Work* — O017/D120. Language: `en`.
Translation date: 2026-08-31. Status: complete within the bounded teaching
scope below. The Indonesian edition has not been changed.

## Scope and inventory

The original Indonesian teaching companion was translated in full, without
abridging the five assessment families or their calibration dossiers:

- `source/wrapper/index.qmd`: complete delivery and assessment wrapper,
  retaining the nine-unit narrative boundary, all nine noncompensable gates,
  privacy and accessibility requirements, local/community pathway distinction,
  outcome labels, machine-package instructions, and source citations.
- `delivery/README.md`: existing English documentation reused and localized
  to this English package, with validation instructions and scope limitations.
- `delivery/definitions/o017-delivery-definitions.json`: all human-readable
  labels and pass conditions translated; machine keys and policies preserved.
- `delivery/definitions/rubric-criteria.csv`: all 23 criteria translated.
- `delivery/definitions/evidence-types.csv`: all 32 evidence types translated.
- `delivery/definitions/lifecycle-statuses.csv`: all 22 lifecycle definitions
  translated.
- `delivery/schema/o017-delivery.schema.json`: existing English schema reused;
  its locale constant changes from `id-ID` to `en`, with no other semantic
  change.
- `delivery/calibration/01-real-source-search.md`: complete real-source search
  calibration.
- `delivery/calibration/02-seminar-supervised-equivalent.md`: complete seminar
  and supervised-equivalent calibration.
- `delivery/calibration/03-independent-referee-cycle.md`: complete synthetic
  author–referee cycle, including both manuscript versions and calculations.
- `delivery/calibration/04-real-source-erratum-dossier.md`: complete real-source
  erratum dossier and both minimal reproducers.
- `delivery/calibration/05-externally-reviewed-local.md`: complete local-review
  calibration and explicit weaker-credential distinction.
- `delivery/calibration/calibration-package.json`: human-readable fields
  translated; already-English authority and rights statements reused.
- `delivery/calibration/evidence-manifest.csv`: regenerated for the exact
  English dossier bytes.

The bounded validator is `delivery/validate_english_delivery.py`; its
machine-readable comparison result and exact 14-file byte/hash inventory are
in `delivery/validation-report.json`; standalone validation is recorded in
`delivery/validation-standalone-report.json`.

## Preservation decisions

Stable O017 IDs, schema keys, enum values, query strings, formulas, source
URLs, citations, and historical source-byte witnesses are preserved.
Legacy keys such as `label_id`, `notes_id`, `summary_id`, and `limitations_id`
remain unchanged for backend compatibility even where their values are
human-readable English rather than identifiers. Locale values are `en`.

No English Turing Way or PyRSE donor content was translated again in this
teaching scope. The original wrapper and calibration analysis are O017 prose;
existing English bibliographic and rights statements were reused directly.
The real sources behind calibration remain OpenStax, MIT OpenCourseWare,
and Hardy's official 1928 correction, with the original redistribution
boundaries and credits preserved. No source prose, video, image, or publisher
layout was added.

Historical timestamps in the calibration JSON and example ledgers are retained
as scenario or source-witness data, not re-labelled as new observations. This
translation performed no network retrieval or external contact.

Assessment rules requiring real people remain teaching content. They do not
delay construction, validation, or release of the edition. All calibration
people and events remain synthetic, every actual completion claim is false,
`credit_eligible` remains false, and no authorization or transmission is
claimed. The actual lifecycle remains `prepared`, not `submitted`.

## Validation performed

Run from the English-edition root:

```text
python delivery/validate_english_delivery.py --refresh-manifest --compare-indonesian <explicit-original-edition-root>
python delivery/validate_english_delivery.py
```

The first command regenerates the two derived English evidence inventories,
then compares the exact original files. The second validates the standalone
English package without requiring access to the Indonesian tree. The script
reads a fixed 14-file inventory and never scans recursively.

Checks cover UTF-8 decoding, nonempty files and headings, unique explicit
anchors, Draft 2020-12 JSON Schema including format checking, stable CSV
headers and row widths, all English locale fields, evidence/source/evaluator
reference closure, five exact dossier byte counts and SHA-256 hashes in both
inventories, and 11 synthetic/no-credit/no-transmission assertions.

Translation comparison confirms identical stable-ID sets, explicit anchors,
inline-code literals, source URLs, and heading counts for the full wrapper
and all five dossiers. Mathematical fenced-code blocks in A03 and A04 are
identical. The schema changes only its locale; definitions change only locale
and human-readable text; package JSON changes only locale, human-readable
text, and dossier bytes/hashes. Machine-bearing CSV columns are unchanged.

## Actual limitations retained, not disguised as completion

1. The inherited schema's exemplar and evidence definitions are
   calibration-specific. Although it has a `learner_submission` package kind,
   this demonstrator does not prove a complete authentic learner-submission
   workflow. No real learner pass or credential is claimed. A later authentic
   submission model requires its own schema work; it is not a prerequisite for
   publishing this complete teaching companion.
2. Source retrieval witnesses are those recorded by the Indonesian edition.
   They were preserved, not independently re-fetched during translation.
3. This validation is source/package validation, not PDF rendering,
   screen-reader testing, external-link availability testing, or a new proof
   audit. Those edition-level checks belong to the parent build/release work.
4. The erratum exercise deliberately leaves the full historical impact audit
   open and does not claim a new finding. Its synthetic checker is not an
   independent human checker.

No untranslated human-facing content remains in the assigned teaching scope.
No original Indonesian files or public access states were changed.
