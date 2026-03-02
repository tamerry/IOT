#include <ESP8266WiFi.h>
#include <FirebaseESP8266.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

// --- AYARLAR ---
#define WIFI_SSID "wifi ssid"
#define WIFI_PASSWORD " wifi pass"
#define FIREBASE_HOST "firebase host"
#define FIREBASE_AUTH "firebase secret key"

#define DHTPIN D4
#define SOIL_PIN A0
#define RELAY_PIN D5
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);
ESP8266WebServer server(80);
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

int nemSiniri = 30;
unsigned long sonFirebaseZamani = 0;
bool manuelCalisma = false;

// --- WEB ARAYÜZÜ (SADE VE HIZLI) ---
void handleRoot() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int toprak = map(analogRead(SOIL_PIN), 1023, 300, 0, 100);
  
  if (toprak > 100) toprak = 100;
  if (toprak < 0) toprak = 0;

  String html = "<!DOCTYPE html><html lang='tr'><head><meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>Sera Kontrol Paneli</title>";
  html += "<style>";
  html += "body{font-family:sans-serif; background:#f4f7f6; text-align:center; padding:20px;}";
  html += ".container{max-width:500px; margin:auto; background:white; padding:30px; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);}";
  html += ".box{background:#f9f9f9; padding:20px; border-radius:10px; margin:10px 0; border-left:5px solid #28a745;}";
  html += ".value{font-size:2em; font-weight:bold; color:#333;}";
  html += ".label{color:#666; font-size:1.1em;}";
  html += ".btn{display:block; width:100%; padding:15px; margin:10px 0; border:none; border-radius:8px; font-size:1.1em; cursor:pointer; font-weight:bold; transition:0.2s;}";
  html += ".btn-water{background:#007bff; color:white;}";
  html += ".btn-reset{background:#dc3545; color:white; margin-top:30px; font-size:0.9em; opacity:0.8;}";
  html += ".btn:active{transform:scale(0.98); opacity:0.9;}";
  html += "</style></head><body>";
  html += "<div class='container'>";
  html += "<h1>🌿 Akıllı Sera</h1>";
  html += "<div class='box'><div class='label'>Sıcaklık</div><div class='value'>" + String(t) + " °C</div></div>";
  html += "<div class='box'><div class='label'>Hava Nemi</div><div class='value'>%" + String((int)h) + "</div></div>";
  html += "<div class='box'><div class='label'>Toprak Nemi</div><div class='value'>%" + String(toprak) + "</div></div>";
  html += "<button class='btn btn-water' onclick=\"location.href='/pompaAc'\">🚿 MANUEL SULAMA (5sn)</button>";
  html += "<button class='btn btn-reset' onclick=\"if(confirm('Sistem resetlensin mi?')) location.href='/reset'\">🔄 SİSTEMİ RESETLE</button>";
  html += "<p style='color:#999;'>Veriler 5 saniyede bir güncellenir.</p>";
  html += "</div>";
  html += "<script>setTimeout(function () { location.reload(); }, 5000);</script>";
  html += "</body></html>";

  server.send(200, "text/html", html);
}

// --- RESET FONKSİYONU ---
void handleReset() {
  server.send(200, "text/plain", "Sistem yeniden baslatiliyor... Lutfen 10 saniye bekleyin.");
  delay(1000);
  ESP.restart();
}

// --- POMPA FONKSİYONU ---
void handlePompa() {
  manuelCalisma = true;
  lcd.setCursor(0, 1);
  lcd.print("MANUEL SULAMA...");
  
  digitalWrite(RELAY_PIN, LOW); // Röleyi aç (Aktif Low varsayımı ile)
  delay(5000);
  digitalWrite(RELAY_PIN, HIGH); // Röleyi kapat
  
  manuelCalisma = false;
  server.sendHeader("Location", "/");
  server.send(303);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1);
  lcd.init();
  lcd.backlight();
  dht.begin();
  
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Başlangıçta röle kapalı olsun

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lcd.print("WiFi Baglaniyor");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    lcd.print("."); 
  }

  config.database_url = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);

  lcd.clear(); 
  lcd.print("Baglandi!");
  lcd.setCursor(0, 1); 
  lcd.print(WiFi.localIP().toString());
  delay(3000); 
  lcd.clear();

  server.on("/", handleRoot);
  server.on("/pompaAc", handlePompa);
  server.on("/reset", handleReset);
  server.begin();
}

void loop() {
  server.handleClient();

  if (!manuelCalisma && millis() - sonFirebaseZamani > 3000) {
    sonFirebaseZamani = millis();
    
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int toprak = map(analogRead(SOIL_PIN), 1023, 300, 0, 100);
    
    if (toprak > 100) toprak = 100; 
    if (toprak < 0) toprak = 0; 
    
    // LCD Ekran Güncellemesi
    lcd.setCursor(0, 0);
    lcd.print("T:"); lcd.print((int)t); lcd.print("C H:%"); lcd.print((int)h); lcd.print("   ");
    lcd.setCursor(0, 1);
    lcd.print(" Toprak:%"); lcd.print(toprak); lcd.print("   ");

    // Firebase Güncellemesi
    Firebase.setInt(fbdo, "/Sera/Sicaklik", (int)t); 
    Firebase.setInt(fbdo, "/Sera/ToprakNemi", toprak);
    Firebase.setInt(fbdo, "/Sera/HavaNemi", (int)h); 
    
    // Otomatik Sulama Kontrolü
    if (toprak < nemSiniri) { 
      digitalWrite(RELAY_PIN, LOW); // Röle AÇIK
      lcd.setCursor(12, 1); 
      lcd.print(" ON ");
    } else {
      digitalWrite(RELAY_PIN, HIGH); // Röle KAPALI
      lcd.setCursor(12, 1); 
      lcd.print(" OFF"); 
    } 
  } 
}