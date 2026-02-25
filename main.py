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