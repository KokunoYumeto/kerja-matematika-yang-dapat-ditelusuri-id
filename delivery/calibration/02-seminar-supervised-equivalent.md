# O017-WRAP-CAL-A02 — Kalibrasi seminar/padanan tersupervisi

Status: `calibration_only`  
Jalur yang diperagakan: `supervised_equivalent`  
Kredit pelajar: `false`  
Kehadiran seminar nyata yang diklaim: `false`  
Kontak atau transmisi eksternal: `false`

Ini adalah gladi sintetis berstruktur, bukan rekaman Lecture 22, bukan bukti
bahwa seseorang menontonnya, dan bukan pengesahan oleh MIT. Isi matematika
disusun secara orisinal dengan halaman resmi MIT OCW 18.100A Lecture 22 dan
OpenStax §5.3 sebagai sumber nyata. Penanda waktu di bawah mengacu hanya pada
transkrip latihan sintetis berdurasi 24 menit.

## Identitas sesi kalibrasi

| Bidang | Nilai |
|---|---|
| ID | `O017-WRAP-CAL-A02-SESSION` |
| jenis | gladi padanan tersupervisi sintetis |
| tanggal skenario | `2026-08-22` |
| durasi | `00:24:00` |
| sumber nyata | MIT OCW 18.100A Lecture 22; OpenStax *Calculus Volume 1* §5.3 |
| pelaku sintetis | `O017-WRAP-EVAL-CAL-LEARNER` |
| supervisor sintetis | `O017-WRAP-EVAL-CAL-SUPERVISOR` |
| bukti manusia nyata | tidak ada |
| akibat terhadap kredit | tidak ada; G03 dan G04 tidak dinilai secara autentik |

## Catatan berwaktu dari transkrip sintetis

| Waktu | Jenis | Catatan | Dasar dan lokator | Status setelah pemeriksaan |
|---|---|---|---|---|
| `00:00–02:30` | ruang lingkup | Sesi akan membedakan pernyataan FTC Bagian 1 dan evaluasi integral pada Bagian 2. | OpenStax §5.3, dua kotak teorema; MIT Lecture 22, deskripsi resmi | teramati dalam naskah sintetis; cocok dengan kedua lokator |
| `02:30–06:00` | dependensi | Kontinuitas dipakai agar rata-rata lokal fungsi mendekati nilai fungsi pada titik. | OpenStax, bukti Bagian 1; dependensi pada teorema nilai rata-rata integral | didukung dalam batas penyajian sumber |
| `06:00–10:30` | klaim | Jika `F(x)=∫_a^x f(t)dt` dan `f` kontinu, maka `F'(x)=f(x)` pada interior interval. | OpenStax §5.3, FTC Bagian 1 | didukung; notasi ditulis ulang, bukan kutipan |
| `10:30–14:30` | langkah bukti | Hasil bagi selisih `F` menjadi rata-rata `f` pada interval yang menyusut. | perhitungan orisinal yang mengikuti struktur bukti pada sumber | didukung; arah interval untuk `h<0` perlu dinyatakan dengan hati-hati |
| `14:30–18:00` | pertanyaan | Apakah kontinuitas perlu, atau cukup kondisi lebih lemah hampir di mana-mana? | pertanyaan pelaku sintetis | terbuka; berada di luar teorema elementer yang dibekukan |
| `18:00–21:30` | klaim | Untuk antiturunan `F`, integral tentu dapat dihitung sebagai `F(b)-F(a)`. | OpenStax §5.3, FTC Bagian 2 | didukung dalam hipotesis sumber |
| `21:30–24:00` | batas | Sesi tidak membuktikan bentuk Lebesgue, prioritas historis, atau kondisi minimal. | batas yang ditetapkan sebelum sesi | dipertahankan sebagai masalah di luar lingkup |

## Peta dependensi

```text
kontinuitas f pada [a,b]
        |
        v
integrabilitas Riemann + teorema nilai rata-rata integral
        |
        v
rata-rata f pada interval yang menyusut -> f(x)
        |
        v
F'(x)=f(x) untuk F(x)=integral dari a ke x
        |
        v
evaluasi integral melalui suatu antiturunan
```

Panah terakhir memakai fakta tambahan bahwa dua antiturunan berbeda dengan
konstanta pada interval. Gladi mencatat dependensi itu agar kesimpulan tidak
terlihat muncul langsung dari definisi integral.

## Log pertanyaan dan disposisi

| ID | Pertanyaan | Tindakan | Bukti/lokator | Status |
|---|---|---|---|---|
| `O017-WRAP-CAL-A02-Q01` | Bagaimana hasil bagi selisih bekerja untuk `h<0`? | tulis integral berorientasi dan periksa tanda | perhitungan orisinal; definisi integral berorientasi | `verified_after_session` |
| `O017-WRAP-CAL-A02-Q02` | Apakah kontinuitas merupakan kondisi paling lemah? | jangan memperluas klaim; catat sebagai pertanyaan lanjut | sumber yang dibekukan hanya menyatakan bentuk kontinu | `open_out_of_scope` |
| `O017-WRAP-CAL-A02-Q03` | Mengapa pilihan antiturunan tidak memengaruhi nilai? | tambahkan bahwa konstanta saling meniadakan | OpenStax §5.3, penjelasan setelah contoh evaluasi | `verified_after_session` |

## Catatan akhir yang dikoreksi

Versi awal sintetis menulis “FTC menjamin setiap fungsi terintegralkan memiliki
antiturunan.” Catatan akhir mempersempitnya:

> Dalam bentuk yang diperiksa di OpenStax §5.3, fungsi kontinu pada interval
> menghasilkan fungsi integral `F(x)=∫_a^x f(t)dt` yang turunannya sama dengan
> `f` pada interior interval.

Perubahan mencegah satu teorema elementer dipakai untuk kelas fungsi yang tidak
dibahas dalam sumber.

## Bukti supervisi dan batasnya

Dalam penyerahan autentik, supervisor manusia akan mengesahkan ID sesi, segmen
yang ditugaskan, pekerjaan mandiri pelajar, waktu pemeriksaan, dan hasil dengan
ID buram. Contoh ini hanya menyediakan bentuk rekamannya:

```yaml
attestation_id: O017-WRAP-CAL-A02-ATT-SYNTHETIC
supervisor_id: O017-WRAP-EVAL-CAL-SUPERVISOR
human_status: synthetic_persona
work_observed: false
credit_effect: none
```

Karena `human_status` bukan `verified_human`, data ini tidak boleh diubah
menjadi `pass`.

## Alternatif akses yang setara

Jalur tanpa audio memakai:

1. halaman deskripsi Lecture 22 dan catatan kuliah resmi sebagai lokator teks;
2. transkrip latihan sintetis berjudul dan bersegmen;
3. rumus sebagai teks LaTeX yang dapat disalin;
4. peta dependensi dalam daftar teks selain diagram monospace; dan
5. log pertanyaan tertulis yang tidak menuntut bicara langsung.

Supervisor autentik harus menguji berkas dengan navigasi keyboard dan pembaca
layar yang tersedia, lalu menyebut apa yang belum diuji. Menyediakan PDF atau
video saja bukan alternatif akses.

## Pemeriksaan terhadap gerbang

Contoh memperagakan seluruh elemen G03, G08, dan G09, tetapi tidak memenuhi
gerbang autentik karena sesi dan supervisor bersifat sintetis. Status tetap
`calibration_only`; ia tidak boleh disebut seminar yang dihadiri atau padanan
tersupervisi yang selesai.

