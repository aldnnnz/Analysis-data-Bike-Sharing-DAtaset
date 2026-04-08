import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Bike Rental Analysis Dashboard",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set style
sns.set_theme(style="darkgrid")
plt.style.use('seaborn-v0_8-darkgrid')

# Load data
@st.cache_data
def load_data():
    day_df = pd.read_csv("data/day.csv")
    hour_df = pd.read_csv("data/hour.csv")
    
    # Convert date columns
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Rename cnt to total_count
    day_df.rename(columns={'cnt': 'total_count'}, inplace=True)
    hour_df.rename(columns={'cnt': 'total_count'}, inplace=True)
    
    return day_df, hour_df

day_df, hour_df = load_data()

# Sidebar
st.sidebar.title("🚴 Bike Rental Dashboard")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["📊 Overview", 
     "⏰ Analisis Pola Waktu",
     "🌤️ Analisis Pengaruh Cuaca",
     "👥 Analisis User Casual vs Registered"]
)

# Helper functions
def create_season_label(season_num):
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    return season_map.get(season_num, str(season_num))

def create_weather_label(weather_num):
    weather_map = {
        1: 'Clear',
        2: 'Mist/Cloudy',
        3: 'Light Rain/Snow',
        4: 'Heavy Rain/Snow'
    }
    return weather_map.get(weather_num, str(weather_num))

# PAGE 1: OVERVIEW
if menu == "📊 Overview":
    st.title("📊 Bike Rental Analysis Dashboard")
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_rentals = day_df['total_count'].sum()
        st.metric("Total Penyewaan", f"{total_rentals:,}")
    
    with col2:
        avg_daily = day_df['total_count'].mean()
        st.metric("Rata-rata per Hari", f"{avg_daily:,.0f}")
    
    with col3:
        max_rentals = day_df['total_count'].max()
        st.metric("Penyewaan Tertinggi", f"{max_rentals:,}")
    
    with col4:
        min_rentals = day_df['total_count'].min()
        st.metric("Penyewaan Terendah", f"{min_rentals:,}")
    
    st.markdown("---")
    
    # Main trend visualization
    st.subheader("📈 Tren Penyewaan Sepeda (Harian)")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(day_df['dteday'], day_df['total_count'], linewidth=2, color='#1f77b4')
    ax.fill_between(day_df['dteday'], day_df['total_count'], alpha=0.3, color='#1f77b4')
    ax.set_title("Tren Penyewaan Sepeda Setiap Hari", fontsize=14, fontweight='bold')
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah Penyewaan")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    
    # Statistical summary
    st.subheader("📊 Ringkasan Statistik")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Statistik Penyewaan Harian:**")
        stats = {
            'Minimum': day_df['total_count'].min(),
            'Q1 (25%)': day_df['total_count'].quantile(0.25),
            'Median': day_df['total_count'].median(),
            'Q3 (75%)': day_df['total_count'].quantile(0.75),
            'Maximum': day_df['total_count'].max(),
            'Mean': day_df['total_count'].mean(),
            'Std Dev': day_df['total_count'].std()
        }
        stats_df = pd.DataFrame(list(stats.items()), columns=['Statistik', 'Nilai'])
        st.dataframe(stats_df, use_container_width=True)
    
    with col2:
        # Distribution plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(day_df['total_count'], bins=30, color='#2ca02c', alpha=0.7, edgecolor='black')
        ax.axvline(day_df['total_count'].mean(), color='red', linestyle='--', linewidth=2, label='Mean')
        ax.axvline(day_df['total_count'].median(), color='orange', linestyle='--', linewidth=2, label='Median')
        ax.set_title("Distribusi Jumlah Penyewaan", fontsize=12, fontweight='bold')
        ax.set_xlabel("Jumlah Penyewaan")
        ax.set_ylabel("Frekuensi")
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)


