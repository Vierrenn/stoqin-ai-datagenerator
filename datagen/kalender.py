"""Faktor kalender warung: pengaruh hari dalam minggu dan posisi tanggal.

Seluruh angka pada modul ini merupakan asumsi, bukan hasil pengukuran, karena
data penjualan warung belum tersedia pada saat modul disusun.

faktor_gajian dipakai generator lima warung. faktor_tanggal dan faktor_kalender
hanya dipakai pipeline 60 SKU lama.
"""

import math

# Nama hari mengikuti keluaran Timestamp.day_name() agar sesuai dengan kolom
# weekday yang dibaca model. Rata-rata ketujuh faktor bernilai 1,0 supaya volume
# harian tidak bergeser dari unit_per_hari.
FAKTOR_HARI = {
    "Monday": 1.00,
    "Tuesday": 0.95,
    "Wednesday": 0.93,
    "Thursday": 0.95,
    "Friday": 1.02,
    "Saturday": 1.08,
    "Sunday": 1.07,
}

# Elemen: (batas atas tanggal, faktor). Barang berharga tinggi ditunda sampai
# penerimaan gaji, sedangkan barang berharga rendah bergerak berlawanan arah
# karena pembeli beralih ke kemasan sachet menjelang akhir bulan.
FAKTOR_TANGGAL_SENSITIF = [(10, 1.25), (20, 0.98), (31, 0.80)]
FAKTOR_TANGGAL_BIASA = [(10, 0.93), (20, 0.98), (31, 1.08)]

AMBANG_HARGA_SENSITIF = 10_000


def faktor_hari(tanggal) -> float:
    return FAKTOR_HARI[tanggal.day_name()]


def faktor_gajian(tanggal, kekuatan: float) -> float:
    """Pengali siklus gajian: puncak di pergantian bulan, terendah di tengah bulan.

    Rata-rata dalam satu bulan bernilai 1,0 untuk berapa pun jumlah harinya.
    Kekuatan 0 berarti barang tidak terpengaruh gajian.
    """
    sudut = 2 * math.pi * (tanggal.day - 0.5) / tanggal.days_in_month
    return 1 + kekuatan * math.cos(sudut)


def faktor_tanggal(tanggal, sensitif: bool) -> float:
    pita = FAKTOR_TANGGAL_SENSITIF if sensitif else FAKTOR_TANGGAL_BIASA
    for batas, nilai in pita:
        if tanggal.day <= batas:
            return nilai
    raise ValueError(f"tanggal gak valid: {tanggal.day}")


def faktor_kalender(tanggal, sensitif: bool) -> float:
    """Pengali gabungan hari dan posisi tanggal untuk satu tanggal."""
    return faktor_hari(tanggal) * faktor_tanggal(tanggal, sensitif)
