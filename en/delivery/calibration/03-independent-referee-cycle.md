# O017-WRAP-CAL-A03 — Author–referee cycle calibration

Status: `calibration_only`  
Learner credit: `false`  
Two distinct humans: `false`  
External contact or transmission: `false`

Both role IDs below are synthetic personas. They demonstrate separation of
roles and artifacts, but do not satisfy the human-independence gate. The
mathematical manuscript is original and uses the integral mentioned in
G. H. Hardy's official 1928 correction as a real case.

## Identities and freezing

| Object | ID | State |
|---|---|---|
| synthetic author | `O017-WRAP-EVAL-CAL-AUTHOR` | `synthetic_persona` |
| synthetic referee | `O017-WRAP-EVAL-CAL-REFEREE` | `synthetic_persona` |
| initial manuscript | `O017-WRAP-CAL-A03-MS-V1` | frozen as text below |
| report | `O017-WRAP-CAL-A03-RR-V1` | assesses V1 only |
| response | `O017-WRAP-CAL-A03-AR-V1` | answers every comment |
| revision | `O017-WRAP-CAL-A03-MS-V2` | frozen as text below |

No authentic attestation that the people are distinct is available. The
calibration record states `distinct_humans = false` and `credit_effect = none`.

## Synthetic initial manuscript V1

> **Claim.** For
> `g(x,y)=(x-y)/(x+y)^3` on `(0,1]×(0,1]`, both iterated integrals equal
> zero. The reason is that exchanging `x` and `y` changes the sign of the
> integrand while leaving the unit square unchanged.

The manuscript does not prove absolute integrability and treats iterated
integrals like a double integral without a specified order.

## Synthetic referee report V1

Scope: validity of the claim, legitimacy of exchanging the order, and adequacy
of the proof. Style and historical priority are not assessed. Conflicts of
interest cannot be checked because the personas are not human.

### Major comment C1

- Locator: V1's sole proof paragraph.
- Claim assessed: antisymmetry forces both iterated integrals to equal zero.
- Diagnosis: that conclusion requires exchanging the order or having a
  suitably defined double integral. Near `(0,0)`, `|g|` is not integrable, so
  the step is unavailable without an additional argument.
- Reproducer: calculate the inner integral first with respect to `y` and then
  first with respect to `x`. The two give opposite values, not zero.
- Request: state the order of integration, calculate each inner integral, and
  remove the claim about a double integral without a specified order.
- Severity: major; V1's central claim is false.
- Confidence: high for the mathematical diagnosis; not a claim about the
  historical author's intent.

### Minor comment C2

- Locator: definition of the domain.
- Diagnosis: the singular point `(0,0)` is informally excluded, but the
  integration bounds still reach zero.
- Request: state that the inner integrals are understood as improper limits
  at an endpoint where necessary, and show the resulting limits.

Synthetic recommendation: `major_revision`.

## Synthetic author response

| Comment | Disposition | Action | Evidence and new location | Remaining issue |
|---|---|---|---|---|
| C1 | `accepted` | zero claim removed; both orders calculated separately | V2, the two elementary derivative calculations | no value is intentionally assigned to a double integral without a specified order |
| C2 | `accepted` | improper behavior at the corner stated | V2, paragraph following the formulas | general Fubini/Tonelli theory is out of scope |

The response does not say “fixed” before presenting V2.

## Synthetic revised manuscript V2

Define

```text
I_yx = integral x=0..1 [ integral y=0..1 (x-y)/(x+y)^3 dy ] dx,
I_xy = integral y=0..1 [ integral x=0..1 (x-y)/(x+y)^3 dx ] dy.
```

For `x>0`,

```text
d/dy [ y/(x+y)^2 ] = (x-y)/(x+y)^3.
```

The first inner integral therefore equals `1/(x+1)^2`, and then

```text
I_yx = integral_0^1 1/(x+1)^2 dx = 1/2.
```

For `y>0`,

```text
d/dx [ -x/(x+y)^2 ] = (x-y)/(x+y)^3.
```

The second inner integral therefore equals `-1/(y+1)^2`, so

```text
I_xy = integral_0^1 -1/(y+1)^2 dy = -1/2.
```

Endpoint values are obtained as limits from positive lower bounds. Thus the
two iterated integrals exist but differ. The manuscript assigns no value to
a double integral without a specified order.

To check the failure of absolute integrability, take the region
`0<y<x/2<1/2`. There, `|x-y|>=x/2` and `x+y<=3x/2`, so
`|g(x,y)| >= 4/(27x^2)`. Integrating with respect to `y` over an interval of
length `x/2` gives a lower bound proportional to `1/x`; the integral with
respect to `x` diverges at zero.

## Before/after evidence

| Element | V1 | V2 |
|---|---|---|
| value claim | both orders give zero | order `dy dx` gives `1/2`; order `dx dy` gives `-1/2` |
| basis | antisymmetry without a gate check | explicit antiderivatives and endpoint limits |
| exchange of order | performed silently | not performed; failure of absolute integrability proved |
| double-integral status | assumed to exist | deliberately not claimed |

## Issues that remain open

1. The example does not discuss two-dimensional Cauchy principal values or
   other regularization schemes.
2. The example does not assess all the historical consequences of the
   numerical error.
3. Synthetic personas do not satisfy human independence; an authentic cycle
   must be repeated by two distinct humans with new artifacts and hashes.

## Gate check

The V1–report–response–disposition–V2 chain is complete and demonstrates G05,
G06, G08, and G09. G04 intentionally does not pass authentically. Replacing
`synthetic_persona` with `verified_human` without a real attestation is
falsification of evidence.
