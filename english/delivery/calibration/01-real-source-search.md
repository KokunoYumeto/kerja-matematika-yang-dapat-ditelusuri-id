# O017-WRAP-CAL-A01 — Real-source search calibration

Status: `calibration_only`  
Learner credit: `false`  
Actual learner search event: `false`  
External contact or transmission: `false`

This document is a synthetic worked example. The queries, times, and decisions
below show what a complete ledger looks like; they are not claimed to be the
activities of a learner. The sources compared are real and come from official
publisher or institutional pages.

## Question before the search

`O017-WRAP-CAL-A01-Q`:

> Which open primary sources provide a statement and proof context for the
> Fundamental Theorem of Calculus precise enough to compare the continuity
> hypotheses, version locators, and modes of presentation?

Boundary: sources must be papers, monographs, or official lecture notes;
aggregator pages and encyclopedic summaries may help locate candidates but
may not serve as the source for final claims. There is no language restriction.
No list of titles is supplied in advance to the calibration participant.

## Stopping rule frozen in advance

The search stops after all the following conditions have been met:

1. at least one official monograph and one official teaching source from
   different institutions have been found;
2. each source has a precise locator for the relevant statement or lecture;
3. the publisher or institution states the basis for access and rights;
4. the hypotheses can be compared without copying lengthy prose; and
5. one additional query pass reveals no material version conflict.

If condition 2 or 3 fails, the search may not stop merely because the
mathematical content appears suitable.

## Synthetic query ledger

| ID | Synthetic calibration time | Service | Query | Retained result | Reason |
|---|---|---|---|---|---|
| `O017-WRAP-CAL-A01-QL01` | `2026-08-22T08:00:00+02:00` | general search engine | `site:openstax.org calculus fundamental theorem calculus` | OpenStax §5.3 page | publisher domain; section locator and theorem numbers available |
| `O017-WRAP-CAL-A01-QL02` | `2026-08-22T08:04:00+02:00` | general search engine | `site:ocw.mit.edu 18.100A fundamental theorem calculus` | MIT OCW Lecture 22 | institutional page; lecture identity, instructor, semester, and materials available |
| `O017-WRAP-CAL-A01-QL03` | `2026-08-22T08:09:00+02:00` | domain-restricted search | `site:openstax.org/books/calculus-volume-1 "Fundamental Theorem" continuity` | OpenStax §5.3 and key equations page | additional pass confirms the locator; no edition conflict found on the web surfaces inspected |

The times in the table are part of the calibration scenario, not system
telemetry or evidence of any particular person's activity.

## Candidate and authority matrix

| Candidate | Type | Primary authority | Version/locator | Stated rights | Decision |
|---|---|---|---|---|---|
| OpenStax, *Calculus Volume 1*, §5.3 | monograph section | official OpenStax/Rice University page; authors Gilbert Strang and Edwin Herman | §5.3 page, Fundamental Theorem of Calculus Parts 1 and 2; web state accessed 2026-08-22 | introduction page states CC BY-NC-SA 4.0 for the current state | used as the principal monograph source; this package retains only citations and original analysis |
| MIT OCW 18.100A, Lecture 22, Fall 2020 | official lecture and notes | official MIT OpenCourseWare page; instructor Casey Rodriguez | Lecture 22, “Fundamental Theorem of Calculus, Integration by Parts, and Change of Variable Formula” | MIT OCW terms state CC BY-NC-SA 4.0, with exceptions for third-party components where marked | used to compare presentation and access routes |
| aggregator/encyclopedia results | secondary summaries | not the publisher of the work being assessed | changes without a version frozen in this example | varies | excluded as evidence for claims; may serve only as discovery tools |

## Source-freeze records

### O017-WRAP-SRC-OPENSTAX-FTC

- Title: *Calculus Volume 1*, §5.3, “The Fundamental Theorem of Calculus”.
- Authors: Gilbert Strang and Edwin “Jed” Herman.
- Publisher: OpenStax, Rice University.
- Authoritative URL:
  <https://openstax.org/books/calculus-volume-1/pages/5-3-the-fundamental-theorem-of-calculus>.
- Scenario access date: 2026-08-22.
- Claim locator: Fundamental Theorem of Calculus Part 1 and Part 2 in §5.3.
- Representation witness actually retrieved on 2026-08-22: HTTP 200,
  584,844 bytes, ETag `4253b01ceda870aaafd28b138d480603`, `Last-Modified`
  `2026-08-04T15:28:25Z`, SHA-256
  `f426a837c943b545698f9dc5f5918d8f1a0e901acb794cacb44383b59a3ea84a`.
  The web URL can still change; the digest freezes the bytes assessed but
  does not guarantee that those bytes will remain available at the URL.
- Rights: CC BY-NC-SA 4.0 stated in the web edition's introduction at the time
  of inspection.
- Redistribution of source content in this package: none; only metadata,
  locators, and short original paraphrases.

### O017-WRAP-SRC-MIT-FTC-LECTURE22

- Title: MIT OCW 18.100A Real Analysis, Lecture 22.
- Instructor: Casey Rodriguez; course term: Fall 2020.
- Authoritative URL:
  <https://ocw.mit.edu/courses/18-100a-real-analysis-fall-2020/resources/18100a-lecture-22-multicam/>.
- Scenario access date: 2026-08-22.
- Claim locator: Lecture 22 description and associated lecture notes.
- Page-representation witness actually retrieved on 2026-08-22: HTTP
  200, 49,617 bytes, ETag `5a2901baa2b34b376082baeb22d7f5b5`,
  `Last-Modified` `2026-08-18T18:10:52Z`, SHA-256
  `a9d4da8752e51471b94070b8ab1dbfed3ca35e79e527f2d97aa7bd3dae172261`.
- Rights: MIT OCW CC BY-NC-SA 4.0, with exceptions that may be stated for
  third-party components.
- Redistribution of source video, images, or notes: none.

## Claim comparison and decision

Both sources treat continuity as a central hypothesis for the form of the
Fundamental Theorem of Calculus they teach. OpenStax provides a direct,
easy-to-cite monograph locator. MIT OCW provides an analysis-lecture context
and an alternative route through notes and video. For written claims about
the theorem statement, OpenStax is selected as the principal source; MIT is
used to compare the dependency sequence and as an alternative access surface.

This decision does not claim that either source is the first historical proof
or a critical edition. Those questions lie outside the search boundary.

## Retained uncertainty

1. The OpenStax web page may be updated without a new URL; an access date alone
   is not a byte witness. An authentic package must archive a permitted
   representation or at least the hash of the bytes actually inspected.
2. MIT OCW's general license does not automatically cover every third-party
   component. This package therefore does not copy media.
3. The search does not investigate historical priority for the Fundamental
   Theorem of Calculus.
4. No full accessibility assessment of the source sites was performed; only
   the existence of more than one surface is recorded.

## Gate check

This example demonstrates all the fields of G01, G02, G08, and G09. Its actual
status nevertheless remains `calibration_only`: there is no learner, no human
evaluator, and no source artifact submitted for credit. Copying this dossier
and changing the name does not satisfy A01.
