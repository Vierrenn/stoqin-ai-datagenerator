"""Pemeriksaan hasil generate lima warung terhadap rancangannya.

Tes membaca berkas di data/demo_5warung, sehingga run_generate_5warung.py harus
dijalankan lebih dahulu. Ambang tes diturunkan dari parameter rancangan (profil warung,
kalender, resep), bukan dari hasil generate itu sendiri.
"""

import numpy as np
import pandas as pd
import pytest

from datagen.gabung_klasifikasi import BERKAS_GABUNG
from datagen.kalender_warung import pengali_harian
from datagen.profil_warung import KATEGORI_SEKOLAH, PROFIL
from datagen.referensi_m5 import AMBANG_ADI, AMBANG_CV2
from datagen.resep_otomatis import BERKAS_RESEP, DIR_KELUARAN, HARGA_KELAS

BERKAS_STOK = DIR_KELUARAN / "stok_harian.csv"
pytestmark = pytest.mark.skipif(not BERKAS_STOK.exists(),
                                reason="jalankan run_generate_5warung.py terlebih dahulu")
PROFIL_KODE = {p.kode: p for p in PROFIL}


@pytest.fixture(scope="module")
def resep():
    return pd.read_csv(BERKAS_RESEP, dtype={"kode": str})


@pytest.fixture(scope="module")
def harian(resep):
    stok = pd.read_csv(BERKAS_STOK, dtype={"kode": str}, parse_dates=["date"])
    return stok.merge(resep[["store_id", "kode", "kategori", "kelas_harga", "kekuatan_gajian",
                             "prob_bulk", "qty_maks", "rata_per_beli"]],
                      on=["store_id", "kode"])


def _total_per_tanggal(df: pd.DataFrame, kolom: str = "terjual") -> pd.Series:
    return df.groupby("date")[kolom].sum()


def test_jumlah_barang_dan_periode(harian):
    jumlah = harian.groupby("store_id")["kode"].nunique().to_dict()
    assert jumlah == {p.kode: p.jumlah_barang for p in PROFIL}
    assert harian["date"].min() == pd.Timestamp("2025-10-01")
    assert harian["date"].max() == pd.Timestamp("2026-09-30")
    assert (harian.groupby(["store_id", "kode"]).size() == 365).all()


def test_semua_barang_lolos_klasifikasi(resep):
    if not BERKAS_GABUNG.exists():
        pytest.skip("hasil klasifikasi tidak tersedia")
    lolos = set(pd.read_csv(BERKAS_GABUNG, dtype={"kode": str})["kode"])
    assert set(resep["kode"]) <= lolos


def test_permintaan_sesuai_resep_dan_kalender(harian, resep):
    """Permintaan tiap warung mendekati resep yang dikalikan rata-rata pengali kalender."""
    tanggal = pd.date_range("2025-10-01", "2026-09-30")
    for kode, profil in PROFIL_KODE.items():
        r = resep[resep["store_id"] == kode].reset_index(drop=True)
        pengali = pengali_harian(r, profil, tanggal).mean(axis=1)
        harapan = (r["rata_harian_target"] * pengali).sum() * len(tanggal)
        aktual = harian.loc[harian["store_id"] == kode, "permintaan"].sum()
        assert aktual / harapan == pytest.approx(1, abs=0.02), kode


def test_efek_hari(harian):
    for kode, g in harian.groupby("store_id"):
        per_hari = g.groupby(g["date"].dt.day_name())["terjual"].sum()
        assert per_hari["Saturday"] / per_hari["Wednesday"] > 1.08, kode


def test_efek_gajian(harian):
    """Barang yang ikut siklus gajian lebih laku di sekitar pergantian bulan; rokok datar."""
    hari = harian["date"].dt.day
    muda, tengah = (hari >= 28) | (hari <= 4), (hari >= 11) & (hari <= 20)

    def rasio(m):
        return (_total_per_tanggal(harian[m & muda]).mean()
                / _total_per_tanggal(harian[m & tengah]).mean())

    assert rasio(harian["kekuatan_gajian"] > 0) > 1.04
    assert rasio(harian["kategori"] == "rokok") == pytest.approx(1, abs=0.04)


