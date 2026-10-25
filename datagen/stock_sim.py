"""Simulasi persediaan yang mengubah permintaan harian menjadi penjualan tercatat.

Permintaan yang melebihi stok tersedia tidak terlayani dan tidak tercatat di mana
pun, sebagaimana terjadi pada pencatatan warung. Keluaran penjualan modul ini
yang dibaca model, bukan permintaan aslinya.

Kebijakan pemesanan pada modul ini sengaja hanya memakai rata-rata penjualan
terakhir, bukan hasil forecast. Data yang dibangkitkan menggambarkan kondisi
warung sebelum memakai sistem, sehingga penggunaan forecast di dalamnya akan
membuat evaluasi menjadi melingkar.
"""

import numpy as np
import pandas as pd

PENYANGGA = 1.3
JENDELA_RATA_RATA = 28

# Stok awal ditetapkan dari laju permintaan sebenarnya, sedangkan pemesanan
# berikutnya hanya memakai penjualan tercatat. Selisih kedua sudut pandang itu
# membuat awal simulasi berada pada kondisi persediaan yang lebih longgar
# daripada kondisi seimbangnya. Periode ini dibuang agar data yang tersimpan
# seluruhnya berada pada kondisi seimbang.
HARI_PEMANASAN = 90


def _peta_offset(parameter: pd.DataFrame) -> dict:
    """Pergeseran hari kulakan tiap SKU, dibagikan bergilir dalam kelompok periode sama.

    Periode 7 dan 14 habis dibagi tujuh, sehingga tanpa pergeseran seluruh SKU
    dengan periode tersebut menerima kiriman pada hari yang sama setiap minggu.
    Pola itu menimbulkan siklus persediaan mingguan buatan yang ikut terbaca
    sebagai pola hari-dalam-minggu pada data penjualan, dan melebarkan pola
    tersebut sekitar delapan puluh persen di atas pola permintaan sebenarnya.

    Pembagian bergilir dipilih daripada pergeseran acak agar penyebaran merata
    walaupun jumlah SKU per kelompok sedikit.
    """
    offset = {}
    for review_period, kelompok in parameter.groupby("review_period_hari"):
        for urutan, sku_id in enumerate(sorted(kelompok.index)):
            offset[sku_id] = urutan % int(review_period)
    return offset


def _simulasi_satu_sku(permintaan: np.ndarray, unit_per_hari: float, lead_time: int,
                       review_period: int, offset: int, stok_minimal: int = 0) -> pd.DataFrame:
    n = len(permintaan)
    siklus = lead_time + review_period

    stok = max(stok_minimal, round(unit_per_hari * siklus * PENYANGGA))
    datang = np.zeros(n + lead_time + 1, dtype=int)

    kolom = {nama: np.zeros(n, dtype=int) for nama in
             ("stok_awal", "datang", "terjual", "kehilangan", "stok_akhir",
              "dipesan", "dalam_perjalanan")}

    for i in range(n):
        kolom["stok_awal"][i] = stok
        kolom["datang"][i] = datang[i]
        stok += datang[i]

        terjual = min(permintaan[i], stok)
        stok -= terjual
        kolom["terjual"][i] = terjual
        kolom["kehilangan"][i] = permintaan[i] - terjual
        kolom["stok_akhir"][i] = stok

        if (i + offset) % review_period == 0:
            # Rata-rata penjualan tercatat, bukan permintaan. Pemilik tidak
            # mengetahui pembelian yang batal akibat stok kosong, sehingga
            # kekosongan cenderung menekan pesanan berikutnya.
            awal = max(0, i - JENDELA_RATA_RATA + 1)
            laju = kolom["terjual"][awal:i + 1].mean() if i else unit_per_hari
            dalam_perjalanan = datang[i + 1:].sum()
            target = max(stok_minimal, round(laju * siklus * PENYANGGA))
            pesan = max(0, target - stok - dalam_perjalanan)
            if pesan:
                datang[i + lead_time] += pesan
            kolom["dipesan"][i] = pesan

        kolom["dalam_perjalanan"][i] = datang[i + 1:].sum()

    return pd.DataFrame(kolom)


def jalankan_simulasi(permintaan: pd.DataFrame, katalog: pd.DataFrame,
                      hari_pemanasan: int = 0, stok_minimal: int = 0) -> pd.DataFrame:
    """Menjalankan simulasi persediaan untuk seluruh SKU.

    Mengembalikan tabel harian gabungan berisi kolom permintaan, terjual,
    kehilangan, pergerakan stok, dan pemesanan. Kolom terjual merupakan penjualan
    tercatat yang selanjutnya dipakai sebagai masukan model.

    hari_pemanasan menentukan jumlah hari pertama yang dibuang dari keluaran.
    Simulasi tetap dijalankan atas hari-hari tersebut, sehingga sisa data mewarisi
    kondisi persediaan yang sudah seimbang.

    stok_minimal adalah batas bawah stok target saat kulakan. Tanpa batas ini, barang
    sangat lambat yang sempat habis tidak pernah dipesan lagi: rata-rata penjualan
    tercatatnya menjadi nol sehingga pesanan selalu dibulatkan ke nol. Apabila katalog
    memiliki kolom stok_minimal, nilai per SKU tersebut yang dipakai.
    """
    parameter = katalog.set_index("sku_id")[["lead_time_hari", "review_period_hari"]]
    minimal = (katalog.set_index("sku_id")["stok_minimal"] if "stok_minimal" in katalog
               else pd.Series(stok_minimal, index=parameter.index))
    laju = permintaan.groupby("sku_id")["qty"].mean()
    offset = _peta_offset(parameter)

    bagian = []
    for sku_id, kelompok in permintaan.groupby("sku_id", sort=False):
        kelompok = kelompok.sort_values("date").reset_index(drop=True)
        review_period = int(parameter.loc[sku_id, "review_period_hari"])
        hasil = _simulasi_satu_sku(
            kelompok["qty"].to_numpy(),
            laju[sku_id],
            int(parameter.loc[sku_id, "lead_time_hari"]),
            review_period,
            offset[sku_id],
            int(minimal[sku_id]),
        )
        gabung = pd.concat([kelompok.rename(columns={"qty": "permintaan"}), hasil], axis=1)
        bagian.append(gabung.iloc[hari_pemanasan:])

    return pd.concat(bagian, ignore_index=True)


def ambil_penjualan(harian: pd.DataFrame) -> pd.DataFrame:
    """Mengambil buku penjualan yang boleh dibaca model."""
    return (
        harian[["sku_id", "date", "weekday", "terjual"]]
        .rename(columns={"terjual": "qty"})
        .reset_index(drop=True)
    )


def ambil_snapshot(harian: pd.DataFrame) -> pd.DataFrame:
    """Kondisi persediaan pada hari terakhir simulasi, masukan untuk fitur restock."""
    akhir = harian.sort_values("date").groupby("sku_id", sort=False).last().reset_index()
    return akhir[["sku_id", "date", "stok_akhir", "dalam_perjalanan"]].rename(
        columns={"date": "tanggal", "stok_akhir": "current_stock",
                 "dalam_perjalanan": "incoming_stock"}
    )
