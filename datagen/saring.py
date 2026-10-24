"""Penyaringan katalog induk menjadi kandidat barang warung berdasarkan kata kunci.

Hasil penyaringan bersifat kasar dan sengaja longgar. Ketepatan kategori dan
kecocokan dengan warung ditetapkan pada tahap klasifikasi berikutnya; tahap ini
hanya membuang barang yang jelas bukan barang warung.

Kamus disusun dari pembacaan 900 kelompok kata pertama nama barang yang paling
sering muncul di antara barang yang tidak tertangkap, mencakup sekitar tiga
perempat barang tersebut. Penamaan pada katalog IPOS banyak memakai singkatan
(KCG untuk kacang, BMB untuk bumbu, MKP untuk minyak kayu putih) dan istilah
bahasa Inggris, sehingga keduanya ikut dimasukkan.
"""

import re

import pandas as pd

from datagen.katalog_induk import BERKAS_KELUARAN as BERKAS_KATALOG
from datagen.katalog_induk import DIR_INDUK

BERKAS_KANDIDAT = DIR_INDUK / "kandidat.csv"

# Diperiksa sebelum kamus kategori. Barang yang mengandung salah satu kata ini
# dibuang walaupun cocok dengan kategori warung, misalnya botol susu bayi yang
# akan tertangkap kata kunci SUSU.
PENGECUALIAN = [
    # perabot, alat dapur, elektronik, sandang
    "BOTOL SUSU", "DOT", "BASKOM", "TALENAN", "HANGER", "STAPLER", "KODAK", "FILM",
    "PANCI", "WAJAN", "SENDOK", "GARPU", "PISAU", "PIRING", "MANGKOK", "MANGKUK",
    "EMBER", "RAK", "KERANJANG", "CHARGER", "KABEL", "HEADSET", "CASING", "BONEKA",
    "KAOS", "BAJU", "CELANA", "HANDUK", "KOTAK SABUN", "TEMPAT SABUN",
    # kosmetik dan wewangian
    "MAYBELINE", "MAYBELLINE", "PIXY", "REVLON", "LIPSTICK", "LIPS", "MASCARA",
    "EYELINER", "EYE SHADOW", "BLUSH", "FOUNDATION", "TWC", "CUSHION", "KUTEK",
    "NAIL", "PARFUM", "PERFUME", "DEO", "LINER", "SPRITZ", "B/L", "BODY LOTION",
    "H&B", "HAND & BODY", "HAND BODY",
    # minuman beralkohol dan makanan hewan
    "BEER", "BIR", "PILSEN", "STOUT", "GIN", "WHISKY", "VODKA", "WINE",
    "WHISKAS", "ALPO", "FRISKIES", "MKN KUCING",
    # salah tangkap nama merek
    "VITA CHARM",
]

# Kemasan karton distributor, misalnya "ROYCO 96 x 17G". Warung menjual satuannya.
# Pengali minimal 12 dan diapit spasi, agar kemasan eceran seperti
# "SARIWANGI 50X1.85G" (kotak isi 50 kantong) tidak ikut terbuang. Dua
# pengali berturut-turut, seperti "8 x 6 x 100G", selalu berarti karton.
_POLA_KARTON = re.compile(r"(?<![0-9.])(?:1[2-9]|[2-9][0-9]|[1-9][0-9]{2})\s+X\s+[0-9]"
    r"|[0-9]+\s*X\s*[0-9]+\s*X\s*[0-9]")

# Awalan "X " pada katalog IPOS menandai barang yang sudah tidak dijual.
_POLA_TIDAK_AKTIF = re.compile(r"^X\s")

# Awalan "O " pada katalog IPOS menandai obat. Isinya campuran obat warung dan obat
# apotek; pemilahannya diserahkan ke tahap klasifikasi.
_POLA_OBAT = re.compile(r"^O\s")

