"""Penyusunan resep penjualan untuk setiap pasangan warung dan barang.

Resep diturunkan dalam tiga tahap:

1. Laju harian: patokan kategori (laju barang peringkat 1 di warung B) dikalikan faktor
   popularitas dan peringkat relatif terhadap barang peringkat 1, faktor harga satuan,
   keramaian warung, dan penekanan kategori yang dinormalkan.
2. Borongan: tiga barang teratas di kategori tertentu yang lajunya cukup tinggi mendapat
   peluang pembelian besar. Bagian borongan dikurangkan dari penjualan normal sehingga
   laju total tidak berubah.
3. Pola laku: laju penjualan normal dipetakan ke peluang laku dan rentang kuantitas
   menurut pita laju.

Siklus gajian, masa libur, dan musim tahun ajaran baru tidak masuk resep; ketiganya
diterapkan saat pembangkitan.
"""

import numpy as np
import pandas as pd

from datagen.assortment import BERKAS_ASSORTMENT, DIR_KELUARAN
from datagen.profil_warung import PROFIL, ProfilWarung, penekanan
from datagen.resep import hitung_rata_harian, validasi_resep

BERKAS_RESEP = DIR_KELUARAN / "resep.csv"

PATOKAN = {
    "mie instan": 15, "air minum": 11, "snack": 9, "rokok": 8, "deterjen dan pembersih": 8,
    "permen dan coklat": 7, "bumbu": 6, "teh": 5, "roti dan biskuit": 4, "kopi": 4,
    "beras dan pokok": 3, "sabun dan sampo": 3, "es krim": 3, "minuman ringan": 3, "susu": 3,
    "minyak goreng": 2.7, "obat warung": 2, "rumah tangga": 2, "perawatan gigi": 1.5,
    "alat tulis": 1, "pembalut dan bayi": 0.8, "makanan kaleng": 0.6,
}
FAKTOR_POPULARITAS = {5: 1.0, 4: 0.55, 3: 0.25, 2: 0.10, 1: 0.04}
EKSPONEN_PERINGKAT = 0.25
# Harga wakil per kelas, hanya untuk perbandingan harga satuan antarbarang.
HARGA_KELAS = {"murah": 2_000, "sedang": 8_000, "mahal": 25_000}
EKSPONEN_HARGA = 0.5

# kategori: (bulk_min, bulk_maks, prob_bulk)
BORONGAN = {
    "mie instan": (20, 40, 0.04), "air minum": (12, 24, 0.05), "teh": (12, 24, 0.03),
    "kopi": (10, 10, 0.02), "bumbu": (10, 12, 0.02), "susu": (4, 10, 0.05),
    "minyak goreng": (4, 10, 0.03), "beras dan pokok": (4, 10, 0.05),
    "snack": (4, 10, 0.03), "roti dan biskuit": (5, 12, 0.03),
}
BORONGAN_PERINGKAT_MAKS = 3
BORONGAN_LAJU_MIN = 2.0
BORONGAN_KALI_LAJU_MAKS = 5

# kategori: (lead_time_hari, review_period_hari), mengikuti 60 SKU.
KULAKAN = {
    "mie instan": (2, 7), "air minum": (2, 7), "minyak goreng": (2, 7), "beras dan pokok": (2, 7),
    "rokok": (2, 7), "es krim": (3, 7), "minuman ringan": (3, 14), "teh": (3, 14),
    "bumbu": (3, 14), "kopi": (3, 14), "snack": (4, 14), "roti dan biskuit": (4, 14),
    "susu": (4, 14), "permen dan coklat": (4, 14), "sabun dan sampo": (4, 14),
    "perawatan gigi": (4, 14), "deterjen dan pembersih": (4, 14), "pembalut dan bayi": (4, 14),
    "rumah tangga": (5, 30), "makanan kaleng": (5, 30), "obat warung": (7, 30),
    "alat tulis": (7, 30),
}


def pengali_penekanan(profil: ProfilWarung) -> pd.Series:
    """Penekanan kategori dinormalkan agar rata-ratanya, ditimbang patokan, bernilai 1.
    Dengan begitu keramaian tetap menjadi satu-satunya penentu volume keseluruhan."""
    bobot = pd.Series(PATOKAN)
    pen = pd.Series({k: penekanan(profil, k) for k in PATOKAN})
    return pen * bobot.sum() / (bobot * pen).sum()


def hitung_laju(rak: pd.DataFrame, profil: ProfilWarung) -> pd.Series:
    pen = pengali_penekanan(profil)
    harga = rak["kelas_harga"].map(HARGA_KELAS).where(rak["kategori"] != "rokok", 27_000)
    laju = pd.Series(0.0, index=rak.index)
    for kategori, isi in rak.groupby("kategori"):
        isi = isi.sort_values("peringkat")
        relatif = isi["popularitas"].map(FAKTOR_POPULARITAS) * isi["peringkat"] ** -EKSPONEN_PERINGKAT
        relatif = relatif / relatif.iloc[0]
        h = harga[isi.index]
        f_harga = np.minimum(1.0, (h.iloc[0] / h) ** EKSPONEN_HARGA)
        laju[isi.index] = (PATOKAN[kategori] * relatif * f_harga
                           * profil.keramaian * pen[kategori])
    return laju


