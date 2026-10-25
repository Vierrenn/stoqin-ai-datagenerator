"""Pembangkitan permintaan harian per SKU dari parameter resep.

Keluaran modul ini merupakan permintaan, bukan penjualan. Pembatasan akibat
kekosongan stok diterapkan terpisah pada stock_sim.

Setiap hari ditentukan oleh tiga penarikan acak: apakah terjadi penjualan,
berapa kuantitas normalnya, dan apakah terjadi pembelian besar.
"""

import numpy as np
import pandas as pd

from datagen.kalender import faktor_kalender

TANGGAL_MULAI = "2025-09-01"
JUMLAH_HARI = 365
SEED = 20260912


def _tarik_kuantitas(rng, batas_bawah: float, batas_atas: float) -> int:
    """Kuantitas bilangan bulat dari sebaran seragam pada rentang yang diberikan.

    Rata-ratanya tepat sama dengan titik tengah rentang, sehingga rata-rata harian
    dapat dihitung dan diperiksa secara manual dari parameter resep.

    Sebaran seragam dipilih daripada triangular karena triangular dengan puncak di
    titik tengah menghasilkan keluaran yang terlalu memusat pada rentang bilangan
    bulat yang sempit. Pada rentang 1 sampai 3, triangular menghasilkan nilai 2
    sebanyak tiga perempat waktu, sedangkan pembacaan yang wajar atas sebuah
    rentang adalah ketiga nilai berpeluang sebanding.
    """
    if batas_atas <= batas_bawah:
        return int(batas_bawah)
    return max(1, int(round(rng.uniform(batas_bawah, batas_atas))))


def _tarik_geometrik(rng, rata_rata: float, batas_atas: int) -> int:
    """Kuantitas yang biasanya 1 dan sesekali lebih banyak, dengan rata-rata tertentu.

    Dipakai untuk barang yang tidak laku setiap hari. Sebaran seragam pada rentang
    sempit tidak pernah menghasilkan variasi kuantitas yang cukup besar untuk pola
    lumpy, sedangkan pembelian nyata atas barang lambat sesekali berjumlah beberapa
    buah sekaligus.
    """
    return int(min(batas_atas, rng.geometric(min(1.0, 1.0 / max(rata_rata, 1.0)))))


def _deret_satu_sku(baris, pengali_harian: np.ndarray, rng) -> np.ndarray:
    qty = np.zeros(len(pengali_harian), dtype=int)

    for i, pengali in enumerate(pengali_harian):
        # Pengaruh kalender diserap frekuensi selama peluang masih di bawah 1,
        # sisanya tumpah ke kuantitas. SKU berfrekuensi penuh dikecualikan: seluruh
        # pengaruh masuk ke kuantitas, karena hari sepi pada barang pokok berarti
        # jumlah lebih sedikit, bukan tidak terjadi penjualan.
        if baris.prob_laku >= 1.0:
            peluang, skala = 1.0, pengali
        else:
            efektif = baris.prob_laku * pengali
            peluang = min(1.0, efektif)
            skala = efektif / peluang

        total = 0
        if rng.random() < peluang:
            per_beli = getattr(baris, "rata_per_beli", 0)
            if per_beli > 0:
                total += _tarik_geometrik(rng, per_beli * skala, baris.qty_maks)
            else:
                total += _tarik_kuantitas(rng, baris.qty_min * skala, baris.qty_maks * skala)

        # Peluang pembelian besar ikut dipengaruhi kalender, sedangkan kuantitasnya
        # tidak: hajatan lebih sering terjadi pada tanggal muda, bukan lebih besar.
        if baris.prob_bulk > 0 and rng.random() < min(1.0, baris.prob_bulk * pengali):
            total += _tarik_kuantitas(rng, baris.bulk_min, baris.bulk_maks)

        qty[i] = total

    return qty


def bangkitkan_permintaan(
    resep: pd.DataFrame,
    tanggal_mulai: str = TANGGAL_MULAI,
    jumlah_hari: int = JUMLAH_HARI,
    seed: int = SEED,
) -> pd.DataFrame:
    """Membangkitkan permintaan harian untuk seluruh SKU pada tabel resep.

    Setiap SKU memakai aliran bilangan acak sendiri yang diturunkan dari seed
    utama, sehingga perubahan parameter satu SKU tidak menggeser hasil SKU lain.
    """
    tanggal = pd.date_range(tanggal_mulai, periods=jumlah_hari, freq="D")
    pengali = np.array([[faktor_kalender(t, baris.sensitif_tanggal_muda) for t in tanggal]
                        for baris in resep.itertuples()])
    return bangkitkan_dengan_pengali(resep, tanggal, pengali, seed)


def bangkitkan_dengan_pengali(resep: pd.DataFrame, tanggal: pd.DatetimeIndex,
                              pengali: np.ndarray, seed: int) -> pd.DataFrame:
    """Membangkitkan permintaan dengan pengali kalender yang dihitung di luar modul ini.

    pengali berbentuk (jumlah SKU, jumlah hari), berurutan sama dengan baris resep.
    """
    induk = np.random.SeedSequence(seed)

    bagian = []
    for anak, baris, deret_pengali in zip(induk.spawn(len(resep)), resep.itertuples(), pengali):
        bagian.append(
            pd.DataFrame(
                {
                    "sku_id": baris.sku_id,
                    "date": tanggal,
                    "weekday": tanggal.day_name(),
                    "qty": _deret_satu_sku(baris, deret_pengali, np.random.default_rng(anak)),
                }
            )
        )

    return pd.concat(bagian, ignore_index=True)
