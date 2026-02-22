import pandas as pd
import random

isimler = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Murat", "Ömer", "İbrahim", "Hüseyin", "Yusuf", "Osman", "Can", "Eren", "Hasan", "Salih"]
soyisimler = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Arslan", "Doğan", "Aydın", "Öztürk", "Kılıç", "Koç", "Özkan"]
gorevler = ["Kalıpçı", "Demirci", "Betoncu", "Elektrikçi", "Tesisatçı", "İşçi"]
sirketler = ["Alfa İnşaat", "Beta Yapı", "Gama Enerji"]

unique_names = set()
while len(unique_names) < 50:
    unique_names.add(f"{random.choice(isimler)} {random.choice(soyisimler)}")

data = []
for i, name in enumerate(list(unique_names)):
    data.append({
        "ad_soyad": name,
        "tc_no": str(30000000000 + i),
        "telefon": f"0500{1000000 + i}",
        "gorev": random.choice(gorevler),
        "sirket": random.choice(sirketler),
        "kan_grubu": random.choice(["A+", "B+", "0+"]),
        "dogum_tarihi": "1990-01-01"
    })

pd.DataFrame(data).to_excel("tam_otomatik_test_listesi.xlsx", index=False)
print("✅ 50 Benzersiz Personel Dosyası Hazır.")