import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Hava Durumu Analizi", layout="wide")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Lütfen önce giriş yapın.")
    st.stop()

st.title("🏗️ Şantiye Meteorolojik Analiz & Tahmin")

# Şantiye Koordinatları
LAT = 41.0082  
LON = 28.9784

tabs = st.tabs(["📊 Geçmiş Kayıtlar", "🔮 7 Günlük Tahmin", "📅 14 Günlük Projeksiyon"])

# --- RENKLENDİRME FONKSİYONLARI ---
def stil_uygula(row):
    """Satırları risk durumuna göre renklendirir."""
    # Yağış 5mm üstü veya Rüzgar 45km/s üstü KIRMIZI (Riskli)
    if row['Yagis_mm'] > 5 or row['Ruzgar_kms'] > 45:
        return ['background-color: #ffcccc'] * len(row)
    # Yağış 0.5mm altı ve Rüzgar 30km/s altı YEŞİL (Güvenli)
    elif row['Yagis_mm'] < 0.5 and row['Ruzgar_kms'] < 30:
        return ['background-color: #c8e6c9'] * len(row)
    return [''] * len(row)

def stil_uygula_tahmin(row):
    """Tahmin tabloları için renklendirme."""
    if row['Yağış (%)'] > 70 or row['Rüzgar (km/s)'] > 45:
        return ['background-color: #ffcccc'] * len(row)
    elif row['Yağış (%)'] < 20 and row['Rüzgar (km/s)'] < 30:
        return ['background-color: #c8e6c9'] * len(row)
    return [''] * len(row)

# --- TAB 1: GEÇMİŞ KAYITLAR ---
with tabs[0]:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.subheader("Filtreler")
        baslangic = st.date_input("Başlangıç", datetime.now() - timedelta(days=14), key="p_s")
        bitis = st.date_input("Bitiş", datetime.now() - timedelta(days=1), key="p_e")
        yagis_filtresi = st.checkbox("Sadece Yağmurlu Günler")

    if st.button("Geçmiş Verileri Getir", type="primary"):
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={LAT}&longitude={LON}&start_date={baslangic}&end_date={bitis}&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max&timezone=auto"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()['daily']
            df_past = pd.DataFrame({
                "Tarih": data['time'],
                "Max_Isi": data['temperature_2m_max'],
                "Yagis_mm": data['precipitation_sum'],
                "Ruzgar_kms": data['windspeed_10m_max']
            })
            if yagis_filtresi: df_past = df_past[df_past["Yagis_mm"] > 0]
            
            with col2:
                st.dataframe(df_past.style.apply(stil_uygula, axis=1), use_container_width=True)
                st.bar_chart(df_past.set_index("Tarih")["Yagis_mm"])

# --- TAB 2: 7 GÜNLÜK TAHMİN ---
with tabs[1]:
    t_url_7 = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,precipitation_probability_max,precipitation_sum,windspeed_10m_max&timezone=auto&forecast_days=7"
    t_res_7 = requests.get(t_url_7)
    if t_res_7.status_code == 200:
        d7 = t_res_7.json()['daily']
        df_7 = pd.DataFrame({
            "Tarih": d7['time'], "Isı (°C)": d7['temperature_2m_max'], 
            "Yağış (%)": d7['precipitation_probability_max'], "Yağış (mm)": d7['precipitation_sum'], 
            "Rüzgar (km/s)": d7['windspeed_10m_max']
        })
        st.dataframe(df_7.style.apply(stil_uygula_tahmin, axis=1), use_container_width=True)

# --- TAB 3: 14 GÜNLÜK PROJEKSİYON ---
with tabs[2]:
    t_url_14 = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,precipitation_probability_max,precipitation_sum,windspeed_10m_max&timezone=auto&forecast_days=14"
    t_res_14 = requests.get(t_url_14)
    if t_res_14.status_code == 200:
        d14 = t_res_14.json()['daily']
        df_14 = pd.DataFrame({
            "Tarih": d14['time'], "Isı (°C)": d14['temperature_2m_max'], 
            "Yağış (%)": d14['precipitation_probability_max'], "Yağış (mm)": d14['precipitation_sum'], 
            "Rüzgar (km/s)": d14['windspeed_10m_max']
        })
        st.dataframe(df_14.style.apply(stil_uygula_tahmin, axis=1), use_container_width=True)
        st.line_chart(df_14.set_index("Tarih")[["Yağış (%)", "Rüzgar (km/s)"]])