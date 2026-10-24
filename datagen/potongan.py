"""Pemilihan kandidat yang akan diklasifikasikan, lalu pemotongannya ke beberapa berkas.

Pemilihan berjalan dalam tiga lapis:

1. Kuota per kategori, dihitung dari kebutuhan warung terbesar, sehingga perbandingan
   antar kategori mengikuti isi rak warung dan kategori tidak saling berebut tempat.
2. Merek inti tiap kategori diambil lebih dahulu dengan batas per merek, sehingga
   merek yang hampir pasti ada di warung terwakili tanpa memonopoli kategori.
3. Sisa kuota diisi acak dari kandidat lain pada kategori yang sama, untuk ekor
   panjang dan keragaman antar warung.

Hasil dipotong per 500 barang agar klasifikasi dapat dikerjakan bertahap dan setiap
potongan yang selesai langsung tersimpan.
"""

import math
import sys

import numpy as np
import pandas as pd

from datagen.katalog_induk import DIR_INDUK
from datagen.saring import BERKAS_KANDIDAT, _pola

BERKAS_TERPILIH = DIR_INDUK / "terpilih.csv"
DIR_POTONGAN = DIR_INDUK / "potongan"
DIR_KLASIFIKASI = DIR_INDUK / "klasifikasi"

SEED = 20261021
UKURAN_POTONGAN = 500
UKURAN_WARUNG_TERBESAR = 900
# Gabungan barang lima warung diperkirakan 1,3 kali kebutuhan warung terbesar,
# karena barang ekor yang dipilih tiap warung berbeda-beda.
PENGALI_SEBARAN = 1.3
# Merek inti paling banyak mengisi porsi ini dari kuota kategori, sisanya untuk
# barang acak di luar merek inti.
BATAS_PORSI_INTI = 0.6

# (porsi kategori di rak warung, perkiraan porsi kandidat yang ditolak saat klasifikasi).
# Porsi rak merupakan penilaian; porsi tolak diperkirakan dari sampel kandidat.
PORSI = {
    "snack": (0.09, 0.35),
    "sabun dan sampo": (0.08, 0.55),
    "roti dan biskuit": (0.08, 0.40),
    "bumbu": (0.08, 0.45),
    "permen dan coklat": (0.06, 0.40),
    "minuman ringan": (0.06, 0.35),
    "susu": (0.05, 0.45),
    "kopi": (0.05, 0.30),
    "mie instan": (0.05, 0.20),
    "deterjen dan pembersih": (0.05, 0.35),
    "rokok": (0.04, 0.10),
    "pembalut dan bayi": (0.04, 0.35),
    "obat warung": (0.04, 0.50),
    "rumah tangga": (0.04, 0.45),
    "teh": (0.03, 0.35),
    "perawatan gigi": (0.03, 0.35),
    "beras dan pokok": (0.03, 0.40),
    "alat tulis": (0.03, 0.45),
    "air minum": (0.02, 0.30),
    "minyak goreng": (0.02, 0.30),
    "makanan kaleng": (0.02, 0.50),
    "es krim": (0.01, 0.30),
}

