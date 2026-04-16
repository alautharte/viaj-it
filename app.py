import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide", initial_sidebar_state="collapsed")

# ─── ESTILOS CSS (Forzando contraste contra Streamlit Dark Mode) ──────────────
st.markdown(textwrap.dedent("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
  
  :root {
    --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --terracotta-light: #E8956D;
    --terracotta-dark: #8B3E1E; --olive: #6B7A3E; --slate: #3D4A5C;
    --slate-light: #6B7A8D; --gold: #C9A84C; --gold-light: #E8C96A; --ink: #1A1A2E; --white: #FFFFFF;
  }

  .stApp { background-color: var(--cream) !important; color: var(--ink) !important; }
  
  /* MATAR ELEMENTOS POR DEFECTO */
  [data-testid="collapsedControl"], [data-testid="stSidebar"], header, footer { display: none !important; visibility: hidden !important; }

  /* FORZAR COLORES CONTRA EL DARK MODE DE STREAMLIT */
  p, div, span, h1, h2, h3, h4, h5, h6, li, td, th { font-family: 'DM Sans', sans-serif; }
  
  /* TABS (Navegación Superior) */
  .stTabs [data-baseweb="tab-list"] { gap: 8px; background: var(--parchment); padding: 8px 12px; border-radius: 12px; }
  .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; border: none; background: rgba(255,255,255,0.5); }
  .stTabs [data-baseweb="tab"] p { color: var(--slate) !important; font-weight: 600 !important; font-size: 0.9rem !important; }
  .stTabs [aria-selected="true"] { background: var(--white) !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
  .stTabs [aria-selected="true"] p { color: var(--terracotta-dark) !important; }
  .stTabs [data-baseweb="tab-highlight"] { display: none; }

  /* RADIO BUTTONS HORIZONTALES (Navegación de Ciudades) */
  div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; gap: 10px; background: white; padding: 15px; border-radius: 12px; border: 1px solid var(--parchment); box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
  div.row-widget.stRadio > div > label { background-color: var(--parchment) !important; padding: 10px 18px; border-radius: 20px; cursor: pointer; transition: 0.2s; }
  div.row-widget.stRadio > div > label p { color: var(--ink) !important; font-weight: 600 !important; font-size: 0.9rem !important; margin: 0; }
  div.row-widget.stRadio > div > label[data-checked="true"] { background-color: var(--terracotta) !important; border: 2px solid var(--terracotta-dark) !important; }
  div.row-widget.stRadio > div > label[data-checked="true"] p { color: var(--white) !important; }
  div.row-widget.stRadio div[role="radiogroup"] label > div:first-child { display: none; }

  /* HERO Y STATS */
  .hero { background: var(--slate); padding: 3rem 2rem 2rem; text-align: center; border-radius: 16px; margin-bottom: 0; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: var(--cream); line-height: 1.1; margin-bottom: 0.5rem; }
  .hero-title em { color: var(--gold-light); font-style: italic; }
  .hero-sub { font-size: 0.95rem; color: rgba(247,243,238,0.65); letter-spacing: 0.05em; margin-bottom: 1.5rem; }
  .hero-dates { display: inline-flex; gap: 1rem; background: rgba(247,243,238,0.1); border: 0.5px solid rgba(247,243,238,0.2); border-radius: 50px; padding: 0.5rem 1.5rem; font-size: 0.85rem; color: var(--gold-light); }
  
  .stats-bar { display: flex; justify-content: center; background: var(--terracotta); margin-top: -10px; margin-bottom: 2rem; border-radius: 0 0 16px 16px; flex-wrap: wrap; }
  .stat-item { flex: 1; padding: 1rem; text-align: center; border-right: 0.5px solid rgba(247,243,238,0.2); min-width: 120px; }
  .stat-item:last-child { border-right: none; }
  .stat-num { font-family: 'Playfair Display', serif; font-size: 1.8rem !important; color: var(--cream) !important; display: block; font-weight: 600; line-height: 1; }
  .stat-lbl { font-size: 0.7rem !important; color: rgba(247,243,238,0.8) !important; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; display: block; }

  /* COMPONENTES */
  .section-header { display: flex; flex-direction: column; margin: 1.5rem 0; padding-bottom: 1rem; border-bottom: 1px solid var(--parchment); }
  .section-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: var(--terracotta-dark); line-height: 1.2; }
  .section-meta { font-size: 0.9rem; color: var(--slate-light); margin-top: 4px; font-weight: 500; }
  
  .card { background: var(--white); border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(26,26,46,0.05); overflow: hidden; }
  .card-header { display: flex; align-items: center; gap: 10px; padding: 0.85rem 1.2rem; background: var(--parchment); border-bottom: 1px solid rgba(196,105,58,0.15); }
  .day-badge { background: var(--terracotta); color: var(--white) !important; font-size: 0.75rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; }
  
  .t-row { display: grid; grid-template-columns: 55px 16px 1fr; gap: 0 12px; padding: 15px 20px; border-bottom: 1px solid var(--parchment); }
  .t-time { font-size: 0.85rem; color: var(--slate-light); text-align: right; padding-top: 2px; font-weight: 600; }
  .t-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--parchment); border: 2px solid var(--terracotta-light); margin-top: 5px; }
  .t-dot.hi { background: var(--terracotta); border-color: var(--terracotta-dark); }
  .t-ttl { font-size: 1rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .t-ttl.star::before { content: '★ '; color: #C9A84C; }
  .t-desc { font-size: 0.85rem; color: var(--slate-light); line-height: 1.5; }
  .t-tip { font-size: 0.75rem; color: var(--terracotta-dark); background: rgba(196,105,58,0.07); border-left: 3px solid var(--terracotta-light); padding: 6px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; }
  
  .btn { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; padding: 5px 12px; border-radius: 6px; border: 1px solid; text-decoration: none !important; font-weight: 600; margin: 8px 8px 0 0; background: white; transition: all 0.2s; }
  .btn-maps { border-color: #4285F4; color: #4285F4 !important; }
  .btn-booking { border-color: #003580; color: #003580 !important; }
  .btn-airbnb { border-color: #FF5A5F; color: #FF5A5F !important; }
  .btn-ticket { border-color: var(--olive); color: var(--olive) !important; }
  .btn:hover { background: #f8f9fa; transform: translateY(-1px); }
  
  .tag { display: inline-flex; align-items: center; font-size: 0.7rem; padding: 3px 10px; border-radius: 20px; font-weight: 600; margin-right: 6px; margin-top: 6px; }
  .tag-train { background: #E8F0FB; color: #2A5FAC !important; }
  .tag-walk { background: #EBF5E1; color: #3A6B18 !important; }
  .tag-food { background: #FDE8DE; color: #8B3E1E !important; }
  .tag-museum { background: #F5E8F5; color: #7A3A8C !important; }
  .tag-shop { background: #FFF0E0; color: #8B5010 !important; }
  .tag-boat { background: #E0F4EF; color: #0F6E56 !important; }
  .tag-sleep { background: #EEF0FD; color: #4A50B0 !important; }
  .tag-bus { background: #FEF3E2; color: #8B5E10 !important; }

  .hotel-card { border: 1px solid var(--parchment); border-radius: 12px; padding: 1.2rem; margin: 0.75rem 0 1.5rem 0; background: var(--white); box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
  .transport-card { background: var(--white); border: 1px solid var(--parchment); border-radius: 10px; padding: 1rem 1.2rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
  
  .budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 5px; }
  .budget-table th { text-align: left; padding: 12px; background: var(--parchment); color: var(--slate) !important; font-size: 0.75rem; text-transform: uppercase; }
  .budget-table td { padding: 12px; border-bottom: 1px solid var(--parchment); color: var(--ink) !important; font-weight: 500; }
  
  .alert { background: rgba(196,105,58,0.08); border: 1px solid rgba(196,105,58,0.25); border-radius: 8px; padding: 1rem; font-size: 0.85rem; color: var(--terracotta-dark) !important; margin-bottom: 1.5rem; line-height: 1.5; }
  .alert-green { background: rgba(107,122,62,0.08); border-color: rgba(107,122,62,0.25); color: var(--olive) !important; }
</style>
"""), unsafe_allow_html=True)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
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

# ─── DATA COMPLETA (Estructurada en Diccionarios para evitar cortes) ──────────

RESERVAS_DATA = [
    {"tit": "La Última Cena — Da Vinci", "det": "Milán · Día 2 · 26 mayo · 08:15hs", "url": "https://cenacolodavincimilano.vivaticket.com", "urg": "🔴 URGENTE"},
    {"tit": "Galería Borghese — Roma", "det": "Roma · Día 12 · 5 junio · Tarde", "url": "https://www.galleriaborghese.it", "urg": "🔴 URGENTE"},
    {"tit": "Museos Vaticanos + Sixtina", "det": "Roma · Día 10 · 3 junio · 08:00hs", "url": "https://www.museivaticani.va", "urg": "🔴 URGENTE"},
    {"tit": "Cúpula Brunelleschi — Florencia", "det": "Florencia · Día 6 · 30 mayo · Tarde", "url": "https://www.ilgrandemuseodelduomo.it", "urg": "🟠 Importante"},
    {"tit": "David — Accademia Florencia", "det": "Florencia · Día 7 · 31 mayo · 14:00hs", "url": "https://www.uffizi.it/en/the-accademia-gallery", "urg": "🟠 Importante"},
    {"tit": "Galería degli Uffizi", "det": "Florencia · Día 7 · 31 mayo · 08:30hs", "url": "https://www.uffizi.it", "urg": "🟠 Importante"},
    {"tit": "Coliseo + Foro Romano", "det": "Roma · Día 11 · 4 junio · 08:00hs", "url": "https://www.coopculture.it", "urg": "🟡 Recomendado"},
    {"tit": "Tren Milán → La Spezia", "det": "28 mayo · 08:10hs · Trenitalia", "url": "https://www.trenitalia.com", "urg": "🟡 Anticipado"},
    {"tit": "Tren Venecia → Zurich", "det": "11 junio · 09:00hs · SBB", "url": "https://www.sbb.ch", "urg": "🟡 Anticipado"},
    {"tit": "Todos los trenes Frecciarossa", "det": "Firenze, Roma, Nápoles, Venecia · Trenitalia o Italo", "url": "https://www.trenitalia.com", "urg": "🟡 Anticipado"}
]

TRANSPORTES_DATA = [
    {"ico": "✈️→🚄", "r": "MXP → Milano Centrale", "d": "Malpensa Express · 52 min · Sale cada 30 min", "p": "€13/p", "u": "https://www.trenord.it"},
    {"ico": "🚄", "r": "Milano → La Spezia", "d": "Intercity · ~3h · Salida 08:10", "p": "€25–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "La Spezia ↔ Cinque Terre", "d": "Tren regional · 5–12 min entre pueblos · Incluido en Cinque Terre Card", "p": "Incluido", "u": "https://www.cinqueterre.eu.com"},
    {"ico": "🚄", "r": "La Spezia → Firenze SMN", "d": "Intercity · ~2h · Salida 08:30", "p": "€15–20", "u": "https://www.trenitalia.com"},
    {"ico": "🚌", "r": "Firenze ↔ Siena", "d": "Bus SENA · 1h30 · Sale cada hora desde Autostazione", "p": "€9", "u": "https://www.tiemmespa.it"},
    {"ico": "🚄", "r": "Firenze → Roma Termini", "d": "Frecciarossa · 1h30 · Sale cada 30 min", "p": "€25–45", "u": "https://www.trenitalia.com"},
    {"ico": "🚄", "r": "Roma → Napoli Centrale", "d": "Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00", "p": "€20–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "Napoli → Pompei Scavi", "d": "Circumvesuviana · 40 min · Andén -1 de Napoli Centrale", "p": "€3", "u": "https://www.eavsrl.it"},
    {"ico": "⛵", "r": "Napoli → Positano (ferry)", "d": "SNAV o Alilauro · Molo Beverello · 65 min · Solo mayo–oct", "p": "€20/p", "u": "https://www.alilauro.it"},
    {"ico": "🚌", "r": "Costa Amalfi (bus SITA)", "d": "Positano ↔ Amalfi ↔ Ravello · Ticket en tabacchi", "p": "€2.50", "u": "https://www.sitasudtrasporti.it"},
    {"ico": "🚄", "r": "Napoli → Venezia S. Lucia", "d": "Frecciarossa directo · 4h50 · Salida 07:30–08:00", "p": "€35–60", "u": "https://www.trenitalia.com"},
    {"ico": "🚤", "r": "Vaporetto Venecia (24h)", "d": "Línea 1 = Gran Canal completo · Línea 2 = rápida", "p": "€25", "u": "https://actv.avmspa.it"},
    {"ico": "🚄", "r": "Venezia → Zurich HB (Alpes)", "d": "EuroCity directo · 4h45 · Paisaje alpino · SBB.ch", "p": "€40–60", "u": "https://www.sbb.ch"},
    {"ico": "🚄", "r": "Zurich HB → Aeropuerto ZRH", "d": "SBB · 10 min · Sale cada 10 min · Andén S-Bahn", "p": "€4", "u": "https://www.sbb.ch"}
]

TIPS_DATA = [
    ("☕ Café en la barra", "Parado en la barra = €1.20. Sentado en mesa = €3–5. La ley lo establece — tienen que mostrar ambos precios en la carta."),
    ("💧 Agua del grifo", "Potable en toda Italia. Pedir 'acqua del rubinetto' en restaurantes — gratis. El agua mineral embotellada en mesa = €3–5."),
    ("🍽️ Menú del giorno", "Primer plato + segundo + bebida + pan = €12–15. Solo al almuerzo. La cena siempre es más cara. Buscar el menú en la pizarra."),
    ("💳 Revolut o Wise", "Para no pagar comisiones de cambio. En Suiza: cambiar a CHF francos suizos al llegar. 1 CHF ≈ €1.05."),
    ("👟 Zapatos (fundamental)", "10–15 km por día en adoquines. Amalfi y Cinque Terre requieren suela firme. Zapatillas de running funcionan bien."),
    ("🕌 Ropa para iglesias", "Hombros y rodillas cubiertos. Llevar una bufanda liviana — sirve para ambos. En verano hace calor pero las iglesias lo exigen."),
    ("🚌 Bus SITA Amalfi", "Comprar ticket en tabacchi (estanco) ANTES de subir. €2.50 el tramo. Sentarse del lado derecho mirando al mar Positano→Amalfi."),
    ("🍦 Gelato auténtico", "Colores apagados (no fluo), tapado con espátula, no en montañas. Si está brillante como plástico: es industrial."),
    ("📱 Apps esenciales", "Trenitalia + Italo (trenes) · Maps.me offline · TheFork para restaurantes · Revolut para pagos · SBB para Suiza."),
    ("🎾 Pádel — Padel Nuestro Roma", "La mejor tienda. Centro de Roma. Bullpadel, Siux, Babolat, Head, Star Vie. Pista interior para probar palas. Día 12 por la tarde."),
    ("🛍️ Ropa barata — Corso B. Aires", "Milán. Zara, H&M, Bershka, marcas italianas accesibles. 2km de tiendas. Día 2 por la tarde."),
    ("🧀 Suiza — Fondue y chocolate", "Sprüngli (1836) en Zurich. Fondue en Swiss Chuchi. En Suiza todo es más caro — presupuestar €80–100/día.")
]

PRESUPUESTO_DATA = [
    {"Ciudad": "Milán", "Noches": "3", "€/noche": "€80", "Total": "€240", "b": "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2", "a": "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2"},
    {"Ciudad": "La Spezia", "Noches": "2", "€/noche": "€75", "Total": "€150", "b": "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2", "a": "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2"},
    {"Ciudad": "Florencia", "Noches": "4", "€/noche": "€100", "Total": "€400", "b": "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2", "a": "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2"},
    {"Ciudad": "Roma", "Noches": "4", "€/noche": "€88", "Total": "€350", "b": "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2", "a": "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2"},
    {"Ciudad": "Nápoles", "Noches": "1", "€/noche": "€80", "Total": "€80", "b": "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2", "a": "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2"},
    {"Ciudad": "Costa Amalfi", "Noches": "2", "€/noche": "€92", "Total": "€185", "b": "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2", "a": "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2"},
    {"Ciudad": "Venecia", "Noches": "1", "€/noche": "€100", "Total": "€100", "b": "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2", "a": ""},
    {"Ciudad": "Zurich", "Noches": "3", "€/noche": "€100", "Total": "€300", "b": "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2", "a": ""}
]

ITINERARIO_FULL = {
    "🏛️ Milán (Días 1-3)": {
        "meta": "25, 26 y 27 mayo · 3 noches",
        "hotel": {"n": "Hotel Ariston ★★★ (o similar zona Centrale/Navigli)", "m": "Central para metro · Desayuno incluido · Habitación doble<br>Alternativa premium: Hotel Dei Cavalieri (junto al Duomo, ~€110/noche)", "p": "~€70–90 / noche · 3 noches", "book": "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28", "air": "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28", "maps": "https://maps.google.com/?q=Hotel+Ariston+Milan"},
        "days": [
            {"d": "Día 1", "date": "Lunes 25 mayo — Llegada y primer paseo", "events": [
                {"t": "10:15", "hi": True, "ttl": "Llegada MXP — Inmigración y aduana", "desc": "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta."},
                {"t": "11:30", "hi": False, "ttl": "Malpensa Express → Milano Centrale", "desc": "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station", "tags": '<span class="tag tag-train">🚄 €13/p</span> <a href="https://www.trenord.it/en/tickets/relations/malpensa-express/" target="_blank" class="btn btn-trenitalia">Trenord</a>'},
                {"t": "13:30", "hi": False, "ttl": "Check-in + almuerzo tranquilo", "desc": "Pedir risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones.", "tags": '<span class="tag tag-food">🍝 Risotto</span>'},
                {"t": "15:00", "hi": False, "ttl": "Siesta obligatoria", "desc": "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes."},
                {"t": "18:00", "hi": False, "ttl": "Paseo Navigli + Aperitivo", "desc": "Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.", "maps": "https://maps.google.com/?q=Navigli+Milan", "tags": '<span class="tag tag-walk">🚶 Paseo</span>'}
            ]},
            {"d": "Día 2", "date": "Martes 26 mayo — Duomo, Última Cena, Shopping y Pádel", "events": [
                {"t": "08:00", "hi": False, "ttl": "Desayuno italiano", "desc": "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.", "tags": '<span class="tag tag-food">☕ €3</span>'},
                {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA — Santa Maria delle Grazie", "desc": "El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.", "tip": "⚠️ CRÍTICO: Reservar hoy mismo. Los cupos de mayo se agotan meses antes.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan", "tags": '<span class="tag tag-museum">🎨 €15 + €2 reserva</span> <a href="https://cenacolodavincimilano.vivaticket.com" target="_blank" class="btn btn-ticket">🎟️ Reservar ahora</a>'},
                {"t": "10:00", "hi": True, "ttl": "★ Duomo di Milano", "desc": "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán.", "maps": "https://maps.google.com/?q=Duomo+di+Milano", "tags": '<span class="tag tag-museum">⛪ €15 terraza</span> <a href="https://ticket.duomomilano.it" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "11:30", "hi": False, "ttl": "Galleria Vittorio Emanuele II + Scala", "desc": "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).", "maps": "https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II+Milan", "tags": '<span class="tag tag-walk">🚶 Gratis</span>'},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo en Brera", "desc": "Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15.", "maps": "https://maps.google.com/?q=Brera+Milan", "tags": '<span class="tag tag-food">🍽️ €15</span>'},
                {"t": "15:00", "hi": True, "ttl": "★ Shopping — Corso Buenos Aires", "desc": "La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas accesibles. 2km de tiendas.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan", "tags": '<span class="tag tag-shop">🛍️ Ropa</span>'},
                {"t": "17:30", "hi": True, "ttl": "★ Padel Nuestro Milano (opcional)", "desc": "La mayor tienda de pádel del norte de Italia. Bullpadel, Siux, Adidas, Nox. Tienen pista interior.", "tip": "Más conveniente visitar Padel Nuestro Roma (centro) que ésta (40 min del centro). Abre hasta las 19:30.", "maps": "https://maps.google.com/?q=Via+Papa+Giovanni+XXIII+9a+Rodano+Millepini+Milan", "tags": '<span class="tag tag-padel">🎾 Pádel</span>'},
                {"t": "20:00", "hi": False, "ttl": "Cena en Navigli", "desc": "Evitar restaurantes con foto en el menú en la puerta — señal de trampa turística.", "tags": '<span class="tag tag-food">🍷 Cena</span>'}
            ]},
            {"d": "Día 3", "date": "Miércoles 27 mayo — Brera, Isola y preparación", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Pinacoteca di Brera", "desc": "Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia. Calcular 2h.", "maps": "https://maps.google.com/?q=Pinacoteca+di+Brera+Milan", "tags": '<span class="tag tag-museum">🎨 €15</span> <a href="https://pinacotecabrera.org" target="_blank" class="btn btn-ticket">Reservar</a>'},
                {"t": "11:30", "hi": False, "ttl": "Barrio Isola + Bosco Verticale", "desc": "El famoso 'bosque vertical' de Stefano Boeri. El barrio Isola tiene cafés y mercaditos locales muy cool.", "maps": "https://maps.google.com/?q=Bosco+Verticale+Milan", "tags": '<span class="tag tag-walk">🌿 Gratis</span>'},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo + tarde libre", "desc": "Zona Sant'Ambrogio (Basílica del siglo IV, gratis). Tarde para compras adicionales o descanso."},
                {"t": "19:00", "hi": False, "ttl": "Preparar maletas — mañana viajan a Cinque Terre", "desc": "Tren 08:10 desde Milano Centrale. Poner alarma.", "tags": '<span class="tag tag-sleep">🧳 Preparación</span>'}
            ]}
        ]
    },
    "🌊 C. Terre (D4-5)": {
        "meta": "28–29 mayo · Base: La Spezia · 2 noches",
        "alert": "💡 Estrategia: Alojarse en La Spezia (más económico, más opciones) y usar el tren local incluido en la Cinque Terre Card para moverse entre los 5 pueblos.",
        "hotel": {"n": "Hotel Firenze ★★★ (La Spezia)", "m": "5 min a pie de la estación · Habitación doble · 2 noches", "p": "~€70–80 / noche", "book": "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30", "air": "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30", "maps": "https://maps.google.com/?q=La+Spezia+train+station"},
        "days": [
            {"d": "Día 4", "date": "Jueves 28 mayo — Riomaggiore, Manarola, Corniglia", "events": [
                {"t": "11:30", "hi": False, "ttl": "Llegada La Spezia — Check-in + Cinque Terre Card", "desc": "Comprar la Card 2 días en InfoParco o taquilla de la estación (~€29.50/persona). Incluye todos los trenes locales.", "tags": '<span class="tag tag-train">🎫 €29.50 · 2 días</span> <a href="https://www.cinqueterre.eu.com/en/cinque-terre-card" target="_blank" class="btn btn-ticket">Info Card</a>'},
                {"t": "12:30", "hi": True, "ttl": "★ Riomaggiore — el más fotogénico", "desc": "Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre", "tags": '<span class="tag tag-food">🍃 Pesto original</span>'},
                {"t": "15:30", "hi": True, "ttl": "★ Manarola — el mirador icónico", "desc": "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre", "tags": '<span class="tag tag-walk">📸 Foto icónica</span>'},
                {"t": "17:30", "hi": False, "ttl": "Corniglia — vista 360°", "desc": "El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.", "maps": "https://maps.google.com/?q=Corniglia+Cinque+Terre"}
            ]},
            {"d": "Día 5", "date": "Viernes 29 mayo — Vernazza, senderismo y Monterosso", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Vernazza — el más medieval", "desc": "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.", "maps": "https://maps.google.com/?q=Vernazza+Cinque+Terre"},
                {"t": "11:00", "hi": True, "ttl": "★ Senderismo Vernazza → Monterosso (3.5 km · 2h)", "desc": "El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir. Llevar agua y zapatos.", "tip": "Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.", "maps": "https://maps.google.com/?q=Sentiero+Vernazza+Monterosso", "tags": '<span class="tag tag-walk">🥾 Trekking</span> <a href="https://www.parconazionale5terre.it" target="_blank" class="btn btn-ticket">Estado senderos</a>'},
                {"t": "14:00", "hi": False, "ttl": "Monterosso — playa y anchoas", "desc": "El único pueblo con playa de arena real. Probar acciughe (anchoas de Monterosso). Reposeras ~€5. Agua ~22°C.", "maps": "https://maps.google.com/?q=Monterosso+al+Mare", "tags": '<span class="tag tag-walk">🏖️ Playa</span>'}
            ]}
        ]
    },
    "🌸 Florencia (D6-9)": {
        "meta": "30 mayo – 2 junio · 4 noches",
        "hotel": {"n": "Hotel Davanzati ★★★ (recomendado)", "m": "2 min del Duomo y Uffizi · Desayuno excelente · Servicio muy bueno<br>Alternativa: B&B en Oltrarno (€70–80, más auténtico)", "p": "~€95–110 / noche · 4 noches", "book": "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03", "air": "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03", "maps": "https://maps.google.com/?q=Hotel+Davanzati+Florence"},
        "days": [
            {"d": "Día 6", "date": "Sábado 30 mayo — Duomo + Oltrarno + Piazzale", "events": [
                {"t": "11:00", "hi": True, "ttl": "★ Duomo + Cúpula de Brunelleschi", "desc": "463 escalones. Reservar turno online — sin reserva la fila es 2h+.", "maps": "https://maps.google.com/?q=Duomo+Florence", "tags": '<span class="tag tag-museum">⛪ Pase ~€20</span> <a href="https://www.ilgrandemuseodelduomo.it" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "13:00", "hi": False, "ttl": "Mercato Centrale — almuerzo", "desc": "Piso superior con puestos de comida. Probar lampredotto (para valientes) o pasta fresca.", "maps": "https://maps.google.com/?q=Mercato+Centrale+Florence"},
                {"t": "16:30", "hi": False, "ttl": "Ponte Vecchio → Oltrarno", "desc": "El puente con joyerías del siglo XVI. Al cruzar: el Florencia auténtico.", "maps": "https://maps.google.com/?q=Ponte+Vecchio+Florence"},
                {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo — atardecer", "desc": "EL punto de Florencia al atardecer. Vista panorámica de toda la ciudad. Llegar 30 min antes del sunset.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence", "tags": '<span class="tag tag-walk">🌅 Gratis</span>'}
            ]},
            {"d": "Día 7", "date": "Domingo 31 mayo — Uffizi + David + San Miniato", "events": [
                {"t": "08:30", "hi": True, "ttl": "★ Galería degli Uffizi", "desc": "El museo renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence", "tags": '<span class="tag tag-museum">🎨 €20 + €4 reserva</span> <a href="https://www.uffizi.it" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "14:00", "hi": True, "ttl": "★ David de Michelangelo — Accademia", "desc": "5.17 metros de mármol perfecto. El original, no la copia de la piazza. 1.5h.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence", "tags": '<span class="tag tag-museum">🗿 €12 + reserva</span> <a href="https://www.uffizi.it/en/the-accademia-gallery" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "17:30", "hi": False, "ttl": "San Miniato al Monte", "desc": "La iglesia más bella de Florencia para muchos. Entrada gratis. Canto gregoriano a las 17:30.", "maps": "https://maps.google.com/?q=San+Miniato+al+Monte+Florence"}
            ]},
            {"d": "Día 8", "date": "Lunes 1 junio — Pitti + Boboli + Cappelle Medicee", "events": [
                {"t": "09:00", "hi": False, "ttl": "Palazzo Pitti + Jardines de Boboli", "desc": "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina. Jardines renacentistas.", "maps": "https://maps.google.com/?q=Palazzo+Pitti+Florence", "tags": '<span class="tag tag-museum">🏰 €16</span>'},
                {"t": "16:00", "hi": True, "ttl": "★ Cappelle Medicee — Michelangelo", "desc": "Aurora, Crepúsculo, Día y Noche. Menos conocidas que el David, igual de impactantes.", "maps": "https://maps.google.com/?q=Cappelle+Medicee+Florence", "tags": '<span class="tag tag-museum">🗿 €9</span>'}
            ]},
            {"d": "Día 9", "date": "Martes 2 junio — Siena y Val d'Orcia", "events": [
                {"t": "07:30", "hi": False, "ttl": "Bus SENA a Siena", "desc": "Desde Autostazione di Firenze (frente a SMN). 1.5h · €9.", "maps": "https://maps.google.com/?q=Autostazione+Firenze", "tags": '<span class="tag tag-bus">🚌 €9</span>'},
                {"t": "09:00", "hi": True, "ttl": "★ Piazza del Campo + Torre del Mangia", "desc": "La plaza más bella de Italia. La Torre tiene 400 escalones y vista impresionante de los tejados rojizos.", "maps": "https://maps.google.com/?q=Piazza+del+Campo+Siena", "tags": '<span class="tag tag-museum">🏰 Torre €10</span>'},
                {"t": "10:30", "hi": False, "ttl": "Duomo di Siena", "desc": "Interior diferente al florentino. El pavimento de mármol es único.", "maps": "https://maps.google.com/?q=Siena+Cathedral"},
                {"t": "17:00", "hi": False, "ttl": "Bus de regreso a Florencia", "desc": "Hay buses frecuentes hasta las 21:00. Cena en Florencia. Mañana viajan a Roma."}
            ]}
        ]
    },
    "🏟️ Roma (D10-13)": {
        "meta": "3–6 junio · 4 noches",
        "alert": "🎾 Padel Nuestro Roma: La tienda está en el centro de Roma — mucho más conveniente que la de Milán. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Permiten probar palas.",
        "hotel": {"n": "Hotel Arco del Lauro ★★★ (Trastevere)", "m": "Zona auténtica · B&B familiar · Muy buenas reseñas · A pie del centro", "p": "~€80–95 / noche · 4 noches", "book": "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07", "air": "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07", "maps": "https://maps.google.com/?q=Trastevere+Rome"},
        "days": [
            {"d": "Día 10", "date": "Miércoles 3 junio — Vaticano completo", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos + Capilla Sixtina", "desc": "Los museos más visitados del mundo. 3–4h. RESERVA OBLIGATORIA con semanas de anticipación.", "tip": "⚠️ En la Capilla Sixtina: prohibido fotografiar y hacer ruido. Silencio absoluto.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome", "tags": '<span class="tag tag-museum">🎨 €17 + €4 reserva</span> <a href="https://www.museivaticani.va" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "14:00", "hi": False, "ttl": "Basílica de San Pedro + Cúpula", "desc": "La basílica más grande del mundo cristiano. Cúpula: 551 escalones o ascensor parcial (€8).", "maps": "https://maps.google.com/?q=St+Peters+Basilica+Rome", "tags": '<span class="tag tag-museum">⛪ Gratis · Cúpula €8</span>'}
            ]},
            {"d": "Día 11", "date": "Jueves 4 junio — Roma clásica imperial", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Coliseo + Foro Romano + Palatino", "desc": "Combo obligatorio. 3–4h. Reservar online para evitar 2h de fila.", "maps": "https://maps.google.com/?q=Colosseum+Rome", "tags": '<span class="tag tag-museum">🏛️ €16 + reserva</span> <a href="https://www.coopculture.it" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "17:30", "hi": False, "ttl": "Trastevere — paseo y cena", "desc": "El barrio medieval más pintoresco. Basílica di Santa Maria in Trastevere (siglo XII, gratis). Cena: Da Enzo al 29.", "maps": "https://maps.google.com/?q=Trastevere+Rome"}
            ]},
            {"d": "Día 12", "date": "Viernes 5 junio — Roma barroca + Borghese + Pádel", "events": [
                {"t": "09:00", "hi": False, "ttl": "Pantheon → Piazza Navona → Fontana di Trevi", "desc": "El Pantheon requiere ticket (€5 desde 2023). Trevi: lanzar la moneda de espaldas con la derecha.", "maps": "https://maps.google.com/?q=Pantheon+Rome", "tags": '<a href="https://maps.google.com/?q=Trevi+Fountain+Rome" target="_blank" class="btn btn-maps">📍 Trevi</a>'},
                {"t": "15:00", "hi": True, "ttl": "★ Galería Borghese — Bernini", "desc": "Solo 360 personas cada 2h. Apolo y Dafne, El rapto de Proserpina — lo más impactante de Roma.", "maps": "https://maps.google.com/?q=Galleria+Borghese+Rome", "tags": '<span class="tag tag-museum">🗿 €15 + €2 reserva</span> <a href="https://www.galleriaborghese.it" target="_blank" class="btn btn-ticket">🎟️ Reservar</a>'},
                {"t": "18:00", "hi": True, "ttl": "★ Padel Nuestro Roma", "desc": "La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Pista interior para probar palas.", "maps": "https://maps.google.com/?q=Padel+Nuestro+Roma+Italy", "tags": '<span class="tag tag-padel">🎾 Pádel Roma</span> <a href="https://www.padelnuestro.com" target="_blank" class="btn btn-ticket">Web tienda</a>'}
            ]},
            {"d": "Día 13", "date": "Sábado 6 junio — Castel Sant'Angelo + día libre", "events": [
                {"t": "09:00", "hi": False, "ttl": "Castel Sant'Angelo", "desc": "Mausoleo de Adriano convertido en fortaleza papal. Vista del Tiber y San Pedro desde la cima.", "maps": "https://maps.google.com/?q=Castel+Sant'Angelo+Rome", "tags": '<span class="tag tag-museum">🏰 €14</span>'},
                {"t": "14:00", "hi": False, "ttl": "Tarde libre + preparación", "desc": "Compras en Via del Corso o zona Spagna. Mañana temprano: tren a Nápoles."}
            ]}
        ]
    },
    "🍕 Nápoles (D14)": {
        "meta": "7 junio · 1 noche",
        "hotel": {"n": "Hotel Piazza Bellini ★★★ (centro histórico UNESCO)", "m": "En el corazón de Spaccanapoli · 1 noche (7–8 junio)", "p": "~€75–90 / noche", "book": "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08", "air": "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08", "maps": "https://maps.google.com/?q=Piazza+Bellini+Naples"},
        "days": [
            {"d": "Día 14", "date": "Domingo 7 junio — Pompeya + Nápoles", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Circumvesuviana → Pompeya Scavi", "desc": "Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento. Bajarse en 'Pompei Scavi'.", "maps": "https://maps.google.com/?q=Pompei+Scavi+station", "tags": '<span class="tag tag-train">🚂 €3 · 40min</span>'},
                {"t": "10:00", "hi": True, "ttl": "★ Pompeya — ciudad del 79 d.C.", "desc": "3h mínimo. Imprescindible: Casa dei Vettii, Anfiteatro, moldes humanos en el Granario. Llevar agua y sombrero.", "maps": "https://maps.google.com/?q=Pompeii+Archaeological+Park", "tags": '<span class="tag tag-museum">🌋 €16</span>'},
                {"t": "15:00", "hi": False, "ttl": "Spaccanapoli + Museo Arqueológico", "desc": "El mejor museo de arqueología romana del mundo. Los objetos de Pompeya y Herculano están aquí.", "maps": "https://maps.google.com/?q=National+Archaeological+Museum+Naples", "tags": '<span class="tag tag-museum">🏺 €15</span>'},
                {"t": "19:30", "hi": True, "ttl": "★ La pizza napolitana original", "desc": "Da Michele (solo Margherita y Marinara, fila larga) · Sorbillo (favorita de los napolitanos) · Di Matteo (Spaccanapoli).", "maps": "https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples", "tags": '<span class="tag tag-food">🍕 €5–8</span> <a href="https://maps.google.com/?q=L'Antica+Pizzeria+da+Michele+Naples" target="_blank" class="btn btn-maps">📍 Da Michele</a> <a href="https://maps.google.com/?q=Pizzeria+Sorbillo+Naples" target="_blank" class="btn btn-maps">📍 Sorbillo</a>'}
            ]}
        ]
    },
    "🌅 Amalfi (D15-16)": {
        "meta": "8–9 junio · Base: Praiano · 2 noches",
        "alert": "💰 Tip de presupuesto: Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200 fácilmente.",
        "hotel": {"n": "Albergo California (Praiano) ★★★", "m": "Vista al mar · Desayuno incluido · 10 min de Positano en ferry · 2 noches (8–10 junio)", "p": "~€85–100 / noche", "book": "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10", "air": "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10", "maps": "https://maps.google.com/?q=Praiano+Amalfi+Coast"},
        "days": [
            {"d": "Día 15", "date": "Lunes 8 junio — Positano + Amalfi", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Positano — las casas en cascada", "desc": "Playa Grande, el pueblo sobre el acantilado. Playa de guijarros, reposeras ~€20 el par. Agua ~22°C.", "maps": "https://maps.google.com/?q=Positano+Amalfi+Coast"},
                {"t": "15:00", "hi": True, "ttl": "★ Bus SITA → Amalfi ciudad", "desc": "La carretera más espectacular de Italia. Sentarse del lado DERECHO mirando al mar. Duomo árabe-normando del siglo IX.", "tip": "Comprar ticket en tabacchi antes de subir. €2.50 el tramo.", "maps": "https://maps.google.com/?q=Amalfi+Cathedral", "tags": '<span class="tag tag-bus">🚌 €2.50 · Lado derecho</span>'},
                {"t": "19:30", "hi": False, "ttl": "Cena con vista al mar", "desc": "El atardecer sobre el Tirreno desde la Costa Amalfi. Uno de los más bellos de Italia.", "tags": '<span class="tag tag-food">🌅 Scialatielli ai frutti</span>'}
            ]},
            {"d": "Día 16", "date": "Martes 9 junio — Ravello + Sentiero degli Dei", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Ravello — Villa Cimbrone + Terrazza dell'Infinito", "desc": "El balcón más bello del mundo según Wagner. Jardines sobre el precipicio. 350m sobre el mar.", "maps": "https://maps.google.com/?q=Villa+Cimbrone+Ravello", "tags": '<span class="tag tag-museum">🌿 €7</span>'},
                {"t": "11:00", "hi": True, "ttl": "★ Sentiero degli Dei — Camino de los Dioses", "desc": "El sendero más famoso de Amalfi. 7.8km · 3h · Desde Bomerano bajando a Positano. Vista de toda la costa desde 600m. Llevar agua, sombrero, calzado firme.", "tip": "El mejor día del viaje para muchos viajeros. Baja (no sube) — el cansancio es manejable.", "maps": "https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast", "tags": '<span class="tag tag-walk">🥾 Trekking</span>'},
                {"t": "15:00", "hi": False, "ttl": "Llegada Positano + playa merecida", "desc": "Después del sendero: baño en el Tirreno. Tarde libre. Mañana tren largo a Venecia — preparar maletas."}
            ]}
        ]
    },
    "🚤 Venecia (D17)": {
        "meta": "10 junio · 1 noche",
        "hotel": {"n": "Hotel Dalla Mora ★★★ (Santa Croce)", "m": "Zona auténtica · 10 min a pie de la estación · No en Mestre (tierra firme) — en Venecia real", "p": "~€90–110 / noche", "book": "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11", "air": "", "maps": "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice"},
        "days": [
            {"d": "Día 17", "date": "Miércoles 10 junio — Venecia completa", "events": [
                {"t": "13:00", "hi": True, "ttl": "★ Gran Canal en Vaporetto línea 1 (la lenta)", "desc": "45 minutos de palacios del siglo XIV. El paseo más cinematográfico del viaje. Ticket 24h vale la pena.", "maps": "https://maps.google.com/?q=Grand+Canal+Venice", "tags": '<span class="tag tag-boat">🚤 24h = €25</span>'},
                {"t": "15:00", "hi": True, "ttl": "★ Plaza San Marcos + Basílica + Campanile", "desc": "Basílica siglo XI, estilo bizantino, gratis con espera. Campanile €10 con la mejor vista de Venecia.", "maps": "https://maps.google.com/?q=St+Marks+Basilica+Venice", "tags": '<span class="tag tag-museum">🏛️ Gratis + €10 campanile</span>'},
                {"t": "17:00", "hi": True, "ttl": "★ Perderse sin mapa — la mejor actividad", "desc": "Apagar Google Maps. 118 islas, 400 puentes. Los callejones más angostos llevan a los campos más secretos.", "tags": '<span class="tag tag-walk">🗺️ Sin mapa</span>'},
                {"t": "19:30", "hi": False, "ttl": "Spritz veneziano en bacaro + Rialto", "desc": "El Spritz se inventó en Venecia. Cicchetti (tapas de €1–2). Zona Cannaregio para los más auténticos.", "maps": "https://maps.google.com/?q=Rialto+Bridge+Venice"},
                {"t": "21:00", "hi": False, "ttl": "Góndola nocturna (opcional)", "desc": "Precio fijo oficial: €80 para 30 min (hasta 6 personas). De noche los canales sin turistas son mágicos.", "tags": '<span class="tag tag-boat">🎭 €80 / góndola</span>'}
            ]}
        ]
    },
    "🇨🇭 Zurich (D18-20)": {
        "meta": "11–13 junio · 3 noches · Vuelo 14/6 a las 08:55",
        "alert": "⚠️ Vuelo el 14/6 a las 08:55: Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min. El día 13 preparar todo y dormir temprano.",
        "hotel": {"n": "Hotel Otter ★★ (Langstrasse) o IBIS City West", "m": "Zona cool y multicultural · A pie del casco histórico · 3 noches (11–14 junio)<br>Alternativa con vista: Hotel Limmatblick (~€120, sobre el río Limmat)", "p": "~€90–110 / noche", "book": "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14", "air": "", "maps": "https://maps.google.com/?q=Langstrasse+Zurich"},
        "days": [
            {"d": "Día 18", "date": "Jueves 11 junio — Llegada + Altstadt", "events": [
                {"t": "14:00", "hi": False, "ttl": "Bahnhofstrasse + Lago de Zurich", "desc": "La calle más cara del mundo. El lago al final es perfecto para una pausa. Cambio mental: de caos italiano a precisión suiza.", "maps": "https://maps.google.com/?q=Bahnhofstrasse+Zurich"},
                {"t": "15:30", "hi": True, "ttl": "★ Altstadt + Grossmünster", "desc": "Donde Zwinglio inició la Reforma Protestante (1519). Subir las torres (€5) para la vista de Zurich.", "maps": "https://maps.google.com/?q=Grossmunster+Zurich"},
                {"t": "18:00", "hi": False, "ttl": "Fraumünster — vitrales de Chagall (1970)", "desc": "5 vitrales de Marc Chagall en un edificio del siglo XIII. Entrada €5.", "maps": "https://maps.google.com/?q=Fraumunster+Zurich"}
            ]},
            {"d": "Día 19", "date": "Viernes 12 junio — Lago + ETH + Fondue", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Crucero Lago de Zurich", "desc": "ZSG opera cruceros. Recorrido corto 1h o largo 4h hasta Rapperswil. Los Alpes de fondo.", "maps": "https://maps.google.com/?q=Lake+Zurich+boat+tours", "tags": '<span class="tag tag-boat">⛵ €8–30</span> <a href="https://www.zsg.ch" target="_blank" class="btn btn-ticket">ZSG</a>'},
                {"t": "16:00", "hi": False, "ttl": "Polybahn → terraza ETH (vista gratis)", "desc": "El funicular universitario de 1889 sube a la ETH de Einstein. Vista de Zurich, el lago y los Alpes. Gratis.", "maps": "https://maps.google.com/?q=ETH+Zurich+terrace"},
                {"t": "20:00", "hi": True, "ttl": "★ Fondue suiza — Swiss Chuchi", "desc": "El plato nacional. Swiss Chuchi en el Altstadt. Experiencia completa ~€35–45/persona.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich", "tags": '<span class="tag tag-food">🧀 Fondue</span>'}
            ]},
            {"d": "Día 20", "date": "Sábado 13 junio — Uetliberg + Chocolates + Última noche", "events": [
                {"t": "09:00", "hi": False, "ttl": "Uetliberg — la montaña de Zurich", "desc": "Tren S10 desde HB, 20 min, €5. 870m de altura. Vista de Zurich, el lago y los Alpes. Bajada por sendero a Felsenegg.", "maps": "https://maps.google.com/?q=Uetliberg+Zurich", "tags": '<span class="tag tag-walk">⛰️ €5 tren</span>'},
                {"t": "13:00", "hi": True, "ttl": "★ Chocolates Sprüngli + Mercado Bürkliplatz", "desc": "Sprüngli (desde 1836) — los mejores truffes du jour de Zurich. Mercado de artesanías los sábados.", "maps": "https://maps.google.com/?q=Confiserie+Sprungli+Zurich"},
                {"t": "19:00", "hi": True, "ttl": "★ Última cena del viaje 🥂", "desc": "Elegir el mejor restaurante de los días en Zurich. Brindar por el viaje. Hacer check-in online del vuelo LA8799.", "tags": '<span class="tag tag-food">🥂 Despedida</span>'},
                {"t": "22:00", "hi": False, "ttl": "A dormir — vuelo 08:55 mañana", "desc": "Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración. Estar en aeropuerto a las 07:00.", "tip": "⚠️ ALARMA 06:00. No fallar.", "tags": '<span class="tag tag-sleep">✈️ Alarma 06:00</span>'}
            ]}
        ]
    }
}

# ─── 0. HERO Y STATS ──────────────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
    <div class="hero">
      <div class="hero-title">Italia & <em>Zurich</em></div>
      <div class="hero-sub">Luna de Miel · Adilson & Mirtha · Mayo – Junio 2026</div>
      <div class="hero-dates"><span>✈ Sale 24 mayo · Foz de Iguazú</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
    </div>
    <div class="stats-bar">
      <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
      <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
      <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div>
      <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
      <div class="stat-item" style="border:none;"><span class="stat-num">~€85</span><span class="stat-lbl">Hotel Avg</span></div>
    </div>
"""), unsafe_allow_html=True)

# ─── NAVEGACIÓN SUPERIOR (TABS en lugar de Sidebar) ───────────────────────────
t_res, t_iti, t_book, t_pre, t_tra, t_tip, t_not = st.tabs([
    "🌍 Vuelos y Ruta", "📅 Itinerario Diario", "🎟️ Reservas", "💰 Presupuesto", "🚄 Transportes", "💡 Tips", "📝 Notas"
])

# ─── 1. VUELOS Y RESUMEN ──────────────────────────────────────────────────────
with t_res:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">Ruta en U — Vista general</div><div class="section-meta">Norte → Sur → Norte → Suiza</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>⚠️ Reservas urgentes:</strong> La Última Cena (Da Vinci), Galería Borghese, Museos Vaticanos y Uffizi se agotan con meses de anticipación. Ir a la sección <strong>Reservas</strong> y gestionar hoy.</div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div class="card">
          <div class="card-header"><span class="day-badge">IDA</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--ink);">24 Mayo — Foz de Iguazú → Milán</span></div>
          <div class="t-row"><div class="t-time">14:50</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Vuelo LA3879 / LA8072</div><div class="t-desc">IGU 14:50 → GRU 16:30 (Conexión 1h30)<br>GRU 18:00 → MXP 10:15 (+1 día)</div><span class="tag tag-train">✈ LATAM Brasil</span> <span class="tag tag-train">1 parada · 14h25</span></div></div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">VUELTA</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--ink);">14 Junio — Zurich → Foz de Iguazú</span></div>
          <div class="t-row"><div class="t-time">08:55</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Vuelo LA8799 / LA8073 / LA3206</div><div class="t-desc">ZRH 08:55 → MXP 09:50 (Swiss, Conexión 3h10)<br>MXP 13:00 → GRU 20:00 (LATAM, Conexión 2h20)<br>GRU 22:20 → IGU 00:05 (+1 día)</div><span class="tag tag-train">✈ Swiss + LATAM</span> <span class="tag tag-train">2 paradas · 20h10</span></div></div>
        </div>
    """), unsafe_allow_html=True)

# ─── 2. ITINERARIO DIARIO ─────────────────────────────────────────────────────
with t_iti:
    ciudades = list(ITINERARIO_FULL.keys())
    ciudad_sel = st.radio("Selecciona una ciudad:", ciudades, horizontal=True, label_visibility="collapsed")
    
    data = ITINERARIO_FULL[ciudad_sel]
    nombre_limpio = ciudad_sel.split(" (")[0]
    
    st.markdown(f'<div class="section-header" style="margin-top:2rem;"><div class="section-title" style="color:var(--ink);">{nombre_limpio}</div><div class="section-meta">{data["meta"]}</div></div>', unsafe_allow_html=True)
    if "alert" in data:
        st.markdown(f'<div class="alert"><strong>{data["alert"].split(":")[0]}:</strong> {data["alert"].split(":")[1]}</div>', unsafe_allow_html=True)
    
    h = data["hotel"]
    bb = f'<a href="{h["book"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if h.get("book") else ""
    ba = f'<a href="{h["air"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if h.get("air") else ""
    st.markdown(f'<div class="hotel-card"><div style="font-family:\'Playfair Display\';font-size:1.15rem;color:var(--ink);font-weight:600;">{h["n"]}</div><div style="font-size:0.85rem;color:var(--slate-light);margin-bottom:8px;line-height:1.5;">{h["m"]}</div><div style="display:inline-block;background:rgba(107,122,62,0.1);color:var(--olive);padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-bottom:10px;">{h["p"]}</div><br>{bb} {ba} <a href="{h["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a></div>', unsafe_allow_html=True)
    
    for day in data["days"]:
        st.markdown(f'<div class="card-header" style="margin-top:1.5rem; border-radius:12px 12px 0 0;"><span class="day-badge">{day["d"]}</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--ink);">{day["date"]}</span></div>', unsafe_allow_html=True)
        html_events = '<div class="card" style="border-top:none; border-radius:0 0 12px 12px; margin-bottom:0;">'
        for ev in day["events"]:
            dc = "hi" if ev.get("hi") else ""
            sc = "star" if ev.get("hi") else ""
            tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
            bm = f'<a href="{ev["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if "maps" in ev else ""
            tags = ev.get("tags", "")
            html_events += f'<div class="t-row"><div class="t-time">{ev["t"]}</div><div class="t-dot {dc}"></div><div class="t-content"><div class="t-ttl {sc}">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip}<div style="margin-top:8px;">{tags} {bm}</div></div></div>'
        html_events += '</div>'
        st.markdown(html_events, unsafe_allow_html=True)

# ─── 3. RESERVAS ──────────────────────────────────────────────────────────────
with t_book:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">Tracker de Reservas</div><div class="section-meta">Enlaces oficiales directos</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>Prioridad máxima:</strong> La Última Cena y Galería Borghese se agotan con meses de anticipación.</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, r in enumerate(RESERVAS_DATA):
        with cols[i % 2]:
            st.markdown(f'<div class="card" style="padding:1.2rem;margin-bottom:1rem;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div style="font-size:0.95rem;font-weight:600;color:var(--ink);">{r["tit"]}</div><div style="font-size:0.65rem;background:#FEF3CD;color:#8B6914;padding:3px 10px;border-radius:20px;font-weight:600;">⏳ Pendiente</div></div><div style="font-size:0.8rem;color:var(--slate-light);margin-top:6px;margin-bottom:10px;">{r["urg"]} · {r["det"]}</div><a href="{r["url"]}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;font-size:0.75rem;color:var(--terracotta);text-decoration:none;font-weight:600;">🔗 Ir al sitio oficial →</a></div>', unsafe_allow_html=True)
    df_r = load_sheet_data("viaje_reservas")
    if not df_r.empty: st.dataframe(df_r, use_container_width=True, hide_index=True)

# ─── 4. PRESUPUESTO ───────────────────────────────────────────────────────────
with t_pre:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">Presupuesto estimado</div><div class="section-meta">Para 2 personas · 20 días</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; margin-bottom:2rem;">
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Alojamiento (20 noches)</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€1.900</div><div style="font-size:0.72rem;color:var(--slate-light);margin-top:2px;">Promedio €95/noche</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Transportes internos</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€500</div><div style="font-size:0.72rem;color:var(--slate-light);margin-top:2px;">Trenes + ferries + buses</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Entradas museos</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€350</div><div style="font-size:0.72rem;color:var(--slate-light);margin-top:2px;">Para 2 personas</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Comidas (€60/día)</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€1.200</div><div style="font-size:0.72rem;color:var(--slate-light);margin-top:2px;">Desayuno + almuerzo + cena</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Imprevistos (10%)</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€400</div><div style="font-size:0.72rem;color:var(--slate-light);margin-top:2px;">Compras, extras</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0; background:rgba(196,105,58,0.05); border-color:var(--terracotta);"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--terracotta-dark);font-weight:600;margin-bottom:4px;">TOTAL ESTIMADO</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€4.350</div><div style="font-size:0.72rem;color:var(--terracotta-dark);margin-top:2px;">Sin vuelos · Para 2</div></div>
        </div>
    """), unsafe_allow_html=True)
    
    st.markdown('<div class="card"><div class="card-header"><span class="day-badge">Desglose</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--ink);">Alojamiento por ciudad</span></div>', unsafe_allow_html=True)
    html_table = '<table class="budget-table"><thead><tr><th>Ciudad</th><th>Noches</th><th>€/Noche</th><th>Total</th><th>Booking</th><th>Airbnb</th></tr></thead><tbody>'
    for p in PRESUPUESTO_DATA:
        b_btn = f'<a href="{p["b"]}" target="_blank" class="btn btn-booking" style="font-size:0.65rem;padding:2px 6px;">Book</a>' if p["b"] else "—"
        a_btn = f'<a href="{p["a"]}" target="_blank" class="btn btn-airbnb" style="font-size:0.65rem;padding:2px 6px;">Airbnb</a>' if p["a"] else "—"
        html_table += f'<tr><td>{p["Ciudad"]}</td><td>{p["Noches"]}</td><td>{p["€/noche"]}</td><td>{p["Total"]}</td><td>{b_btn}</td><td>{a_btn}</td></tr>'
    html_table += '<tr style="border-top:2px solid var(--terracotta-light);font-weight:700;color:var(--terracotta-dark);font-size:0.9rem;"><td>Total alojamiento</td><td>20</td><td>~€95</td><td>~€1.805</td><td>—</td><td>—</td></tr></tbody></table></div>'
    st.markdown(html_table, unsafe_allow_html=True)

# ─── 5. TRANSPORTES ───────────────────────────────────────────────────────────
with t_tra:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">Todos los transportes</div><div class="section-meta">En orden cronológico · Con links oficiales</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-green"><strong>Truco de precio:</strong> Comprar trenes con 60 días de anticipación puede costar 4 veces menos que el día del viaje. Frecciarossa Roma→Nápoles: €9 anticipado vs €55 último momento.</div>', unsafe_allow_html=True)
    for t in TRANSPORTES_DATA:
        st.markdown(f"""
        <div class="transport-card">
          <div style="font-size:1.8rem; min-width:50px; text-align:center;">{t['ico']}</div>
          <div style="flex:1;">
            <div style="font-size:1rem; font-weight:600; color:var(--ink); margin-bottom:2px;">{t['r']}</div>
            <div style="font-size:0.85rem; color:var(--slate-light);">{t['d']}</div>
          </div>
          <div style="font-size:0.95rem; font-weight:700; color:var(--terracotta); padding:0 15px;">{t['p']}</div>
          <a href="{t['u']}" target="_blank" class="btn btn-trenitalia">Comprar</a>
        </div>
        """, unsafe_allow_html=True)

# ─── 6. TIPS ──────────────────────────────────────────────────────────────────
with t_tip:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">12 Tips esenciales</div><div class="section-meta">Lo que marca la diferencia</div></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (tit, txt) in enumerate(TIPS_DATA):
        with cols[i % 3]:
            icon, title = tit.split(" ", 1)
            st.markdown(f'<div class="card" style="height:92%; padding:1.2rem;"><div style="font-size:1.5rem; margin-bottom:5px;">{icon}</div><strong style="font-size:0.95rem; color:var(--ink);">{title}</strong><br><span style="font-size:0.85rem;color:var(--slate-light);display:block;margin-top:8px;line-height:1.5;">{txt}</span></div>', unsafe_allow_html=True)

# ─── 7. NOTAS ─────────────────────────────────────────────────────────────────
with t_not:
    st.markdown('<div class="section-header"><div class="section-title" style="color:var(--ink);">Notas Compartidas</div><div class="section-meta">Sincronizado en tiempo real con Google Sheets</div></div>', unsafe_allow_html=True)
    with st.form("new_note", clear_on_submit=True):
        n_txt = st.text_area("Nueva nota:", placeholder="Ej: No olvidar llevar adaptador de enchufe suizo (es distinto al de Italia)...")
        n_aut = st.selectbox("Quién escribe:", ["Adilson", "Mirtha"])
        if st.form_submit_button("📤 Publicar nota en Sheets"):
            if n_txt:
                if add_nota(n_txt, n_aut): st.success("Nota publicada correctamente ✓")
    df_n = load_sheet_data("viaje_notas")
    if not df_n.empty and 'texto' in df_n.columns:
        for _, r in df_n.iloc[::-1].iterrows():
            st.markdown(f'<div class="card" style="padding:1.2rem; border-left: 4px solid var(--gold);"><strong style="font-size:0.95rem; color:var(--ink);">{r.get("autor","")}</strong><div style="margin:10px 0;font-size:0.9rem;color:var(--slate-light);line-height:1.5;">{r.get("texto","")}</div><small style="color:var(--terracotta);font-weight:600;">🕐 {r.get("fecha","")}</small></div>', unsafe_allow_html=True)