# PAGE 2: ANALISIS POLA WAKTU
elif menu == "⏰ Analisis Pola Waktu":
    st.title("⏰ Analisis Pola Jumlah Penyewaan Berdasarkan Waktu")
    st.markdown("---")
    
    # Pertanyaan bisnis
    st.markdown("""
    **Pertanyaan Bisnis:**
    Bagaimana pola jumlah penyewaan sepeda berdasarkan waktu (jam, hari kerja vs akhir pekan, dan musim)?
    """)
    st.markdown("---")
    
    # Tab untuk berbagai analisis waktu
    tab1, tab2, tab3 = st.tabs(["⏱️ Per Jam", "📅 Hari Kerja vs Akhir Pekan", "🍂 Per Musim"])
    
    # Tab 1: Per Jam
    with tab1:
        st.subheader("Rata-rata Penyewaan per Jam")
        
        hourly_pattern = hour_df.groupby('hr')['total_count'].mean().reset_index()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.plot(hourly_pattern['hr'], hourly_pattern['total_count'], 
                   marker='o', linewidth=2, markersize=6, color='#ff7f0e')
            ax.fill_between(hourly_pattern['hr'], hourly_pattern['total_count'], 
                           alpha=0.3, color='#ff7f0e')
            ax.set_title("Pola Penyewaan Sepeda per Jam", fontsize=14, fontweight='bold')
            ax.set_xlabel("Jam dalam Sehari (00:00 - 23:00)")
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Insight:**")
            peak_hour = hourly_pattern.loc[hourly_pattern['total_count'].idxmax()]
            low_hour = hourly_pattern.loc[hourly_pattern['total_count'].idxmin()]
            st.metric("Jam Puncak", f"{int(peak_hour['hr']):02d}:00")
            st.metric("Jam Terendah", f"{int(low_hour['hr']):02d}:00")
            st.write(f"**Rata-rata Puncak:** {peak_hour['total_count']:.0f} penyewaan")
            st.write(f"**Rata-rata Terendah:** {low_hour['total_count']:.0f} penyewaan")
    
    # Tab 2: Hari Kerja vs Akhir Pekan
    with tab2:
        st.subheader("Perbandingan Hari Kerja vs Akhir Pekan/Libur")
        
        workday_pattern = hour_df.groupby('workingday')['total_count'].mean().reset_index()
        workday_pattern['day_type'] = workday_pattern['workingday'].map({0: 'Akhir Pekan/Libur', 1: 'Hari Kerja'})
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#d62728', '#2ca02c']
            bars = ax.bar(workday_pattern['day_type'], workday_pattern['total_count'], 
                         color=colors, alpha=0.7, edgecolor='black', linewidth=2)
            ax.set_title("Rata-rata Penyewaan: Hari Kerja vs Akhir Pekan", fontsize=14, fontweight='bold')
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Insight:**")
            working_day_avg = workday_pattern[workday_pattern['day_type'] == 'Hari Kerja']['total_count'].values[0]
            weekend_avg = workday_pattern[workday_pattern['day_type'] == 'Akhir Pekan/Libur']['total_count'].values[0]
            difference = ((working_day_avg - weekend_avg) / weekend_avg) * 100
            
            st.metric("Rata-rata Hari Kerja", f"{working_day_avg:.0f}")
            st.metric("Rata-rata Akhir Pekan", f"{weekend_avg:.0f}")
            st.metric("Perbedaan", f"+{difference:.1f}%")
    
    # Tab 3: Per Musim
    with tab3:
        st.subheader("Rata-rata Penyewaan per Musim")
        
        season_pattern = hour_df.groupby('season')['total_count'].mean().reset_index()
        season_pattern['season_name'] = season_pattern['season'].apply(create_season_label)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors_season = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            bars = ax.bar(season_pattern['season_name'], season_pattern['total_count'], 
                         color=colors_season, alpha=0.7, edgecolor='black', linewidth=2)
            ax.set_title("Rata-rata Penyewaan per Musim", fontsize=14, fontweight='bold')
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Insight:**")
            max_season = season_pattern.loc[season_pattern['total_count'].idxmax()]
            min_season = season_pattern.loc[season_pattern['total_count'].idxmin()]
            st.metric("Musim Tertinggi", max_season['season_name'])
            st.metric("Musim Terendah", min_season['season_name'])
            st.write(f"**Max:** {max_season['total_count']:.0f} penyewaan")
            st.write(f"**Min:** {min_season['total_count']:.0f} penyewaan")
    
    # Advanced: Jam per Hari Kerja vs Akhir Pekan
    st.markdown("---")
    st.subheader("📊 Detail: Pola Jam pada Hari Kerja vs Akhir Pekan")
    
    hourly_workday = hour_df.groupby(['workingday', 'hr'])['total_count'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    for workday in [0, 1]:
        data = hourly_workday[hourly_workday['workingday'] == workday]
        label = 'Hari Kerja' if workday == 1 else 'Akhir Pekan/Libur'
        ax.plot(data['hr'], data['total_count'], marker='o', linewidth=2, label=label)
    
    ax.set_title("Pola Penyewaan per Jam: Hari Kerja vs Akhir Pekan", fontsize=14, fontweight='bold')
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_ylabel("Rata-rata Jumlah Penyewaan")
    ax.set_xticks(range(0, 24, 2))
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)


