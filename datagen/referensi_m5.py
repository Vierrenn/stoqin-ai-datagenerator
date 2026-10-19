"""Angka rujukan empiris dari dataset M5, dipakai untuk verifikasi hasil generate.

Modul ini tidak terlibat dalam pembangkitan data. Parameter pembangkitan ditetapkan
manual pada resep_sintetis.csv, dan angka di sini dipakai untuk memeriksa apakah
karakteristik hasil generate masih berada pada rentang yang wajar menurut data
ritel nyata.

Seluruh angka diturunkan dari 1.437 SKU dataset M5, store CA_1, kategori FOODS.
"""

# Pemetaan rata-rata unit per hari terhadap jumlah hari terjadinya penjualan dalam
# 30 hari. Elemen: (batas atas unit per hari, nilai per tanda konsistensi).
FREKUENSI = [
    (0.2, {"konsisten": 3.9, "lompat": 2.5}),
    (0.5, {"konsisten": 7.5, "lompat": 7.1}),
    (1.0, {"konsisten": 12.3, "lompat": 10.2}),
    (2.0, {"konsisten": 17.9, "lompat": 16.0}),
    (4.0, {"konsisten": 22.6, "lompat": 20.9}),
    (8.0, {"konsisten": 25.5, "lompat": 23.5}),
    (float("inf"), {"konsisten": 27.6, "lompat": 24.5}),
]

# Dispersi kuantitas penjualan, dinyatakan sebagai CV kuadrat, dengan pembagian
# pita yang sama.
CV2 = [
    (0.2, {"konsisten": 0.164, "lompat": 0.534}),
    (0.5, {"konsisten": 0.293, "lompat": 0.593}),
    (1.0, {"konsisten": 0.372, "lompat": 0.593}),
    (2.0, {"konsisten": 0.422, "lompat": 0.569}),
    (4.0, {"konsisten": 0.410, "lompat": 0.632}),
    (8.0, {"konsisten": 0.363, "lompat": 0.625}),
    (float("inf"), {"konsisten": 0.291, "lompat": 0.678}),
]

# Koefisien variasi data harian per pita laju, beserta proporsi hari tanpa
# penjualan. Dipakai sebagai pembanding tingkat keacakan hasil generate.
CV_HARIAN = [
    (0.5, 2.15, 0.76),
    (1.0, 1.59, 0.60),
    (2.0, 1.25, 0.43),
    (4.0, 1.03, 0.27),
    (8.0, 0.92, 0.18),
    (float("inf"), 0.79, 0.09),
]

CV_HARIAN_MEDIAN_SELURUH = 1.38

# Komposisi kuadran ADI/CV2 pada dataset M5, sebagai pembanding komposisi katalog.
KOMPOSISI_KUADRAN = {
    "intermittent": 0.584,
    "lumpy": 0.271,
    "smooth": 0.105,
    "erratic": 0.040,
}

AMBANG_ADI = 1.32
AMBANG_CV2 = 0.49


def baca_pita(tabel: list, unit_per_hari: float, tanda: str = "konsisten"):
    """Mengambil nilai rujukan pada pita laju yang memuat unit_per_hari."""
    for batas, nilai in tabel:
        if unit_per_hari < batas:
            return nilai[tanda] if isinstance(nilai, dict) else nilai
    raise ValueError(f"unit_per_hari di luar jangkauan tabel: {unit_per_hari}")
