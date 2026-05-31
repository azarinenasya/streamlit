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
with st.sidebar:
    st.markdown("## 💰 Financial Health")
    st.markdown("---")
    st.markdown("### Filter Cluster")
    selected_clusters = st.multiselect(
        "Tampilkan cluster:",
        options=[0, 1, 2], default=[0, 1, 2],
        format_func=lambda x: f"{'🔴' if x==0 else '🟡' if x==1 else '🟢'} Cluster {x} – {CLUSTER_NAMES[x]}"
    )
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
Analisis Segmentasi Keuangan Individu · Clustering Dashboard
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
        **LIGHT_LAYOUT,
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
    st.markdown("#### Ke Mana Uang Pergi? (Komposisi per Cluster)")
    st.caption("Luas irisan menunjukkan seberapa besar porsi pengeluaran untuk tiap kategori.")

    col_a, col_b, col_c = st.columns(3)
    palette = px.colors.qualitative.Pastel
    for col, cid in zip([col_a, col_b, col_c], [0, 1, 2]):
        if cid not in selected_clusters:
            col.empty()
            continue
        sub = df[df["Cluster"] == cid][FEATURE_COLS].mean()
        labels = [PRETTY[c] for c in FEATURE_COLS]
        emoji = "🔴" if cid == 0 else "🟡" if cid == 1 else "🟢"
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=(sub.values * 100).round(1),
            hole=0.4,
            marker=dict(colors=palette[:len(labels)]),
            textinfo="label+percent",
            textfont_size=11,
            hovertemplate="<b>%{label}</b><br>%{value:.1f}% dari pendapatan<extra></extra>",
        ))
        fig_pie.update_layout(
            title=dict(text=f"{emoji} {CLUSTER_NAMES[cid]}", font_color=COLORS[cid],
                       font_size=16, font_family="Syne"),
            paper_bgcolor="white", showlegend=False,
            height=380, margin=dict(t=50, b=10, l=10, r=10),
        )
        col.plotly_chart(fig_pie, use_container_width=True)

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

tab4, tab5, tab6 = st.tabs(["🏆 Fitur Paling Berbeda", "📊 Perbandingan Langsung", "📋 Tabel Selisih"])

with tab4:
    st.markdown("#### Fitur yang Paling Membedakan Antar Kondisi")
    st.caption("Grafik ini menunjukkan seberapa 'jauh' nilai tiap fitur antara kondisi Crisis dan Aman. Makin panjang, makin besar perbedaannya.")

    m0 = df[df["Cluster"] == 0][FEATURE_COLS].mean()
    m1 = df[df["Cluster"] == 1][FEATURE_COLS].mean()
    m2 = df[df["Cluster"] == 2][FEATURE_COLS].mean()

    diff_df = pd.DataFrame({
        "Fitur": [PRETTY[f] for f in FEATURE_COLS],
        "Crisis vs Aman": ((m0 - m2) * 100).round(1).values,
        "Crisis vs Rentan": ((m0 - m1) * 100).round(1).values,
        "Rentan vs Aman": ((m1 - m2) * 100).round(1).values,
    })
    diff_melt = diff_df.melt(id_vars="Fitur", var_name="Perbandingan", value_name="Selisih (%)")
    diff_melt["abs"] = diff_melt["Selisih (%)"].abs()

    # Sort by Crisis vs Aman
    sort_order = diff_df.reindex(diff_df["Crisis vs Aman"].abs().sort_values(ascending=True).index)["Fitur"].tolist()

    COMP_COLORS = {
        "Crisis vs Aman": "#ef4444",
        "Crisis vs Rentan": "#f59e0b",
        "Rentan vs Aman": "#10b981",
    }

    fig_diff = px.bar(
        diff_melt, y="Fitur", x="Selisih (%)", color="Perbandingan",
        barmode="group", orientation="h",
        color_discrete_map=COMP_COLORS,
        category_orders={"Fitur": sort_order},
        labels={"Selisih (%)": "Selisih (poin %)", "Fitur": ""},
        text="Selisih (%)",
    )
    fig_diff.update_traces(texttemplate="%{text:+.1f}%", textposition="outside")
    fig_diff.add_vline(x=0, line_dash="dash", line_color="#9ca3af", line_width=1)
    fig_diff.update_layout(
        **LIGHT_LAYOUT,
        xaxis=dict(gridcolor="#e5e7eb", ticksuffix="%", zeroline=False),
        yaxis=dict(gridcolor="#e5e7eb"),
        height=520, margin=dict(t=10, b=40, l=10, r=100),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="white", bordercolor="#e5e7eb", borderwidth=1),
    )
    st.plotly_chart(fig_diff, use_container_width=True)

    st.markdown("""<div class='insight-box'>
    💡 <b>Cara membaca:</b> Nilai <b>positif (+)</b> berarti kondisi pertama lebih tinggi, nilai <b>negatif (−)</b> berarti lebih rendah.
    Contoh: <i>Crisis vs Aman</i> di Tabungan bernilai negatif besar → kelompok Crisis menabung jauh lebih sedikit dari Aman.
    </div>""", unsafe_allow_html=True)

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
    tbl_sorted = tbl.reindex(
        ((m0 - m2).abs().sort_values(ascending=False)).index
    ).reset_index(drop=True)
    tbl_sorted.index = range(1, len(tbl_sorted)+1)
    st.dataframe(tbl_sorted, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#d1d5db; font-size:0.78rem'>
Financial Health Clustering Dashboard · Data Science Project · Streamlit + Plotly
</p>
""", unsafe_allow_html=True)
