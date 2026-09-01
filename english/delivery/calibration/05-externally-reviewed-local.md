# O017-WRAP-CAL-A05 — `externally_reviewed_local` route calibration

Actual status: `calibration_only`  
Route demonstrated: `externally_reviewed_local`  
Actual transaction status: `prepared`  
Learner credit: `false`  
Transmission authorization: `false`  
Transmission performed: `false`  
Community participation claimed: `false`

This example deliberately chooses the weaker A05 route. It shows how a
real-source erratum package can be reviewed locally when sending it is
unauthorized or unsafe. All evaluators are synthetic personas; consequently,
even the label `externally_reviewed_local` is only a **demonstrated target
state**, not an actual outcome awarded to anyone.

## Local contribution package

| Field | Value |
|---|---|
| package_id | `O017-WRAP-CAL-A05-PACKET` |
| source | Hardy's official 1928 correction, DOI `10.1112/plms/s2-28.1.553-t` |
| principal artifact | `04-real-source-erratum-dossier.md` |
| contribution type | reproduction and concise explanation of an already published correction |
| external marginal value | not demonstrated; the official correction already exists |
| external target | not designated |
| outgoing message draft | not created |
| authorization_present | `false` |
| transmission_performed | `false` |
| current_state | `prepared` |

Because there is no target and the correction has already been published,
sending a new report would risk duplication. The package stays local. Stopping
is not a technical failure; it is the outcome of the target and marginal-value
gates.

## Rights, target, and privacy checks

1. The package retains metadata, mathematical formulas, and original analysis;
   it does not copy publisher layout or lengthy prose.
2. The DOI and official locators are preserved.
3. The package contains no evaluator names, email addresses, accounts, or
   personal data.
4. Evaluator IDs are opaque and are not derived from personal data.
5. The calibration package contains no identity mapping.
6. There is no external target, so authorization cannot be assumed to exist.

## Local review simulation

The synthetic reviewer `O017-WRAP-EVAL-CAL-LOCAL-REVIEWER` is given the
following scope:

- check the two antiderivatives and evaluations at the bounds;
- check that the “not a new finding” status agrees with the official correction;
- check that the package does not claim to have been sent;
- check the separation between the mathematical values and the historical
  impact audit; and
- check the text access alternatives.

### Synthetic report

| Comment ID | Locator | Finding | Target disposition | Example's actual status |
|---|---|---|---|---|
| `O017-WRAP-CAL-A05-LR01` | dossier §First minimal reproducer | the derivative of `y/(x+y)^2` is correct and the outer value is `1/2` | `accepted` | simulation only |
| `O017-WRAP-CAL-A05-LR02` | dossier §Second minimal reproducer | the derivative of `-x/(x+y)^2` is correct and the outer value is `-1/2` | `accepted` | simulation only |
| `O017-WRAP-CAL-A05-LR03` | dossier §Impact audit and uncertainty | the scope of historical use remains open and is not overstated | `accepted` | simulation only |
| `O017-WRAP-CAL-A05-LR04` | entire package | no-contact and no-transmission labels are consistent | `accepted` | simulation only |

Target recommendation: `externally_reviewed_local`. Because the reviewer is
not a verified human, the actual result remains `calibration_only`.

## Append-only status ledger

| Event ID | Scenario time | Status | External event | Evidence | Permitted meaning |
|---|---|---|---|---|---|
| `O017-WRAP-EVT-CAL-A05-01` | `2026-08-22T09:00:00+02:00` | `prepared` | `false` | local package and manifest | ready only for local inspection |

There are no `submitted`, `acknowledged`, `accepted`, `merged`, or `published`
events. Such rows may not be added as placeholders. If an external state is
later unknown after a real transaction, `unknown` is appended as a new event
while retaining the last state supported by evidence.

## Distinction between the two credentials

| Label | Minimum A05 evidence | Permitted claim |
|---|---|---|
| `complete_community_transaction` | specific authorization, transmission evidence, and a ledger that has reached at least `submitted` | one real contribution was sent; it was not automatically accepted |
| `complete_externally_reviewed_local` | an independent human reviewer assesses the real-source package locally; no transmission claim | an authentic package was reviewed outside the author role but remains local |
| `calibration_only` | a synthetic example such as this document | the form of the package is demonstrated; no credit or human event |

The second label is deliberately weaker than the first. Interfaces,
certificates, and data exports may not conceal the
`externally_reviewed_local` suffix.

## Access alternatives

The package can be reviewed without video or audio. All claims have headings,
tables, and text forms; formulas are written as plain LaTeX; status does not
depend on color. An authentic submission adds keyboard/screen-reader test
results and distinguishes tested from untested surfaces.

## Conditions for changing route in an authentic submission

A learner package may move to `community_transaction` only when a human
provides specific authorization covering the target, artifact and version,
channel, accountable sender, personal-data boundaries, and validity period.
After that, transmission must still be performed by the authorized actor and
evidenced. Authorization without a receipt is insufficient for `submitted`;
a receipt without authorization violates G07.

## Gate check

The example demonstrates G05, G07, G08, and G09 and the form of G04. G04 does
not pass authentically because the reviewer persona is not a verified human.
No status route may turn `calibration_only` into a passing outcome.
