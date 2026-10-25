"""Pemilihan isi rak setiap warung dari daftar barang lolos klasifikasi.

Per warung dan per kategori, separuh kuota diisi barang dengan bobot tertinggi agar
barang inti tidak terlewat, dan separuh sisanya diundi sebanding bobot agar barang ekor
berbeda antar warung. Bobot ditentukan popularitas, preferensi warung kecil terhadap
barang murah, dan penyesuaian nama per profil (misalnya barang bayi di warung kos).
Setiap barang terpilih diberi peringkat dalam kategorinya, yang dipakai saat menyusun
resep penjualan.
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd

from datagen.gabung_klasifikasi import BERKAS_GABUNG
from datagen.profil_warung import PROFIL, ProfilWarung, hitung_kuota

DIR_KELUARAN = Path(__file__).resolve().parents[1] / "data" / "demo_5warung"
BERKAS_ASSORTMENT = DIR_KELUARAN / "assortment.csv"
DIR_RAK = DIR_KELUARAN / "rak"

BOBOT_POPULARITAS = {5: 100.0, 4: 30.0, 3: 8.0, 2: 3.0, 1: 1.0}
WARUNG_KECIL = ("A", "C", "E")
BOBOT_KELAS_WARUNG_KECIL = {"murah": 1.5, "sedang": 1.0, "mahal": 0.5}
PORSI_PASTI = 0.5
URUTAN_KELAS = {"murah": 0, "sedang": 1, "mahal": 2}

KOLOM = ["store_id", "kode", "nama", "kategori", "satuan", "ukuran", "kelas_harga",
         "popularitas", "peringkat"]


def bobot(barang: pd.DataFrame, profil: ProfilWarung) -> pd.Series:
    b = barang["popularitas"].map(BOBOT_POPULARITAS)
    if profil.kode in WARUNG_KECIL:
        b = b * barang["kelas_harga"].map(BOBOT_KELAS_WARUNG_KECIL)
    for pola, pengali in profil.bobot_nama:
        b = b.where(~barang["nama"].str.upper().str.contains(pola), b * pengali)
    return b


def ukuran_dasar(ukuran: pd.Series) -> pd.Series:
    """Ukuran dalam gram atau mililiter; kosong atau tidak terbaca dianggap tak hingga."""
    angka = ukuran.str.extract(r"^(\d+(?:\.\d+)?)\s*(kg|g|l|ml)$")
    nilai = angka[0].astype(float) * angka[1].map({"kg": 1000, "l": 1000, "g": 1, "ml": 1})
    return nilai.fillna(float("inf"))


def urutkan(terpilih: pd.DataFrame) -> pd.DataFrame:
    """Peringkat dalam kategori: popularitas tertinggi lebih dahulu; di antara popularitas
    yang sama, barang lebih murah lalu kemasan lebih kecil, karena lebih sering dibeli."""
    return (terpilih.assign(_kelas=terpilih["kelas_harga"].map(URUTAN_KELAS),
                            _ukuran=ukuran_dasar(terpilih["ukuran"]))
            .sort_values(["popularitas", "_kelas", "_ukuran", "_kunci"],
                         ascending=[False, True, True, False]))


def undi(barang: pd.DataFrame, jumlah: int, bobot_barang: pd.Series,
         rng: np.random.Generator) -> pd.DataFrame:
    """Undian berbobot tanpa pengembalian (kunci acak u^(1/bobot), ambil terbesar)."""
    kunci = rng.random(len(barang)) ** (1.0 / bobot_barang.to_numpy())
    return barang.assign(_kunci=kunci).nlargest(jumlah, "_kunci")


def pilih_rak(barang: pd.DataFrame, profil: ProfilWarung) -> pd.DataFrame:
    rng = np.random.default_rng(profil.seed)
    kuota = hitung_kuota(profil, barang.groupby("kategori").size())
    bagian = []
    for kategori, jumlah in kuota.items():
        isi = barang[barang["kategori"] == kategori]
        b = bobot(isi, profil)
        acak_urut = pd.Series(rng.random(len(isi)), index=isi.index)
        urutan = pd.DataFrame({"b": b, "acak": acak_urut}).sort_values(["b", "acak"],
                                                                       ascending=False)
        pasti = urutan.index[:math.ceil(int(jumlah) * PORSI_PASTI)]
        sisa = isi.drop(pasti)
        diundi = undi(sisa, int(jumlah) - len(pasti), b[sisa.index], rng)
        terpilih = urutkan(pd.concat([isi.loc[pasti].assign(_kunci=2.0), diundi]))
        bagian.append(terpilih.assign(peringkat=range(1, len(terpilih) + 1)))
    rak = pd.concat(bagian).assign(store_id=profil.kode)
    return rak[KOLOM].reset_index(drop=True)


def tulis_md(rak: pd.DataFrame, profil: ProfilWarung, berkas: Path) -> None:
    kelas = rak["kelas_harga"].value_counts()
    pop = rak["popularitas"].value_counts().sort_index(ascending=False)
    per_kategori = rak.groupby("kategori").size().sort_values(ascending=False, kind="stable")
    teks = [
        f"# Rak Warung {profil.kode}: {profil.nama}",
        "",
        f"{len(rak)} barang. Keramaian {profil.keramaian}, kekuatan gajian "
        f"{profil.kekuatan_gajian}.",
        "",
        "| popularitas | " + " | ".join(str(p) for p in pop.index) + " |",
        "| --- | " + " | ".join("---" for _ in pop.index) + " |",
        "| jumlah | " + " | ".join(str(v) for v in pop.values) + " |",
        "",
        f"Kelas harga: murah {kelas.get('murah', 0)}, sedang {kelas.get('sedang', 0)}, "
        f"mahal {kelas.get('mahal', 0)}.",
        "",
        "| kategori | barang |",
        "| --- | --- |",
        *[f"| [{k}](#{k.replace(' ', '-')}) | {n} |" for k, n in per_kategori.items()],
    ]
    for kategori in per_kategori.index:
        isi = rak[rak["kategori"] == kategori]
        teks += ["", f"## {kategori}", "", "| # | nama | satuan | ukuran | harga | pop |",
                 "| --- | --- | --- | --- | --- | --- |"]
        teks += [f"| {r.peringkat} | {r.nama.replace('|', '/')} | {r.satuan} | {r.ukuran} | "
                 f"{r.kelas_harga} | {r.popularitas} |" for r in isi.itertuples()]
    berkas.write_text("\n".join(teks) + "\n", encoding="utf-8")


def cetak_laporan(assortment: pd.DataFrame, barang: pd.DataFrame) -> None:
    tabel = pd.crosstab(assortment["store_id"], assortment["popularitas"])
    tabel["total"] = tabel.sum(axis=1)
    print("sebaran popularitas per warung")
    print(tabel.to_string(), "\n")

    sebaran = assortment.groupby("kode").size().value_counts().sort_index()
    print("jumlah warung yang menjual sebuah barang")
    print(sebaran.rename_axis("warung").to_frame("barang").T.to_string(), "\n")

    utama = barang[barang["popularitas"] == 5]["kode"]
    di = assortment[assortment["kode"].isin(utama)].groupby("nama")["store_id"].apply("".join)
    print("barang popularitas 5 dan warung yang menjualnya")
    print(di.to_string())


if __name__ == "__main__":
    barang = pd.read_csv(BERKAS_GABUNG, dtype=str).fillna("")
    barang["popularitas"] = barang["popularitas"].astype(int)

    DIR_RAK.mkdir(parents=True, exist_ok=True)
    semua = []
    for profil in PROFIL:
        rak = pilih_rak(barang, profil)
        rak.to_csv(DIR_RAK / f"rak_{profil.kode}.csv", index=False)
        tulis_md(rak, profil, DIR_RAK / f"rak_{profil.kode}.md")
        semua.append(rak)

    assortment = pd.concat(semua, ignore_index=True)
    assortment.to_csv(BERKAS_ASSORTMENT, index=False)
    cetak_laporan(assortment, barang)
    print(f"\n{len(assortment)} baris ditulis ke {BERKAS_ASSORTMENT}, per warung di {DIR_RAK}")