def parameter_borongan(rak: pd.DataFrame, laju: pd.Series) -> pd.DataFrame:
    hasil = pd.DataFrame({"prob_bulk": 0.0, "bulk_min": 0, "bulk_maks": 0}, index=rak.index)
    layak = (rak["kategori"].isin(BORONGAN) & (rak["peringkat"] <= BORONGAN_PERINGKAT_MAKS)
             & (laju >= BORONGAN_LAJU_MIN))
    for i in rak.index[layak]:
        bmin, bmaks, prob = BORONGAN[rak.at[i, "kategori"]]
        # Borongan minimal sebesar penjualan tertinggi hari biasa agar tetap terasa sebagai
        # lonjakan, lalu dibatasi kelipatan laju agar tidak ekstrem.
        lebar = bmaks - bmin
        bmin = max(bmin, _qty_maks_biasa(laju[i]))
        bmaks = max(bmaks, bmin + lebar)
        batas = int(BORONGAN_KALI_LAJU_MAKS * laju[i] + 0.5)
        bmaks = min(bmaks, batas)
        bmin = min(bmin, bmaks)
        hasil.loc[i] = [prob, bmin, bmaks]
    return hasil


def _qty_maks_biasa(laju: float) -> int:
    """Perkiraan kuantitas tertinggi penjualan normal, mengikuti pita pola laku."""
    if laju >= 3:
        return int(1.5 * laju + 0.5)
    return 5 if laju > 2.5 else 4


# Barang yang tidak laku setiap hari: kuantitas per pembelian biasanya 1 dan sesekali
# lebih, dengan rata-rata per barang yang diundi dari pilihan berikut.
PILIHAN_PER_BELI = (1.5, 2.0, 2.5, 3.0)
PELUANG_PER_BELI = (0.65, 0.15, 0.12, 0.08)
QTY_MAKS_GEOMETRIK = 12
SEED_PER_BELI = 20261107
# Stok minimal saat kulakan: dua kali rata-rata per pembelian, paling sedikit dua buah,
# agar pembelian beberapa buah sekaligus tidak terpotong stok yang terlalu tipis.
STOK_MINIMAL_DASAR = 2
STOK_MINIMAL_KALI_PER_BELI = 3


def rata_per_beli_barang(kode: pd.Series) -> pd.Series:
    """Rata-rata kuantitas per pembelian untuk tiap kode, sama di semua warung."""
    unik = sorted(kode.unique())
    rng = np.random.default_rng(SEED_PER_BELI)
    return pd.Series(rng.choice(PILIHAN_PER_BELI, size=len(unik), p=PELUANG_PER_BELI), index=unik)


def pola_laku(laju_normal: float, per_beli: float) -> tuple[float, int, int, float]:
    """Peluang laku, rentang kuantitas, dan rata-rata per pembelian menurut pita laju.

    Rata-rata yang dihasilkan sama dengan laju. Rata-rata per pembelian bernilai nol
    untuk sebaran seragam dan di atas nol untuk sebaran geometrik.
    """
    if laju_normal >= 3:
        qmin = max(1, int(laju_normal * 0.5 + 0.5))
        qmaks = int(2 * laju_normal - qmin + 0.5)
        return 1.0, qmin, qmaks, 0.0
    if laju_normal >= 1.5:
        # Rentang 1 sampai 4 tidak mampu mencapai laju di atas 2,5 dengan peluang 1.
        qmin, qmaks = (1, 5) if laju_normal > 2.5 else (1, 4)
        return laju_normal / ((qmin + qmaks) / 2), qmin, qmaks, 0.0
    return laju_normal / per_beli, 1, QTY_MAKS_GEOMETRIK, per_beli


PELUANG_STABIL = 0.6


def tipe_demand(prob_laku: float, laju: float, ada_bulk: bool) -> str:
    """Label pola untuk laporan; komposisi kuadran sebenarnya diukur dari data hasil."""
    if prob_laku >= PELUANG_STABIL:
        return "stabil_tinggi" if laju >= 5 else "stabil_sedang"
    return "lumpy_bulk" if ada_bulk else "intermittent"


