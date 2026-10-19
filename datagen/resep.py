"""Pemuatan dan validasi parameter resep sintetis.

Parameter pembangkitan ditetapkan langsung pada resep_sintetis.csv, memisahkan
empat hal yang sebelumnya tercampur dalam satu angka rata-rata harian: peluang
terjadinya penjualan, kuantitas pada penjualan normal, peluang terjadinya
pembelian besar, dan kuantitas pembelian besar tersebut.

Rata-rata harian merupakan besaran turunan:

    rata_harian = prob_laku x (qty_min + qty_maks) / 2
                + prob_bulk x (bulk_min + bulk_maks) / 2

Modul ini tidak menurunkan parameter dari dataset M5. Angka rujukan M5 dipakai
pada tahap verifikasi, bukan pembangkitan.
"""

from pathlib import Path

import pandas as pd

from datagen.kalender import AMBANG_HARGA_SENSITIF

DIR_DATA = Path(__file__).resolve().parents[1] / "data"

TIPE_DEMAND = {
    "stabil_tinggi", "stabil_sedang", "rutin_bulk",
    "intermittent", "lumpy_bulk", "musiman", "event",
}

TOLERANSI_RATA_HARIAN = 0.01


def hitung_rata_harian(resep: pd.DataFrame) -> pd.Series:
    normal = resep["prob_laku"] * (resep["qty_min"] + resep["qty_maks"]) / 2
    bulk = resep["prob_bulk"] * (resep["bulk_min"] + resep["bulk_maks"]) / 2
    return normal + bulk


def validasi_resep(resep: pd.DataFrame) -> None:
    """Memeriksa konsistensi parameter, termasuk kesesuaian rata_harian_target.

    Kolom rata_harian_target pada berkas bersifat informatif dan mudah menjadi
    usang apabila parameter diubah tanpa menghitung ulang. Ketidaksesuaian
    diperlakukan sebagai kesalahan agar penyimpangan tidak lolos tanpa terdeteksi.
    """
    def gagal(kondisi: pd.Series, pesan: str) -> None:
        salah = resep.loc[kondisi, "sku_id"].tolist()
        if salah:
            raise ValueError(f"{pesan}: {salah}")

    gagal(~resep["tipe_demand"].isin(TIPE_DEMAND), "tipe_demand tidak dikenal")
    gagal((resep["prob_laku"] <= 0) | (resep["prob_laku"] > 1), "prob_laku harus di rentang (0, 1]")
    gagal((resep["prob_bulk"] < 0) | (resep["prob_bulk"] >= 1), "prob_bulk harus di rentang [0, 1)")
    gagal(resep["qty_min"] < 1, "qty_min minimal 1")
    gagal(resep["qty_maks"] < resep["qty_min"], "qty_maks tidak boleh di bawah qty_min")

    ada_bulk = resep["prob_bulk"] > 0
    gagal(ada_bulk & (resep["bulk_min"] < 1), "bulk_min minimal 1 apabila prob_bulk di atas 0")
    gagal(ada_bulk & (resep["bulk_maks"] < resep["bulk_min"]),
          "bulk_maks tidak boleh di bawah bulk_min")
    gagal(~ada_bulk & ((resep["bulk_min"] > 0) | (resep["bulk_maks"] > 0)),
          "bulk_min dan bulk_maks harus 0 apabila prob_bulk 0")

    selisih = (hitung_rata_harian(resep) - resep["rata_harian_target"]).abs()
    gagal(selisih > TOLERANSI_RATA_HARIAN, "rata_harian_target tidak sesuai parameternya")


def muat_resep(dir_data: Path = DIR_DATA) -> pd.DataFrame:
    """Memuat katalog dan resep, menggabungkan berdasarkan sku_id, lalu memvalidasi.

    SKU yang tidak memiliki pasangan pada salah satu berkas menghasilkan kesalahan,
    bukan diabaikan.

    Kolom sensitif_tanggal_muda diturunkan dari harga jual, bukan ditetapkan per
    SKU, dengan asumsi pembelian barang berharga tinggi ditunda sampai penerimaan
    gaji.
    """
    katalog = pd.read_csv(dir_data / "katalog_sku_warung.csv")
    resep = pd.read_csv(dir_data / "resep_sintetis.csv")

    tanpa_resep = sorted(set(katalog["sku_id"]) - set(resep["sku_id"]))
    tanpa_katalog = sorted(set(resep["sku_id"]) - set(katalog["sku_id"]))
    if tanpa_resep or tanpa_katalog:
        raise ValueError(
            f"katalog dan resep tidak sinkron. "
            f"tanpa resep: {tanpa_resep}, tanpa katalog: {tanpa_katalog}"
        )

    gabung = katalog.merge(resep, on="sku_id")
    validasi_resep(gabung)
    gabung["sensitif_tanggal_muda"] = gabung["harga_jual"] >= AMBANG_HARGA_SENSITIF
    return gabung
