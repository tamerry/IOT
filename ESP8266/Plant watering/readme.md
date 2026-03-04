🌱 Akıllı Sera OS - Sistem Mimarisi ve DokümantasyonSürüm: v2.0 (Kararlı Sürüm)Bu belge, ESP8266 tabanlı bir IoT donanım düğümü ile Google Firebase bulut altyapısını ve Python tabanlı profesyonel bir web kontrol panelini birleştiren tam otonom akıllı sera sisteminin mimarisini açıklar.🌟 Sistemin Temel Özellikleri💧 Akıllı Sulama: Toprak nemi belirlenen eşik değerinin altına düştüğünde su pompasını otomatik çalıştırır.📍 Konum Takibi: APM GPS modülü ile sistemin bulunduğu konum, bağlı uydu sayısı ve hareket durumu izlenir.☁️ Bulut Kontrolü: Web paneli üzerinden sisteme uzaktan manuel "Su Ver" veya "Reset At" komutları gönderilir.🛜 Kolay Kurulum: Wi-Fi koptuğunda Sera_Kurulum ağı açılır ve koda dokunmadan Wi-Fi/Firebase şifreleri telefondan yenilenir.1. Sistem Akış ŞemasıVerinin sensörlerden çıkıp kullanıcının ekranına ulaşana kadar izlediği yol ve komutların kullanıcıdan seraya nasıl döndüğü aşağıdaki şemada belirtilmiştir:graph TD
    subgraph DONANIM KATMANI (ESP8266 Edge Node)
        A[DHT11 Sensörü] -->|Sıcaklık/Nem| ESP(NodeMCU ESP8266)
        B[Toprak Nem Sensörü] -->|Analog Nem| ESP
        C[DS1302 RTC Modülü] <-->|Sistem Saati| ESP
        ESP -->|Aç/Kapat| D[5V Röle & Su Pompası]
        ESP -->|Durum Gösterimi| E[16x2 I2C LCD Ekran]
    end

    subgraph AĞ VE KURULUM KATMANI
        ESP <..>|İlk Kurulum (Sera_Kurulum WPA2)| F(Akıllı Telefon ile WiFiManager)
        ESP <-->|Kalıcı Bağlantı| G(Ev Wi-Fi Modemi)
    end

    subgraph BULUT KATMANI (Firebase Realtime DB)
        G <-->|SSL / HTTPS Şifreli| H[(Firebase Veritabanı)]
        H -->|Sensör Okumaları| I{.../Veriler}
        H -->|Pompa/Reset Komutları| J{.../Komutlar}
        H -->|Nem Sınırı Değeri| K{.../Ayarlar}
    end

    subgraph SUNUM KATMANI (Python Streamlit Dashboard)
        L[Güvenli Login Ekranı] --> M[Ana Kontrol Paneli]
        M <-->|HTTPS İstekleri| H
        M --> N[Plotly Canlı Grafikler]
        M --> O[Sistem Metrik Kartları]
    end
2. Donanım Bağlantı Şeması (Pinout)NodeMCU DevKit V1 (ESP8266) üzerindeki pinlerin çevresel sensörler ve modüllerle olan eşleşmesi:ESP8266 PiniModül / SensörModül Piniİşlev / NotVIN / 5VRöle & DS1302VCC5V besleme hattı.GNDTüm ModüllerGNDOrtak toprak hattı.3V3DHT11 & Toprak Sens.VCC3.3V besleme hattı.A0 (Analog)Toprak Nem SensörüA0Toprak kuruluğunu ölçer (0-1023).D0 (GPIO16)DS1302 RTCRST (CE)Boot hatasını önlemek için D8'den buraya alındı.D1 (GPIO5)16x2 I2C LCDSCLI2C Saat Sinyali.D2 (GPIO4)16x2 I2C LCDSDAI2C Veri Sinyali.D4 (GPIO2)DHT11 SensörüDATASıcaklık ve hava nemi veri hattı.D5 (GPIO14)5V Röle ModülüIN (Sinyal)Su pompasını tetikleyen pin (LOW Tetiklemeli).D6 (GPIO12)DS1302 RTCCLK (SCLK)Saat modülü saat sinyali.D7 (GPIO13)DS1302 RTCDAT (I/O)Saat modülü veri hattı.D3 (RX)APM Drone GPSTX(9600 Baud) NMEA konum verilerini okur.⚡ Güç Uyarısı: Modüllerin stabil çalışması ve ESP8266'nın resetlenmemesi için sistem PC USB'sinden değil, harici 5V 2A gücünde bir adaptör ile beslenmelidir.3. Çalışma Protokolleri ve GüvenlikA. İlk Kurulum (Provisioning)Cihaz ilk kez fişe takıldığında veya kayıtlı Wi-Fi bulunamadığında Sera_Kurulum AP'si yayar.Kullanıcı ağa SeraAdmin123 şifresi ile katılır (WPA2 korumalı).Captive Portal üzerinden Ev Wi-Fi şifresi, Firebase adresi ve Cihaz Auth Kodu girilir.Bilgiler ESP8266 EEPROM'a yazılır ve cihaz buluta bağlanır.B. Otomatik Sulama DöngüsüDöngü her 4 saniyede bir çalışır.Analog topraktan alınan veri (0-1023), yüzdeye (%0-100) dönüştürülür.Toprak nemi, Firebase'deki nemSiniri değerinin altındaysa röle tetiklenir ve o anki saat kaydedilir.Değer sınıra ulaştığında pompa durdurulur.C. Uzaktan Manuel TetiklemeKullanıcı Python Dashboard'dan "Su Ver" tuşuna basar.Python, Firebase'deki Komutlar/manuelPompa değerini true yapar.ESP8266 komutu görür, pompayı 5 sn çalıştırır.İşlem bittiğinde değeri tekrar false yaparak emri doğrular.D. Veri GüvenliğiKişisel Ağ: Wi-Fi şifresi kodda hardcoded (açık metin) tutulmaz.Bulut İletişimi: HTTP istekleri BearSSL ve TLS 1.2 protokolleri ile şifrelenir.Arayüz: Session-State tabanlı Login ve Cihaz ID doğrulaması kullanır.4. Firebase Veritabanı Yapısı (JSON)ESP8266'nın oluşturduğu ve Python'un okuyup yazdığı standart NoSQL veritabanı yapısı:{
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
        "ip": "192.168.1.103",
        "isi": 24.5,
        "kalite": 85,
        "mac": "A4:CF:12:XX:XX:XX",
        "nem": 45,
        "pompaAcik": false,
        "rssi": -60,
        "saat": "14:30:15",
        "sonSulama": "12:15:00",
        "toprak": 25,
        "lat": 41.0082,
        "lng": 28.9784,
        "hiz": 0.0,
        "uydular": 6
      }
    }
  }
}
