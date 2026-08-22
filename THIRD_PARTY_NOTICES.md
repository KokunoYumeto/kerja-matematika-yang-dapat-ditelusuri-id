# Third-party notices for the offline HTML reader

The files below are generated or copied by Quarto 1.9.37 into
`build/html/site_libs/`. They are not original O017 software. Version authority
is the official Quarto v1.9.37 configuration and the version banners in the
distributed files.

| Component | Version | Bundled paths | License and copyright notice | Official source |
|---|---:|---|---|---|
| Quarto browser runtime | 1.9.37 | `quarto-html/quarto.js`, `quarto-html/tabsets/tabsets.js`, `quarto-nav/quarto-nav.js`, `quarto-search/quarto-search.js`, Quarto-generated syntax/theme support | MIT; Copyright © 2020–2024 Posit Software, PBC | <https://github.com/quarto-dev/quarto-cli/tree/v1.9.37> |
| Bootstrap | 5.3.1 | `bootstrap/bootstrap-*.min.css`, `bootstrap/bootstrap.min.js` | MIT; Copyright © 2011–2023 The Bootstrap Authors | <https://github.com/twbs/bootstrap/tree/v5.3.1> |
| Bootstrap Icons | 1.13.1 | `bootstrap/bootstrap-icons.css`, `bootstrap/bootstrap-icons.woff` | MIT; Copyright © 2019–2024 The Bootstrap Authors | <https://github.com/twbs/icons/tree/v1.13.1> |
| clipboard.js | 2.0.11 | `clipboard/clipboard.min.js` | MIT; Copyright © Zeno Rocha | <https://github.com/zenorocha/clipboard.js/tree/v2.0.11> |
| AnchorJS | 5.0.0 | `quarto-html/anchor.min.js` | MIT; Copyright © 2023 Bryan Braun | <https://github.com/bryanbraun/anchorjs/tree/5.0.0> |
| Popper | 2.11.7 | `quarto-html/popper.min.js` | MIT; Copyright © 2019 Federico Zivolo | <https://github.com/popperjs/popper-core/tree/v2.11.7> |
| Tippy.js | 6.3.7 | `quarto-html/tippy.umd.min.js`, `quarto-html/tippy.css` | MIT; Copyright © 2017–present atomiks | <https://github.com/atomiks/tippyjs/tree/v6.3.7> |
| Headroom.js | 0.12.0 | `quarto-nav/headroom.min.js` | MIT; Copyright © 2020 Nick Williams | <https://github.com/WickyNilliams/headroom.js/tree/v0.12.0> |
| Algolia Autocomplete | 1.19.1 | `quarto-search/autocomplete.umd.js` | MIT; Copyright © 2015–present Algolia, Inc. | <https://github.com/algolia/autocomplete/tree/v1.19.1> |
| Preact | 10.13.2 | Bundled into `quarto-search/autocomplete.umd.js` | MIT; Copyright (c) 2015-present Jason Miller | <https://github.com/preactjs/preact/tree/10.13.2> |
| HTM | 3.1.1 | Bundled into `quarto-search/autocomplete.umd.js` | Apache License 2.0 | <https://github.com/developit/htm/tree/3.1.1> |
| Fuse.js | 6.6.2 | `quarto-search/fuse.min.js` | Apache License 2.0; applied source-license notice: Copyright 2017 Kirollos Risk; bundled v6.6.2 banner: Copyright © 2022 Kiro Risk | <https://github.com/krisk/Fuse/tree/v6.6.2> |

The complete MIT permission and warranty text applicable to the MIT components
is in `licenses/MIT.txt`. The complete Apache License 2.0 text applicable to
HTM and Fuse.js is in `licenses/APACHE-2.0.txt`. Preserve this notice and both
license files with every redistributed HTML bundle.

The official Quarto 1.9.37 dependency declaration fixes AnchorJS 5.0.0, Popper
2.11.7, clipboard.js 2.0.11, Tippy.js 6.3.7, Autocomplete 1.19.1, and Fuse.js
6.6.2. The exact bundled file SHA-256 values are recorded by the release
manifest; this notice does not substitute a different upstream version.

## Embedded PDF fonts

The fixed-layout PDF contains embedded subsets of these font programs; they
remain under their component licenses and are not covered by the reader's
CC BY-SA grant.

| Component | Version | PDF use | License / notice | Official source |
|---|---:|---|---|---|
| Latin Modern text | 2.004 | 12 embedded subset objects | GUST Font License 1.0; Copyright 2003, 2009 B. Jackowski and J. M. Nowacki (on behalf of TeX users groups); `licenses/GUST-FONT-LICENSE-1.0.txt` | <https://ctan.org/pkg/lm> |
| Latin Modern Math | 1.959 | 1 embedded subset object | GUST Font License 1.0; Copyright 2012–2014 B. Jackowski, P. Strzelczyk, and P. Pianowski (on behalf of TeX Users Groups); `licenses/LATIN-MODERN-MATH-1.959-README.txt` and `licenses/GUST-FONT-LICENSE-1.0.txt` | <https://ctan.org/pkg/lm-math> |
| Font Awesome 5 Free Solid font | 5.15.4 | 1 embedded subset object | SIL OFL 1.1 for the font; Copyright © Font Awesome; `licenses/FONT-AWESOME-FREE-5.15.4-LICENSE.txt` and `licenses/SIL-OFL-1.1.txt` | <https://github.com/FortAwesome/Font-Awesome/tree/5.15.4> |
| AMSFonts MSAM10 Type 1 | 003.002 (AMSFonts 3.04) | 1 embedded subset object | SIL OFL 1.1; Copyright © 1997, 2009 American Mathematical Society; Reserved Font Name `msam10`; `licenses/AMSFonts-3.04-README.txt` and `licenses/AMSFonts-3.04-OFL.txt` | <https://ctan.org/pkg/amsfonts> |

The PDF carries font subsets, not standalone upstream source-font packages.
Preserve the notices above and `licenses/FONT_COMPONENT_PROVENANCE.json` when
redistributing it. Embedding/subsetting does not relicense any font.
