# O017-WRAP-CAL-A03 — Kalibrasi putaran penulis–penelaah

Status: `calibration_only`  
Kredit pelajar: `false`  
Dua manusia berbeda: `false`  
Kontak atau transmisi eksternal: `false`

Kedua ID peran di bawah adalah persona sintetis. Mereka memperagakan pemisahan
peran dan artefak, tetapi tidak memenuhi gerbang independensi manusia. Naskah
matematikanya orisinal dan memakai integral yang disebut dalam koreksi resmi
G. H. Hardy tahun 1928 sebagai kasus nyata.

## Identitas dan pembekuan

| Objek | ID | Keadaan |
|---|---|---|
| penulis sintetis | `O017-WRAP-EVAL-CAL-AUTHOR` | `synthetic_persona` |
| penelaah sintetis | `O017-WRAP-EVAL-CAL-REFEREE` | `synthetic_persona` |
| naskah awal | `O017-WRAP-CAL-A03-MS-V1` | beku sebagai teks di bawah |
| laporan | `O017-WRAP-CAL-A03-RR-V1` | menilai V1 saja |
| tanggapan | `O017-WRAP-CAL-A03-AR-V1` | menjawab setiap komentar |
| revisi | `O017-WRAP-CAL-A03-MS-V2` | beku sebagai teks di bawah |

Atestasi distingsi autentik tidak tersedia. Rekaman kalibrasi menyatakan
`distinct_humans = false` dan `credit_effect = none`.

## Naskah awal sintetis V1

> **Klaim.** Untuk
> `g(x,y)=(x-y)/(x+y)^3` pada `(0,1]×(0,1]`, kedua integral berulang bernilai
> nol. Alasannya, menukar `x` dan `y` mengubah tanda integran sementara bujur
> sangkar satuan tetap sama.

Naskah tidak membuktikan integrabilitas absolut dan memperlakukan integral
berulang seperti integral ganda tak berurutan.

## Laporan penelaah sintetis V1

Lingkup: validitas klaim, legitimasi pertukaran urutan, dan kecukupan bukti.
Gaya serta prioritas sejarah tidak dinilai. Konflik kepentingan tidak dapat
diperiksa karena persona bukan manusia.

### Komentar utama C1

- Lokator: satu-satunya paragraf bukti V1.
- Klaim yang dinilai: antisimetri memaksa kedua integral berulang bernilai nol.
- Diagnosis: simpulan itu memerlukan pertukaran urutan atau integral ganda yang
  terdefinisi secara sesuai. Dekat `(0,0)`, `|g|` tidak terintegralkan absolut,
  sehingga langkah tersebut tidak tersedia tanpa argumen tambahan.
- Reproducer: hitung integral dalam terhadap `y` lebih dahulu dan terhadap `x`
  lebih dahulu. Keduanya memberi nilai berlawanan, bukan nol.
- Permintaan: nyatakan urutan integral, hitung setiap integral dalam, dan hapus
  klaim integral ganda tak berurutan.
- Keparahan: utama; klaim pusat V1 salah.
- Keyakinan: tinggi untuk diagnosis matematika; bukan klaim tentang maksud
  penulis sejarah.

### Komentar minor C2

- Lokator: definisi domain.
- Diagnosis: titik singular `(0,0)` dikeluarkan secara informal, tetapi batas
  integral masih mencapai nol.
- Permintaan: sebut bahwa integral dalam dipahami sebagai limit improper pada
  titik ujung jika diperlukan, dan tunjukkan hasil limitnya.

Rekomendasi sintetis: `major_revision`.

## Tanggapan penulis sintetis

| Komentar | Disposisi | Tindakan | Bukti dan lokasi baru | Masalah tersisa |
|---|---|---|---|---|
| C1 | `accepted` | klaim nol dihapus; dua urutan dihitung terpisah | V2, dua perhitungan turunan elementer | integral ganda tak berurutan sengaja tidak diberi nilai |
| C2 | `accepted` | sifat improper pada sudut dinyatakan | V2, paragraf setelah rumus | teori umum Fubini/Tonelli di luar lingkup |

Tanggapan tidak mengatakan “diperbaiki” sebelum menampilkan V2.

## Naskah revisi sintetis V2

Definisikan

```text
I_yx = integral x=0..1 [ integral y=0..1 (x-y)/(x+y)^3 dy ] dx,
I_xy = integral y=0..1 [ integral x=0..1 (x-y)/(x+y)^3 dx ] dy.
```

Untuk `x>0`,

```text
d/dy [ y/(x+y)^2 ] = (x-y)/(x+y)^3.
```

Karena itu integral dalam pertama bernilai `1/(x+1)^2`, lalu

```text
I_yx = integral_0^1 1/(x+1)^2 dx = 1/2.
```

Untuk `y>0`,

```text
d/dx [ -x/(x+y)^2 ] = (x-y)/(x+y)^3.
```

Maka integral dalam kedua bernilai `-1/(y+1)^2`, sehingga

```text
I_xy = integral_0^1 -1/(y+1)^2 dy = -1/2.
```

Nilai pada ujung diperoleh sebagai limit dari batas bawah positif. Dengan
demikian dua integral berulang ada tetapi berbeda. Naskah tidak memberi nilai
pada integral ganda tak berurutan.

Sebagai pemeriksaan kegagalan integrabilitas absolut, ambil wilayah
`0<y<x/2<1/2`. Di sana `|x-y|>=x/2` dan `x+y<=3x/2`, sehingga
`|g(x,y)| >= 4/(27x^2)`. Mengintegralkan terhadap `y` sepanjang interval dengan
panjang `x/2` menghasilkan batas bawah yang sebanding dengan `1/x`; integral
terhadap `x` divergen di nol.

## Bukti sebelum/sesudah

| Unsur | V1 | V2 |
|---|---|---|
| klaim nilai | kedua urutan nol | urutan `dy dx` memberi `1/2`; urutan `dx dy` memberi `-1/2` |
| dasar | antisimetri tanpa gerbang | antiturunan eksplisit dan limit ujung |
| pertukaran urutan | dilakukan diam-diam | tidak dilakukan; kegagalan integrabilitas absolut dibuktikan |
| status integral ganda | dianggap ada | sengaja tidak diklaim |

## Masalah yang tetap terbuka

1. Contoh tidak membahas nilai utama Cauchy dua dimensi atau skema regularisasi
   lain.
2. Contoh tidak menilai semua akibat historis dari kesalahan numerik.
3. Persona sintetis tidak memenuhi independensi manusia; putaran autentik harus
   diulang oleh dua manusia berbeda dengan artefak dan hash baru.

## Pemeriksaan terhadap gerbang

Rantai V1–laporan–respons–disposisi–V2 lengkap dan memperagakan G05, G06, G08,
serta G09. G04 sengaja tidak lulus secara autentik. Mengganti
`synthetic_persona` menjadi `verified_human` tanpa atestasi nyata merupakan
pemalsuan bukti.

