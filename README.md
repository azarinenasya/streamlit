# 💰 Financial Health Clustering Dashboard

Dashboard interaktif untuk visualisasi hasil clustering kesehatan finansial individu menggunakan Streamlit dan Plotly.

## 📊 Tentang Dataset

Dataset terdiri dari **16.432 observasi** dengan **12 fitur rasio pengeluaran** terhadap pendapatan:

| Fitur | Deskripsi |
|---|---|
| `Rent_Ratio` | Proporsi pendapatan untuk sewa |
| `Loan_Repayment_Ratio` | Proporsi untuk cicilan pinjaman |
| `Savings_Ratio` | Proporsi yang ditabung |
| ... | 9 fitur lainnya |

## 🎯 Pertanyaan Bisnis (SMART)

### Q1 — Pola Alokasi Keuangan per Cluster
> Apa pola alokasi keuangan yang membedakan individu dalam kondisi krisis, rentan, dan aman secara finansial, dan seberapa besar proporsi masing-masing kelompok dari total 16.432 data?

**SMART Breakdown:**
- **Specific** — Mengidentifikasi rata-rata rasio 12 fitur per cluster
- **Measurable** — Nilai rata-rata rasio & persentase jumlah anggota cluster
- **Achievable** — Data tersedia lengkap dengan label cluster
- **Relevant** — Langsung menjawab karakteristik tiap segmen finansial
- **Time-bound** — Snapshot dataset saat ini (16.432 observasi)

### Q2 — Fitur Pembeda Crisis vs Aman
> Fitur finansial mana yang paling signifikan membedakan individu krisis dari individu aman, khususnya dari sisi `Savings_Ratio` dan `Loan_Repayment_Ratio`?

**SMART Breakdown:**
- **Specific** — Perbandingan Cluster 0 (Crisis) vs Cluster 2 (Aman) pada fitur kunci
- **Measurable** — Selisih mean antar cluster & distribusi (histogram, boxplot)
- **Achievable** — Dihitung dari statistik deskriptif yang tersedia
- **Relevant** — Savings_Ratio negatif & Loan tinggi = indikator krisis finansial
- **Time-bound** — Berdasarkan data yang sudah di-cleaning

## 🏷️ Label Cluster

| Cluster | Label | Karakteristik |
|---|---|---|
| 0 | 🔴 **Crisis** | Tabungan rendah/negatif, cicilan tinggi |
| 1 | 🟡 **Rentan** | Tabungan moderat, pengeluaran cukup tinggi |
| 2 | 🟢 **Aman** | Tabungan tinggi, cicilan rendah |

## 🚀 Cara Menjalankan Lokal

```bash
# Clone repo
git clone https://github.com/<username>/financial-dashboard.git
cd financial-dashboard

# Install dependencies
pip install -r requirements.txt

# Jalankan Streamlit
streamlit run app.py
```

## ☁️ Deploy ke Streamlit Cloud

1. Push repo ke GitHub
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Klik **New app** → pilih repo → set `app.py` sebagai main file
4. Klik **Deploy** 🎉

## 🛠️ Tech Stack

- **Streamlit** — Framework dashboard
- **Plotly** — Visualisasi interaktif (radar chart, boxplot, histogram, heatmap)
- **Pandas / NumPy** — Data processing
- **Google Fonts** — Syne + DM Sans typography
