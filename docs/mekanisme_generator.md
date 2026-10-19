# Dataset Penjualan Warung Sintetis

Ringkasan apa yang dibuat, bagaimana cara membuatnya, dan sejauh mana hasilnya
dapat dipercaya.

---

## 1. Apa ini, dan apa yang bukan

Satu buku catatan penjualan warung sembako selama satu tahun.

```
60 barang  x  365 hari  =  21.900 baris
kolom: sku_id, tanggal, hari, jumlah terjual
```

**Data ini karangan.** Tidak ada satu angka pun yang berasal dari warung sungguhan,
karena data transaksi warung belum tersedia.

**Karena itu data ini tidak boleh dipakai menilai akurasi model.** Datanya dibuat
sendiri, sehingga nilai akurasi apa pun yang muncul di atasnya hanya menunjukkan
kesesuaian antara karangan kita dan cara kerja model. Bukti akurasi berasal dari
tempat lain, yaitu benchmark 1.437 SKU dataset M5.

Yang bisa ditunjukkan dataset ini cuma satu hal: **bagaimana sistemnya bekerja**,
bukan seberapa akurat sistemnya.

---

## 2. Kenapa tidak menunggu data asli

Karena demo perlu berjalan lebih dulu. Tanpa data, tidak ada yang bisa
diperlihatkan: tidak ada grafik ramalan, tidak ada prediksi stok habis, tidak ada
rekomendasi kulakan.

Prinsip yang dipakai: **targetnya masuk akal, bukan mirip.** Kemiripan sungguhan
baru dikejar setelah ada data pilot.

Satu aturan turunannya: **kalau ragu, pilih yang lebih berantakan.** Kesalahan yang
membuat hasil terlihat lebih buruk dari kenyataan itu aman. Kesalahan yang membuatnya
terlihat lebih bagus itu berbahaya, karena menimbulkan harapan yang nanti dipatahkan
data pilot.

---

## 3. Tiap barang dijelaskan lewat empat pertanyaan

Cara yang salah adalah menumpuk semuanya jadi satu angka rata-rata. Contohnya
"telur laku 6 kg per hari" bisa berarti dua kondisi yang sangat berbeda:

```
laku merata 6 kg tiap hari
laku 2 kg tiap hari, sesekali hajatan memborong 20 kg
```

Angka rata-ratanya sama, tapi bentuk datanya jauh berbeda, dan yang kedua jauh lebih
sulit diramalkan. Karena itu tiap barang dijelaskan lewat empat hal yang berdiri
sendiri:

| variabel | pertanyaan yang dijawab | contoh, galon 19 liter |
| --- | --- | --- |
| **peluang laku** | apakah barang ini laku hari ini | 1,00, laku tiap hari |
| **rentang kuantitas** | kalau laku, totalnya berapa hari itu | 6 sampai 16 galon |
| **peluang borongan** | apakah hari ini ada pembelian besar | 0,04, sekitar 15 kali setahun |
| **rentang borongan** | kalau ada, berapa tambahannya | 5 sampai 10 galon |

Rata-rata harian menjadi **hasil hitungan**, bukan sesuatu yang ditetapkan:

```
1,00 peluang laku     x  titik tengah 6 sampai 16  = 11,00
0,04 peluang borongan x  titik tengah 5 sampai 10  =  0,30
                                             total = 11,30 galon per hari
```

Bisa diperiksa dengan kalkulator. Kalau seseorang merasa 11 galon per hari terlalu
banyak, yang dibantah bukan angka akhirnya, melainkan salah satu dari empat variabel
penyusunnya. Itu jauh lebih mudah didiskusikan.

Dua puluh tiga dari 60 barang punya mekanisme borongan. Obat, produk sachet, dan
barang yang sekali beli tahan lama tidak punya, karena barang seperti itu memang
tidak diborong.

---

## 4. Warungnya juga punya irama

Tiga hal di luar sifat barang ikut menentukan penjualan harian.

**Hari dalam minggu.** Sabtu dan Minggu sedikit lebih ramai, Rabu paling sepi.
Selisihnya tipis, karena orang berbelanja di warung setiap hari, bukan borongan
sekali seminggu.

**Tanggal dalam bulan.** Barang berharga Rp10.000 ke atas naik sekitar 25 persen di
tanggal muda dan turun 20 persen di tanggal tua. Barang murah bergerak berlawanan,
karena menjelang akhir bulan pembeli berpindah ke kemasan sachet.

**Stok yang habis.** Permintaan yang datang saat barang kosong **hilang tanpa
tercatat**, persis seperti di warung sungguhan. Pemilik tidak pernah tahu berapa
pembeli yang batal. Di dataset ini 1,6 persen permintaan hilang karena kekosongan.

---

## 5. Bagaimana angka hariannya dihasilkan

Tiap barang, tiap hari, tiga lemparan dadu:

```
1. apakah laku hari ini          mengikuti peluang laku, disesuaikan irama warung
2. kalau laku, berapa jumlahnya  diambil acak dari rentang kuantitas
3. apakah ada borongan           kalau ya, tambahkan kuantitas borongan
```

Lalu hasilnya dilewatkan simulasi gudang, yang membatasi penjualan sesuai stok yang
ada, mencatat pesanan kulakan, dan menjadwalkan kedatangan barang.

