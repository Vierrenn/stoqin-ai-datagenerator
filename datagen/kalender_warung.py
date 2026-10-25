"""Pengali kalender harian untuk setiap barang di lima warung.

Pengali harian merupakan hasil kali empat efek: hari dalam minggu, siklus gajian,
masa libur profil warung, dan musim tahun ajaran baru. Efek gajian bergantung pada
kekuatan per barang di resep; efek libur dan musim bergantung pada kategori.
"""

import numpy as np
import pandas as pd

from datagen.kalender import FAKTOR_HARI
from datagen.profil_warung import ProfilWarung, faktor_libur, faktor_musim


def _gajian(tanggal: pd.DatetimeIndex, kekuatan: float) -> np.ndarray:
    """Sama dengan kalender.faktor_gajian, dihitung sekaligus untuk seluruh tanggal."""
    sudut = 2 * np.pi * (tanggal.day.to_numpy() - 0.5) / tanggal.days_in_month.to_numpy()
    return 1 + kekuatan * np.cos(sudut)


def pengali_harian(resep_warung: pd.DataFrame, profil: ProfilWarung,
                   tanggal: pd.DatetimeIndex) -> np.ndarray:
    """Matriks pengali berbentuk (jumlah barang, jumlah hari), urut sesuai baris resep."""
    hari = tanggal.day_name().map(FAKTOR_HARI).to_numpy(dtype=float)
    per_kategori = {
        k: np.array([faktor_libur(profil, k, t) * faktor_musim(k, t) for t in tanggal.date])
        for k in resep_warung["kategori"].unique()
    }
    per_kekuatan = {k: _gajian(tanggal, k) for k in resep_warung["kekuatan_gajian"].unique()}
    return np.vstack([
        hari * per_kategori[r.kategori] * per_kekuatan[r.kekuatan_gajian]
        for r in resep_warung.itertuples()
    ])
