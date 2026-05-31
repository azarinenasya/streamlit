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

.cluster-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin-bottom: 6px; color: #6b7280;
}
.cluster-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem; font-weight: 800; line-height: 1; color: #111827;
}
.cluster-sub { font-size: 0.8rem; color: #9ca3af; margin-top: 4px; }

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

def hex_to_rgba(hex_color, alpha=0.15):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"

LIGHT_LAYOUT = dict(
    paper_bgcolor="white", plot_bgcolor="#f9fafb",
    font_color="#374151",
    legend=dict(bgcolor="white", bordercolor="#e5e7eb", borderwidth=1),
)

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

    cols = ["Cluster"] + [
        "Rent_Ratio","Loan_Repayment_Ratio","Insurance_Ratio","Groceries_Ratio",
        "Transport_Ratio","Eating_Out_Ratio","Entertainment_Ratio","Utilities_Ratio",
        "Healthcare_Ratio","Education_Ratio","Miscellaneous_Ratio","Savings_Ratio"
    ]
    df = pd.DataFrame(rows, columns=cols)
    df["Cluster_Label"] = df["Cluster"].map(CLUSTER_NAMES)
    return df

df = generate_data()

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
st.markdown("## Deskripsi")
st.info("Dashboard ini dirancang untuk memvisualisasikan dataset utama yang digunakan dalam pengembangan **SpendWise AI**.")
st.markdown("---")
st.markdown("### Pertanyaan Bisnis")
st.markdown("""
<div class='bq-box'><b>Q1.</b> Apa pola alokasi keuangan yang membedakan tiap cluster dan seberapa besar proporsinya?</div>
<div class='bq-box'><b>Q2.</b> Fitur finansial mana yang paling membedakan kondisi Crisis, Rentan, dan Aman?</div>
""", unsafe_allow_html=True)
st.markdown("---")
st.caption("Dataset: 16,432 observasi · 12 fitur rasio · 3 cluster")

df_f = df[df["Cluster"].isin(selected_clusters)]

# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='margin-bottom:0; color:#111827'>Financial Health Clustering</h1>
<p style='color:#9ca3af; font-size:0.9rem; margin-top:4px'>
Analisis Segmentasi Keuangan Individu
</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ─── KPI Cards ───────────────────────────────────────────────────────────────────
counts = df["Cluster"].value_counts().sort_index()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class='metric-card'>
        <div class='cluster-label'>Total Individu</div>
        <div class='cluster-value'>{len(df):,}</div>
        <div class='cluster-sub'>16.432 observasi</div>
    </div>""", unsafe_allow_html=True)
with col2:
    c = counts.get(0, 0)
    st.markdown(f"""<div class='metric-card crisis'>
        <div class='cluster-label' style='color:#ef4444'>🔴 Crisis</div>
        <div class='cluster-value' style='color:#ef4444'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)
