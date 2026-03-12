#include <EEPROM.h>
#include <ThreeWire.h>
#include <RtcDS1302.h>
#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include <WiFiManager.h>
#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>

// --- DONANIM PİN TANIMLARI ---

// 1. RTC Saat Modülü Pinleri
ThreeWire myWire(D7, D6, D0); // DAT(D7), CLK(D6), RST(D0)
RtcDS1302<ThreeWire> Rtc(myWire);

// 2. Sensör ve Röle Pinleri
#define DHTPIN D4
#define DHTTYPE DHT11
#define SOIL_PIN A0
#define RELAY_PIN D5

// 3. APM GPS Modülü Pinleri
static const int RXPin = D3;          // GPS TX kablosu (Veri Gönderen) buraya takılacak
static const int TXPin = D8;          // (Yükleme hatası vermemesi için boş bırakın)
static const uint32_t GPSBaud = 9600; // Eski modüller için düzeltilmiş hız!

// --- NESNELER ---
TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// --- KALICI HAFIZA (EEPROM) ---
char firebaseHost[100] = "";
char firebaseAuth[60] = "";
char cihazKodu[20] = "SERA-001";
bool ayarlariKaydet = false;

// --- SİSTEM DEĞİŞKENLERİ ---
int nemSiniri = 30;
unsigned long sonDonguZamani = 0;
bool oncekiPompa = false;
String sonSulama = "Henuz Yok";

String yol_komut_pompa, yol_komut_reset, yol_ayar_sinir, yol_veriler;

// WiFiManager Tetikleyici
void ayarKaydetCallback()
{
  ayarlariKaydet = true;
}

// Saat Fonksiyonu
String getTimeString()
{
  RtcDateTime now = Rtc.GetDateTime();
  char buf[10];
  snprintf(buf, sizeof(buf), "%02u:%02u:%02u", now.Hour(), now.Minute(), now.Second());
  return String(buf);
}

void setup()
{
  Serial.begin(115200);

  // 1. GPS BAŞLAT
  ss.begin(GPSBaud);
  Serial.println(F("\nGPS Modulu Bekleniyor..."));

  // 2. ÇEVRE BİRİMLERİ
  Wire.begin(D2, D1);
  lcd.init();
  lcd.backlight();
  dht.begin();
  pinMode(RELAY_PIN, INPUT); // Röle varsayılan Kapalı (LOW)

  // 3. RTC SAAT MODÜLÜ BAŞLAT
  Rtc.Begin();
  if (!Rtc.IsDateTimeValid())
  {
    Rtc.SetDateTime(RtcDateTime(__DATE__, __TIME__));
  }
  if (Rtc.GetIsWriteProtected())
  {
    Rtc.SetIsWriteProtected(false);
  }
  if (!Rtc.GetIsRunning())
  {
    Rtc.SetIsRunning(true);
  }

  // 4. EEPROM'DAN AYARLARI OKU
  EEPROM.begin(512);
  if (EEPROM.read(0) == 'X')
  {
    EEPROM.get(1, firebaseHost);
    EEPROM.get(105, firebaseAuth);
    EEPROM.get(170, cihazKodu);
  }
  EEPROM.end();

  // 5. WIFIMANAGER (KURULUM PORTALI)
  lcd.clear();
  lcd.print("Kurulum Bekleniyor");
  lcd.setCursor(0, 1);
  lcd.print("Aga Baglanin...");

  WiFiManagerParameter custom_host("host", "Firebase Linki (https:// haric)", firebaseHost, 100);
  WiFiManagerParameter custom_auth("auth", "Firebase Gizli Anahtari", firebaseAuth, 60);
  WiFiManagerParameter custom_kodu("kodu", "Cihaz Auth Kodu (Orn: SERA-1)", cihazKodu, 20);

  WiFiManager wifiManager;
  wifiManager.setSaveConfigCallback(ayarKaydetCallback);

  wifiManager.addParameter(&custom_host);
  wifiManager.addParameter(&custom_auth);
  wifiManager.addParameter(&custom_kodu);

  if (!wifiManager.autoConnect("Sera_Kurulum", "SeraAdmin123"))
  {
    Serial.println("Baglanti hatasi!");
    delay(3000);
    ESP.restart();
  }

  // 6. YENİ AYAR GİRİLDİYSE KAYDET
  if (ayarlariKaydet)
  {
    strcpy(firebaseHost, custom_host.getValue());
    strcpy(firebaseAuth, custom_auth.getValue());
    strcpy(cihazKodu, custom_kodu.getValue());

    EEPROM.begin(512);
    EEPROM.write(0, 'X');
    EEPROM.put(1, firebaseHost);
    EEPROM.put(105, firebaseAuth);
    EEPROM.put(170, cihazKodu);
    EEPROM.commit();
    EEPROM.end();
  }

  lcd.clear();
  lcd.print("WiFi Baglandi!");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());
  delay(2000);

  // 7. FIREBASE BAĞLANTISI
  yol_komut_pompa = "/Cihazlar/" + String(cihazKodu) + "/Komutlar/manuelPompa";
  yol_komut_reset = "/Cihazlar/" + String(cihazKodu) + "/Komutlar/reset";
  yol_ayar_sinir = "/Cihazlar/" + String(cihazKodu) + "/Ayarlar/nemSiniri";
  yol_veriler = "/Cihazlar/" + String(cihazKodu) + "/Veriler";

  config.database_url = firebaseHost;
  config.signer.tokens.legacy_token = firebaseAuth;
  Firebase.begin(&config, &auth);

  lcd.clear();
  lcd.print("Bulut Hazir!");
  lcd.setCursor(0, 1);
  lcd.print("Kod: ");
  lcd.print(cihazKodu);
  delay(3000);
  lcd.clear();
}

