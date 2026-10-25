# Data Penjualan Sintetis Lima Warung

Dokumen ini menjelaskan cara data penjualan sintetis lima warung dibuat, keputusan yang
diambil di setiap tahap beserta alasannya, hasil pemeriksaannya, dan keterbatasannya.

---

## 0. Ringkasan

| | |
| --- | --- |
| **isi** | penjualan harian setahun untuk lima warung dengan karakter berbeda |
| **periode** | 1 Oktober 2025 sampai 30 September 2026 (365 hari) |
| **barang** | 2.400 pasangan warung dan barang, dari 1.130 jenis barang katalog IPOS |
| **ukuran** | 876.000 baris penjualan harian |
| **omzet per hari** | Rp1,2 juta (warung gang) sampai Rp4,8 juta (kelontong besar) |
| **pemeriksaan** | 12 tes otomatis atas hasil generate, seluruhnya lolos |

Data dibuat agar terasa seperti warung sungguhan: barang laris laku setiap hari, sebagian
besar barang jarang laku, akhir pekan lebih ramai, ada pembelian borongan sesekali, ada
masa sepi saat libur, dan stok kadang habis.

**Peringatan.** Data ini untuk demonstrasi dan pengujian alur sistem. Data ini **tidak
boleh dipakai sebagai bukti akurasi model forecasting**, karena polanya dirancang oleh kami
sendiri. Akurasi baru dapat diukur dengan data warung sungguhan.

---

## 1. Kenapa data sintetis

Akses ke data penjualan warung sungguhan baru tersedia setelah demo. Sementara itu, sistem
forecasting dan tampilan produk perlu data yang realistis untuk dikembangkan dan
didemonstrasikan.

Prinsip yang dipegang selama pembuatan:

1. **Logis dan konsisten.** Setiap angka punya alasan yang dapat dijelaskan, dan angka
   saling konsisten satu sama lain.
2. **Realistis untuk warung Indonesia,** bukan meniru data ritel negara lain.
3. **Mudah diganti.** Setiap asumsi tercatat, sehingga dapat diganti hasil ukur begitu data
   warung sungguhan tersedia.

---

## 2. Daftar barang: dari katalog IPOS ke 1.130 barang

Barang diambil dari katalog aplikasi kasir IPOS berisi 50.601 barang. Katalog ini memuat
banyak barang yang bukan barang warung (kosmetik, perabot, produk impor, kemasan grosir),
sehingga disaring bertahap.

| tahap | jumlah | isi tahap |
| --- | --- | --- |
| katalog IPOS | 50.601 | kode, barcode, nama barang |
| saringan kata kunci | 16.304 | barang yang namanya cocok dengan kamus 22 kategori warung |
| pemilihan per kuota | 1.947 | dipilih per kategori, merek utama didahulukan |
| tambahan | 123 | barang satuan yang terlewat, barang terlaris yang tidak terambil, es krim |
| **lolos klasifikasi** | **1.130** | dinilai cocok dijual di warung |

**Klasifikasi.** Setiap barang terpilih dinilai satu per satu:

| kolom | isi |
| --- | --- |
| kategori | salah satu dari 22 kategori warung |
| satuan dan ukuran | bungkus, sachet, botol, dan sebagainya |
| kelas harga | murah (di bawah Rp5.000), sedang (Rp5.000 sampai Rp15.000), mahal (di atas Rp15.000) |
| popularitas | 1 (jarang dicari) sampai 5 (ada di hampir semua warung, laku setiap hari) |
| cocok warung | ya atau tidak, dengan alasan apabila tidak |

Barang yang tidak lolos antara lain kemasan isi banyak yang dijual eceran oleh pemilik
(renceng sachet, mie isi lima), produk impor, kemasan rumah makan, kosmetik, dan merek yang
sudah tidak beredar. Hasil klasifikasi ditinjau ulang secara menyeluruh, termasuk
pemeriksaan barang kembar, konsistensi kategori, dan kelengkapan barang terlaris.

**Dua keputusan penting:**

- **Hanya barang dari katalog IPOS.** Backend diasumsikan memakai katalog IPOS, sehingga
  barang di luar katalog tidak akan dikenali. Konsekuensinya, barang tanpa barcode yang
  laris di warung (telur, gas, galon isi ulang, beras kiloan) belum termasuk.