# Merek inti per kategori: (label, kata kunci, batas jumlah barang). Batas sebanding
# dengan banyaknya varian merek tersebut yang lazim dijumpai di rak warung.
MEREK_INTI = {
    "mie instan": [
        ("Indomie", ["INDOMIE"], 15), ("Mie Sedaap", ["MIE SEDAAP", "MIE SEDAP", "SEDAP MIE"], 10),
        ("Sarimi", ["SARIMI"], 6), ("Pop Mie", ["POP MIE"], 6),
        ("Supermi", ["SUPERMI"], 5), ("Mie Gelas", ["MIE GELAS"], 3),
    ],
    "rokok": [
        ("Sampoerna", ["SAMPOERNA"], 8), ("Gudang Garam", ["GUDANG GARAM", "GG MILD", "G G"], 7),
        ("Djarum", ["DJARUM"], 6), ("Surya", ["SURYA"], 5),
        ("Dji Sam Soe", ["DJI SAM SOE"], 3), ("Marlboro", ["MARLBORO", "MALBORO"], 3),
    ],
    "kopi": [
        ("Kapal Api", ["KAPAL API"], 8), ("ABC", ["ABC"], 6), ("Good Day", ["GOOD DAY"], 6),
        ("Torabika", ["TORABIKA"], 6), ("Luwak", ["LUWAK"], 4),
        ("Indocafe", ["INDOCAFE"], 4), ("Nescafe", ["NESCAFE"], 4),
    ],
    "teh": [
        ("Sariwangi", ["SARIWANGI"], 6), ("Sosro", ["SOSRO"], 6), ("Teh Pucuk", ["TEH PUCUK"], 4),
        ("Frestea", ["FRESTEA"], 3), ("Teh Gelas", ["TEH GELAS"], 3), ("2 Tang", ["2 TANG", "2TANG"], 3),
    ],
    "susu": [
        ("Frisian Flag", ["FRISIAN FLAG", "BENDERA"], 10), ("Indomilk", ["INDOMILK"], 8),
        ("Dancow", ["DANCOW"], 8), ("Ultra Milk", ["ULTRA MILK", "ULTRAMILK"], 8),
        ("Milo", ["MILO"], 5), ("Bear Brand", ["BEAR BRAND"], 4),
    ],
    "air minum": [
        ("Aqua", ["AQUA"], 8), ("Le Minerale", ["LE MINERALE"], 5),
        ("Cleo", ["CLEO"], 3), ("Ades", ["ADES"], 3),
    ],
    "minuman ringan": [
        ("Coca Cola", ["COCA COLA", "COCA-COLA", "SPRITE", "FANTA"], 6),
        ("Nutrisari", ["NUTRISARI"], 5), ("Marimas", ["MARIMAS"], 4), ("Pop Ice", ["POP ICE"], 4),
        ("Pocari", ["POCARI"], 4), ("Mizone", ["MIZONE"], 4),
        ("Extra Joss", ["EXTRA JOSS", "EXTRA JOOS"], 4), ("Kuku Bima", ["KUKUBIMA", "KUKU BIMA"], 4),
        ("Larutan Kaki Tiga", ["LARUTAN", "KAKI TIGA"], 4), ("Adem Sari", ["ADEM SARI"], 3),
        ("Yakult", ["YAKULT"], 2),
    ],
    "minyak goreng": [
        ("Bimoli", ["BIMOLI"], 5), ("Filma", ["FILMA"], 4), ("Sunco", ["SUNCO"], 4),
        ("Sania", ["SANIA"], 3), ("Fortune", ["FORTUNE"], 3),
    ],
    "beras dan pokok": [
        ("Rose Brand", ["ROSE BRAND"], 5), ("Bihun", ["BIHUN", "BIHON"], 5), ("Beras", ["BERAS"], 5),
        ("Gulaku", ["GULAKU"], 4), ("Segitiga Biru", ["SEGITIGA BIRU"], 4),
        ("Agar-agar", ["AGAR", "AGAR2"], 4), ("Maizena", ["MAIZENA"], 3),
    ],
    "makanan kaleng": [
        ("Sarden", ["SARDEN", "SARDINES"], 6), ("Pronas", ["PRONAS"], 5), ("Kornet", ["KORNET"], 4),
    ],
    "bumbu": [
        ("Royco", ["ROYCO"], 10), ("ABC", ["ABC"], 10), ("Masako", ["MASAKO"], 8),
        ("Bango", ["BANGO"], 6), ("Sasa", ["SASA"], 6), ("Ajinomoto", ["AJINOMOTO"], 5),
        ("Sajiku", ["SAJIKU"], 4), ("Kobe", ["KOBE"], 4), ("Kara", ["KARA"], 4), ("Maggi", ["MAGGI"], 3),
    ],
    "permen dan coklat": [
        ("Kopiko", ["KOPIKO"], 6), ("Relaxa", ["RELAXA"], 5), ("Mentos", ["MENTOS"], 5),
        ("Yupi", ["YUPI"], 5), ("Silverqueen", ["SILVERQUEEN"], 5), ("Beng Beng", ["BENG BENG"], 4),
        ("Delfi", ["DELFI"], 4), ("Hexos", ["HEXOS"], 3), ("Chacha", ["CHACHA"], 3),
        ("Kiss", ["KISS"], 3), ("Fruitella", ["FRUITELLA"], 3), ("Happydent", ["HAPPYDENT"], 3),
    ],
    "roti dan biskuit": [
        ("Roma", ["ROMA"], 10), ("Nabati", ["NABATI", "RICHEESE"], 8), ("Khong Guan", ["KHONG GUAN"], 6),
        ("Oreo", ["OREO"], 6), ("Tango", ["TANGO"], 6), ("Sari Roti", ["SARI ROTI"], 5),
        ("Biskuat", ["BISKUAT"], 4), ("Marie", ["MARIE"], 4), ("Good Time", ["GOOD TIME"], 4),
        ("Slai Olai", ["SLAI OLAI"], 3),
    ],
    "snack": [
        ("Chitato", ["CHITATO"], 8), ("Garuda", ["GARUDA"], 8), ("Taro", ["TARO"], 6),
        ("Qtela", ["QTELA"], 6), ("Dua Kelinci", ["DUA KELINCI"], 6), ("Chiki", ["CHIKI"], 5),
        ("Gery", ["GERY", "CHOCOLATOS"], 5), ("Lay's", ["LAYS", "LAY'S"], 4),
        ("Kusuka", ["KUSUKA"], 4), ("Piattos", ["PIATTOS"], 4), ("Oishi", ["OISHI"], 4),
        ("Momogi", ["MOMOGI"], 3),
    ],
    "perawatan gigi": [
        ("Pepsodent", ["PEPSODENT"], 10), ("Ciptadent", ["CIPTADENT"], 6),
        ("Sikat gigi", ["SIKAT GIGI", "SIGI"], 6), ("Close Up", ["CLOSE UP", "CLOSE-UP"], 5),
    ],
    "sabun dan sampo": [
        ("Lifebuoy", ["LIFEBUOY", "LIFEBOY"], 15), ("Lux", ["LUX"], 10), ("Sunsilk", ["SUNSILK"], 10),
        ("Giv", ["GIV"], 8), ("Pantene", ["PANTENE"], 8), ("Clear", ["CLEAR"], 8),
        ("Nuvo", ["NUVO"], 6), ("Shinzui", ["SHINZUI"], 6), ("Emeron", ["EMERON"], 6),
        ("Dettol", ["DETTOL"], 5), ("Head & Shoulders", ["H&S", "HEAD & S", "HEAD & SHOULDERS"], 5),
        ("Zinc", ["ZINC"], 5),
    ],
    "deterjen dan pembersih": [
        ("Rinso", ["RINSO"], 8), ("So Klin", ["SO KLIN", "SOKLIN"], 8), ("Daia", ["DAIA"], 6),
        ("Attack", ["ATTACK"], 6), ("Molto", ["MOLTO"], 6), ("Sunlight", ["SUNLIGHT"], 6),
        ("Mama Lemon", ["MAMA LEMON"], 4), ("Wipol", ["WIPOL"], 3), ("Bayclin", ["BAYCLIN"], 3),
        ("Superpell", ["SUPERPELL"], 3),
    ],
    "pembalut dan bayi": [
        ("Charm", ["CHARM"], 8), ("Laurier", ["LAURIER"], 6), ("MamyPoko", ["MAMYPOKO", "MAMY POKO"], 6),
        ("Sweety", ["SWEETY"], 6), ("Softex", ["SOFTEX"], 5), ("Johnson", ["JOHNSON", "JHONSON", "JHONSONS"], 4),
        ("My Baby", ["MY BABY"], 4), ("Kotex", ["KOTEX"], 3), ("Zwitsal", ["ZWITSAL"], 3),
    ],
    "rumah tangga": [
        ("Baygon", ["BAYGON"], 6), ("Tisu", ["TISSUE", "TISU", "TISSU"], 6), ("Hit", ["HIT"], 5),
        ("Korek", ["KOREK"], 5), ("Baterai", ["BATERAI", "BATTERY", "ALKALINE"], 5),
        ("Soffell", ["SOFFELL", "SOFFEL"], 4), ("Vape", ["VAPE"], 3), ("Lilin", ["LILIN"], 3),
        ("Kapur barus", ["KAPUR BARUS", "BARUS"], 3),
    ],
    "obat warung": [
        ("Bodrex", ["BODREX"], 5), ("Paramex", ["PARAMEX"], 4), ("Promag", ["PROMAG"], 4),
        ("Tolak Angin", ["TOLAK ANGIN"], 4), ("Antangin", ["ANTANGIN"], 4), ("OBH", ["OBH"], 4),
        ("Minyak kayu putih", ["KAYU PUTIH", "MKP"], 4), ("Mixagrip", ["MIXAGRIP"], 3),
        ("Cap Gajah", ["CAP GAJAH"], 3), ("Balsem", ["BALSEM"], 3), ("Koyo", ["KOYO"], 3),
        ("Vicks", ["VICKS"], 3), ("Insto", ["INSTO"], 2), ("Entrostop", ["ENTROSTOP"], 2),
        ("Konidin", ["KONIDIN"], 2), ("Fresh Care", ["FRESH CARE"], 2),
    ],
    "alat tulis": [
        ("Sinar Dunia", ["SINAR DUNIA", "SIDU"], 6), ("Buku tulis", ["BUKU TULIS", "BK TULIS"], 6),
        ("Pensil", ["PENSIL"], 5), ("Pulpen", ["PULPEN", "BOLPOIN"], 5), ("Kiky", ["KIKY"], 4),
        ("Penghapus", ["PENGHAPUS"], 3), ("Penggaris", ["PENGGARIS"], 3),
        ("Snowman", ["SNOWMAN"], 3), ("Joyko", ["JOYKO"], 3),
    ],
    "es krim": [
        ("Wall's", ["WALL'S", "WALLS", "WALL S"], 5), ("Paddle Pop", ["PADDLE POP"], 3),
        ("Campina", ["CAMP"], 3),
    ],
}


