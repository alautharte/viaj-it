import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide", initial_sidebar_state="collapsed")

# CSS Comprimido para evitar cortes de límite de caracteres
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
:root {--cream:#F7F3EE;--parchment:#EDE7DC;--terracotta:#C4693A;--terracotta-light:#E8956D;--terracotta-dark:#8B3E1E;--olive:#6B7A3E;--slate:#3D4A5C;--slate-light:#6B7A8D;--gold:#C9A84C;--gold-light:#E8C96A;--ink:#1A1A2E;--white:#FFFFFF;}
.stApp {background-color: var(--cream) !important; color: var(--ink) !important;}
[data-testid="collapsedControl"], [data-testid="stSidebar"], header, footer {display: none !important; visibility: hidden !important;}
p, div, span, h1, h2, h3, h4, h5, h6, li, td, th {font-family: 'DM Sans', sans-serif;}
.stTabs [data-baseweb="tab-list"] {gap:8px; background:var(--parchment); padding:8px 12px; border-radius:12px;}
.stTabs [data-baseweb="tab"] {padding:10px 20px; border-radius:8px; border:none; background:rgba(255,255,255,0.5);}
.stTabs [data-baseweb="tab"] p {color:var(--slate) !important; font-weight:600 !important; font-size:0.9rem !important;}
.stTabs [aria-selected="true"] {background:var(--white) !important; box-shadow:0 2px 4px rgba(0,0,0,0.05);}
.stTabs [aria-selected="true"] p {color:var(--terracotta-dark) !important;}
.stTabs [data-baseweb="tab-highlight"] {display:none;}
div.row-widget.stRadio > div {flex-direction:row; flex-wrap:wrap; gap:10px; background:white; padding:15px; border-radius:12px; border:1px solid var(--parchment); box-shadow:0 2px 5px rgba(0,0,0,0.02);}
div.row-widget.stRadio > div > label {background-color:var(--parchment) !important; padding:10px 18px; border-radius:20px; cursor:pointer; transition:0.2s;}
div.row-widget.stRadio > div > label p {color:var(--ink) !important; font-weight:600 !important; font-size:0.9rem !important; margin:0;}
div.row-widget.stRadio > div > label[data-checked="true"] {background-color:var(--terracotta) !important; border:2px solid var(--terracotta-dark) !important;}
div.row-widget.stRadio > div > label[data-checked="true"] p {color:var(--white) !important;}
div.row-widget.stRadio div[role="radiogroup"] label > div:first-child {display:none;}
.hero {background:var(--slate); padding:3rem 2rem 2rem; text-align:center; border-radius:16px; margin-bottom:0;}
.hero-title {font-family:'Playfair Display', serif; font-size:3.5rem; color:var(--cream); line-height:1.1; margin-bottom:0.5rem;}
.hero-title em {color:var(--gold-light); font-style:italic;}
.hero-sub {font-size:0.95rem; color:rgba(247,243,238,0.65); letter-spacing:0.05em; margin-bottom:1.5rem;}
.hero-dates {display:inline-flex; gap:1rem; background:rgba(247,243,238,0.1); border:0.5px solid rgba(247,243,238,0.2); border-radius:50px; padding:0.5rem 1.5rem; font-size:0.85rem; color:var(--gold-light);}
.stats-bar {display:flex; justify-content:center; background:var(--terracotta); margin-top:-10px; margin-bottom:2rem; border-radius:0 0 16px 16px; flex-wrap:wrap;}
.stat-item {flex:1; padding:1rem; text-align:center; border-right:0.5px solid rgba(247,243,238,0.2); min-width:120px;}
.stat-item:last-child {border-right:none;}
.stat-num {font-family:'Playfair Display', serif; font-size:1.8rem !important; color:var(--cream) !important; display:block; font-weight:600; line-height:1;}
.stat-lbl {font-size:0.7rem !important; color:rgba(247,243,238,0.8) !important; text-transform:uppercase; letter-spacing:0.1em; margin-top:4px; display:block;}
.section-header {display:flex; flex-direction:column; margin:1.5rem 0; padding-bottom:1rem; border-bottom:1px solid var(--parchment);}
.section-title {font-family:'Playfair Display', serif; font-size:2.2rem; color:var(--terracotta-dark); line-height:1.2;}
.section-meta {font-size:0.9rem; color:var(--slate-light); margin-top:4px; font-weight:500;}
.card {background:var(--white); border-radius:12px; border:1px solid var(--parchment); margin-bottom:1.5rem; box-shadow:0 2px 8px rgba(26,26,46,0.05); overflow:hidden;}
.card-header {display:flex; align-items:center; gap:10px; padding:0.85rem 1.2rem; background:var(--parchment); border-bottom:1px solid rgba(196,105,58,0.15);}
.day-badge {background:var(--terracotta); color:var(--white) !important; font-size:0.75rem; font-weight:600; padding:4px 12px; border-radius:20px;}
.t-row {display:grid; grid-template-columns:55px 16px 1fr; gap:0 12px; padding:15px 20px; border-bottom:1px solid var(--parchment);}
.t-time {font-size:0.85rem; color:var(--slate-light); text-align:right; padding-top:2px; font-weight:600;}
.t-dot {width:10px; height:10px; border-radius:50%; background:var(--parchment); border:2px solid var(--terracotta-light); margin-top:5px;}
.t-dot.hi {background:var(--terracotta); border-color:var(--terracotta-dark);}
.t-ttl {font-size:1rem; font-weight:600; color:var(--ink); margin-bottom:4px;}
.t-ttl.star::before {content:'★ '; color:#C9A84C;}
.t-desc {font-size:0.85rem; color:var(--slate-light); line-height:1.5;}
.t-tip {font-size:0.75rem; color:var(--terracotta-dark); background:rgba(196,105,58,0.07); border-left:3px solid var(--terracotta-light); padding:6px 12px; margin-top:8px; border-radius:0 4px 4px 0;}
.btn {display:inline-flex; align-items:center; gap:6px; font-size:0.75rem; padding:5px 12px; border-radius:6px; border:1px solid; text-decoration:none !important; font-weight:600; margin:8px 8px 0 0; background:white; transition:all 0.2s;}
.btn-maps {border-color:#4285F4; color:#4285F4 !important;}
.btn-booking {border-color:#003580; color:#003580 !important;}
.btn-airbnb {border-color:#FF5A5F; color:#FF5A5F !important;}
.btn-ticket {border-color:var(--olive); color:var(--olive) !important;}
.tag {display:inline-flex; align-items:center; font-size:0.7rem; padding:3px 10px; border-radius:20px; font-weight:600; margin-right:6px; margin-top:6px;}
.tag-train {background:#E8F0FB; color:#2A5FAC !important;}
.tag-walk {background:#EBF5E1; color:#3A6B18 !important;}
.tag-food {background:#FDE8DE; color:#8B3E1E !important;}
.tag-museum {background:#F5E8F5; color:#7A3A8C !important;}
.tag-shop {background:#FFF0E0; color:#8B5010 !important;}
.tag-boat {background:#E0F4EF; color:#0F6E56 !important;}
.tag-sleep {background:#EEF0FD; color:#4A50B0 !important;}
.tag-bus {background:#FEF3E2; color:#8B5E10 !important;}
.tag-padel {background:#E8F5E8; color:#2A6B2A !important;}
.hotel-card {border:1px solid var(--parchment); border-radius:12px; padding:1.2rem; margin:0.75rem 0 1.5rem 0; background:var(--white); box-shadow:0 2px 5px rgba(0,0,0,0.03);}
.transport-card {background:var(--white); border:1px solid var(--parchment); border-radius:10px; padding:1rem 1.2rem; margin:0.5rem 0; display:flex; align-items:center; gap:15px; box-shadow:0 1px 3px rgba(0,0,0,0.03);}
.budget-table {width:100%; border-collapse:collapse; font-size:0.85rem; margin-top:5px;}
.budget-table th {text-align:left; padding:12px; background:var(--parchment); color:var(--slate) !important; font-size:0.75rem; text-transform:uppercase;}
.budget-table td {padding:12px; border-bottom:1px solid var(--parchment); color:var(--ink) !important; font-weight:500;}
.alert {background:rgba(196,105,58,0.08); border:1px solid rgba(196,105,58,0.25); border-radius:8px; padding:1rem; font-size:0.85rem; color:var(--terracotta-dark) !important; margin-bottom:1.5rem; line-height:1.5;}
.alert-green {background:rgba(107,122,62,0.08); border-color:rgba(107,122,62,0.25); color:var(--olive) !important;}
</style>""", unsafe_allow_html=True)

@st.cache_resource(ttl=300)
def get_workbook():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])

def load_sheet_data(name):
    try: return pd.DataFrame(get_workbook().worksheet(name).get_all_records())
    except: return pd.DataFrame()

def add_nota(txt, autor):
    try:
        ws = get_workbook().worksheet("viaje_notas")
        ws.append_row([f"n{datetime.now().strftime('%m%d%H%M')}", txt, "General", autor, datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear()
        return True
    except: return False

RESERVAS_DATA = [
    {"tit": "La Última Cena", "det": "Milán · Día 2 · 26 mayo · 08:15", "url": "https://cenacolodavincimilano.vivaticket.com", "urg": "🔴 URGENTE"},
    {"tit": "Galería Borghese", "det": "Roma · Día 12 · 5 junio · Tarde", "url": "https://www.galleriaborghese.it", "urg": "🔴 URGENTE"},
    {"tit": "Museos Vaticanos + Sixtina", "det": "Roma · Día 10 · 3 junio · 08:00", "url": "https://www.museivaticani.va", "urg": "🔴 URGENTE"},
    {"tit": "Cúpula Brunelleschi", "det": "Florencia · Día 6 · 30 mayo · Tarde", "url": "https://www.ilgrandemuseodelduomo.it", "urg": "🟠 Importante"},
    {"tit": "David Accademia", "det": "Florencia · Día 7 · 31 mayo · 14:00", "url": "https://www.uffizi.it", "urg": "🟠 Importante"},
    {"tit": "Galería Uffizi", "det": "Florencia · Día 7 · 31 mayo · 08:30", "url": "https://www.uffizi.it", "urg": "🟠 Importante"},
    {"tit": "Coliseo + Foro Romano", "det": "Roma · Día 11 · 4 junio · 08:00", "url": "https://www.coopculture.it", "urg": "🟡 Recomendado"},
    {"tit": "Tren Milán → La Spezia", "det": "28 mayo · 08:10hs", "url": "https://www.trenitalia.com", "urg": "🟡 Anticipado"},
    {"tit": "Tren Venecia → Zurich", "det": "11 junio · 09:00hs", "url": "https://www.sbb.ch", "urg": "🟡 Anticipado"}
]

TRANSPORTES_DATA = [
    {"ico": "✈️→🚄", "r": "MXP → Milano", "d": "Malpensa Express · Sale cada 30 min", "p": "€13/p", "u": "https://www.trenord.it"},
    {"ico": "🚄", "r": "Milano → La Spezia", "d": "Intercity · ~3h · Salida 08:10", "p": "€25–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "C. Terre Express", "d": "Tren regional · Incluido en Cinque Terre Card", "p": "Incluido", "u": "https://www.cinqueterre.eu.com"},
    {"ico": "🚄", "r": "La Spezia → Firenze", "d": "Intercity · ~2h · Salida 08:30", "p": "€15–20", "u": "https://www.trenitalia.com"},
    {"ico": "🚌", "r": "Firenze ↔ Siena", "d": "Bus SENA · 1h30", "p": "€9", "u": "https://www.tiemmespa.it"},
    {"ico": "🚄", "r": "Firenze → Roma", "d": "Frecciarossa · 1h30", "p": "€25–45", "u": "https://www.trenitalia.com"},
    {"ico": "🚄", "r": "Roma → Napoli", "d": "Frecciarossa · 1h10", "p": "€20–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "Napoli → Pompei", "d": "Circumvesuviana · 40 min", "p": "€3", "u": "https://www.eavsrl.it"},
    {"ico": "⛵", "r": "Napoli → Positano", "d": "Ferry SNAV o Alilauro · 65 min", "p": "€20/p", "u": "https://www.alilauro.it"},
    {"ico": "🚌", "r": "Bus SITA Amalfi", "d": "Positano ↔ Amalfi ↔ Ravello", "p": "€2.50", "u": "https://www.sitasudtrasporti.it"},
    {"ico": "🚄", "r": "Napoli → Venezia", "d": "Frecciarossa directo · 4h50", "p": "€35–60", "u": "https://www.trenitalia.com"},
    {"ico": "🚤", "r": "Vaporetto Venecia", "d": "Ticket 24h", "p": "€25", "u": "https://actv.avmspa.it"},
    {"ico": "🚄", "r": "Venezia → Zurich", "d": "EuroCity directo · 4h45 · Alpes", "p": "€40–60", "u": "https://www.sbb.ch"}
]

TIPS_DATA = [
    ("☕ Café en barra", "Parado = €1.20. Sentado en mesa = €3–5."),
    ("💧 Agua del grifo", "Pedir 'acqua del rubinetto' en restaurantes — gratis."),
    ("🍽️ Menú del giorno", "Primer plato + segundo + bebida + pan = €12–15. Solo almuerzo."),
    ("💳 Revolut/Wise", "En Suiza cambiar a CHF. 1 CHF ≈ €1.05."),
    ("👟 Zapatos", "10–15 km por día en adoquines. Suela firme fundamental."),
    ("🕌 Ropa iglesias", "Hombros y rodillas cubiertos obligatorio."),
    ("🚌 Bus SITA", "Comprar ticket en tabacchi ANTES de subir. €2.50."),
    ("🍦 Gelato", "Evitar colores fluo o montañas brillantes."),
    ("📱 Apps", "Trenitalia, Maps.me, TheFork, SBB para Suiza."),
    ("🎾 Pádel Roma", "Padel Nuestro Roma (D12). Probar palas en pista."),
    ("🛍️ Ropa Milán", "Corso Buenos Aires. 2km de tiendas accesibles."),
    ("🧀 Fondue Suiza", "Sprüngli (1836) en Zurich y Swiss Chuchi. Muy caro.")
]

ITIN = {
    "Milán": {
        "meta": "25-27 mayo · 3 noches",
        "hotel": {"n": "Hotel Ariston ★★★", "m": "Central · Desayuno", "p": "~€80", "b": "https://booking.com", "a": "https://airbnb.com", "maps": "http://google.com/maps"},
        "days": [
            {"d": "D1", "date": "Lun 25 Mayo — Llegada", "events": [
                {"t": "10:15", "hi": True, "ttl": "Llegada MXP", "desc": "Inmigración pasaporte argentino.", "tags": "", "maps": ""},
                {"t": "11:30", "hi": False, "ttl": "Malpensa Express", "desc": "Tren a Centrale. 52 min.", "tags": '<span class="tag tag-train">🚄 €13</span>', "maps": ""},
                {"t": "13:30", "hi": False, "ttl": "Almuerzo", "desc": "Risotto alla milanese.", "tags": '<span class="tag tag-food">🍝 Comida</span>', "maps": ""},
                {"t": "18:00", "hi": False, "ttl": "Navigli", "desc": "Aperol Spritz.", "tags": '<span class="tag tag-walk">🚶 Paseo</span>', "maps": "http://google.com/maps"}
            ]},
            {"d": "D2", "date": "Mar 26 Mayo — Cultura", "events": [
                {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA", "desc": "RESERVA CRÍTICA. 15 min.", "tags": '<span class="tag tag-museum">🎨 €17</span>', "maps": "http://google.com/maps", "tip": "⚠️ Reservar ya."},
                {"t": "10:00", "hi": True, "ttl": "★ Duomo", "desc": "Terrazas en ascensor.", "tags": '<span class="tag tag-museum">⛪ €15</span>', "maps": ""},
                {"t": "15:00", "hi": True, "ttl": "★ Corso Buenos Aires", "desc": "Shopping barato.", "tags": '<span class="tag tag-shop">🛍️ Ropa</span>', "maps": ""},
                {"t": "17:30", "hi": False, "ttl": "Padel Nuestro Milano", "desc": "Pista interior.", "tags": '<span class="tag tag-padel">🎾 Pádel</span>', "maps": ""}
            ]},
            {"d": "D3", "date": "Mié 27 Mayo — Brera", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Pinacoteca Brera", "desc": "Arte renacentista.", "tags": '<span class="tag tag-museum">🎨 €15</span>', "maps": ""},
                {"t": "11:30", "hi": False, "ttl": "Bosco Verticale", "desc": "Barrio Isola.", "tags": '<span class="tag tag-walk">🌿 Gratis</span>', "maps": ""}
            ]}
        ]
    },
    "Cinque Terre": {
        "meta": "28-29 mayo · 2 noches (La Spezia)",
        "hotel": {"n": "Hotel Firenze ★★★", "m": "A 5 min de estación", "p": "~€75", "b": "https://booking.com", "a": "https://airbnb.com", "maps": ""},
        "days": [
            {"d": "D4", "date": "Jue 28 Mayo — Pueblos", "events": [
                {"t": "11:30", "hi": False, "ttl": "Llegada La Spezia", "desc": "Comprar CT Card.", "tags": '<span class="tag tag-train">🎫 €29.50</span>', "maps": ""},
                {"t": "12:30", "hi": True, "ttl": "★ Riomaggiore", "desc": "Pesto y fotos.", "tags": '<span class="tag tag-food">🍃 Pesto</span>', "maps": ""},
                {"t": "15:30", "hi": True, "ttl": "★ Manarola", "desc": "Mirador icónico.", "tags": '<span class="tag tag-walk">📸 Foto</span>', "maps": ""}
            ]},
            {"d": "D5", "date": "Vie 29 Mayo — Trekking", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Vernazza", "desc": "Castillo Doria.", "tags": "", "maps": ""},
                {"t": "11:00", "hi": True, "ttl": "★ Trekking a Monterosso", "desc": "3.5km. 2h.", "tags": '<span class="tag tag-walk">🥾 Trek</span>', "maps": ""},
                {"t": "14:00", "hi": False, "ttl": "Monterosso", "desc": "Playa y anchoas.", "tags": '<span class="tag tag-food">🐟 Comida</span>', "maps": ""}
            ]}
        ]
    },
    "Florencia": {
        "meta": "30 mayo-2 jun · 4 noches",
        "hotel": {"n": "Hotel Davanzati ★★★", "m": "Cerca del Duomo", "p": "~€100", "b": "https://booking.com", "a": "https://airbnb.com", "maps": ""},
        "days": [
            {"d": "D6", "date": "Sáb 30 Mayo — Duomo", "events": [
                {"t": "11:00", "hi": True, "ttl": "★ Cúpula Brunelleschi", "desc": "463 escalones.", "tags": '<span class="tag tag-museum">⛪ €20</span>', "maps": ""},
                {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo", "desc": "Atardecer.", "tags": '<span class="tag tag-walk">🌅 Gratis</span>', "maps": ""}
            ]},
            {"d": "D7", "date": "Dom 31 Mayo — Museos", "events": [
                {"t": "08:30", "hi": True, "ttl": "★ Uffizi", "desc": "3h mínimo.", "tags": '<span class="tag tag-museum">🎨 €24</span>', "maps": ""},
                {"t": "14:00", "hi": True, "ttl": "★ David", "desc": "Original en Accademia.", "tags": '<span class="tag tag-museum">🗿 €16</span>', "maps": ""}
            ]},
            {"d": "D8", "date": "Lun 1 Jun — Pitti", "events": [
                {"t": "09:00", "hi": False, "ttl": "Palazzo Pitti", "desc": "Jardines Boboli.", "tags": '<span class="tag tag-museum">🏰 €16</span>', "maps": ""},
                {"t": "16:00", "hi": True, "ttl": "★ Cappelle Medicee", "desc": "Miguel Ángel.", "tags": '<span class="tag tag-museum">🗿 €9</span>', "maps": ""}
            ]},
            {"d": "D9", "date": "Mar 2 Jun — Siena", "events": [
                {"t": "07:30", "hi": False, "ttl": "Bus a Siena", "desc": "1.5h. Autostazione.", "tags": '<span class="tag tag-bus">🚌 €9</span>', "maps": ""},
                {"t": "09:00", "hi": True, "ttl": "Piazza del Campo", "desc": "Torre Mangia.", "tags": '<span class="tag tag-museum">🏰 €10</span>', "maps": ""}
            ]}
        ]
    },
    "Roma": {
        "meta": "3-6 jun · 4 noches",
        "hotel": {"n": "Hotel Arco del Lauro ★★★", "m": "Trastevere", "p": "~€88", "b": "https://booking.com", "a": "https://airbnb.com", "maps": ""},
        "days": [
            {"d": "D10", "date": "Mié 3 Jun — Vaticano", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos", "desc": "Capilla Sixtina.", "tags": '<span class="tag tag-museum">🎨 €21</span>', "maps": "", "tip": "⚠️ Silencio absoluto."},
                {"t": "14:00", "hi": False, "ttl": "San Pedro", "desc": "Cúpula.", "tags": '<span class="tag tag-museum">⛪ €8</span>', "maps": ""}
            ]},
            {"d": "D11", "date": "Jue 4 Jun — Imperial", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Coliseo", "desc": "Foro y Palatino.", "tags": '<span class="tag tag-museum">🏛️ €16</span>', "maps": ""},
                {"t": "17:30", "hi": False, "ttl": "Trastevere", "desc": "Cena típica.", "tags": "", "maps": ""}
            ]},
            {"d": "D12", "date": "Vie 5 Jun — Borghese", "events": [
                {"t": "09:00", "hi": False, "ttl": "Pantheon y Trevi", "desc": "Moneda de espaldas.", "tags": "", "maps": ""},
                {"t": "15:00", "hi": True, "ttl": "★ Borghese", "desc": "Bernini.", "tags": '<span class="tag tag-museum">🗿 €17</span>', "maps": ""},
                {"t": "18:00", "hi": True, "ttl": "★ Padel Nuestro", "desc": "Probar palas.", "tags": '<span class="tag tag-padel">🎾 Compras</span>', "maps": ""}
            ]},
            {"d": "D13", "date": "Sáb 6 Jun — Libre", "events": [
                {"t": "09:00", "hi": False, "ttl": "Castel Sant'Angelo", "desc": "Mausoleo.", "tags": '<span class="tag tag-museum">🏰 €14</span>', "maps": ""}
            ]}
        ]
    },
    "Nápoles": {
        "meta": "7 jun · 1 noche",
        "hotel": {"n": "Hotel Piazza Bellini", "m": "Spaccanapoli", "p": "~€80", "b": "https://booking.com", "a": "https://airbnb.com", "maps": ""},
        "days": [
            {"d": "D14", "date": "Dom 7 Jun — Pompeya", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Circumvesuviana", "desc": "Tren a Pompeya.", "tags": '<span class="tag tag-train">🚂 €3</span>', "maps": ""},
                {"t": "10:00", "hi": True, "ttl": "★ Pompeya Scavi", "desc": "3h mínimo.", "tags": '<span class="tag tag-museum">🌋 €16</span>', "maps": ""},
                {"t": "19:30", "hi": True, "ttl": "★ Pizza original", "desc": "Da Michele o Sorbillo.", "tags": '<span class="tag tag-food">🍕 €5-8</span>', "maps": ""}
            ]}
        ]
    },
    "Amalfi": {
        "meta": "8-9 jun · 2 noches (Praiano)",
        "hotel": {"n": "Albergo California", "m": "Vista mar", "p": "~€92", "b": "https://booking.com", "a": "https://airbnb.com", "maps": ""},
        "days": [
            {"d": "D15", "date": "Lun 8 Jun — Positano", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Positano", "desc": "Playa Grande.", "tags": "", "maps": ""},
                {"t": "15:00", "hi": True, "ttl": "★ Bus SITA", "desc": "Lado derecho al mar.", "tags": '<span class="tag tag-bus">🚌 €2.5</span>', "maps": ""}
            ]},
            {"d": "D16", "date": "Mar 9 Jun — Trekking", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Villa Cimbrone", "desc": "Ravello.", "tags": '<span class="tag tag-museum">🌿 €7</span>', "maps": ""},
                {"t": "11:00", "hi": True, "ttl": "★ Sentiero", "desc": "Camino de Dioses.", "tags": '<span class="tag tag-walk">🥾 Trek</span>', "maps": ""}
            ]}
        ]
    },
    "Venecia": {
        "meta": "10 jun · 1 noche",
        "hotel": {"n": "Hotel Dalla Mora", "m": "Auténtico", "p": "~€100", "b": "https://booking.com", "a": "", "maps": ""},
        "days": [
            {"d": "D17", "date": "Mié 10 Jun — Canales", "events": [
                {"t": "13:00", "hi": True, "ttl": "★ Vaporetto 1", "desc": "Gran Canal.", "tags": '<span class="tag tag-boat">🚤 €25</span>', "maps": ""},
                {"t": "15:00", "hi": True, "ttl": "★ San Marcos", "desc": "Campanile.", "tags": '<span class="tag tag-museum">🏛️ €10</span>', "maps": ""},
                {"t": "21:00", "hi": False, "ttl": "Góndola", "desc": "Nocturna.", "tags": '<span class="tag tag-boat">🎭 €80</span>', "maps": ""}
            ]}
        ]
    },
    "Zurich": {
        "meta": "11-13 jun · 3 noches",
        "hotel": {"n": "Hotel Otter", "m": "Altstadt", "p": "~€100", "b": "https://booking.com", "a": "", "maps": ""},
        "days": [
            {"d": "D18", "date": "Jue 11 Jun — Llegada", "events": [
                {"t": "14:00", "hi": False, "ttl": "Bahnhofstrasse", "desc": "Lago y compras.", "tags": "", "maps": ""},
                {"t": "15:30", "hi": True, "ttl": "★ Grossmünster", "desc": "Torres.", "tags": "", "maps": ""}
            ]},
            {"d": "D19", "date": "Vie 12 Jun — Lago", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Crucero", "desc": "Lago de Zurich.", "tags": '<span class="tag tag-boat">⛵ €8</span>', "maps": ""},
                {"t": "20:00", "hi": True, "ttl": "★ Swiss Chuchi", "desc": "Fondue.", "tags": '<span class="tag tag-food">🧀 €40</span>', "maps": ""}
            ]},
            {"d": "D20", "date": "Sáb 13 Jun — Adiós", "events": [
                {"t": "09:00", "hi": False, "ttl": "Uetliberg", "desc": "Montaña.", "tags": '<span class="tag tag-walk">⛰️ €5</span>', "maps": ""},
                {"t": "13:00", "hi": True, "ttl": "★ Sprüngli", "desc": "Chocolates.", "tags": "", "maps": ""},
                {"t": "22:00", "hi": False, "ttl": "A dormir", "desc": "Vuelo 08:55 am.", "tags": '<span class="tag tag-sleep">✈️ Alarma</span>', "maps": ""}
            ]}
        ]
    }
}

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero"><div class="hero-title">Italia & <em>Zurich</em></div><div class="hero-sub">Luna de Miel · Adilson & Mirtha · Mayo-Junio 2026</div><div class="hero-dates"><span>✈ Sale 24 mayo · IGU</span><span>·</span><span>Regresa 14 junio · ZRH</span></div></div>
<div class="stats-bar"><div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días</span></div><div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div><div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Italia</span></div><div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Zurich</span></div></div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🌍 Vuelos", "📅 Itinerario", "🎟️ Reservas", "💰 Presupuesto", "🚄 Trenes", "💡 Tips", "📝 Notas"])

with tab1:
    st.markdown('<div class="section-header"><div class="section-title">Vuelos confirmados</div></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card"><div class="card-header"><span class="day-badge">IDA</span><span style="margin-left:10px;font-weight:600;">24 Mayo</span></div><div class="t-row"><div class="t-time">14:50</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Foz → Milán</div><div class="t-desc">LA3879 IGU 14:50 → GRU → MXP 10:15+1</div><span class="tag tag-train">LATAM</span></div></div></div>
    <div class="card"><div class="card-header"><span class="day-badge">VUELTA</span><span style="margin-left:10px;font-weight:600;">14 Junio</span></div><div class="t-row"><div class="t-time">08:55</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Zurich → Foz</div><div class="t-desc">LA8799 ZRH 08:55 → MXP → GRU → IGU 00:05+1</div><span class="tag tag-train">Swiss/LATAM</span></div></div></div>
    """, unsafe_allow_html=True)

with tab2:
    ciudad_sel = st.radio("Ciudades", list(ITIN.keys()), horizontal=True, label_visibility="collapsed")
    d = ITIN[ciudad_sel]
    h = d["hotel"]
    bb = f'<a href="{h["b"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if h["b"] else ""
    ba = f'<a href="{h["a"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if h["a"] else ""
    st.markdown(f'<div class="section-header" style="margin-top:1rem;"><div class="section-title">{ciudad_sel}</div><div class="section-meta">{d["meta"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hotel-card"><h3>{h["n"]}</h3><p>{h["m"]}</p><span class="day-badge" style="background:#6B7A3E;">{h["p"]}</span><br><br>{bb}{ba}</div>', unsafe_allow_html=True)
    
    for day in d["days"]:
        html = f'<div class="card-header" style="margin-top:1.5rem;border-radius:12px 12px 0 0;"><span class="day-badge">{day["d"]}</span><strong style="margin-left:12px;">{day["date"]}</strong></div><div class="card" style="border-top:none;border-radius:0 0 12px 12px;">'
        for e in day["events"]:
            dc = "hi" if e["hi"] else ""
            sc = "star" if e["hi"] else ""
            tip = f'<div class="t-tip">{e["tip"]}</div>' if "tip" in e else ""
            bm = f'<a href="{e["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if e["maps"] else ""
            html += f'<div class="t-row"><div class="t-time">{e["t"]}</div><div class="t-dot {dc}"></div><div class="t-content"><div class="t-ttl {sc}">{e["ttl"]}</div><div class="t-desc">{e["desc"]}</div>{tip}<div style="margin-top:5px;">{e["tags"]} {bm}</div></div></div>'
        st.markdown(html + '</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-header"><div class="section-title">Reservas</div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for i, r in enumerate(RESERVAS_DATA):
        with (c1 if i%2==0 else c2):
            st.markdown(f'<div class="card" style="padding:1rem;"><strong>{r["tit"]}</strong><br><small>{r["det"]} · {r["urg"]}</small><br><br><a href="{r["url"]}" class="btn btn-ticket" target="_blank">Reservar</a></div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-header"><div class="section-title">Presupuesto</div></div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(PRESUPUESTO_DATA).drop(columns=["b","a"]))

with tab5:
    st.markdown('<div class="section-header"><div class="section-title">Trenes</div></div>', unsafe_allow_html=True)
    for t in TRANSPORTES_DATA:
        st.markdown(f'<div class="transport-card"><div style="font-size:1.5rem;">{t["ico"]}</div><div style="flex:1;"><strong>{t["r"]}</strong><br><small>{t["d"]}</small></div><div>{t["p"]}</div><a href="{t["u"]}" target="_blank" class="btn btn-maps">Comprar</a></div>', unsafe_allow_html=True)

with tab6:
    st.markdown('<div class="section-header"><div class="section-title">Tips</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for i, (tit, txt) in enumerate(TIPS_DATA):
        with [c1,c2,c3][i%3]:
            st.markdown(f'<div class="card" style="padding:1rem;"><strong>{tit}</strong><br><small>{txt}</small></div>', unsafe_allow_html=True)

with tab7:
    st.markdown('<div class="section-header"><div class="section-title">Notas</div></div>', unsafe_allow_html=True)
    with st.form("nota_form"):
        txt = st.text_area("Nota")
        aut = st.selectbox("Autor", ["Adilson", "Mirtha"])
        if st.form_submit_button("Guardar"):
            if add_nota(txt, aut): st.success("Ok")

# --- FIN DEL CÓDIGO ---
