# import streamlit as st
# import pandas as pd
# from database import get_connection
# import base64
# from datetime import datetime

# st.set_page_config(page_title="Malzeme ve Stok Takibi", layout="wide")

# # --- TABLO GARANTİLEME (Altın Format + Dinamik Havuzlar) ---
# def tabloyu_garantile():
#     try:
#         conn = get_connection()
#         cur = conn.cursor()
#         # 1. Malzeme Havuzu (Unique)
#         cur.execute("CREATE TABLE IF NOT EXISTS public.havuz_malzeme (id SERIAL PRIMARY KEY, ad TEXT UNIQUE NOT NULL);")
#         # 2. Birim Havuzu (Unique)
#         cur.execute("CREATE TABLE IF NOT EXISTS public.havuz_birim (id SERIAL PRIMARY KEY, ad TEXT UNIQUE NOT NULL);")
#         # 3. Stok Kayıtları
#         cur.execute("""
#             CREATE TABLE IF NOT EXISTS public.stok_kayitlari (
#                 id SERIAL PRIMARY KEY,
#                 tarih DATE NOT NULL,
#                 malzeme_adi TEXT NOT NULL,
#                 miktar FLOAT NOT NULL,
#                 birim TEXT NOT NULL,
#                 tedarikci TEXT,
#                 irsaliye_foto TEXT,
#                 kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#         """)
#         conn.commit()
#         cur.close()
#         conn.close()
#     except Exception as e:
#         st.error(f"Sistem hazırlık hatası: {e}")

# tabloyu_garantile()

# if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#     st.warning("Lütfen giriş yapın.")
#     st.stop()

# st.title("📦 Malzeme ve Stok Yönetimi")

# tab1, tab2, tab3, tab4 = st.tabs(["📥 Malzeme Girişi", "📊 Stok Durumu", "📜 İrsaliye Arşivi", "⚙️ Malzeme/Birim Tanımları"])

# # --- TAB 4: MALZEME/BİRİM TANIMLARI (Yeni Bölüm) ---
# with tab4:
#     st.subheader("🛠️ Havuz Yönetimi")
#     col_h1, col_h2 = st.columns(2)
    
#     with col_h1:
#         st.markdown("### 🏗️ Malzeme Havuzu")
#         yeni_m = st.text_input("Yeni Malzeme Ekle", placeholder="Örn: C30 Beton")
#         if st.button("Malzemeyi Kaydet"):
#             if yeni_m:
#                 try:
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute("INSERT INTO public.havuz_malzeme (ad) VALUES (%s)", (yeni_m.strip(),))
#                     conn.commit()
#                     st.success(f"{yeni_m} eklendi.")
#                     st.rerun()
#                 except: st.error("Bu malzeme zaten mevcut!")
        
#         # Listeleme ve Silme
#         conn = get_connection()
#         m_listesi = pd.read_sql("SELECT * FROM public.havuz_malzeme ORDER BY ad", conn)
#         conn.close()
#         st.dataframe(m_listesi["ad"], use_container_width=True, hide_index=True)

#     with col_h2:
#         st.markdown("### 📏 Birim Havuzu")
#         yeni_b = st.text_input("Yeni Birim Ekle", placeholder="Örn: m³")
#         if st.button("Birimi Kaydet"):
#             if yeni_b:
#                 try:
#                     conn = get_connection()
#                     cur = conn.cursor()
#                     cur.execute("INSERT INTO public.havuz_birim (ad) VALUES (%s)", (yeni_b.strip(),))
#                     conn.commit()
#                     st.success(f"{yeni_b} eklendi.")
#                     st.rerun()
#                 except: st.error("Bu birim zaten mevcut!")

#         conn = get_connection()
#         b_listesi = pd.read_sql("SELECT * FROM public.havuz_birim ORDER BY ad", conn)
#         conn.close()
#         st.dataframe(b_listesi["ad"], use_container_width=True, hide_index=True)

# # --- HAVUZLARDAN VERİ ÇEKME ---
# conn = get_connection()
# malzeme_opsiyonlari = pd.read_sql("SELECT ad FROM public.havuz_malzeme ORDER BY ad", conn)["ad"].tolist()
# birim_opsiyonlari = pd.read_sql("SELECT ad FROM public.havuz_birim ORDER BY ad", conn)["ad"].tolist()
# conn.close()

