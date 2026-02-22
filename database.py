# import pandas as pd
# from sqlalchemy import create_engine
# from fpdf import FPDF
# import psycopg2

# # DİKKAT: 'BURAYA_SIFRENI_YAZ' kısmını PostgreSQL şifrenle değiştir!
# DB_PASSWORD = "admin"

# # 1. SQLAlchemy Engine (Veri okuma için)
# def get_engine():
#     return create_engine(f"postgresql+psycopg2://postgres:{DB_PASSWORD}@localhost:5432/insaat_puantaj")

# # 2. Psycopg2 Bağlantısı (Kayıt ekleme ve silme için)
# def get_connection():
#     return psycopg2.connect(
#         dbname="insaat_puantaj",
#         user="postgres",
#         password=DB_PASSWORD, 
#         host="localhost",
#         port="5432"
#     )

# def query_to_df(sql):
#     engine = get_engine()
#     with engine.connect() as conn:
#         df = pd.read_sql_query(sql, conn)
#     return df

# def tr_temizle(metin):
#     metin = str(metin)
#     duzeltmeler = {'İ':'I','ı':'i','Ş':'S','ş':'s','Ğ':'G','ğ':'g','Ç':'C','ç':'c','Ö':'O','ö':'o','Ü':'U','ü':'u'}
#     for k, h in duzeltmeler.items(): metin = metin.replace(k, h)
#     return metin

# def pdf_olustur(df, tarih_str):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Helvetica", size=12)
#     pdf.cell(0, 10, txt=tr_temizle("GUNLUK SANTIYE PUANTAJ RAPORU"), ln=True, align='C')
#     pdf.set_font("Helvetica", size=10)
#     pdf.cell(0, 10, txt=f"Rapor Tarihi: {tarih_str}", ln=True)
#     pdf.ln(5)
#     pdf.set_fill_color(200, 220, 255)
#     pdf.cell(40, 10, tr_temizle('Personel'), 1, 0, 'C', 1)
#     pdf.cell(40, 10, tr_temizle('Alan'), 1, 0, 'C', 1)
#     pdf.cell(20, 10, tr_temizle('Saat'), 1, 0, 'C', 1)
#     pdf.cell(30, 10, tr_temizle('Hava'), 1, 0, 'C', 1)
#     pdf.cell(60, 10, tr_temizle('Gecikme Nedeni'), 1, 1, 'C', 1)
#     pdf.set_font("Helvetica", size=9)
#     for _, row in df.iterrows():
#         pdf.cell(40, 10, tr_temizle(row.get('ad_soyad', '-')), 1)
#         pdf.cell(40, 10, tr_temizle(row.get('alan_adi', '-')), 1)
#         pdf.cell(20, 10, str(row.get('mesai_saati', '0')), 1, 0, 'C')
#         pdf.cell(30, 10, tr_temizle(row.get('hava_durumu', '-')), 1)
#         pdf.cell(60, 10, tr_temizle(row.get('gecikme_nedeni', '-'))[:25], 1, 1)
    
#     # bytearray hatasını çözen bytes dönüşümü
#     return bytes(pdf.output())

import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from fpdf import FPDF
import io

# --- 1. VERİTABANI BAĞLANTI AYARLARI ---
def get_connection():
    """Hem Streamlit Cloud hem de Yerel (Local) ortamda çalışan bağlantı fonksiyonu."""
    try:
        # 1. Öncelik: Streamlit Secrets (Bulut/Neon)
        return psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"],
            sslmode="require"
        )
    except Exception:
        # 2. Öncelik: Yerel Test (Buradaki bilgileri kendi yerel ayarlarınla değiştirebilirsin)
        return psycopg2.connect(
            host="localhost",
            database="insaat_puantaj",
            user="postgres",
            password="admin", # Yerelde kullandığın şifren
            port="5432"
        )

def get_engine():
    """SQLAlchemy Engine - pandas read_sql_query için."""
    try:
        # Bulut Ayarları
        s = st.secrets["postgres"]
        return create_engine(f"postgresql+psycopg2://{s['user']}:{s['password']}@{s['host']}:{s['port']}/{s['database']}?sslmode=require")
    except Exception:
        # Yerel Ayarlar
        return create_engine(f"postgresql+psycopg2://postgres:admin@localhost:5432/insaat_puantaj")

# --- 2. VERİ ÇEKME FONKSİYONU ---
def query_to_df(sql):
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        st.error(f"Sorgu hatası: {e}")
        return pd.DataFrame()

# --- 3. PDF YARDIMCI FONKSİYONLARI ---
def tr_temizle(metin):
    """Türkçe karakterleri PDF kütüphanesi için temizler."""
    metin = str(metin)
    duzeltmeler = {
        'İ':'I','ı':'i','Ş':'S','ş':'s','Ğ':'G','ğ':'g',
        'Ç':'C','ç':'c','Ö':'O','ö':'o','Ü':'U','ü':'u'
    }
    for k, h in duzeltmeler.items(): 
        metin = metin.replace(k, h)
    return metin

def pdf_olustur(df, tarih_str):
    """Filtrelenmiş veriden PDF raporu üretir."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12, style='B')
    
    # Başlık
    pdf.cell(0, 10, txt=tr_temizle("GUNLUK SANTIYE PUANTAJ RAPORU"), ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, txt=f"Rapor Tarihi: {tarih_str}", ln=True)
    pdf.ln(5)
    
    # Tablo Başlıkları
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(45, 10, tr_temizle('Personel'), 1, 0, 'C', 1)
    pdf.cell(40, 10, tr_temizle('Alan'), 1, 0, 'C', 1)
    pdf.cell(20, 10, tr_temizle('Saat'), 1, 0, 'C', 1)
    pdf.cell(30, 10, tr_temizle('Hava'), 1, 0, 'C', 1)
    pdf.cell(55, 10, tr_temizle('Gecikme/Not'), 1, 1, 'C', 1)
    
    # Veri Satırları
    pdf.set_font("Helvetica", size=9)
    for _, row in df.iterrows():
        pdf.cell(45, 10, tr_temizle(row.get('ad_soyad', '-')), 1)
        pdf.cell(40, 10, tr_temizle(row.get('alan_adi', '-')), 1)
        pdf.cell(20, 10, str(row.get('mesai_saati', '0')), 1, 0, 'C')
        pdf.cell(30, 10, tr_temizle(row.get('hava_durumu', '-')), 1)
        # Uzun notları kesmek için [:25]
        not_metni = tr_temizle(row.get('gecikme_nedeni', '-'))
        pdf.cell(55, 10, not_metni[:28], 1, 1)
    
    # Streamlit için bytes olarak çıktı ver
    return pdf.output(dest='S').encode('latin-1')

# npx neonctl@latest init neon bağlantı bilgileri: 
# postgresql://neondb_owner:npg_M8kfXNLQCyI3@ep-broad-grass-aijro8zd-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
# br-long-shadow-aiiuwmue ID
