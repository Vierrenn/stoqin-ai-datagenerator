"""Profil lima warung: ciri yang membedakan data penjualan antar warung.

Setiap profil menentukan jumlah barang, keramaian dibanding warung B, kekuatan siklus
gajian, penekanan kategori, dan masa libur. Penekanan dipakai dua kali: memperbesar
porsi kategori di rak (lebih banyak jenis barang) dan memperbesar volume per barang di
kategori itu.

Siklus gajian umumnya hanya berlaku untuk barang mahal. Warung dekat kos berbeda:
seluruh belanja penghuni kos bergantung pada kiriman bulanan, sehingga siklus berlaku
untuk semua barang kecuali rokok.

Porsi rak berbeda dari porsi pemilihan kandidat di `potongan.py`: rokok dan es krim
mendapat porsi lebih besar karena warung menjual banyak jenisnya, dan kategori pokok
memiliki jumlah jenis minimal yang berlaku untuk warung sekecil apa pun.

Seluruh angka merupakan penilaian, bukan hasil pengukuran.
"""

from dataclasses import dataclass, field
from datetime import date

import pandas as pd

PORSI_RAK = {
    "snack": 0.08, "sabun dan sampo": 0.07, "roti dan biskuit": 0.07, "bumbu": 0.08,
    "permen dan coklat": 0.05, "minuman ringan": 0.06, "susu": 0.05, "kopi": 0.05,
    "mie instan": 0.05, "deterjen dan pembersih": 0.05, "rokok": 0.07,
    "pembalut dan bayi": 0.04, "obat warung": 0.04, "rumah tangga": 0.04, "teh": 0.03,
    "perawatan gigi": 0.03, "beras dan pokok": 0.03, "alat tulis": 0.02, "air minum": 0.02,
    "minyak goreng": 0.02, "makanan kaleng": 0.02, "es krim": 0.03,
}
MINIMUM_JENIS = {
    "rokok": 12, "bumbu": 12, "mie instan": 10, "sabun dan sampo": 10, "kopi": 8,
    "deterjen dan pembersih": 8, "es krim": 8, "obat warung": 6, "beras dan pokok": 5,
    "teh": 5, "perawatan gigi": 5, "minyak goreng": 4, "air minum": 4,
}

# (bulan, tanggal) awal dan akhir libur, berulang setiap tahun.
LIBUR_SEKOLAH = (((6, 20), (7, 12)), ((12, 20), (1, 4)))
LIBUR_SEMESTER = (((6, 15), (8, 10)), ((12, 20), (2, 10)))
KATEGORI_SEKOLAH = ("snack", "permen dan coklat", "es krim", "alat tulis", "minuman ringan")
POLA_BARANG_BAYI = (r"BABY|BAYI|BALITA|POPOK|DIAPER|POKO|SWEETY|POPOKU|ZWITSAL|CUSSONS"
                    r"|JOHNSON|JHONSON|TELON|PROMINA|MILNA|CERELAC|MP-ASI|\bSUN \d|SGM|LACTOGEN")


@dataclass(frozen=True)
class ProfilWarung:
    kode: str
    nama: str
    jumlah_barang: int
    keramaian: float
    kekuatan_gajian: float
    seed: int
    penekanan: dict = field(default_factory=dict)
    gajian_semua_barang: bool = False
    libur: tuple = ()
    kategori_libur: tuple | None = None  # None berarti seluruh kategori
    faktor_libur: float = 1.0
    # Lama penurunan bertahap di awal libur dan kenaikan bertahap di akhirnya.
    transisi_libur_hari: int = 0
    # (pola nama, pengali bobot) untuk barang yang jarang dijual di lingkungan warung ini.
    bobot_nama: tuple = ()


PROFIL = [
    ProfilWarung(
        "A", "gang kecil", 250, 0.6, 0.04, 20261101,
        penekanan={"bumbu": 1.3, "mie instan": 1.3, "sabun dan sampo": 1.2,
                   "deterjen dan pembersih": 1.2, "kopi": 1.2, "minyak goreng": 1.2,
                   "beras dan pokok": 1.2, "alat tulis": 0.5, "es krim": 0.5,
                   "makanan kaleng": 0.7, "roti dan biskuit": 0.8, "snack": 0.8,
                   "permen dan coklat": 0.8, "obat warung": 0.8},
    ),
    ProfilWarung("B", "sembako menengah", 500, 1.0, 0.08, 20261102),
    ProfilWarung(
        "C", "dekat sekolah", 400, 0.8, 0.04, 20261103,
        penekanan={"snack": 1.6, "permen dan coklat": 1.6, "es krim": 2.0, "alat tulis": 2.0,
                   "minuman ringan": 1.4, "roti dan biskuit": 1.2, "susu": 1.2, "teh": 1.2,
                   "rokok": 0.5, "deterjen dan pembersih": 0.6, "minyak goreng": 0.6,
                   "beras dan pokok": 0.6, "makanan kaleng": 0.5, "pembalut dan bayi": 0.7,
                   "obat warung": 0.8, "kopi": 0.7, "bumbu": 0.7},
        libur=LIBUR_SEKOLAH, kategori_libur=KATEGORI_SEKOLAH, faktor_libur=0.5,
    ),
    ProfilWarung("D", "kelontong besar", 900, 1.5, 0.08, 20261104),
    ProfilWarung(
        "E", "dekat kos atau kampus", 350, 0.9, 0.08, 20261105,
        penekanan={"mie instan": 1.6, "kopi": 1.4, "air minum": 1.4, "snack": 1.3,
                   "minuman ringan": 1.2, "sabun dan sampo": 1.2, "perawatan gigi": 1.2,
                   "alat tulis": 1.2, "rokok": 1.2, "teh": 1.1, "beras dan pokok": 0.5,
                   "minyak goreng": 0.5, "bumbu": 0.6, "susu": 0.7, "pembalut dan bayi": 0.8,
                   "makanan kaleng": 0.8},
        gajian_semua_barang=True,
        libur=LIBUR_SEMESTER, faktor_libur=0.6, transisi_libur_hari=7,
        bobot_nama=((POLA_BARANG_BAYI, 0.2),),
    ),
]


