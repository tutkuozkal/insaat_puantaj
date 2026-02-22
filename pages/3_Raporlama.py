# import streamlit as st
# from database import query_to_df, pdf_olustur
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# from datetime import datetime

# # Sayfa Konfigürasyonu
# st.set_page_config(page_title="Raporlama ve Analiz", layout="wide")
# st.title("📊 Analiz, Rapor ve İlerleme Paneli")

# # 1. Veritabanından Veri Çekme
# query = """
#     SELECT 
#         p.ad_soyad, 
#         a.alan_adi, 
#         pk.tarih, 
#         pk.mesai_saati, 
#         pk.hava_durumu, 
#         pk.aciklama as brans,
#         pk.gecikme_nedeni
#     FROM puantaj_kayitlari pk 
#     JOIN personeller p ON pk.personel_id = p.id 
#     JOIN alanlar a ON pk.alan_id = a.id
#     ORDER BY pk.tarih ASC
# """
# df = query_to_df(query)

# if df.empty:
#     st.info("⚠️ Henüz analiz edilecek veri bulunmuyor. Lütfen puantaj girişi yapın.")
# else:
#     # Tarih formatını standartlaştır
#     df['tarih'] = pd.to_datetime(df['tarih'])
    
#     # --- YAN MENÜ FİLTRELERİ ---
#     st.sidebar.header("🔍 Filtreleme Seçenekleri")
#     baslangic = st.sidebar.date_input("Başlangıç Tarihi", df['tarih'].min())
#     bitis = st.sidebar.date_input("Bitiş Tarihi", df['tarih'].max())
    
#     # Filtreyi Uygula
#     mask = (df['tarih'] >= pd.to_datetime(baslangic)) & (df['tarih'] <= pd.to_datetime(bitis))
#     f_df = df.loc[mask]

#     # --- 🏗️ ALAN BAZLI BRANŞ GRUPLAMASI (Üst Özet Bölümü) ---
#     st.subheader("🏗️ Alan Bazlı Branş Dağılımı")
    
#     alanlar = f_df['alan_adi'].unique()
    
#     for alan in alanlar:
#         # SyntaxError hatasını önlemek için standart with kullanımı
#         with st.expander(f"📍 {alan} - Toplam İş Gücü Detayı", expanded=True):
#             alan_df = f_df[f_df['alan_adi'] == alan]
#             alan_brans_ozet = alan_df.groupby('brans')['mesai_saati'].sum().sort_values(ascending=False)
            
#             if not alan_brans_ozet.empty:
#                 # Metriklerin yan yana dizilmesi için dinamik kolonlar
#                 cols = st.columns(len(alan_brans_ozet))
#                 for i, (brans_adi, toplam_saat) in enumerate(alan_brans_ozet.items()):
#                     cols[i].metric(label=brans_adi, value=f"{toplam_saat:,.0f} Sa")
#             else:
#                 st.write("Bu alanda kayıtlı çalışma bulunamadı.")

#     st.divider()

#     # --- ANALİZ SEKMELERİ ---
#     tab1, tab2, tab3 = st.tabs(["📉 Trend Analizi (S-Curve)", "🏗️ Alan Dağılımı", "📜 Veri Tablosu"])

#     with tab1:
#         st.subheader("🚀 Hibrit Analiz: Branş Dağılımı ve İlerleme Eğrisi")
        
#         # Grafik Verilerini Hazırla
#         daily_brans = f_df.groupby(['tarih', 'brans'])['mesai_saati'].sum().reset_index()
#         daily_total = f_df.groupby('tarih')['mesai_saati'].sum().reset_index()
#         daily_total['kumulatif'] = daily_total['mesai_saati'].cumsum()

#         # İkincil eksenli grafik nesnesi
#         fig_hybrid = make_subplots(specs=[[{"secondary_y": True}]])

#         # A. Branşlar: Çubuk Grafik (Stacked Bar)
#         unique_branslar = daily_brans['brans'].unique()
#         for br in unique_branslar:
#             br_data = daily_brans[daily_brans['brans'] == br]
#             fig_hybrid.add_trace(
#                 go.Bar(
#                     x=br_data['tarih'], 
#                     y=br_data['mesai_saati'], 
#                     name=str(br),
#                     text=br_data['mesai_saati'],
#                     textposition='inside'
#                 ),
#                 secondary_y=False
#             )

#         # B. Kümülatif İlerleme: Kalın Çizgi (S-Curve)
#         fig_hybrid.add_trace(
#             go.Scatter(
#                 x=daily_total['tarih'], 
#                 y=daily_total['kumulatif'], 
#                 mode='lines+markers+text',
#                 name="S-Curve (Kümülatif)",
#                 text=daily_total['kumulatif'],
#                 textposition="top left",
#                 textfont=dict(color="red", size=10),
#                 line=dict(color='red', width=4)
#             ),
#             secondary_y=True
#         )

