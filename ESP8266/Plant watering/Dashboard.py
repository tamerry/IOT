import streamlit as st
import requests
import plotly.graph_objects as go
import time
import pandas as pd
import urllib3
import pydeck as pdk

# SSL uyarılarını gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Sayfa Ayarları (Tam ekran, Modern Başlık)
st.set_page_config(page_title="Sera OS Pro", page_icon="🌱", layout="wide", initial_sidebar_state="collapsed")

# --- FIREBASE SABİTLERİ ---
FIREBASE_URL = "https://bitki-sulama-default-rtdb.firebaseio.com"
FIREBASE_AUTH = "qr2pcxY3h8VBGVKAJhoNY83DfsBouyviDmuCHw2h"

# --- PREMIUM CSS TASARIMI ---
st.markdown("""
<style>
    /* Genel Arkaplan */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Üst barları gizle */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Metrik Kartları */
    .kpi-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .kpi-title {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #0f172a;
        font-size: 2.25rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .kpi-status {
        margin-top: 8px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-good { color: #10b981; }
    .status-warn { color: #f59e0b; }
    
    /* Login Ekranı */
    [data-testid="stForm"] {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #f1f5f9;
    }
    
    /* GPS Bekleme Ekranı */
    .gps-loader {
        background: white;
        height: 400px;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 2px dashed #cbd5e1;
        color: #64748b;
    }
    
    /* Harita Konteyneri */
    [data-testid="stDeckGlJsonChart"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Ayarlar Butonu */
    [data-testid="stPopover"] > button {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        color: #334155;
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 600;
        transition: all 0.2s;
    }
    [data-testid="stPopover"] > button:hover {
        background-color: #f1f5f9;
        border-color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# --- GÜVENLİK ---
USERNAME = "admin"
PASSWORD = "123"

if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.cihaz_kodu = ""
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Saat', 'Toprak Nemi', 'Sıcaklık'])

# ==========================================
# 1. GİRİŞ EKRANI
# ==========================================
if not st.session_state.auth:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h1 style='text-align:center; color:#0f172a; font-weight:800; margin-bottom:5px;'>🌱 Sera OS Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#64748b; margin-bottom:30px;'>Sistem Kontrol Paneline Giriş Yapın</p>", unsafe_allow_html=True)
            
            kullanici = st.text_input("Kullanıcı Adı", placeholder="admin")
            sifre = st.text_input("Şifre", type="password", placeholder="••••")
            cihaz_kodu = st.text_input("Cihaz Auth Kodu", placeholder="Örn: SERA-001")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Sisteme Bağlan 🚀", type="primary", use_container_width=True):
                if kullanici == USERNAME and sifre == PASSWORD and cihaz_kodu != "":
                    test_url = f"{FIREBASE_URL}/Cihazlar/{cihaz_kodu}/Veriler.json?auth={FIREBASE_AUTH}"
                    res = requests.get(test_url, verify=False).json()
                    if res is not None:
                        st.session_state.auth = True
                        st.session_state.cihaz_kodu = cihaz_kodu
                        st.rerun()
                    else:
                        st.error("⚠️ Cihaz bulunamadı! Cihazın açık olduğundan emin olun.")
                else:
                    st.error("⚠️ Hatalı giriş bilgileri!")
    st.stop()

# ==========================================
# 2. ANA BULUT EKRANI
# ==========================================
cihaz_kodu = st.session_state.cihaz_kodu

def get_firebase_data(path):
    url = f"{FIREBASE_URL}/Cihazlar/{cihaz_kodu}/{path}.json?auth={FIREBASE_AUTH}"
    try: return requests.get(url, timeout=3, verify=False).json()
    except: return None

def set_firebase_cmd(cmd_node, value):
    url = f"{FIREBASE_URL}/Cihazlar/{cihaz_kodu}/Komutlar.json?auth={FIREBASE_AUTH}"
    requests.patch(url, json={cmd_node: value}, verify=False)

def set_firebase_setting(set_node, value):
    url = f"{FIREBASE_URL}/Cihazlar/{cihaz_kodu}/Ayarlar.json?auth={FIREBASE_AUTH}"
    requests.patch(url, json={set_node: value}, verify=False)

data = get_firebase_data("Veriler")
settings = get_firebase_data("Ayarlar")

current_limit = settings.get("nemSiniri", 30) if settings else 30

# --- ÜST BAŞLIK VE MENÜ (YENİ TASARIM) ---
head_col1, head_col2, head_col3 = st.columns([2, 1, 1])
with head_col1:
    # Başlık ve Badge (Etiket) Yanyana Şık Tasarım
    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 15px; margin-top: -5px;'>
            <h2 style='color:#0f172a; font-weight:800; margin:0; letter-spacing: -0.5px;'>Sera Kontrol</h2>
            <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; box-shadow: 0 2px 10px rgba(59,130,246,0.3); letter-spacing: 1px;'>{cihaz_kodu}</div>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    canli_akis = st.toggle("🔄 Canlı Akış", value=True)
with head_col3:
    with st.popover("⚙️ Sistem Ayarları", use_container_width=True):
        st.markdown("**Sulama Eşiği (%)**")
        new_limit = st.slider("", 0, 100, current_limit, label_visibility="collapsed")
        if st.button("Sınırı Kaydet", use_container_width=True):
            set_firebase_setting("nemSiniri", new_limit)
            st.success("Kaydedildi!")
        st.markdown("---")
        if st.button("🚿 Su Motorunu Çalıştır", use_container_width=True): 
            set_firebase_cmd("manuelPompa", True); st.toast("Emir gönderildi!")
        if st.button("🔄 Cihazı Yeniden Başlat", use_container_width=True): 
            set_firebase_cmd("reset", True); st.toast("Cihaz resetleniyor!")
        st.markdown("---")
        if st.button("🚪 Güvenli Çıkış", type="primary", use_container_width=True): 
            st.session_state.auth = False; st.rerun()

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

if data:
    # --- KPI KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    
    pompa_renk = "#10b981" if data.get('pompaAcik', False) else "#64748b"
    pompa_metin = "AKTİF" if data.get('pompaAcik', False) else "BEKLEMEDE"
    
    c1.markdown(f"""
        <div class="kpi-card border-t-4" style="border-top-color: #f43f5e;">
            <div class="kpi-title">🌡️ İç Sıcaklık</div>
            <div class="kpi-value">{data.get('isi', 0)}<span style="font-size: 1.2rem; color: #94a3b8;"> °C</span></div>
            <div class="kpi-status status-good">Sistem Stabil</div>
        </div>
    """, unsafe_allow_html=True)
    
    c2.markdown(f"""
        <div class="kpi-card border-t-4" style="border-top-color: #3b82f6;">
            <div class="kpi-title">💧 Toprak Nemi</div>
            <div class="kpi-value">{data.get('toprak', 0)}<span style="font-size: 1.2rem; color: #94a3b8;"> %</span></div>
            <div class="kpi-status status-warn">Eşik Değeri: {current_limit}%</div>
        </div>
    """, unsafe_allow_html=True)
    
    c3.markdown(f"""
        <div class="kpi-card border-t-4" style="border-top-color: {pompa_renk};">
            <div class="kpi-title">⚙️ Su Pompası</div>
            <div class="kpi-value" style="color: {pompa_renk}; font-size: 1.8rem; padding-top: 5px;">{pompa_metin}</div>
            <div class="kpi-status" style="color:#64748b;">Son: {data.get('sonSulama', '-')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    c4.markdown(f"""
        <div class="kpi-card border-t-4" style="border-top-color: #8b5cf6;">
            <div class="kpi-title">📡 Sinyal Gücü</div>
            <div class="kpi-value">{data.get('kalite', 0)}<span style="font-size: 1.2rem; color: #94a3b8;"> %</span></div>
            <div class="kpi-status" style="color:#64748b;">IP: {data.get('ip', '-')}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # --- ALT BÖLÜM: HARİTA VE GRAFİK ---
    col_map, col_chart = st.columns([1, 2])

    with col_map:
        st.markdown("<h4 style='color:#334155; font-weight:700; margin-bottom:15px;'>📍 Canlı Lokasyon</h4>", unsafe_allow_html=True)
        lat = data.get('lat', 0.0)
        lng = data.get('lng', 0.0)
        hiz = data.get('hiz', 0.0)
        uydular = data.get('uydular', 0)

        if lat == 0.0 or lng == 0.0:
            st.markdown("""
            <div class="gps-loader">
                <h1 style="font-size: 40px; margin:0; animation: pulse 2s infinite;">🛰️</h1>
                <h3 style="color:#0f172a; margin-top:15px;">Uydu Aranıyor...</h3>
                <p style="text-align:center; font-size:13px; margin-top:5px;">Açık gökyüzü bekleniyor.</p>
            </div>
            <style>@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }</style>
            """, unsafe_allow_html=True)
        else:
            # --- PYDECK HARİTA KONTROLÜ (Nokta Boyutu Düzeltildi) ---
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lng]})
            
            view_state = pdk.ViewState(latitude=lat, longitude=lng, zoom=16, pitch=0)
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position="[lon, lat]",
                get_color="[225, 29, 72, 200]", # Şık bir kırmızı tonu
                get_radius=20, # NOKTAYI KÜÇÜLTTÜK!
                pickable=True,
            )
            st.pydeck_chart(pdk.Deck(
                layers=[layer], 
                initial_view_state=view_state, 
                map_style="light",
                tooltip={"text": "Sera Konumu"}
            ))
            
        # Alt GPS Bilgileri
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; background: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 15px;">
                <div style="text-align: center; width: 50%; border-right: 1px solid #e2e8f0;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase;">Uydular</div>
                    <div style="font-size: 20px; font-weight: 800; color: #0f172a;">{uydular} <span style="font-size:12px; font-weight:normal;">Adet</span></div>
                </div>
                <div style="text-align: center; width: 50%;">
                    <div style="font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase;">Hız</div>
                    <div style="font-size: 20px; font-weight: 800; color: #0f172a;">{hiz} <span style="font-size:12px; font-weight:normal;">km/h</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_chart:
        st.markdown("<h4 style='color:#334155; font-weight:700; margin-bottom:15px;'>📈 Gerçek Zamanlı Akış</h4>", unsafe_allow_html=True)
        
        # Veri geçmişini güncelle
        new_row = pd.DataFrame({'Saat': [data.get('saat', '')], 'Toprak Nemi': [data.get('toprak', 0)], 'Sıcaklık': [data.get('isi', 0)]})
        st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(40)

        # Plotly Grafiği (Daha temiz ve minimalist)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=st.session_state.history['Saat'], y=st.session_state.history['Toprak Nemi'], 
                                 fill='tozeroy', mode='lines+markers', name='Toprak Nemi (%)', 
                                 line=dict(color='#3b82f6', width=3, shape='spline'), fillcolor='rgba(59, 130, 246, 0.1)'))
        fig.add_trace(go.Scatter(x=st.session_state.history['Saat'], y=st.session_state.history['Sıcaklık'], 
                                 mode='lines+markers', name='Sıcaklık (°C)', 
                                 line=dict(color='#f43f5e', width=3, shape='spline')))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=0, r=0, t=10, b=0), 
            xaxis=dict(showgrid=False, showticklabels=False), 
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False), 
            legend=dict(orientation="h", y=1.1, x=0),
            height=460
        )
        
        # Grafik için beyaz kasa
        st.markdown('<div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("⏳ Cihazdan veri bekleniyor... Lütfen ESP8266'nın internete bağlı olduğundan emin olun.")

# Canlı Akış Döngüsü
if canli_akis:
    time.sleep(4)
    st.rerun()