# Pedoman Klasifikasi Barang

Acuan untuk mengklasifikasikan barang terpilih dari katalog induk IPOS. Dipakai
pada setiap potongan agar penilaian tetap konsisten walaupun dikerjakan bertahap.

## Tujuan

Katalog IPOS hanya memuat kode, barcode, dan nama barang. Klasifikasi menambahkan
informasi yang dibutuhkan generator: apakah barang lazim dijual warung, kategori
sebenarnya, satuan dan ukuran, kelas harga, popularitas, dan tingkat keyakinan
atas penilaian tersebut.

Seluruh nilai merupakan penilaian berdasarkan nama barang dan pengetahuan umum
tentang produk serta warung di Indonesia, bukan hasil pengukuran.

## Masukan dan keluaran

Masukan: `data/induk/potongan/potongan_NN.csv` dengan kolom `kode, nama, kategori_kasar`.

Keluaran: `data/induk/klasifikasi/potongan_NN.csv`, satu baris untuk setiap baris
masukan dengan urutan yang sama, kolom:

```
kode,nama,kategori,satuan,ukuran,kelas_harga,popularitas,cocok_warung,keyakinan,alasan
```

Kolom `nama` disalin dari masukan tanpa diubah, untuk memudahkan pemeriksaan. Kolom
`alasan` diisi untuk barang yang dibuang (`cocok_warung = tidak` atau keyakinan
`rendah`) dan dikosongkan untuk barang yang lolos.

Tidak boleh ada baris masukan yang terlewat, termasuk barang yang dinilai tidak
cocok warung.

## Kolom dan nilai yang diizinkan

### kategori

Salah satu dari 22 kategori yang sama dengan saringan, agar kuota rak tetap berlaku:

```
mie instan, rokok, kopi, teh, susu, air minum, minuman ringan, minyak goreng,
beras dan pokok, makanan kaleng, bumbu, permen dan coklat, roti dan biskuit, snack,
perawatan gigi, sabun dan sampo, deterjen dan pembersih, pembalut dan bayi,
rumah tangga, obat warung, alat tulis, es krim
```

Kategori kasar dari saringan dikoreksi apabila keliru. Ketentuan khusus:

- makanan dan susu bayi (Cerelac, susu formula) masuk `susu`
- perlengkapan mandi dan perawatan bayi (bedak, minyak telon, sabun bayi) masuk
  `pembalut dan bayi`
- minuman siap minum berbahan teh masuk `teh`, berbahan kopi masuk `kopi`
- barang yang tidak sesuai satu pun kategori tetap diberi kategori terdekat dan
  dinilai `cocok_warung = tidak`

### satuan

Satuan yang diterima pembeli:

```
bungkus, sachet, botol, kaleng, kotak, pak, cup, tube, strip, batang, pcs,
kg, liter, karung, tabung, galon
```

### ukuran

Ukuran sebagaimana tertulis di nama, ditulis ringkas dengan huruf kecil:
`85g`, `600ml`, `1kg`, `25x1.85g`, `isi 10`. Dikosongkan apabila nama tidak
menyebut ukuran.

### kelas_harga

Perkiraan kelas harga eceran di warung, dinilai sebagai fakta tentang harga barang
dan tidak pernah ditampilkan sebagai rupiah. Di generator, barang `mahal` mengikuti
siklus gajian, sedangkan barang lain datar. Rokok dikecualikan di generator walaupun
harganya mahal. Kelas harga tidak boleh diubah untuk memasukkan atau menghindarkan
barang dari pola tersebut.

| kelas | rentang | contoh |
| --- | --- | --- |
| `murah` | di bawah Rp5.000 | sachet, mie bungkus, permen, korek, air 600 ml |
| `sedang` | Rp5.000 sampai Rp15.000 | sabun batang, teh botol, biskuit kotak, obat strip, pembalut isi sedikit |
| `mahal` | di atas Rp15.000 | minyak 2 liter, rokok bungkus, deterjen besar, susu kaleng, popok |

### popularitas

Seberapa sering barang ini dicari di warung sembako pada umumnya.