def penekanan(profil: ProfilWarung, kategori: str) -> float:
    return profil.penekanan.get(kategori, 1.0)


def porsi_kategori(profil: ProfilWarung) -> pd.Series:
    """Porsi rak umum dikalikan penekanan, lalu dinormalkan agar berjumlah 1."""
    porsi = pd.Series({k: rak * penekanan(profil, k) for k, rak in PORSI_RAK.items()})
    return porsi / porsi.sum()


def _bulatkan(nilai: pd.Series, total: int) -> pd.Series:
    """Pembulatan sisa terbesar, agar jumlahnya tepat sama dengan total."""
    bawah = nilai.astype(int)
    sisa = total - bawah.sum()
    tambah = (nilai - bawah).sort_values(ascending=False).index[:sisa]
    bawah[tambah] += 1
    return bawah


def hitung_kuota(profil: ProfilWarung, tersedia: pd.Series) -> pd.Series:
    """Jumlah barang per kategori di rak warung.

    Kuota mengikuti porsi, dengan dua batas: tidak kurang dari jumlah jenis minimal
    kategori dan tidak lebih dari barang yang tersedia. Kategori yang menyentuh batas
    dikunci, lalu sisa kuota dibagi ulang ke kategori lain sebanding porsinya.
    """
    porsi = porsi_kategori(profil)
    tersedia = tersedia.reindex(porsi.index, fill_value=0)
    minimum = pd.Series(MINIMUM_JENIS).reindex(porsi.index, fill_value=0).clip(upper=tersedia)
    if tersedia.sum() < profil.jumlah_barang:
        raise ValueError(f"warung {profil.kode}: barang tersedia kurang dari jumlah barang")

    terkunci = pd.Series(0.0, index=porsi.index)
    kunci = pd.Series(False, index=porsi.index)
    while True:
        sisa_total = profil.jumlah_barang - terkunci[kunci].sum()
        bebas = porsi[~kunci] / porsi[~kunci].sum() * sisa_total
        kurang = bebas < minimum[~kunci]
        lebih = bebas > tersedia[~kunci]
        if not (kurang.any() or lebih.any()):
            break
        terkunci[kurang[kurang].index] = minimum[kurang[kurang].index]
        terkunci[lebih[lebih].index] = tersedia[lebih[lebih].index]
        kunci[kurang[kurang].index] = True
        kunci[lebih[lebih].index] = True

    kuota = pd.concat([terkunci[kunci], bebas])
    return _bulatkan(kuota[porsi.index], profil.jumlah_barang)


def bobot_libur(libur: tuple, tanggal: date, transisi_hari: int = 0) -> float:
    """Kedalaman libur pada suatu tanggal: 0 di luar libur, 1 di tengah libur.

    Dengan transisi, bobot naik bertahap selama sekian hari pertama libur dan turun
    bertahap selama sekian hari terakhir.
    """
    for (bulan_awal, tgl_awal), (bulan_akhir, tgl_akhir) in libur:
        lintas_tahun = (bulan_akhir, tgl_akhir) < (bulan_awal, tgl_awal)
        for tahun in (tanggal.year - 1, tanggal.year):
            awal = date(tahun, bulan_awal, tgl_awal)
            akhir = date(tahun + lintas_tahun, bulan_akhir, tgl_akhir)
            if awal <= tanggal <= akhir:
                if transisi_hari <= 0:
                    return 1.0
                jarak = min((tanggal - awal).days, (akhir - tanggal).days) + 1
                return min(1.0, jarak / transisi_hari)
    return 0.0


def faktor_libur(profil: ProfilWarung, kategori: str, tanggal: date) -> float:
    if profil.kategori_libur is not None and kategori not in profil.kategori_libur:
        return 1.0
    bobot = bobot_libur(profil.libur, tanggal, profil.transisi_libur_hari)
    return 1.0 - (1.0 - profil.faktor_libur) * bobot


if __name__ == "__main__":
    from datagen.gabung_klasifikasi import BERKAS_GABUNG

    tersedia = pd.read_csv(BERKAS_GABUNG, dtype=str).groupby("kategori").size()
    tabel = pd.DataFrame({p.kode: hitung_kuota(p, tersedia) for p in PROFIL})
    tabel["tersedia"] = tersedia.reindex(tabel.index, fill_value=0)
    print(tabel.to_string())
    print(tabel.sum().to_frame("total").T.to_string(header=False))
