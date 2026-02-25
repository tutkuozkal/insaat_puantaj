

import streamlit as st
import pandas as pd
from database import get_connection
import base64
from datetime import datetime
import requests

st.set_page_config(page_title="Saha Günlüğü", layout="wide")

# --- TABLO GARANTİLEME (Hafızadaki Standart) ---
def tabloyu_garantile():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.saha_gunlugu (
                id SERIAL PRIMARY KEY,
                tarih DATE NOT NULL,
                notlar TEXT NOT NULL,
                foto_url TEXT,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Sistem hazırlık hatası: {e}")

tabloyu_garantile()

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Lütfen giriş yapın.")
    st.stop()

def get_today_weather():
    LAT, LON = 41.0082, 28.9784 
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,precipitation_sum,windspeed_10m_max&timezone=auto&forecast_days=1"
    try:
        res = requests.get(url).json()
        d = res['daily']
        return f" (Hava: {d['temperature_2m_max'][0]}°C, Yağış: {d['precipitation_sum'][0]}mm, Rüzgar: {d['windspeed_10m_max'][0]}km/s)"
    except: return ""

st.title("📂 Saha Günlüğü Arşivi")
# Yeni sekme "🖼️ Fotoğraf Galerisi" olarak eklendi
tab1, tab2, tab3 = st.tabs(["📝 Yeni Kayıt", "🔍 Arşiv", "🖼️ Fotoğraf Galerisi"])

# --- TAB 1: YENİ KAYIT ---
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        tarih = st.date_input("Kayıt Tarihi", datetime.now())
        gunluk_not = st.text_area("Bugünkü Çalışma Notları", height=250)
    with col2:
        st.subheader("📸 Fotoğraf")
        img_file = st.file_uploader("Dosya Seç", type=['jpg', 'png', 'jpeg'])
        if img_file:
            st.image(img_file, caption="Yüklenecek Resim Önizlemesi", use_container_width=True)

    if st.button("💾 Günlüğü Kaydet", type="primary"):
        if gunluk_not:
            with st.spinner("Kaydediliyor..."):
                hava = get_today_weather()
                tam_not = f"{gunluk_not}\n\n[Meteoroloji: {hava}]"
                base64_image = base64.b64encode(img_file.getvalue()).decode() if img_file else ""
                
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO public.saha_gunlugu (tarih, notlar, foto_url) VALUES (%s, %s, %s)",
                        (tarih, tam_not, base64_image)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("✅ Kayıt başarıyla tamamlandı!")
                except Exception as e:
                    st.error(f"❌ Veritabanı Hatası: {e}")
        else:
            st.warning("Lütfen not alanını doldurun.")

# --- TAB 2: ARŞİV (Detaylı Notlar) ---
with tab2:
    try:
        query = "SELECT tarih, notlar, foto_url FROM public.saha_gunlugu ORDER BY tarih DESC"
        conn = get_connection()
        df_logs = pd.read_sql(query, conn)
        conn.close()
        for _, row in df_logs.iterrows():
            with st.expander(f"📅 {row['tarih']} Raporu"):
                st.info(row['notlar'])
                if row['foto_url']:
                    st.image(f"data:image/jpeg;base64,{row['foto_url']}", use_container_width=True)
    except:
        st.info("Kayıt bulunamadı.")

# --- TAB 3: FOTOĞRAF GALERİSİ (Yeni Bölüm) ---
with tab3:
    st.subheader("🖼️ Saha Fotoğrafları Galerisi")
    
    try:
        # Verileri çek
        conn = get_connection()
        df_gallery = pd.read_sql("SELECT tarih, foto_url FROM public.saha_gunlugu WHERE foto_url != '' ORDER BY tarih DESC", conn)
        conn.close()

        if not df_gallery.empty:
            # Filtreleme Seçenekleri
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                start_date = st.date_input("Başlangıç", df_gallery['tarih'].min())
            with col_f2:
                end_date = st.date_input("Bitiş", df_gallery['tarih'].max())

            # Filtreyi uygula
            mask = (df_gallery['tarih'] >= start_date) & (df_gallery['tarih'] <= end_date)
            df_filtered = df_gallery.loc[mask]

            # Galeri Görünümü
            if not df_filtered.empty:
                # Fotoğrafları 3'lü kolonlar halinde diz
                cols = st.columns(3)
                for i, row in enumerate(df_filtered.itertuples()):
                    with cols[i % 3]:
                        st.image(f"data:image/jpeg;base64,{row.foto_url}", caption=f"📅 {row.tarih}", use_container_width=True)
            else:
                st.warning("Seçili tarih aralığında fotoğraf bulunamadı.")
        else:
            st.info("Henüz fotoğraf içeren bir kayıt bulunmuyor.")
    except Exception as e:
        st.error(f"Galeri yüklenirken hata: {e}")