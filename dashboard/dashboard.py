import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚲 Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05) !important;
    border-right: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] * { color: #e8e8f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label { color: #b0b0d0 !important; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(8px);
    transition: transform 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-label { color: #9999bb; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.metric-value { color: #ffffff; font-size: 2rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.metric-delta { font-size: 0.78rem; margin-top: 4px; }
.delta-up   { color: #56e39f; }
.delta-down { color: #ff6b6b; }

/* Section headers */
.section-header {
    color: #ffffff;
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    letter-spacing: -0.01em;
}
.section-sub {
    color: #8888aa;
    font-size: 0.78rem;
    margin-bottom: 16px;
}

/* Chart containers */
.chart-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(6px);
}

/* Divider */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Streamlit elements override */
[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)



@st.cache_data
def load_data():
    day_df  = pd.read_csv("data/day.csv")
    hour_df = pd.read_csv("data/hour.csv")

    for df in [day_df, hour_df]:
        df["dteday"] = pd.to_datetime(df["dteday"])
        df["season_label"]  = df["season"].map({1:"Spring",2:"Summer",3:"Fall",4:"Winter"})
        df["weather_label"] = df["weathersit"].map({
            1:"Clear / Few Clouds", 2:"Mist / Cloudy",
            3:"Light Snow / Rain",  4:"Heavy Rain / Ice"})
        df["weekday_label"] = df["weekday"].map(
            {0:"Sunday",1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday"})
        df["year"] = df["yr"].map({0:2011, 1:2012})
        df["month_name"] = df["dteday"].dt.strftime("%b")

    # clustering
    bins   = [0, 2000, 4000, 6000, day_df["cnt"].max()+1]
    labels = ["Rendah (<2k)", "Sedang (2–4k)", "Tinggi (4–6k)", "Sangat Tinggi (>6k)"]
    day_df["demand_cluster"] = pd.cut(day_df["cnt"], bins=bins, labels=labels)

    return day_df, hour_df

day_df, hour_df = load_data()

# ── Matplotlib Dark Theme ─────────────────────────────────────────────────────
DARK_BG   = "#1a1a2e"
CARD_BG   = "#16213e"
ACCENT1   = "#0f3460"
GRID_C    = "#2a2a4a"
TEXT_C    = "#c8c8e8"
PALETTE   = ["#56e39f","#7eb8f7","#f9c74f","#f4845f","#c77dff","#48cae4","#ff6b9d"]

plt.rcParams.update({
    "figure.facecolor":  DARK_BG,
    "axes.facecolor":    DARK_BG,
    "axes.edgecolor":    GRID_C,
    "axes.labelcolor":   TEXT_C,
    "axes.titlecolor":   TEXT_C,
    "xtick.color":       TEXT_C,
    "ytick.color":       TEXT_C,
    "grid.color":        GRID_C,
    "grid.linewidth":    0.6,
    "text.color":        TEXT_C,
    "legend.facecolor":  DARK_BG,
    "legend.edgecolor":  GRID_C,
    "legend.labelcolor": TEXT_C,
    "font.family":       "DejaVu Sans",
    "figure.dpi":        130,
})


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR FILTERS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🚲 Bike Sharing")
    st.markdown("**Dashboard Analisis Data**")
    st.markdown("---")

    st.markdown("### 🎛️ Filter Data")

    # Year
    years_avail = sorted(day_df["year"].unique().tolist())
    sel_years = st.multiselect("📅 Tahun", years_avail, default=years_avail)

    # Season
    seasons_avail = ["Spring","Summer","Fall","Winter"]
    sel_seasons = st.multiselect("🌸 Musim", seasons_avail, default=seasons_avail)

    # Weather
    weather_avail = day_df["weather_label"].unique().tolist()
    sel_weather = st.multiselect("🌤️ Kondisi Cuaca", weather_avail, default=weather_avail)

    # Date range
    min_d = day_df["dteday"].min().date()
    max_d = day_df["dteday"].max().date()
    date_range = st.date_input("📆 Rentang Tanggal", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    st.markdown("---")
    st.markdown("### 📊 Opsi Visualisasi")
    chart_type = st.radio("Tipe Chart Musim", ["Bar Chart","Box Plot"])
    show_reg   = st.checkbox("Tampilkan garis Registered", value=True)
    show_cas   = st.checkbox("Tampilkan garis Casual",     value=True)

    st.markdown("---")
    st.markdown("<span style='color:#9999bb;font-size:0.7rem'>Bike Sharing Dataset · UCI ML Repo</span>", unsafe_allow_html=True)


# ── Apply Filters ─────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_d, end_d = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_d, end_d = day_df["dteday"].min(), day_df["dteday"].max()

mask = (
    day_df["year"].isin(sel_years) &
    day_df["season_label"].isin(sel_seasons) &
    day_df["weather_label"].isin(sel_weather) &
    day_df["dteday"].between(start_d, end_d)
)
filtered_day  = day_df[mask].copy()

mask_hr = (
    hour_df["year"].isin(sel_years) &
    hour_df["season_label"].isin(sel_seasons) &
    hour_df["weather_label"].isin(sel_weather) &
    hour_df["dteday"].between(start_d, end_d)
)
filtered_hour = hour_df[mask_hr].copy()

if filtered_day.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter. Silakan ubah pilihan filter.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style='padding: 8px 0 24px 0'>
  <h1 style='color:#ffffff;font-size:2rem;font-weight:800;margin:0;letter-spacing:-0.02em'>
    🚲 Bike Sharing Analytics
  </h1>
  <p style='color:#8888aa;margin:4px 0 0 0;font-size:0.9rem'>
    Analisis interaktif pola penyewaan sepeda · 2011–2012
  </p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
total_cnt   = int(filtered_day["cnt"].sum())
avg_daily   = filtered_day["cnt"].mean()
total_days  = len(filtered_day)
peak_day    = filtered_day.loc[filtered_day["cnt"].idxmax(), "dteday"].strftime("%d %b %Y")
peak_val    = int(filtered_day["cnt"].max())
casual_pct  = filtered_day["casual"].sum() / filtered_day["cnt"].sum() * 100

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Total Penyewaan</div>
      <div class="metric-value">{total_cnt:,}</div>
      <div class="metric-delta delta-up">📅 {total_days} hari data</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Rata-rata Harian</div>
      <div class="metric-value">{avg_daily:,.0f}</div>
      <div class="metric-delta delta-up">sepeda / hari</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Puncak Tertinggi</div>
      <div class="metric-value">{peak_val:,}</div>
      <div class="metric-delta delta-up">🗓️ {peak_day}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Casual Riders</div>
      <div class="metric-value">{casual_pct:.1f}%</div>
      <div class="metric-delta delta-down">{100-casual_pct:.1f}% registered</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 1 — Tren Harian + Musim & Cuaca
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">📈 Pertanyaan 1 — Pengaruh Musim & Kondisi Cuaca</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Bagaimana musim dan cuaca memengaruhi total penyewaan sepeda harian?</p>', unsafe_allow_html=True)

colA, colB = st.columns([2, 1])

with colA:
    # Tren harian
    fig, ax = plt.subplots(figsize=(9, 3.6))
    fig.patch.set_facecolor(DARK_BG)

    monthly = filtered_day.groupby(["year","dteday"])["cnt"].sum().reset_index()
    for i, yr in enumerate(sorted(filtered_day["year"].unique())):
        sub = monthly[monthly["year"] == yr]
        ax.fill_between(sub["dteday"], sub["cnt"], alpha=0.15, color=PALETTE[i])
        ax.plot(sub["dteday"], sub["cnt"], color=PALETTE[i], lw=1.8, label=str(yr))

    if show_reg:
        for i, yr in enumerate(sorted(filtered_day["year"].unique())):
            sub = filtered_day[filtered_day["year"] == yr]
            ax.plot(sub["dteday"], sub["registered"], color=PALETTE[i], lw=0.8, alpha=0.5, linestyle="--")
    if show_cas:
        for i, yr in enumerate(sorted(filtered_day["year"].unique())):
            sub = filtered_day[filtered_day["year"] == yr]
            ax.plot(sub["dteday"], sub["casual"], color=PALETTE[i+2], lw=0.8, alpha=0.5, linestyle=":")

    ax.set_title("Tren Penyewaan Harian", fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Tanggal", fontsize=9)
    ax.set_ylabel("Jumlah Penyewaan", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(title="Tahun", fontsize=8, title_fontsize=8)
    ax.grid(axis="y", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with colB:
    # Musim chart — user pilihan
    season_avg = filtered_day.groupby("season_label")["cnt"].mean().reindex(
        ["Spring","Summer","Fall","Winter"]).dropna()

    fig, ax = plt.subplots(figsize=(4.5, 3.6))
    fig.patch.set_facecolor(DARK_BG)

    if chart_type == "Bar Chart":
        bars = ax.bar(season_avg.index, season_avg.values,
                      color=PALETTE[:len(season_avg)], edgecolor=DARK_BG, linewidth=1.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
                    f'{bar.get_height():,.0f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
        ax.set_ylim(0, season_avg.max() * 1.2)
        ax.set_ylabel("Rata-rata Penyewaan", fontsize=8)
    else:
        data_box = [filtered_day[filtered_day["season_label"]==s]["cnt"].values
                    for s in ["Spring","Summer","Fall","Winter"]
                    if s in filtered_day["season_label"].values]
        labels_box= [s for s in ["Spring","Summer","Fall","Winter"]
                     if s in filtered_day["season_label"].values]
        bp = ax.boxplot(data_box, labels=labels_box, patch_artist=True,
                        medianprops=dict(color="#f9c74f", linewidth=2),
                        flierprops=dict(marker='o', color='gray', alpha=0.4, markersize=3))
        for patch, color in zip(bp["boxes"], PALETTE):
            patch.set_facecolor(color); patch.set_alpha(0.6)
        ax.set_ylabel("Total Penyewaan", fontsize=8)

    ax.set_title("Per Musim", fontsize=10, fontweight="bold", pad=8)
    ax.tick_params(axis='x', labelsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Baris kedua: cuaca + share casual vs registered
colC, colD = st.columns(2)

with colC:
    weather_avg = filtered_day.groupby("weather_label")["cnt"].mean().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(DARK_BG)
    colors_w = [PALETTE[3], PALETTE[2], PALETTE[1], PALETTE[0]][:len(weather_avg)]
    bars = ax.barh(weather_avg.index, weather_avg.values, color=colors_w, edgecolor=DARK_BG, height=0.6)
    for bar in bars:
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f'{bar.get_width():,.0f}', va='center', fontsize=8, fontweight='bold')
    ax.set_title("Rata-rata Penyewaan per Kondisi Cuaca", fontsize=10, fontweight="bold", pad=8)
    ax.set_xlabel("Rata-rata Penyewaan / Hari", fontsize=8)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with colD:
    # Stacked bar: casual vs registered per musim
    s_grp = filtered_day.groupby("season_label")[["casual","registered"]].mean().reindex(
        ["Spring","Summer","Fall","Winter"]).dropna()
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    fig.patch.set_facecolor(DARK_BG)
    x = np.arange(len(s_grp))
    ax.bar(x, s_grp["casual"],     label="Casual",     color=PALETTE[3], alpha=0.85, edgecolor=DARK_BG)
    ax.bar(x, s_grp["registered"], label="Registered", color=PALETTE[1], alpha=0.85,
           bottom=s_grp["casual"], edgecolor=DARK_BG)
    ax.set_xticks(x); ax.set_xticklabels(s_grp.index, fontsize=8)
    ax.set_title("Casual vs Registered per Musim", fontsize=10, fontweight="bold", pad=8)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=8)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=8); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 2 — Pola Per Jam
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">⏰ Pertanyaan 2 — Pola Penyewaan Per Jam</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Perbedaan pola jam-jaman antara hari kerja vs hari libur/akhir pekan</p>', unsafe_allow_html=True)

colE, colF = st.columns([1.2, 1])

with colE:
    hourly_avg = filtered_hour.groupby(["hr","workingday"])["cnt"].mean().reset_index()
    working    = hourly_avg[hourly_avg["workingday"] == 1]
    nonworking = hourly_avg[hourly_avg["workingday"] == 0]

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    fig.patch.set_facecolor(DARK_BG)

    if not working.empty:
        ax.plot(working["hr"], working["cnt"], marker="o", markersize=4,
                color=PALETTE[1], lw=2.5, label="Hari Kerja")
        ax.fill_between(working["hr"], working["cnt"], alpha=0.12, color=PALETTE[1])
    if not nonworking.empty:
        ax.plot(nonworking["hr"], nonworking["cnt"], marker="s", markersize=4,
                color=PALETTE[3], lw=2.5, label="Hari Libur / Akhir Pekan")
        ax.fill_between(nonworking["hr"], nonworking["cnt"], alpha=0.12, color=PALETTE[3])

    ax.axvspan(7, 9,   alpha=0.10, color=PALETTE[1], label="Rush Morning")
    ax.axvspan(16, 19, alpha=0.10, color=PALETTE[0], label="Rush Evening")
    ax.set_title("Rata-rata Penyewaan per Jam", fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Jam (0–23)", fontsize=9)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=9)
    ax.set_xticks(range(0, 24, 2))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with colF:
    # Heatmap hari vs jam
    heatmap_data = filtered_hour.groupby(["weekday_label","hr"])["cnt"].mean().unstack(fill_value=0)
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

    fig, ax = plt.subplots(figsize=(6, 3.6))
    fig.patch.set_facecolor(DARK_BG)
    sns.heatmap(heatmap_data, ax=ax, cmap="YlOrRd",
                cbar_kws={"label":"Avg Penyewaan", "shrink":0.8},
                xticklabels=2, linewidths=0.2, linecolor=DARK_BG)
    ax.set_title("Heatmap: Hari × Jam", fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Jam", fontsize=9)
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=7.5)
    ax.tick_params(axis="y", labelsize=7.5)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Jam terpopuler tabel
colG, colH = st.columns(2)

with colG:
    st.markdown("**🏆 Top 5 Jam Paling Ramai (Hari Kerja)**")
    if not filtered_hour[filtered_hour["workingday"]==1].empty:
        top_work = (filtered_hour[filtered_hour["workingday"]==1]
                    .groupby("hr")["cnt"].mean()
                    .sort_values(ascending=False).head(5)
                    .reset_index())
        top_work.columns = ["Jam", "Rata-rata Penyewaan"]
        top_work["Jam"] = top_work["Jam"].apply(lambda x: f"{x:02d}:00")
        top_work["Rata-rata Penyewaan"] = top_work["Rata-rata Penyewaan"].round(1)
        st.dataframe(top_work, hide_index=True, use_container_width=True)

with colH:
    st.markdown("**🎉 Top 5 Jam Paling Ramai (Hari Libur)**")
    if not filtered_hour[filtered_hour["workingday"]==0].empty:
        top_off = (filtered_hour[filtered_hour["workingday"]==0]
                   .groupby("hr")["cnt"].mean()
                   .sort_values(ascending=False).head(5)
                   .reset_index())
        top_off.columns = ["Jam", "Rata-rata Penyewaan"]
        top_off["Jam"] = top_off["Jam"].apply(lambda x: f"{x:02d}:00")
        top_off["Rata-rata Penyewaan"] = top_off["Rata-rata Penyewaan"].round(1)
        st.dataframe(top_off, hide_index=True, use_container_width=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 3 — Analisis Lanjutan: Clustering
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🔬 Analisis Lanjutan — Clustering Permintaan</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Segmentasi hari berdasarkan tingkat permintaan penyewaan</p>', unsafe_allow_html=True)

colI, colJ = st.columns(2)

with colI:
    # Pie chart distribusi cluster
    cluster_dist = filtered_day["demand_cluster"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(5, 3.8))
    fig.patch.set_facecolor(DARK_BG)
    wedges, texts, autotexts = ax.pie(
        cluster_dist.values,
        labels=cluster_dist.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(cluster_dist)],
        startangle=140,
        wedgeprops={"edgecolor": DARK_BG, "linewidth": 2}
    )
    for t in texts:      t.set_fontsize(8);  t.set_color(TEXT_C)
    for t in autotexts:  t.set_fontsize(8.5); t.set_color("#ffffff"); t.set_fontweight("bold")
    ax.set_title("Distribusi Cluster Permintaan", fontsize=11, fontweight="bold", pad=8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with colJ:
    # Stacked bar per musim
    sc = filtered_day.groupby(["season_label","demand_cluster"], observed=True).size().unstack(fill_value=0)
    sc = sc.reindex([s for s in ["Spring","Summer","Fall","Winter"] if s in sc.index])

    fig, ax = plt.subplots(figsize=(5.5, 3.8))
    fig.patch.set_facecolor(DARK_BG)
    sc.plot(kind="bar", stacked=True, ax=ax,
            color=PALETTE[:sc.shape[1]], edgecolor=DARK_BG, linewidth=0.8)
    ax.set_title("Komposisi Cluster per Musim", fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("Musim", fontsize=9)
    ax.set_ylabel("Jumlah Hari", fontsize=9)
    ax.tick_params(axis="x", rotation=0, labelsize=9)
    ax.legend(title="Cluster", bbox_to_anchor=(1.01,1), loc="upper left", fontsize=7.5, title_fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# Tabel profil cluster
st.markdown("**📋 Profil Tiap Cluster**")
cluster_profile = filtered_day.groupby("demand_cluster", observed=True).agg(
    Jumlah_Hari    = ("cnt", "count"),
    Rata_Penyewaan = ("cnt", "mean"),
    Rata_Suhu      = ("temp", lambda x: round(x.mean() * 41, 1)),   # denormalize °C
    Rata_Kelembaban= ("hum", lambda x: round(x.mean() * 100, 1)),   # denormalize %
    Rata_Windspeed = ("windspeed", lambda x: round(x.mean() * 67, 1))
).reset_index()
cluster_profile.columns = ["Cluster","Jumlah Hari","Rata-rata Penyewaan","Suhu (°C)","Kelembaban (%)","Kecepatan Angin (km/h)"]
cluster_profile["Rata-rata Penyewaan"] = cluster_profile["Rata-rata Penyewaan"].round(0).astype(int)
st.dataframe(cluster_profile, hide_index=True, use_container_width=True)

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW 4 — Data Explorer
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("🗃️ Lihat Raw Data (filtered)", expanded=False):
    col_show = ["dteday","season_label","weather_label","weekday_label","year",
                "casual","registered","cnt","demand_cluster"]
    st.dataframe(filtered_day[col_show].rename(columns={
        "dteday":"Tanggal","season_label":"Musim","weather_label":"Cuaca",
        "weekday_label":"Hari","year":"Tahun","casual":"Casual",
        "registered":"Registered","cnt":"Total","demand_cluster":"Cluster"
    }), use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        data=filtered_day[col_show].to_csv(index=False).encode("utf-8"),
        file_name="filtered_bike_sharing.csv",
        mime="text/csv"
    )

# Footer
st.markdown("""
<div style='text-align:center;color:#555577;font-size:0.75rem;padding:20px 0 8px 0'>
  Bike Sharing Dashboard · Dataset: Capital Bikeshare Washington D.C. (2011–2012)
</div>
""", unsafe_allow_html=True)