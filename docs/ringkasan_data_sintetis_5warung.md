# Data Sintetis Lima Warung: Ringkasan

Ringkasan untuk dibaca sekitar 20 menit. Penjelasan lengkap ada di
[data_sintetis_5warung.md](data_sintetis_5warung.md).

---

## 1. Apa yang sudah jadi

Data penjualan setahun untuk lima warung yang berbeda karakter, memakai barang dari
katalog IPOS, siap dipakai untuk membangun dan mendemokan forecasting sebelum ada data
warung asli.

| warung | ciri | barang | terjual per hari | omzet per hari |
| --- | --- | --- | --- | --- |
| A | gang kecil | 250 | 231 | Rp1,2 juta |
| B | sembako menengah | 500 | 498 | Rp2,7 juta |
| C | dekat sekolah | 400 | 390 | Rp1,4 juta |
| D | kelontong besar | 900 | 890 | Rp4,8 juta |
| E | dekat kos atau kampus | 350 | 365 | Rp1,8 juta |

Periode 1 Oktober 2025 sampai 30 September 2026, total 876.000 baris penjualan harian.

---

## 2. Dari 50.601 barang IPOS ke rak warung

Katalog IPOS adalah templat aplikasi kasir yang memuat segala jenis barang toko, bukan
hanya barang warung. Barang warung dipisahkan dalam empat tahap.

| tahap | sisa | yang dibuang atau dipilih |
| --- | --- | --- |
| **katalog IPOS** | **50.601** | |
| saringan nama | 16.304 | 30.246 barang yang namanya tidak cocok dengan kamus 22 kategori warung (kosmetik, perabot, pakaian, elektronik, obat apotek, produk impor), 2.755 barang yang jelas bukan barang warung (minuman beralkohol, makanan hewan, perawatan tubuh), 1.017 kemasan karton, dan 279 barang yang ditandai tidak aktif |
| pemilihan per kategori | 1.947 | diambil sesuai kebutuhan rak per kategori; merek utama setiap kategori diambil lebih dahulu, sisanya acak |
| tambahan | +123 | barang laris yang terlewat (misalnya GG Filter, Djarum 76, Teh Pucuk 350 ml, SKM Frisian Flag kaleng) dan es krim |
| **dinilai satu per satu** | **2.070** | dinilai oleh Claude (AI) dengan pedoman tertulis, lalu ditinjau ulang tim |
| **lolos penilaian** | **1.130** | 938 dibuang, rinciannya di bawah |
| **dipakai di rak lima warung** | **971 jenis** | 140 barang inti ada di kelima warung, sisanya berbeda antar warung |

**Siapa yang menilai dan bagaimana.** Penilaian 2.070 barang dikerjakan oleh Claude (AI)
mengikuti [pedoman klasifikasi](pedoman_klasifikasi.md) yang sama untuk setiap barang:
kategori, satuan dan ukuran, kelas harga, popularitas 1 sampai 5, cocok warung atau tidak,
tingkat keyakinan, dan alasan apabila dibuang. Karena memakai satu pedoman, penilaiannya
konsisten antar barang. Dasarnya adalah pengetahuan umum tentang produk dan warung di
Indonesia, bukan data penjualan, sehingga hasilnya tetap penilaian. Barang yang
keyakinannya rendah dibuang, dan seluruh hasil ditinjau ulang oleh tim.

**Alasan 938 barang dibuang saat penilaian:**

| alasan | jumlah | contoh |
| --- | --- | --- |
| produk impor | 284 | produk Filipina dan Malaysia, terlihat dari awalan barcode |
| kemasan kulakan yang dijual per bagian oleh pemilik | 239 | kopi isi 10, renceng Masako, Indomie isi 5 |
| nama atau merek tidak jelas | 202 | merek lokal kecil yang tidak dapat dipastikan |
| kemasan besar atau grosir | 79 | saus 1 kg, minyak 5 liter, susu 1 kg |
| bukan barang warung | 54 | parfum, deodoran, keperluan kantor, kemasan hadiah |
| produk apotek atau supermarket | 41 | vitamin, obat resep, susu formula bayi |
| barang kembar | 16 | barang sama dengan nama atau kode berbeda |
| sudah tidak beredar | 9 | Pepsi, Mirinda, Tide |

**Kenapa tidak memakai lebih banyak barang:**