# PAGE 3: ANALISIS PENGARUH CUACA
elif menu == "🌤️ Analisis Pengaruh Cuaca":
    st.title("🌤️ Analisis Pengaruh Kondisi Cuaca pada Penyewaan Sepeda")
    st.markdown("---")
    
    # Pertanyaan bisnis
    st.markdown("""
    **Pertanyaan Bisnis:**
    Bagaimana pengaruh kondisi cuaca (weathersit, suhu, kelembapan, dan kecepatan angin) terhadap jumlah penyewaan sepeda?
    """)
    st.markdown("---")
    
    # Tab untuk berbagai analisis cuaca
    tab1, tab2, tab3 = st.tabs(["☁️ Kondisi Cuaca", "🌡️ Faktor Cuaca", "📈 Korelasi"])
    
    # Tab 1: Kondisi Cuaca
    with tab1:
        st.subheader("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")
        
        weather_pattern = hour_df.groupby('weathersit')['total_count'].mean().reset_index()
        weather_pattern['weather_name'] = weather_pattern['weathersit'].apply(create_weather_label)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(12, 6))
            colors_weather = ['#2ca02c', '#ff7f0e', '#d62728', '#8b008b']
            bars = ax.bar(weather_pattern['weather_name'], weather_pattern['total_count'], 
                         color=colors_weather, alpha=0.7, edgecolor='black', linewidth=2)
            ax.set_title("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca", fontsize=14, fontweight='bold')
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=15, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Insight:**")
            best_weather = weather_pattern.loc[weather_pattern['total_count'].idxmax()]
            worst_weather = weather_pattern.loc[weather_pattern['total_count'].idxmin()]
            
            st.metric("Cuaca Terbaik", best_weather['weather_name'])
            st.metric("Cuaca Terburuk", worst_weather['weather_name'])
            st.write(f"**Terbaik:** {best_weather['total_count']:.0f} penyewaan")
            st.write(f"**Terburuk:** {worst_weather['total_count']:.0f} penyewaan")
            
            decline_pct = ((best_weather['total_count'] - worst_weather['total_count']) / best_weather['total_count']) * 100
            st.write(f"**Penurunan:** -{decline_pct:.1f}%")
    
    # Tab 2: Faktor Cuaca
    with tab2:
        st.subheader("Pengaruh Faktor Cuaca Individual")
        
        # Create bins for temperature, humidity, windspeed
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature analysis
            st.write("**Analisis Suhu**")
            hour_df['temp_range'] = pd.cut(hour_df['temp'], bins=5, labels=['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Sangat Hangat'])
            temp_analysis = hour_df.groupby('temp_range')['total_count'].mean()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            temp_analysis.plot(kind='bar', color='#ff7f0e', alpha=0.7, edgecolor='black', ax=ax)
            ax.set_title("Rata-rata Penyewaan Berdasarkan Suhu", fontweight='bold')
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            ax.set_xlabel("Kategori Suhu")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Humidity analysis
            st.write("**Analisis Kelembapan**")
            hour_df['humidity_range'] = pd.cut(hour_df['hum'], bins=4, labels=['Sangat Kering', 'Kering', 'Lembab', 'Sangat Lembab'])
            humidity_analysis = hour_df.groupby('humidity_range')['total_count'].mean()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            humidity_analysis.plot(kind='bar', color='#1f77b4', alpha=0.7, edgecolor='black', ax=ax)
            ax.set_title("Rata-rata Penyewaan Berdasarkan Kelembapan", fontweight='bold')
            ax.set_ylabel("Rata-rata Jumlah Penyewaan")
            ax.set_xlabel("Kategori Kelembapan")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
        
        # Windspeed analysis
        st.write("**Analisis Kecepatan Angin**")
        hour_df['windspeed_range'] = pd.cut(hour_df['windspeed'], bins=4, labels=['Sangat Tenang', 'Tenang', 'Sedang', 'Kencang'])
        windspeed_analysis = hour_df.groupby('windspeed_range')['total_count'].mean()
        
        fig, ax = plt.subplots(figsize=(12, 5))
        windspeed_analysis.plot(kind='bar', color='#2ca02c', alpha=0.7, edgecolor='black', ax=ax)
        ax.set_title("Rata-rata Penyewaan Berdasarkan Kecepatan Angin", fontweight='bold')
        ax.set_ylabel("Rata-rata Jumlah Penyewaan")
        ax.set_xlabel("Kategori Kecepatan Angin")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Tab 3: Korelasi
    with tab3:
        st.subheader("Korelasi Faktor Cuaca dengan Jumlah Penyewaan")
        
        weather_corr = hour_df[['temp', 'atemp', 'hum', 'windspeed', 'total_count']].corr()
        corr_values = weather_corr['total_count'].sort_values(ascending=False)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            corr_values_plot = corr_values.drop('total_count')
            colors_corr = ['#2ca02c' if x > 0 else '#d62728' for x in corr_values_plot.values]
            bars = ax.barh(range(len(corr_values_plot)), corr_values_plot.values, color=colors_corr, alpha=0.7, edgecolor='black')
            ax.set_yticks(range(len(corr_values_plot)))
            ax.set_yticklabels(['Suhu Aktual', 'Suhu', 'Kelembapan', 'Kecepatan Angin'])
            ax.set_title("Korelasi Faktor Cuaca dengan Jumlah Penyewaan", fontsize=14, fontweight='bold')
            ax.set_xlabel("Nilai Korelasi")
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{width:.3f}',
                       ha='left' if width > 0 else 'right', va='center', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Interpretasi Korelasi:**")
            st.write("""
            - **Positif (+):** Semakin tinggi nilai, semakin meningkat penyewaan
            - **Negatif (-):** Semakin tinggi nilai, semakin menurun penyewaan
            - **Kuat:** |korelasi| > 0.5
            - **Sedang:** 0.3 < |korelasi| ≤ 0.5
            - **Lemah:** |korelasi| ≤ 0.3
            """)
            
            st.write("**Temuan Utama:**")
            for idx, (var, corr) in enumerate(corr_values_plot.items()):
                st.write(f"{idx+1}. {['Suhu Aktual', 'Suhu', 'Kelembapan', 'Kecepatan Angin'][idx]}: {corr:.3f}")


