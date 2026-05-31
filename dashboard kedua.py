import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Financial Health Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (Light Theme) ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

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
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 6px;
    color: #6b7280;
}
.cluster-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    color: #111827;
}
.cluster-sub { font-size: 0.8rem; color: #9ca3af; margin-top: 4px; }

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 2rem 0 1rem;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
}

.bq-box {
    background: #f9fafb;
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.88rem;
    line-height: 1.6;
    color: #374151;
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
    "Rent_Ratio": "Sewa", "Loan_Repayment_Ratio": "Cicilan",
    "Insurance_Ratio": "Asuransi", "Groceries_Ratio": "Belanja",
    "Transport_Ratio": "Transportasi", "Eating_Out_Ratio": "Makan Luar",
    "Entertainment_Ratio": "Hiburan", "Utilities_Ratio": "Utilitas",
    "Healthcare_Ratio": "Kesehatan", "Education_Ratio": "Pendidikan",
    "Miscellaneous_Ratio": "Lain-lain", "Savings_Ratio": "Tabungan",
}

def hex_to_rgba(hex_color, alpha=0.15):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ─── Data Generation ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_data(n=16432, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    n0 = int(n * 0.30)
    for _ in range(n0):
        rent = rng.uniform(0.25, 0.30); loan = rng.uniform(0.10, 0.20)
        ins = rng.uniform(0.02, 0.04); groc = rng.uniform(0.13, 0.15)
        trp = rng.uniform(0.06, 0.08); eat = rng.uniform(0.04, 0.05)
        ent = rng.uniform(0.03, 0.05); util = rng.uniform(0.06, 0.08)
        hlth = rng.uniform(0.03, 0.05); edu = rng.uniform(0.00, 0.04)
        misc = rng.uniform(0.01, 0.03)
        svng = max(-0.06, 1 - (rent+loan+ins+groc+trp+eat+ent+util+hlth+edu+misc))
        rows.append([0, rent, loan, ins, groc, trp, eat, ent, util, hlth, edu, misc, svng])

    n1 = int(n * 0.45)
    for _ in range(n1):
        rent = rng.uniform(0.18, 0.25); loan = rng.uniform(0.04, 0.10)
        ins = rng.uniform(0.025, 0.045); groc = rng.uniform(0.11, 0.14)
        trp = rng.uniform(0.055, 0.075); eat = rng.uniform(0.025, 0.045)
        ent = rng.uniform(0.025, 0.045); util = rng.uniform(0.05, 0.07)
        hlth = rng.uniform(0.035, 0.048); edu = rng.uniform(0.05, 0.085)
        misc = rng.uniform(0.015, 0.026)
        svng = max(0.05, 1 - (rent+loan+ins+groc+trp+eat+ent+util+hlth+edu+misc))
        rows.append([1, rent, loan, ins, groc, trp, eat, ent, util, hlth, edu, misc, svng])

    n2 = n - n0 - n1
    for _ in range(n2):
        rent = rng.uniform(0.15, 0.22); loan = rng.uniform(0.00, 0.05)
        ins = rng.uniform(0.03, 0.05); groc = rng.uniform(0.10, 0.135)
        trp = rng.uniform(0.05, 0.07); eat = rng.uniform(0.02, 0.04)
        ent = rng.uniform(0.02, 0.04); util = rng.uniform(0.04, 0.065)
        hlth = rng.uniform(0.03, 0.048); edu = rng.uniform(0.06, 0.10)
        misc = rng.uniform(0.01, 0.025)
        svng = max(0.20, 1 - (rent+loan+ins+groc+trp+eat+ent+util+hlth+edu+misc))
        rows.append([2, rent, loan, ins, groc, trp, eat, ent, util, hlth, edu, misc, svng])

    cols = ["Cluster", "Rent_Ratio", "Loan_Repayment_Ratio", "Insurance_Ratio",
            "Groceries_Ratio", "Transport_Ratio", "Eating_Out_Ratio",
            "Entertainment_Ratio", "Utilities_Ratio", "Healthcare_Ratio",
            "Education_Ratio", "Miscellaneous_Ratio", "Savings_Ratio"]
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
        options=[0, 1, 2],
        default=[0, 1, 2],
        format_func=lambda x: f"{'🔴' if x==0 else '🟡' if x==1 else '🟢'} Cluster {x} – {CLUSTER_NAMES[x]}"
    )
    st.markdown("---")
    st.markdown("### Pertanyaan Bisnis")
    st.markdown("""
<div class='bq-box'><b>Q1.</b> Apa pola alokasi keuangan yang membedakan tiap cluster dan seberapa besar proporsinya?</div>
<div class='bq-box'><b>Q2.</b> Fitur finansial mana yang paling signifikan membedakan individu crisis dari aman?</div>
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
    st.markdown(f"""
    <div class='metric-card'>
        <div class='cluster-label'>Total Individu</div>
        <div class='cluster-value'>{len(df):,}</div>
        <div class='cluster-sub'>16.432 observasi</div>
    </div>""", unsafe_allow_html=True)

with col2:
    c = counts.get(0, 0)
    st.markdown(f"""
    <div class='metric-card crisis'>
        <div class='cluster-label' style='color:#ef4444'>🔴 Crisis</div>
        <div class='cluster-value' style='color:#ef4444'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)

