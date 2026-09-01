# O017-WRAP-CAL-A04 — Real-source erratum dossier calibration

Status: `calibration_only`  
Learner credit: `false`  
New discovery claimed: `false`  
Independent human checker: `false`  
External contact or transmission: `false`

This dossier audits an already published correction; it does not report a new
error. Its real source is G. H. Hardy, “Addenda and Corrigenda”,
*Proceedings of the London Mathematical Society* (1928), DOI
<https://doi.org/10.1112/plms/s2-28.1.553-t>. The publisher's page states that
two iterated-integral values previously printed as `1` and `-1` should be
`1/2` and `-1/2`.

## Object freeze

| Field | Value |
|---|---|
| source_id | `O017-WRAP-SRC-HARDY-1928-CORRECTION` |
| type | official publisher correction |
| title | “Addenda and Corrigenda” |
| author | G. H. Hardy |
| year | 1928 |
| DOI | `10.1112/plms/s2-28.1.553-t` |
| locator | note “Note on the inversion of a repeated integral” on the correction page |
| audited state | the old pair of values `1`, `-1` as referenced by the correction |
| official comparator | the corrected pair of values `1/2`, `-1/2` |
| scenario access date | 2026-08-22 |
| basis for use here | bibliographic facts, mathematical formulas, and original analysis; no publisher layout or prose copied |

The DOI identifies the correction's version of record. The dossier does not
have a hashed copy of the old printing and therefore does not claim to have
independently inspected the entire original page.

## Statement and classification

For

```text
g(x,y) = (x-y)/(x+y)^3,
```

the two iterated integrals over the unit square are examined in different
orders.

| Field | Value |
|---|---|
| statement_status of the old values | `false_as_written` |
| principal defect_kind | `numerical_error` |
| mathematical consequence | the values of both iterated integrals are wrong by a factor of two in the referenced old note |
| severity | `S2_local_substantive` |
| confidence | `C3_high` for the calculation; `C2_moderate` for historical scope because the full old source was not audited |
| new discovery | no; the official correction has already published the result |

## First minimal reproducer: order `dy` then `dx`

For `x>0`, an antiderivative with respect to `y` is

```text
y/(x+y)^2,
```

because its derivative equals `(x-y)/(x+y)^3`. Hence

```text
integral y=0..1 g(x,y) dy = 1/(x+1)^2.
```

The outer integration gives

```text
integral x=0..1 1/(x+1)^2 dx
= [-1/(x+1)] from 0 to 1
= 1/2.
```

## Second minimal reproducer: order `dx` then `dy`

For `y>0`, an antiderivative with respect to `x` is

```text
-x/(x+y)^2,
```

so

```text
integral x=0..1 g(x,y) dx = -1/(y+1)^2.
```

The outer integration gives

```text
integral y=0..1 -1/(y+1)^2 dy
= [1/(y+1)] from 0 to 1
= -1/2.
```

Both values match the official correction.

## Diagnosis and minimal correction

The minimal correction to the referenced values is:

```text
1     ->  1/2
-1    -> -1/2
```

The dossier proposes no change to the integrand, domain, or order of
integration. It also does not claim that antisymmetry gives zero, because the
absolute integral diverges at the corner `(0,0)` and exchanging the order is
not legitimate without additional hypotheses.

## Independent check within the calibration

The persona `O017-WRAP-EVAL-CAL-CHECKER` follows a second calculation route
in the scenario:

1. differentiate both antiderivatives directly;
2. evaluate at bounds `0` and `1`;
3. use the exchange transformation `x<->y` only to check that the signs of the
   two orders must be opposite, not to determine their values; and
4. confirm the pair `1/2`, `-1/2`.

Scenario outcome: `agrees_with_dossier`. However, the persona's `human_status`
is `synthetic_persona`, so this is **not an independent human check** and does
not satisfy G04. In an authentic submission, a second checker must repeat the
calculation, sign off on the scope, and retain evidence using an opaque ID.

## Impact audit and uncertainty

| Question | Evidence | Status |
|---|---|---|
| Is the old pair of values correct? | elementary calculation and official correction | closed: no |
| Is the new pair correct? | two antiderivatives and evaluation at the bounds | closed: yes within the scope of iterated integrals |
| Can the order be exchanged? | absolute integrability fails near zero | closed: not via the usual Fubini/Tonelli route |
| Which parts of the old work use those values? | no full audit of the old printing in this package | open |
| Is this a new discovery? | the official 1928 correction already exists | closed: no |
| Is publisher contact needed? | the correction is already published; no marginal value has been demonstrated | no; prohibited by the no-contact boundary |

## Local correction draft, not sent

> For the iterated integral with integrand `(x-y)/(x+y)^3` over the unit
> square, integration with respect to `y` then `x` gives `1/2`, whereas the
> reverse order gives `-1/2`. The respective inner antiderivatives are
> `y/(x+y)^2` and `-x/(x+y)^2`. This reproduces Hardy's official correction
> (1928), DOI `10.1112/plms/s2-28.1.553-t`; it is not a new finding and does
> not require a report outside this calibration package.

## Gate check

The example demonstrates the fields of G01, G05, G08, and G09. G04 remains
unassessed because the checker is a synthetic persona. The example's highest
status is `calibration_only`, not `passed` and not `ready_for_submission`.