with col3:
    c = counts.get(1, 0)
    st.markdown(f"""<div class='metric-card rentan'>
        <div class='cluster-label' style='color:#f59e0b'>🟡 Rentan</div>
        <div class='cluster-value' style='color:#f59e0b'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)
with col4:
    c = counts.get(2, 0)
    st.markdown(f"""<div class='metric-card aman'>
        <div class='cluster-label' style='color:#10b981'>🟢 Aman</div>
        <div class='cluster-value' style='color:#10b981'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Q1 – POLA ALOKASI KEUANGAN
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q1 · Pola Alokasi Keuangan per Cluster</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Perbandingan Antar Cluster", "🥧 Komposisi Pengeluaran", "📋 Tabel Ringkasan"])

with tab1:
    st.markdown("#### Rata-rata Alokasi per Kategori (% dari Pendapatan)")
    st.caption("Semakin panjang batang → semakin besar porsi pendapatan yang dialokasikan untuk kategori tersebut.")

    means = df_f.groupby("Cluster")[FEATURE_COLS].mean().reset_index()
    means_melt = means.melt(id_vars="Cluster", var_name="Feature", value_name="Ratio")
    means_melt["Cluster_Label"] = means_melt["Cluster"].map(CLUSTER_NAMES)
    means_melt["Feature_Pretty"] = means_melt["Feature"].map(PRETTY)
    means_melt["Persen"] = (means_melt["Ratio"] * 100).round(1)
    color_map = {CLUSTER_NAMES[k]: v for k, v in COLORS.items()}

    # Sort by overall mean descending for readability
    order = (df_f[FEATURE_COLS].mean().sort_values(ascending=False).index.tolist())
    order_pretty = [PRETTY[f] for f in order]

    fig_hbar = px.bar(
        means_melt, y="Feature_Pretty", x="Persen",
        color="Cluster_Label", barmode="group",
        color_discrete_map=color_map,
        orientation="h",
        category_orders={"Feature_Pretty": order_pretty},
        labels={"Feature_Pretty": "", "Persen": "% dari Pendapatan", "Cluster_Label": "Kondisi"},
        text="Persen",
    )
    fig_hbar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_hbar.update_layout(
        paper_bgcolor="white", plot_bgcolor="#f9fafb", font_color="#374151",
        xaxis=dict(gridcolor="#e5e7eb", ticksuffix="%", range=[0, 60]),
        yaxis=dict(gridcolor="#e5e7eb"),
        height=520, margin=dict(t=10, b=40, l=10, r=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="white", bordercolor="#e5e7eb", borderwidth=1),
    )
    st.plotly_chart(fig_hbar, use_container_width=True)

    st.markdown("""<div class='insight-box'>
    💡 <b>Cara membaca:</b> Perhatikan perbedaan panjang batang antar warna pada baris yang sama.
    Batang <b style='color:#ef4444'>merah (Crisis)</b> paling panjang di <i>Cicilan & Sewa</i> — artinya kelompok ini menghabiskan
    lebih banyak untuk hutang. Batang <b style='color:#10b981'>hijau (Aman)</b> paling panjang di <i>Tabungan</i>.
    </div>""", unsafe_allow_html=True)

with tab2:
    st.markdown("#### Detail Alokasi per Kategori")
    st.caption("Gunakan filter di bawah untuk melihat detail angka tiap kondisi keuangan.")
    
    # FILTER diletakkan di dalam Tab 2 agar hanya berpengaruh/muncul di sini
    selected_cls = st.selectbox(
        "Pilih Kondisi untuk Detail:", 
        options=[0, 1, 2], 
        format_func=lambda x: f"{CLUSTER_NAMES[x]}",
        key="filter_q1_tab2" # Key unik agar tidak bentrok
    )

    df_target = df[df["Cluster"] == selected_cls]
    avg_vals = df_target[FEATURE_COLS].mean()

    # --- MULAI GRID KPI ---
    # Membagi fitur menjadi baris-baris (4 kolom per baris)
    for i in range(0, len(FEATURE_COLS), 4):
        cols = st.columns(4)
        for j, feat in enumerate(FEATURE_COLS[i:i+4]):
            val = avg_vals[feat] * 100
            cols[j].markdown(f"""
            <div class='kpi-box'>
                <div class='kpi-label'>{PRETTY[feat]}</div>
                <div class='kpi-value' style='color:{COLORS[selected_cls]}'>{val:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    # Insight Box di dalam Tab 2
    st.markdown(f"""
    <div class='insight-box'>
        💡 <b>Insight {CLUSTER_NAMES[selected_cls]}:</b> Kelompok ini menghabiskan rata-rata 
        <b>{avg_vals['Savings_Ratio']*100:.1f}%</b> untuk Tabungan.
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("#### Rata-rata Alokasi per Kategori per Cluster")
    means_tbl = df_f.groupby("Cluster_Label")[FEATURE_COLS].mean() * 100
    means_tbl.columns = [PRETTY[c] for c in FEATURE_COLS]
    means_tbl = means_tbl.round(1).astype(str) + "%"
    st.dataframe(means_tbl, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Q2 – FITUR PEMBEDA: SEMUA CLUSTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q2 · Apa yang Membedakan Crisis, Rentan, dan Aman?</div>", unsafe_allow_html=True)

m0 = df[df["Cluster"] == 0][FEATURE_COLS].mean()
m1 = df[df["Cluster"] == 1][FEATURE_COLS].mean()
m2 = df[df["Cluster"] == 2][FEATURE_COLS].mean()

tab4, tab5, tab6 = st.tabs(["🏆 Fitur Paling Berbeda", "📊 Perbandingan Langsung", "📋 Tabel Selisih"])

with tab4:
    st.markdown("<div class='section-header'>Q2 · Fitur Paling Signifikan (Top 5 Pembeda Crisis vs Aman)</div>", unsafe_allow_html=True)

# Hitung selisih
    m0 = df[df["Cluster"] == 0][FEATURE_COLS].mean()
    m2 = df[df["Cluster"] == 2][FEATURE_COLS].mean()
    diff_df = pd.DataFrame({
        "Fitur": [PRETTY[f] for f in FEATURE_COLS],
        "Selisih": (m0 - m2).values * 100
})
    diff_df["Abs_Selisih"] = diff_df["Selisih"].abs()
    top_5 = diff_df.sort_values(by="Abs_Selisih", ascending=True).tail(5) # Asc True agar bar yang terpanjang di atas di plotly h-bar

# Warna custom: Merah jika Crisis > Aman, Hijau jika Aman > Crisis (Negatif)
    top_5["Warna"] = top_5["Selisih"].apply(lambda x: COLORS[0] if x > 0 else COLORS[2])

fig_q2 = px.bar(
    top_5, x="Selisih", y="Fitur",
    orientation="h",
    text_auto=".1f",
    labels={"Selisih": "Selisih Poin Persentase (Crisis vs Aman)"},
    color="Warna", 
    color_discrete_map="identity" # Menggunakan kode warna langsung dari kolom 'Warna'
)

fig_q2.update_layout(
    height=400,
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0", zeroline=True, zerolinecolor="#333"),
    yaxis=dict(title=""),
    margin=dict(t=20, b=20, l=10, r=40)
)

col_left, col_right = st.columns([2, 1])
with col_left:
    st.plotly_chart(fig_q2, use_container_width=True)

with col_right:
    st.markdown("### Kesimpulan Fitur")
    st.write("Berdasarkan perbandingan antara cluster **Crisis** dan **Aman**, ditemukan 5 fitur dengan perbedaan paling mencolok:")
    
    # Ambil fitur teratas (terakhir karena sort ascending)
    top_feature = top_5.iloc[-1]
    st.success(f"**{top_feature['Fitur']}** adalah pembeda nomor 1 dengan selisih **{abs(top_feature['Selisih']):.1f}%**.")
    
    st.info("""
    **Cara Membaca Grafik:**
    *   **Batang Merah (+):** Pengeluaran yang jauh lebih tinggi di kelompok **Crisis**.
    *   **Batang Hijau (-):** Alokasi yang jauh lebih tinggi di kelompok **Aman** (umumnya Tabungan).
    """)

st.markdown(f"""
<div class='insight-box'>
    💡 <b>Analisis Bisnis:</b> Cluster <b>Crisis</b> (merah) sangat dipengaruhi oleh tingginya rasio <b>{top_5[top_5['Selisih']>0]['Fitur'].iloc[-1]}</b>, 
    sedangkan cluster <b>Aman</b> (hijau) memiliki keunggulan mutlak pada rasio <b>Tabungan</b>. 
    Hal ini menunjukkan bahwa strategi intervensi harus difokuskan pada pengurangan beban cicilan/sewa bagi kelompok Crisis.
</div>
""", unsafe_allow_html=True)

with tab5:
    st.markdown("#### Perbandingan Nilai Rata-rata per Fitur")
    feat_sel = st.selectbox(
        "Pilih kategori yang ingin dibandingkan:",
        FEATURE_COLS, format_func=lambda x: PRETTY[x], key="featsel2"
    )

    means_bar = pd.DataFrame({
        "Kondisi": [CLUSTER_NAMES[i] for i in [0, 1, 2]],
        "Nilai": [df[df["Cluster"] == i][feat_sel].mean() * 100 for i in [0, 1, 2]],
        "Warna": [COLORS[i] for i in [0, 1, 2]],
    })

    fig_compare = px.bar(
        means_bar, x="Kondisi", y="Nilai",
        color="Kondisi",
        color_discrete_map={CLUSTER_NAMES[k]: v for k, v in COLORS.items()},
        labels={"Nilai": "% dari Pendapatan", "Kondisi": ""},
        text="Nilai",
    )
    fig_compare.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_compare.update_layout(
        **LIGHT_LAYOUT,
        yaxis=dict(gridcolor="#e5e7eb", ticksuffix="%",
                   range=[0, means_bar["Nilai"].max() * 1.3]),
        showlegend=False,
        height=380, margin=dict(t=20, b=20),
        title=dict(text=f"Rata-rata <b>{PRETTY[feat_sel]}</b> per Kondisi",
                   font_color="#374151", font_size=14),
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # Mini insight per feature
    v0 = df[df["Cluster"]==0][feat_sel].mean()*100
    v1 = df[df["Cluster"]==1][feat_sel].mean()*100
    v2 = df[df["Cluster"]==2][feat_sel].mean()*100
    st.markdown(f"""<div class='insight-box'>
    📌 Untuk <b>{PRETTY[feat_sel]}</b>: kelompok <b style='color:#ef4444'>Crisis rata-rata {v0:.1f}%</b>,
    <b style='color:#f59e0b'>Rentan {v1:.1f}%</b>, dan
    <b style='color:#10b981'>Aman {v2:.1f}%</b> dari pendapatan mereka.
    Selisih Crisis vs Aman: <b>{v0-v2:+.1f} poin persen</b>.
    </div>""", unsafe_allow_html=True)

with tab6:
    st.markdown("#### Tabel Selisih Rata-rata Antar Kondisi")
    st.caption("Nilai positif (+) = kondisi pertama lebih tinggi. Nilai negatif (−) = kondisi pertama lebih rendah.")

    tbl = pd.DataFrame({
        "Kategori": [PRETTY[f] for f in FEATURE_COLS],
        "Crisis (%)": (m0 * 100).round(1).values,
        "Rentan (%)": (m1 * 100).round(1).values,
        "Aman (%)": (m2 * 100).round(1).values,
        "Crisis vs Aman": ((m0 - m2) * 100).round(1).apply(lambda x: f"{x:+.1f}%").values,
        "Crisis vs Rentan": ((m0 - m1) * 100).round(1).apply(lambda x: f"{x:+.1f}%").values,
        "Rentan vs Aman": ((m1 - m2) * 100).round(1).apply(lambda x: f"{x:+.1f}%").values,
    })
    tbl["Crisis (%)"] = tbl["Crisis (%)"].apply(lambda x: f"{x:.1f}%")
    tbl["Rentan (%)"] = tbl["Rentan (%)"].apply(lambda x: f"{x:.1f}%")
    tbl["Aman (%)"]   = tbl["Aman (%)"].apply(lambda x: f"{x:.1f}%")
    sort_order = (m0 - m2).abs().sort_values(ascending=False).index.tolist()
    tbl_sorted = tbl.set_index("Kategori").loc[[PRETTY[f] for f in sort_order]].reset_index()
    tbl_sorted.index = range(1, len(tbl_sorted) + 1)
    st.dataframe(tbl_sorted, use_container_width=True)
