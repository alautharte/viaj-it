import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide", initial_sidebar_state="collapsed")

# ─── ESTILOS CSS (Fondo claro y estética refinada) ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
:root { --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --slate: #3D4A5C; --ink: #1A1A2E; }
.stApp { background-color: var(--cream); }
html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }
.hero-box { background-color: var(--slate); padding: 2rem; border-radius: 16px; text-align: center; color: var(--cream); margin-bottom: 1rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; margin-bottom: 0.5rem; color: #FFFFFF; }
.hero-title em { color: #E8C96A; font-style: italic; }
.stats-container { display: flex; justify-content: space-around; background-color: var(--terracotta); padding: 0.8rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
.stat-item { text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 600; display: block; }
.stat-lbl { font-size: 0.65rem; text-transform: uppercase; opacity: 0.8; }
.t-row { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--parchment); }
.t-time { font-size: 0.75rem; color: #6B7A8D; width: 45px; font-weight: 500; flex-shrink: 0; padding-top: 2px; }
.t-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--terracotta); margin-top: 6px; flex-shrink: 0; }
.t-ttl { font-weight: 500; font-size: 0.9rem; margin-bottom: 2px; }
.t-desc { font-size: 0.8rem; color: #555; line-height: 1.4; }
.t-tip { font-size: 0.72rem; color: #8B3E1E; background: rgba(196,105,58,0.08); padding: 4px 10px; border-left: 3px solid var(--terracotta); margin-top: 5px; border-radius: 0 4px 4px 0; }
.btn-maps { text-decoration: none; color: #4285F4; font-size: 0.75rem; font-weight: 500; border: 1px solid #4285F4; padding: 2px 8px; border-radius: 5px; display: inline-block; margin-top: 5px; }
.btn-maps:hover { background: #4285F4; color: white; }
.card-white { background: white; padding: 1rem; border-radius: 10px; border: 1px solid var(--parchment); margin-bottom: 0.8rem; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
@st.cache_resource(ttl=300)
def get_sheets():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])

def load_data(name):
    try: return pd.DataFrame(get_sheets().worksheet(name).get_all_records())
    except: return pd.DataFrame()

# ─── DATOS (Restaurados del HTML) ─────────────────────────────────────────────
ITINERARIO = [
    {"city": "Milán", "dates": "25–27 Mayo", "days": [
        {"d": "D1", "date": "25 Mayo", "ttl": "Llegada y Navigli", "events": [
            {"t": "10:15", "ttl": "Llegada MXP", "desc": "Inmigración (30-45 min).", "maps": "https://maps.app.goo.gl/milan_mxp"},
            {"t": "18:00", "ttl": "Aperitivo Navigli", "desc": "Alzaia Naviglio Grande.", "maps": "https://maps.app.goo.gl/navigli"}
        ]},
        {"d": "D2", "date": "26 Mayo", "ttl": "Duomo y Da Vinci", "events": [
            {"t": "08:15", "ttl": "★ LA ÚLTIMA CENA", "desc": "Reserva obligatoria.", "tip": "⚠️ Reservar con meses de antelación.", "maps": "https://maps.app.goo.gl/da_vinci"},
            {"t": "10:30", "ttl": "Duomo Terrazas", "desc": "Vista de los chapiteles.", "maps": "https://maps.app.goo.gl/duomo"}
        ]}
    ]},
    {"city": "Cinque Terre", "dates": "28–29 Mayo", "days": [
        {"d": "D4", "date": "28 Mayo", "ttl": "Pueblos de la Costa", "events": [
            {"t": "12:30", "ttl": "Riomaggiore", "desc": "Puerto fotogénico.", "maps": "https://maps.app.goo.gl/riomaggiore"},
            {"t": "15:30", "ttl": "Manarola", "desc": "Foto icónica.", "maps": "https://maps.app.goo.gl/manarola"}
        ]}
    ]}
    # (Agregá aquí el resto de ciudades siguiendo esta estructura)
]

# ─── INTERFAZ ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="hero-box"><div class="hero-title">Italia & <em>Zurich</em></div><div style="opacity:0.8; font-size:0.9rem;">Mirtha & Adilson · Mayo – Junio 2026</div></div>', unsafe_allow_html=True)
st.markdown('<div class="stats-container"><div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días Totales</span></div><div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div><div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div><div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div></div>', unsafe_allow_html=True)

t_itin, t_res, t_gas = st.tabs(["🗺️ Itinerario", "🎟️ Reservas", "💰 Gastos"])

with t_itin:
    col1, col2 = st.columns([1, 4])
    with col1:
        destino = st.radio("Ciudad:", [c["city"] for c in ITINERARIO], label_visibility="collapsed")
    with col2:
        ciudad = next(c for c in ITINERARIO if c["city"] == destino)
        st.markdown(f"<h3 style='font-family:\"Playfair Display\"; color:#8B3E1E;'>{ciudad['city']}</h3>", unsafe_allow_html=True)
        for day in ciudad["days"]:
            st.markdown(f'<div style="background:#EDE7DC; padding:5px 12px; border-radius:6px; font-weight:500; font-size:0.85rem; margin-top:10px;">{day["d"]} · {day["date"]} — {day["ttl"]}</div>', unsafe_allow_html=True)
            for ev in day["events"]:
                tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
                maps = f'<a href="{ev["maps"]}" target="_blank" class="btn-maps">📍 Maps</a>' if "maps" in ev else ""
                # NOTA: Todo el HTML del evento en una sola línea para evitar el error de código
                st.markdown(f'<div class="t-row"><div class="t-time">{ev["t"]}</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip}{maps}</div></div>', unsafe_allow_html=True)

with t_res:
    st.info("Aquí podés ver y gestionar las reservas críticas.")
    # (Lógica de reservas similar a la anterior)
