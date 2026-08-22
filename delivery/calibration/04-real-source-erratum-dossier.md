# O017-WRAP-CAL-A04 — Kalibrasi dossier erratum sumber nyata

Status: `calibration_only`  
Kredit pelajar: `false`  
Penemuan baru yang diklaim: `false`  
Pemeriksa manusia independen: `false`  
Kontak atau transmisi eksternal: `false`

Dossier ini mengaudit koreksi yang telah diterbitkan, bukan melaporkan kesalahan
baru. Sumber nyatanya adalah G. H. Hardy, “Addenda and Corrigenda”,
*Proceedings of the London Mathematical Society* (1928), DOI
<https://doi.org/10.1112/plms/s2-28.1.553-t>. Halaman penerbit menyatakan bahwa
dua nilai integral berulang yang sebelumnya dicetak sebagai `1` dan `-1`
seharusnya `1/2` dan `-1/2`.

## Pembekuan objek

| Bidang | Nilai |
|---|---|
| source_id | `O017-WRAP-SRC-HARDY-1928-CORRECTION` |
| jenis | koreksi resmi penerbit |
| judul | “Addenda and Corrigenda” |
| penulis | G. H. Hardy |
| tahun | 1928 |
| DOI | `10.1112/plms/s2-28.1.553-t` |
| lokator | catatan “Note on the inversion of a repeated integral” pada halaman koreksi |
| keadaan yang diaudit | pasangan nilai lama `1`, `-1` sebagaimana dirujuk oleh koreksi |
| pembanding resmi | pasangan nilai koreksi `1/2`, `-1/2` |
| tanggal akses skenario | 2026-08-22 |
| hak penggunaan di sini | fakta bibliografis, rumus matematika, dan analisis orisinal; tidak ada tata letak atau prosa penerbit yang disalin |

DOI mengidentifikasi versi rekaman koreksi. Dossier tidak mempunyai salinan
berhash dari cetakan lama dan karena itu tidak mengklaim telah memeriksa seluruh
halaman asal secara mandiri.

## Pernyataan dan klasifikasi

Untuk

```text
g(x,y) = (x-y)/(x+y)^3,
```

dua integral berulang pada bujur sangkar satuan diperiksa dalam urutan berbeda.

| Bidang | Nilai |
|---|---|
| statement_status nilai lama | `false_as_written` |
| defect_kind utama | `numerical_error` |
| akibat matematika | nilai kedua integral berulang salah dengan faktor dua dalam catatan lama yang dirujuk |
| keparahan | `S2_local_substantive` |
| keyakinan | `C3_high` untuk perhitungan; `C2_moderate` untuk jangkauan sejarah karena sumber lama penuh tidak diaudit |
| penemuan baru | tidak; koreksi resmi sudah menerbitkan hasil |

## Reproducer minimal pertama: urutan `dy` lalu `dx`

Untuk `x>0`, antiturunan terhadap `y` adalah

```text
y/(x+y)^2,
```

karena turunannya sama dengan `(x-y)/(x+y)^3`. Maka

```text
integral y=0..1 g(x,y) dy = 1/(x+1)^2.
```

Integrasi luar memberi

```text
integral x=0..1 1/(x+1)^2 dx
= [-1/(x+1)] from 0 to 1
= 1/2.
```

## Reproducer minimal kedua: urutan `dx` lalu `dy`

Untuk `y>0`, antiturunan terhadap `x` adalah

```text
-x/(x+y)^2,
```

sehingga

```text
integral x=0..1 g(x,y) dx = -1/(y+1)^2.
```

Integrasi luar memberi

```text
integral y=0..1 -1/(y+1)^2 dy
= [1/(y+1)] from 0 to 1
= -1/2.
```

Kedua nilai cocok dengan koreksi resmi.

## Diagnosis dan koreksi minimal

Koreksi minimal untuk nilai yang dirujuk ialah:

```text
1     ->  1/2
-1    -> -1/2
```

Dossier tidak mengusulkan perubahan pada integran, domain, atau urutan
integrasi. Ia juga tidak menyatakan bahwa antisimetri memberi nilai nol, karena
integral absolut divergen di sudut `(0,0)` dan pertukaran urutan tidak sah tanpa
hipotesis tambahan.

## Pemeriksaan independen dalam kalibrasi

Persona `O017-WRAP-EVAL-CAL-CHECKER` melakukan jalur hitung kedua dalam skenario:

1. menurunkan kedua antiturunan secara langsung;
2. mengevaluasi batas `0` dan `1`;
3. memakai transformasi pertukaran `x<->y` hanya untuk memeriksa bahwa tanda
   kedua urutan harus berlawanan, bukan untuk menetapkan nilainya; dan
4. mengonfirmasi pasangan `1/2`, `-1/2`.

Hasil skenario: `agrees_with_dossier`. Namun `human_status` persona adalah
`synthetic_persona`, sehingga ini **bukan pemeriksaan manusia independen** dan
tidak memenuhi G04. Dalam penyerahan autentik, pemeriksa kedua harus mengulang
perhitungan, menandatangani lingkup, dan menyimpan bukti dengan ID buram.

## Audit dampak dan ketidakpastian

| Pertanyaan | Bukti | Status |
|---|---|---|
| Apakah pasangan nilai lama benar? | perhitungan elementer dan koreksi resmi | ditutup: tidak |
| Apakah pasangan baru benar? | dua antiturunan dan evaluasi batas | ditutup: ya dalam lingkup integral berulang |
| Apakah urutan dapat dipertukarkan? | integrabilitas absolut gagal dekat nol | ditutup: tidak melalui Fubini/Tonelli biasa |
| Bagian karya lama mana yang memakai nilai itu? | tidak ada audit penuh cetakan lama dalam paket | terbuka |
| Apakah ini penemuan baru? | koreksi resmi tahun 1928 sudah ada | ditutup: tidak |
| Apakah perlu menghubungi penerbit? | koreksi sudah diterbitkan; tidak ada nilai marjinal yang dibuktikan | tidak; dilarang oleh batas tanpa kontak |

## Draf koreksi lokal, tidak dikirim

> Pada integral berulang dengan integran `(x-y)/(x+y)^3` di bujur sangkar
> satuan, integrasi terhadap `y` lalu `x` menghasilkan `1/2`, sedangkan urutan
> sebaliknya menghasilkan `-1/2`. Antiturunan dalam masing-masing adalah
> `y/(x+y)^2` dan `-x/(x+y)^2`. Ini mereproduksi koreksi resmi Hardy (1928), DOI
> `10.1112/plms/s2-28.1.553-t`; bukan temuan baru dan tidak memerlukan laporan
> keluar dari paket kalibrasi ini.

## Pemeriksaan terhadap gerbang

Contoh memperagakan bidang G01, G05, G08, dan G09. G04 tetap tidak dinilai
karena pemeriksa adalah persona sintetis. Status tertinggi contoh adalah
`calibration_only`, bukan `passed` dan bukan `ready_for_submission`.