#         # Grafik Düzeni
#         fig_hybrid.update_layout(
#             height=600, 
#             hovermode="x unified", 
#             barmode='stack',
#             legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
#         )
        
#         fig_hybrid.update_yaxes(title_text="Günlük Mesai (Sa)", secondary_y=False)
#         fig_hybrid.update_yaxes(title_text="Kümülatif Toplam (Sa)", secondary_y=True)
        
#         st.plotly_chart(fig_hybrid, use_container_width=True)

#     with tab2:
#         c1, c2 = st.columns(2)
#         with c1:
#             st.plotly_chart(px.pie(f_df, values='mesai_saati', names='alan_adi', 
#                                    title="Alanlara Göre Toplam Efor", hole=0.4), use_container_width=True)
#         with c2:
#             brans_genel = f_df.groupby('brans')['mesai_saati'].sum().reset_index()
#             st.plotly_chart(px.bar(brans_genel, x='mesai_saati', y='brans', 
#                                    title="Branş Bazlı Toplam Kıyaslama", orientation='h'), use_container_width=True)

#     with tab3:
#         st.dataframe(f_df, use_container_width=True)
#         st.divider()
        
#         # PDF Butonu
#         if st.button("📄 PDF Raporu Oluştur"):
#             pdf_data = pdf_olustur(f_df, f"{baslangic} - {bitis}")
#             st.download_button(
#                 label="📥 İndir",
#                 data=pdf_data,
#                 file_name=f"Rapor_{datetime.now().strftime('%Y%m%d')}.pdf",
#                 mime="application/pdf"
#             )
#------------------------------ versiyon2 ------------------------------#
# import streamlit as st
# from database import query_to_df
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# from datetime import datetime

# # Sayfa Genel Ayarları
# st.set_page_config(page_title="Raporlama ve Analiz", layout="wide")
# st.title("📊 Şantiye Raporlama ve İlerleme Analizi")

# # --- 1. VERİ ÇEKME (Şirket Bilgisi Dahil Edildi) ---
# # personeller üzerinden sirketler tablosunu JOIN ile bağlıyoruz
# query = """
#     SELECT 
#         p.ad_soyad, 
#         s.sirket_adi as sirket, 
#         a.alan_adi, 
#         pk.tarih, 
#         pk.mesai_saati, 
#         pk.aciklama as brans 
#     FROM puantaj_kayitlari pk 
#     JOIN personeller p ON pk.personel_id = p.id 
#     LEFT JOIN sirketler s ON p.sirket_id = s.id 
#     JOIN alanlar a ON pk.alan_id = a.id 
#     ORDER BY pk.tarih ASC
# """
# df = query_to_df(query)

# if df.empty:
#     st.info("📊 Henüz raporlanacak veri bulunmuyor. Lütfen puantaj girişi yapın.")
# else:
#     df['tarih'] = pd.to_datetime(df['tarih'])
    
#     # --- ÜST FİLTRELEME ALANI ---
#     st.sidebar.header("🔍 Rapor Filtreleri")
#     # Şirket Filtresi
#     sirket_listesi = ["Tümü"] + sorted(df['sirket'].dropna().unique().tolist())
#     secilen_sirket = st.sidebar.selectbox("🏢 Şirket Seçin", sirket_listesi)
    
#     # Branş Filtresi
#     brans_listesi = ["Tümü"] + sorted(df['brans'].unique().tolist())
#     secilen_brans = st.sidebar.selectbox("🛠️ Branş Seçin", brans_listesi)

#     # Veriyi filtrelere göre süzüyoruz
#     filtered_df = df.copy()
#     if secilen_sirket != "Tümü":
#         filtered_df = filtered_df[filtered_df['sirket'] == secilen_sirket]
#     if secilen_brans != "Tümü":
#         filtered_df = filtered_df[filtered_df['brans'] == secilen_brans]

#     # --- ÖZET METRİKLER ---
#     m1, m2, m3, m4 = st.columns(4)
#     total_saat = filtered_df['mesai_saati'].sum()
#     unique_p = filtered_df['ad_soyad'].nunique()
#     unique_s = filtered_df['sirket'].nunique()
    
#     m1.metric("Toplam Efor", f"{total_saat:,.0f} Saat")
#     m2.metric("Aktif Personel", f"{unique_p} Kişi")
#     m3.metric("Çalışan Şirket", f"{unique_s} Firma")
#     m4.metric("Seçili Branş", secilen_brans if secilen_brans != "Tümü" else "Hepsi")