# Urutan menentukan prioritas: barang yang cocok dengan beberapa kategori masuk
# ke kategori yang tercantum lebih dahulu, sehingga kategori yang lebih spesifik
# diletakkan di atas. Contoh: KOPI SUSU masuk kopi, bukan susu.
KAMUS = {
    "obat warung": [
        "BODREX", "PARAMEX", "PROMAG", "TOLAK ANGIN", "ANTANGIN", "MIXAGRIP",
        "PANADOL", "DECOLGEN", "INSTO", "KAYU PUTIH", "MKP", "BALSEM", "KOYO",
        "ENTROSTOP", "OSKADON", "NEOZEP", "INZA", "SANMOL", "WOODS", "KONIDIN",
        "FRESH CARE", "VICKS", "CAP LANG", "CAP GAJAH", "MINYAK TAWON",
        "MINYAK ANGIN", "GANDAPURA", "HANSAPLAST", "SALONPAS", "OBH", "CURCUMA", "JAMU",
    ],
    "rokok": [
        "SAMPOERNA", "GUDANG GARAM", "DJARUM", "SURYA", "MARLBORO", "MALBORO",
        "LA LIGHTS", "DJI SAM SOE", "CLAS MILD", "U MILD", "GG MILD", "DUNHILL",
        "ROKOK",
    ],
    "deterjen dan pembersih": [
        "RINSO", "SO KLIN", "SOKLIN", "DAIA", "ATTACK", "MOLTO", "SUNLIGHT",
        "MAMA LEMON", "DOWNY", "BAYCLIN", "WIPOL", "SUPERPELL", "PORSTEX", "VIXAL",
        "DETERJEN", "DETERGENT", "PEWANGI", "SABUN CUCI", "SURF", "TIDE",
        "SCOTCH BRITE", "SCOTCH-BRITE", "SABUT", "PEMUTIH",
    ],
    "perawatan gigi": [
        "PEPSODENT", "CIPTADENT", "CLOSE UP", "CLOSE-UP", "SIKAT GIGI", "SIGI", "ODOL",
        "ENZIM", "COLGATE", "SENSODYNE", "SYSTEMA",
    ],
    "sabun dan sampo": [
        "LIFEBUOY", "LIFEBOY", "LUX", "GIV", "NUVO", "SHINZUI", "DETTOL", "SABUN",
        "SOAP", "SHAMPOO", "SHAMPO", "SHP", "SUNSILK", "CLEAR", "PANTENE", "DOVE",
        "EMERON", "HEAD & SHOULDERS", "HEAD & S", "H&S", "ZINC", "PALMOLIVE", "ELLIPS",
        "LIP ICE",
    ],
    "pembalut dan bayi": [
        "CHARM", "LAURIER", "SOFTEX", "KOTEX", "WHISPER", "HERS", "MODESS", "PEMBALUT",
        "MAMYPOKO", "MAMY POKO", "SWEETY", "POPOK", "POPOKU", "PAMPERS", "DRYPERS",
        "MY BABY", "BEDAK BAYI", "JOHNSON", "JHONSON", "JHONSONS", "ZWITSAL", "CUSSONS",
    ],
    "rumah tangga": [
        "BATERAI", "BATTERY", "ALKALINE", "EVEREADY", "ENERGIZER", "KOREK", "LILIN",
        "TISSUE", "TISU", "TISSU", "OBAT NYAMUK", "BAYGON", "HIT", "VAPE",
        "KAPUR BARUS", "BARUS", "SOFFELL", "SOFFEL", "AUTAN", "STELLA", "INSECT",
        "LEM TIKUS", "LAMPU", "PASEO",
    ],
    "es krim": [
        "WALL'S", "WALLS", "WALL S", "PADDLE POP", "CORNETTO", "CAMP", "AICE",
    ],
    "mie instan": [
        "INDOMIE", "SARIMI", "SUPERMI", "MIE SEDAAP", "MIE SEDAP", "POP MIE",
        "MIE GELAS", "LEMONILO", "MIE INSTAN", "MI INSTAN", "INTERMI", "MIE", "RAMEN",
        "NOODLE", "NOODLES",
    ],
    "air minum": [
        "AQUA", "LE MINERALE", "AIR MINERAL", "MINERAL WATER", "CLEO", "ADES", "PURE LIFE",
    ],
    "kopi": [
        "KOPI", "KAPAL API", "NESCAFE", "TORABIKA", "GOOD DAY", "LUWAK", "INDOCAFE",
        "TOP COFFEE", "ABC MOCCA", "COFFEE", "COFFEEMIX", "COFFEMIX", "COFFE",
    ],
    "teh": [
        "TEH", "TEA", "SARIWANGI", "SOSRO", "TEH PUCUK", "FRESTEA", "TEH GELAS",
        "TEH KOTAK", "TONG TJI", "2 TANG", "2TANG", "SARI MURNI", "LIPTON",
    ],
    "susu": [
        "SUSU", "DANCOW", "FRISIAN FLAG", "ULTRA MILK", "ULTRAMILK", "INDOMILK",
        "BEAR BRAND", "MILO", "SKM", "SGM", "LACTOGEN", "ZEE", "BENDERA", "UHT",
        "MILKUAT", "CIMORY", "ENERGEN",
    ],
    "minuman ringan": [
        "COCA COLA", "COCA-COLA", "SPRITE", "FANTA", "PEPSI", "MIRINDA", "POCARI",
        "MIZONE", "YAKULT", "ADEM SARI", "KRATINGDAENG", "EXTRA JOSS", "HEMAVITON",
        "KUKUBIMA", "KUKU BIMA", "EXTRA JOOS", "BIG COLA", "TEBS", "FLORIDINA", "OKKY", "ALE ALE",
        "MARIMAS", "NUTRISARI", "POP ICE", "MARJAN", "SIRUP", "LASEGAR",
        "KAKI TIGA", "LARUTAN", "SEGAR SARI",
    ],
    "minyak goreng": [
        "MINYAK GORENG", "BIMOLI", "FILMA", "SUNCO", "SANIA", "FORTUNE",
        "KUNCI MAS", "SOVIA", "M.GORENG", "M. GORENG",
    ],
    "beras dan pokok": [
        "BERAS", "GULA", "GULAKU", "TEPUNG", "TERIGU", "SEGITIGA BIRU", "KUNCI BIRU",
        "MAIZENA", "ROSE BRAND", "BIHUN", "BIHON", "SOHUN", "AGAR", "AGAR2",
    ],
    "makanan kaleng": [
        "SARDEN", "SARDINES", "KORNET", "CORNED", "PRONAS", "MACKEREL",
    ],
    "bumbu": [
        "ROYCO", "MASAKO", "KECAP", "SAUS", "SAMBAL", "BUMBU", "BMB", "TERASI",
        "MERICA", "LADA", "GARAM", "MICIN", "AJINOMOTO", "SASA", "KALDU", "BANGO",
        "SAJIKU", "MAGGI", "KNORR", "KOBE", "MAMASUKA", "SANTAN", "KARA",
        "PEWARNA MAKANAN", "ABC",
    ],
    "permen dan coklat": [
        "PERMEN", "KOPIKO", "RELAXA", "MENTOS", "HEXOS", "YUPI", "SUGUS",
        "SILVERQUEEN", "CHOKI", "BENG BENG", "CHACHA", "DELFI", "KISS", "NARAYA",
        "INACO", "ALPENLIEBE", "HAPPYDENT", "FRUITELLA", "GOLIA", "JUICY FRUIT",
        "TREBOR", "CLORETS", "HALLS", "FROZZ", "LOLLYPOP", "LOLLIPOP",
    ],
    "roti dan biskuit": [
        "ROMA", "OREO", "BISKUIT", "BISCUIT", "BISC", "WAFER", "WF", "TANGO", "SARI ROTI",
        "ROTI", "KHONG GUAN", "MARIE", "RICHEESE", "NABATI", "GOOD TIME", "BISKUAT",
        "SLAI OLAI", "CRACKER", "CRACKERS", "COOKIES", "COOKIE", "NISSIN",
    ],
    "snack": [
        "CHITATO", "TARO", "QTELA", "LAYS", "LAY'S", "CHIKI", "CHEETOS", "KUSUKA",
        "POTABEE", "KERIPIK", "KACANG", "KCG", "KCNG", "MAYASI", "TINI WINI", "GARUDA", "DUA KELINCI", "KRUPUK",
        "KERUPUK", "MOMOGI", "JETZ", "BIPI", "OISHI", "LAGIE", "SNEKKU", "SMAX",
        "PIATTOS", "MISTER POTATO", "CHIPS", "KWACI", "KUACI", "GERY", "CHOCOLATOS",
        "KOKO KRUNCH",
    ],
    "alat tulis": [
        "BUKU TULIS", "BK TULIS", "BUKU", "PENSIL", "PULPEN", "BOLPOIN", "PENGHAPUS",
        "PENGGARIS", "GARISAN", "RAUTAN", "SINAR DUNIA", "SIDU", "KIKY", "SNOWMAN",
        "STABILO", "JOYKO", "HVS", "SPIDOL", "CRAYON",
    ],
}


