# import streamlit as st
# from database import query_to_df

# st.set_page_config(page_title="Şantiye Yönetim Sistemi", layout="wide")

# # --- SOL MENÜ (Sidebar) ---
# with st.sidebar:
#     st.title("🏗️ Şantiye Yönetim")
#     st.divider()
#     # Dosya yollarının pages/ klasörü altında olduğundan emin olun
#     st.page_link("main.py", label="Ana Sayfa", icon="🏠")
#     try:
#         st.page_link("pages/1_Kayıt_Ve_Yonetim.py", label="Kayıt & Yönetim", icon="👤")
#         st.page_link("pages/2_Gunluk_Puantaj.py", label="Günlük Puantaj", icon="🕒")
#         st.page_link("pages/3_Raporlama.py", label="Raporlama", icon="📊")
#     except Exception as e:
#         st.error("Sayfa dosyaları bulunamadı. Lütfen 'pages' klasörünü kontrol edin.")
#     st.divider()

# # --- ANA EKRAN İÇERİĞİ ---
# st.title("🚀 Şantiye Genel Durum Paneli")

# # Metrikleri yan yana dizelim
# m1, m2, m3 = st.columns(3)

# try:
#     # Veritabanından canlı verileri çekelim
#     p_count = query_to_df("SELECT COUNT(*) FROM personeller").iloc[0,0]
#     total_efor = query_to_df("SELECT SUM(mesai_saati) FROM puantaj_kayitlari").iloc[0,0] or 0
    
#     m1.metric("Toplam Personel", f"{p_count} Kişi")
#     m2.metric("Toplam İş Gücü", f"{total_efor:,.0f} Saat")
#     m3.metric("Aktif Şantiyeler", "1") # Bu manuel veya veritabanından gelebilir
# except Exception as e:
#     st.warning("Veritabanı bağlantısı henüz kurulmadı veya tablo boş.")

# st.divider()
# st.info("Yönetim paneline erişmek için sol menüdeki 'Kayıt & Yönetim' sekmesini kullanabilirsiniz.")

import streamlit as st
from database import query_to_df
import time

# Sayfa Ayarları
st.set_page_config(page_title="Şantiye Kontrol Sistemi", layout="centered")

# --- LOGIN FONKSİYONU ---
def login():
    st.title("🔐 Şantiye Yönetim Sistemi")
    st.subheader("Lütfen Giriş Yapın")
    
    with st.form("login_form"):
        u_name = st.text_input("Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        submit = st.form_submit_button("Giriş Yap")
        
        if submit:
            # Database'den kullanıcıyı kontrol et
            user_check = query_to_df(f"SELECT * FROM kullanicilar WHERE kullanici_adi = '{u_name}' AND sifre = '{u_pass}'")
            
            if not user_check.empty:
                st.session_state["logged_in"] = True
                st.session_state["user_info"] = user_check.iloc[0].to_dict()
                st.success(f"Hoş geldiniz, {st.session_state['user_info']['tam_ad']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")

# --- OTURUM KONTROLÜ ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    # Giriş yapılmışsa ana içeriği göster
    st.sidebar.success(f"Giriş Yapıldı: {st.session_state['user_info']['tam_ad']}")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.rerun()
        
    st.title("🏗️ Şantiye Yönetim Paneli")
    st.write("Sol menüden yapmak istediğiniz işlemi seçebilirsiniz.")
    
    # Buraya genel bir özet tablo veya şantiye görseli eklenebilir