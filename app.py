import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide")

# ─── ESTILOS CSS (Fondo crema, Sidebar oscura y Cronograma limpio) ──────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
:root { --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --slate: #3D4A5C; --ink: #1A1A2E; }
.stApp { background-color: var(--cream); }

/* SIDEBAR: Forzado de contraste máximo */
[data-testid="stSidebar"] { background-color: #1A1A2E !important; border-right: 1px solid rgba(255,255,255,0.1); }
[data-testid="stSidebar"] * { color: #F7F3EE !important; font-family: 'DM Sans', sans-serif; }
[data-testid="stSidebarNav"] { padding-top: 2rem; }
[data-testid="stSidebar"] .stRadio label { background: rgba(255,255,255,0.05); padding: 5px 10px; border-radius: 5px; margin-bottom: 5px; cursor: pointer; }

/* Tipografía y Hero */
html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }
.hero-box { background-color: var(--slate); padding: 2.5rem; border-radius: 16px; text-align: center; color: white; margin-bottom: 1rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.8rem; color: #FFFFFF; }
.hero-title em { color: #E8C96A; font-style: italic; }
.stats-container { display: flex; justify-content: space-around; background-color: var(--terracotta); padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 600; display: block; }
.stat-lbl { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.9; }

/* Itinerario Visual */
.day-header { background: var(--parchment); padding: 8px 15px; border-radius: 8px; font-weight: 600; margin-top: 25px; color: var(--slate); border-left: 5px solid var(--terracotta); }
.t-row { display: flex; gap: 15px; padding: 12px 0; border-bottom: 1px solid #EDE7DC; }
.t-time { font-size: 0.8rem; color: #6B7A8D; width: 50px; font-weight: 500; flex-shrink: 0; padding-top: 3px; }
.t-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--terracotta); margin-top: 7px; flex-shrink: 0; }
.t-ttl { font-weight: 500; font-size: 1rem; margin-bottom: 2px; }
.t-ttl.star::before { content: '★ '; color: #C9A84C; }
.t-desc { font-size: 0.85rem; color: #555; line-height: 1.5; }
.t-tip { font-size: 0.75rem; color: #8B3E1E; background: rgba(196,105,58,0.08); padding: 6px 12px; border-left: 3px solid var(--terracotta); margin-top: 8px; border-radius: 0 4px 4px 0; }
.btn-maps { text-decoration: none; color: #4285F4; font-size: 0.8rem; font-weight: 500; border: 1px solid #4285F4; padding: 3px 12px; border-radius: 6px; display: inline-block; margin-top: 10px; background: white; }

/* Cards y Presupuesto */
.card-white { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.budget-table th { text-align: left; padding: 10px; background: var(--parchment); color: var(--slate); }
.budget-table td { padding: 10px; border-bottom: 1px solid var(--parchment); }
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

# ─── DATA COMPLETA (20 DÍAS) ──────────────────────────────────────────────────
ITINERARIO = [
    {"city": "🏛️ Milán", "n": 3, "dates": "25–27 Mayo", "days": [
        {"d": "D1", "date": "25 Mayo", "ttl": "Llegada y Navigli", "evs": [{"t": "10:15", "ttl": "Llegada MXP", "desc": "Inmigración.", "maps": "https://maps.app.goo.gl/mxp"}, {"t": "18:00", "ttl": "Navigli", "desc": "Aperol Spritz.", "maps": "https://maps.app.goo.gl/navigli"}]},
        {"d": "D2", "date": "26 Mayo", "ttl": "Duomo y Da Vinci", "evs": [{"t": "08:15", "ttl": "★ LA ÚLTIMA CENA", "desc": "Reserva crítica.", "tip": "⚠️ Reservar hoy.", "maps": "https://maps.app.goo.gl/davinci"}, {"t": "10:30", "ttl": "Duomo", "desc": "Terrazas.", "maps": "https://maps.app.goo.gl/duomo"}]},
        {"d": "D3", "date": "27 Mayo", "ttl": "Brera e Isola", "evs": [{"t": "09:00", "ttl": "Pinacoteca Brera", "desc": "Arte.", "maps": "https://maps.app.goo.gl/brera"}]}
    ]},
    {"city": "🌊 Cinque Terre", "n": 2, "dates": "28–29 Mayo", "days": [
        {"d": "D4", "date": "28 Mayo", "ttl": "Riomaggiore", "evs": [{"t": "12:30", "ttl": "Pueblo Riomaggiore", "desc": "Puerto.", "maps": "https://maps.app.goo.gl/rio"}]},
        {"d": "D5", "date": "29 Mayo", "ttl": "Vernazza", "evs": [{"t": "11:00", "ttl": "Trekking Monterosso", "desc": "3.5km.", "maps": "https://maps.app.goo.gl/vernazza"}]}
    ]},
    {"city": "🌸 Florencia", "n": 4, "dates": "30 Mayo–2 Junio", "days": [
        {"d": "D6", "date": "30 Mayo", "ttl": "Cúpula", "evs": [{"t": "11:00", "ttl": "Cúpula Brunelleschi", "desc": "463 escalones.", "maps": "https://maps.app.goo.gl/cupula"}]},
        {"d": "D7", "date": "31 Mayo", "ttl": "David", "evs": [{"t": "14:00", "ttl": "David Michelangelo", "desc": "Original.", "maps": "https://maps.app.goo.gl/david"}]},
        {"d": "D8", "date": "1 Junio", "ttl": "Jardines", "evs": [{"t": "09:00", "ttl": "Boboli", "desc": "Medici.", "maps": "https://maps.app.goo.gl/boboli"}]},
        {"d": "D9", "date": "2 Junio", "ttl": "Siena", "evs": [{"t": "09:00", "ttl": "Piazza del Campo", "desc": "Excursión.", "maps": "https://maps.app.goo.gl/siena"}]}
    ]},
    {"city": "🏟️ Roma", "n": 4, "dates": "3–6 Junio", "days": [
        {"d": "D10", "date": "3 Junio", "ttl": "Vaticano", "evs": [{"t": "10:30", "ttl": "Museos Vaticanos", "desc": "Capilla Sixtina.", "maps": "https://maps.app.goo.gl/vaticano"}]},
        {"d": "D11", "date": "4 Junio", "ttl": "Coliseo", "evs": [{"t": "08:00", "ttl": "Coliseo + Foro", "desc": "3-4h.", "maps": "https://maps.app.goo.gl/coliseo"}]},
        {"d": "D12", "date": "5 Junio", "ttl": "Borghese", "evs": [{"t": "15:00", "ttl": "Galería Borghese", "desc": "Bernini.", "maps": "https://maps.app.goo.gl/borghese"}]},
        {"d": "D13", "date": "6 Junio", "ttl": "Tarde Libre", "evs": [{"t": "14:00", "ttl": "Shopping Roma", "desc": "Via del Corso."}]}
    ]},
    {"city": "🍕 Nápoles", "n": 1, "dates": "7 Junio", "days": [
        {"d": "D14", "date": "7 Junio", "ttl": "Pompeya", "evs": [{"t": "10:00", "ttl": "Ruinas Pompeya", "desc": "3h.", "maps": "https://maps.app.goo.gl/pompeya"}]}
    ]},
    {"city": "🌅 Amalfi", "n": 2, "dates": "8–9 Junio", "days": [
        {"d": "D15", "date": "8 Junio", "ttl": "Positano", "evs": [{"t": "10:30", "ttl": "Playa Grande", "desc": "Vistas.", "maps": "https://maps.app.goo.gl/positano"}]},
        {"d": "D16", "date": "9 Junio", "ttl": "Sendero", "evs": [{"t": "11:00", "ttl": "Sentiero degli Dei", "desc": "7.8km.", "maps": "https://maps.app.goo.gl/amalfi"}]}
    ]},
    {"city": "🚤 Venecia", "n": 1, "dates": "10 Junio", "days": [
        {"d": "D17", "date": "10 Junio", "ttl": "Canales", "evs": [{"t": "13:00", "ttl": "Vaporetto L1", "desc": "Paseo.", "maps": "https://maps.app.goo.gl/venecia"}]}
    ]},
    {"city": "🇨🇭 Zurich", "n": 3, "dates": "11–13 Junio", "days": [
        {"d": "D18", "date": "11 Junio", "ttl": "Altstadt", "evs": [{"t": "14:00", "ttl": "Casco Viejo", "desc": "Lago Zurich.", "maps": "https://maps.app.goo.gl/zrh1"}]},
        {"d": "D19", "date": "12 Junio", "ttl": "Fondue", "evs": [{"t": "20:00", "ttl": "Swiss Chuchi", "desc": "Cena.", "maps": "https://maps.app.goo.gl/zrh2"}]},
        {"d": "D20", "date": "13 Junio", "ttl": "Uetliberg", "evs": [{"t": "09:00", "ttl": "Montaña Zurich", "desc": "Vistas.", "maps": "https://maps.app.goo.gl/zrh3"}]}
    ]}
]

# ─── INTERFAZ ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ NAVEGACIÓN")
    menu = st.radio("Sección:", ["📍 Itinerario", "🎟️ Reservas", "💰 Presupuesto", "🚄 Transportes", "💡 Tips", "📝 Notas"])
    if menu == "📍 Itinerario":
        st.markdown("---")
        st.markdown("### 🇮🇹 CIUDADES")
        destino = st.radio("Saltar a:", [c["city"] for c in ITINERARIO])

# Hero
st.markdown('<div class="hero-box"><div class="hero-title">Italia & <em>Zurich</em></div><div style="opacity:0.8; font-size:1rem;">Luna de Miel · Mirtha & Adilson · 2026</div></div>', unsafe_allow_html=True)
st.markdown('<div class="stats-container"><div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días</span></div><div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div><div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Italia</span></div><div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Zurich</span></div></div>', unsafe_allow_html=True)

if menu == "📍 Itinerario":
    ciudad = next(c for c in ITINERARIO if c["city"] == destino)
    st.markdown(f"<h2 style='font-family:\"Playfair Display\"; color:#8B3E1E;'>{ciudad['city']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:grey; font-size:0.9rem;'>{ciudad['dates']} · {ciudad['n']} noches</p>", unsafe_allow_html=True)
    for day in ciudad["days"]:
        st.markdown(f'<div class="day-header">{day["d"]} · {day["date"]} — {day["ttl"]}</div>', unsafe_allow_html=True)
        for ev in day["evs"]:
            tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
            maps = f'<a href="{ev["maps"]}" target="_blank" class="btn-maps">📍 Maps</a>' if "maps" in ev else ""
            st.markdown(f'<div class="t-row"><div class="t-time">{ev["t"]}</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip}{maps}</div></div>', unsafe_allow_html=True)

elif menu == "💰 Presupuesto":
    st.markdown("<h2 class='playfair'>Presupuesto Estimado</h2>", unsafe_allow_html=True)
    st.markdown('<div class="card-white"><h4>Total: ~€4.350</h4><p>Promedio por día para 2: €217</p></div>', unsafe_allow_html=True)
    st.table(pd.DataFrame([
        {"Ciudad": "Milán", "Noches": 3, "Total": "€240"}, {"Ciudad": "La Spezia", "Noches": 2, "Total": "€150"},
        {"Ciudad": "Florencia", "Noches": 4, "Total": "€400"}, {"Ciudad": "Roma", "Noches": 4, "Total": "€350"}
    ]))

elif menu == "💡 Tips":
    st.markdown("<h2 class='playfair'>Tips de Oro</h2>", unsafe_allow_html=True)
    st.markdown("- **Café**: En barra €1.20, sentado €4.")
    st.markdown("- **Agua**: Pedir 'rubinetto' (gratis).")
    st.markdown("- **Pádel**: Padel Nuestro Roma tiene pista para probar palas.")

elif menu == "🚄 Transportes":
    st.info("MXP → Centrale: Malpensa Express cada 30 min (€13).")
