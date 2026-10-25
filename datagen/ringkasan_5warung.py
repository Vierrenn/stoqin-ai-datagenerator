"""Ringkasan hasil generate per warung dalam Markdown, untuk peninjauan manual.

Berkas yang dihasilkan merupakan turunan dari stok_harian.csv dan tidak dibaca oleh
komponen mana pun.
"""

import pandas as pd

from datagen.profil_warung import PROFIL
from datagen.resep_otomatis import BERKAS_RESEP, DIR_KELUARAN, HARGA_KELAS

DIR_RINGKASAN = DIR_KELUARAN / "ringkasan"
NAMA_BULAN = ["Okt", "Nov", "Des", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep"]
HARI = {"Monday": "Sen", "Tuesday": "Sel", "Wednesday": "Rab", "Thursday": "Kam",
        "Friday": "Jum", "Saturday": "Sab", "Sunday": "Min"}
CONTOH_MULAI, CONTOH_HARI = "2025-11-03", 14


def _tabel(df: pd.DataFrame, judul_indeks: str) -> list[str]:
    kepala = f"| {judul_indeks} | " + " | ".join(str(c) for c in df.columns) + " |"
    garis = "| --- | " + " | ".join("---" for _ in df.columns) + " |"
    baris = [f"| {i} | " + " | ".join(f"{v:,.0f}".replace(",", ".") if isinstance(v, float) else str(v)
                                     for v in row) + " |" for i, row in df.iterrows()]
    return [kepala, garis, *baris]


def _per_bulan(df: pd.DataFrame, indeks: str) -> pd.DataFrame:
    tabel = df.pivot_table(index=indeks, columns="bulan", values="terjual", aggfunc="sum").fillna(0)
    tabel = tabel.reindex(columns=range(12), fill_value=0)
    tabel.columns = NAMA_BULAN
    tabel["setahun"] = tabel.sum(axis=1)
    return tabel.sort_values("setahun", ascending=False).astype(float)


def tulis_ringkasan(harian: pd.DataFrame, resep: pd.DataFrame, profil) -> str:
    r = resep[resep["store_id"] == profil.kode].set_index("kode")
    h = harian[harian["store_id"] == profil.kode].join(r[["nama", "kategori", "kelas_harga", "popularitas", "peringkat"]], on="kode")
    h["bulan"] = (h["date"].dt.year - 2025) * 12 + h["date"].dt.month - 10
    harga = h["kelas_harga"].map(HARGA_KELAS).where(h["kategori"] != "rokok", 27_000)
    hari = h["date"].nunique()

    per_barang = h.groupby("kode").agg(kosong=("stok_akhir", lambda s: (s == 0).mean()))
    teks = [
        f"# Ringkasan Warung {profil.kode}: {profil.nama}", "",
        f"Periode {h['date'].min():%d-%m-%Y} sampai {h['date'].max():%d-%m-%Y}, {len(r)} barang.", "",
        "| ukuran | nilai |", "| --- | --- |",
        f"| terjual per hari | {h['terjual'].sum() / hari:.0f} |",
        f"| omzet per hari (harga wakil per kelas) | Rp{(h['terjual'] * harga).sum() / hari / 1e6:.2f} juta |",
        f"| permintaan hilang karena stok habis | {1 - h['terjual'].sum() / h['permintaan'].sum():.1%} |",
        f"| hari stok habis di akhir hari, median per barang | {per_barang['kosong'].median():.1%} |",
        "", "## Penjualan per bulan per kategori", "",
        "Efek libur dan tahun ajaran baru terlihat di sini.", "",
    ]
    per_kategori = _per_bulan(h, "kategori")
    per_kategori.loc["**total**"] = per_kategori.sum()
    teks += _tabel(per_kategori, "kategori")

    teratas = r.sort_values("laju_harian", ascending=False).head(10).index
    teks += ["", "## 10 barang terlaris per bulan", ""]
    teks += _tabel(_per_bulan(h[h["kode"].isin(teratas)], "nama"), "barang")

    laris = r.sort_values("laju_harian", ascending=False).index[[0, 1, 5]]
    lambat = r[r["laju_harian"] < 0.5].sort_values("laju_harian").index
    lambat = lambat[[len(lambat) // 2, len(lambat) * 3 // 4, len(lambat) - 1]]
    contoh = h[h["kode"].isin(laris.append(lambat))
               & h["date"].between(CONTOH_MULAI, pd.Timestamp(CONTOH_MULAI) + pd.Timedelta(days=CONTOH_HARI - 1))]
    lebar = contoh.pivot_table(index="nama", columns="date", values="terjual", aggfunc="sum")
    lebar = lebar.reindex([r.at[k, "nama"] for k in laris.append(lambat)])
    lebar.columns = [f"{HARI[d.day_name()]} {d.day}" for d in lebar.columns]
    teks += ["", f"## Contoh dua minggu penjualan harian", "",
             "Tiga barang terlaris di atas, tiga barang lambat di bawah. Angka 0 berarti tidak laku.", ""]
    teks += _tabel(lebar.astype(int), "barang")

    sering_kosong = per_barang.join(r["nama"]).sort_values("kosong", ascending=False).head(10)
    teks += ["", "## Barang yang paling sering kosong", "", "| barang | hari stok habis di akhir hari |", "| --- | --- |"]
    teks += [f"| {b.nama} | {b.kosong:.1%} |" for b in sering_kosong.itertuples()]
    return "\n".join(teks) + "\n"


def main() -> None:
    resep = pd.read_csv(BERKAS_RESEP, dtype={"kode": str})
    harian = pd.read_csv(DIR_KELUARAN / "stok_harian.csv", dtype={"kode": str}, parse_dates=["date"])
    DIR_RINGKASAN.mkdir(parents=True, exist_ok=True)
    for p in PROFIL:
        (DIR_RINGKASAN / f"ringkasan_{p.kode}.md").write_text(tulis_ringkasan(harian, resep, p), encoding="utf-8")
    print(f"ringkasan ditulis ke {DIR_RINGKASAN}")


if __name__ == "__main__":
    main()