# # --- TAB 1: YENİ MALZEME GİRİŞİ (Dinamik) ---
# with tab1:
#     if not malzeme_opsiyonlari:
#         st.info("Lütfen önce Tanımlamalar sekmesinden malzeme ekleyin.")
#     else:
#         col1, col2 = st.columns([2, 1])
#         with col1:
#             tarih = st.date_input("Teslim Tarihi", datetime.now())
#             malzeme_secimi = st.selectbox("Malzeme Seçin", malzeme_opsiyonlari)
#             col_m1, col_m2 = st.columns(2)
#             miktar = col_m1.number_input("Miktar", min_value=0.0)
#             birim_secimi = st.selectbox("Birim", birim_opsiyonlari)
#             tedarikci = st.text_input("Tedarikçi Firma / Plaka")
#         with col2:
#             st.subheader("📸 İrsaliye Görseli")
#             img_file = st.file_uploader("Dosya Seç", type=['jpg', 'png', 'jpeg'])
#             if img_file: st.image(img_file, use_container_width=True)

#         if st.button("📥 Stoğa İşle", type="primary"):
#             if miktar > 0:
#                 base64_image = base64.b64encode(img_file.getvalue()).decode() if img_file else ""
#                 conn = get_connection()
#                 cur = conn.cursor()
#                 cur.execute("INSERT INTO public.stok_kayitlari (tarih, malzeme_adi, miktar, birim, tedarikci, irsaliye_foto) VALUES (%s, %s, %s, %s, %s, %s)",
#                            (tarih, malzeme_secimi, miktar, birim_secimi, tedarikci, base64_image))
#                 conn.commit()
#                 st.success("Stok güncellendi!")
#                 st.rerun()

# # --- TAB 2 & 3 (Önceki Formatla Aynı Mantık) ---
# with tab2:
#     st.subheader("📊 Güncel Stok Durumu")
#     conn = get_connection()
#     df_stok = pd.read_sql("SELECT malzeme_adi, SUM(miktar) as toplam, birim FROM public.stok_kayitlari GROUP BY malzeme_adi, birim", conn)
#     conn.close()
#     st.dataframe(df_stok, use_container_width=True, hide_index=True)

# with tab3:
#     st.subheader("📜 İrsaliye Arşivi")
#     conn = get_connection()
#     df_arsiv = pd.read_sql("SELECT * FROM public.stok_kayitlari ORDER BY tarih DESC", conn)
#     conn.close()
#     for _, row in df_arsiv.iterrows():
#         with st.expander(f"📅 {row['tarih']} - {row['malzeme_adi']} ({row['miktar']} {row['birim']})"):
#             st.write(f"Tedarikçi: {row['tedarikci']}")
#             if row['irsaliye_foto']:
#                 st.image(f"data:image/jpeg;base64,{row['irsaliye_foto']}", use_container_width=True)

import streamlit as st
import pandas as pd
from database import get_connection
import base64
from datetime import datetime

st.set_page_config(page_title="Malzeme ve Stok Yönetimi", layout="wide")

# --- ALTIN FORMAT: OTOMATİK TABLO VE SÜTUN KONTROLÜ ---
def tabloyu_garantile():
    try:
        conn = get_connection()
        cur = conn.cursor()
        # 1. Havuz Tabloları
        cur.execute("CREATE TABLE IF NOT EXISTS public.havuz_malzeme (id SERIAL PRIMARY KEY, ad TEXT UNIQUE NOT NULL);")
        cur.execute("CREATE TABLE IF NOT EXISTS public.havuz_birim (id SERIAL PRIMARY KEY, ad TEXT UNIQUE NOT NULL);")
        
        # 2. Ana Stok Tablosu
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.stok_kayitlari (
                id SERIAL PRIMARY KEY,
                tarih DATE NOT NULL,
                malzeme_adi TEXT NOT NULL,
                miktar FLOAT NOT NULL,
                birim TEXT NOT NULL,
                tedarikci TEXT,
                irsaliye_foto TEXT,
                kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. Plaka Sütunu Kontrolü (Hata Giderici)
        cur.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='stok_kayitlari' AND column_name='plaka') THEN
                    ALTER TABLE public.stok_kayitlari ADD COLUMN plaka TEXT;
                END IF;
            END $$;
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

# --- VERİ ÇEKME ---
conn = get_connection()
malzeme_opsiyonlari = pd.read_sql("SELECT ad FROM public.havuz_malzeme ORDER BY ad", conn)["ad"].tolist()
birim_opsiyonlari = pd.read_sql("SELECT ad FROM public.havuz_birim ORDER BY ad", conn)["ad"].tolist()
conn.close()

st.title("📦 Malzeme ve Stok Yönetimi")
tab1, tab2, tab3, tab4 = st.tabs(["📥 Malzeme Girişi", "📊 Stok Durumu", "📜 İrsaliye Arşivi", "⚙️ Ayarlar"])