def hitung_kuota(kandidat: pd.DataFrame) -> pd.Series:
    """Kuota per kategori, dibatasi oleh jumlah nama unik yang tersedia."""
    tersedia = kandidat.drop_duplicates("nama").groupby("kategori_kasar").size()
    kuota = {
        kategori: min(
            int(tersedia.get(kategori, 0)),
            math.ceil(UKURAN_WARUNG_TERBESAR * rak * PENGALI_SEBARAN / (1 - tolak)),
        )
        for kategori, (rak, tolak) in PORSI.items()
    }
    return pd.Series(kuota, name="kuota")


def pilih_kategori(kandidat_kategori: pd.DataFrame, kuota: int, merek_inti: list,
                   rng: np.random.Generator) -> pd.DataFrame:
    """Memilih barang satu kategori: merek inti lebih dahulu, sisanya acak."""
    sisa = kandidat_kategori.drop_duplicates("nama").copy()
    nama_besar = sisa["nama"].str.upper()
    batas_inti = math.floor(kuota * BATAS_PORSI_INTI)
    terpilih = []

    for label, kata, batas in merek_inti:
        ruang = min(batas, batas_inti - sum(len(t) for t in terpilih))
        if ruang <= 0:
            break
        cocok = sisa[nama_besar.loc[sisa.index].str.contains(_pola(kata))]
        ambil = cocok.sample(min(ruang, len(cocok)), random_state=rng.integers(2**31))
        terpilih.append(ambil.assign(sumber=f"inti: {label}"))
        sisa = sisa.drop(ambil.index)

    ruang = kuota - sum(len(t) for t in terpilih)
    acak = sisa.sample(min(ruang, len(sisa)), random_state=rng.integers(2**31))
    terpilih.append(acak.assign(sumber="acak"))
    return pd.concat(terpilih)


