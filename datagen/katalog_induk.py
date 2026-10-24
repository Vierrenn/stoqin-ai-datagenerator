"""Pemuatan katalog induk dari basis data barang IPOS 5 ke CSV ringkas.

Berkas sumber berisi templat basis data aplikasi kasir IPOS 5. Kolom harga, jenis,
merek, dan stok kosong atau seragam pada seluruh baris, sehingga yang dipertahankan
hanya kode, barcode, dan nama barang.
"""

from pathlib import Path

import pandas as pd

DIR_INDUK = Path(__file__).resolve().parents[1] / "data" / "induk"
BERKAS_SUMBER = DIR_INDUK / "IPOS 5 DATABASE 50.600+ DATA ITEM WARUNG.xls"
BERKAS_KELUARAN = DIR_INDUK / "katalog_induk.csv"

SHEET = "DATA ITEM 1 HARGA"
BARIS_JUDUL = 1  # baris pertama berisi penanda templat IPOS, bukan data
JUMLAH_BARANG = 50_601

_KOLOM = {"KODE ITEM": "kode", "BARCODE": "barcode", "NAMA ITEM": "nama"}


def muat_katalog_induk(sumber: Path = BERKAS_SUMBER) -> pd.DataFrame:
    """Membaca sheet barang dan mengembalikan kolom kode, barcode, dan nama.

    Kode dan barcode dibaca sebagai teks agar angka nol di depan tidak hilang.
    """
    mentah = pd.read_excel(
        sumber,
        sheet_name=SHEET,
        skiprows=BARIS_JUDUL,
        usecols=list(_KOLOM),
        dtype=str,
        engine="xlrd",
    )
    katalog = mentah.rename(columns=_KOLOM)
    for kolom in katalog.columns:
        katalog[kolom] = katalog[kolom].str.strip()
    katalog["nama"] = katalog["nama"].str.replace(r"\s+", " ", regex=True)
    return katalog


def validasi_katalog(katalog: pd.DataFrame) -> None:
    if len(katalog) != JUMLAH_BARANG:
        raise ValueError(f"jumlah barang {len(katalog)}, seharusnya {JUMLAH_BARANG}")
    if katalog["kode"].isna().any() or katalog["kode"].duplicated().any():
        raise ValueError("kode barang kosong atau tidak unik")
    if katalog["nama"].isna().any() or (katalog["nama"] == "").any():
        raise ValueError("terdapat nama barang kosong")


if __name__ == "__main__":
    katalog = muat_katalog_induk()
    validasi_katalog(katalog)
    katalog.to_csv(BERKAS_KELUARAN, index=False)

    nama_kembar = katalog["nama"].duplicated(keep=False).sum()
    print(f"{len(katalog)} barang ditulis ke {BERKAS_KELUARAN}")
    print(f"  nama unik: {katalog['nama'].nunique()}, "
          f"barang dengan nama kembar: {nama_kembar}")
    print(f"  kode diawali nol: {katalog['kode'].str.startswith('0').sum()}")