- **Harga tidak diperkirakan dalam rupiah.** Harga disediakan backend lewat kode barang.
  Generator hanya memakai kelas harga.

---

## 3. Lima warung

| warung | ciri | barang | keramaian | siklus gajian | libur | jadwal kulakan |
| --- | --- | --- | --- | --- | --- | --- |
| **A** | gang kecil, belanja harian kecil | 250 | 0,6 | lemah, barang mahal | tidak ada | 2 kali lebih sering |
| **B** | sembako menengah, warung standar | 500 | 1,0 | sedang, barang mahal | tidak ada | standar |
| **C** | dekat sekolah | 400 | 0,8 | lemah, barang mahal | libur sekolah | standar |
| **D** | kelontong besar | 900 | 1,5 | sedang, barang mahal | tidak ada | standar |
| **E** | dekat kos atau kampus | 350 | 0,9 | sedang, **semua barang** | libur semester | 2 kali lebih sering |

- **Keramaian:** banyaknya penjualan dibanding warung B.
- **Siklus gajian:** di warung E berlaku untuk semua barang, karena seluruh belanja
  penghuni kos bergantung pada kiriman bulanan. Rokok tidak pernah ikut siklus gajian.
- **Jadwal kulakan:** warung bermodal kecil (A dan E) berbelanja ke grosir lebih sering
  dalam jumlah lebih sedikit.

**Kategori yang ditonjolkan:**

| warung | lebih kuat | lebih lemah |
| --- | --- | --- |
| A | bumbu, mie instan, sabun, deterjen, kopi, minyak, beras dan pokok | alat tulis, es krim, makanan kaleng |
| C | es krim, alat tulis, snack, permen, minuman ringan | rokok, makanan kaleng, deterjen, minyak, beras |
| E | mie instan, kopi, air minum, snack | beras, minyak, bumbu, susu |

Penekanan memperbesar jumlah jenis barang di kategori itu sekaligus volume penjualannya.
Penekanan diseimbangkan per warung, sehingga keramaian keseluruhan tetap sesuai profil.

**Jumlah jenis minimal.** Kategori pokok punya jumlah jenis minimal di warung sekecil apa
pun, misalnya rokok dan bumbu 12, mie instan dan sabun 10, kopi dan es krim 8, minyak dan
air minum 4.

---

## 4. Isi rak

Setiap warung memilih barang per kategori sesuai kuotanya.

- **Separuh kuota diisi barang paling populer.** Barang inti seperti Indomie Goreng, Aqua
  600 ml, dan Sampoerna Mild ada di kelima warung.
- **Separuh sisanya diundi**, dengan peluang sebanding popularitas. Barang ekor berbeda
  antar warung, seperti di kenyataan.
- **Warung kecil (A, C, E) lebih memilih barang murah,** karena jarang menyetok kemasan
  besar.
- **Warung kos jarang menjual barang bayi.**

Barang yang terpilih diberi **peringkat** dalam kategorinya: popularitas tertinggi lebih
dahulu, dan di antara popularitas yang sama, barang lebih murah dan kemasan lebih kecil
lebih dahulu.

Hasilnya, 142 barang ada di kelima warung, sedangkan barang ekor bervariasi.

---

## 5. Resep penjualan

Setiap pasangan warung dan barang punya resep: seberapa sering laku dan berapa banyak.

### 5.1 Rata-rata laku per hari

> **laku per hari = patokan kategori × faktor popularitas dan peringkat × faktor harga × keramaian warung × penekanan kategori**

**Patokan kategori** adalah rata-rata laku barang peringkat 1 di warung B. Angkanya diambil
dari resep 60 barang yang sudah diaudit sebelumnya, lalu diperiksa dengan perkiraan porsi
omzet warung (rokok sekitar sepertiga omzet, jajanan dibeli sangat sering dalam nilai
kecil).

| kategori | barang peringkat 1 | patokan per hari |
| --- | --- | --- |
| mie instan | Indomie Goreng | 15 |
| air minum | Aqua 600 ml | 11 |
| snack | Chocolatos | 9 |
| rokok | Sampoerna Mild 16 | 8 |
| deterjen | Rinso sachet | 8 |
| permen dan coklat | Beng Beng | 7 |
| bumbu | Royco Ayam sachet | 6 |
| teh | Teh Pucuk 350 ml | 5 |

