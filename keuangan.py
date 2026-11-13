from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

# --- INISIALISASI DATABASE SQLITE ---
def init_db():
  conn = sqlite3.connect("keuangan.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT,
            kategori TEXT,
            jumlah INTEGER,
            keterangan TEXT
        )
    """)
  conn.commit()
  conn.close()


# Panggil fungsi inisialisasi database
init_db()


# Fungsi untuk mengambil data dari SQLite
def get_data():
  conn = sqlite3.connect("keuangan.db")
  df = pd.read_sql_query(
      "SELECT tanggal, jenis, kategori, jumlah, keterangan FROM transaksi",
      conn,
  )
  conn.close()
  return df


# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Keuangan SQLite", page_icon="💰", layout="wide"
)

st.title("💰 Aplikasi Pencatatan Keuangan Bulanan (SQLite)")
st.write(
    "Data transaksi tersimpan aman di database lokal dan diolah otomatis per"
    " bulan."
)

# Sidebar untuk Input Transaksi
st.sidebar.header("➕ Tambah Transaksi Baru")

with st.sidebar.form("form_transaksi"):
  tanggal = st.date_input("Tanggal Transaksi", datetime.today())
  jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])

  if jenis == "Pemasukan":
    kategori = st.selectbox(
        "Kategori", ["Gaji", "Bonus", "Investasi", "Lainnya (Masuk)"]
    )
  else:
    kategori = st.selectbox(
        "Kategori",
        [
            "Makanan",
            "Transportasi",
            "Belanja",
            "Tagihan",
            "Asuransi",
            "Hiburan",
            "Lainnya (Keluar)",
        ],
    )

  jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=10000)
  keterangan = st.text_area("Keterangan (Opsional)")

  submit_button = st.form_submit_button(label="Simpan Transaksi")

# Proses saat tombol simpan ditekan
if submit_button:
  try:
    conn = sqlite3.connect("keuangan.db")
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO transaksi (tanggal, jenis, kategori, jumlah, keterangan)
            VALUES (?, ?, ?, ?, ?)
        """,
        (str(tanggal), jenis, kategori, int(jumlah), str(keterangan)),
    )
    conn.commit()
    conn.close()
    st.sidebar.success("✅ Transaksi berhasil disimpan ke database!")
    st.rerunn()  # Refresh halaman agar data langsung muncul
  except Exception as e:
    st.sidebar.error(f"❌ Gagal menyimpan data: {e}")

# --- TARIK & OLAH DATA DI STREAMLIT ---
df = get_data()

if not df.empty:
  # Konversi kolom Tanggal ke format datetime dan ekstrak Bulan (YYYY-MM)
  df["Tanggal_DT"] = pd.to_datetime(df["tanggal"], errors="coerce")
  df = df.dropna(subset=["Tanggal_DT"])
  df["Bulan"] = df["Tanggal_DT"].dt.strftime("%Y-%m")

  st.divider()

  # Filter Periode Bulan
  daftar_bulan = sorted(df["Bulan"].unique(), reverse=True)
  if daftar_bulan:
    pilih_bulan = st.selectbox(
        "📅 Pilih Periode Bulan untuk Dilihat:", daftar_bulan
    )

    # Filter dataframe berdasarkan bulan yang dipilih
    df_filtered = df[df["Bulan"] == pilih_bulan]

    st.subheader(f"📊 Ringkasan Keuangan Periode: {pilih_bulan}")

    # Hitung Ringkasan
    total_pemasukan = df_filtered[df_filtered["jenis"] == "Pemasukan"][
        "jumlah"
    ].sum()
    total_pengeluaran = df_filtered[df_filtered["jenis"] == "Pengeluaran"][
        "jumlah"
    ].sum()
    sisa_saldo = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}")
    col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
    col3.metric(
        "Sisa Saldo Bulan Ini",
        f"Rp {sisa_saldo:,.0f}",
        delta=f"Rp {sisa_saldo:,.0f}",
    )

    st.divider()

    st.subheader(f"📋 Riwayat Transaksi ({pilih_bulan})")
    # Ubah nama kolom agar lebih rapi saat ditampilkan di tabel
    df_display = df_filtered[
        ["tanggal", "jenis", "kategori", "jumlah", "keterangan"]
    ].copy()
    df_display.columns = ["Tanggal", "Jenis", "Kategori", "Jumlah", "Keterangan"]
    st.dataframe(df_display, use_container_width=True)
  else:
    st.info("📁 Belum ada data transaksi yang valid.")
else:
  st.info(
      "📁 Database masih kosong. Silakan tambah transaksi pertama melalui"
      " sidebar di kiri."
  )