void loop()
{

  // --- A. GPS VERİLERİNİ KESİNTİSİZ OKUMA ---
  while (ss.available() > 0)
  {
    gps.encode(ss.read());
  }

  // --- B. ANA DÖNGÜ (Her 4 Saniyede Bir Çalışır) ---
  if (millis() - sonDonguZamani > 4000)
  {
    sonDonguZamani = millis();

    // 1. BULUTTAN KOMUT DİNLE (Hata Çözümü: .c_str() kaldırıldı)
    if (Firebase.getBool(fbdo, yol_komut_pompa))
    {
      if (fbdo.boolData() == true)
      {
        lcd.setCursor(0, 1);
        lcd.print("BULUT SULAMA!   ");
        pinMode(RELAY_PIN, OUTPUT);
        digitalWrite(RELAY_PIN, LOW);
        delay(5000);
        pinMode(RELAY_PIN, INPUT);
        sonSulama = getTimeString();
        Firebase.setBool(fbdo, yol_komut_pompa, false);
      }
    }

    if (Firebase.getBool(fbdo, yol_komut_reset))
    {
      if (fbdo.boolData() == true)
      {
        Firebase.setBool(fbdo, yol_komut_reset, false);
        ESP.restart();
      }
    }

    if (Firebase.getInt(fbdo, yol_ayar_sinir))
    {
      nemSiniri = fbdo.intData();
    }

    // 2. SENSÖRLERİ OKUMA
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (isnan(h))
      h = 0;
    if (isnan(t))
      t = 0;

    // Toprak sensörü genelde kuruyken 1023, ıslakken 300 verir. Tersi ise ilk iki rakamı (0, 1023) yapın.
    int toprak = map(analogRead(SOIL_PIN), 1023, 300, 0, 100);
    if (toprak > 100)
      toprak = 100;
    if (toprak < 0)
      toprak = 0;

    int dbm = WiFi.RSSI();
    int wifiKalite = (dbm <= -100) ? 0 : ((dbm >= -50) ? 100 : 2 * (dbm + 100));

    // Otomatik Sulama Kararı
    bool anlikPompa = (toprak < nemSiniri);
    if (anlikPompa && !oncekiPompa)
      sonSulama = getTimeString();
    oncekiPompa = anlikPompa;

    // 3. GPS VERİLERİNİ HAZIRLAMA
    double enlem = 0.0;
    double boylam = 0.0;
    double gpsHiz = 0.0;
    int uydular = 0;

    if (gps.location.isValid())
    {
      enlem = gps.location.lat();
      boylam = gps.location.lng();
      gpsHiz = gps.speed.kmph();
      uydular = gps.satellites.value();
    }

    // 4. LCD EKRANI GÜNCELLEME
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print((int)t);
    lcd.print("C H:");
    lcd.print((int)h);
    lcd.print("% ");
    lcd.setCursor(0, 1);
    lcd.print("Toprak:%");
    lcd.print(toprak);
    lcd.print("   ");
    if (anlikPompa)
    {
      pinMode(RELAY_PIN, OUTPUT);
      digitalWrite(RELAY_PIN, LOW);
      lcd.setCursor(12, 1);
      lcd.print(" ON ");
    }
    else
    {
      pinMode(RELAY_PIN, INPUT);
      lcd.setCursor(12, 1);
      lcd.print(" OFF");
    }

    // 5. BULUTA VERİ YAZMA (Hata Çözümü: .c_str() kaldırıldı)
    FirebaseJson fbJson;
    fbJson.set("isi", t);
    fbJson.set("nem", (int)h);
    fbJson.set("toprak", toprak);
    fbJson.set("saat", getTimeString());
    fbJson.set("sonSulama", sonSulama);
    fbJson.set("pompaAcik", anlikPompa);
    fbJson.set("ip", WiFi.localIP().toString());
    fbJson.set("mac", WiFi.macAddress());
    fbJson.set("rssi", dbm);
    fbJson.set("kalite", wifiKalite);
    fbJson.set("lat", enlem);
    fbJson.set("lng", boylam);
    fbJson.set("hiz", gpsHiz);
    fbJson.set("uydular", uydular);

    Firebase.setJSON(fbdo, yol_veriler, fbJson);
  }
}