#     st.divider()

#     # --- ŞİRKET BAZLI DAĞILIM (Yeni Grafik) ---
#     c1, c2 = st.columns(2)
    
#     with c1:
#         st.subheader("🏢 Şirketlere Göre Efor Dağılımı")
#         sirket_ozet = filtered_df.groupby('sirket')['mesai_saati'].sum().reset_index()
#         fig_sirket = px.pie(sirket_ozet, values='mesai_saati', names='sirket', hole=0.4,
#                            color_discrete_sequence=px.colors.qualitative.Pastel)
#         st.plotly_chart(fig_sirket, use_container_width=True)

#     with c2:
#         st.subheader("🛠️ Branşlara Göre Efor Dağılımı")
#         brans_ozet = filtered_df.groupby('brans')['mesai_saati'].sum().reset_index()
#         fig_brans = px.bar(brans_ozet, x='brans', y='mesai_saati', color='brans',
#                           text_auto='.2s', title="Branş Bazlı Toplam Saat")
#         st.plotly_chart(fig_brans, use_container_width=True)

#     st.divider()

#     # --- ALAN BAZLI DETAYLAR ---
#     st.subheader("🏗️ Alan ve Şirket Bazlı Detaylar")
#     alanlar = filtered_df['alan_adi'].unique()
#     for alan in alanlar:
#         with st.expander(f"📍 {alan} Detay Raporu", expanded=False):
#             alan_df = filtered_df[filtered_df['alan_adi'] == alan]
#             # Şirket ve Branş kırılımında özet tablo
#             alan_ozet = alan_df.groupby(['sirket', 'brans'])['mesai_saati'].sum().reset_index()
#             st.table(alan_ozet)

#     st.divider()

#     # --- İLERLEME ANALİZİ (S-CURVE) ---
#     st.subheader("📈 Kümülatif İlerleme Eğrisi (S-Curve)")
    
#     # Tarih bazlı kümülatif toplamlar
#     daily_total = filtered_df.groupby('tarih')['mesai_saati'].sum().reset_index()
#     daily_total['kumulatif'] = daily_total['mesai_saati'].cumsum()

#     fig_s = make_subplots(specs=[[{"secondary_y": True}]])
    
#     # Günlük Barlar
#     fig_s.add_trace(go.Bar(x=daily_total['tarih'], y=daily_total['mesai_saati'], 
#                            name="Günlük Efor (Saat)", marker_color='lightblue'), secondary_y=False)
    
#     # Kümülatif Çizgi (S-Curve)
#     fig_s.add_trace(go.Scatter(x=daily_total['tarih'], y=daily_total['kumulatif'], 
#                                name="Kümülatif Toplam", line=dict(color='red', width=3)), secondary_y=True)

#     fig_s.update_layout(height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
#     st.plotly_chart(fig_s, use_container_width=True)

#     # --- VERİ TABLOSU ---
#     st.subheader("📋 Detaylı Veri Listesi")
#     st.dataframe(filtered_df, use_container_width=True)

# import streamlit as st
# from database import query_to_df
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import pandas as pd
# from datetime import datetime, timedelta

# # Sayfa Genel Ayarları
# st.set_page_config(page_title="Raporlama ve Analiz", layout="wide")
# st.title("📊 Şantiye Raporlama ve İlerleme Analizi")

# # --- 1. VERİ ÇEKME ---
# query = """
#     SELECT 
#         p.ad_soyad, 
#         s.sirket_adi as sirket, 
#         a.alan_adi, 
#         pk.tarih, 
#         pk.mesai_saati, 
#         pk.aciklama as brans 
#     FROM puantaj_kayitlari pk 
#     JOIN personeller p ON pk.personel_id = p.id 
#     LEFT JOIN sirketler s ON p.sirket_id = s.id 
#     JOIN alanlar a ON pk.alan_id = a.id 
#     ORDER BY pk.tarih ASC
# """
# df = query_to_df(query)

# if df.empty:
#     st.info("📊 Henüz raporlanacak veri bulunmuyor. Lütfen puantaj girişi yapın.")
# else:
#     # Tarih sütununu datetime objesine çeviriyoruz
#     df['tarih'] = pd.to_datetime(df['tarih'])
    
#     # --- 2. SIDEBAR FİLTRELEME ALANI ---
#     st.sidebar.header("🔍 Rapor Filtreleri")
    
#     # A. TARİH ARALIĞI FİLTRESİ
#     min_date = df['tarih'].min().date()
#     max_date = df['tarih'].max().date()
    