with col3:
    c = counts.get(1, 0)
    st.markdown(f"""
    <div class='metric-card rentan'>
        <div class='cluster-label' style='color:#f59e0b'>🟡 Rentan</div>
        <div class='cluster-value' style='color:#f59e0b'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)

with col4:
    c = counts.get(2, 0)
    st.markdown(f"""
    <div class='metric-card aman'>
        <div class='cluster-label' style='color:#10b981'>🟢 Aman</div>
        <div class='cluster-value' style='color:#10b981'>{c:,}</div>
        <div class='cluster-sub'>{c/len(df)*100:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Chart layout helpers ────────────────────────────────────────────────────────
LIGHT_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="#f9fafb",
    font_color="#374151",
    legend=dict(bgcolor="white", bordercolor="#e5e7eb", borderwidth=1),
)

# ═══════════════════════════════════════════════════════════════════════════════
# Q1
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q1 · Pola Alokasi Keuangan per Cluster</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Radar Chart", "📈 Bar Comparison", "🥧 Komposisi"])

with tab1:
    means = df_f.groupby("Cluster")[FEATURE_COLS].mean()
    categories = [PRETTY[c] for c in FEATURE_COLS]

    fig_radar = go.Figure()
    for cluster_id in selected_clusters:
        if cluster_id not in means.index:
            continue
        vals = means.loc[cluster_id].tolist()
        vals += vals[:1]
        cats = categories + [categories[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=cats, fill='toself',
            name=f"Cluster {cluster_id} – {CLUSTER_NAMES[cluster_id]}",
            line_color=COLORS[cluster_id],
            fillcolor=hex_to_rgba(COLORS[cluster_id], 0.15),
            opacity=0.9,
        ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 0.55], tickformat=".0%",
                            gridcolor="#e5e7eb", tickfont_color="#6b7280"),
            angularaxis=dict(gridcolor="#e5e7eb", tickfont_color="#374151"),
            bgcolor="white",
        ),
        paper_bgcolor="white",
        font_color="#374151",
        legend=dict(bgcolor="white"),
        height=450, margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with tab2:
    means_all = df_f.groupby("Cluster_Label")[FEATURE_COLS].mean().reset_index()
    means_melt = means_all.melt(id_vars="Cluster_Label", var_name="Feature", value_name="Ratio")
    means_melt["Feature_Pretty"] = means_melt["Feature"].map(PRETTY)
    color_map = {CLUSTER_NAMES[k]: v for k, v in COLORS.items()}

    fig_bar = px.bar(
        means_melt, x="Feature_Pretty", y="Ratio",
        color="Cluster_Label", barmode="group",
        color_discrete_map=color_map,
        labels={"Feature_Pretty": "Kategori", "Ratio": "Rata-rata Rasio", "Cluster_Label": "Cluster"},
    )
    fig_bar.update_layout(
        **LIGHT_LAYOUT,
        xaxis=dict(gridcolor="#e5e7eb", tickangle=-30),
        yaxis=dict(gridcolor="#e5e7eb", tickformat=".0%"),
        height=420, margin=dict(t=20, b=80),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    col_a, col_b, col_c = st.columns(3)
    for col, cid in zip([col_a, col_b, col_c], [0, 1, 2]):
        if cid not in selected_clusters:
            continue
        sub = df[df["Cluster"] == cid][FEATURE_COLS].mean()
        labels = [PRETTY[c] for c in FEATURE_COLS]
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=sub.values, hole=0.45,
            marker=dict(colors=px.colors.sequential.Plasma_r[:len(labels)]),
            textinfo="none",
        ))
        fig_pie.update_layout(
            title=dict(text=f"{'🔴' if cid==0 else '🟡' if cid==1 else '🟢'} {CLUSTER_NAMES[cid]}",
                       font_color=COLORS[cid], font_size=15, font_family="Syne"),
            paper_bgcolor="white", plot_bgcolor="white",
            font_color="#374151",
            legend=dict(bgcolor="white", font_size=10),
            height=340, margin=dict(t=50, b=10, l=10, r=10),
        )
        col.plotly_chart(fig_pie, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Q2
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-header'>Q2 · Fitur Pembeda: Crisis vs Aman</div>", unsafe_allow_html=True)

tab4, tab5, tab6 = st.tabs(["📦 Box Plot Distribusi", "📉 Savings & Loan Focus", "🔥 Heatmap Mean"])

with tab4:
    feat_sel = st.selectbox("Pilih fitur:", FEATURE_COLS, format_func=lambda x: PRETTY[x], key="boxsel")
    df_box = df_f.copy()
    df_box["Cluster_Label"] = df_box["Cluster"].map(CLUSTER_NAMES)
    color_map2 = {CLUSTER_NAMES[k]: v for k, v in COLORS.items()}

    fig_box = px.box(
        df_box, x="Cluster_Label", y=feat_sel,
        color="Cluster_Label", color_discrete_map=color_map2, points="outliers",
        labels={"Cluster_Label": "Cluster", feat_sel: f"Rasio {PRETTY[feat_sel]}"},
    )
    fig_box.update_layout(
        **LIGHT_LAYOUT,
        yaxis=dict(gridcolor="#e5e7eb", tickformat=".0%"),
        xaxis=dict(gridcolor="#e5e7eb"),
        showlegend=False, height=400, margin=dict(t=20),
    )
    st.plotly_chart(fig_box, use_container_width=True)

with tab5:
    key_feats = ["Savings_Ratio", "Loan_Repayment_Ratio"]
    col_s, col_l = st.columns(2)

    for col, feat in zip([col_s, col_l], key_feats):
        fig_hist = go.Figure()
        for cid in [0, 2]:
            sub = df[df["Cluster"] == cid][feat]
            fig_hist.add_trace(go.Histogram(
                x=sub, name=CLUSTER_NAMES[cid],
                marker_color=COLORS[cid], opacity=0.75,
                xbins=dict(size=0.01), histnorm="probability density",
            ))
        fig_hist.update_layout(
            barmode="overlay",
            title=dict(text=PRETTY[feat], font_color="#374151", font_size=13, font_family="Syne"),
            **LIGHT_LAYOUT,
            xaxis=dict(gridcolor="#e5e7eb", tickformat=".0%"),
            yaxis=dict(gridcolor="#e5e7eb"),
            height=350, margin=dict(t=40, b=20),
        )
        col.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("##### Delta Rata-rata: Crisis vs Aman")
    m0 = df[df["Cluster"] == 0][FEATURE_COLS].mean()
    m2 = df[df["Cluster"] == 2][FEATURE_COLS].mean()
    delta = (m0 - m2).reset_index()
    delta.columns = ["Fitur", "Delta"]
    delta["Fitur"] = delta["Fitur"].map(PRETTY)
    delta["Arah"] = delta["Delta"].apply(lambda x: "🔺 Crisis lebih tinggi" if x > 0 else "🔻 Aman lebih tinggi")
    delta["Delta %"] = delta["Delta"].apply(lambda x: f"{x*100:+.2f}%")
    st.dataframe(delta.sort_values("Delta", key=abs, ascending=False)[["Fitur", "Delta %", "Arah"]],
                 use_container_width=True, hide_index=True)

with tab6:
    pivot = df_f.groupby("Cluster")[FEATURE_COLS].mean()
    pivot.index = [CLUSTER_NAMES[i] for i in pivot.index]
    pivot.columns = [PRETTY[c] for c in FEATURE_COLS]

    fig_heat = px.imshow(
        pivot, text_auto=".1%", aspect="auto",
        color_continuous_scale="RdYlGn",
        labels=dict(color="Rasio"),
    )
    fig_heat.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font_color="#374151",
        xaxis=dict(tickangle=-30),
        coloraxis_colorbar=dict(tickformat=".0%", title=""),
        height=250, margin=dict(t=20, b=80),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#d1d5db; font-size:0.78rem'>
Financial Health Clustering Dashboard · Data Science Project · Streamlit + Plotly
</p>
""", unsafe_allow_html=True)
