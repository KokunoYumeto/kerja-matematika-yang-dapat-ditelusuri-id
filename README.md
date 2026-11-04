# Kerja Matematika yang Dapat Ditelusuri

Buku praktik Bahasa Indonesia sembilan unit tentang kerja matematika yang dapat ditelusuri: membaca argumen dan
literatur penelitian, merekonstruksi pembuktian, sitasi dan provenans, eksposisi, komputasi yang dapat direproduksi,
errata, penelaahan sejawat, dan kontribusi komunitas, beserta perangkat penyampaian dan penilaian. Tersedia sebagai
pembaca HTML semantik, PDF, dan backend semantik; edisi bahasa Inggris *Traceable Mathematical Work* ada di folder
`english/`.

[Baca daring](https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/) ·
[Unduh PDF](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/releases/download/v2026.08.24/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.24.pdf) ·
[English reader](https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/en/)

## Cara pembuatan

Buku ini ditulis oleh AI: OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi KokunoYumeto, untuk mata kuliah *Research
Reading, Exposition, and Reproducible Mathematical Work* (D120). Pemeriksaan terminologi membandingkan glosarium
dengan sumber TeX berbahasa Indonesia arXiv:0807.4609v1 dan bahan matematika resmi ITB; dua bentuk dikoreksi menjadi
`pohon merentang minimum` dan `Provenance pencarian`. Bukti pemeriksaan PDF, tampilan, dan paket rilis ada di
[`qa/`](qa/).

## Status

Edisi lengkap, versi 2026.08.24: unit O017-U01 sampai O017-U09 dengan perangkat penyampaian dan penilaian autentik
yang terpisah. Edisi bahasa Inggris lengkap, versi 2026.08.31. PDF tidak bertag dan bukan edisi aksesibel; untuk
pembaca layar, reflow, navigasi papan tik, dan MathML gunakan pembaca HTML. Masih mungkin ada kesalahan.

## Isi

Buku ini mengandaikan pembaca sudah dapat menulis pembuktian dasar, menggunakan matematika diskret, dan menjalankan
komputasi matematika yang dapat direproduksi.

1. Membaca argumen sebagai jejaring klaim, dan membedakan komputasi dari pembuktian.
2. Menelusuri literatur, menetapkan versi dan otoritas sumber, dan mengaudit rantai sitasi.
3. Merekonstruksi pembuktian yang diringkas melalui audit kuantor dan domain, graf ketergantungan, dan kontrak lema.
4. Memisahkan sitasi, provenans bukti, provenans komputasi, versi, koreksi, dan ketidakpastian.
5. Menulis eksposisi matematika yang dapat diaudit.
6. Paket komputasi matematika yang dapat direproduksi: eksekusi, keterulangan, validitas implementasi, bukti
   berhingga, dan pembuktian universal.
7. Dari diagnosis cacat ke erratum, koreksi yang mempertahankan sejarah, dan bahasa ketidakpastian.
8. Komentar penelaah, tanggapan penulis, revisi matematis minimal, dan rekomendasi.
9. Kontribusi komunitas yang terbatas dan penutupan portofolio unit 1–8.

Rilis: [v2026.08.24](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/releases/tag/v2026.08.24)
(PDF, arsip pembaca HTML luring, arsip sumber, backend, dan bukti) dan
[en-v2026.08.31](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/releases/tag/en-v2026.08.31)
(edisi bahasa Inggris). Di repositori: kontrol di `controls/`, sumber pembaca di `source/`, backend di `backend/`,
keluaran terbangun di `build/`, bukti pemeriksaan di `qa/`, sumber edisi bahasa Inggris di `english/`, dan petunjuk
build di [BUILD.md](BUILD.md).

## Sumber dan atribusi

- Unit 2, 4, 5, dan 6 memuat adaptasi metodologis terbatas dari *The Turing Way* (The Turing Way Community) dan
  *Research Software Engineering with Python* (Damien Irving, Kate Hertweck, Luke Johnston, Joel Ostblom, Charlotte
  Wickham, dan Greg Wilson), keduanya CC BY 4.0. Repositori, commit, lisensi, dan unit yang diadaptasi dicatat di
  `RELEASE_PROVENANCE.csv`; buku ini tidak menyiratkan dukungan mereka.
- Runtime pembaca HTML (Quarto 1.9.37, Bootstrap, dan lainnya) mempertahankan lisensinya sendiri:
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Lisensi

Teks buku tersedia menurut CC BY-SA 4.0, dengan atribusi donor CC BY 4.0 yang dipertahankan; perangkat lunak dan runtime
menurut MIT atau Apache-2.0. Pemetaan per komponen ada di [LICENSES.md](LICENSES.md).