Tabel lengkap 22 kategori ada di Lampiran A.

**Faktor popularitas** menurunkan laju barang lain relatif terhadap peringkat 1:

| popularitas | 5 | 4 | 3 | 2 | 1 |
| --- | --- | --- | --- | --- | --- |
| faktor | 1,00 | 0,55 | 0,25 | 0,10 | 0,04 |

Angka 0,55 untuk popularitas 4 sesuai resep yang sudah diaudit: varian kedua Indomie dan
merek kedua mie laku sekitar separuh barang terlaris. Peringkat memberi penurunan kecil
tambahan agar barang berpopularitas sama tidak laku persis sama.

**Faktor harga.** Barang yang lebih mahal dari barang peringkat 1 di kategorinya laku lebih
sedikit (sedang dibanding murah ×0,5, mahal dibanding murah ×0,28). Tanpa faktor ini,
deterjen kemasan 900 gram akan laku sebanyak sachet Rp1.000.

### 5.2 Pola laku

Rata-rata yang sama dapat terbentuk dari pola yang berbeda. Pola ditentukan oleh pita
laju:

| laju per hari | pola | kalau laku, terjual |
| --- | --- | --- |
| 3 ke atas | setiap hari | setengah sampai satu setengah kali rata-rata |
| 1,5 sampai 3 | hampir setiap hari | 1 sampai 4 atau 5 |
| di bawah 1,5 | tidak setiap hari | biasanya 1, sesekali lebih |

Untuk barang yang tidak laku setiap hari, jumlah per pembelian biasanya 1 tetapi sesekali
beberapa buah sekaligus, misalnya tiga sabun untuk sebulan. Rata-rata per pembelian
berbeda per barang (1,5 sampai 3) dan sama di semua warung, karena cara orang membeli
suatu barang adalah sifat barang itu.

### 5.3 Borongan

Sesekali ada pembeli yang membeli jauh lebih banyak: satu dus mie untuk acara, satu dus
air untuk pengajian, beberapa kilogram gula untuk hajatan.

| kategori | ukuran borongan | peluang per hari |
| --- | --- | --- |
| mie instan | 20 sampai 40 | 4% |
| air minum | 12 sampai 24 | 5% |
| teh | 12 sampai 24 | 3% |
| kopi, bumbu | satu renteng, 10 sampai 12 | 2% |
| susu, beras dan pokok | 4 sampai 10 | 5% |
| minyak goreng | 4 sampai 10 | 3% |
| snack, roti dan biskuit | 4 sampai 12 | 3% |

Aturan pembatas:
- hanya 3 barang teratas per kategori, dengan laju 2 per hari ke atas
- ukuran borongan minimal sebesar penjualan tertinggi hari biasa, agar terasa sebagai
  lonjakan
- ukuran paling banyak 5 kali laju harian, agar tidak ekstrem
- borongan tidak menambah rata-rata, karena bagiannya dikurangkan dari penjualan biasa

Kategori lain (rokok, minuman ringan, permen, es krim, sabun, obat, dan sebagainya) tidak
pernah diborong, karena dibeli untuk dipakai sendiri atau langsung dikonsumsi.

### 5.4 Contoh resep

| warung | barang | laku per hari | pola |
| --- | --- | --- | --- |
| B | Indomie Goreng | 15,0 | setiap hari 7 sampai 21, borongan satu dus sekitar sekali sebulan |
| E | Indomie Goreng | 18,8 | lebih tinggi karena warung kos menonjolkan mie |
| C | Chocolatos | 11,1 | setiap hari, ramai karena dekat sekolah |
| B | Sampoerna Mild 16 | 8,0 | setiap hari 4 sampai 12 bungkus, tanpa borongan |
| B | Gulaku 1 kg | 3,0 | hampir setiap hari, borongan untuk hajatan |
| B | Teh Botol Sosro | 2,3 | hampir setiap hari 1 sampai 4 |
| B | Bimoli 1 L botol | 0,9 | sekitar 3 hari seminggu |
| A | Giv sabun batang | 0,3 | sekitar sekali seminggu, kadang 2 sampai 3 sekaligus |
| D | Surya Slim Merah | 0,2 | sekali tiap 1 sampai 2 minggu |
| D | Johnson's Baby Cologne | 0,05 | sekitar sekali sebulan |