def _pola(kata_kunci: list[str]) -> re.Pattern:
    """Pola regex yang mencocokkan kata kunci sebagai kata utuh.

    Batas kata ditentukan oleh huruf dan angka di sekitarnya, bukan oleh \\b,
    agar kata kunci yang mengandung tanda baca seperti HEAD & SHOULDERS tetap
    dicocokkan dengan benar.
    """
    gabungan = "|".join(re.escape(k) for k in sorted(kata_kunci, key=len, reverse=True))
    return re.compile(rf"(?<![A-Z0-9])(?:{gabungan})(?![A-Z0-9])")


_POLA_PENGECUALIAN = _pola(PENGECUALIAN)
_POLA_KATEGORI = {kategori: _pola(kata) for kategori, kata in KAMUS.items()}


def kategorikan(nama: str) -> str | None:
    """Kategori kasar suatu nama barang, atau None apabila bukan kandidat warung."""
    nama = nama.upper()
    if (_POLA_TIDAK_AKTIF.search(nama) or _POLA_KARTON.search(nama)
            or _POLA_PENGECUALIAN.search(nama)):
        return None
    if _POLA_OBAT.search(nama):
        return "obat warung"
    for kategori, pola in _POLA_KATEGORI.items():
        if pola.search(nama):
            return kategori
    return None


