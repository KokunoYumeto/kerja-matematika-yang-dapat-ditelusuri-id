# O017 PDF font and tag audit

Artifact: `output/pdf/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.22.1.pdf`  
SHA-256: `bfac70f7efd2ce0a65fd0b2435ed817dee8186169f8f3a95b0fe526a0f46f2bf`  
Extent: 134 pages; every page inspected.

## Accessibility finding

**UNTAGGED.** The catalog declares `/Lang` as `id-ID`, but it has no
`/StructTreeRoot`, no `/MarkInfo` declaration, no page `/StructParents`, and no
marked-content sequence.
The PDF has bookmarks and extractable text on every page, but these do not create
a programmatic heading/table/list/reading-order structure. It must not be described
as an accessible PDF or as PDF/UA conforming. The semantic HTML reader remains the
accessibility-oriented surface.

This interpretation follows W3C's PDF accessibility techniques, which identify a
logical structure tree and tagged reading order as the core PDF accessibility
mechanism: <https://www.w3.org/TR/WCAG20-TECHS/pdf>.

## Font result

All 15 referenced font objects are embedded and subset.
14 have ToUnicode maps;
1 do not. The sole missing ToUnicode map is
the Font Awesome icon subset; that is an additional reason not to infer accessibility
from successful text extraction.

| PDF BaseFont | Type | Embedded | ToUnicode | Pages | Stream SHA-256 |
|---|---|---:|---:|---:|---|
| /CFMBFB+LMRoman9-Bold-Identity-H | /Type0 | yes | yes | 5 | `959ad029a9de531596969013659a6fc80206092842b8890597d5983e2e24d4c3` |
| /EGLSXS+LMMono10-Regular-Identity-H | /Type0 | yes | yes | 61 | `2fe0a0c37d6471369fead260c557f0846bb0f4a77a61ff8e49fbd3e793dc7fd1` |
| /FWPYUO+LMRoman10-Italic-Identity-H | /Type0 | yes | yes | 32 | `ddcfd5cade32df10754dbc93bfa7f82d6e7d86644cea999fbf796827b0837327` |
| /GCYTVB+LMSans10-Bold-Identity-H | /Type0 | yes | yes | 129 | `1d1855273a0ce5ace08b82860116d530f8188699c55a72fdd9f88a12b366cfcf` |
| /GMLBJW+LatinModernMath-Regular-Identity-H | /Type0 | yes | yes | 77 | `fb089ce9c48d7867434b37d595c1ca7eacceafdce4f3fa9786aba4d922bc7e2d` |
| /HTTFVG+FontAwesome5Free-Solid-Identity-H | /Type0 | yes | no | 46 | `70cabc36d1557973c5b843fcfb7bb97602d0a240e583b8c72d8b295c6f561023` |
| /IXWMJS+LMRoman12-Regular-Identity-H | /Type0 | yes | yes | 1 | `7c987ea28570cc2bc58d934fe8b0cfaf31b3a0bfde31cf9db2c5a1c610ea8131` |
| /JLZJML+LMRoman7-Regular-Identity-H | /Type0 | yes | yes | 1 | `c9c52f85e6728edbf9022a16d06fbd04ac1fe9e2497f6091ea4c72f3e49813a5` |
| /KDFUFA+LMRoman9-Italic-Identity-H | /Type0 | yes | yes | 4 | `197ef52432e943d96b9ab6b64a0ae19880c0902ec912704db5e5d51c2268dc47` |
| /SXFKEC+LMRoman10-BoldItalic-Identity-H | /Type0 | yes | yes | 1 | `102b9411ebe7c2e74fd199796ee690a4085d653f6fe7ebc7d39f00af16a10dfa` |
| /TZQTTS+MSAM10 | /Type1 | yes | yes | 7 | `88932ad26375cd739d788bd5ad5bb042d204d867758059b3a216ae76095445b4` |
| /VULLSM+LMMono9-Regular-Identity-H | /Type0 | yes | yes | 33 | `34d84032ac0fb0793bb943080c77ed1059d66eb6d16e9fa1a1a070e6435c788d` |
| /WTGFWZ+LMRoman10-Bold-Identity-H | /Type0 | yes | yes | 102 | `d69777e4d2fde0094bbe525194201887583bfbf923306665dcb847a5d449cfeb` |
| /WZNLEL+LMRoman10-Regular-Identity-H | /Type0 | yes | yes | 133 | `daefdae1c5558c4b1d1830ad11e8e2fc7fcc4ef581424f9f2b21b0c3322c053d` |
| /ZTRMKA+LMRoman9-Regular-Identity-H | /Type0 | yes | yes | 122 | `0ab8edd0c48d1e012e62f1e432bde0e04cad7234bd8886591d871d981b6f63ed` |

## Permanent disclosure to publish beside the PDF

> **Aksesibilitas PDF.** PDF ini adalah edisi cetak berhalaman tetap dan belum
> memiliki tag struktur PDF. Teks dapat dicari dan disalin, dan penanda bab tersedia,
> tetapi urutan baca, judul, daftar, tabel, rumus, dan tautan belum dikodekan sebagai
> struktur semantik untuk teknologi bantu. PDF ini tidak dinyatakan memenuhi PDF/UA.
> Untuk pembacaan dengan pembaca layar, pembesaran/reflow, navigasi papan ketik, dan
> struktur MathML, gunakan edisi HTML semantik yang diterbitkan bersama edisi ini.

> **PDF accessibility.** This fixed-layout print PDF is currently untagged. Its text is
> searchable and chapter bookmarks are present, but reading order, headings, lists,
> tables, mathematics, and links are not encoded as an assistive-technology structure.
> No PDF/UA conformance is claimed. Use the companion semantic HTML edition for screen
> readers, keyboard navigation, reflow/zoom, and MathML.
