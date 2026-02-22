# import streamlit as st
# from database import get_connection, query_to_df
# import pandas as pd
# import time
# import io
# from datetime import datetime

# # Sayfa Konfigürasyonu
# st.set_page_config(page_title="Puantaj Yönetimi", layout="wide")
# st.title("🕒 Günlük Puantaj Yönetimi")

# # Sekme yapısını oluşturuyoruz
# tab_manuel, tab_excel = st.tabs(["✍️ Manuel Giriş", "📥 Excel ile Toplu Yükleme"])

# # --- 1. SEKME: MANUEL GİRİŞ (Firma Bilgisi Entegre Edildi) ---
# with tab_manuel:
#     st.subheader("Tekil Puantaj Kaydı")
    
#     # 1. VERİ ÇEKME: Personelleri, branşlarını ve şirketlerini JOIN ile çekiyoruz
#     p_query = """
#         SELECT p.id, p.ad_soyad, p.gorev, s.sirket_adi 
#         FROM personeller p 
#         LEFT JOIN sirketler s ON p.sirket_id = s.id 
#         ORDER BY p.ad_soyad ASC
#     """
#     p_df = query_to_df(p_query)
    
#     # Alan listesini çekiyoruz
#     a_df = query_to_df("SELECT id, alan_adi FROM alanlar ORDER BY alan_adi ASC")
    
#     if p_df.empty or a_df.empty:
#         st.warning("⚠️ Lütfen önce Personel, Şirket ve Alan tanımlamalarını tamamlayın.")
#     else:
#         with st.form("manuel_puantaj_form_v3", clear_on_submit=True):
#             col1, col2, col3 = st.columns(3)
            
#             with col1:
#                 # UNIQUE PERSONEL SEÇİMİ
#                 p_list = p_df["ad_soyad"].tolist()
#                 secilen_p_ad = st.selectbox("👷 Personel Seçin", options=p_list)
                
#                 # Seçilen personelin bilgilerini yakalıyoruz
#                 p_info = p_df[p_df["ad_soyad"] == secilen_p_ad].iloc[0]
#                 p_id = int(p_info["id"])
                
#                 # OTOMATİK GELEN BİLGİLER
#                 db_kayitli_brans = str(p_info["gorev"]) if p_info["gorev"] else ""
#                 db_sirket_adi = str(p_info["sirket_adi"]) if p_info["sirket_adi"] else "Firma Atanmamış"
                
#                 tarih = st.date_input("📅 Çalışma Tarihi", value=datetime.now())

#             with col2:
#                 # ALAN SEÇİMİ
#                 a_list = a_df["alan_adi"].tolist()
#                 secilen_a_ad = st.selectbox("📍 Çalışılan Alan", options=a_list)
#                 a_id = int(a_df[a_df["alan_adi"] == secilen_a_ad].iloc[0]["id"])
                
#                 mesai = st.number_input("⏱️ Mesai Saati", min_value=0.0, max_value=24.0, value=8.0, step=0.5)

#             with col3:
#                 # FİRMA BİLGİSİ (Otomatik Gelir - Değiştirilemez Bilgi Amaçlı)
#                 st.text_input("🏢 Bağlı Olduğu Firma", value=db_sirket_adi, disabled=False)
                
#                 # DİNAMİK BRANŞ ALANI (Değiştirilebilir)
#                 yapilan_is = st.text_input("🛠️ Yapılan İş / Branş", value=db_kayitli_brans)

#             # Ek bilgiler
#             c4, c5 = st.columns(2)
#             with c4:
#                 hava = st.selectbox("☁️ Hava Durumu", ["Güneşli", "Parçalı Bulutlu", "Bulutlu", "Yağmurlu", "Karlı"])
#             with c5:
#                 gecikme = st.text_input("⚠️ Gecikme/Not", value="Yok")
            
#             submit = st.form_submit_button("💾 Puantajı Veritabanına İşle")
            
#             if submit:
#                 conn = get_connection(); cur = conn.cursor()
#                 try:
#                     cur.execute("""
#                         INSERT INTO puantaj_kayitlari 
#                         (personel_id, alan_id, tarih, mesai_saati, hava_durumu, aciklama, gecikme_nedeni)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s)
#                     """, (p_id, a_id, tarih, mesai, hava, yapilan_is, gecikme))
#                     conn.commit()
#                     st.success(f"✅ {secilen_p_ad} ({db_sirket_adi}) için puantaj kaydedildi.")
#                     time.sleep(1)
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Teknik bir hata oluştu: {e}")
#                 finally:
#                     conn.close()

# # --- 2. SEKME: EXCEL İLE TOPLU YÜKLEME ---
# with tab_excel:
#     col_a, col_b = st.columns([1, 1])
    
