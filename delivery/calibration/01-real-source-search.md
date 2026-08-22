# O017-WRAP-CAL-A01 — Kalibrasi pencarian sumber nyata

Status: `calibration_only`  
Kredit pelajar: `false`  
Peristiwa pencarian pelajar nyata: `false`  
Kontak atau transmisi eksternal: `false`

Dokumen ini adalah contoh kerja sintetis. Kueri, waktu, dan keputusan di bawah
menunjukkan seperti apa ledger yang lengkap; mereka tidak diklaim sebagai
aktivitas seorang pelajar. Sumber yang dibandingkan nyata dan berasal dari
halaman resmi penerbit atau institusi.

## Pertanyaan sebelum pencarian

`O017-WRAP-CAL-A01-Q`:

> Sumber primer terbuka mana yang memberi pernyataan dan konteks pembuktian
> Teorema Dasar Kalkulus yang cukup tepat untuk membandingkan hipotesis
> kontinuitas, lokator versi, dan cara penyajiannya?

Batas: sumber harus berupa makalah, monograf, atau catatan kuliah resmi; halaman
agregator dan ringkasan ensiklopedis boleh membantu menemukan kandidat tetapi
tidak boleh menjadi sumber klaim akhir. Bahasa tidak dibatasi. Tidak ada daftar
judul yang disediakan sebelumnya kepada pelaku kalibrasi.

## Aturan berhenti yang dibekukan lebih dahulu

Pencarian berhenti setelah semua kondisi berikut terpenuhi:

1. ditemukan sedikitnya satu monograf resmi dan satu sumber pengajaran resmi
   dari institusi berbeda;
2. setiap sumber mempunyai lokator tepat ke pernyataan atau kuliah yang
   relevan;
3. penerbit atau institusi menyatakan dasar akses/haknya;
4. pernyataan hipotesis dapat dibandingkan tanpa menyalin prosa panjang; dan
5. satu lintasan kueri tambahan tidak menghasilkan konflik versi yang material.

Jika syarat 2 atau 3 gagal, pencarian tidak boleh berhenti hanya karena isi
matematikanya tampak cocok.

## Ledger kueri sintetis

| ID | Waktu kalibrasi sintetis | Layanan | Kueri | Hasil yang dipertahankan | Alasan |
|---|---|---|---|---|---|
| `O017-WRAP-CAL-A01-QL01` | `2026-08-22T08:00:00+02:00` | mesin pencari umum | `site:openstax.org calculus fundamental theorem calculus` | halaman OpenStax §5.3 | domain penerbit; lokator bagian dan nomor teorema tersedia |
| `O017-WRAP-CAL-A01-QL02` | `2026-08-22T08:04:00+02:00` | mesin pencari umum | `site:ocw.mit.edu 18.100A fundamental theorem calculus` | MIT OCW Lecture 22 | halaman institusi; identitas kuliah, pengajar, semester, dan bahan tersedia |
| `O017-WRAP-CAL-A01-QL03` | `2026-08-22T08:09:00+02:00` | pencarian terbatas domain | `site:openstax.org/books/calculus-volume-1 "Fundamental Theorem" continuity` | OpenStax §5.3 dan halaman persamaan kunci | lintasan tambahan mengonfirmasi lokator; tidak menemukan konflik edisi pada permukaan web yang diperiksa |

Waktu pada tabel adalah bagian skenario kalibrasi, bukan telemetri sistem dan
bukan bukti aktivitas orang tertentu.

## Matriks calon dan otoritas

| Calon | Jenis | Otoritas primer | Versi/lokator | Hak yang dinyatakan | Keputusan |
|---|---|---|---|---|---|
| OpenStax, *Calculus Volume 1*, §5.3 | bagian monograf | halaman resmi OpenStax/Rice University; penulis Gilbert Strang dan Edwin Herman | halaman §5.3, Teorema Dasar Kalkulus Bagian 1 dan 2; keadaan web diakses 2026-08-22 | halaman pengantar menyatakan CC BY-NC-SA 4.0 untuk keadaan kini | dipakai sebagai sumber monograf utama; paket ini hanya menyimpan sitasi dan analisis orisinal |
| MIT OCW 18.100A, Lecture 22, Fall 2020 | kuliah dan catatan resmi | halaman resmi MIT OpenCourseWare; pengajar Casey Rodriguez | Lecture 22, “Fundamental Theorem of Calculus, Integration by Parts, and Change of Variable Formula” | ketentuan MIT OCW menyatakan CC BY-NC-SA 4.0, dengan pengecualian komponen pihak ketiga bila ditandai | dipakai sebagai pembanding penyajian dan jalur akses |
| hasil agregator/ensiklopedia | ringkasan sekunder | bukan penerbit karya yang dinilai | berubah tanpa versi yang dibekukan dalam contoh | bervariasi | dikeluarkan dari bukti klaim; hanya dapat menjadi alat penemuan |

