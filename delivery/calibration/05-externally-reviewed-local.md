# O017-WRAP-CAL-A05 — Kalibrasi jalur `externally_reviewed_local`

Status aktual: `calibration_only`  
Jalur yang diperagakan: `externally_reviewed_local`  
Status transaksi aktual: `prepared`  
Kredit pelajar: `false`  
Otorisasi transmisi: `false`  
Transmisi dilakukan: `false`  
Partisipasi komunitas yang diklaim: `false`

Contoh ini sengaja memilih jalur A05 yang lebih lemah. Ia menunjukkan bagaimana
paket erratum sumber nyata dapat ditelaah secara lokal ketika pengiriman tidak
diotorisasi atau tidak aman. Semua evaluator adalah persona sintetis; oleh
karena itu bahkan label `externally_reviewed_local` hanya merupakan **keadaan
target yang diperagakan**, bukan hasil aktual yang diberikan kepada siapa pun.

## Paket kontribusi lokal

| Bidang | Nilai |
|---|---|
| package_id | `O017-WRAP-CAL-A05-PACKET` |
| sumber | koreksi resmi Hardy 1928, DOI `10.1112/plms/s2-28.1.553-t` |
| artefak utama | `04-real-source-erratum-dossier.md` |
| jenis kontribusi | reproduksi dan penjelasan ringkas koreksi yang sudah diterbitkan |
| nilai marjinal luar | tidak dibuktikan; koreksi resmi sudah ada |
| target luar | tidak ditetapkan |
| draf pesan keluar | tidak dibuat |
| authorization_present | `false` |
| transmission_performed | `false` |
| current_state | `prepared` |

Karena tidak ada target dan koreksi telah diterbitkan, mengirim laporan baru
akan berisiko duplikasi. Paket berhenti lokal. Berhenti bukan kegagalan teknis;
ia adalah hasil gerbang target dan nilai marjinal.

## Pemeriksaan hak, target, dan privasi

1. Paket menyimpan metadata, rumus matematika, serta analisis orisinal; tidak
   menyalin tata letak atau prosa panjang penerbit.
2. DOI dan lokator resmi dipertahankan.
3. Tidak ada nama, surel, akun, atau data pribadi evaluator di paket.
4. ID evaluator bersifat buram dan tidak dibentuk dari data pribadi.
5. Tidak ada pemetaan identitas di dalam paket kalibrasi.
6. Tidak ada target eksternal, jadi otorisasi tidak dapat dianggap ada.

## Simulasi penelaahan lokal

Penelaah sintetis `O017-WRAP-EVAL-CAL-LOCAL-REVIEWER` diberi lingkup berikut:

- periksa dua antiturunan dan evaluasi batas;
- periksa bahwa status “bukan temuan baru” cocok dengan koreksi resmi;
- periksa bahwa paket tidak menyatakan telah dikirim;
- periksa pemisahan antara nilai matematika dan audit dampak sejarah; serta
- periksa alternatif akses teks.

### Laporan sintetis

| ID komentar | Lokator | Temuan | Disposisi target | Status aktual contoh |
|---|---|---|---|---|
| `O017-WRAP-CAL-A05-LR01` | dossier §Reproducer pertama | turunan `y/(x+y)^2` benar dan nilai luar `1/2` | `accepted` | simulasi saja |
| `O017-WRAP-CAL-A05-LR02` | dossier §Reproducer kedua | turunan `-x/(x+y)^2` benar dan nilai luar `-1/2` | `accepted` | simulasi saja |
| `O017-WRAP-CAL-A05-LR03` | dossier §Audit dampak | jangkauan pemakaian sejarah tetap terbuka dan tidak dilebihkan | `accepted` | simulasi saja |
| `O017-WRAP-CAL-A05-LR04` | seluruh paket | label tanpa kontak dan tanpa transmisi konsisten | `accepted` | simulasi saja |

Rekomendasi target: `externally_reviewed_local`. Karena penelaah bukan manusia
terverifikasi, hasil aktual tetap `calibration_only`.

## Ledger status append-only

| Event ID | Waktu skenario | Status | Peristiwa luar | Bukti | Makna yang diizinkan |
|---|---|---|---|---|---|
| `O017-WRAP-EVT-CAL-A05-01` | `2026-08-22T09:00:00+02:00` | `prepared` | `false` | paket lokal dan manifest | hanya siap diperiksa secara lokal |

Tidak ada peristiwa `submitted`, `acknowledged`, `accepted`, `merged`, atau
`published`. Baris tersebut tidak boleh ditambahkan sebagai placeholder. Jika
keadaan luar kelak tidak diketahui setelah transaksi nyata, `unknown` ditambah
sebagai peristiwa baru sambil menyimpan status terakhir yang mempunyai bukti.

## Perbedaan dua kredensial

| Label | Bukti A05 minimum | Klaim yang boleh dibuat |
|---|---|---|
| `complete_community_transaction` | otorisasi khusus, bukti transmisi, dan ledger yang sekurang-kurangnya pernah mencapai `submitted` | satu kontribusi nyata dikirim; tidak otomatis diterima |
| `complete_externally_reviewed_local` | penelaah manusia independen menilai paket sumber nyata secara lokal; tidak ada klaim transmisi | paket autentik ditelaah di luar peran penulis tetapi tetap lokal |
| `calibration_only` | contoh sintetis seperti dokumen ini | bentuk paket diperagakan; tidak ada kredit atau peristiwa manusia |

Label kedua sengaja lebih lemah dari yang pertama. Antarmuka, sertifikat, dan
ekspor data tidak boleh menyembunyikan akhiran `externally_reviewed_local`.

## Alternatif akses

Paket dapat ditinjau tanpa video atau audio. Semua klaim memiliki judul, tabel,
dan bentuk teks; rumus ditulis sebagai LaTeX polos; status tidak bergantung pada
warna. Penyerahan autentik menambahkan hasil uji keyboard/pembaca layar dan
membedakan permukaan yang diuji dari yang belum diuji.

## Kondisi untuk mengubah jalur pada penyerahan autentik

Paket pelajar hanya boleh berpindah ke `community_transaction` bila seorang
manusia memberi otorisasi khusus yang memuat target, artefak dan versi, saluran,
pengirim bertanggung jawab, batas data pribadi, dan masa berlaku. Setelah itu,
pengiriman masih harus dilakukan oleh pelaku yang diotorisasi dan dibuktikan.
Otorisasi tanpa tanda terima tidak cukup untuk `submitted`; tanda terima tanpa
otorisasi melanggar G07.

## Pemeriksaan terhadap gerbang

Contoh memperagakan G05, G07, G08, dan G09 serta bentuk G04. G04 tidak lulus
secara autentik karena persona penelaah bukan manusia terverifikasi. Tidak ada
jalur status yang boleh mengubah `calibration_only` menjadi hasil kelulusan.

