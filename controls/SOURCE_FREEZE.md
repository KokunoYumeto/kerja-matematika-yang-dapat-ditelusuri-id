# Official-source freeze — O017/D120

Date: 2026-08-21  
State: `SOURCE_FROZEN`

The two works below are bounded methodological donors. Neither is the O017
spine, and Unit 1 copies no donor prose. Exact source bytes are retained under
`authority/`; full repositories were not checked out.

## The Turing Way

- Official repository: <https://github.com/the-turing-way/the-turing-way>
- Commit: `c98a0e6ca47450456cca7c5eedda2d5ee131d1ce`
- Tree: `94b81b26ea209b4b067456b9b6740c76fff1eac9`
- Selected content: 21 files, 2,128,347 bytes; manifest SHA-256
  `82a352d497ecdf372b1628b405ef83754f960b7ace239e1710e06e4eb6c9c133`.
- Scope: peer-review procedure; citation, metadata, and versioning; definitions
  of reproducibility; research compendia; open notebooks; bounded contribution
  etiquette. Five logical figures have alt text, but any reused
  `reproducible-matrix` figure needs a fuller Indonesian description.
- Rights: selected website content CC BY 4.0; infrastructure MIT where stated.
  Preserve The Turing Way Community, immutable commit, license/change notice,
  Scriberia figure credits, relevant DOIs, and the nested René Bekkers credit.
- Build evidence: MyST/Jupyter Book 2.1.6, Python 3.14, and 79 exact Python
  pins. Upstream defines HTML but no PDF/EPUB path. Its full build additionally
  fetches a pinned external plugin, so the repository alone is not an offline
  closure. The six retained build-evidence files total 83,435 bytes; manifest
  SHA-256 `a288e0bbdeb911941b42513693ac38965e73104a82b4b5f32956204d563dd9a4`.
- Learning closure: no formal exercises, hints, answers, or solutions. O017
  must author them.
- B80 exclusion: no Git/VCS, testing, CI, environments, containers, code
  quality, code documentation, or code-review instruction is imported.

The immutable full-archive observation is 167,935,841 bytes, SHA-256
`0aa12abcc930f63c402dc7fc070308808217da72d93d595d0f3d58fb0bb90446`.
The archive was independently opened and measured but is not retained because
the bounded commit-pinned closure is sufficient.

## Research Software Engineering with Python

- Official repository: <https://github.com/merely-useful/py-rse>
- Commit: `62217e6606842ab9752fcf8e73954d1eb4a3cf07`
- Tree: `f570f30bb8ace202550c474e81eb3414e8976be5`
- Selected witness: 8 files, 124,227 bytes; manifest SHA-256
  `003333798535f050c359f26ea0d5936dd6e43a722b32890b3079b90b2333870f`.
- Exact provenance slice: source lines 68–86, 201–230, 310–316, 335–356,
  and 362–417, concatenated in order with LF endings: 134 lines, 6,759 bytes,
  SHA-256 `7c9ce175f20db5f248e56018ecabc3c364ce46f15d7f1e20564c8547b0a95dbc`.
- Scope: DOI/ORCID; three-part computational provenance; per-result workflow
  documentation; archival of analysis scripts; reproducibility versus durable
  inspectability.
- Rights: prose CC BY 4.0; preserve its six authors, immutable commit, license
  link, and translation/adaptation notice. Preserve the MIT notice if code is
  copied. Quotes, screenshot, external-account exercises, and third-party
  adaptation surfaces are excluded.
- Build evidence: R Markdown/Bookdown with HTML and XeLaTeX targets, but
  dependency versions are unpinned, old CI is not a frozen-head witness, and
  the Makefile requires absent `CONDUCT.md`. The upstream head is therefore not
  reproducibly buildable as written and is not used as the O017 build base.
- Learning closure: the full book pairs 109 exercise/solution headings, but the
  selected chapter’s activities depend heavily on external services and some
  solutions are only completion criteria. O017 imports none verbatim.

The immutable full-archive observation is 20,728,265 bytes, SHA-256
`840b78f1f0d8e5520126a25a8152cd198fc867042df08827158bcb44cf482e56`;
it is not retained locally.

## Curriculum-spine adjudication

Verdict: **GO** for the original nine-unit Indonesian O017 spine with only the
exact frozen slices above as bounded donors. This judgment is independent of
how much production work is already complete.

- Full *The Turing Way* is not a viable replacement spine: it is strong on
  research practice and has clear CC BY 4.0 content rights, but it does not
  close formal mathematical reading, proof reconstruction, exposition,
  errata, or keyed self-study; its complete build is not an offline closure;
  and its Git/testing/CI/environment material would duplicate B80.
- The full 528-page *Research Software Engineering with Python* book is not a
  viable replacement spine: it is editable and strong on provenance, but it
  is primarily software engineering, substantially overlaps B80, leaves the
  mathematics-specific reading/proof curriculum open, has unpinned build
  dependencies, and its Makefile references absent `CONDUCT.md`.
- The earlier MIT 18.821-led composite is not presently admissible: the frozen
  evidence identifies only HTML/PDF/video surfaces, not an exact edition with
  editable-source closure, derivative-rights chain, immutable archive hash,
  and reproducible build. It may have pedagogical merit, but those missing
  gates prevent it from replacing the current spine.

Remaining bounded conditions are completion conditions rather than reasons to
switch corpora: every unit must retain keyed self-study support; component
rights and attribution must remain separate; any reused
`reproducible-matrix` figure needs fuller Indonesian description; and Git,
testing, CI, environments, APIs, and numerical-method instruction must remain
outside O017.

## Original bridge obligation

Neither donor adequately teaches mathematical literature search, theorem and
proof reading, reconstruction of omitted arguments, examples and
counterexamples, mathematical exposition, errata, experiment-versus-proof,
author response to review, or a generic bounded contribution. Those surfaces
remain original O017 work under the component policy in `LICENSES.md`.