#     with col_a:
#         st.subheader("📄 1. Şablonu Hazırla")
#         if not p_df.empty and not a_df.empty:
#             puantaj_template = {
#                 "personel_id": p_df["id"].tolist()[:5],
#                 "ad_soyad": p_df["ad_soyad"].tolist()[:5],
#                 "alan_id": [a_df["id"].iloc[0]] * 5,
#                 "tarih": [datetime.now().strftime('%Y-%m-%d')] * 5,
#                 "mesai_saati": [8.0] * 5,
#                 "hava_durumu": ["Güneşli"] * 5,
#                 "brans": p_df["gorev"].tolist()[:5],
#                 "gecikme_nedeni": ["Yok"] * 5
#             }
#             template_df = pd.DataFrame(puantaj_template)
            
#             buffer = io.BytesIO()
#             with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#                 template_df.to_excel(writer, index=False, sheet_name='Puantaj_Yukleme')
            
#             st.download_button(
#                 label="📥 Güncel Şablonu İndir",
#                 data=buffer.getvalue(),
#                 file_name="gunluk_puantaj_sablonu.xlsx",
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#     with col_b:
#         st.subheader("📤 2. Verileri Yükle")
#         uploaded_puantaj = st.file_uploader("Excel Dosyasını Seçin", type=['xlsx'])
        
#         if uploaded_puantaj:
#             try:
#                 p_import_df = pd.read_excel(uploaded_puantaj)
#                 if st.button("🚀 Excel Verilerini İşle"):
#                     conn = get_connection(); cur = conn.cursor()
#                     success = 0
#                     for index, row in p_import_df.iterrows():
#                         try:
#                             cur.execute("""
#                                 INSERT INTO puantaj_kayitlari 
#                                 (personel_id, alan_id, tarih, mesai_saati, hava_durumu, aciklama, gecikme_nedeni)
#                                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#                             """, (int(row['personel_id']), int(row['alan_id']), row['tarih'], 
#                                   float(row['mesai_saati']), str(row['hava_durumu']), 
#                                   str(row['brans']), str(row['gecikme_nedeni'])))
#                             success += 1
#                         except: continue
#                     conn.commit(); conn.close()
#                     st.success(f"✅ {success} kayıt başarıyla eklendi.")
#                     time.sleep(1); st.rerun()
#             except Exception as e:
#                 st.error(f"Hata: {e}")

import streamlit as st
from database import get_connection, query_to_df
import pandas as pd
import time
import io
from datetime import datetime

# Her sayfanın (pages içindeki dosyaların) en başına eklenecek kontrol:

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("Bu sayfayı görüntülemek için lütfen ana sayfadan giriş yapın.")
    st.stop() # Sayfanın geri kalanının yüklenmesini durdurur



# Sayfa Konfigürasyonu
st.set_page_config(page_title="Puantaj Yönetimi", layout="wide")
st.title("🕒 Günlük Puantaj Yönetimi")

# Sekme yapısını oluşturuyoruz
tab_manuel, tab_excel = st.tabs(["✍️ Manuel Giriş", "📥 Excel ile Toplu Yükleme"])

