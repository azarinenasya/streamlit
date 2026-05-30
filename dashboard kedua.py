import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="AI Financial Coach", layout="wide")

# 2. Fungsi Load Data
@st.cache_data
def load_data():
    # Streamlit akan mencoba membaca file df_val2.csv
    # Pastikan file ini ada di GitHub kamu
    try:
        df = pd.read_csv('df_clean_summary.csv')
        return df
    except Exception as e:
        st.error(f"Gagal memuat file: {e}")
        return None

df = load_data()

# 3. Header Dashboard
st.title("🏦 Personal Financial SMART Dashboard")

if df is not None:
    # Ambil baris terakhir sebagai data user terbaru
    user_data = df.iloc[-1]
    
    # Sidebar Input Gaji
    st.sidebar.header("Konfigurasi Gaji")
    income = st.sidebar.number_input("Pendapatan Bulanan (Rp)", value=10000000, step=500000)
    
    # --- PERBAIKAN KEYERROR CLUSTER ---
    # Cek apakah kolom 'Cluster' ada di file CSV
    if 'Cluster' in user_data:
        cluster_info = f"(Cluster {int(user_data['Cluster'])})"
    else:
        cluster_info = "" # Kosongkan jika kolom tidak ada
        
    st.sidebar.info(f"Menganalisis data terbaru {cluster_info}")

    # Metrics Utama
    c1, c2, c3, c4 = st.columns(4)
    # Gunakan .get() agar jika kolom tidak ada, aplikasi tidak crash (muncul 0)
    savings_ratio = user_data.get('Savings_Ratio', 0)
    rent_ratio = user_data.get('Rent_Ratio', 0)
    loan_ratio = user_data.get('Loan_Repayment_Ratio', 0)
    eat_out = user_data.get('Eating_Out_Ratio', 0)
    ent_ratio = user_data.get('Entertainment_Ratio', 0)
    health_ratio = user_data.get('Healthcare_Ratio', 0)

    c1.metric("Savings Ratio", f"{savings_ratio*100:.1f}%")
    c2.metric("Rent Ratio", f"{rent_ratio*100:.1f}%")
    c3.metric("Lifestyle Ratio", f"{(eat_out + ent_ratio)*100:.1f}%")
    c4.metric("Healthcare Ratio", f"{health_ratio*100:.1f}%")

    tab1, tab2 = st.tabs(["🛡️ SMART 1: Dana Darurat", "📈 SMART 2: Target Menabung"])

    # --- SMART 1: DANA DARURAT ---
    with tab1:
        st.subheader("Strategi Dana Darurat (3x Sewa + Cicilan)")
        fixed_cost_rp = (rent_ratio + loan_ratio) * income
        target_ef = 3 * fixed_cost_rp
        monthly_needed = target_ef / 12
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Target Total:** Rp {target_ef:,.0f}")
            st.write(f"**Tabungan bulanan untuk EF:** Rp {monthly_needed:,.0f}")
            if health_ratio > 0:
                st.success(f"✅ Healthcare tetap aman di {health_ratio*100:.1f}%")
        with col2:
            months = [f"Bln {i}" for i in range(1, 13)]
            acc = [monthly_needed * i for i in range(1, 13)]
            fig_ef = px.area(x=months, y=acc, title="Proyeksi 12 Bulan")
            st.plotly_chart(fig_ef, use_container_width=True)

    # --- SMART 2: TARGET SAVINGS ---
    with tab2:
        st.subheader("Konsistensi Tabungan 20% & Lifestyle 5%")
        lifestyle_now = eat_out + ent_ratio
        
        col_x, col_y = st.columns(2)
        with col_x:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = savings_ratio * 100,
                title = {'text': "Savings Ratio (%)"},
                gauge = {'axis': {'range': [0, 50]},
                         'threshold': {'line': {'color': "red", 'width': 4}, 'value': 20}}))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        with col_y:
            st.write(f"**Lifestyle saat ini:** {lifestyle_now*100:.1f}%")
            if lifestyle_now <= 0.05:
                st.success("✅ Lifestyle terkontrol di bawah 5%")
            else:
                potong = (lifestyle_now - 0.05) * income
                st.error(f"⚠️ Potong biaya lifestyle Rp {potong:,.0f}/bln")

    # Pie Chart
    st.divider()
    st.subheader("Struktur Pengeluaran Lengkap")
    # Ambil semua kolom kecuali Cluster dan Savings_Ratio untuk Pie Chart
    pie_data = user_data.drop(['Cluster', 'Savings_Ratio'], errors='ignore')
    fig_pie = px.pie(names=pie_data.index, values=pie_data.values, hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("Silakan pastikan file 'df_clean_summary.csv' tersedia di repository GitHub Anda.")
