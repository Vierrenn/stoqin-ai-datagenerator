# stoqin-ai-datagenerator

Alat internal untuk membuat data penjualan warung **buatan**, dipakai sebagai
panggung demo sampai Stoqin punya data transaksi warung sungguhan.

Repo ini tidak pernah di-deploy ke mana pun. Dia cuma jalan di laptop.

## Yang harus dipahami sebelum memakai hasilnya

**Data dari sini tidak bisa dipakai sebagai bukti akurasi model.** Datanya kita
sendiri yang mengarang, jadi kalau model dapat nilai bagus di situ, itu cuma
berarti karangan kita kebetulan cocok dengan cara kerja modelnya.

Bukti akurasi tetap datang dari `stoqin-ai-experiment` (benchmark 1.437 SKU data
M5 nyata). Data dari repo ini cuma boleh dipakai untuk memperlihatkan **bagaimana
sistemnya bekerja**, bukan **seberapa akurat sistemnya**.

## Prinsip yang dipegang

1. **Targetnya masuk akal, bukan mirip.** Kemiripan sungguhan baru dikejar setelah
   ada data warung asli. Sekarang cukup logis.
2. **Kalau ragu, pilih yang lebih berantakan.** Salah yang bikin demo terlihat
   lebih jelek dari kenyataan itu aman. Salah yang bikin demo terlihat lebih bagus
   itu berbahaya, karena penonton menaruh ekspektasi di situ lalu data pilot
   menghancurkannya. Makanya stok habis, pergeseran level, dan lonjakan Ramadan
   tetap dipertahankan walau menurunkan angka model.
3. **Model tidak boleh melihat resepnya.** Yang boleh dibaca model cuma buku
   penjualan hasil generate. Kalau model diberi tahu barang mana yang ikut siklus
   tanggal muda, seluruh pengujian jadi tidak ada artinya.

## Ketergantungan

Repo ini memanggil `stoqin-ai` untuk memeriksa hasilnya sendiri. Pemeriksaan
kuadran harus memakai `classify_series()` **versi produksi**, bukan salinan
sendiri, supaya pemeriksaannya berarti.

Pasang sekali saja:

```
pip install -e ../stoqin-ai
pip install -r requirements.txt
```

## Isi

```
data/
  katalog_sku_warung.csv   60 barang: nama, harga, lead time, periode kulakan
  resep_sintetis.csv       60 resep: unit per hari, lompat-lompat atau tidak
  README_katalog.md        batasan katalog ini
```

Yang belum ada: `datagen/synthetic.py` (generator), `datagen/stock_sim.py`
(simulasi stok), dan pengujian kemiripan.

## Umur pakai

Begitu data transaksi warung asli tersedia, repo ini **dihapus**, dan kuadran tiap
barang dihitung dari penjualan sungguhan, bukan dideklarasikan di `resep_sintetis.csv`.