# PAGE 4: ANALISIS USER CASUAL VS REGISTERED
elif menu == "👥 Analisis User Casual vs Registered":
    st.title("👥 Analisis Pengguna Casual vs Registered")
    st.markdown("---")
    
    # Tab untuk berbagai analisis user
    tab1, tab2, tab3 = st.tabs(["⏱️ Per Jam", "🍂 Per Musim", "📊 Perbandingan"])
    
    # Tab 1: Per Jam
    with tab1:
        st.subheader("Perbandingan User Casual vs Registered per Jam")
        
        hourly_user = hour_df.groupby('hr')[['casual', 'registered', 'total_count']].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(hourly_user['hr'], hourly_user['casual'], marker='o', linewidth=2, 
               markersize=6, label='Casual Users', color='#ff7f0e')
        ax.plot(hourly_user['hr'], hourly_user['registered'], marker='s', linewidth=2, 
               markersize=6, label='Registered Users', color='#1f77b4')
        
        ax.set_title("Rata-rata Penyewaan Casual vs Registered per Jam", fontsize=14, fontweight='bold')
        ax.set_xlabel("Jam dalam Sehari")
        ax.set_ylabel("Rata-rata Jumlah Penyewaan")
        ax.set_xticks(range(0, 24, 2))
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rata-rata Casual per Jam", f"{hourly_user['casual'].mean():.0f}")
            st.metric("Peak Casual", f"{hourly_user['casual'].max():.0f}")
        with col2:
            st.metric("Rata-rata Registered per Jam", f"{hourly_user['registered'].mean():.0f}")
            st.metric("Peak Registered", f"{hourly_user['registered'].max():.0f}")
    
    # Tab 2: Per Musim
    with tab2:
        st.subheader("Perbandingan User Casual vs Registered per Musim")
        
        seasonal_user = hour_df.groupby('season')[['casual', 'registered', 'total_count']].mean().reset_index()
        seasonal_user['season_name'] = seasonal_user['season'].apply(create_season_label)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(seasonal_user))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, seasonal_user['casual'], width, label='Casual Users', 
                      color='#ff7f0e', alpha=0.7, edgecolor='black')
        bars2 = ax.bar(x + width/2, seasonal_user['registered'], width, label='Registered Users', 
                      color='#1f77b4', alpha=0.7, edgecolor='black')
        
        ax.set_title("Rata-rata Penyewaan Casual vs Registered per Musim", fontsize=14, fontweight='bold')
        ax.set_ylabel("Rata-rata Jumlah Penyewaan")
        ax.set_xticks(x)
        ax.set_xticklabels(seasonal_user['season_name'])
        ax.legend()
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # Tab 3: Perbandingan Proporsi
    with tab3:
        st.subheader("Proporsi Casual vs Registered")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall proportion
            total_casual = hour_df['casual'].sum()
            total_registered = hour_df['registered'].sum()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            sizes = [total_casual, total_registered]
            labels = ['Casual Users', 'Registered Users']
            colors = ['#ff7f0e', '#1f77b4']
            explode = (0.05, 0)
            
            ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                  shadow=True, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
            ax.set_title("Proporsi Total Penyewaan", fontsize=12, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.write("**Statistik Perbandingan:**")
            st.metric("Total Casual", f"{total_casual:,.0f}")
            st.metric("Total Registered", f"{total_registered:,.0f}")
            st.metric("Rasio Registered/Casual", f"{total_registered/total_casual:.2f}x")
            st.write(f"""
            **Insight:**
            - Pengguna terdaftar (registered) mendominasi dengan {(total_registered/(total_casual+total_registered))*100:.1f}% dari total penyewaan
            - Pengguna kasual (casual) hanya {(total_casual/(total_casual+total_registered))*100:.1f}% dari total penyewaan
            - Ini menunjukkan bahwa mayoritas pengguna adalah pelanggan reguler yang sudah terdaftar
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p style='color: gray; font-size: 12px;'>
        Dashboard Analisis Penyewaan Sepeda | Data: 2011-2012 | Muhammad Aldyn Ismail Putra
    </p>
</div>
""", unsafe_allow_html=True)
