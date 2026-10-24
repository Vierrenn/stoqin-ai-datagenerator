# Katalog SKU warung untuk demo

## Apa ini

`katalog_sku_warung.csv` berisi 60 barang warung sembako beserta identitasnya:
nama, kategori, satuan, harga, lead time supplier, dan periode kulakan.

Semua isinya karangan. Tidak ada satu angka pun yang diambil dari warung
sungguhan, karena Stoqin belum punya akses data warung sampai demo selesai.

## Yang perlu diluruskan sebelum dipakai presentasi

**60 barang itu BUKAN isi sebuah warung.** Warung sembako sungguhan menyimpan
sekitar 200 sampai 800 barang berbeda. Enam puluh baris ini adalah **contoh yang
mewakili rentangnya**, bukan daftar lengkap dan bukan daftar barang terlaris.

Konsekuensinya untuk pengisian angka penjualan (`resep_sintetis.csv`): sebagian
barang harus sengaja diberi angka penjualan yang benar-benar rendah (sebulan laku
2 sampai 4 kali), supaya ekor barang jarang laku tetap terwakili. Kalau semua
barang diisi angka laris, campuran kuadrannya jadi tidak mewakili warung.

Kalau ada penonton demo yang punya warung dan bertanya kenapa barangnya cuma
segini, jawabannya: ini 60 barang contoh, bukan seluruh isi warung.

## Yang sengaja tidak dimasukkan

- **Pulsa, token listrik, bensin eceran.** Ini jasa atau barang tanpa stok yang
  dikelola per unit, jadi tidak ada yang bisa diramalkan maupun direstok.
- **Rokok eceran (jual batangan).** Sangat umum di warung, tapi memunculkan kasus
  satuan jual berbeda dari satuan kulakan (batang vs bungkus). Ditunda sampai
  setelah demo.
- **Sayur dan bumbu segar (bawang, cabai).** Dijual timbangan dan cepat busuk,
  pola permintaannya beda sendiri.

## Kolom yang sengaja tidak ada

`stok_awal` tidak dicantumkan di katalog. Stok awal yang masuk akal selalu
bergantung pada kecepatan laku barang, jadi dia dihitung di simulasi stok
(kira-kira sebanyak kebutuhan selama lead time ditambah periode kulakan,
dilebihkan sedikit), bukan ditebak terpisah.

## Umur pakai

File ini dan `resep_sintetis.csv` dipakai sampai data transaksi warung asli
tersedia. Setelah itu `resep_sintetis.csv` dihapus, dan kuadran tiap barang
dihitung dari penjualan sungguhan lewat `classify_series()`, bukan dideklarasikan.
