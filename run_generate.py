"""Membangkitkan data penjualan warung sintetis untuk keperluan demonstrasi.

Menjalankan seluruh rangkaian: memuat katalog dan resep, membangkitkan permintaan
harian, menjalankan simulasi persediaan, lalu menulis tiga berkas ke data/demo.

Kolom permintaan dan kehilangan pada stok_harian.csv tidak dapat diamati pada
kondisi nyata. Kedua kolom tersebut hanya boleh dipakai untuk memeriksa hasil
simulasi, dan tidak boleh dibaca oleh komponen yang mensimulasikan produk.
"""

import pandas as pd

from datagen.resep import DIR_DATA, muat_resep
from datagen.stock_sim import (HARI_PEMANASAN, ambil_penjualan, ambil_snapshot,
                               jalankan_simulasi)
from datagen.synthetic import JUMLAH_HARI, SEED, TANGGAL_MULAI, bangkitkan_permintaan
from datagen.tinjauan import lebar_bulanan, lebar_harian

DIR_KELUARAN = DIR_DATA / "demo"
DIR_TINJAUAN = DIR_KELUARAN / "tinjauan"


def main() -> None:
    resep = muat_resep()

    mulai_pemanasan = pd.Timestamp(TANGGAL_MULAI) - pd.Timedelta(days=HARI_PEMANASAN)
    permintaan = bangkitkan_permintaan(
        resep,
        tanggal_mulai=mulai_pemanasan,
        jumlah_hari=JUMLAH_HARI + HARI_PEMANASAN,
        seed=SEED,
    )

    harian = jalankan_simulasi(permintaan, resep, hari_pemanasan=HARI_PEMANASAN)
    penjualan = ambil_penjualan(harian)
    snapshot = ambil_snapshot(harian)

    DIR_TINJAUAN.mkdir(parents=True, exist_ok=True)
    penjualan.to_csv(DIR_KELUARAN / "penjualan_harian.csv", index=False)
    harian.to_csv(DIR_KELUARAN / "stok_harian.csv", index=False)
    snapshot.to_csv(DIR_KELUARAN / "snapshot_stok.csv", index=False)

    lebar_harian(penjualan, resep).to_csv(
        DIR_TINJAUAN / "penjualan_harian_lebar.csv", index=False)
    lebar_bulanan(penjualan, resep).to_csv(
        DIR_TINJAUAN / "penjualan_bulanan_lebar.csv", index=False)

    _cetak_ringkasan(resep, harian, penjualan)


def _cetak_ringkasan(resep: pd.DataFrame, harian: pd.DataFrame,
                     penjualan: pd.DataFrame) -> None:
    per_sku = harian.groupby("sku_id")[["permintaan", "terjual"]].mean()
    mutu = (per_sku["permintaan"] / resep.set_index("sku_id")["rata_harian_target"] - 1) * 100
    dampak = (per_sku["terjual"] / per_sku["permintaan"] - 1) * 100
    kosong = harian.groupby("sku_id")["kehilangan"].apply(lambda s: (s > 0).mean() * 100)

    print(f"seed {SEED}, {penjualan['sku_id'].nunique()} SKU, "
          f"{penjualan['date'].nunique()} hari "
          f"({penjualan['date'].min():%Y-%m-%d} sampai {penjualan['date'].max():%Y-%m-%d})")
    print(f"  permintaan thd target resep  : rata-rata {mutu.mean():+.2f}%, "
          f"terbesar {mutu.abs().max():.1f}%   (mutu generator)")
    print(f"  penjualan thd permintaan     : rata-rata {dampak.mean():+.2f}%   "
          f"(dampak stok kosong)")
    print(f"  hari stok kosong per SKU     : median {kosong.median():.1f}%, "
          f"tertinggi {kosong.max():.1f}%")
    print(f"  berkas ditulis ke {DIR_KELUARAN}")
    print("  data sintetis, tidak boleh dipakai sebagai bukti akurasi model")


if __name__ == "__main__":
    main()
