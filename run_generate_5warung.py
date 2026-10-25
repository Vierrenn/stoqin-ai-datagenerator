"""Membangkitkan data penjualan sintetis lima warung untuk keperluan demonstrasi.

Per warung: membangkitkan permintaan harian dari resep dan pengali kalender, lalu
menjalankan simulasi persediaan. Hasil ditulis ke data/demo_5warung.

Kolom permintaan dan kehilangan pada stok_harian.csv tidak dapat diamati pada kondisi
nyata. Kedua kolom tersebut hanya untuk memeriksa hasil simulasi dan tidak boleh dibaca
oleh komponen yang mensimulasikan produk.
"""

import pandas as pd

from datagen.kalender_warung import pengali_harian
from datagen.profil_warung import PROFIL
from datagen.resep_otomatis import BERKAS_RESEP, DIR_KELUARAN, HARGA_KELAS
from datagen.stock_sim import HARI_PEMANASAN, ambil_snapshot, jalankan_simulasi
from datagen.synthetic import bangkitkan_dengan_pengali
from datagen.tinjauan import lebar_bulanan, lebar_harian

TANGGAL_MULAI = "2025-10-01"
JUMLAH_HARI = 365
STOK_MINIMAL = 2
DIR_TINJAUAN = DIR_KELUARAN / "tinjauan"

KOLOM_KATALOG = ["store_id", "kode", "nama", "kategori", "satuan", "kelas_harga",
                 "popularitas", "peringkat"]


def bangkitkan_warung(resep: pd.DataFrame, profil) -> pd.DataFrame:
    mulai = pd.Timestamp(TANGGAL_MULAI) - pd.Timedelta(days=HARI_PEMANASAN)
    tanggal = pd.date_range(mulai, periods=JUMLAH_HARI + HARI_PEMANASAN, freq="D")
    pengali = pengali_harian(resep, profil, tanggal)
    permintaan = bangkitkan_dengan_pengali(resep, tanggal, pengali, profil.seed)
    return jalankan_simulasi(permintaan, resep, hari_pemanasan=HARI_PEMANASAN,
                             stok_minimal=STOK_MINIMAL)


def main() -> None:
    resep = pd.read_csv(BERKAS_RESEP, dtype={"kode": str})
    identitas = resep.set_index("sku_id")[["store_id", "kode"]]

    harian = pd.concat(
        [bangkitkan_warung(resep[resep["store_id"] == p.kode].reset_index(drop=True), p)
         for p in PROFIL],
        ignore_index=True,
    )
    harian = identitas.join(harian.set_index("sku_id"), how="inner").reset_index()

    penjualan = harian[["store_id", "kode", "date", "weekday", "terjual"]].rename(
        columns={"terjual": "qty"})
    snapshot = identitas.join(ambil_snapshot(harian).set_index("sku_id")).reset_index(drop=True)

    DIR_TINJAUAN.mkdir(parents=True, exist_ok=True)
    penjualan.to_csv(DIR_KELUARAN / "penjualan_harian.csv", index=False)
    harian.drop(columns="sku_id").to_csv(DIR_KELUARAN / "stok_harian.csv", index=False)
    snapshot.to_csv(DIR_KELUARAN / "snapshot_stok.csv", index=False)
    resep[KOLOM_KATALOG].to_csv(DIR_KELUARAN / "katalog_warung.csv", index=False)

    buku = harian[["sku_id", "date", "terjual"]].rename(columns={"terjual": "qty"})
    for p in PROFIL:
        r = resep[resep["store_id"] == p.kode]
        b = buku[buku["sku_id"].isin(r["sku_id"])]
        lebar_harian(b, r).to_csv(DIR_TINJAUAN / f"harian_{p.kode}.csv", index=False)
        lebar_bulanan(b, r).to_csv(DIR_TINJAUAN / f"bulanan_{p.kode}.csv", index=False)

    _cetak_ringkasan(resep, harian)


def _cetak_ringkasan(resep: pd.DataFrame, harian: pd.DataFrame) -> None:
    per_sku = harian.groupby("sku_id")[["permintaan", "terjual"]].mean()
    r = resep.set_index("sku_id").join(per_sku)
    r["kosong"] = harian.groupby("sku_id")["kehilangan"].apply(lambda s: (s > 0).mean() * 100)
    harga = r["kelas_harga"].map(HARGA_KELAS).where(r["kategori"] != "rokok", 27_000)

    print(f"{harian['date'].min():%Y-%m-%d} sampai {harian['date'].max():%Y-%m-%d}, "
          f"{len(r)} barang di {r['store_id'].nunique()} warung\n")
    print(f"{'warung':8s}{'mutu':>8}{'hilang':>9}{'kosong med':>12}{'kosong maks':>13}"
          f"{'terjual/hari':>14}{'omzet/hari':>13}")
    for kode, g in r.groupby("store_id"):
        mutu = (g["permintaan"].sum() / g["rata_harian_target"].sum() - 1) * 100
        hilang = (g["terjual"].sum() / g["permintaan"].sum() - 1) * 100
        omzet = (g["terjual"] * harga[g.index]).sum()
        print(f"{kode:8s}{mutu:>+7.1f}%{hilang:>+8.1f}%{g['kosong'].median():>11.1f}%"
              f"{g['kosong'].max():>12.1f}%{g['terjual'].sum():>14.0f}{omzet / 1e6:>10.2f} jt")
    print("\nmutu: permintaan thd resep (libur dan musim menggeser angka ini secara wajar)")
    print("hilang: penjualan thd permintaan, akibat stok kosong")
    print(f"berkas ditulis ke {DIR_KELUARAN}")
    print("data sintetis, tidak boleh dipakai sebagai bukti akurasi model")


if __name__ == "__main__":
    main()