- **Ukuran rak warung memang terbatas.** Warung gang menjual sekitar 250 jenis barang dan
  kelontong besar sekitar 900. Kumpulan 1.130 barang sudah lebih banyak dari kebutuhan
  warung terbesar, sehingga setiap warung masih dapat memilih isi raknya sendiri.
- **Setiap barang dinilai satu per satu**, termasuk apakah lazim dijual di warung dan dalam
  kemasan apa. Penilaian dikerjakan pada sampel yang mewakili setiap kategori, bukan pada
  16.304 kandidat.
- **Pemilihan tidak acak murni.** Merek utama setiap kategori diambil lebih dahulu, lalu
  hasilnya diperiksa ulang untuk memastikan barang terlaris warung (Indomie, Sampoerna,
  Aqua, Royco, Rinso, Gulaku, dan sebagainya) tersedia.

---

## 3. Dasar angka penjualan

Setiap barang punya rata-rata laku per hari yang ditentukan oleh empat faktor.

**Faktor 1: patokan per kategori.** Setiap kategori punya patokan, yaitu berapa laku barang
terlarisnya di warung standar (B). Angkanya diambil dari resep 60 barang yang sebelumnya
sudah diaudit satu per satu, lalu dicocokkan dengan perkiraan porsi omzet warung.

| kategori | barang terlaris | patokan per hari |
| --- | --- | --- |
| mie instan | Indomie Goreng | 15 bungkus |
| air minum | Aqua 600 ml | 11 botol |
| rokok | Sampoerna Mild 16 | 8 bungkus |
| obat warung | Tolak Angin | 2 sachet |
| makanan kaleng | Maya Mackerel 425 g | 0,6 kaleng |

**Faktor 2: popularitas barang.** Di dalam satu kategori, barang yang kurang populer laku
lebih sedikit. Contoh mie instan di warung B:

| peringkat | barang | popularitas | laku per hari |
| --- | --- | --- | --- |
| 1 | Indomie Goreng | 5 | 15,0 |
| 2 | Indomie Ayam Spesial | 4 | 6,9 |
| 3 | Indomie Ayam Bawang | 4 | 6,3 |
| 9 | Sarimi Gelas Soto | 3 | 2,2 |
| 16 | Pop Mie Goreng Pedas | 3 | 0,9 |
| 25 | Pop Mie Kari Susu | 1 | 0,13, sekitar sekali seminggu |

Perbandingan varian kedua Indomie terhadap Indomie Goreng (sekitar separuh) sesuai resep 60
barang yang sudah diaudit.

**Faktor 3: harga satuan.** Barang dengan popularitas sama tetapi kemasan lebih mahal laku
lebih jarang. Contoh Rinso di warung B:

| barang | kelas harga | popularitas | laku per hari |
| --- | --- | --- | --- |
| Rinso sachet 23 g | murah | 4 | 8,0 |
| Rinso 75 g | murah | 3 | 2,2 |
| Rinso bubuk 500 g | sedang | 3 | 0,9 |

**Faktor 4: karakter warung.** Barang yang sama laku berbeda di setiap warung, tergantung
keramaian dan kategori yang ditonjolkan:

| barang | A gang | B standar | C sekolah | D besar | E kos |
| --- | --- | --- | --- | --- | --- |
| Indomie Goreng | 11,3 | 15,0 | 11,6 | 22,5 | **18,8** |
| Chocolatos | 4,2 | 9,0 | **11,1** | 13,5 | 9,2 |
| Sampoerna Mild 16 | 4,6 | 8,0 | **3,1** | 12,0 | 7,5 |

Warung kos menonjolkan mie, warung sekolah menonjolkan jajanan dan lemah di rokok, warung
besar paling ramai.

Hasilnya kemudian dicek terhadap angka yang diketahui:

| pembanding | angka yang diketahui | di data |
| --- | --- | --- |
| omzet warung kelontong | pedagang menyebut [hingga sekitar Rp5 juta per hari](https://finance.detik.com/industri/d-7474476/dilarang-jual-rokok-dekat-sekolah-pedagang-bisa-kehilangan-setengah-omzet) | Rp1,2 sampai 4,8 juta |
| porsi rokok di omzet | pedagang menyebut [40 persen ke atas](https://www.medcom.id/ekonomi/bisnis/JKRPYoyb-larangan-penjualan-rokok-batangan-ditolak-para-pemilik-warung) | sekitar sepertiga |

---

## 4. Datanya terasa seperti warung

**Penjualan harian warung B, dua minggu pertama November**

| barang | Sen | Sel | Rab | Kam | Jum | Sab | Min | Sen | Sel | Rab | Kam | Jum | Sab | Min |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Indomie Goreng | 18 | 10 | 9 | 14 | 9 | 21 | 8 | 10 | 9 | 18 | 15 | **57** | 13 | 19 |
| Aqua 600 ml | 12 | 11 | 9 | 12 | 10 | 15 | 14 | 15 | 14 | 13 | 14 | 6 | 11 | 11 |
| Chitato 14 g | 7 | 7 | 7 | 6 | 4 | 5 | **25** | 4 | 6 | 6 | 4 | 7 | 5 | 9 |
| Garuda Pilus 95 g | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Mixagrip Flu & Batuk | 0 | 2 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 |

- Barang laris laku setiap hari dan naik-turun, akhir pekan sedikit lebih ramai.
- Angka tebal adalah **borongan**: pembeli satu dus mie atau bingkisan snack.
- Barang lambat kebanyakan tidak laku, sesekali beberapa sekaligus. Sekitar separuh barang
  di setiap warung berpola seperti ini, sesuai rak warung yang berisi banyak barang ekor.

**Total penjualan per bulan warung E (dekat kos), dalam ribu barang**

| Okt | Nov | Des | Jan | Feb | Mar | Apr | Mei | Jun | Jul | Agu | Sep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12,8 | 12,6 | 11,0 | **7,8** | 9,7 | 12,7 | 12,6 | 12,8 | 10,4 | **7,7** | 11,1 | 12,1 |

Sepi saat libur semester, karena penghuni kos pulang kampung.

**Rata-rata terjual per hari, beberapa kategori**

| kategori | A gang | B standar | C sekolah | D besar | E kos |
| --- | --- | --- | --- | --- | --- |
| mie instan | 42 | 65 | 46 | 121 | **77** |
| snack | 19 | 61 | **78** | 112 | 52 |
| es krim | 3 | 19 | **33** | 35 | 10 |
| rokok | 21 | 42 | **13** | 65 | 34 |
| minyak goreng | 5 | 10 | 3 | 19 | **2** |

Warung sekolah kuat di jajanan dan lemah di rokok. Warung kos kuat di mie dan nyaris tidak
menjual minyak.

Efek lain yang juga ada di data: siklus gajian yang lemah di sekitar pergantian bulan,
lonjakan alat tulis saat tahun ajaran baru, dan stok yang kadang habis (3 sampai 5 persen
permintaan tidak terlayani, karena pemilik berkulakan tanpa sistem).

---

## 5. Cara kualitas dipastikan

**Tinjauan manual.** Daftar barang, isi rak, dan resep setiap warung ditinjau menyeluruh,
dan kejanggalan diperbaiki. Contohnya: barang kembar, kopi bubuk yang menempati posisi kopi
sachet, kemasan 900 gram yang laku sebanyak sachet, dan barang bayi di warung kos.

**Pemeriksaan otomatis.** Dua belas tes memastikan data sesuai rancangan, seluruhnya lolos:

| yang diperiksa | hasil |
| --- | --- |
| volume penjualan sesuai rancangan | selisih di bawah 2 persen |
| akhir pekan lebih ramai | Sabtu sekitar 15 persen di atas Rabu |
| siklus gajian | ada pada barang mahal, rokok datar |
| libur semester dan libur sekolah | turun sesuai rancangan (60 dan 50 persen) |
| tahun ajaran baru | alat tulis naik lebih dari 50 persen |
| borongan | muncul sesuai frekuensinya |
| stok habis | tidak ada barang yang kosong lebih dari separuh tahun |
| urutan omzet antar warung | sesuai profil |
| barang di data | seluruhnya lolos penilaian |

**Temuan yang sudah diperbaiki lewat pemeriksaan:** 66 barang sempat tidak pernah terjual
karena simulasi stok berhenti memesan barang yang sangat lambat, dan jumlah per pembelian
semula terlalu seragam.

---

## 6. Asumsi yang perlu disetujui

| | asumsi | dampaknya |
| --- | --- | --- |
| ☐ | **Hanya barang dari katalog IPOS.** Telur, gas, galon isi ulang, dan beras kiloan belum termasuk | backend diasumsikan memakai katalog IPOS. Apabila tidak, barang tambahan dapat dimasukkan tanpa mengulang pekerjaan |
| ☐ | **Harga diambil dari backend** lewat kode barang. Data hanya memakai kelas harga | backend perlu menyediakan harga |
| ☐ | **Lima profil warung** (gang, sembako menengah, sekolah, kelontong besar, kos) | apakah sesuai target pasar |
| ☐ | **Periode Oktober 2025 sampai September 2026** | dapat digeser mengikuti tanggal demo |
| ☐ | **Lebaran tidak dimodelkan** | lonjakan menjelang Lebaran dan sepi saat mudik tidak ada di data |

---

## 7. Yang perlu diingat

- **Data ini bukan bukti akurasi model.** Polanya kami rancang sendiri, sehingga model yang
  akurat di data ini belum tentu akurat di warung sungguhan. Angka akurasi dari data ini
  tidak boleh dipakai untuk klaim ke luar.
- Popularitas, patokan penjualan, efek gajian, dan efek libur adalah penilaian dan asumsi.
  Semuanya tercatat dan akan diganti hasil ukur setelah ada data warung asli.
- Beberapa barang laris tidak tersedia versi satuannya di katalog IPOS (Mie Sedaap bungkus,
  kopi sachet Kapal Api dan Torabika).

---

## 8. Pertanyaan yang mungkin muncul

**Kenapa tidak langsung memakai data warung sungguhan?**
Akses ke warung baru tersedia setelah demo. Data sintetis memungkinkan sistem dibangun dan
diuji sekarang, lalu diganti data asli tanpa mengubah alurnya.

**Kenapa tidak memakai seluruh 16.304 kandidat?**
Kandidat masih bercampur barang impor, kemasan kulakan, dan barang bukan warung, sehingga
harus dinilai satu per satu. Warung terbesar hanya butuh 900 jenis, dan kumpulan 1.130
barang hasil penilaian sudah melebihi kebutuhan itu.

**Siapa yang menentukan popularitas dan cocok tidaknya barang?**
Claude (AI), mengikuti satu pedoman tertulis untuk seluruh 2.070 barang, lalu ditinjau
ulang oleh tim. Penilaiannya konsisten antar barang, tetapi tetap berdasarkan pengetahuan
umum, bukan data penjualan. Popularitas akan diganti peringkat penjualan sungguhan setelah
ada data warung asli.

**Seberapa yakin angka penjualannya benar?**
Angkanya konsisten satu sama lain dan dengan kisaran omzet yang disebut pedagang, tetapi
tetap asumsi. Itulah alasan data ini tidak dipakai sebagai bukti akurasi.

**Bisa diubah kalau ada masukan, misalnya menambah warung atau mengganti periode?**
Bisa. Seluruh proses dijalankan ulang dalam sekitar satu menit dengan hasil yang sama persis
setiap kali. Menambah profil warung baru cukup dengan menambah satu profil.

**Kenapa ada stok habis di data?**
Kasir hanya mencatat barang yang benar-benar terjual. Warung tanpa sistem sesekali kehabisan
stok, dan masalah inilah yang ingin diselesaikan Stoqin.

---

## 9. Langkah berikutnya

| langkah | penanggung jawab |
| --- | --- |
| menyepakati bentuk data dengan backend, lalu menulis skrip ekspor | tim AI dan backend |
| membangun layanan forecasting: membaca data, meramal 14 hari, menghitung saran kulakan | tim AI |
| menyambungkan layanan forecasting ke backend | tim AI dan backend |
| demo | |
| mengumpulkan data warung asli dan mengganti asumsi | setelah demo |

**Pertanyaan untuk backend:**

1. Apakah backend memakai katalog IPOS yang sama dengan berkas 50.601 barang ini?
2. Penjualan disimpan per hari atau per transaksi (struk)?
3. Data demo dimasukkan lewat impor CSV, skrip SQL, atau API?
4. Perlu dibuatkan lima toko demo? ID-nya apa?
5. Layanan forecasting membaca data langsung dari database, atau dikirimi data oleh backend?

---

## 10. Yang dibutuhkan dari pertemuan ini

- [ ] Data ini cukup untuk demo
- [ ] Asumsi di bagian 6 disetujui
- [ ] Tanggal demo
- [ ] Penanggung jawab layanan forecasting
- [ ] Kontak di tim backend
