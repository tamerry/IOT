# 🌱 SERACORE: ESP8266 Akıllı Sera Donanım Mimarisi

Modern tarım teknolojilerinin temelini oluşturan sensör, mikrokontrolcü ve aktüatör bağlantılarının detaylı topolojik ve elektriksel analizi.

---

## 📊 Sistem Özeti & Temel Metrikler

Akıllı sera projesi, çevresel verileri toplayan ve sulama sistemini otonom olarak yöneten entegre bir IoT (Nesnelerin İnterneti) cihazıdır. Bu mimari; işlem gücünü sağlayan bir ESP8266 NodeMCU, çevresel durumu izleyen iki farklı sensör, veri gösterimi için bir I2C LCD ekran ve fiziksel sulama işlemini tetikleyen bir röle mekanizmasından oluşmaktadır.

* ⚡ **Voltaj Hattı:** 2
* 📡 **Aktif Pin:** 5
* 🔌 **Dış Bileşen:** 5
* 💧 **Aktüatör:** 1

---

## ⚡ Güç Dağılımı (Power Distribution)

Mikrokontrolcü sistemlerinde stabilite, doğru voltaj seviyelerinin sağlanmasına bağlıdır. Bu sistemde bileşenler, ihtiyaç duydukları enerji seviyelerine göre `5V (Vin)` ve `3.3V (3V3)` olmak üzere iki ana gruba ayrılmıştır.

### 🔋 5V (Vin) Hattı
Sistemin ana güç omurgasıdır. Genellikle USB üzerinden alınan gücü doğrudan diğer yüksek güç gerektiren bileşenlere iletir.
* **NodeMCU** (Ana Besleme)
* **I2C LCD Ekran** (Daha parlak görüntü için)
* **Röle Modülü** (Güvenilir anahtarlama için)

### 🔋 3.3V (3V3) Hattı
NodeMCU üzerindeki regülatörden sağlanan, sensörler için optimize edilmiş hassas ve düşük gürültülü güç hattıdır.
* **DHT11 Sıcaklık ve Nem Sensörü**
* **Toprak Nem Sensörü**

---

## 🖧 Pin Haritası ve Veri İletişimi



Sensör verilerinin okunması ve aktüatörlerin kontrol edilmesi için ESP8266 üzerindeki belirli GPIO (Genel Amaçlı Giriş/Çıkış) pinleri kullanılmıştır. 

| Pin | Bileşen | Sinyal Türü & İşlev |
| :---: | :--- | :--- |
| **A0** | Toprak Nem Sensörü | **Analog Giriş:** Topraktaki direnç değişimini voltaja dönüştürür. |
| **D1** | I2C LCD Ekran | **I2C SCL (Saat):** Veri senkronizasyon pini. |
| **D2** | I2C LCD Ekran | **I2C SDA (Veri):** Çift yönlü veri aktarım pini. |
| **D4** | DHT11 Sensörü | **Dijital Giriş:** Tek hat üzerinden sıcaklık ve hava nemi verisi. |
| **D5** | Röle Modülü | **Dijital Çıkış:** Pompayı açıp kapatmak için sinyal gönderir. |

---

## 🔄 Röle ve Pompa Mantıksal Akışı



Su pompasının çalışması, NodeMCU'nun düşük akımlı mantık sinyallerinin röle modülü aracılığıyla yüksek akımlı bir devreye dönüştürülmesiyle sağlanır. Elektriksel akış şu şekildedir:

1.  🔋 **Dış Güç Kaynağı:** Pil veya Adaptör
2.  🎛️ **Röle Modülü:** `COM` (Ortak Giriş) ➡️ `NO` (Normalde Açık Çıkış)
3.  ⛲ **Su Pompası:** Devre tamamlandığında aktifleşir.

> **💡 Çalışma Mantığı:** NodeMCU **D5** pini üzerinden gönderilen sinyal röleyi tetikler. Röle tetiklendiğinde iç anahtar kapanarak **COM** ucundaki elektriği **NO** ucuna aktarır ve su pompası devresini tamamlayarak sulamayı başlatır.

---
*Tasarlanan sistem mimarisi, stabilite ve veri doğruluğunu maksimize edecek şekilde yapılandırılmıştır.*