#     st.sidebar.subheader("📅 Tarih Aralığı")
#     secilen_tarihler = st.sidebar.date_input(
#         "Rapor Dönemi Seçin",
#         value=(min_date, max_date),
#         min_value=min_date,
#         max_value=max_date
#     )
    
#     # B. ŞİRKET FİLTRESİ
#     st.sidebar.subheader("🏢 Şirket & Branş")
#     sirket_listesi = ["Tümü"] + sorted(df['sirket'].dropna().unique().tolist())
#     secilen_sirket = st.sidebar.selectbox("Şirket Seçin", sirket_listesi)
    
#     # C. BRANŞ FİLTRESİ
#     brans_listesi = ["Tümü"] + sorted(df['brans'].unique().tolist())
#     secilen_brans = st.sidebar.selectbox("Branş Seçin", brans_listesi)

#     # --- 3. VERİYİ FİLTRELEME ---
#     filtered_df = df.copy()
    
#     # Tarih Filtresini Uygula (Başlangıç ve Bitiş seçildiyse)
#     if isinstance(secilen_tarihler, tuple) and len(secilen_tarihler) == 2:
#         start_date, end_date = secilen_tarihler
#         filtered_df = filtered_df[
#             (filtered_df['tarih'].dt.date >= start_date) & 
#             (filtered_df['tarih'].dt.date <= end_date)
#         ]
    
#     # Şirket Filtresini Uygula
#     if secilen_sirket != "Tümü":
#         filtered_df = filtered_df[filtered_df['sirket'] == secilen_sirket]
        
#     # Branş Filtresini Uygula
#     if secilen_brans != "Tümü":
#         filtered_df = filtered_df[filtered_df['brans'] == secilen_brans]

#     # --- 4. ÖZET METRİKLER ---
#     if filtered_df.empty:
#         st.warning("⚠️ Seçilen filtrelere uygun veri bulunamadı.")
#     else:
#         m1, m2, m3, m4 = st.columns(4)
#         total_saat = filtered_df['mesai_saati'].sum()
#         unique_p = filtered_df['ad_soyad'].nunique()
#         unique_s = filtered_df['sirket'].nunique()
        
#         m1.metric("Toplam Efor", f"{total_saat:,.0f} Saat")
#         m2.metric("Aktif Personel", f"{unique_p} Kişi")
#         m3.metric("Çalışan Şirket", f"{unique_s} Firma")
#         m4.metric("Kayıt Sayısı", len(filtered_df))

#         st.divider()

#         # --- GRAFİKLER ---
#         c1, c2 = st.columns(2)
        
#         with c1:
#             st.subheader("🏢 Şirket Dağılımı")
#             s_ozet = filtered_df.groupby('sirket')['mesai_saati'].sum().reset_index()
#             fig_s = px.pie(s_ozet, values='mesai_saati', names='sirket', hole=0.4)
#             st.plotly_chart(fig_s, use_container_width=True)

#         with c2:
#             st.subheader("🛠️ Branş Dağılımı")
#             b_ozet = filtered_df.groupby('brans')['mesai_saati'].sum().reset_index()
#             fig_b = px.bar(b_ozet, x='brans', y='mesai_saati', color='brans')
#             st.plotly_chart(fig_b, use_container_width=True)

#         st.divider()

#         # --- S-CURVE (KÜMÜLATİF ANALİZ) ---
#         st.subheader("📈 Tarih Bazlı İlerleme (S-Curve)")
#         daily = filtered_df.groupby('tarih')['mesai_saati'].sum().reset_index()
#         daily['kumulatif'] = daily['mesai_saati'].cumsum()

#         fig_curve = make_subplots(specs=[[{"secondary_y": True}]])
#         fig_curve.add_trace(go.Bar(x=daily['tarih'], y=daily['mesai_saati'], name="Günlük Saat"), secondary_y=False)
#         fig_curve.add_trace(go.Scatter(x=daily['tarih'], y=daily['kumulatif'], name="Kümülatif", line=dict(color='red', width=3)), secondary_y=True)
#         st.plotly_chart(fig_curve, use_container_width=True)

#         # --- ALAN BAZLI TABLO ---
#         st.subheader("🏗️ Alan Bazlı Efor Özeti")
#         alan_ozet = filtered_df.groupby(['alan_adi', 'sirket', 'brans'])['mesai_saati'].sum().reset_index()
#         st.dataframe(alan_ozet, use_container_width=True)

#         # --- DETAYLI LİSTE ---
#         with st.expander("📋 Ham Veri Listesini Görüntüle"):
#             st.dataframe(filtered_df, use_container_width=True)


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