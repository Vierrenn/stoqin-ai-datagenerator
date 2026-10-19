"""Penyusunan tampilan lebar dari buku penjualan untuk keperluan pemeriksaan manual.

Berkas yang dihasilkan modul ini merupakan turunan dan tidak dibaca oleh komponen
mana pun. Sumber data yang berlaku tetap penjualan_harian.csv dalam bentuk panjang.
"""

import pandas as pd

KOLOM_IDENTITAS = ["nama", "satuan"]


def _tempel_identitas(lebar: pd.DataFrame, katalog: pd.DataFrame) -> pd.DataFrame:
    identitas = katalog.set_index("sku_id")[KOLOM_IDENTITAS]
    return identitas.join(lebar).reset_index()


def lebar_harian(penjualan: pd.DataFrame, katalog: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per SKU, satu kolom per tanggal."""
    lebar = penjualan.pivot(index="sku_id", columns="date", values="qty")
    lebar.columns = [pd.Timestamp(c).strftime("%Y-%m-%d") for c in lebar.columns]
    return _tempel_identitas(lebar, katalog)


def lebar_bulanan(penjualan: pd.DataFrame, katalog: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per SKU, satu kolom per bulan, berisi total penjualan bulan tersebut."""
    bulan = pd.to_datetime(penjualan["date"]).dt.strftime("%Y-%m")
    lebar = penjualan.assign(bulan=bulan).pivot_table(
        index="sku_id", columns="bulan", values="qty", aggfunc="sum"
    )
    lebar["total_setahun"] = lebar.sum(axis=1)
    return _tempel_identitas(lebar, katalog)
