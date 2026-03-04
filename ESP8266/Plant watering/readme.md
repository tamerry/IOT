# 🌱 Akıllı Sera OS (Smart Greenhouse OS)

![Sürüm](https://img.shields.io/badge/Sürüm-v2.0-blue.svg)  
![Platform](https://img.shields.io/badge/Platform-ESP8266-success.svg)  
![Veritabanı](https://img.shields.io/badge/Veritabanı-Firebase-orange.svg)

**Akıllı Sera OS**, ESP8266 tabanlı bir mikrodenetleyici ile sera veya saksı bitkilerinin otomatik sulanmasını, ortam verilerinin izlenmesini ve GPS üzerinden konum takibini sağlayan **uçtan uca bir IoT (Nesnelerin İnterneti) projesidir.**

Sensör verileri **Google Firebase Realtime Database**’e senkronize edilir ve sistem uzaktan kontrol edilebilir.

---

## ✨ Öne Çıkan Özellikler

- 💧 **Otonom Sulama:**  
  Toprak nemi belirlenen eşik değerinin altına düştüğünde su pompası otomatik olarak çalışır.

- 📍 **Canlı GPS Takibi:**  
  APM modülü entegrasyonu ile cihazın (veya taşınabilir seranın) konumu, uydu sayısı ve hareket hızı buluta aktarılır.

- ☁️ **Bulut Tabanlı Uzaktan Kontrol:**  
  Firebase (veya entegre Python Dashboard) üzerinden:
  - Sulama eşiği değiştirilebilir  
  - Manuel sulama yapılabilir  
  - Cihaza uzaktan reset atılabilir  

- 🛜 **Akıllı WiFi Kurulumu (WiFiManager):**  
  Kod değiştirmeden, telefon üzerinden `Sera_Kurulum` ağına bağlanarak WiFi ve Firebase bilgileri yapılandırılabilir.

- 💾 **Kalıcı Hafıza (EEPROM):**  
  Ayarlar EEPROM’a kaydedilir. Elektrik kesintilerinde WiFi ve Firebase bilgileri korunur.

- ⌚ **RTC (Gerçek Zamanlı Saat):**  
  İnternet bağlantısı olmasa bile DS1302 modülü sayesinde son sulama zamanı gibi kritik bilgiler doğru şekilde takip edilir.

---

## 🔌 Kullanılan Donanımlar ve Pin Bağlantıları

Projenin ana kontrol birimi: **NodeMCU ESP8266 (DevKit V1)**

| Modül / Sensör        | ESP8266 Pini         | Açıklama |
|-----------------------|----------------------|----------|
| DHT11 Sensörü         | `D4` (GPIO2)         | Ortam sıcaklığı ve hava nemi ölçümü |
| Toprak Nem Sensörü    | `A0` (Analog)        | Toprak nem değeri |
| 5V Röle (Su Pompası)  | `D5` (GPIO14)        | Su pompası kontrol pini (LOW tetiklemeli) |
| I2C 16x2 LCD          | `D1` (SCL), `D2` (SDA) | Anlık durum ekranı |
| DS1302 RTC            | `D7` (DAT), `D6` (CLK), `D0` (RST) | Saat modülü bağlantıları |
| APM Drone GPS         | `D3` (RX)            | 9600 baud NMEA veri okuma |

> ⚠️ **Önemli:** Sistem kararlı çalışması için USB yerine **harici 5V (minimum 1A) güç kaynağı** ile beslenmelidir.

---

## 🛠️ Kurulum

### 1️⃣ Arduino IDE ve Kütüphaneler

Aşağıdaki kütüphanelerin kurulu olduğundan emin olun:

- `Firebase ESP8266 Client` – Mobizt  
- `TinyGPSPlus` – Mikal Hart  
- `WiFiManager` – tzapu  
- `Rtc by Makuna`  
- `DHT sensor library` – Adafruit  
- `LiquidCrystal I2C`  

---

### 2️⃣ Kodu Yükleme

1. `sera_node.ino` dosyasını Arduino IDE’de açın.
2. Kart seçimi: **NodeMCU 1.0 (ESP-12E Module)**
3. Yükleme sırasında:
   - `D8` pini boş olmalı  
   - GPS bağlı olan `D3` pini boş olmalı  

Yükleme tamamlandıktan sonra kabloları tekrar bağlayabilirsiniz.

---

### 3️⃣ İlk Kurulum (Provisioning)

1. Cihaza güç verin.  
2. Kayıtlı ağ yoksa LCD ekranda **“Kurulum Bekleniyor”** yazar.
3. Telefonunuzdan WiFi ayarlarına girin.
4. **Sera_Kurulum** ağına bağlanın.  
   - Şifre: `SeraAdmin123`
5. Açılan yapılandırma ekranında:
   - WiFi ağınızı seçin  
   - WiFi şifrenizi girin  
   - Firebase URL  
   - Firebase Secret Key  
   - Cihaz ID (örn: `SERA-001`)  

Kaydet butonuna basın.

---

## 🌲 Firebase JSON Veri Yapısı

Sistem verileri her **4 saniyede bir** aşağıdaki formatta Firebase’e gönderilir:

```json
{
  "Cihazlar": {
    "SERA-001": {
      "Ayarlar": {
        "nemSiniri": 30
      },
      "Komutlar": {
        "manuelPompa": false,
        "reset": false
      },
      "Veriler": {
        "ip": "192.168.1.X",
        "isi": 24.5,
        "nem": 45,
        "toprak": 25,
        "lat": 41.0082,
        "lng": 28.9784,
        "hiz": 0.0,
        "uydular": 6,
        "pompaAcik": false,
        "saat": "14:30:15",
        "sonSulama": "12:15:00"
      }
    }
  }
}
```
## 🤝 Katkıda Bulunma

Hata bildirimleri ve Pull Request’ler memnuniyetle kabul edilir.

Büyük değişiklikler öncesinde lütfen bir Issue açarak tartışma başlatın.

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.
Serbestçe kullanabilir, değiştirebilir ve geliştirebilirsiniz.