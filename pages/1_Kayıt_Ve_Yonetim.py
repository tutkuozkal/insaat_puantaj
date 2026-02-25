import streamlit as st
from database import get_connection, query_to_df
import pandas as pd
import psycopg2
from datetime import datetime
import time
import io

# Her sayfanın (pages içindeki dosyaların) en başına eklenecek kontrol:
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Bu sayfayı görüntülemek için lütfen ana sayfadan giriş yapın.")
    st.stop() # Sayfanın geri kalanının yüklenmesini durdurur


# Sayfa Ayarları
st.set_page_config(page_title="Sistem Yönetimi", layout="wide")
st.title("⚙️ Sistem Tanımlamaları ve Güvenli Yönetim")

# Sekmeleri Oluştur
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Akıllı Toplu Ekle", 
    "🏢 Şirket Havuzu",
    "🏗️ Alan Havuzu", 
    "🛠️ Görev Havuzu", 
    "📋 Personel Detay & Dosya",
    "📊 Personel İstatistik"
])

# --- 1. AKILLI TOPLU EKLE (Otomatik Havuz Doldurma) ---
with tab1:
    st.subheader("📥 Tek Excel ile Sistemi Kur")
    col_temp, col_up = st.columns(2)
    with col_temp:
        template_data = {
            "ad_soyad": ["Ahmet Yılmaz"], "tc_no": ["10000000000"], "telefon": ["0500"],
            "gorev": ["Kalıpçı"], "sirket": ["Alfa Yapı"], "kan_grubu": ["A+"], "dogum_tarihi": ["1990-01-01"]
        }
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(template_data).to_excel(writer, index=False)
        st.download_button("📄 Şablonu İndir", buffer.getvalue(), "akilli_sablon.xlsx")

    with col_up:
        uploaded_file = st.file_uploader("Dosya Yükleyin", type=['xlsx'])
        if uploaded_file and st.button("🚀 Otomatik Aktar"):
            import_df = pd.read_excel(uploaded_file)
            conn = get_connection(); cur = conn.cursor()
            success, skipped = 0, 0
            for _, row in import_df.iterrows():
                try:
                    cur.execute("INSERT INTO gorev_havuzu (gorev_adi) VALUES (%s) ON CONFLICT DO NOTHING", (str(row['gorev']).strip(),))
                    cur.execute("INSERT INTO sirketler (sirket_adi) VALUES (%s) ON CONFLICT DO NOTHING", (str(row['sirket']).strip(),))
                    cur.execute("SELECT id FROM sirketler WHERE sirket_adi = %s", (str(row['sirket']).strip(),))
                    s_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO personeller (ad_soyad, tc_no, telefon, gorev, sirket_id, kan_grubu, dogum_tarihi)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (row['ad_soyad'], str(row['tc_no']), str(row['telefon']), row['gorev'], s_id, row['kan_grubu'], row['dogum_tarihi']))
                    success += 1
                except: skipped += 1; conn.rollback(); continue
            conn.commit(); conn.close(); st.success(f"✅ {success} Kayıt eklendi."); time.sleep(1); st.rerun()

# --- 2. ŞİRKET HAVUZU (Güvenli Silme & Sayım) ---
with tab2:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        with st.form("sirket_form"):
            s_adi = st.text_input("Yeni Şirket Adı")
            if st.form_submit_button("Ekle"):
                conn = get_connection(); cur = conn.cursor()
                cur.execute("INSERT INTO sirketler (sirket_adi) VALUES (%s) ON CONFLICT DO NOTHING", (s_adi.strip(),))
                conn.commit(); conn.close(); st.rerun()
    with col_b:
        s_query = """
            SELECT s.id, s.sirket_adi, COUNT(p.id) as p_count 
            FROM sirketler s LEFT JOIN personeller p ON s.id = p.sirket_id 
            GROUP BY s.id, s.sirket_adi ORDER BY s.sirket_adi
        """
        s_list = query_to_df(s_query)
        for _, r in s_list.iterrows():
            c1, c2 = st.columns([4,1])
            c1.info(f"🏢 {r['sirket_adi']} ({r['p_count']} Personel)")
            if r['p_count'] == 0:
                if c2.button("Sil", key=f"s_del_{r['id']}"):
                    conn = get_connection(); cur = conn.cursor(); cur.execute("DELETE FROM sirketler WHERE id=%s", (r['id'],)); conn.commit(); conn.close(); st.rerun()
            else: c2.write("🔒")

# --- 3. ALAN HAVUZU (Güvenli Silme & Sayım) ---
with tab3:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        with st.form("alan_form"):
            a_adi = st.text_input("Alan Adı")
            if st.form_submit_button("Alanı Kaydet"):
                conn = get_connection(); cur = conn.cursor(); cur.execute("INSERT INTO alanlar (alan_adi) VALUES (%s)", (a_adi.strip(),)); conn.commit(); conn.close(); st.rerun()
    with col_b:
        a_query = """
            SELECT a.id, a.alan_adi, COUNT(pk.id) as pk_count 
            FROM alanlar a LEFT JOIN puantaj_kayitlari pk ON a.id = pk.alan_id 
            GROUP BY a.id, a.alan_adi ORDER BY a.alan_adi
        """
        a_list = query_to_df(a_query)
        for _, r in a_list.iterrows():
            c1, c2 = st.columns([4,1]); c1.write(f"🏗️ {r['alan_adi']} ({r['pk_count']} Kayıt)")
            if r['pk_count'] == 0:
                if c2.button("Sil", key=f"a_del_{r['id']}"):
                    conn = get_connection(); cur = conn.cursor(); cur.execute("DELETE FROM alanlar WHERE id=%s", (r['id'],)); conn.commit(); conn.close(); st.rerun()
            else: c2.write("🔒")

