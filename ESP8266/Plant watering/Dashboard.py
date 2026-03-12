from flask import Flask, request, jsonify, make_response
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)

# --- YEREL VERİTABANI VE AYAR KURULUMU ---
DB_NAME = "sera_gecmis.db"
AYAR_DOSYASI = "sera_ayarlar.json"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Eğer tablo ilk defa oluşturuluyorsa bitki_turu sütunuyla birlikte oluşturulur.
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_verileri
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  cihaz_kodu TEXT,
                  kayit_zamani TEXT,
                  cihaz_saati TEXT,
                  isi REAL,
                  nem INTEGER,
                  toprak INTEGER,
                  pompa_durumu INTEGER,
                  lat REAL,
                  lng REAL,
                  bitki_turu TEXT)''')
    
    # Eğer tablo daha önceden varsa (eski sürüm), yeni sütunu eski verileri bozmadan ekleriz.
    try:
        c.execute("ALTER TABLE sensor_verileri ADD COLUMN bitki_turu TEXT")
    except sqlite3.OperationalError:
        pass # Sütun zaten varsa hata verir, hatayı yoksayarız (Geçerli durum)
        
    conn.commit()
    conn.close()

init_db()

# Aynı dakikada birden fazla kayıt atılmasını önlemek için bellek
son_kayitlar = {}

# --- MUAZZAM WEB ARAYÜZÜ (HTML + TAILWIND + JS) ---
# DİKKAT: Python'un JS kodlarını bozmaması için r""" (Raw String) kullanılmıştır.
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sera OS | Profesyonel Kontrol Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .metric-card { background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-3px); }
        .tab-btn.active { color: #059669; border-bottom: 2px solid #059669; }
        
        /* Özel Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="text-slate-800">

    <!-- ================= GİRİŞ EKRANI ================= -->
    <div id="loginScreen" class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
        <div class="bg-white p-8 rounded-3xl shadow-2xl border border-slate-100 max-w-md w-full transform transition-all">
            <div class="text-center mb-8">
                <span class="text-5xl block mb-4">🌱</span>
                <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight">Sera OS Pro</h1>
                <p class="text-slate-500 text-sm mt-2 font-medium">Güvenli Sisteme Giriş</p>
            </div>
            <div class="space-y-5">
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Kullanıcı Adı</label>
                    <input type="text" id="loginUser" value="admin" onkeypress="if(event.key === 'Enter') doLogin()" class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all">
                </div>
                <div>
                    <label class="block text-sm font-bold text-slate-700 mb-2">Şifre</label>
                    <input type="password" id="loginPass" value="123" onkeypress="if(event.key === 'Enter') doLogin()" class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all">
                </div>
                <button id="loginBtn" type="button" onclick="doLogin()" class="w-full bg-slate-900 hover:bg-emerald-600 text-white font-bold py-3.5 px-4 rounded-xl transition-colors shadow-lg mt-4 cursor-pointer">
                    Sisteme Giriş Yap
                </button>
            </div>
        </div>
    </div>

    <!-- ================= ANA UYGULAMA (Giriş Sonrası) ================= -->
    <div id="appScreen" class="hidden min-h-screen flex flex-col">
        
        <!-- Üst Menü -->
        <header class="bg-white border-b border-slate-200 sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <span class="text-2xl">🌱</span>
                    <span class="font-black text-xl tracking-tight text-slate-800">Sera OS</span>
                </div>
                <div class="hidden md:flex gap-6 h-full">
                    <button onclick="switchTab('dashboard')" id="tab-dashboard" class="tab-btn active font-bold px-2 h-full flex items-center transition-colors">📊 Dashboard</button>
                    <button onclick="switchTab('ayarlar')" id="tab-ayarlar" class="tab-btn font-bold px-2 h-full flex items-center text-slate-500 transition-colors">⚙️ Ayarlar</button>
                    <button onclick="switchTab('gecmis')" id="tab-gecmis" class="tab-btn font-bold px-2 h-full flex items-center text-slate-500 transition-colors">🗄️ Veritabanı</button>
                    <button onclick="switchTab('rehber')" id="tab-rehber" class="tab-btn font-bold px-2 h-full flex items-center text-slate-500 transition-colors">📖 Rehber</button>
                </div>
                <div class="flex items-center gap-4">
                    <div class="flex items-center gap-2 bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-full text-xs font-bold border border-emerald-200">
                        <span class="relative flex h-2 w-2"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span></span>
                        Bağlı Cihaz: <span id="headerDeviceCount">0</span>
                    </div>
                    <button onclick="doLogout()" class="text-slate-400 hover:text-rose-500 font-bold text-sm transition-colors">Çıkış 🚪</button>
                </div>
            </div>
            <!-- Mobil Menü (Basit) -->
            <div class="md:hidden flex overflow-x-auto bg-slate-50 border-t border-slate-200 text-sm">
                <button onclick="switchTab('dashboard')" class="px-4 py-3 font-bold text-emerald-600 whitespace-nowrap">Dashboard</button>
                <button onclick="switchTab('ayarlar')" class="px-4 py-3 font-bold text-slate-600 whitespace-nowrap">Ayarlar</button>
                <button onclick="switchTab('gecmis')" class="px-4 py-3 font-bold text-slate-600 whitespace-nowrap">Veritabanı</button>
                <button onclick="switchTab('rehber')" class="px-4 py-3 font-bold text-slate-600 whitespace-nowrap">Rehber</button>
            </div>
        </header>

        <!-- İÇERİK: DASHBOARD -->
        <main id="view-dashboard" class="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-extrabold text-slate-800">📊 Canlı Kontrol Paneli</h2>
            </div>
            
            <div id="noDeviceWarning" class="hidden bg-amber-50 border border-amber-200 text-amber-800 p-6 rounded-2xl text-center">
                <span class="text-3xl block mb-2">⚠️</span>
                <h3 class="font-bold text-lg">Cihaz Bulunamadı</h3>
                <p class="text-sm mt-1">Lütfen önce <b>Ayarlar</b> menüsüne giderek sisteminize cihaz ekleyin.</p>
                <button onclick="switchTab('ayarlar')" class="mt-4 bg-amber-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-amber-700">Ayarlara Git</button>
            </div>

            <!-- Cihazların oluşturulacağı kap -->
            <div id="devicesContainer" class="space-y-10"></div>
        </main>

        <!-- İÇERİK: AYARLAR -->
        <main id="view-ayarlar" class="hidden flex-1 max-w-7xl mx-auto px-4 py-8 w-full space-y-8">
            <h2 class="text-2xl font-extrabold text-slate-800">⚙️ Sistem Ayarları</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- Cihaz Eşleştirme -->
                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">🔗 Cihaz Eşleştirme</h3>
                    <p class="text-sm text-slate-500 mb-6">Sisteme kaç cihaz bağlayacağınızı seçin ve yetkilendirme kodlarını girin.</p>
                    
                    <div class="mb-4">
                        <label class="block text-sm font-bold text-slate-700 mb-2">Cihaz Sayısı</label>
                        <input type="number" id="deviceCountInput" min="1" max="20" value="1" onchange="renderDeviceInputs()" class="w-24 px-3 py-2 border border-slate-300 rounded-lg outline-none focus:border-emerald-500">
                    </div>
                    
                    <div id="deviceInputFields" class="space-y-3 mb-6">
                        <!-- JS ile doldurulacak -->
                    </div>
                    
                    <button onclick="saveDevices()" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl transition-colors">
                        Cihazları Kaydet
                    </button>
                </div>

                <!-- Manuel Kontroller ve Cihaz Ayarları -->
                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-800 mb-2">🎛️ Sistem Kontrolleri</h3>
                    <p class="text-sm text-slate-500 mb-6">Sulama eşiklerini belirleyin, bitkinizi tanımlayın veya manuel müdahale edin.</p>
                    
                    <div class="mb-6">
                        <label class="block text-sm font-bold text-slate-700 mb-2">Kontrol Edilecek Cihaz</label>
                        <select id="controlSelect" onchange="loadDeviceSettings()" class="w-full px-3 py-3 border border-slate-300 rounded-lg outline-none focus:border-emerald-500 bg-slate-50">
                            <!-- JS ile doldurulacak -->
                        </select>
                    </div>

                    <!-- Yeni Ayarlar Bloğu (AI Uyumlu Standart Bitki Türü ve Sınır) -->
                    <div class="p-5 border border-slate-100 rounded-xl bg-slate-50 mb-4">
                        <div class="mb-5">
                            <label class="block text-sm font-bold text-slate-700 mb-2">🪴 Yetiştirilen Bitki Türü</label>
                            <select id="plantInput" class="w-full px-3 py-3 border border-slate-300 rounded-lg outline-none focus:border-emerald-500 bg-white font-medium text-slate-700">
                                <option value="" disabled selected>Standart bir bitki seçin...</option>
                                <optgroup label="🍅 Sebzeler">
                                    <option value="Domates">Domates</option>
                                    <option value="Salatalık">Salatalık</option>
                                    <option value="Biber">Biber</option>
                                    <option value="Patlıcan">Patlıcan</option>
                                    <option value="Kabak">Kabak</option>
                                </optgroup>
                                <optgroup label="🍓 Meyveler">
                                    <option value="Çilek">Çilek</option>
                                    <option value="Kavun">Kavun</option>
                                    <option value="Karpuz">Karpuz</option>
                                    <option value="Limon">Limon Fidanı</option>
                                </optgroup>
                                <optgroup label="🌿 Yeşillik & Otlar">
                                    <option value="Marul">Marul</option>
                                    <option value="Nane">Nane</option>
                                    <option value="Fesleğen">Fesleğen</option>
                                    <option value="Maydanoz">Maydanoz</option>
                                </optgroup>
                                <optgroup label="🌸 Süs & Ev Bitkileri">
                                    <option value="Orkide">Orkide</option>
                                    <option value="Gül">Gül</option>
                                    <option value="Sukulent">Kaktüs / Sukulent</option>
                                    <option value="Monstera">Monstera (Deve Tabanı)</option>
                                </optgroup>
                            </select>
                            <p class="text-xs text-slate-500 mt-2">💡 Seçimler, gelecekteki yapay zeka (AI) verim analizleri için standartlaştırılmıştır.</p>
                        </div>
                        
                        <div class="flex justify-between items-center mb-2">
                            <label class="text-sm font-bold text-slate-700">Otomatik Sulama Eşiği</label>
                            <span id="thresholdVal" class="font-black text-emerald-600">%30</span>
                        </div>
                        <input type="range" id="thresholdSlider" min="0" max="100" value="30" class="w-full accent-emerald-600 mb-4" oninput="document.getElementById('thresholdVal').innerText = '%' + this.value">
                        
                        <button onclick="saveDeviceSettings()" class="w-full bg-emerald-100 text-emerald-700 hover:bg-emerald-200 font-bold py-2 rounded-lg transition-colors">Ayarları Güncelle</button>
                    </div>

                    <div class="p-5 border border-slate-100 rounded-xl bg-slate-50">
                        <label class="block text-sm font-bold text-slate-700 mb-3">Manuel Müdahale</label>
                        <button onclick="sendManualPump()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors shadow-md">
                            🚿 Seçili Cihaza Su Ver
                        </button>
                    </div>
                </div>
            </div>
        </main>

        <!-- İÇERİK: GEÇMİŞ VERİLER (VERİTABANI) -->
        <main id="view-gecmis" class="hidden flex-1 max-w-7xl mx-auto px-4 py-8 w-full space-y-6">
            <div class="flex justify-between items-center mb-2">
                <div>
                    <h2 class="text-2xl font-extrabold text-slate-800">🗄️ Yerel Veritabanı (SQLite)</h2>
                    <p class="text-sm text-slate-500 mt-1">Veriler bilgisayarınıza dakikada bir otomatik kaydedilir.</p>
                </div>
                <div class="flex gap-2">
                    <select id="dbDeviceSelect" class="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"></select>
                    <button onclick="loadDatabase()" class="bg-slate-800 text-white px-4 py-2 rounded-lg font-bold text-sm hover:bg-slate-700">Yenile</button>
                    <button onclick="downloadCSV()" class="bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold text-sm hover:bg-emerald-700">CSV İndir</button>
                </div>
            </div>

            <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                <div class="overflow-x-auto h-[600px]">
                    <table class="w-full text-left text-sm whitespace-nowrap" id="dataTable">
                        <thead class="bg-slate-100 sticky top-0 text-slate-600 font-bold shadow-sm">
                            <tr>
                                <th class="px-4 py-3">ID</th>
                                <th class="px-4 py-3">Sisteme Kayıt</th>
                                <th class="px-4 py-3">Cihaz Saati</th>
                                <th class="px-4 py-3">Bitki Türü</th>
                                <th class="px-4 py-3">Isı (°C)</th>
                                <th class="px-4 py-3">Nem (%)</th>
                                <th class="px-4 py-3">Toprak (%)</th>
                                <th class="px-4 py-3">Pompa</th>
                            </tr>
                        </thead>
                        <tbody id="db-table-body" class="divide-y divide-slate-100 text-slate-700">
                            <tr><td colspan="8" class="text-center py-8 text-slate-400">Veriler yükleniyor...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>

        <!-- İÇERİK: KURULUM REHBERİ -->
        <main id="view-rehber" class="hidden flex-1 max-w-7xl mx-auto px-4 py-8 w-full space-y-6">
            <h2 class="text-2xl font-extrabold text-slate-800 mb-6">📖 Cihaz Kurulum Rehberi</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="space-y-4">
                    <div class="bg-white p-5 rounded-2xl border-l-4 border-blue-500 shadow-sm">
                        <h4 class="font-bold text-slate-800">1. Adım: Cihaza Bağlanın</h4>
                        <p class="text-sm text-slate-600 mt-1">Telefonunuzun Wi-Fi ayarlarına gidin ve <b>'Sera_Kurulum'</b> adlı ağa bağlanın. (Şifre: <code>SeraAdmin123</code>)</p>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border-l-4 border-blue-500 shadow-sm">
                        <h4 class="font-bold text-slate-800">2. Adım: Portalı Açın</h4>
                        <p class="text-sm text-slate-600 mt-1">Bağlandıktan sonra otomatik olarak bir ayar sayfası açılacaktır. (Açılmazsa tarayıcıya 192.168.4.1 yazın).</p>
                    </div>
                    <div class="bg-white p-5 rounded-2xl border-l-4 border-emerald-500 shadow-sm">
                        <h4 class="font-bold text-slate-800">3. Adım: Bilgileri Girin</h4>
                        <p class="text-sm text-slate-600 mt-1">Ev Wi-Fi şifrenizi, Firebase URL'nizi ve cihaz için belirlediğiniz Auth Kodunu girip kaydedin. Sistem otomatik başlayacaktır.</p>
                    </div>
                </div>
                <div class="bg-slate-100 rounded-2xl flex items-center justify-center border border-slate-200 p-6">
                    <div class="text-center text-slate-400">
                        <span class="text-6xl block mb-2">📱</span>
                        <p class="font-bold">Captive Portal</p>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- ================= JAVASCRIPT MANTIĞI ================= -->
    <script>
        // --- Sabit Ayarlar ---
        const FIREBASE_URL = "https://bitki-sulama-default-rtdb.firebaseio.com";
        const FIREBASE_AUTH = "qr2pcxY3h8VBGVKAJhoNY83DfsBouyviDmuCHw2h";
        
        let kayitliCihazlar = [];
        let fetchInterval = null;
        
        // Cihaza özel harita, grafik ve veri depoları
        let mapStore = {};
        let markerStore = {};
        let chartStore = {};
        let dataStore = {};

        // --- 1. GİRİŞ İŞLEMLERİ ---
        function doLogin() {
            const btn = document.getElementById("loginBtn");
            const originalText = btn.innerText;
            btn.innerText = "Yükleniyor... ⏳";
            
            setTimeout(() => {
                const u = document.getElementById("loginUser").value.trim().toLowerCase();
                const p = document.getElementById("loginPass").value.trim();
                
                if(u === "admin" && p === "123") {
                    document.getElementById("loginScreen").classList.add("hidden");
                    document.getElementById("appScreen").classList.remove("hidden");
                    fetchSavedDevices();
                    btn.innerText = originalText;
                } else {
                    alert("HATA: Kullanıcı adı veya şifre yanlış!");
                    btn.innerText = originalText;
                }
            }, 300);
        }

        function doLogout() {
            if(fetchInterval) clearInterval(fetchInterval);
            document.getElementById("appScreen").classList.add("hidden");
            document.getElementById("loginScreen").classList.remove("hidden");
            document.getElementById("loginPass").value = "";
        }

        // --- 2. TAB NAVİGASYONU ---
        function switchTab(tabId) {
            ['dashboard', 'ayarlar', 'gecmis', 'rehber'].forEach(t => {
                document.getElementById('view-' + t).classList.add('hidden');
                const btn = document.getElementById('tab-' + t);
                if(btn) { btn.classList.remove('active', 'text-slate-800'); btn.classList.add('text-slate-500'); }
            });
            
            document.getElementById('view-' + tabId).classList.remove('hidden');
            const actBtn = document.getElementById('tab-' + tabId);
            if(actBtn) { actBtn.classList.add('active'); actBtn.classList.remove('text-slate-500'); }
            
            if(tabId === 'gecmis') { populeDbSelect(); loadDatabase(); }
            if(tabId === 'ayarlar') { renderDeviceInputs(); }
        }

        // --- 3. AYARLAR VE CİHAZ YÖNETİMİ ---
        async function fetchSavedDevices() {
            try {
                const res = await fetch('/api/ayarlar');
                const data = await res.json();
                kayitliCihazlar = data || [];
                document.getElementById("headerDeviceCount").innerText = kayitliCihazlar.length;
                document.getElementById("deviceCountInput").value = kayitliCihazlar.length || 1;
                
                if(kayitliCihazlar.length === 0) {
                    document.getElementById("noDeviceWarning").classList.remove("hidden");
                    switchTab('ayarlar');
                } else {
                    document.getElementById("noDeviceWarning").classList.add("hidden");
                    buildDashboardUI();
                    populateControlSelect();
                    switchTab('dashboard'); 
                }
            } catch (e) { console.error("Ayar çekme hatası", e); }
        }

        function renderDeviceInputs() {
            const count = parseInt(document.getElementById("deviceCountInput").value) || 1;
            const container = document.getElementById("deviceInputFields");
            container.innerHTML = '';
            for(let i=0; i<count; i++) {
                const val = kayitliCihazlar[i] || "";
                container.innerHTML += `<input type="text" id="devInput_${i}" value="${val}" class="w-full px-4 py-2 rounded-lg bg-slate-50 border border-slate-200 outline-none focus:border-emerald-500" placeholder="${i+1}. Cihaz Kodu (Örn: SERA-001)">`;
            }
        }

        async function saveDevices() {
            const count = parseInt(document.getElementById("deviceCountInput").value) || 1;
            let newDevices = [];
            for(let i=0; i<count; i++) {
                const val = document.getElementById(`devInput_${i}`).value.trim();
                if(val && !newDevices.includes(val)) newDevices.push(val);
            }
            if(newDevices.length === 0) return alert("En az 1 geçerli kod girin.");
            
            try {
                await fetch('/api/ayarlar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({cihazlar: newDevices})
                });
                kayitliCihazlar = newDevices;
                document.getElementById("headerDeviceCount").innerText = kayitliCihazlar.length;
                alert("Cihazlar başarıyla kaydedildi!");
                
                document.getElementById("noDeviceWarning").classList.add("hidden");
                buildDashboardUI();
                populateControlSelect();
                switchTab('dashboard');
            } catch(e) { alert("Kaydedilirken hata oluştu!"); }
        }

        // --- 4. KONTROL VE BİTKİ AYARLARI (FIREBASE PATCH) ---
        function populateControlSelect() {
            const sel = document.getElementById("controlSelect");
            sel.innerHTML = '';
            kayitliCihazlar.forEach(c => { sel.innerHTML += `<option value="${c}">${c}</option>`; });
            loadDeviceSettings();
        }

        // Seçilen cihazın hem nem sınırını hem de bitki adını yükler
        function loadDeviceSettings() {
            const dev = document.getElementById("controlSelect").value;
            if(!dev) return;
            fetch(`${FIREBASE_URL}/Cihazlar/${dev}/Ayarlar.json?auth=${FIREBASE_AUTH}`)
                .then(r => r.json()).then(d => {
                    if(d) {
                        if(d.nemSiniri) {
                            document.getElementById("thresholdSlider").value = d.nemSiniri;
                            document.getElementById("thresholdVal").innerText = "%" + d.nemSiniri;
                        }
                        if(d.bitkiAdi) {
                            document.getElementById("plantInput").value = d.bitkiAdi;
                        } else {
                            document.getElementById("plantInput").value = "";
                        }
                    }
                });
        }

        // Hem nem sınırını hem de bitki adını aynı anda Firebase'e kaydeder
        function saveDeviceSettings() {
            const dev = document.getElementById("controlSelect").value;
            const val = document.getElementById("thresholdSlider").value;
            const plant = document.getElementById("plantInput").value.trim();
            
            fetch(`${FIREBASE_URL}/Cihazlar/${dev}/Ayarlar.json?auth=${FIREBASE_AUTH}`, {
                method: 'PATCH', 
                body: JSON.stringify({ nemSiniri: parseInt(val), bitkiAdi: plant })
            }).then(() => alert(`${dev} için ayarlar (Bitki Türü ve Nem Eşiği) güncellendi!`));
        }

        function sendManualPump() {
            const dev = document.getElementById("controlSelect").value;
            fetch(`${FIREBASE_URL}/Cihazlar/${dev}/Komutlar.json?auth=${FIREBASE_AUTH}`, {
                method: 'PATCH', body: JSON.stringify({ manuelPompa: true })
            }).then(() => alert(`${dev} cihazına su verme emri iletildi!`));
        }

        // --- 5. DASHBOARD UI OLUŞTURMA (ÇOKLU CİHAZ) ---
        function buildDashboardUI() {
            const container = document.getElementById("devicesContainer");
            container.innerHTML = '';
            
            if(fetchInterval) clearInterval(fetchInterval);
            mapStore = {}; markerStore = {}; chartStore = {}; dataStore = {};

            kayitliCihazlar.forEach(dev => {
                dataStore[dev] = { labels: [], isi: [], nem: [] };
                
                const html = `
                <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-200">
                    <div class="flex items-center gap-3 mb-6 border-b border-slate-100 pb-4">
                        <div class="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 text-xl">🌿</div>
                        <h3 class="text-xl font-black text-slate-800 flex items-center gap-3">
                            ${dev}
                            <span id="plant-badge-${dev}" class="hidden text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-3 py-1 rounded-full font-bold shadow-sm"></span>
                        </h3>
                    </div>
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div class="metric-card"><div class="text-slate-400 text-xs font-bold uppercase mb-1">🌡️ Sıcaklık</div><div class="text-3xl font-black" id="val-isi-${dev}">--°C</div></div>
                        <div class="metric-card"><div class="text-slate-400 text-xs font-bold uppercase mb-1">💧 Toprak</div><div class="text-3xl font-black text-blue-600" id="val-nem-${dev}">%--</div></div>
                        <div class="metric-card"><div class="text-slate-400 text-xs font-bold uppercase mb-1">⚙️ Pompa</div><div class="text-xl font-black mt-2" id="val-pompa-${dev}">--</div><div class="text-[10px] text-slate-400 mt-1" id="val-son-${dev}">Son: --</div></div>
                        <div class="metric-card"><div class="text-slate-400 text-xs font-bold uppercase mb-1">🛰️ Uydu/Hız</div><div class="text-2xl font-black" id="val-uydu-${dev}">--</div><div class="text-[10px] text-slate-400 mt-1" id="val-hiz-${dev}">0 km/h</div></div>
                    </div>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[300px]">
                        <div class="bg-slate-50 rounded-xl border border-slate-200 p-2 lg:col-span-1 relative z-10"><div id="map-${dev}" class="w-full h-full rounded-lg"></div></div>
                        <div class="bg-slate-50 rounded-xl border border-slate-200 p-4 lg:col-span-2 relative"><canvas id="chart-${dev}"></canvas></div>
                    </div>
                </div>
                `;
                container.innerHTML += html;
            });

            setTimeout(() => {
                kayitliCihazlar.forEach(dev => {
                    initMapFor(dev);
                    initChartFor(dev);
                });
                fetchAllData(); 
                fetchInterval = setInterval(fetchAllData, 4000); 
            }, 100);
        }

        function initMapFor(dev) {
            const m = L.map(`map-${dev}`).setView([0, 0], 2);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(m);
            mapStore[dev] = m;
        }

        function initChartFor(dev) {
            const ctx = document.getElementById(`chart-${dev}`).getContext('2d');
            const c = new Chart(ctx, {
                type: 'line',
                data: { labels: [], datasets: [
                    { label: 'Nem (%)', data: [], borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.1)', fill: true, tension: 0.4 },
                    { label: 'Isı (°C)', data: [], borderColor: '#f43f5e', tension: 0.4 }
                ]},
                options: { responsive: true, maintainAspectRatio: false, animation: { duration: 0 } }
            });
            chartStore[dev] = c;
        }

        // --- 6. VERİ AKIŞI VE VERİTABANI YAZIMI ---
        async function fetchAllData() {
            for(let dev of kayitliCihazlar) {
                try {
                    // Ayarlar (Bitki adı) ve Veriler objesini tek seferde alabilmek için ana düğümü (.json) çekiyoruz
                    const res = await fetch(`${FIREBASE_URL}/Cihazlar/${dev}.json?auth=${FIREBASE_AUTH}`);
                    const fullData = await res.json();
                    
                    if(fullData && fullData.Veriler) {
                        updateDeviceUI(dev, fullData.Veriler, fullData.Ayarlar);
                        
                        // Ayarlardan bitki türünü çekiyoruz. Yoksa "Belirtilmedi" olarak kaydedeceğiz.
                        let bitkiTuru = "Belirtilmedi";
                        if (fullData.Ayarlar && fullData.Ayarlar.bitkiAdi) {
                            bitkiTuru = fullData.Ayarlar.bitkiAdi;
                        }

                        // Sadece sensör verilerini ve bitki türünü SQLite'a yazması için Python'a yolla
                        fetch('/api/kaydet', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                cihaz_kodu: dev, 
                                veri: fullData.Veriler,
                                bitki_turu: bitkiTuru 
                            })
                        });
                    }
                } catch(e) {} 
            }
        }

        function updateDeviceUI(dev, data, ayarlar) {
            // Bitki Rozetini Güncelle
            const badge = document.getElementById(`plant-badge-${dev}`);
            if(badge) {
                if(ayarlar && ayarlar.bitkiAdi) {
                    badge.innerText = "🪴 " + ayarlar.bitkiAdi;
                    badge.classList.remove("hidden");
                } else {
                    badge.classList.add("hidden");
                }
            }

            document.getElementById(`val-isi-${dev}`).innerText = data.isi + "°C";
            document.getElementById(`val-nem-${dev}`).innerText = "%" + data.toprak;
            document.getElementById(`val-pompa-${dev}`).innerHTML = data.pompaAcik ? "<span class='text-emerald-500'>AÇIK 💦</span>" : "<span class='text-slate-400'>KAPALI</span>";
            document.getElementById(`val-son-${dev}`).innerText = "Son: " + (data.sonSulama || "--");
            document.getElementById(`val-uydu-${dev}`).innerText = data.uydular || "0";
            document.getElementById(`val-hiz-${dev}`).innerText = (data.hiz || "0") + " km/h";

            // Harita Güncelle
            if(data.lat !== 0 && data.lng !== 0 && mapStore[dev]) {
                const pos = [data.lat, data.lng];
                if(!markerStore[dev]) { 
                    markerStore[dev] = L.marker(pos).addTo(mapStore[dev]); 
                    mapStore[dev].setView(pos, 16); 
                } else { 
                    markerStore[dev].setLatLng(pos); 
                    mapStore[dev].panTo(pos); 
                }
            }

            // Grafik Güncelle
            let ds = dataStore[dev];
            if(ds.labels.length === 0 || ds.labels[ds.labels.length-1] !== data.saat) {
                ds.labels.push(data.saat); ds.nem.push(data.toprak); ds.isi.push(data.isi);
                if(ds.labels.length > 20) { ds.labels.shift(); ds.nem.shift(); ds.isi.shift(); }
                
                chartStore[dev].data.labels = ds.labels;
                chartStore[dev].data.datasets[0].data = ds.nem;
                chartStore[dev].data.datasets[1].data = ds.isi;
                chartStore[dev].update();
            }
        }

        // --- 7. VERİTABANI GEÇMİŞİ (SQLITE) ---
        function populeDbSelect() {
            const sel = document.getElementById("dbDeviceSelect");
            sel.innerHTML = '<option value="TUMU">Tüm Cihazlar</option>';
            kayitliCihazlar.forEach(c => { sel.innerHTML += `<option value="${c}">${c}</option>`; });
        }

        async function loadDatabase() {
            const dev = document.getElementById("dbDeviceSelect").value;
            const tbody = document.getElementById('db-table-body');
            tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 text-slate-500">Veriler çekiliyor...</td></tr>';
            try {
                const res = await fetch(`/api/gecmis?cihaz=${dev}`);
                const kayitlar = await res.json();
                
                if(kayitlar.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 font-bold text-slate-400">Veritabanında henüz kayıt yok.</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                kayitlar.forEach(row => {
                    // row[10] bitki_turu hücresini temsil eder. (Yoksa '-' yazar)
                    tbody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition-colors">
                            <td class="px-4 py-3 border-b border-slate-100 text-slate-400">#${row[0]}</td>
                            <td class="px-4 py-3 border-b border-slate-100 font-medium">${row[2]}</td>
                            <td class="px-4 py-3 border-b border-slate-100 font-mono text-xs">${row[3]}</td>
                            <td class="px-4 py-3 border-b border-slate-100 font-bold text-emerald-600">${row[10] || '-'}</td>
                            <td class="px-4 py-3 border-b border-slate-100 font-bold text-rose-500">${row[4]}</td>
                            <td class="px-4 py-3 border-b border-slate-100 font-bold text-blue-600">${row[5]}</td>
                            <td class="px-4 py-3 border-b border-slate-100">${row[6]}</td>
                            <td class="px-4 py-3 border-b border-slate-100">${row[7] ? '<span class="bg-emerald-100 text-emerald-700 px-2 py-1 rounded text-xs font-bold">AÇIK</span>' : '<span class="text-slate-400 text-xs font-bold">KAPALI</span>'}</td>
                        </tr>`;
                });
            } catch (e) { tbody.innerHTML = `<tr><td colspan="8" class="text-center text-red-500 py-4">Hata oluştu!</td></tr>`; }
        }

        function downloadCSV() {
            const table = document.getElementById("dataTable");
            let csv = [];
            for (let i = 0; i < table.rows.length; i++) {
                let row = [], cols = table.rows[i].querySelectorAll("td, th");
                for (let j = 0; j < cols.length; j++) row.push(cols[j].innerText);
                csv.push(row.join(","));
            }
            const csvFile = new Blob([csv.join("\n")], {type: "text/csv"});
            const downloadLink = document.createElement("a");
            downloadLink.download = "sera_gecmis_veriler.csv";
            downloadLink.href = window.URL.createObjectURL(csvFile);
            downloadLink.style.display = "none";
            document.body.appendChild(downloadLink);
            downloadLink.click();
        }
    </script>
</body>
</html>
"""

# --- FLASK REST API ENDPOINTLERİ ---

@app.route('/')
def ana_sayfa():
    resp = make_response(HTML_TEMPLATE)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/api/ayarlar', methods=['GET', 'POST'])
def ayarlar_api():
    if request.method == 'POST':
        data = request.json.get('cihazlar', [])
        with open(AYAR_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump({"cihaz_kodlari": data}, f, indent=4)
        return jsonify({"status": "success"})
    else:
        if os.path.exists(AYAR_DOSYASI):
            try:
                with open(AYAR_DOSYASI, 'r', encoding='utf-8') as f:
                    return jsonify(json.load(f).get("cihaz_kodlari", []))
            except Exception:
                pass
        return jsonify([])

@app.route('/api/kaydet', methods=['POST'])
def veri_kaydet():
    req = request.json
    cihaz_kodu = req.get('cihaz_kodu')
    data = req.get('veri')
    bitki_turu = req.get('bitki_turu', 'Belirtilmedi') # JS'den gelen bitki türünü yakala
    
    cihaz_saati = data.get('saat', '')
    if not cihaz_saati or len(cihaz_saati) < 5:
        return jsonify({"status": "error"}), 400
        
    dakika_damgasi = cihaz_saati[:5] 
    
    if son_kayitlar.get(cihaz_kodu) != dakika_damgasi:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # bitki_turu verisini de SQLite'a ekleyerek Insert işlemi
        c.execute('''INSERT INTO sensor_verileri
                     (cihaz_kodu, kayit_zamani, cihaz_saati, isi, nem, toprak, pompa_durumu, lat, lng, bitki_turu)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (cihaz_kodu, su_an, cihaz_saati, data.get('isi'), data.get('nem'), data.get('toprak'),
                   1 if data.get('pompaAcik') else 0, data.get('lat'), data.get('lng'), bitki_turu))
        conn.commit()
        conn.close()
        
        son_kayitlar[cihaz_kodu] = dakika_damgasi
        return jsonify({"status": "saved"})
        
    return jsonify({"status": "ignored"})

@app.route('/api/gecmis', methods=['GET'])
def gecmis_getir():
    cihaz_kodu = request.args.get('cihaz')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if cihaz_kodu and cihaz_kodu != "TUMU":
        c.execute("SELECT * FROM sensor_verileri WHERE cihaz_kodu=? ORDER BY id DESC LIMIT 500", (cihaz_kodu,))
    else:
        c.execute("SELECT * FROM sensor_verileri ORDER BY id DESC LIMIT 500")
        
    veriler = c.fetchall()
    conn.close()
    return jsonify(veriler)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SERA OS PRO - FLASK SUNUCUSU HAZIR!")
    print("👉 Web Tarayıcınızdan şu adresi açın:")
    print("👉 http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)