# Rencana Data Sintetis Lima Warung

Ringkasan tahapan pembuatan data penjualan sintetis untuk lima warung dengan barang
dari katalog IPOS. Setiap langkah memuat tujuan, cara kerja, hasil, dan statusnya.

## Gambaran besar

```
katalog IPOS 50.601 barang
  -> saring dan pilih            (Langkah 1-2)
  -> klasifikasi barang          (Langkah 3)    -> 1.130 barang lolos
  -> profil dan isi rak warung   (Langkah 4-5)
  -> resep dan pembangkitan      (Langkah 6-7)  -> penjualan harian lima warung
  -> pemeriksaan dan dokumentasi (Langkah 8-9)
```

## Keputusan yang sudah diambil

- **Hanya barang IPOS.** Backend diasumsikan memakai katalog IPOS, sehingga barang di
  luar katalog (telur, gas, galon, beras kiloan, minyak curah) tidak dimasukkan.
  Asumsi ini dikonfirmasi ke tim backend setelah data selesai.
- **Harga dalam rupiah tidak diperkirakan.** Harga disediakan backend lewat kode
  barang. Generator hanya memakai kelas harga (murah, sedang, mahal).
- **Siklus gajian lemah.** Puncak di sekitar tanggal 25 sampai 5, kekuatan 4 sampai 8
  persen, hanya untuk barang mahal selain rokok. Dasar dan cara mengukurnya ada di
  bagian keterbatasan.
- **Kemasan isi banyak yang disobek pemilik warung tidak dipakai,** karena pembeli
  membeli satuannya, bukan kemasan kulakan.

---

## Langkah 1: Muat katalog induk ✅

Membaca berkas IPOS dan menyimpan kode, barcode, dan nama barang. Kolom lain (harga,
merek, satuan) kosong atau seragam di berkas sumber sehingga tidak dipakai.

- Hasil: `data/induk/katalog_induk.csv`, 50.601 barang
- Kode: `datagen/katalog_induk.py`

## Langkah 2: Saring dan pilih kandidat ✅

Katalog IPOS memuat banyak barang bukan warung (kosmetik, perabot, produk impor).
Kamus kata kunci menyaring barang yang mungkin dijual warung dan memberi kategori kasar.
Dari kandidat itu dipilih barang per kategori dengan kuota, merek inti didahulukan,
sisanya acak.

- Hasil: `kandidat.csv` (16.304 barang), `terpilih.csv` (1.947 barang)
- Kode: `datagen/saring.py`, `datagen/potongan.py`

## Langkah 3: Klasifikasi barang ✅

Setiap barang terpilih dinilai: kategori sebenarnya, satuan, ukuran, kelas harga,
popularitas (1 sampai 5), cocok warung atau tidak, dan tingkat keyakinan. Barang yang
dibuang diberi alasan. Tiga putaran tambahan menutup kekurangan: barang satuan yang
terlewat dan kategori yang kurang, barang terlaris warung yang tidak terambil acak, dan
es krim satuan karena kuota awalnya terlalu kecil dibanding isi freezer warung.
Seluruh hasil sudah ditinjau ulang.

- Hasil: `data/induk/klasifikasi.csv`, 1.130 barang lolos
- Tinjauan: `data/induk/tinjauan_klasifikasi.md`
- Pedoman: `docs/pedoman_klasifikasi.md`
- Kode: `datagen/tambahan.py`, `datagen/gabung_klasifikasi.py`
- Catatan: kopi (31 barang) dan air minum (16 barang) di bawah kebutuhan warung
  terbesar, karena versi satuannya memang sedikit di IPOS

## Langkah 4: Profil lima warung

Menentukan ciri tiap warung agar datanya berbeda satu sama lain.

| warung | ciri | barang | keramaian | gajian |
| --- | --- | --- | --- | --- |
| A | gang kecil, belanja harian kecil | 250 | 0,6 | 0,04 |
| B | sembako menengah, warung standar | 500 | 1,0 | 0,08 |
| C | dekat sekolah, sepi saat libur sekolah | 400 | 0,8 | 0,04 |
| D | kelontong besar, barang paling beragam | 900 | 1,5 | 0,08 |
| E | dekat kos atau kampus, sepi saat libur semester | 350 | 0,9 | 0,08, semua barang |

Setiap profil juga menentukan kategori yang ditonjolkan (misalnya snack dan alat tulis
di C, mie instan dan kopi di E). Porsi rak dasar memberi rokok dan es krim porsi lebih
besar daripada tahap pemilihan kandidat, dan kategori pokok punya jumlah jenis minimal
untuk warung sekecil apa pun (rokok dan bumbu 12, mie instan dan sabun 10, kopi,
deterjen, dan es krim 8, obat 6, beras dan pokok, teh, dan perawatan gigi 5, minyak
dan air minum 4). Kategori yang barangnya kurang diambil semua, lalu sisa kuotanya
dibagi ke kategori lain.