Seluruh proses memakai bilangan acak dengan benih tetap, sehingga **dijalankan
berapa kali pun hasilnya sama persis.** Satu perintah, lima berkas keluar.

---

## 6. Hasilnya seperti apa

Empat barang dengan sifat berbeda, 28 hari pertama.

**Galon 19 liter** (laku tiap hari, volume tinggi)
```
17  9  7 17 21 18 12 16 10  9 13 12 10  7 20 11 13 10  8 10 10 13  7  8  7  9 11  7
tidak pernah kosong, rata-rata 11,5 galon per hari
```

**Royco sachet** (laku tiap hari, tanpa borongan)
```
 5  4  3  7  6  5  6  3  4  7  4  6  5  6  9  6  5  5  8  7 10  4  8  7  8  8  4 10
tidak pernah kosong, rata-rata 6,0 sachet, tidak pernah melonjak jauh
```

**Bodrex** (jarang laku, jumlah kecil)
```
 0  0  0  0  1  0  0  0  0  2  0  1  0  0  2  0  2  0  2  0  1  2  0  0  2  0  0  0
257 hari kosong dari 365, sekali laku cuma 1 atau 2 strip
```

**Susu kental manis kaleng** (jarang laku, sesekali diborong)
```
 2  2  2  2  2  2  2  2  3  6  0  0  0  0  1  0  0  2  2  2  2  0  1  1  0  0  3  2
158 hari kosong, biasanya 1 sampai 3 kaleng, tapi pernah 12 saat ada yang berhajat
```

Empat pola yang jelas berbeda, dan semuanya keluar dari mesin yang sama. Yang
membedakan hanya empat variabel di resep.

---

## 7. Apa yang diperiksa dan apa yang ditemukan

Hasil generate diperiksa dengan membandingkannya ke dataset M5, yaitu 1.437 SKU data
ritel nyata. Perlu ditegaskan: **M5 dipakai memverifikasi, bukan menghasilkan.**

Lima cacat ditemukan lewat pemeriksaan ini, semuanya sudah diperbaiki:

| cacat | akibatnya | perbaikan |
| --- | --- | --- |
| pembulatan satu arah | volume barang lambat naik sampai 26 persen | ditarik langsung sebagai bilangan bulat |
| jadwal kulakan seragam | pola mingguan membengkak 80 persen di atas yang sebenarnya | jadwal disebar antar barang |
| sebaran terlalu memusat | pola permintaan yang melompat nyaris hilang | diganti sebaran seragam |
| stok awal terlalu longgar | bulan-bulan awal sistematis lebih mudah diramal | 90 hari pertama dibuang |
| satu angka menumpuk empat konsep | parameter bertentangan dengan deskripsinya | empat konsep dipisah |

Cacat kedua yang paling berbahaya. Pola hari dalam minggu adalah **penyumbang
keunggulan terbesar model**, jadi membengkakkannya 80 persen akan membuat sistem
terlihat jauh lebih hebat daripada sebenarnya.

Hasil pemeriksaan setelah semua perbaikan:

```
volume yang dihasilkan   +0,4 persen dari target      tidak ada bias sistematis
keacakan harian          0,95 berbanding 1,38 di M5   data kita lebih tenang
```

---

## 8. Keterbatasan yang sudah diketahui

Disebutkan di muka supaya tidak perlu ditemukan sendiri.

**Sepuluh angka irama warung adalah asumsi murni.** Tujuh faktor hari dan tiga faktor
posisi tanggal tidak punya pembanding apa pun. Ini satu-satunya bagian yang begitu,
dan justru bagian yang paling menentukan, karena faktor hari adalah penyumbang
keunggulan terbesar model. **Inilah yang paling layak diukur pertama begitu ada akses
ke warung**, dan cukup dengan tiga pertanyaan ke pemilik warung: hari apa paling
ramai, tanggal berapa paling ramai, dan seberapa jauh bedanya.

**Komposisi pola permintaan menjauh dari data nyata.**

| pola | dataset ini | M5 |
| --- | --- | --- |
| jarang laku, jumlah konsisten | 28 | 58 persen |
| laku tiap hari, jumlah stabil | 23 | 10 persen |
| jarang laku, jumlah melompat | 7 | 27 persen |
| laku tiap hari, jumlah melompat | 2 | 4 persen |

Penyebabnya katalog 60 barang ini tidak memuat ekor panjang warung yang sebenarnya,
yaitu merek kedua dan ketiga tiap kategori serta barang yang jarang dicari.
Menambahkan barang seperti itu akan memperbaiki komposisinya tanpa mengubah perilaku
barang mana pun.

**Data ini lebih tenang daripada data ritel nyata.** Konsekuensi dari memilih
realisme warung di atas kecocokan statistik dengan M5.

**Penjualan rokok hanya mencakup satuan bungkus.** Eceran batangan, yang di warung
Indonesia justru mendominasi, tidak dimodelkan karena satuan jualnya berbeda dari
satuan kulakan.

---

## 9. Umur pakai

Berkas resep dihapus begitu data transaksi warung tersedia. Setelah itu pola
permintaan tiap barang **dihitung dari penjualan sungguhan**, bukan ditetapkan.

Urutan yang disarankan begitu akses warung terbuka:

1. ukur irama warung (hari dan tanggal), karena itu asumsi paling berisiko
2. bandingkan komposisi pola permintaan nyata dengan dataset ini
3. jalankan ulang benchmark model di data pilot
