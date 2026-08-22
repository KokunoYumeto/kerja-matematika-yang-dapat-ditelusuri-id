# O017/D120 authentic-delivery package

This directory is the machine-readable companion to the Indonesian wrapper at
`source/wrapper/index.qmd`. It does not alter the nine-unit narrative spine.

## Normative files

- `schema/o017-delivery.schema.json`: enforceable JSON Schema for calibration
  and learner-submission packages.
- `definitions/o017-delivery-definitions.json`: assessment families,
  noncompensable gates, privacy, accessibility, contact, and status policies.
- `definitions/rubric-criteria.csv`: criterion-to-gate mapping.
- `definitions/evidence-types.csv`: evidence vocabulary and verification rules.
- `definitions/lifecycle-statuses.csv`: assessment, community, and credential
  lifecycle definitions.

## Calibration files

`calibration/calibration-package.json` is a schema-valid, non-credit package.
Its five Markdown dossiers cover all assessment families. Every person and
event in those dossiers is synthetic; the cited mathematical sources are real.
The package makes no learner-completion or community-participation claim.

The default operational boundary is no contact and no transmission. A local
artifact may reach `prepared` without authorization. No external action may be
performed until a human grants authorization for one named target, artifact
version, channel, sender, data boundary, and validity period.

## Validation contract

Validate JSON against Draft 2020-12, parse every CSV as UTF-8 with unique
headers and stable row widths, verify every evidence byte count and SHA-256,
and check Markdown for UTF-8 decoding, nonempty headings, duplicate explicit
anchors, and forbidden completion claims. Calibration must always retain:

```text
package_kind = calibration_only
credit_eligible = false
synthetic_personas = true
authorization_present = false
transmission_performed = false
credential_label = calibration_only
```