| nilai | arti | contoh |
| --- | --- | --- |
| `5` | ada di hampir semua warung, laku setiap hari | Indomie Goreng, Sampoerna Mild, Aqua 600 ml, Kapal Api sachet |
| `4` | ada di kebanyakan warung, laku sering | Mie Sedaap Goreng, Lifebuoy batang, Royco sachet, Rinso sachet |
| `3` | lazim di warung, laku sesekali | varian rasa kedua dan ketiga merek inti, Pepsodent 75 g |
| `2` | ada di sebagian warung, jarang laku | merek kedua tiap kategori, ukuran tidak umum |
| `1` | jarang dijumpai di warung | merek kecil, varian langka |

Barang dengan `cocok_warung = tidak` tetap diberi popularitas, tetapi nilainya
tidak dipakai.

### cocok_warung

`ya` apabila barang lazim dijual warung sembako dalam bentuk tersebut. `tidak`
apabila termasuk salah satu kelompok berikut:

- **kemasan rumah makan atau grosir**: bumbu, sambal, dan saus 1 kg ke atas, minyak
  5 liter ke atas, kaleng besar
- **satuan kulakan**: kemasan isi banyak yang disobek dan dijual per bagian
  (lihat bagian berikutnya)
- **produk supermarket atau impor khusus**: selai impor, pasta, makanan beku,
  produk Filipina dan negara lain yang jarang beredar di Indonesia
- **obat apotek**: obat yang memerlukan resep atau lazimnya hanya dijual apotek
  (antibiotik, salep resep, obat keras); obat bebas seperti Paramex, Promag, OBH,
  dan minyak kayu putih tetap `ya`
- **produk salon atau perawatan premium**: masker rambut, serum, perawatan wajah
  kelas atas
- **kemasan tidak lazim**: hadiah, paket, toples besar, kaleng parsel

### keyakinan

| nilai | kapan dipakai |
| --- | --- |
| `tinggi` | produk dikenal dan nama jelas |
| `sedang` | produk dikenal tetapi ukuran atau bentuk kemasan tidak pasti |
| `rendah` | nama ambigu, merek tidak dikenal, atau bentuk kemasan tidak dapat dipastikan |

Barang berkeyakinan `rendah` diprioritaskan pada pemeriksaan sampel.

## Kemasan isi banyak

Pertanyaan penentu: **apakah pembeli mengambil kemasan itu utuh, atau pemilik
menyobeknya dan menjual per bagian?**

| bentuk | perlakuan | contoh |
| --- | --- | --- |
| dijual utuh ke pembeli | `cocok_warung = ya` | teh celup kotak isi 25, pembalut isi 10, baterai isi 2, wafer kotak isi 4, obat strip isi 4 |
| disobek, dijual per bagian | `cocok_warung = tidak` | kantong kopi isi 30, renceng bumbu 6x8g, renceng sampo, mie isi 5 |

Produk yang di warung dijual per sachet: kopi sachet, minuman serbuk, bumbu dan
penyedap sachet, sampo sachet, deterjen sachet, pewangi sachet, permen eceran.
Kemasan isi banyak untuk produk ini dianggap satuan kulakan.

Produk yang di warung dijual per kemasan: teh celup, pembalut, popok, baterai, tisu,
biskuit dan wafer kotak, obat strip.

Petunjuk pada nama barang:

| petunjuk | arti |
| --- | --- |
| `SCT`, `SACHET`, berat 8 sampai 30 gram | sachet satuan |
| `BAG`, `RENCENG`, `RCG` pada produk sachet | satuan kulakan |
| pola `6X8G`, `30GX10'S` pada produk sachet | renceng, angka pertama atau terakhir adalah isinya |
| `BOX`, `KOTAK`, `KTK` pada teh atau biskuit | kemasan eceran |
| `10'S`, `25'S` pada pembalut, popok, atau teh celup | isi kemasan, dijual utuh |

Potongan diurutkan menurut kategori lalu nama, sehingga varian satu merek berdekatan.
Sebelum membuang kemasan kulakan, periksa apakah satuannya muncul di sekitarnya.

## Urutan kerja per potongan

1. Baca seluruh potongan
2. Nilai setiap barang menurut pedoman ini
3. Tulis keluaran dengan urutan dan jumlah baris yang sama dengan masukan
4. Lewati potongan yang keluarannya sudah ada
5. Setelah seluruh potongan selesai, gabungkan dan validasi dengan
   `datagen/gabung_klasifikasi.py`
