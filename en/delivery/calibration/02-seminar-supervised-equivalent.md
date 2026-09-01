# O017-WRAP-CAL-A02 — Seminar/supervised-equivalent calibration

Status: `calibration_only`  
Route demonstrated: `supervised_equivalent`  
Learner credit: `false`  
Actual seminar attendance claimed: `false`  
External contact or transmission: `false`

This is a structured synthetic rehearsal, not a recording of Lecture 22, not
evidence that anyone watched it, and not an endorsement by MIT. The
mathematical content is originally composed using the official MIT OCW
18.100A Lecture 22 and OpenStax §5.3 pages as real sources. The timestamps
below refer only to the 24-minute synthetic practice transcript.

## Calibration session identity

| Field | Value |
|---|---|
| ID | `O017-WRAP-CAL-A02-SESSION` |
| type | synthetic supervised-equivalent rehearsal |
| scenario date | `2026-08-22` |
| duration | `00:24:00` |
| real sources | MIT OCW 18.100A Lecture 22; OpenStax *Calculus Volume 1* §5.3 |
| synthetic participant | `O017-WRAP-EVAL-CAL-LEARNER` |
| synthetic supervisor | `O017-WRAP-EVAL-CAL-SUPERVISOR` |
| actual human evidence | none |
| effect on credit | none; G03 and G04 are not authentically assessed |

## Timestamped notes from the synthetic transcript

| Time | Type | Note | Basis and locator | Status after checking |
|---|---|---|---|---|
| `00:00–02:30` | scope | The session will distinguish the statement of FTC Part 1 from integral evaluation in Part 2. | OpenStax §5.3, the two theorem boxes; MIT Lecture 22, official description | observed in the synthetic script; matches both locators |
| `02:30–06:00` | dependency | Continuity is used so that the local average of the function approaches its value at the point. | OpenStax, proof of Part 1; dependence on the mean value theorem for integrals | supported within the source's presentation |
| `06:00–10:30` | claim | If `F(x)=∫_a^x f(t)dt` and `f` is continuous, then `F'(x)=f(x)` in the interior of the interval. | OpenStax §5.3, FTC Part 1 | supported; notation rewritten, not quoted |
| `10:30–14:30` | proof step | The difference quotient of `F` becomes the average of `f` over a shrinking interval. | original calculation following the proof structure in the source | supported; the interval's orientation for `h<0` needs to be stated carefully |
| `14:30–18:00` | question | Is continuity necessary, or does a weaker almost-everywhere condition suffice? | synthetic participant's question | open; outside the frozen elementary theorem |
| `18:00–21:30` | claim | For an antiderivative `F`, the definite integral can be evaluated as `F(b)-F(a)`. | OpenStax §5.3, FTC Part 2 | supported under the source's hypotheses |
| `21:30–24:00` | boundary | The session does not prove the Lebesgue form, historical priority, or minimal conditions. | boundary established before the session | retained as out-of-scope matters |

## Dependency map

```text
continuity of f on [a,b]
        |
        v
Riemann integrability + mean value theorem for integrals
        |
        v
average of f over a shrinking interval -> f(x)
        |
        v
F'(x)=f(x) for F(x)=integral from a to x
        |
        v
evaluation of the integral using an antiderivative
```

The last arrow uses the additional fact that two antiderivatives differ by a
constant on an interval. The rehearsal records this dependency so that the
conclusion does not appear to follow directly from the definition of the
integral.

## Question and disposition log

| ID | Question | Action | Evidence/locator | Status |
|---|---|---|---|---|
| `O017-WRAP-CAL-A02-Q01` | How does the difference quotient work for `h<0`? | write the oriented integral and check the sign | original calculation; definition of the oriented integral | `verified_after_session` |
| `O017-WRAP-CAL-A02-Q02` | Is continuity the weakest condition? | do not extend the claim; record it as a further question | the frozen source states only the continuous case | `open_out_of_scope` |
| `O017-WRAP-CAL-A02-Q03` | Why does the choice of antiderivative not affect the value? | add that the constants cancel | OpenStax §5.3, explanation following the evaluation example | `verified_after_session` |

## Corrected final note

The synthetic initial version said, “FTC guarantees that every integrable
function has an antiderivative.” The final note narrows it:

> In the form examined in OpenStax §5.3, a function continuous on an interval
> gives rise to an integral function `F(x)=∫_a^x f(t)dt` whose derivative equals
> `f` in the interior of the interval.

The change prevents one elementary theorem from being applied to a class of
functions not covered by the source.

## Supervision evidence and its limits

In an authentic submission, a human supervisor would attest to the session
ID, assigned segment, learner's independent work, inspection time, and result
using an opaque ID. This example supplies only the form of the record:

```yaml
attestation_id: O017-WRAP-CAL-A02-ATT-SYNTHETIC
supervisor_id: O017-WRAP-EVAL-CAL-SUPERVISOR
human_status: synthetic_persona
work_observed: false
credit_effect: none
```

Because `human_status` is not `verified_human`, these data may not be changed
to `pass`.

## Equivalent access alternatives

The audio-free route uses:

1. the Lecture 22 description page and official lecture notes as text locators;
2. the synthetic practice transcript with headings and segments;
3. formulas as copyable LaTeX text;
4. a dependency map in a text list as well as a monospace diagram; and
5. a written question log that does not require speaking live.

An authentic supervisor must test the files using keyboard navigation and an
available screen reader, then state what remains untested. Providing only a
PDF or a video is not an access alternative.

## Gate check

The example demonstrates all the elements of G03, G08, and G09, but does not
satisfy the authentic gates because the session and supervisor are synthetic.
Its status remains `calibration_only`; it may not be described as an attended
seminar or a completed supervised equivalent.