# --- 1. SEKME: MANUEL GİRİŞ (Dinamik Firma Seçimi Aktif) ---
with tab_manuel:
    st.subheader("Tekil Puantaj Kaydı")
    
    # Veri Çekme: Personelleri, branşlarını ve şirketlerini JOIN ile çekiyoruz
    p_query = """
        SELECT p.id, p.ad_soyad, p.gorev, s.sirket_adi 
        FROM personeller p 
        LEFT JOIN sirketler s ON p.sirket_id = s.id 
        ORDER BY p.ad_soyad ASC
    """
    p_df = query_to_df(p_query)
    
    # Şirket listesini ve Alan listesini çekiyoruz
    s_df = query_to_df("SELECT sirket_adi FROM sirketler ORDER BY sirket_adi ASC")
    a_df = query_to_df("SELECT id, alan_adi FROM alanlar ORDER BY alan_adi ASC")
    
    if p_df.empty or a_df.empty or s_df.empty:
        st.warning("⚠️ Lütfen önce Personel, Şirket ve Alan tanımlamalarını (Kayıt & Yönetim sayfasından) tamamlayın.")
    else:
        # Formun her personel değişiminde yenilenmesi için benzersiz bir yapı kuruyoruz
        with st.form("manuel_puantaj_form_v5", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # PERSONEL SEÇİMİ
                p_list = p_df["ad_soyad"].tolist()
                secilen_p_ad = st.selectbox("👷 Personel Seçin", options=p_list)
                
                # Seçilen personelin veritabanı bilgilerini yakalıyoruz
                p_info = p_df[p_df["ad_soyad"] == secilen_p_ad].iloc[0]
                p_id = int(p_info["id"])
                
                # OTOMATİK GELEN BİLGİLERİN HAZIRLANMASI
                db_brans = str(p_info["gorev"]).strip() if p_info["gorev"] else ""
                db_sirket = str(p_info["sirket_adi"]).strip() if p_info["sirket_adi"] else ""
                
                tarih = st.date_input("📅 Çalışma Tarihi", value=datetime.now())

            with col2:
                # ALAN SEÇİMİ
                a_list = a_df["alan_adi"].tolist()
                secilen_a_ad = st.selectbox("📍 Çalışılan Alan", options=a_list)
                a_id = int(a_df[a_df["alan_adi"] == secilen_a_ad].iloc[0]["id"])
                
                mesai = st.number_input("⏱️ Mesai Saati", min_value=0.0, max_value=24.0, value=8.0, step=0.5)

            with col3:
                # --- ŞİRKET/FİRMA SEÇİMİ (Açılır Kutu ve Aktif) ---
                s_options = s_df["sirket_adi"].tolist()
                
                # Personelin kayıtlı şirketini listede bulup varsayılan index yapıyoruz
                try:
                    s_idx = s_options.index(db_sirket) if db_sirket in s_options else 0
                except:
                    s_idx = 0
                
                # Kullanıcı isterse buradan firmayı değiştirebilir (disabled=False varsayılan)
                u_sirket = st.selectbox("🏢 Bağlı Olduğu Firma", options=s_options, index=s_idx)
                
                # YAPILAN İŞ / BRANŞ (Değiştirilebilir)
                yapilan_is = st.text_input("🛠️ Yapılan İş / Branş", value=db_brans)

            # Alt Satır Bilgileri
            c_alt1, c_alt2 = st.columns(2)
            with c_alt1:
                hava = st.selectbox("☁️ Hava Durumu", ["Güneşli", "Parçalı Bulutlu", "Bulutlu", "Yağmurlu", "Karlı"])
            with c_alt2:
                gecikme = st.text_input("⚠️ Gecikme/Not", value="Yok")
            
            submit = st.form_submit_button("💾 Puantajı Veritabanına İşle")
            
            if submit:
                conn = get_connection(); cur = conn.cursor()
                try:
                    # Puantaj kaydı personel_id üzerinden atılır. 
                    # Firma seçimi o anki teyit içindir, raporlarda personel tablosundaki sirket_id ile birleşir.
                    cur.execute("""
                        INSERT INTO puantaj_kayitlari 
                        (personel_id, alan_id, tarih, mesai_saati, hava_durumu, aciklama, gecikme_nedeni)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (p_id, a_id, tarih, mesai, hava, yapilan_is, gecikme))
                    conn.commit()
                    st.success(f"✅ {secilen_p_ad} ({u_sirket}) için puantaj kaydı başarıyla oluşturuldu.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Kayıt sırasında bir hata oluştu: {e}")
                finally:
                    conn.close()

# --- 2. SEKME: EXCEL İLE TOPLU YÜKLEME ---
with tab_excel:
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("📄 1. Şablonu Hazırla")
        if not p_df.empty and not a_df.empty:
            # Güncel Excel şablonu (Sirket bilgisi personel tablosundan çekildiği için ID bazlıdır)
            puantaj_template = {
                "personel_id": p_df["id"].tolist()[:10],
                "ad_soyad": p_df["ad_soyad"].tolist()[:10],
                "alan_id": [a_df["id"].iloc[0]] * 10 if not a_df.empty else [0]*10,
                "tarih": [datetime.now().strftime('%Y-%m-%d')] * 10,
                "mesai_saati": [8.0] * 10,
                "hava_durumu": ["Güneşli"] * 10,
                "brans": p_df["gorev"].tolist()[:10],
                "gecikme_nedeni": ["Yok"] * 10
            }
            template_df = pd.DataFrame(puantaj_template)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                template_df.to_excel(writer, index=False, sheet_name='Puantaj_Yukleme')
            
            st.download_button(
                label="📥 Güncel Puantaj Şablonunu İndir",
                data=buffer.getvalue(),
                file_name="gunluk_puantaj_sablonu.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col_b:
        st.subheader("📤 2. Verileri Yükle")
        uploaded_puantaj = st.file_uploader("Doldurulan Excel Dosyasını Seçin", type=['xlsx'])
        
        if uploaded_puantaj:
            try:
                p_import_df = pd.read_excel(uploaded_puantaj)
                st.write("Veri Önizleme (İlk 5 Satır):")
                st.dataframe(p_import_df.head(), use_container_width=True)
                
                if st.button("🚀 Excel Verilerini Veritabanına İşle"):
                    conn = get_connection(); cur = conn.cursor()
                    success_count = 0
                    for index, row in p_import_df.iterrows():
                        try:
                            cur.execute("""
                                INSERT INTO puantaj_kayitlari 
                                (personel_id, alan_id, tarih, mesai_saati, hava_durumu, aciklama, gecikme_nedeni)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (int(row['personel_id']), int(row['alan_id']), row['tarih'], 
                                  float(row['mesai_saati']), str(row['hava_durumu']), 
                                  str(row['brans']), str(row['gecikme_nedeni'])))
                            success_count += 1
                        except:
                            continue
                    conn.commit(); conn.close()
                    st.success(f"✅ {success_count} adet puantaj kaydı başarıyla eklendi.")
                    time.sleep(1); st.rerun()
            except Exception as e:
                st.error(f"Dosya işleme hatası: {e}")