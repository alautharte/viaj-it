import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide")

# ─── ESTILOS CSS (Contraste Máximo y Fidelidad al HTML) ────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* Colores Base */
:root { --cream: #F7F3EE; --terracotta: #C4693A; --slate: #3D4A5C; --ink: #1A1A2E; }

/* Fondo de la App */
.stApp { background-color: var(--cream); }

/* BARRA LATERAL - Forzado de contraste */
[data-testid="stSidebar"] {
    background-color: #1A1A2E !important;
}
/* Forzar color de texto en todos los elementos del sidebar */
[data-testid="stSidebar"] *, [data-testid="stSidebar"] label p {
    color: white !important;
    font-family: 'DM Sans', sans-serif;
}

/* Tipografía General */
html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }

/* Hero y Stats */
.hero-box { background-color: var(--slate); padding: 2rem; border-radius: 16px; text-align: center; color: white; margin-bottom: 1rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #FFFFFF; }
.hero-title em { color: #E8C96A; font-style: italic; }
.stats-container { display: flex; justify-content: space-around; background-color: var(--terracotta); padding: 0.8rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
.stat-item { text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 600; display: block; color: white; }
.stat-lbl { font-size: 0.65rem; text-transform: uppercase; opacity: 0.8; color: white; }

/* Timeline Itinerario */
.t-row { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid #EDE7DC; }
.t-time { font-size: 0.75rem; color: #6B7A8D; width: 45px; font-weight: 500; flex-shrink: 0; padding-top: 2px; }
.t-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--terracotta); margin-top: 6px; flex-shrink: 0; }
.t-ttl { font-weight: 500; font-size: 0.92rem; margin-bottom: 2px; }
.t-desc { font-size: 0.82rem; color: #555; line-height: 1.4; }
.t-tip { font-size: 0.75rem; color: #8B3E1E; background: rgba(196,105,58,0.08); padding: 5px 10px; border-left: 3px solid var(--terracotta); margin-top: 5px; border-radius: 0 4px 4px 0; }
.btn-maps { text-decoration: none; color: #4285F4; font-size: 0.75rem; font-weight: 500; border: 1px solid #4285F4; padding: 2px 10px; border-radius: 5px; display: inline-block; margin-top: 8px; background: white; }

/* Ocultar basura de Streamlit */
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── DATOS COMPLETOS (Extraídos de viaje-italia-zurich.html) ──────────────────
ITINERARIO_FULL = [
    {"city": "🏛️ Milán", "range": "D1–3", "days": [
        {"d": "D1", "date": "25 Mayo", "ttl": "Llegada", "evs": [{"t": "10:15", "ttl": "MXP Inmigración", "desc": "Pasaporte argentino.", "maps": "https://maps.app.goo.gl/mPjS8p1mF6XW4vE6A"}]},
        {"d": "D2", "date": "26 Mayo", "ttl": "Cultura", "evs": [{"t": "08:15", "ttl": "★ LA ÚLTIMA CENA", "desc": "RESERVA CRÍTICA.", "tip": "Urgente", "maps": "https://maps.app.goo.gl/0"}, {"t": "10:30", "ttl": "Duomo Terrazas", "desc": "Chapiteles.", "maps": "https://maps.app.goo.gl/18"}]},
        {"d": "D3", "date": "27 Mayo", "ttl": "Brera", "evs": [{"t": "09:00", "ttl": "Pinacoteca di Brera", "desc": "2h.", "maps": "https://maps.app.goo.gl/23"}]}
    ]},
    {"city": "🌊 Cinque Terre", "range": "D4–5", "days": [
        {"d": "D4", "date": "28 Mayo", "ttl": "Costa", "evs": [{"t": "12:30", "ttl": "Riomaggiore", "desc": "Puerto.", "maps": "https://maps.app.goo.gl/25"}]},
        {"d": "D5", "date": "29 Mayo", "ttl": "Trek", "evs": [{"t": "11:00", "ttl": "Vernazza → Monterosso", "desc": "Sendero.", "maps": "https://maps.app.goo.gl/29"}]}
    ]},
    {"city": "🌸 Florencia", "range": "D6–9", "days": [
        {"d": "D6", "date": "30 Mayo", "ttl": "Brunelleschi", "evs": [{"t": "11:00", "ttl": "Cúpula", "desc": "463 escalones.", "maps": "https://maps.app.goo.gl/3"}]},
        {"d": "D7", "date": "31 Mayo", "ttl": "David", "evs": [{"t": "14:00", "ttl": "David Michelangelo", "desc": "Original.", "maps": "https://maps.app.goo.gl/4"}]}
    ]},
    {"city": "🏟️ Roma", "range": "D10–13", "days": [
        {"d": "D11", "date": "4 Junio", "ttl": "Coliseo", "evs": [{"t": "08:00", "ttl": "Coliseo + Foro", "desc": "3-4h.", "maps": "https://maps.app.goo.gl/6"}]},
        {"d": "D12", "date": "5 Junio", "ttl": "Pádel", "evs": [{"t": "18:00", "ttl": "★ Padel Nuestro Roma", "desc": "Probar palas.", "maps": "https://maps.app.goo.gl/42"}]}
    ]},
    {"city": "🍕 Nápoles", "range": "D14", "days": [
        {"d": "D14", "date": "7 Junio", "ttl": "Pompeya", "evs": [{"t": "10:00", "ttl": "Pompeya Scavi", "desc": "3h.", "maps": "https://maps.app.goo.gl/45"}]}
    ]},
    {"city": "🌅 Amalfi", "range": "D15–16", "days": [
        {"d": "D16", "date": "9 Junio", "ttl": "Dioses", "evs": [{"t": "11:00", "ttl": "Sentiero degli Dei", "desc": "7.8km.", "maps": "https://maps.app.goo.gl/51"}]}
    ]},
    {"city": "🚤 Venecia", "range": "D17", "days": [
        {"d": "D17", "date": "10 Junio", "ttl": "San Marcos", "evs": [{"t": "13:00", "ttl": "Gran Canal", "desc": "Vaporetto.", "maps": "https://maps.app.goo.gl/52"}]}
    ]},
    {"city": "🇨🇭 Zurich", "range": "D18–20", "days": [
        {"d": "D19", "date": "12 Junio", "ttl": "Fondue", "evs": [{"t": "20:00", "ttl": "Swiss Chuchi", "desc": "Cena.", "maps": "https://maps.app.goo.gl/60"}]}
    ]}
]

# ─── NAVEGACIÓN (Sidebar) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✈️ MENU")
    seccion = st.radio("Ir a:", ["🗺️ Itinerario", "🎟️ Reservas", "🚄 Transportes", "💰 Gastos", "📝 Notas", "💡 Tips"])
    
    if seccion == "🗺️ Itinerario":
        st.markdown("---")
        st.markdown("### 📍 DESTINOS")
        destino_sel = st.radio("Ciudad:", [c["city"] for c in ITINERARIO_FULL])

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-box">
    <div class="hero-title">Italia & <em>Zurich</em></div>
    <div style="opacity:0.8; font-size:0.9rem;">Mirtha & Adilson · Luna de Miel 2026</div>
</div>
<div class="stats-container">
    <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días</span></div>
    <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
    <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Italia</span></div>
    <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Zurich</span></div>
</div>
""", unsafe_allow_html=True)

# ─── RENDERIZADO ──────────────────────────────────────────────────────────────
if seccion == "🗺️ Itinerario":
    ciudad = next(c for c in ITINERARIO_FULL if c["city"] == destino_sel)
    st.markdown(f"<h2 style='font-family:\"Playfair Display\"; color:#8B3E1E;'>{ciudad['city']}</h2>", unsafe_allow_html=True)
    
    for day in ciudad["days"]:
        st.markdown(f'<div style="background:#EDE7DC; padding:8px 15px; border-radius:8px; font-weight:600; margin-top:20px;">{day["d"]} · {day["date"]} — {day["ttl"]}</div>', unsafe_allow_html=True)
        for ev in day["evs"]:
            tip = f'<div class="t-tip">⚠️ {ev["tip"]}</div>' if "tip" in ev else ""
            maps = f'<a href="{ev["maps"]}" target="_blank" class="btn-maps">📍 Ver en Google Maps</a>' if "maps" in ev else ""
            st.markdown(f"""
            <div class="t-row">
                <div class="t-time">{ev['t']}</div><div class="t-dot"></div>
                <div class="t-content">
                    <div class="t-ttl">{ev['ttl']}</div>
                    <div class="t-desc">{ev['desc']}</div>
                    {tip}{maps}
                </div>
            </div>""", unsafe_allow_html=True)

elif seccion == "💡 Tips":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Tips de Oro</h3>", unsafe_allow_html=True)
    st.markdown("1. **Café**: Parado en barra €1.20, sentado €4.")
    st.markdown("2. **Agua**: Pedir 'rubinetto' (gratis).")
    st.markdown("3. **Pádel**: Probar palas en Padel Nuestro Roma.")
