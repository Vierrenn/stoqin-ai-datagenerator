"""Pemilihan barang tambahan setelah klasifikasi pertama.

Klasifikasi pertama menunjukkan beberapa kategori kekurangan barang lolos dan beberapa
barang penting tidak terambil oleh pemilihan acak. Tambahan ditulis sebagai potongan
tersendiri agar hasil klasifikasi sebelumnya tidak terganggu:

- tambahan_01: barang satuan yang terlewat dan tambahan acak untuk kategori yang kurang
- tambahan_02: barang terlaris warung yang terlewat, diambil langsung dari katalog induk
  karena sebagian tidak tertangkap kamus saringan
- tambahan_03: es krim satuan, karena kuota es krim di pemilihan awal terlalu kecil
  dibanding isi freezer warung
"""

import sys

import numpy as np
import pandas as pd

from datagen.katalog_induk import BERKAS_KELUARAN as BERKAS_KATALOG
from datagen.potongan import BERKAS_TERPILIH, DIR_KLASIFIKASI, DIR_POTONGAN
from datagen.saring import BERKAS_KANDIDAT

SEED = 20261024

BARANG_UTAMA = [
    "INDOMIE GORENG", "Gudang Garam Merah", "GG FILTER", "GG SURYA 12", "DJARUM 76",
    "DJARUM 76 ISI 16", "DJARUM COKLAT 12", "TEH PUCUK HARUM 350ML", "SARIWANGI 25X1.85G",
    "FRISIAN FLAG PUTIH KLG 375g", "FRISIAN FLAG COKLAT KLG 375g", "BENDERA SKM 45ML 1 S",
    "ROYCO RASA SAPI 10 GR", "BANGO 14ML", "NUVO FAMILY 80G MERAH/BALANCE",
    "NUVO FAMILY 80G BIRU/GENTLE", "SOKLIN SOFTENER FINE SACHET", "VAPE BAKAR JUMBO",
]

TAMBAHAN_ES_KRIM = 40
# Es krim kemasan keluarga (350 ml ke atas), isi banyak, dan lini kemasan besar tidak
# dijual per batang di freezer warung.
_POLA_ES_KRIM_BESAR = (r"\b(?:3[5-9]\d|[4-9]\d\d|\d{4}) ?(?:ML|G|GR)\b|\b\d ?LT?\b|1LT|\bF/?P\b"
                       r"|\bM/?P\b|SELEC|DREAMY|VIENNETTA|EXTRA C|DUNG|TRIPLE|NEOPOL|IN ?1"
                       r"|\b\d+ ?['`’]?S\b|\dX|X\d|ISI \d|MINI CORNET|\bMOO ACTIVE")

# Barang satuan yang ada di katalog tetapi tidak terambil pemilihan acak.
BARANG_WAJIB = [
    "INDOMIE KARI AYAM 72g", "Energen Cokelat", "Energen Vanila", "INDOCAFE COFEMIX 20 GR",
    "CLOSE UP FIRE-FREEZ 65g", "CLOSE UP 100G DIAMOND ATTRACTION",
    "CLOSE UP CRISTAL 110 GR NEW", "CLOSE UP DEEP ACTION",
]

# Jumlah tambahan acak per kategori, kira-kira dua kali kekurangannya karena sekitar
# separuh kandidat biasanya ditolak saat klasifikasi.
TAMBAHAN_ACAK = {"kopi": 20, "permen dan coklat": 15, "air minum": 12, "teh": 10}

# Kandidat yang hampir pasti ditolak tidak diambil: kemasan isi banyak, toples, kaleng,
# kemasan 100 gram ke atas, dan kode negara lain.
_POLA_KULAKAN = (r"\d+ ?['`’]?S\b|\dX|X\d|TOPLES|\bJAR\b|\bBAG\b|RENCENG|\bRCG\b|\bBOX\b"
                 r"|KALENG|\bKLG\b|\b\d{3,4} ?(?:G|GR|GRAM)\b")
_AWALAN_ASING = ("480", "955", "885", "888", "690", "691", "692", "693", "880", "471",
                 "931", "893", "489")


