# Immutable rebuild environment

This directory closes the clean-environment gap for the O017/D120 reader. The
container authority is the manifest digest in `OCI_IMAGE_LOCK.json`, not a
mutable tag. It combines the official Quarto full image at Quarto 1.9.37 and
its digest-frozen TinyTeX installation with a SHA-256-pinned portable CPython
3.13.9 and a hash-locked pypdf 6.12.2 wheel.

## Build the image

Run from the edition root on an x86-64 machine with Docker or Podman:

```sh
docker build --pull=false --file environment/Containerfile \
  --tag o017-rebuild:2026.08.22.1 .
```

The build fails unless the exact base image, Python archive, Python wheel,
Quarto version, XeLaTeX engine, required LaTeX packages, and four font
components are present. Network access is needed only while constructing the
image from the three immutable upstream artifacts.

## Rebuild and verify offline

After the image exists, run the complete content build with networking disabled:

```sh
docker run --rm --network none \
  --volume "$PWD:/work:ro" \
  o017-rebuild:2026.08.22.1 \
  bash /work/environment/rebuild_and_verify.sh /work
```

The script copies only `source/` into a fresh temporary directory, executes and
compares both mathematical witnesses, renders the nine-unit semantic HTML
reader plus the separately identified delivery wrapper, renders the XeLaTeX
PDF without losing any of the preserved 128-page edition, checks Indonesian
language markers and native MathML, opens every PDF page with pypdf, and removes
the temporary stage. It does not write to the mounted edition tree.

The container proves reproducibility of content and structure, not byte-for-byte
identity across operating systems or TeX engines. The published PDF was made
with MiKTeX 26.5; the immutable image uses the TinyTeX bytes already contained
in the pinned official Quarto image. Consequently font subset names, timestamps,
compression, and the final PDF hash may differ while page count, text, links,
mathematics, and visual content remain equivalent.

## Authority and scope

- Official Quarto container package: <https://github.com/quarto-dev/quarto-cli/pkgs/container/quarto-full>
- Python standalone project and portability guidance: <https://github.com/astral-sh/python-build-standalone>
- Python package distribution record: <https://pypi.org/project/pypdf/6.12.2/>

Browser automation is intentionally outside this minimal rebuild closure. The
image rebuilds HTML/PDF and runs the mathematical/structural checks required by
the handoff; historical Playwright screenshots remain separate release evidence.
