import pandas as pd
import random
from datetime import datetime, timedelta

# 1. Önce personel listesini okuyalım (Az önce oluşturduğumuz dosya)
# Eğer o dosya yoksa, hafızadan 50 ID (1-50 arası) varmış gibi davranacağız
try:
    personel_df = pd.read_excel("tam_otomatik_test_listesi.xlsx")
    personel_ids = list(range(1, 51)) # Veritabanında ID'lerin 1'den başladığını varsayıyoruz
    personel_isimler = personel_df["ad_soyad"].tolist()
    personel_branslar = personel_df["gorev"].tolist()
except:
    personel_ids = list(range(1, 51))
    personel_isimler = [f"Personel {i}" for i in personel_ids]
    personel_branslar = ["Kalıpçı", "Demirci", "İşçi", "Elektrikçi"] * 13

# 2. Parametreler
baslangic_tarihi = datetime.now() - timedelta(days=30)
alan_id = 1 # Veritabanında oluşturduğun ilk alanın ID'si (Genelde 1 olur)
hava_durumlari = ["Güneşli", "Parçalı Bulutlu", "Bulutlu", "Yağmurlu"]

puantaj_verisi = []

# 30 Günlük Döngü
for gun in range(30):
    tarih = baslangic_tarihi + timedelta(days=gun)
    
    # S-Curve mantığı: Günler ilerledikçe çalışan sayısını artıralım
    # İlk günler 5-10 kişi, orta günler 20-25 kişi, son günler 15 kişi
    if gun < 10:
        gunluk_kisi_sayisi = random.randint(8, 12)
    elif gun < 20:
        gunluk_kisi_sayisi = random.randint(18, 25)
    else:
        gunluk_kisi_sayisi = random.randint(12, 18)
    
    # O gün çalışacak kişileri rastgele seç
    calisan_indisleri = random.sample(range(len(personel_ids)), gunluk_kisi_sayisi)
    
    for idx in calisan_indisleri:
        puantaj_verisi.append({
            "personel_id": personel_ids[idx],
            "ad_soyad": personel_isimler[idx],
            "alan_id": alan_id,
            "tarih": tarih.strftime('%Y-%m-%d'),
            "mesai_saati": random.choice([8.0, 8.0, 8.0, 10.0, 12.0]), # Genelde 8, bazen mesai
            "hava_durumu": random.choice(hava_durumlari),
            "brans": personel_branslar[idx],
            "gecikme_nedeni": "Yok"
        })

# 3. Excel'e Kaydet
df_puantaj = pd.DataFrame(puantaj_verisi)
df_puantaj.to_excel("toplu_puantaj_test_verisi.xlsx", index=False)

print(f"✅ {len(df_puantaj)} satırlık test puantajı oluşturuldu: 'toplu_puantaj_test_verisi.xlsx'")