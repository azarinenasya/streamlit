import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="AI Financial Coach", layout="wide")

# 2. Fungsi Load Data
@st.cache_data
def load_data():
    # Pastikan file df_val2.csv sudah kamu upload ke GitHub yang sama
    try:
        df = pd.read_csv('df_val2.csv')
        return df
    except:
        return None

df = load_data()

# 3. Header Dashboard
st.title("🏦 Personal Financial SMART Dashboard")
st.markdown("Dashboard ini menganalisis kesehatan finansial berdasarkan target SMART yang telah ditetapkan.")

if df is not None:
    # Pilih data orang (baris) mana yang mau dianalisis
    # Karena datanya fokus ke satu orang, kita ambil baris terakhir sebagai data terbaru
    user_data = df.iloc[-1]
    
    # Sidebar untuk Input Gaji (Agar rasio bisa jadi Rupiah)
    st.sidebar.header("Konfigurasi Gaji")
    income = st.sidebar.number_input("Pendapatan Bulanan (Rp)", value=10000000, step=500000)
    st.sidebar.info(f"Menganalisis data baris ke-{len(df)} (Cluster {int(user_data['Cluster'])})")

    # Metrics Utama
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Savings Ratio", f"{user_data['Savings_Ratio']*100:.1f}%")
    c2.metric("Rent Ratio", f"{user_data['Rent_Ratio']*100:.1f}%")
    c3.metric("Lifestyle Ratio", f"{(user_data['Eating_Out_Ratio'] + user_data['Entertainment_Ratio'])*100:.1f}%")
    c4.metric("Healthcare Ratio", f"{user_data['Healthcare_Ratio']*100:.1f}%")

    # TABS UNTUK PERTANYAAN SMART
    tab1, tab2 = st.tabs(["🛡️ SMART 1: Dana Darurat", "📈 SMART 2: Target Menabung"])

    # --- ANALISIS SMART 1 (DANA DARURAT) ---
    with tab1:
        st.subheader("Strategi Dana Darurat (3x Sewa + Cicilan dalam 12 Bulan)")
        
        # Hitung biaya tetap (Rent + Loan)
        fixed_cost_ratio = user_data['Rent_Ratio'] + user_data['Loan_Repayment_Ratio']
        fixed_cost_rp = fixed_cost_ratio * income
        target_ef = 3 * fixed_cost_rp
        monthly_needed = target_ef / 12
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Target Total Dana Darurat:** Rp {target_ef:,.0f}")
            st.write(f"**Tabungan EF yang dibutuhkan:** Rp {monthly_needed:,.0f} /bulan")
            
            # Cek Healthcare Ratio (Elemen SMART: Tanpa mengurangi Healthcare)
            if user_data['Healthcare_Ratio'] > 0:
                st.success(f"✅ **Healthcare Terjamin:** Alokasi kesehatan Anda tetap di {user_data['Healthcare_Ratio']*100:.1f}%")
            else:
                st.error("⚠️ **Peringatan:** Alokasi kesehatan Anda 0%. Segera buat budget kesehatan.")

        with col2:
            # Grafik Akumulasi
            months = [f"Bulan {i}" for i in range(1, 13)]
            accumulation = [monthly_needed * i for i in range(1, 13)]
            fig_ef = px.area(x=months, y=accumulation, title="Proyeksi Akumulasi 12 Bulan", labels={'y':'Saldo Rp', 'x':''})
            st.plotly_chart(fig_ef, use_container_width=True)

    # --- ANALISIS SMART 2 (SAVINGS & LIFESTYLE) ---
    with tab2:
        st.subheader("Konsistensi Tabungan 20% & Batas Lifestyle 5%")
        
        savings_now = user_data['Savings_Ratio']
        lifestyle_now = user_data['Eating_Out_Ratio'] + user_data['Entertainment_Ratio']
        
        col_x, col_y = st.columns(2)
        with col_x:
            # Indikator Tabungan
            fig_savings = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = savings_now * 100,
                title = {'text': "Savings Ratio (%)"},
                gauge = {'axis': {'range': [None, 50]},
                         'steps': [{'range': [0, 20], 'color': "lightcoral"},
                                   {'range': [20, 50], 'color': "lightgreen"}],
                         'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 20}}))
            st.plotly_chart(fig_savings, use_container_width=True)
            
            if savings_now >= 0.20:
                st.success("✅ Target tabungan 20% tercapai!")
            else:
                st.warning(f"📉 Kurang {(0.20 - savings_now)*100:.1f}% lagi untuk mencapai target.")

        with col_y:
            # Indikator Lifestyle
            st.write(f"**Rasio Lifestyle Saat Ini:** {lifestyle_now*100:.1f}%")
            if lifestyle_now <= 0.05:
                st.success("✅ Pengeluaran gaya hidup di bawah batas 5%.")
            else:
                potongan = (lifestyle_now - 0.05) * income
                st.error(f"⚠️ **Lifestyle Creep!** Anda harus memotong pengeluaran gaya hidup sebesar **Rp {potongan:,.0f}** agar target tabungan tercapai.")
            
            # Pie Chart Pengeluaran
            labels = ['Rent', 'Loan', 'Insurance', 'Groceries', 'Transport', 'Lifestyle', 'Healthcare', 'Education', 'Misc']
            values = [user_data['Rent_Ratio'], user_data['Loan_Repayment_Ratio'], user_data['Insurance_Ratio'], 
                      user_data['Groceries_Ratio'], user_data['Transport_Ratio'], lifestyle_now, 
                      user_data['Healthcare_Ratio'], user_data['Education_Ratio'], user_data['Miscellaneous_Ratio']]
            fig_pie = px.pie(names=labels, values=values, title="Struktur Pengeluaran")
            st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.error("File 'df_val2.csv' tidak ditemukan di GitHub. Pastikan nama file sesuai.")
