import pandas as pd
import pytest

from datagen.kalender import faktor_gajian

KEKUATAN = 0.08


def _faktor_sebulan(awal_bulan: str, kekuatan: float = KEKUATAN) -> pd.Series:
    hari = pd.date_range(awal_bulan, periods=pd.Timestamp(awal_bulan).days_in_month)
    return pd.Series([faktor_gajian(t, kekuatan) for t in hari], index=hari.day)


@pytest.mark.parametrize("awal_bulan", ["2025-02-01", "2024-02-01", "2025-04-01", "2025-01-01"])
def test_rata_rata_sebulan_satu(awal_bulan):
    assert _faktor_sebulan(awal_bulan).mean() == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("awal_bulan", ["2025-02-01", "2025-04-01", "2025-01-01"])
def test_puncak_di_pergantian_bulan(awal_bulan):
    faktor = _faktor_sebulan(awal_bulan)
    assert faktor.idxmax() in (1, len(faktor))
    assert faktor.max() == pytest.approx(1 + KEKUATAN, abs=0.002)


@pytest.mark.parametrize("awal_bulan", ["2025-02-01", "2025-04-01", "2025-01-01"])
def test_terendah_di_tengah_bulan(awal_bulan):
    faktor = _faktor_sebulan(awal_bulan)
    assert 14 <= faktor.idxmin() <= 16
    assert faktor.min() == pytest.approx(1 - KEKUATAN, abs=0.002)


def test_kekuatan_nol_datar():
    assert (_faktor_sebulan("2025-01-01", kekuatan=0) == 1.0).all()


def test_tidak_ada_loncatan_antar_hari():
    hari = pd.date_range("2025-01-01", "2025-12-31")
    faktor = pd.Series([faktor_gajian(t, KEKUATAN) for t in hari])
    assert faktor.diff().abs().max() < 0.02
