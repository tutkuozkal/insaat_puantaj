import streamlit as st
from database import query_to_df
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime


# Her sayfanın (pages içindeki dosyaların) en başına eklenecek kontrol:

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Bu sayfayı görüntülemek için lütfen ana sayfadan giriş yapın.")
    st.stop() # Sayfanın geri kalanının yüklenmesini durdurur


# Sayfa Genel Ayarları
st.set_page_config(page_title="Raporlama ve Analiz", layout="wide")
st.title("📊 Şantiye Raporlama ve İlerleme Analizi")

# --- 1. VERİ ÇEKME ---
query = """
    SELECT 
        p.ad_soyad, 
        s.sirket_adi as sirket, 
        a.alan_adi, 
        pk.tarih, 
        pk.mesai_saati, 
        pk.aciklama as brans 
    FROM puantaj_kayitlari pk 
    JOIN personeller p ON pk.personel_id = p.id 
    LEFT JOIN sirketler s ON p.sirket_id = s.id 
    JOIN alanlar a ON pk.alan_id = a.id 
    ORDER BY pk.tarih ASC
"""
df = query_to_df(query)

if df.empty:
    st.info("📊 Henüz raporlanacak veri bulunmuyor. Lütfen puantaj girişi yapın.")
else:
    # Tarih dönüşümü
    df['tarih'] = pd.to_datetime(df['tarih'])
    
    # --- 2. SIDEBAR FİLTRELEME ---
    st.sidebar.header("🔍 Rapor Filtreleri")
    
    # A. TARİH SEÇİMİ (BAŞLANGIÇ VE BİTİŞ AYRI)
    st.sidebar.subheader("📅 Tarih Aralığı")
    min_db_date = df['tarih'].min().date()
    max_db_date = df['tarih'].max().date()
    
    col_start, col_end = st.sidebar.columns(2)
    with col_start:
        start_date = st.date_input("Başlangıç", value=min_db_date, min_value=min_db_date, max_value=max_db_date)
    with col_end:
        end_date = st.date_input("Bitiş", value=max_db_date, min_value=min_db_date, max_value=max_db_date)
    
    if start_date > end_date:
        st.sidebar.error("Hata: Başlangıç tarihi bitişten büyük olamaz.")

    # B. Şirket ve Branş Seçimi
    st.sidebar.subheader("🏢 Filtreler")
    sirket_list = ["Tümü"] + sorted(df['sirket'].dropna().unique().tolist())
    secilen_sirket = st.sidebar.selectbox("Şirket Seçin", sirket_list)
    
    brans_list = ["Tümü"] + sorted(df['brans'].unique().tolist())
    secilen_brans = st.sidebar.selectbox("Branş Seçin", brans_list)

    # --- 3. VERİ FİLTRELEME MANTIĞI ---
    filtered_df = df.copy()
    
    # Tarih Filtresi (Ayrı alanlardan gelen veriye göre)
    filtered_df = filtered_df[
        (filtered_df['tarih'].dt.date >= start_date) & 
        (filtered_df['tarih'].dt.date <= end_date)
    ]
    
    # Şirket Filtresi
    if secilen_sirket != "Tümü":
        filtered_df = filtered_df[filtered_df['sirket'] == secilen_sirket]
        
    # Branş Filtresi
    if secilen_brans != "Tümü":
        filtered_df = filtered_df[filtered_df['brans'] == secilen_brans]

    # --- 4. ÖZET METRİKLER (Filtreye ve Branşa Duyarlı) ---
    if filtered_df.empty:
        st.warning("⚠️ Seçilen kriterlere uygun veri bulunamadı.")
    else:
        # Metrikleri hesapla
        total_saat = filtered_df['mesai_saati'].sum()
        total_kisi = filtered_df['ad_soyad'].nunique()
        total_kayit = len(filtered_df)
        
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric("Toplam Efor", f"{total_saat:,.1f} Saat")
        with m2:
            st.metric("Toplam Kişi Sayısı", f"{total_kisi} Kişi")
        with m3:
            st.metric("Toplam Kayıt Sayısı", f"{total_kayit} Adet")
        with m4:
            st.info(f"**Seçili Branş:** {secilen_brans}")

        st.divider()

        # --- 5. GRAFİKLER ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🏢 Şirket Dağılımı (Saat)")
            s_ozet = filtered_df.groupby('sirket')['mesai_saati'].sum().reset_index()
            fig_pie = px.pie(s_ozet, values='mesai_saati', names='sirket', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.subheader("🛠️ Branş Dağılımı (Saat)")
            b_ozet = filtered_df.groupby('brans')['mesai_saati'].sum().reset_index()
            fig_bar = px.bar(b_ozet, x='brans', y='mesai_saati', color='brans',
                            text_auto='.1f')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # --- 6. S-CURVE (KÜMÜLATİF İLERLEME) ---
        st.subheader("📈 Tarihsel İlerleme Analizi (S-Curve)")
        daily = filtered_df.groupby('tarih')['mesai_saati'].sum().reset_index()
        daily['kumulatif'] = daily['mesai_saati'].cumsum()

        fig_s = make_subplots(specs=[[{"secondary_y": True}]])
        fig_s.add_trace(go.Bar(x=daily['tarih'], y=daily['mesai_saati'], 
                               name="Günlük Efor", marker_color='rgba(50, 171, 96, 0.6)'), secondary_y=False)
        fig_s.add_trace(go.Scatter(x=daily['tarih'], y=daily['kumulatif'], 
                                   name="Kümülatif Toplam", line=dict(color='firebrick', width=4)), secondary_y=True)
        
        fig_s.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_s, use_container_width=True)

        # --- 7. DETAYLI VERİ TABLOSU ---
        st.subheader("📋 Detaylı Rapor Listesi")
        display_df = filtered_df[['tarih', 'ad_soyad', 'sirket', 'brans', 'alan_adi', 'mesai_saati']].copy()
        display_df['tarih'] = display_df['tarih'].dt.date
        st.dataframe(display_df, use_container_width=True)