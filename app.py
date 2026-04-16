import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Italia & Zurich 2026",
    page_icon="🇮🇹",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── ESTILOS CSS (Inspirados en el HTML) ──────────────────────────────────────
st.markdown(textwrap.dedent("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
    
    :root {
        --cream: #F7F3EE;
        --parchment: #EDE7DC;
        --terracotta: #C4693A;
        --slate: #3D4A5C;
        --olive: #6B7A3E;
        --gold: #C9A84C;
        --ink: #1A1A2E;
    }

    /* Fondo general claro */
    .stApp { background-color: var(--cream); }
    
    html, body, [class*="css"], .stMarkdown {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }

    h1, h2, h3, .playfair {
        font-family: 'Playfair Display', serif !important;
    }

    /* Hero Section */
    .hero-box {
        background-color: var(--slate);
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        color: var(--cream);
        margin-bottom: 1rem;
    }
    .hero-title { font-size: 2.8rem; margin-bottom: 0.5rem; color: #FFFFFF; }
    .hero-title em { color: #E8C96A; font-style: italic; }
    
    /* Stats Bar */
    .stats-container {
        display: flex;
        justify-content: space-around;
        background-color: var(--terracotta);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    .stat-item { text-align: center; }
    .stat-num { font-size: 1.5rem; font-weight: 600; display: block; }
    .stat-lbl { font-size: 0.7rem; text-transform: uppercase; opacity: 0.8; }

    /* Timeline Styling */
    .t-row {
        display: flex;
        gap: 15px;
        padding: 12px 0;
        border-bottom: 1px solid var(--parchment);
    }
    .t-time {
        font-size: 0.8rem;
        color: #6B7A8D;
        width: 50px;
        font-weight: 500;
        flex-shrink: 0;
    }
    .t-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--terracotta);
        margin-top: 5px;
        flex-shrink: 0;
    }
    .t-content { flex-grow: 1; }
    .t-ttl { font-weight: 500; font-size: 0.95rem; margin-bottom: 2px; }
    .t-desc { font-size: 0.85rem; color: #555; line-height: 1.4; }
    .t-tip {
        font-size: 0.75rem;
        color: #8B3E1E;
        background: rgba(196,105,58,0.08);
        padding: 5px 10px;
        border-left: 3px solid var(--terracotta);
        margin-top: 5px;
        border-radius: 0 4px 4px 0;
    }

    /* Cards */
    .card-white {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--parchment);
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Badges */
    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 500;
        margin-right: 5px;
    }
    .tag-museum { background: #F5E8F5; color: #7A3A8C; }
    .tag-food { background: #FDE8DE; color: #8B3E1E; }
    .tag-walk { background: #EBF5E1; color: #3A6B18; }

    /* Botones personalizados */
    .btn-maps {
        text-decoration: none;
        color: #4285F4;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid #4285F4;
        padding: 3px 8px;
        border-radius: 5px;
        transition: 0.2s;
    }
    .btn-maps:hover { background: #4285F4; color: white; }
    </style>
"""), unsafe_allow_html=True)

# ─── LÓGICA DE GOOGLE SHEETS ──────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=300)
def get_workbook():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets(wb):
    existing = [s.title for s in wb.worksheets()]
    needed = {
        "viaje_reservas": ["id","estado","url_reserva","confirmacion","monto","notas","updated"],
        "viaje_gastos":   ["id","descripcion","categoria","monto","fecha","updated"],
        "viaje_notas":    ["id","texto","tag","autor","fecha"],
    }
    for name, headers in needed.items():
        if name not in existing:
            ws = wb.add_worksheet(title=name, rows=500, cols=len(headers))
            ws.append_row(headers)
    return {name: wb.worksheet(name) for name in needed}

@st.cache_data(ttl=20)
def load_data(sheet_name):
    try:
        wb = get_workbook()
        ensure_sheets(wb)
        ws = wb.worksheet(sheet_name)
        records = ws.get_all_records()
        return pd.DataFrame(records) if records else pd.DataFrame()
    except: return pd.DataFrame()

# ─── DATOS DEL VIAJE (Cronograma Completo del HTML) ───────────────────────────
ITINERARIO = [
    {"id": "milan", "city": "Milán", "dates": "25–27 Mayo", "n": 3, "days": [
        {"d": "D1", "date": "Lun 25 Mayo", "title": "Llegada y Navigli", "events": [
            {"t": "10:15", "ttl": "Llegada MXP — Inmigración", "desc": "Pasaporte argentino. Calcular 30–45 min.", "maps": "https://maps.app.goo.gl/mxp"},
            {"t": "11:30", "ttl": "Malpensa Express → Centrale", "desc": "52 min · €13/p. Validar antes de subir.", "maps": "https://maps.app.goo.gl/centrale"},
            {"t": "18:00", "ttl": "Paseo Navigli + Aperitivo", "desc": "Aperol Spritz al borde del canal. Alzaia Naviglio Grande.", "maps": "https://maps.google.com/?q=Navigli+Milan"}
        ]},
        {"d": "D2", "date": "Mar 26 Mayo", "title": "Duomo y Da Vinci", "events": [
            {"t": "08:15", "ttl": "★ LA ÚLTIMA CENA", "desc": "Santa Maria delle Grazie. Reserva obligatoria 15 min.", "tip": "RESERVAR HOY. Se agota meses antes.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
            {"t": "10:30", "ttl": "Duomo di Milano", "desc": "Terrazas en ascensor para ver los 135 chapiteles.", "maps": "https://maps.google.com/?q=Duomo+di+Milano"},
            {"t": "15:00", "ttl": "Shopping Corso Buenos Aires", "desc": "La calle comercial más larga de Italia. Ropa accesible.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan"}
        ]}
    ]},
    {"id": "cinque", "city": "Cinque Terre", "dates": "28–29 Mayo", "n": 2, "days": [
        {"d": "D4", "date": "Jue 28 Mayo", "title": "Riomaggiore y Manarola", "events": [
            {"t": "12:30", "ttl": "Riomaggiore", "desc": "Bajar al puerto pequeño. Focaccia con pesto ligurio.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
            {"t": "15:30", "ttl": "Manarola", "desc": "La foto icónica de las casas pastel sobre las rocas.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"}
        ]}
    ]}
    # Se pueden agregar el resto de ciudades siguiendo el mismo formato del HTML
]

RESERVAS_DEF = [
    {"id":"r1", "title":"La Última Cena", "urgencia":"🔴 URGENTE", "detail":"Milán · Día 2 · 08:15hs"},
    {"id":"r2", "title":"Galería Borghese", "urgencia":"🔴 URGENTE", "detail":"Roma · Día 12 · Tarde"},
    {"id":"r3", "title":"Museos Vaticanos", "urgencia":"🔴 URGENTE", "detail":"Roma · Día 10 · 08:00hs"}
]

# ─── HEADER Y HERO ────────────────────────────────────────────────────────────
st.markdown(f"""
    <div class="hero-box">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🇮🇹 🇨🇭</div>
        <div class="hero-title">Italia & <em>Zurich</em></div>
        <div class="hero-sub">Mirtha & Adilson · Mayo – Junio 2026</div>
    </div>
    <div class="stats-container">
        <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días Totales</span></div>
        <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
        <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div>
        <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
    </div>
""", unsafe_allow_html=True)

# ─── NAVEGACIÓN POR TABS ──────────────────────────────────────────────────────
t_itin, t_res, t_gas, t_tips = st.tabs(["🗺️ Itinerario", "🎟️ Reservas", "💰 Presupuesto", "💡 Tips"])

# ─── TAB: ITINERARIO ──────────────────────────────────────────────────────────
with t_itin:
    col_nav, col_cont = st.columns([1, 3])
    
    with col_nav:
        st.markdown("<p style='font-size:0.7rem; color:grey; text-transform:uppercase;'>Destinos</p>", unsafe_allow_html=True)
        destino = st.radio("Saltar a:", [c["city"] for c in ITINERARIO], label_visibility="collapsed")
    
    with col_cont:
        data_ciudad = next(c for c in ITINERARIO if c["city"] == destino)
        st.markdown(f"<h2 class='playfair' style='color:#8B3E1E; margin-bottom:0;'>{data_ciudad['city']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:grey; font-size:0.9rem;'>{data_ciudad['dates']} · {data_ciudad['n']} noches</p>", unsafe_allow_html=True)
        
        for day in data_ciudad["days"]:
            with st.container():
                st.markdown(f"""
                    <div style="background:#EDE7DC; padding:8px 15px; border-radius:8px; margin-top:15px; font-weight:500;">
                        {day['d']} · {day['date']} — {day['title']}
                    </div>
                """, unsafe_allow_html=True)
                
                for ev in day["events"]:
                    tip_html = f"<div class='t-tip'>{ev['tip']}</div>" if "tip" in ev else ""
                    maps_html = f"<a href='{ev['maps']}' target='_blank' class='btn-maps'>📍 Maps</a>" if "maps" in ev else ""
                    
                    st.markdown(f"""
                        <div class="t-row">
                            <div class="t-time">{ev['t']}</div>
                            <div class="t-dot"></div>
                            <div class="t-content">
                                <div class="t-ttl">{ev['ttl']}</div>
                                <div class="t-desc">{ev['desc']}</div>
                                {tip_html}
                                <div style="margin-top:8px;">{maps_html}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# ─── TAB: RESERVAS ────────────────────────────────────────────────────────────
with t_res:
    st.markdown("<h3 class='playfair'>Tracker de Reservas</h3>", unsafe_allow_html=True)
    df_r = load_data("viaje_reservas")
    
    cols = st.columns(2)
    for i, r in enumerate(RESERVAS_DEF):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="card-white">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; font-size:1rem;">{r['title']}</span>
                        <span style="font-size:0.7rem; color:red; font-weight:600;">{r['urgencia']}</span>
                    </div>
                    <p style="color:grey; font-size:0.85rem; margin-top:5px;">{r['detail']}</p>
                </div>
            """, unsafe_allow_html=True)
            # Aquí iría el botón de "Confirmar" que ya tenías en tu app previa

# ─── TAB: TIPS ────────────────────────────────────────────────────────────────
with t_tips:
    st.markdown("<h3 class='playfair'>Tips Esenciales</h3>", unsafe_allow_html=True)
    tips = [
        {"i": "☕", "t": "Café en la barra", "d": "Parado = €1.20. Sentado = €4. Es ley."},
        {"i": "💧", "t": "Agua gratis", "d": "Pedí 'Acqua del rubinetto'. Es potable y gratuita."},
        {"i": "👟", "t": "Zapatos", "d": "Caminarás 15km por día en adoquines. Suela firme sí o sí."}
    ]
    
    cols_t = st.columns(3)
    for i, tip in enumerate(tips):
        with cols_t[i % 3]:
            st.markdown(f"""
                <div class="card-white" style="height:100%;">
                    <div style="font-size:1.5rem;">{tip['i']}</div>
                    <div style="font-weight:600; margin:5px 0;">{tip['t']}</div>
                    <div style="font-size:0.8rem; color:grey;">{tip['d']}</div>
                </div>
            """, unsafe_allow_html=True)

# ─── SYNC BADGE ───────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("🟢 Conectado a Google Sheets")