## Rekaman pembekuan sumber

### O017-WRAP-SRC-OPENSTAX-FTC

- Judul: *Calculus Volume 1*, §5.3, “The Fundamental Theorem of Calculus”.
- Penulis: Gilbert Strang dan Edwin “Jed” Herman.
- Penerbit: OpenStax, Rice University.
- URL otoritatif:
  <https://openstax.org/books/calculus-volume-1/pages/5-3-the-fundamental-theorem-of-calculus>.
- Tanggal akses skenario: 2026-08-22.
- Lokator klaim: Teorema Dasar Kalkulus Bagian 1 dan Bagian 2 pada §5.3.
- Saksi representasi yang benar-benar diambil pada 2026-08-22: HTTP 200,
  584.844 byte, ETag `4253b01ceda870aaafd28b138d480603`, `Last-Modified`
  `2026-08-04T15:28:25Z`, SHA-256
  `f426a837c943b545698f9dc5f5918d8f1a0e901acb794cacb44383b59a3ea84a`.
  URL web tetap dapat berubah; digest membekukan byte yang dinilai tetapi tidak
  menjamin byte itu akan tetap tersedia di URL.
- Hak: CC BY-NC-SA 4.0 dinyatakan pada pengantar edisi web saat pemeriksaan.
- Redistribusi isi sumber dalam paket ini: tidak; hanya metadata, lokator, dan
  parafrase singkat orisinal.

### O017-WRAP-SRC-MIT-FTC-LECTURE22

- Judul: MIT OCW 18.100A Real Analysis, Lecture 22.
- Pengajar: Casey Rodriguez; masa kuliah: Fall 2020.
- URL otoritatif:
  <https://ocw.mit.edu/courses/18-100a-real-analysis-fall-2020/resources/18100a-lecture-22-multicam/>.
- Tanggal akses skenario: 2026-08-22.
- Lokator klaim: deskripsi Lecture 22 dan catatan kuliah terkait.
- Saksi representasi halaman yang benar-benar diambil pada 2026-08-22: HTTP
  200, 49.617 byte, ETag `5a2901baa2b34b376082baeb22d7f5b5`,
  `Last-Modified` `2026-08-18T18:10:52Z`, SHA-256
  `a9d4da8752e51471b94070b8ab1dbfed3ca35e79e527f2d97aa7bd3dae172261`.
- Hak: MIT OCW CC BY-NC-SA 4.0, dengan pengecualian yang mungkin dinyatakan pada
  komponen pihak ketiga.
- Redistribusi video, gambar, atau catatan sumber: tidak.

## Perbandingan klaim dan keputusan

Kedua sumber menempatkan kontinuitas sebagai hipotesis sentral untuk bentuk
Teorema Dasar Kalkulus yang mereka ajarkan. OpenStax memberi lokator monograf
yang langsung dan mudah disitasi. MIT OCW memberi konteks kuliah analisis dan
jalur alternatif melalui catatan serta video. Untuk klaim tertulis tentang
pernyataan teorema, OpenStax dipilih sebagai sumber utama; MIT dipakai untuk
membandingkan urutan dependensi dan sebagai permukaan akses alternatif.

Keputusan ini tidak menyatakan bahwa salah satu sumber merupakan bukti sejarah
pertama atau edisi kritis. Pertanyaan tersebut berada di luar batas pencarian.

## Ketidakpastian yang dipertahankan

1. Halaman web OpenStax dapat diperbarui tanpa URL baru; tanggal akses saja
   bukan saksi byte. Paket autentik harus mengarsipkan representasi yang
   diperbolehkan atau sekurang-kurangnya hash byte yang benar-benar diperiksa.
2. Lisensi umum MIT OCW tidak otomatis mencakup setiap komponen pihak ketiga.
   Karena itu paket ini tidak menyalin media.
3. Pencarian tidak menguji prioritas historis Teorema Dasar Kalkulus.
4. Tidak dilakukan penilaian aksesibilitas lengkap atas situs sumber; yang
   dicatat hanya keberadaan lebih dari satu permukaan.

## Pemeriksaan terhadap gerbang

Contoh ini memperagakan semua bidang G01, G02, G08, dan G09. Namun status
aktualnya tetap `calibration_only`: tidak ada pelajar, tidak ada evaluator
manusia, dan tidak ada artefak sumber yang diajukan untuk kredit. Menyalin
dossier ini dengan mengganti nama tidak memenuhi A01.
