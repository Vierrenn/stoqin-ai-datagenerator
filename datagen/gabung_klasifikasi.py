"""Penggabungan dan validasi hasil klasifikasi menjadi satu daftar barang lolos.

Setiap berkas hasil klasifikasi dicocokkan dengan potongan masukannya, nilai kolomnya
diperiksa terhadap pedoman, lalu barang yang cocok warung dan keyakinannya bukan rendah
digabung. Barang kembar yang namanya hanya berbeda tanda baca atau spasi dibuang,
dengan mempertahankan yang popularitasnya tertinggi.
"""

import pandas as pd

from datagen.katalog_induk import DIR_INDUK
from datagen.potongan import DIR_KLASIFIKASI, DIR_POTONGAN, PORSI, UKURAN_WARUNG_TERBESAR

BERKAS_GABUNG = DIR_INDUK / "klasifikasi.csv"

KOLOM = ["kode", "nama", "kategori", "satuan", "ukuran", "kelas_harga", "popularitas",
         "cocok_warung", "keyakinan", "alasan"]
KOLOM_KELUARAN = ["kode", "nama", "kategori", "satuan", "ukuran", "kelas_harga",
                  "popularitas", "keyakinan"]
NILAI = {
    "kategori": set(PORSI),
    "satuan": {"bungkus", "sachet", "botol", "kaleng", "kotak", "pak", "cup", "tube", "strip",
               "batang", "pcs", "kg", "liter", "karung", "tabung", "galon"},
    "kelas_harga": {"murah", "sedang", "mahal"},
    "popularitas": {"1", "2", "3", "4", "5"},
    "cocok_warung": {"ya", "tidak"},
    "keyakinan": {"tinggi", "sedang", "rendah"},
}


def muat_satu(berkas_hasil) -> pd.DataFrame:
    """Membaca satu hasil klasifikasi dan memastikan cocok dengan potongan masukannya."""
    hasil = pd.read_csv(berkas_hasil, dtype=str).fillna("")
    masukan = pd.read_csv(DIR_POTONGAN / berkas_hasil.name, dtype=str)
    nama = berkas_hasil.name

    if list(hasil.columns) != KOLOM:
        raise ValueError(f"{nama}: kolom {list(hasil.columns)}, seharusnya {KOLOM}")
    if hasil["kode"].tolist() != masukan["kode"].tolist():
        raise ValueError(f"{nama}: kode atau urutannya tidak sama dengan potongan masukan")
    for kolom, boleh in NILAI.items():
        salah = sorted(set(hasil[kolom]) - boleh)
        if salah:
            raise ValueError(f"{nama}: nilai {kolom} tidak dikenal: {salah}")

    dibuang = (hasil["cocok_warung"] == "tidak") | (hasil["keyakinan"] == "rendah")
    if (dibuang & (hasil["alasan"] == "")).any():
        raise ValueError(f"{nama}: ada barang dibuang tanpa alasan")
    return hasil


def gabung() -> tuple[pd.DataFrame, int]:
    berkas = sorted(DIR_KLASIFIKASI.glob("*_*.csv"))
    if not berkas:
        raise FileNotFoundError(f"tidak ada hasil klasifikasi di {DIR_KLASIFIKASI}")
    semua = pd.concat([muat_satu(b) for b in berkas], ignore_index=True)
    if semua["kode"].duplicated().any():
        raise ValueError("kode yang sama muncul di lebih dari satu berkas")

    lolos = semua[(semua["cocok_warung"] == "ya") & (semua["keyakinan"] != "rendah")]
    kunci = lolos["nama"].str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    urut = lolos.assign(kunci=kunci).sort_values("popularitas", ascending=False, kind="stable")
    bersih = urut.drop_duplicates("kunci").sort_values(["kategori", "nama"])
    return bersih[KOLOM_KELUARAN].reset_index(drop=True), len(lolos) - len(bersih)


def cetak_laporan(barang: pd.DataFrame, kembar: int) -> None:
    print(f"{len(barang)} barang lolos, {kembar} barang kembar dibuang\n")
    print(f"{'kategori':24s}{'lolos':>6}{'butuh D':>9}")
    for kategori, (rak, _) in PORSI.items():
        ada = (barang["kategori"] == kategori).sum()
        butuh = round(UKURAN_WARUNG_TERBESAR * rak)
        tanda = "  kurang" if ada < butuh else ""
        print(f"{kategori:24s}{ada:>6}{butuh:>9}{tanda}")


if __name__ == "__main__":
    barang, kembar = gabung()
    barang.to_csv(BERKAS_GABUNG, index=False)
    cetak_laporan(barang, kembar)
    print(f"\nditulis ke {BERKAS_GABUNG}")
