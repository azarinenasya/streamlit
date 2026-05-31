import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

.metric-card {
    background: #ffffff;
    border: 1.5px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.metric-card.crisis { border-color: #fca5a5; background: #fff5f5; }
.metric-card.rentan { border-color: #fcd34d; background: #fffbeb; }
.metric-card.aman   { border-color: #6ee7b7; background: #f0fdf4; }

/* Styling khusus untuk KPI Grid Q1 */
.kpi-box {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #edf2f7;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.kpi-label { font-size: 0.8rem; color: #718096; margin-bottom: 5px; font-weight: 600; text-transform: uppercase;}
.kpi-value { font-size: 1.4rem; font-weight: 800; color: #2d3748; }

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin: 2rem 0 1rem; padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
}
.bq-box {
    background: #f9fafb; border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0; padding: 14px 18px;
    margin: 10px 0; font-size: 0.88rem; line-height: 1.6; color: #374151;
}
.insight-box {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 12px; padding: 14px 18px; margin: 12px 0;
    font-size: 0.88rem; line-height: 1.7; color: #1e40af;
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────────
COLORS = {0: "#ef4444", 1: "#f59e0b", 2: "#10b981"}
CLUSTER_NAMES = {0: "Crisis", 1: "Rentan", 2: "Aman"}

FEATURE_COLS = [
    "Rent_Ratio", "Loan_Repayment_Ratio", "Insurance_Ratio", "Groceries_Ratio",
    "Transport_Ratio", "Eating_Out_Ratio", "Entertainment_Ratio", "Utilities_Ratio",
    "Healthcare_Ratio", "Education_Ratio", "Miscellaneous_Ratio", "Savings_Ratio",
]
PRETTY = {
    "Rent_Ratio": "Sewa Rumah", "Loan_Repayment_Ratio": "Cicilan Hutang",
    "Insurance_Ratio": "Asuransi", "Groceries_Ratio": "Belanja Kebutuhan",
    "Transport_Ratio": "Transportasi", "Eating_Out_Ratio": "Makan di Luar",
    "Entertainment_Ratio": "Hiburan", "Utilities_Ratio": "Tagihan Utilitas",
    "Healthcare_Ratio": "Kesehatan", "Education_Ratio": "Pendidikan",
    "Miscellaneous_Ratio": "Lain-lain", "Savings_Ratio": "Tabungan",
}

# ─── Data ────────────────────────────────────────────────────────────────────────
@st.cache_data
def generate_data(n=16432, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    specs = [
        (0, int(n*0.30), dict(rent=(0.25,0.30), loan=(0.10,0.20), ins=(0.02,0.04),
            groc=(0.13,0.15), trp=(0.06,0.08), eat=(0.04,0.05), ent=(0.03,0.05),
            util=(0.06,0.08), hlth=(0.03,0.05), edu=(0.00,0.04), misc=(0.01,0.03)), -0.06),
        (1, int(n*0.45), dict(rent=(0.18,0.25), loan=(0.04,0.10), ins=(0.025,0.045),
            groc=(0.11,0.14), trp=(0.055,0.075), eat=(0.025,0.045), ent=(0.025,0.045),
            util=(0.05,0.07), hlth=(0.035,0.048), edu=(0.05,0.085), misc=(0.015,0.026)), 0.05),
        (2, n - int(n*0.30) - int(n*0.45), dict(rent=(0.15,0.22), loan=(0.00,0.05),
            ins=(0.03,0.05), groc=(0.10,0.135), trp=(0.05,0.07), eat=(0.02,0.04),
            ent=(0.02,0.04), util=(0.04,0.065), hlth=(0.03,0.048), edu=(0.06,0.10),
            misc=(0.01,0.025)), 0.20),
    ]
    for cid, cnt, r, min_svng in specs:
        keys = list(r.keys())
        for _ in range(cnt):
            vals = {k: rng.uniform(*r[k]) for k in keys}
            svng = max(min_svng, 1 - sum(vals.values()))
            rows.append([cid] + [vals[k] for k in keys] + [svng])

    cols = ["Cluster"] + FEATURE_COLS
    df = pd.DataFrame(rows, columns=cols)
    df["Cluster_Label"] = df["Cluster"].map(CLUSTER_NAMES)
    return df

df = generate_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Financial Health")
    st.markdown("---")
    st.markdown("### Pertanyaan Bisnis")
    st.markdown("""
<div class='bq-box'><b>Q1.</b> Apa pola alokasi keuangan yang membedakan cluster Crisis, Rentan, dan Aman — dan seberapa besar proporsinya?</div>
<div class='bq-box'><b>Q2.</b> Fitur mana yang paling signifikan membedakan individu Crisis, Rentan, dan Aman?</div>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='margin-bottom:0;'>Financial Health Clustering</h1>", unsafe_allow_html=True)
st.markdown("---")

# ─── KPI Utama (Proporsi) ────────────────────────────────────────────────────────
counts = df["Cluster"].value_counts().sort_index()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"<div class='metric-card'><div class='kpi-label'>Total Data</div><div class='kpi-value'>{len(df):,}</div></div>", unsafe_allow_html=True)
for i, col in enumerate([c2, c3, c4]):
    count = counts.get(i, 0)
    pct = (count/len(df)*100)
    cls_name = CLUSTER_NAMES[i]
    color_class = cls_name.lower()
    col.markdown(f"""<div class='metric-card {color_class}'>
        <div class='kpi-label' style='color:{COLORS[i]}'>{cls_name}</div>
        <div class='kpi-value'>{pct:.1f}%</div>
        <div style='font-size:0.8rem; color:#9ca3af'>{count:,} orang</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Q1 – DYNAMIC KPI METRICS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q1 · Eksplorasi Alokasi Keuangan per Cluster</div>", unsafe_allow_html=True)

selected_cls = st.selectbox("Pilih Cluster untuk Detail Alokasi:", options=[0, 1, 2], 
                            format_func=lambda x: f"Cluster {x} - {CLUSTER_NAMES[x]}")

df_target = df[df["Cluster"] == selected_cls]
avg_vals = df_target[FEATURE_COLS].mean()

# Grid KPI untuk Rasio Keuangan
st.markdown(f"#### Rata-rata Penggunaan Dana - Cluster {CLUSTER_NAMES[selected_cls]}")
rows = [FEATURE_COLS[i:i + 4] for i in range(0, len(FEATURE_COLS), 4)]

for row_cols in rows:
    cols = st.columns(4)
    for i, feat in enumerate(row_cols):
        val = avg_vals[feat] * 100
        cols[i].markdown(f"""
        <div class='kpi-box'>
            <div class='kpi-label'>{PRETTY[feat]}</div>
            <div class='kpi-value' style='color:{COLORS[selected_cls]}'>{val:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

st.markdown(f"""<div class='insight-box'>
💡 <b>Insight Cluster {CLUSTER_NAMES[selected_cls]}:</b> Kelompok ini mengalokasikan 
<b>{avg_vals['Savings_Ratio']*100:.1f}%</b> untuk Tabungan dan <b>{avg_vals['Loan_Repayment_Ratio']*100:.1f}%</b> 
untuk Cicilan Hutang.
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Q2 – TOP 5 FITUR PALING BERBEDA
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q2 · Top 5 Fitur Paling Signifikan (Crisis vs Aman)</div>", unsafe_allow_html=True)

# Hitung selisih antara Crisis (0) dan Aman (2)
m0 = df[df["Cluster"] == 0][FEATURE_COLS].mean()
m2 = df[df["Cluster"] == 2][FEATURE_COLS].mean()

diff_df = pd.DataFrame({
    "Fitur": [PRETTY[f] for f in FEATURE_COLS],
    "Selisih": (m0 - m2).values * 100
})

# Ambil Top 5 berdasarkan nilai absolut selisih terbesar
diff_df["Abs_Selisih"] = diff_df["Selisih"].abs()
top_5_diff = diff_df.sort_values(by="Abs_Selisih", ascending=False).head(5)

col_chart, col_desc = st.columns([2, 1])

with col_chart:
    fig_top5 = px.bar(
        top_5_diff, y="Fitur", x="Selisih",
        orientation="h",
        color="Selisih",
        color_continuous_scale="RdYlGn_r", # Merah ke Hijau (Terbalik)
        labels={"Selisih": "Selisih Poin Persentase (Crisis - Aman)"},
        text_auto=".1f"
    )
    fig_top5.update_layout(
        showlegend=False, height=400, margin=dict(t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_top5, use_container_width=True)

with col_desc:
    st.markdown("#### Kenapa Fitur Ini Signifikan?")
    st.write("Grafik di samping menunjukkan fitur yang memiliki jurang pemisah paling lebar antara individu **Crisis** dan **Aman**.")
    
    for _, row in top_5_diff.iterrows():
        arah = "lebih tinggi" if row['Selisih'] > 0 else "lebih rendah"
        st.markdown(f"- **{row['Fitur']}**: Kelompok Crisis **{abs(row['Selisih']):.1f}%** {arah} dibanding kelompok Aman.")

st.markdown("""<div class='insight-box' style='background:#fff7ed; border-color:#fdba74; color:#9a3412'>
⚠️ <b>Kesimpulan Utama:</b> Sesuai hipotesis, <b>Savings_Ratio</b> dan <b>Loan_Repayment_Ratio</b> selalu muncul di Top 5. 
Individu Aman memiliki rasio tabungan yang jauh lebih besar, sementara individu Crisis terbebani oleh rasio cicilan hutang dan sewa rumah yang tinggi.
</div>""", unsafe_allow_html=True)