def saring(katalog: pd.DataFrame) -> pd.DataFrame:
    hasil = katalog.assign(kategori_kasar=katalog["nama"].map(kategorikan))
    return hasil.dropna(subset=["kategori_kasar"]).reset_index(drop=True)


if __name__ == "__main__":
    katalog = pd.read_csv(BERKAS_KATALOG, dtype=str)
    kandidat = saring(katalog)
    kandidat.to_csv(BERKAS_KANDIDAT, index=False)

    besar = katalog["nama"].str.upper()
    print(f"{len(kandidat)} kandidat dari {len(katalog)} barang "
          f"({len(kandidat) / len(katalog) * 100:.1f}%)")
    print(f"  dibuang: pengecualian {besar.str.contains(_POLA_PENGECUALIAN).sum()}, "
          f"karton {besar.str.contains(_POLA_KARTON).sum()}, "
          f"tidak aktif {besar.str.contains(_POLA_TIDAK_AKTIF).sum()}")
    print()

    jumlah = kandidat["kategori_kasar"].value_counts()
    for kategori in KAMUS:
        isi = kandidat[kandidat["kategori_kasar"] == kategori]
        print(f"[{kategori}] {jumlah.get(kategori, 0)}")
        if len(isi):
            for nama in isi["nama"].sample(min(5, len(isi)), random_state=7):
                print(f"    {nama}")