# --- TAB 1: MALZEME GİRİŞİ (Plaka Formatlı) ---
with tab1:
    if not malzeme_opsiyonlari:
        st.info("Lütfen Ayarlar sekmesinden malzeme ve birim ekleyin.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            tarih = st.date_input("Teslim Tarihi", datetime.now())
            malzeme_secimi = st.selectbox("Malzeme Seçin", malzeme_opsiyonlari)
            
            c_m1, c_m2 = st.columns(2)
            miktar = c_m1.number_input("Miktar", min_value=0.0)
            birim_secimi = c_m2.selectbox("Birim", birim_opsiyonlari)
            
            st.divider()
            tedarikci = st.text_input("Tedarikçi Firma Adı")
            
            p_tip = st.radio("Plaka Tipi", ["Standart (TR)", "Yabancı / Özel"], horizontal=True)
            if p_tip == "Standart (TR)":
                cp1, cp2, cp3 = st.columns([1, 1, 1])
                p_il = cp1.text_input("İl", max_chars=2, placeholder="34")
                p_hrf = cp2.text_input("Harf", max_chars=3, placeholder="FF").upper()
                p_no = cp3.text_input("Sayı", max_chars=4, placeholder="332")
                final_plaka = f"{p_il}-{p_hrf}-{p_no}" if p_il and p_hrf and p_no else ""
            else:
                final_plaka = st.text_input("Manuel Plaka")

        with col2:
            st.subheader("📸 İrsaliye")
            img_file = st.file_uploader("Dosya Seç", type=['jpg', 'png', 'jpeg'])
            if img_file: st.image(img_file, use_container_width=True)

        if st.button("📥 Stoğa İşle", type="primary"):
            if miktar > 0:
                base_img = base64.b64encode(img_file.getvalue()).decode() if img_file else ""
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO public.stok_kayitlari (tarih, malzeme_adi, miktar, birim, plaka, tedarikci, irsaliye_foto)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (tarih, malzeme_secimi, miktar, birim_secimi, final_plaka, tedarikci, base_img))
                    conn.commit()
                    st.success("✅ Kayıt başarılı!")
                    st.rerun()
                except Exception as e: st.error(f"Hata: {e}")

# --- TAB 2: STOK DURUMU ---
with tab2:
    st.subheader("📊 Güncel Stok Durumu")
    conn = get_connection()
    df_stok = pd.read_sql("SELECT malzeme_adi, SUM(miktar) as toplam, birim FROM public.stok_kayitlari GROUP BY malzeme_adi, birim", conn)
    conn.close()
    st.dataframe(df_stok, use_container_width=True, hide_index=True)

# --- TAB 3: ARŞİV ---
with tab3:
    st.subheader("📜 Geçmiş Girişler")
    conn = get_connection()
    df_arsiv = pd.read_sql("SELECT * FROM public.stok_kayitlari ORDER BY tarih DESC", conn)
    conn.close()
    for _, row in df_arsiv.iterrows():
        p_label = row['plaka'] if 'plaka' in row and row['plaka'] else "Yok"
        with st.expander(f"📅 {row['tarih']} - {row['malzeme_adi']} | 🚚 {p_label}"):
            c_a1, c_a2 = st.columns(2)
            c_a1.write(f"**Miktar:** {row['miktar']} {row['birim']}\n\n**Firma:** {row['tedarikci']}")
            if row['irsaliye_foto']:
                c_a2.image(f"data:image/jpeg;base64,{row['irsaliye_foto']}", use_container_width=True)

# --- TAB 4: AYARLAR (Havuz Yönetimi) ---
with tab4:
    st.subheader("⚙️ Havuz Yönetimi")
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown("### 🏗️ Malzeme Listesi")
        yeni_m = st.text_input("Yeni Malzeme")
        if st.button("Malzeme Ekle"):
            if yeni_m:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO public.havuz_malzeme (ad) VALUES (%s)", (yeni_m.strip(),))
                    conn.commit()
                    st.rerun()
                except: st.error("Zaten var!")
        
        conn = get_connection()
        st.dataframe(pd.read_sql("SELECT ad FROM public.havuz_malzeme ORDER BY ad", conn), use_container_width=True)
        conn.close()

    with col_h2:
        st.markdown("### 📏 Birim Listesi")
        yeni_b = st.text_input("Yeni Birim")
        if st.button("Birim Ekle"):
            if yeni_b:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("INSERT INTO public.havuz_birim (ad) VALUES (%s)", (yeni_b.strip(),))
                    conn.commit()
                    st.rerun()
                except: st.error("Zaten var!")
        
        conn = get_connection()
        st.dataframe(pd.read_sql("SELECT ad FROM public.havuz_birim ORDER BY ad", conn), use_container_width=True)
        conn.close()