# --- 4. GÖREV HAVUZU (Güvenli Silme & Sayım) ---
with tab4:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        with st.form("gorev_form"):
            g_adi = st.text_input("Branş Adı")
            if st.form_submit_button("Görevi Kaydet"):
                conn = get_connection(); cur = conn.cursor(); cur.execute("INSERT INTO gorev_havuzu (gorev_adi) VALUES (%s) ON CONFLICT DO NOTHING", (g_adi.strip(),)); conn.commit(); conn.close(); st.rerun()
    with col_b:
        g_query = """
            SELECT g.id, g.gorev_adi, COUNT(p.id) as p_count 
            FROM gorev_havuzu g LEFT JOIN personeller p ON g.gorev_adi = p.gorev 
            GROUP BY g.id, g.gorev_adi ORDER BY g.gorev_adi
        """
        g_list = query_to_df(g_query)
        for _, r in g_list.iterrows():
            c1, c2 = st.columns([4,1]); c1.write(f"🛠️ {r['gorev_adi']} ({r['p_count']} Personel)")
            if r['p_count'] == 0:
                if c2.button("Sil", key=f"g_del_{r['id']}"):
                    conn = get_connection(); cur = conn.cursor(); cur.execute("DELETE FROM gorev_havuzu WHERE id=%s", (r['id'],)); conn.commit(); conn.close(); st.rerun()
            else: c2.write("🔒")

# --- 5. PERSONEL DETAY & DOSYA (DÜZELTİLDİ) ---
with tab5:
    st.subheader("📋 Detaylı Personel Yönetimi")
    p_df = query_to_df("SELECT p.*, s.sirket_adi FROM personeller p LEFT JOIN sirketler s ON p.sirket_id = s.id ORDER BY p.ad_soyad ASC")
    
    if not p_df.empty:
        secilen = st.selectbox("Personel Seçin:", p_df['ad_soyad'].tolist())
        p_row = p_df[p_df['ad_soyad'] == secilen].iloc[0]
        p_id = int(p_row['id'])

        with st.form(f"detay_form_{p_id}"):
            c1, c2, c3 = st.columns([1, 2, 2])
            
            with c2:
                u_ad = st.text_input("Ad Soyad", value=p_row['ad_soyad'])
                
                # ŞİRKET SEÇİMİ (Database'den)
                s_q = query_to_df("SELECT sirket_adi FROM sirketler ORDER BY sirket_adi")
                s_opts = s_q["sirket_adi"].tolist() if not s_q.empty else ["Genel"]
                p_sirket = str(p_row['sirket_adi']).strip() if p_row['sirket_adi'] else ""
                s_idx = s_opts.index(p_sirket) if p_sirket in s_opts else 0
                u_sirket = st.selectbox("Şirket", s_opts, index=s_idx)

            with c3:
                # BRANŞ / GÖREV SEÇİMİ (Database'den Geri Getirildi)
                g_q = query_to_df("SELECT gorev_adi FROM gorev_havuzu ORDER BY gorev_adi")
                g_opts = g_q["gorev_adi"].tolist() if not g_q.empty else ["Genel"]
                p_gorev = str(p_row['gorev']).strip() if p_row['gorev'] else ""
                # Eğer personelin görevi listede yoksa geçici ekle ki hata vermesin
                if p_gorev and p_gorev not in g_opts: g_opts.append(p_gorev)
                g_idx = g_opts.index(p_gorev) if p_gorev in g_opts else 0
                u_brans = st.selectbox("Branş (Görev)", g_opts, index=g_idx)
                
                u_tc = st.text_input("TC No", value=str(p_row['tc_no']))

            if st.form_submit_button("💾 Bilgileri Güncelle"):
                conn = get_connection(); cur = conn.cursor()
                try:
                    cur.execute("SELECT id FROM sirketler WHERE sirket_adi=%s", (u_sirket,))
                    sid = cur.fetchone()[0]
                    cur.execute("""
                        UPDATE personeller 
                        SET ad_soyad=%s, gorev=%s, tc_no=%s, sirket_id=%s 
                        WHERE id=%s
                    """, (u_ad, u_brans, u_tc, sid, p_id))
                    conn.commit(); conn.close(); st.success("✅ Güncellendi!"); time.sleep(1); st.rerun()
                except Exception as e: st.error(f"Hata: {e}")

# --- 6. İSTATİSTİK ---
with tab6:
    st.subheader("📊 Genel Personel Durumu")
    res = query_to_df("SELECT p.ad_soyad, s.sirket_adi, p.gorev FROM personeller p LEFT JOIN sirketler s ON p.sirket_id = s.id")
    if not res.empty:
        st.dataframe(res, use_container_width=True)
        st.bar_chart(res['sirket_adi'].value_counts())