Siklus gajian umumnya hanya berlaku untuk barang mahal. Di warung E berlaku untuk semua
barang kecuali rokok, karena seluruh belanja penghuni kos bergantung pada kiriman
bulanan. Masa libur: warung C pada libur sekolah (kategori jajanan anak turun separuh),
warung E pada libur semester 15 Juni sampai 10 Agustus dan 20 Desember sampai
10 Februari (seluruh kategori turun menjadi 60 persen, bertahap selama 7 hari di awal
dan di akhir libur karena penghuni kos tidak pulang dan kembali serentak).

- Hasil: `datagen/profil_warung.py` ✅
- Efek Lebaran tidak dimodelkan dan dicatat sebagai keterbatasan

## Langkah 5: Isi rak tiap warung

Memilih barang yang dijual di setiap warung dari 1.130 barang lolos, sesuai kuota
kategori profilnya. Separuh kuota tiap kategori diisi barang dengan bobot tertinggi agar
barang inti tidak terlewat; separuh sisanya diundi sebanding bobot sehingga tiap warung
punya barang ekor yang berbeda. Bobot berasal dari popularitas (5: 100, 4: 30, 3: 8,
2: 3, 1: 1), preferensi warung kecil (A, C, E) terhadap barang murah (murah 1,5, mahal
0,5), dan penyesuaian per profil: barang bayi di warung kos berbobot 0,2.

- Hasil: `data/demo_5warung/assortment.csv`, serta `rak/rak_X.csv` dan `rak/rak_X.md`
  per warung
- Kode: `datagen/assortment.py`

## Langkah 6: Resep otomatis

Menentukan seberapa sering dan seberapa banyak setiap barang laku di setiap warung,
memakai empat variabel yang sama dengan generator 60 SKU (peluang laku, rentang
kuantitas, peluang borongan, rentang borongan). Dasarnya:

1. pola kategori, dikalibrasi dari 60 SKU yang sudah diaudit
2. peringkat barang di kategorinya: peringkat atas laku setiap hari, peringkat bawah jarang
3. keramaian dan kategori yang ditonjolkan di profil warung

Langkah ini juga menentukan barang yang ikut siklus gajian, waktu tunggu kulakan, dan
jadwal kulakan.

- Hasil: `data/demo_5warung/resep.csv`, sekitar 2.400 pasangan warung dan barang
- Perlu persetujuan: pola per kategori sebelum ditulis

## Langkah 7: Pembangkitan data

Membangkitkan permintaan harian setahun untuk setiap warung, lalu menjalankan simulasi
stok (stok habis, kulakan, pemanasan 90 hari) seperti generator 60 SKU. Apabila terlalu
lambat untuk sekitar 2.400 barang, perhitungannya dipercepat tanpa mengubah hasil
statistiknya.

- Hasil di `data/demo_5warung/`:
  - `penjualan_harian.csv` (warung, kode, tanggal, hari, jumlah), satu-satunya berkas
    yang dibaca model
  - `stok_harian.csv`, `snapshot_stok.csv`, `katalog_warung.csv`
- Dijalankan sendiri: `python run_generate_5warung.py`

## Langkah 8: Pemeriksaan otomatis

Tes yang memastikan data masuk akal tanpa pemeriksaan manual per barang:

- volume penjualan sesuai resep
- komposisi pola laku (rutin, jarang, borongan) per warung wajar; warung D punya
  barang jarang laku terbanyak
- urutan omzet antar warung wajar
- efek gajian terukur kembali sesuai rancangan; rokok dan barang murah datar
- tidak ada barang yang dibuang ikut masuk

Setelah tes lolos, data ditinjau dalam tampilan lebar per warung seperti putaran 60 SKU.

- Hasil: `tests/test_5warung.py`
- Dijalankan sendiri: `python -m pytest`

## Langkah 9: Dokumentasi

Memperbarui `docs/mekanisme_generator.md` dalam gaya presentasi: katalog induk,
klasifikasi, lima profil, cara data dibuat, dan keterbatasan.

---

## Keterbatasan yang akan dicatat

- Hanya barang berbarcode dari IPOS; barang tanpa barcode yang laris di warung belum
  termasuk.
- Katalog IPOS sudah lama: sebagian merek baru tidak ada, beberapa merek lama mungkin
  sudah tidak beredar.
- Popularitas dan kelas harga adalah penilaian, bukan data penjualan atau harga nyata.
- Siklus gajian dan libur sekolah adalah asumsi. Setelah data warung asli tersedia,
  efek per tanggal diukur per kategori (bukan per barang), setelah pengaruh hari
  dipisahkan, lalu angka asumsi diganti hasil ukur.

## Setelah selesai

1. Commit dan push.
2. Konfirmasi ke tim backend apakah katalog yang dipakai sama dengan berkas IPOS ini.
   Apabila backend dapat menerima barang tambahan, barang tanpa barcode dapat
   ditambahkan tanpa mengulang langkah sebelumnya.