def pilih_semua(kandidat: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    kuota = hitung_kuota(kandidat)
    bagian = [
        pilih_kategori(kandidat[kandidat["kategori_kasar"] == kategori], int(kuota[kategori]),
                       MEREK_INTI.get(kategori, []), rng)
        for kategori in PORSI
    ]
    return (pd.concat(bagian)
            .sort_values(["kategori_kasar", "nama"])
            .reset_index(drop=True))


def tulis_potongan(terpilih: pd.DataFrame) -> int:
    """Menulis potongan berurutan menurut kategori, agar barang sejenis dikerjakan bersama."""
    DIR_POTONGAN.mkdir(parents=True, exist_ok=True)
    for lama in DIR_POTONGAN.glob("potongan_*.csv"):
        lama.unlink()
    jumlah = math.ceil(len(terpilih) / UKURAN_POTONGAN)
    for i in range(jumlah):
        bagian = terpilih.iloc[i * UKURAN_POTONGAN:(i + 1) * UKURAN_POTONGAN]
        bagian[["kode", "nama", "kategori_kasar"]].to_csv(
            DIR_POTONGAN / f"potongan_{i + 1:02d}.csv", index=False)
    return jumlah


def cetak_laporan(terpilih: pd.DataFrame, kandidat: pd.DataFrame) -> None:
    kuota = hitung_kuota(kandidat)
    print(f"{'kategori':24s}{'kuota':>6}{'terisi':>7}{'inti':>6}{'acak':>6}")
    peringatan = []
    for kategori in PORSI:
        isi = terpilih[terpilih["kategori_kasar"] == kategori]
        inti = isi["sumber"].str.startswith("inti").sum()
        print(f"{kategori:24s}{kuota[kategori]:>6}{len(isi):>7}{inti:>6}{len(isi) - inti:>6}")
        per_merek = isi["sumber"].value_counts()
        for label, _, _ in MEREK_INTI.get(kategori, []):
            if per_merek.get(f"inti: {label}", 0) == 0:
                peringatan.append(f"{kategori}: {label}")
    print(f"{'TOTAL':24s}{kuota.sum():>6}{len(terpilih):>7}")
    print()
    if peringatan:
        print("PERINGATAN, merek inti tanpa barang terpilih:")
        for p in peringatan:
            print(f"  {p}")
    else:
        print("seluruh merek inti terwakili")


if __name__ == "__main__":
    sudah_ada = list(DIR_KLASIFIKASI.glob("potongan_*.csv")) if DIR_KLASIFIKASI.exists() else []
    if sudah_ada and "--paksa" not in sys.argv:
        sys.exit(f"{len(sudah_ada)} hasil klasifikasi sudah ada di {DIR_KLASIFIKASI}. "
                 "Memilih ulang akan membuat potongan tidak lagi cocok dengan hasilnya. "
                 "Jalankan dengan --paksa apabila memang disengaja.")

    kandidat = pd.read_csv(BERKAS_KANDIDAT, dtype=str)
    terpilih = pilih_semua(kandidat)
    terpilih.to_csv(BERKAS_TERPILIH, index=False)
    jumlah = tulis_potongan(terpilih)

    cetak_laporan(terpilih, kandidat)
    print(f"\n{len(terpilih)} barang terpilih, dipotong menjadi {jumlah} berkas di {DIR_POTONGAN}")
