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

## Langkah 4: Profil lima warung ✅

Lima profil (A gang, B standar, C sekolah, D besar, E kos) dengan jumlah barang,
keramaian, kekuatan gajian, penekanan kategori, jumlah jenis minimal per kategori, masa
libur (C libur sekolah, E libur semester bertahap), musim tahun ajaran baru untuk alat
tulis, dan jadwal kulakan (A dan E dua kali lebih sering).

- Kode: `datagen/profil_warung.py`

## Langkah 5: Isi rak tiap warung ✅

Separuh kuota tiap kategori diisi barang dengan bobot tertinggi, separuh sisanya diundi
sebanding bobot. Peringkat dalam kategori: popularitas, lalu barang lebih murah dan
kemasan lebih kecil.

- Hasil: `data/demo_5warung/assortment.csv`, `rak/rak_X.md`
- Kode: `datagen/assortment.py`

## Langkah 6: Resep otomatis ✅

Laju harian = patokan kategori × faktor popularitas dan peringkat × faktor harga ×
keramaian × penekanan yang dinormalkan. Pola laku per pita laju, sebaran "biasanya 1,
sesekali lebih" untuk barang yang tidak laku setiap hari, borongan untuk tiga barang
teratas di sepuluh kategori, dan stok minimal per barang.

- Hasil: `data/demo_5warung/resep.csv`, `resep/resep_X.md`
- Kode: `datagen/resep_otomatis.py`

## Langkah 7: Pembangkitan data ✅

Periode 1 Oktober 2025 sampai 30 September 2026, pemanasan 90 hari dibuang. Pengali
kalender (hari, gajian, libur, tahun ajaran baru) dihitung per barang. Waktu jalan sekitar
30 detik. Pipeline 60 SKU tetap menghasilkan data yang identik.

- Hasil: `penjualan_harian.csv`, `stok_harian.csv`, `snapshot_stok.csv`,
  `katalog_warung.csv`, `tinjauan/`, `ringkasan/`
- Kode: `datagen/kalender_warung.py`, `run_generate_5warung.py`,
  `datagen/ringkasan_5warung.py`

## Langkah 8: Pemeriksaan otomatis ✅

Dua belas tes atas hasil generate, seluruhnya lolos. Pemeriksaan menemukan dan
memperbaiki dua masalah: barang lambat yang tidak pernah distok ulang (diperbaiki dengan
stok minimal) dan jumlah per pembelian yang terlalu seragam (diperbaiki dengan sebaran
geometrik).

- Kode: `tests/test_5warung.py`

## Langkah 9: Dokumentasi ✅

- `docs/data_sintetis_5warung.md`: penjelasan lengkap untuk CTO dan tim, termasuk
  keterbatasan dan rencana pengukuran setelah demo

## Setelah selesai

1. Commit dan push.
2. Konfirmasi ke tim backend apakah katalog yang dipakai sama dengan berkas IPOS ini.
   Apabila backend dapat menerima barang tambahan, barang tanpa barcode dapat
   ditambahkan tanpa mengulang langkah sebelumnya.
