# 🌱 Akıllı Sera OS (Smart Greenhouse OS)

![Sürüm](https://img.shields.io/badge/Sürüm-v2.0-blue.svg)
![Platform](https://img.shields.io/badge/Platform-ESP8266-success.svg)
![Veritabanı](https://img.shields.io/badge/Veritabanı-Firebase-orange.svg)

**Akıllı Sera OS**, ESP8266 tabanlı bir mikrodenetleyici kullanarak sera veya saksı bitkilerinin otomatik sulanmasını, ortam değerlerinin ölçülmesini ve GPS üzerinden anlık konum takibini sağlayan **uçtan uca bir IoT (Nesnelerin İnterneti) projesidir.**

Sensör verileri Google Firebase Realtime Database'e senkronize edilir ve uzaktan kontrol edilebilir.

## ✨ Öne Çıkan Özellikler

* 💧 **Otonom Sulama:** Toprak nemi belirlenen eşik değerinin altına düştüğünde su pompasını otomatik olarak çalıştırır.
* 📍 **Canlı GPS Takibi:** APM modülü entegrasyonu ile cihazın (veya taşınabilir seranın) bulunduğu konumu, uydu sayısını ve hareket hızını buluta aktarır.
* ☁️ **Bulut ve Uzaktan Kontrol:** Kullanıcı, Firebase üzerinden (veya entegre Python Dashboard arayüzünden) sulama eşiğini değiştirebilir, manuel su verebilir veya cihaza uzaktan reset atabilir.
* 🛜 **Akıllı WiFi Kurulumu (WiFiManager):** Cihazın kodunu değiştirmeye gerek kalmadan, akıllı telefon üzerinden `Sera_Kurulum` ağına bağlanılarak WiFi ve Firebase şifreleri kolayca yapılandırılabilir.
* 💾 **Kalıcı Hafıza:** Ayarlar EEPROM'a kaydedilir, elektrik kesintilerinde bile cihaz ağı ve Firebase ayarlarını hatırlar.
* ⌚ **RTC (Gerçek Zamanlı Saat):** İnternet bağlantısı olmasa bile DS1302 modülü ile son sulama zamanı gibi kritik veriler doğru şekilde takip edilir.

## 🔌 Kullanılan Donanımlar ve Pin Bağlantıları

Projenin beyni olarak **NodeMCU ESP8266 (DevKit V1)** kullanılmıştır.

| Modül / Sensör | ESP8266 Pini | İşlev / Açıklama |
| :--- | :--- | :--- |
| **DHT11 Sensörü** | `D4` (GPIO2) | Ortam sıcaklığı ve hava nemini ölçer. |
| **Toprak Nem Sensörü** | `A0` (Analog) | Toprağın iletkenliğini okur. |
| **5V Röle (Su Pompası)** | `D5` (GPIO14) | Su motorunu çalıştıran sinyal pini (LOW tetiklemeli). |
| **I2C 16x2 LCD** | `D1`(SCL), `D2`(SDA)| Cihaz üzeri anlık durum ekranı. |
| **DS1302 RTC Saat** | `D7`(DAT), `D6`(CLK), `D0`(RST) | Saat modülü iletişim pinleri. |
| **APM Drone GPS** | `D3` (RX) | (9600 Baud) NMEA konum verilerini okur. |

> ⚠️ **Uyarı:** Donanımların kararlı çalışması için ESP8266 bilgisayar USB'si yerine **harici 5V (min 1A) bir güç kaynağı** ile beslenmelidir.

## 🛠️ Kurulum Adımları

### 1. Arduino IDE ve Kütüphaneler
Arduino IDE'yi açın ve aşağıdaki kütüphanelerin sisteminizde kurulu olduğundan emin olun (Kütüphane Yöneticisinden indirebilirsiniz):
* `Firebase ESP8266 Client` (Mobizt)
* `TinyGPSPlus` (Mikal Hart)
* `WiFiManager` (tzapu)
* `Rtc by Makuna`
* `DHT sensor library` (Adafruit)
* `LiquidCrystal I2C`

### 2. Kodu Yükleme
`sera_node.ino` dosyasını Arduino IDE ile açın.
**ÖNEMLİ:** Kodu karta yüklerken (Upload) `D8` pininin ve GPS'in takılı olduğu `D3` pininin **boş olduğundan** emin olun. Yükleme tamamlandıktan sonra kabloları geri takabilirsiniz.

### 3. Cihazı Ağa Bağlama (Provisioning)
1. Cihaza güç verin. Cihaz kayıtlı bir ağ bulamazsa LCD ekranda "Kurulum Bekleniyor" yazar.
2. Telefonunuzun WiFi ayarlarına gidin ve **Sera_Kurulum** adlı ağa katılın (Şifre: `SeraAdmin123`).
3. Açılan portaldan evinizin WiFi ağını seçin, şifresini girin.
4. Firebase Linkinizi, Firebase Gizli Anahtarınızı ve Cihaz ID'nizi (Örn: `SERA-001`) yazıp **Kaydet** butonuna basın.

## 🌲 Firebase JSON Yapısı

Sistem, verilerini her 4 saniyede bir aşağıdaki NoSQL formatında Firebase'e aktarır:

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
🤝 Katkıda Bulunma
Hata bildirimleri ve çekme istekleri (Pull Requests) kabul edilmektedir. Büyük değişiklikler yapmadan önce lütfen tartışma için bir 'Issue' açın.

📄 Lisans
Bu proje MIT Lisansı altında lisanslanmıştır. Dilediğiniz gibi kullanabilir ve geliştirebilirsiniz.