def test_libur_semester_warung_kos(harian):
    e = _total_per_tanggal(harian[harian["store_id"] == "E"])
    assert e["2026-07"].mean() / e["2025-10"].mean() == pytest.approx(0.6, abs=0.1)


def test_libur_sekolah_hanya_jajanan(harian):
    c = harian[harian["store_id"] == "C"]
    jajan = c["kategori"].isin(KATEGORI_SEKOLAH) & (c["kategori"] != "alat tulis")
    for m, harapan in ((jajan, 0.5), (~c["kategori"].isin(KATEGORI_SEKOLAH), 1.0)):
        t = _total_per_tanggal(c[m])
        assert t["2026-06-22":"2026-07-04"].mean() / t["2025-10"].mean() == pytest.approx(harapan, abs=0.15)


def test_tahun_ajaran_baru(harian):
    t = _total_per_tanggal(harian[(harian["kategori"] == "alat tulis") & (harian["store_id"] != "C")])
    pembanding = pd.concat([t["2026-06-01":"2026-06-14"], t["2026-08-20":"2026-09-30"]])
    assert t["2026-07-05":"2026-07-18"].mean() / pembanding.mean() > 1.5


def test_borongan_muncul_sebagai_lonjakan(harian, resep):
    bulk = harian[harian["prob_bulk"] > 0]
    lonjakan = (bulk["permintaan"] > bulk["qty_maks"]).groupby([bulk["store_id"], bulk["kode"]]).mean()
    harapan = resep[resep["prob_bulk"] > 0].groupby(["store_id", "kode"])["prob_bulk"].first()
    assert lonjakan.mean() / harapan.mean() == pytest.approx(1, abs=0.3)

    tanpa = harian[(harian["prob_bulk"] == 0) & (harian["rata_per_beli"] == 0)]
    assert (tanpa["permintaan"] > tanpa["qty_maks"] * 1.5).sum() == 0


def test_stok_kosong_wajar(harian):
    per_barang = harian.groupby(["store_id", "kode"]).agg(
        kosong=("stok_akhir", lambda s: (s == 0).mean()), terjual=("terjual", "sum"),
        permintaan=("permintaan", "sum"))
    assert (per_barang["kosong"] < 0.5).all()
    assert not ((per_barang["terjual"] == 0) & (per_barang["permintaan"] > 0)).any()
    per_warung = per_barang.groupby("store_id")[["terjual", "permintaan"]].sum()
    assert (1 - per_warung["terjual"] / per_warung["permintaan"] < 0.08).all()


def test_komposisi_kuadran(harian):
    def kuadran(q: pd.Series) -> str:
        nz = q[q > 0]
        adi = len(q) / len(nz) if len(nz) else np.inf
        cv2 = (nz.std(ddof=1) / nz.mean()) ** 2 if len(nz) > 1 else 0.0
        if adi < AMBANG_ADI:
            return "smooth" if cv2 < AMBANG_CV2 else "erratic"
        return "intermittent" if cv2 < AMBANG_CV2 else "lumpy"

    k = harian.groupby(["store_id", "kode"])["terjual"].apply(kuadran)
    porsi = pd.crosstab(k.index.get_level_values("store_id"), k, normalize="index")
    assert ((porsi["intermittent"] + porsi["lumpy"]).between(0.6, 0.9)).all()
    assert (porsi["lumpy"] >= 0.05).all()
    assert (porsi["smooth"].between(0.08, 0.25)).all()


def test_urutan_omzet(harian):
    harga = harian["kelas_harga"].map(HARGA_KELAS).where(harian["kategori"] != "rokok", 27_000)
    omzet = (harian["terjual"] * harga).groupby(harian["store_id"]).sum()
    assert list(omzet.sort_values().index) == ["A", "C", "E", "B", "D"]