def sisa_kandidat(kandidat: pd.DataFrame, terpilih: pd.DataFrame) -> pd.DataFrame:
    sisa = kandidat[~kandidat["kode"].isin(terpilih["kode"])
                    & ~kandidat["nama"].isin(terpilih["nama"])]
    return sisa.drop_duplicates("nama")


def pilih_tambahan(sisa: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    wajib = sisa[sisa["nama"].isin(BARANG_WAJIB)]
    hilang = sorted(set(BARANG_WAJIB) - set(wajib["nama"]))
    if hilang:
        raise ValueError(f"barang wajib tidak ditemukan di kandidat: {hilang}")

    layak = sisa[~sisa["nama"].str.upper().str.contains(_POLA_KULAKAN)
                 & ~sisa["kode"].str.startswith(_AWALAN_ASING)
                 & ~sisa["kode"].isin(wajib["kode"])]
    acak = [
        layak[layak["kategori_kasar"] == kategori].sample(jumlah, random_state=rng.integers(2**31))
        for kategori, jumlah in TAMBAHAN_ACAK.items()
    ]
    return (pd.concat([wajib, *acak])
            .sort_values(["kategori_kasar", "nama"])
            .reset_index(drop=True))


def pilih_utama(katalog: pd.DataFrame, kandidat: pd.DataFrame,
                sudah: pd.DataFrame) -> pd.DataFrame:
    """Barang utama diambil dari katalog induk; kategori kasar diisi dari kandidat bila ada."""
    utama = katalog[katalog["nama"].isin(BARANG_UTAMA) & ~katalog["kode"].isin(sudah["kode"])]
    hilang = sorted(set(BARANG_UTAMA) - set(utama["nama"]))
    if hilang:
        raise ValueError(f"barang utama tidak ditemukan atau sudah terpilih: {hilang}")
    kasar = kandidat.set_index("kode")["kategori_kasar"]
    utama = utama.assign(kategori_kasar=utama["kode"].map(kasar).fillna(""))
    return utama.sort_values(["kategori_kasar", "nama"]).reset_index(drop=True)


def pilih_es_krim(kandidat: pd.DataFrame, sudah: pd.DataFrame,
                  seed: int = SEED) -> pd.DataFrame:
    es = kandidat[(kandidat["kategori_kasar"] == "es krim")
                  & ~kandidat["kode"].isin(sudah["kode"])
                  & ~kandidat["nama"].isin(sudah["nama"])].drop_duplicates("nama")
    es = es[~es["nama"].str.upper().str.contains(_POLA_ES_KRIM_BESAR)
            & ~es["kode"].str.startswith(_AWALAN_ASING)]
    pilihan = es.sample(min(TAMBAHAN_ES_KRIM, len(es)), random_state=seed)
    return pilihan.sort_values("nama").reset_index(drop=True)


def tulis(nama: str, barang: pd.DataFrame) -> None:
    if (DIR_KLASIFIKASI / f"{nama}.csv").exists() and "--paksa" not in sys.argv:
        print(f"{nama}: hasil klasifikasi sudah ada, dilewati")
        return
    berkas = DIR_POTONGAN / f"{nama}.csv"
    barang[["kode", "nama", "kategori_kasar"]].to_csv(berkas, index=False)
    print(f"{nama}: {len(barang)} barang ditulis ke {berkas}")


if __name__ == "__main__":
    katalog = pd.read_csv(BERKAS_KATALOG, dtype=str)
    kandidat = pd.read_csv(BERKAS_KANDIDAT, dtype=str)
    terpilih = pd.read_csv(BERKAS_TERPILIH, dtype=str)

    tambahan = pilih_tambahan(sisa_kandidat(kandidat, terpilih))
    tulis("tambahan_01", tambahan)
    utama = pilih_utama(katalog, kandidat, pd.concat([terpilih, tambahan]))
    tulis("tambahan_02", utama)
    tulis("tambahan_03", pilih_es_krim(kandidat, pd.concat([terpilih, tambahan, utama])))