def susun_resep(assortment: pd.DataFrame) -> pd.DataFrame:
    per_beli = rata_per_beli_barang(assortment["kode"])
    bagian = []
    for profil in PROFIL:
        rak = assortment[assortment["store_id"] == profil.kode].copy()
        laju = hitung_laju(rak, profil)
        bulk = parameter_borongan(rak, laju)
        normal = laju - bulk["prob_bulk"] * (bulk["bulk_min"] + bulk["bulk_maks"]) / 2

        pola = pd.DataFrame([pola_laku(x, per_beli[k]) for x, k in zip(normal, rak["kode"])],
                            index=rak.index,
                            columns=["prob_laku", "qty_min", "qty_maks", "rata_per_beli"])
        rak = pd.concat([rak, pola, bulk], axis=1)
        rak["prob_laku"] = rak["prob_laku"].round(4)
        rak["laju_harian"] = laju.round(4)
        rak["tipe_demand"] = [tipe_demand(p, l, b > 0) for p, l, b
                              in zip(rak["prob_laku"], laju, rak["prob_bulk"])]
        gajian = (profil.gajian_semua_barang | (rak["kelas_harga"] == "mahal")) & (rak["kategori"] != "rokok")
        rak["kekuatan_gajian"] = np.where(gajian, profil.kekuatan_gajian, 0.0)
        rak[["lead_time_hari", "review_period_hari"]] = rak["kategori"].map(KULAKAN).tolist()
        rak["review_period_hari"] = (rak["review_period_hari"] * profil.pengali_kulakan + 0.5).astype(int).clip(lower=3)
        rak["stok_minimal"] = np.maximum(
            STOK_MINIMAL_DASAR, np.ceil(STOK_MINIMAL_KALI_PER_BELI * rak["rata_per_beli"])).astype(int)
        bagian.append(rak)

    resep = pd.concat(bagian, ignore_index=True)
    resep["sku_id"] = resep["store_id"] + "-" + resep["kode"]
    resep["rata_harian_target"] = hitung_rata_harian(resep).round(4)
    return resep


KOLOM = ["sku_id", "store_id", "kode", "nama", "kategori", "satuan", "kelas_harga", "popularitas",
         "peringkat", "laju_harian", "tipe_demand", "prob_laku", "qty_min", "qty_maks",
         "rata_per_beli", "prob_bulk", "bulk_min", "bulk_maks", "rata_harian_target", "kekuatan_gajian",
         "lead_time_hari", "review_period_hari", "stok_minimal"]


DIR_RESEP_MD = DIR_KELUARAN / "resep"


def _frekuensi(prob: float) -> str:
    if prob >= 1:
        return "tiap hari"
    if prob >= 1 / 7:
        return f"{prob * 7:.1f} hari/minggu"
    return f"sekali tiap {1 / prob:.0f} hari"


def _sekali_laku(r) -> str:
    if r.rata_per_beli > 0:
        return f"biasanya 1, rata-rata {r.rata_per_beli:g}"
    return f"{r.qty_min} sampai {r.qty_maks}"


def tulis_md(resep: pd.DataFrame) -> None:
    DIR_RESEP_MD.mkdir(parents=True, exist_ok=True)
    for profil in PROFIL:
        isi = resep[resep["store_id"] == profil.kode]
        urutan = isi.groupby("kategori")["laju_harian"].sum().sort_values(ascending=False).index
        teks = [f"# Resep Warung {profil.kode}: {profil.nama}", "",
                f"{len(isi)} barang, total sekitar {isi['rata_harian_target'].sum():.0f} terjual per hari.",
                "", "| kategori | barang | terjual per hari |", "| --- | --- | --- |"]
        teks += [f"| [{k}](#{k.replace(' ', '-')}) | {(isi['kategori'] == k).sum()} | "
                 f"{isi.loc[isi['kategori'] == k, 'laju_harian'].sum():.1f} |" for k in urutan]
        for kategori in urutan:
            g = isi[isi["kategori"] == kategori].sort_values("peringkat")
            teks += ["", f"## {kategori}", "",
                     "| # | nama | pop | per hari | laku | sekali laku | borongan |",
                     "| --- | --- | --- | --- | --- | --- | --- |"]
            for r in g.itertuples():
                bor = (f"{r.bulk_min} sampai {r.bulk_maks}, {r.prob_bulk:.0%}" if r.prob_bulk > 0 else "")
                teks.append(f"| {r.peringkat} | {r.nama.replace('|', '/')} | {r.popularitas} | "
                            f"{r.laju_harian:.2f} | {_frekuensi(r.prob_laku)} | "
                            f"{_sekali_laku(r)} | {bor} |")
        (DIR_RESEP_MD / f"resep_{profil.kode}.md").write_text("\n".join(teks) + "\n", encoding="utf-8")


def cetak_laporan(resep: pd.DataFrame) -> None:
    resep = resep.assign(selisih=resep["rata_harian_target"] - resep["laju_harian"])
    print(f"selisih rata-rata resep terhadap laju: maks {resep['selisih'].abs().max():.3f}\n")
    print(pd.crosstab(resep["store_id"], resep["tipe_demand"]).to_string(), "\n")
    print(resep.groupby("store_id")[["rata_harian_target"]].sum().round(0).T.to_string())


if __name__ == "__main__":
    assortment = pd.read_csv(BERKAS_ASSORTMENT, dtype={"kode": str})
    resep = susun_resep(assortment)[KOLOM]
    validasi_resep(resep)
    resep.to_csv(BERKAS_RESEP, index=False)
    tulis_md(resep)
    cetak_laporan(resep)
    print(f"\n{len(resep)} resep ditulis ke {BERKAS_RESEP}")