---

## 6. Kalender

Laju harian dikalikan empat efek kalender:

| efek | cara kerja | contoh |
| --- | --- | --- |
| **hari** | sama untuk semua warung | Sabtu ×1,08, Minggu ×1,07, Rabu ×0,93 |
| **gajian** | gelombang bulanan, puncak di pergantian bulan | barang mahal di warung B: tanggal 1 ×1,08, tanggal 15 ×0,92 |
| **libur** | per warung | warung E saat libur semester ×0,60 |
| **tahun ajaran baru** | alat tulis, 5 sampai 18 Juli | ×2,0 |

Untuk barang yang laku setiap hari, efek kalender mengubah **jumlah** yang terjual. Untuk
barang yang tidak laku setiap hari, efek kalender mengubah **seberapa sering** barang itu
laku.

### 6.1 Siklus gajian

> pengali = 1 + kekuatan × cos(2π × (tanggal − 0,5) / jumlah hari bulan itu)

Rata-rata pengali dalam sebulan tepat 1, sehingga total bulanan tidak berubah; yang berubah
hanya sebarannya di dalam bulan.

Efek gajian sengaja dibuat **lemah** (4 sampai 8 persen):

- Studi di luar negeri menemukan konsumsi naik setelah penerimaan pendapatan dan turun
  menjelang akhir siklus, terutama pada rumah tangga tanpa tabungan
  ([Stephens, NBER](https://www.nber.org/system/files/working_papers/w9135/w9135.pdf);
  [Mastrobuoni, Princeton](https://swh.princeton.edu/~ceps/workingpapers/137mastrobuoni.pdf)).
- Di Indonesia sekitar
  [59 persen pekerja bekerja di sektor informal](https://bcasekuritas.co.id/latest-news/news/bps-jumlah-pekerja-informal-alami-penurunan-tipis-per-mei-2026),
  banyak di antaranya berpenghasilan harian.
- Warung umumnya memberi utang (kasbon), yang meratakan belanja sepanjang bulan.
- Gaji di Indonesia umumnya cair tanggal 25 sampai 31 atau tanggal 1, sehingga puncaknya
  diletakkan di pergantian bulan.

### 6.2 Libur

| warung | periode | yang terdampak | penjualan saat libur |
| --- | --- | --- | --- |
| C (sekolah) | 20 Juni sampai 12 Juli, 20 Desember sampai 4 Januari | snack, permen, es krim, alat tulis, minuman ringan | 50%, langsung |
| E (kos) | 15 Juni sampai 10 Agustus, 20 Desember sampai 10 Februari | semua kategori | 60%, turun dan naik bertahap selama 7 hari |

Libur berarti warung lebih sepi, bukan tutup.

---

## 7. Simulasi stok

Resep menghasilkan **permintaan**, yaitu yang ingin dibeli pembeli. Kasir hanya mencatat
yang benar-benar terjual. Apabila stok habis, sisa permintaan hilang dan tidak tercatat di
mana pun. Simulasi stok meniru hal ini.

**Cara pemilik simulasi berkulakan:**

1. Pada setiap jadwal kulakan, pemilik melihat rata-rata penjualan 4 minggu terakhir.
2. Ia memesan agar stok cukup sampai kulakan berikutnya, ditambah cadangan 30 persen.
3. Barang datang beberapa hari kemudian sesuai waktu tunggu kategori.

Pemilik **tidak memakai ramalan** dan **tidak mengetahui pembeli yang batal** karena stok
habis. Data ini menggambarkan warung sebelum memakai sistem, sehingga kebiasaan yang
membuat warung sering kehabisan stok ikut tergambar.

**Jadwal kulakan per kategori** (warung B, C, D; warung A dan E dua kali lebih sering):

| kategori | kulakan tiap | barang datang setelah |
| --- | --- | --- |
| mie, air, minyak, beras dan pokok, rokok | 7 hari | 2 hari |
| es krim | 7 hari | 3 hari |
| bumbu, kopi, teh, minuman ringan | 14 hari | 3 hari |
| snack, roti, susu, permen, sabun, gigi, deterjen, pembalut | 14 hari | 4 hari |
| rumah tangga, makanan kaleng | 30 hari | 5 hari |
| obat, alat tulis | 30 hari | 7 hari |

Barang laris selalu ikut dipesan, sedangkan barang lambat hanya dipesan saat stoknya
kurang. Jadwal kulakan antar barang disebar agar tidak semua datang di hari yang sama.

**Stok minimal.** Pemilik selalu menyimpan beberapa buah barang yang ia jual, yaitu tiga
kali rata-rata per pembelian dan paling sedikit dua buah. Tanpa aturan ini, barang sangat
lambat yang sempat habis tidak pernah dipesan lagi.

**Pemanasan.** Simulasi dijalankan 90 hari lebih awal (mulai 3 Juli 2025) agar stok dan
jadwal kulakan sudah stabil saat data mulai direkam. Data pemanasan dibuang dan tidak
dipakai di mana pun.

---

## 8. Hasil dan pemeriksaan

### 8.1 Angka per warung

| warung | terjual per hari | omzet per hari | permintaan hilang karena stok habis |
| --- | --- | --- | --- |
| A gang | 231 | Rp1,24 juta | 4,6% |
| B standar | 498 | Rp2,68 juta | 3,5% |
| C sekolah | 390 | Rp1,39 juta | 4,2% |
| D besar | 890 | Rp4,78 juta | 3,1% |
| E kos | 365 | Rp1,82 juta | 4,7% |

Omzet dihitung dengan harga wakil per kelas (murah Rp2.000, sedang Rp8.000, mahal
Rp25.000, rokok Rp27.000), hanya sebagai perkiraan kasar.

### 8.2 Komposisi pola penjualan

Penggolongan menurut seberapa sering barang laku (ADI) dan seberapa naik-turun jumlahnya
(CV²):

| warung | smooth | erratic | intermittent | lumpy |
| --- | --- | --- | --- | --- |
| A | 12% | 2% | 74% | 13% |
| B | 19% | 1% | 67% | 12% |
| C | 17% | 2% | 71% | 11% |
| D | 17% | 0% | 70% | 13% |
| E | 15% | 1% | 76% | 7% |

Sebagian besar barang berpola intermittent (jarang laku), sesuai rak warung yang berisi
banyak barang ekor. Keempat pola tersedia, sehingga model forecasting dapat diuji pada
semua jenis pola.

### 8.3 Tes otomatis

Seluruh tes di `tests/test_5warung.py` lolos:

| tes | yang dipastikan |
| --- | --- |
| jumlah barang dan periode | sesuai profil, tepat 365 hari |
| barang lolos klasifikasi | tidak ada barang yang dibuang ikut masuk |
| permintaan sesuai resep | selisih di bawah 2 persen setelah efek kalender |
| efek hari | Sabtu lebih ramai dari Rabu lebih dari 8 persen |
| efek gajian | barang yang ikut gajian lebih laku di pergantian bulan; rokok datar |
| libur semester | penjualan warung E saat libur sekitar 60 persen |
| libur sekolah | jajanan warung C turun separuh, kategori lain tetap |
| tahun ajaran baru | alat tulis naik lebih dari 50 persen |
| borongan | frekuensi lonjakan sesuai peluangnya |
| stok kosong | tidak ada barang kosong lebih dari separuh tahun, permintaan hilang di bawah 8 persen |
| komposisi pola | intermittent dan lumpy 60 sampai 90 persen, lumpy minimal 5 persen |
| urutan omzet | A < C < E < B < D |

### 8.4 Temuan pemeriksaan yang sudah diperbaiki

- **Barang lambat tidak pernah distok ulang.** Sebelum aturan stok minimal, 66 barang tidak
  pernah terjual sepanjang tahun karena pesanannya selalu dibulatkan ke nol.
- **Jumlah per pembelian terlalu seragam.** Sebaran 1 sampai 2 dengan peluang sama hampir
  tidak menghasilkan pola lumpy. Sebaran "biasanya 1, sesekali lebih" menaikkan porsi
  lumpy dari 2 sampai 6 persen menjadi 7 sampai 13 persen.
- **Barang peringkat 1 kadang tidak tepat** (kopi bubuk mengalahkan kopi sachet, tepung
  mengalahkan gula). Diperbaiki dengan urutan barang murah dan kemasan kecil lebih dahulu.

---

## 9. Keterbatasan dan asumsi

| keterbatasan | dampak |
| --- | --- |
| barang tanpa barcode (telur, gas, galon, beras kiloan, minyak curah) tidak termasuk | omzet lebih kecil dari warung sungguhan |
| versi satuan beberapa barang laris tidak ada di IPOS (Mie Sedaap bungkus, kopi sachet Kapal Api dan Torabika) | kategori kopi lebih sedikit jenisnya |
| katalog IPOS sudah lama | sebagian merek baru tidak ada, sebagian merek lama mungkin sudah tidak beredar |
| popularitas dan kelas harga adalah penilaian | bukan data penjualan atau harga nyata |
| patokan per kategori adalah penilaian | konsisten satu sama lain, tetapi belum diukur |
| siklus gajian, libur, dan tahun ajaran baru adalah asumsi | besarnya perlu diukur dari data asli |
| Lebaran tidak dimodelkan | lonjakan menjelang Lebaran dan sepi saat mudik tidak ada |
| rokok eceran per batang tidak dimodelkan | penjualan rokok dinyatakan dalam bungkus |
| harga per kelas hanya wakil | omzet adalah perkiraan kasar |
| pemilik simulasi berkulakan dengan aturan sederhana | pola stok habis bergantung pada aturan itu |

---

## 10. Berkas keluaran dan cara menjalankan ulang

### 10.1 Struktur folder `data/`

Folder `data/` berisi tiga kelompok: bahan 60 SKU lama, bahan dari katalog IPOS, dan hasil
generate. Alurnya mengalir dari atas ke bawah:

```
data/
├── katalog_sku_warung.csv        60 SKU lama: identitas barang, harga, jadwal kulakan
├── resep_sintetis.csv            60 SKU lama: resep yang diaudit tangan
├── README_katalog.md             penjelasan kolom dua berkas di atas
│
├── demo/                         HASIL generate 60 SKU lama
│   ├── penjualan_harian.csv
│   ├── stok_harian.csv
│   ├── snapshot_stok.csv
│   └── tinjauan/                 tabel lebar untuk Excel
│
├── induk/                        BAHAN dari katalog IPOS (tahap 1 sampai 3)
│   ├── IPOS 5 DATABASE ....xls   sumber asli, 50.601 barang
│   ├── katalog_induk.csv         sumber asli dalam bentuk CSV ringkas
│   ├── kandidat.csv              lolos saringan kata kunci, 16.304 barang
│   ├── terpilih.csv              hasil pemilihan per kuota, 1.947 barang
│   ├── potongan/                 barang yang perlu diklasifikasikan, dipecah per 500
│   ├── klasifikasi/              ★ hasil penilaian manual per potongan
│   ├── klasifikasi.csv           gabungan barang lolos, 1.130 barang
│   └── tinjauan_klasifikasi.md   versi tabel untuk dibaca, termasuk alasan barang dibuang
│
└── demo_5warung/                 HASIL lima warung (tahap 5 sampai 8)
    ├── assortment.csv            isi rak kelima warung, 2.400 baris
    ├── rak/                      isi rak per warung, CSV dan Markdown
    ├── resep.csv                 resep penjualan per pasangan warung dan barang
    ├── resep/                    resep per warung dalam Markdown
    ├── penjualan_harian.csv      ★ data penjualan, satu-satunya yang dibaca model
    ├── stok_harian.csv           detail simulasi stok, untuk pemeriksaan
    ├── snapshot_stok.csv         stok di hari terakhir
    ├── katalog_warung.csv        daftar barang per warung
    ├── tinjauan/                 tabel lebar barang × hari dan barang × bulan, untuk Excel
    └── ringkasan/                ringkasan per warung dalam Markdown
```

Penjelasan per bagian:

| bagian | jenis | dibuat oleh | di git? | kalau terhapus |
| --- | --- | --- | --- | --- |
| `katalog_sku_warung.csv`, `resep_sintetis.csv` | bahan tangan | ditulis manual | ya | ambil dari git |
| `demo/` | hasil 60 SKU | `run_generate.py` | tidak | jalankan ulang, sekitar 3 detik |
| `induk/IPOS ... .xls` | sumber pihak ketiga | diberikan atasan | tidak, 23 MB | minta ulang berkasnya |
| `induk/katalog_induk.csv`, `kandidat.csv`, `terpilih.csv`, `potongan/` | antara | `katalog_induk`, `saring`, `potongan`, `tambahan` | tidak | jalankan ulang dari berkas IPOS |
| **`induk/klasifikasi/`** | **penilaian manual** | dinilai satu per satu | **tidak (sebaiknya ya)** | **tidak dapat dibuat ulang dari kode** |
| `induk/klasifikasi.csv`, `tinjauan_klasifikasi.md` | gabungan | `gabung_klasifikasi` | tidak | jalankan ulang |
| `demo_5warung/` | hasil lima warung | `assortment`, `resep_otomatis`, `run_generate_5warung`, `ringkasan_5warung` | tidak | jalankan ulang, sekitar 1 menit |

Cara memakai folder ini:

- **Ingin melihat hasilnya:** buka `demo_5warung/ringkasan/`.
- **Ingin menyerahkan data ke backend atau model:** `demo_5warung/penjualan_harian.csv`,
  ditambah `snapshot_stok.csv` dan `katalog_warung.csv`.
- **Ingin memeriksa barang apa saja yang dipakai dan kenapa:** `induk/tinjauan_klasifikasi.md`
  dan `demo_5warung/rak/`.
- **Ingin memahami kenapa suatu barang laku sekian:** `demo_5warung/resep/`.

### 10.2 Berkas di `data/demo_5warung/`

| berkas | kolom | keterangan |
| --- | --- | --- |
| `penjualan_harian.csv` | store_id, kode, date, weekday, qty | **satu-satunya berkas yang dibaca model.** Hari tanpa penjualan tetap ditulis dengan qty 0 |
| `stok_harian.csv` | store_id, kode, date, permintaan, stok_awal, datang, terjual, kehilangan, stok_akhir, dipesan, dalam_perjalanan | untuk pemeriksaan. Kolom permintaan dan kehilangan tidak dapat diamati di warung nyata dan tidak boleh dibaca komponen produk |
| `snapshot_stok.csv` | store_id, kode, tanggal, current_stock, incoming_stock | posisi stok di hari terakhir |
| `katalog_warung.csv` | store_id, kode, nama, kategori, satuan, kelas_harga, popularitas, peringkat | barang per warung |
| `resep.csv` | parameter resep per pasangan warung dan barang | |
| `tinjauan/` | tabel lebar barang × hari dan barang × bulan | untuk dibuka di Excel |
| `ringkasan/` | ringkasan Markdown per warung | untuk peninjauan cepat |

Kode barang selalu berupa teks; angka nol di depan tidak boleh hilang.

### 10.3 Urutan perintah

```
python -m datagen.katalog_induk       # katalog IPOS ke CSV
python -m datagen.saring              # saringan kata kunci
python -m datagen.potongan            # pemilihan per kuota
                                      # (klasifikasi dikerjakan manual per potongan)
python -m datagen.tambahan            # barang tambahan
python -m datagen.gabung_klasifikasi  # gabung dan validasi klasifikasi
python -m datagen.assortment          # isi rak tiap warung
python -m datagen.resep_otomatis      # resep penjualan
python run_generate_5warung.py        # generate data (sekitar 30 detik)
python -m datagen.ringkasan_5warung   # ringkasan per warung
python -m pytest tests/               # pemeriksaan
```

Setiap tahap memakai seed tetap, sehingga menjalankan ulang menghasilkan data yang sama
persis. Periode data diatur di `run_generate_5warung.py` dan dapat digeser apabila tanggal
demo berubah.

**Ketergantungan penting:** hasil klasifikasi di `data/induk/klasifikasi/` adalah penilaian
manual dan tidak dapat dibangkitkan ulang dari kode. Folder ini perlu disimpan, idealnya di
git.

---

## 11. Setelah demo: yang diukur dari data asli

Begitu data penjualan warung sungguhan tersedia, asumsi berikut diganti hasil ukur:

| asumsi | cara mengukur |
| --- | --- |
| patokan per kategori | rata-rata laku barang terlaris tiap kategori |
| kurva popularitas | perbandingan laku barang peringkat 2, 3, dan seterusnya terhadap peringkat 1 |
| efek hari | rata-rata penjualan per hari dalam minggu |
| siklus gajian | rata-rata penjualan per tanggal 1 sampai 31, digabung per kategori (bukan per barang), setelah pengaruh hari dipisahkan |
| libur dan musim | perbandingan penjualan masa libur terhadap bulan biasa |
| borongan | seberapa sering dan seberapa besar lonjakan pada barang terlaris |
| pola stok habis | seberapa sering barang habis dan berapa lama sampai tersedia lagi |

---

## Lampiran A. Patokan per kategori

| kategori | patokan | | kategori | patokan |
| --- | --- | --- | --- | --- |
| mie instan | 15 | | es krim | 3 |
| air minum | 11 | | minuman ringan | 3 |
| snack | 9 | | susu | 3 |
| rokok | 8 | | minyak goreng | 2,7 |
| deterjen dan pembersih | 8 | | obat warung | 2 |
| permen dan coklat | 7 | | rumah tangga | 2 |
| bumbu | 6 | | perawatan gigi | 1,5 |
| teh | 5 | | alat tulis | 1 |
| roti dan biskuit | 4 | | pembalut dan bayi | 0,8 |
| kopi | 4 | | makanan kaleng | 0,6 |
| beras dan pokok | 3 | | | |
| sabun dan sampo | 3 | | | |

## Lampiran B. Porsi rak dasar dan penekanan per warung

| kategori | porsi dasar | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- | --- |
| snack | 8% | ×0,8 | ×1,0 | ×1,6 | ×1,0 | ×1,3 |
| sabun dan sampo | 7% | ×1,2 | ×1,0 | ×1,0 | ×1,0 | ×1,2 |
| roti dan biskuit | 7% | ×0,8 | ×1,0 | ×1,2 | ×1,0 | ×1,0 |
| bumbu | 8% | ×1,3 | ×1,0 | ×0,7 | ×1,0 | ×0,6 |
| permen dan coklat | 5% | ×0,8 | ×1,0 | ×1,6 | ×1,0 | ×1,0 |
| minuman ringan | 6% | ×1,0 | ×1,0 | ×1,4 | ×1,0 | ×1,2 |
| susu | 5% | ×1,0 | ×1,0 | ×1,2 | ×1,0 | ×0,7 |
| kopi | 5% | ×1,2 | ×1,0 | ×0,7 | ×1,0 | ×1,4 |
| mie instan | 5% | ×1,3 | ×1,0 | ×1,0 | ×1,0 | ×1,6 |
| deterjen dan pembersih | 5% | ×1,2 | ×1,0 | ×0,6 | ×1,0 | ×1,0 |
| rokok | 7% | ×1,0 | ×1,0 | ×0,5 | ×1,0 | ×1,2 |
| pembalut dan bayi | 4% | ×1,0 | ×1,0 | ×0,7 | ×1,0 | ×0,8 |
| obat warung | 4% | ×0,8 | ×1,0 | ×0,8 | ×1,0 | ×1,0 |
| rumah tangga | 4% | ×1,0 | ×1,0 | ×1,0 | ×1,0 | ×1,0 |
| teh | 3% | ×1,0 | ×1,0 | ×1,2 | ×1,0 | ×1,1 |
| perawatan gigi | 3% | ×1,0 | ×1,0 | ×1,0 | ×1,0 | ×1,2 |
| beras dan pokok | 3% | ×1,2 | ×1,0 | ×0,6 | ×1,0 | ×0,5 |
| alat tulis | 2% | ×0,5 | ×1,0 | ×2,0 | ×1,0 | ×1,2 |
| air minum | 2% | ×1,0 | ×1,0 | ×1,0 | ×1,0 | ×1,4 |
| minyak goreng | 2% | ×1,2 | ×1,0 | ×0,6 | ×1,0 | ×0,5 |
| makanan kaleng | 2% | ×0,7 | ×1,0 | ×0,5 | ×1,0 | ×0,8 |
| es krim | 3% | ×0,5 | ×1,0 | ×2,0 | ×1,0 | ×1,0 |
