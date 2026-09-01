# O017 English-access backend

This is an additive English localization of the original nine-unit O017/D120
course and its assessment backend. It neither replaces the Indonesian edition
nor claims that the original Indonesian artifacts have become English.

## Integration and language selection

Start with `languages.json`. For English, load
`semantic-wrapper-v1.records.en.jsonl` and join `localization_ids` to
`semantic-wrapper-v1.localizations.en.jsonl`. These contain all 319 semantic
entities and all 581 English localized fields, including learning outcomes,
competencies, assessment instructions, rubric criteria, evidence requirements,
submission/attempt/result templates, evaluator roles, and credential-state
labels. A missing language is an error, not permission to fall back silently.

`semantic-wrapper-v1.records.jsonl` is the bilingual view: each neutral entity
points to its retained Indonesian localization IDs and its new English IDs.
`semantic-wrapper-v1.localizations.jsonl` contains 581 untouched Indonesian rows
followed by 581 English rows. English uses BCP 47 `en`, without claiming a
particular regional variety. The locale-aware schema validates both languages
and rejects mismatched locale/language/ID combinations.

`localization-crosswalk.csv` pairs every Indonesian field with its English
equivalent through the same subject ID and field. `english-localization-relations.csv`
adds 581 English text relations without modifying any previously issued relation.
All 1,107 core relation IDs and all 1,704 semantic-wrapper relation IDs retain
their original triples and bytes in the two existing relation ledgers.

## Core reader entities and links

The original core `records.jsonl`, `schema.json`, `relations.csv`, and
`relations-ledger.csv` remain byte-identical. Their historical edition locales,
artifact hashes, and QA claims refer to the Indonesian release only. Do not use
those historical artifact hashes to validate the English reader.

For English names, join the 147 schema-validated rows in `core-localizations.en.jsonl` by
`subject_id` and `field`. These cover every existing core title, concept label,
and preferred term, either translated or explicitly reused from existing
English. The two term records distinguish empirical evidence from mathematical
proof. Their enforceable schema is `core-localizations.schema.json`.
`english-access-locators.jsonl` supplies 529 English source/HTML locators
for the same unit, segment, theorem, definition, proof, example, exercise, and
solution IDs. Paths are relative to the English edition root. Explicit fragment
names are retained from the Indonesian edition; a fragment is a locator, not a
canonical entity ID. English source filenames intentionally retain their
established names for stable links.

The English source begins at `source/index.qmd`, the rendered reader at
`build/html/index.html`. The release manifest, not the historical core artifact
rows, records the current English PDF/HTML bytes and hashes.

## Preservation, generation, and checks

`upstream-id-ID/` is a compact byte-for-byte snapshot of the eleven explicitly
listed original backend files. `upstream-id-ID.manifest.json` freezes its byte
counts and SHA-256 identities. It makes this package independently rebuildable
without requiring the original workspace. The generator never writes outside
the English edition. When the adjacent original backend exists, it additionally
verifies that it still matches the snapshot.

`translations-a.json`, `translations-b.json`, and `core-translations.json` are
the authored English translation inputs. Evidence fields that repeat a criterion
reuse the complete criterion translation; recurring template labels and
instructions expand through explicit rules. Nothing is abbreviated to a unit
title, and no English donor is translated again. Mathematics, status codes,
independence requirements, and educational authorization boundaries are retained.
These assessment requirements are course content, not operational instructions
to the production agent.

From the English edition root:

```text
python scripts/english_backend.py
python scripts/english_backend.py --check
```

Python 3.10+ and `jsonschema` are required. Generation validates the schema and
all semantic/localized records, checks ID parity and unchanged neutral fields,
resolves relation endpoints and source anchors, and emits a deterministic
`qa/ENGLISH_BACKEND_QA.json`. `--check` also proves byte-for-byte replay of every
generated backend view. `--allow-incomplete-sources` is a development-only option:
it labels missing anchors explicitly and must not be used to assert release
completion. Final rendered-page and PDF QA belong to the release workflow.

The backend contains definitions and templates only: no actual learner attempts,
results, community events, or credentials are asserted. Calibration remains
calibration. Original source, author, contributor, and component-rights identities
are retained; new English original prose follows the edition's original-text
license. Production provenance: OpenAI Codex gpt-5.6-sol, Ultra.
