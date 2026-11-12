from datetime import datetime
import pandas as pd
import streamlit as st

# Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard Keuangan Bulanan", page_icon="💰", layout="wide"
)

st.title("💰 Aplikasi Pencatatan Keuangan Bulanan")
st.write(
    "Catat pemasukan dan pengeluaranmu setiap bulan dengan mudah dan cepat."
)

# Sidebar untuk Input Transaksi
st.sidebar.header("➕ Tambah Transaksi Baru")

with st.sidebar.form("form_transaksi"):
    tanggal = st.date_input("Tanggal Transaksi", datetime.today())
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])

    # Kategori dinamis berdasarkan jenis transaksi
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
                "Hiburan",
                "Lainnya (Keluar)",
            ],
        )

    jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=10000)
    keterangan = st.text_area("Keterangan (Opsional)")

    submit_button = st.form_submit_button(label="Simpan Transaksi")

# Inisialisasi Data Session State (Database Lokal Sementara)
if "data_keuangan" not in st.session_state:
    st.session_state.data_keuangan = pd.DataFrame(
        columns=[
            "Tanggal",
            "Bulan",
            "Jenis",
            "Kategori",
            "Jumlah",
            "Keterangan",
        ]
    )

if submit_button:
    # Ekstrak bulan dari tanggal (Format: 'YYYY-MM') untuk pengelompokan bulanan
    bulan_str = tanggal.strftime("%Y-%m")

    data_baru = pd.DataFrame(
        {
            "Tanggal": [str(tanggal)],
            "Bulan": [bulan_str],
            "Jenis": [jenis],
            "Kategori": [kategori],
            "Jumlah": [jumlah],
            "Keterangan": [keterangan],
        }
    )

    st.session_state.data_keuangan = pd.concat(
        [st.session_state.data_keuangan, data_baru], ignore_index=True
    )
    st.sidebar.success("Transaksi berhasil dicatat!")

# --- TAMPILAN UTAMA DASHBOARD ---
df = st.session_state.data_keuangan

if not df.empty:
    st.divider()

    # Filter Periode Bulan
    daftar_bulan = sorted(df["Bulan"].unique(), reverse=True)
    pilih_bulan = st.selectbox(
        "📅 Pilih Periode Bulan untuk Dilihat:", daftar_bulan
    )

    # Filter dataframe berdasarkan bulan yang dipilih
    df_filtered = df[df["Bulan"] == pilih_bulan]

    st.subheader(f"📊 Ringkasan Keuangan Periode: {pilih_bulan}")

    # Hitung Ringkasan
    total_pemasukan = df_filtered[df_filtered["Jenis"] == "Pemasukan"][
        "Jumlah"
    ].sum()
    total_pengeluaran = df_filtered[df_filtered["Jenis"] == "Pengeluaran"][
        "Jumlah"
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
    st.dataframe(df_filtered, use_container_width=True)

    # Tombol Ekspor CSV (Cadangan lokal)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Unduh Seluruh Data ke CSV",
        data=csv,
        file_name="keuangan_pribadi_bulanan.csv",
        mime="text/csv",
    )
else:
    st.info(
        "👋 Belum ada transaksi tercatat. Silakan masukkan data melalui form di sidebar sebelah kiri."
    )