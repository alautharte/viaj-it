import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide")

# ─── ESTILOS CSS (Copia fiel del HTML) ────────────────────────────────────────
st.markdown(textwrap.dedent("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
  
  :root {
    --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --terracotta-light: #E8956D;
    --terracotta-dark: #8B3E1E; --olive: #6B7A3E; --olive-light: #9AAD5A; --slate: #3D4A5C;
    --slate-light: #6B7A8D; --gold: #C9A84C; --gold-light: #E8C96A; --ink: #1A1A2E; --white: #FFFFFF;
  }
  .stApp { background: var(--cream); }
  
  /* Sidebar */
  [data-testid="stSidebar"] { background-color: #1A1A2E !important; border-right: 1px solid rgba(255,255,255,0.1); }
  [data-testid="stSidebar"] * { color: #F7F3EE !important; font-family: 'DM Sans', sans-serif; }
  [data-testid="stSidebar"] .stRadio label { background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 6px; margin-bottom: 5px; cursor: pointer; }
  [data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.1); color: var(--cream) !important; }

  /* Tipografía General */
  html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }

  /* Hero y Stats */
  .hero { background: var(--slate); padding: 3rem 2rem 2rem; text-align: center; margin: -6rem -5rem 0 -5rem; position: relative; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: var(--cream); line-height: 1.1; margin-bottom: 0.5rem; }
  .hero-title em { color: var(--gold-light); font-style: italic; }
  .hero-sub { font-size: 0.95rem; color: rgba(247,243,238,0.65); letter-spacing: 0.05em; margin-bottom: 1.5rem; }
  .hero-dates { display: inline-flex; gap: 1rem; background: rgba(247,243,238,0.1); border: 0.5px solid rgba(247,243,238,0.2); border-radius: 50px; padding: 0.5rem 1.5rem; font-size: 0.85rem; color: var(--gold-light); }
  
  .stats-bar { display: flex; justify-content: center; background: var(--terracotta); margin: 0 -5rem 2.5rem -5rem; }
  .stat-item { flex: 1; padding: 1rem; text-align: center; border-right: 0.5px solid rgba(247,243,238,0.2); }
  .stat-num { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--cream); display: block; font-weight: 600; line-height: 1; }
  .stat-lbl { font-size: 0.7rem; color: rgba(247,243,238,0.7); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; display: block; }

  /* Headers */
  .section-header { display: flex; align-items: flex-end; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--parchment); }
  .section-title { font-family: 'Playfair Display', serif; font-size: 2rem; color: var(--terracotta-dark); }
  .section-meta { font-size: 0.85rem; color: var(--slate-light); margin-top: 4px; }
  
  /* Cards */
  .card { background: var(--white); border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(26,26,46,0.08); overflow: hidden; }
  .card-header { display: flex; align-items: center; gap: 10px; padding: 0.75rem 1rem; background: var(--parchment); border-bottom: 1px solid rgba(196,105,58,0.15); }
  .day-badge { background: var(--terracotta); color: var(--white); font-size: 0.7rem; font-weight: 600; padding: 3px 12px; border-radius: 20px; }
  
  /* Timeline */
  .t-row { display: grid; grid-template-columns: 55px 16px 1fr; gap: 0 10px; padding: 12px 20px; border-bottom: 1px solid var(--parchment); }
  .t-time { font-size: 0.8rem; color: var(--slate-light); text-align: right; padding-top: 3px; font-weight: 500; font-variant-numeric: tabular-nums; }
  .t-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--parchment); border: 2px solid var(--terracotta-light); margin-top: 6px; }
  .t-dot.hi { background: var(--terracotta); border-color: var(--terracotta-dark); }
  .t-ttl { font-size: 0.95rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .t-ttl.star::before { content: '★ '; color: #C9A84C; }
  .t-desc { font-size: 0.85rem; color: var(--slate-light); line-height: 1.5; }
  .t-tip { font-size: 0.75rem; color: var(--terracotta-dark); background: rgba(196,105,58,0.07); border-left: 2px solid var(--terracotta-light); padding: 6px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; }
  
  /* Botones y Tablas */
  .btn { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; padding: 5px 12px; border-radius: 6px; border: 1px solid; text-decoration: none !important; font-weight: 500; margin: 8px 8px 0 0; background: white; transition: all 0.15s; }
  .btn-maps { border-color: #4285F4; color: #4285F4 !important; }
  .btn-booking { border-color: #003580; color: #003580 !important; }
  .btn-airbnb { border-color: #FF5A5F; color: #FF5A5F !important; }
  .btn-ticket { border-color: var(--olive); color: var(--olive) !important; }
  .btn-trenitalia { border-color: #B8000A; color: #B8000A !important; }
  .btn:hover { opacity: 0.8; }
  
  .budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 5px; }
  .budget-table th { text-align: left; padding: 12px; background: var(--parchment); color: var(--slate); font-size: 0.75rem; text-transform: uppercase; }
  .budget-table td { padding: 12px; border-bottom: 1px solid var(--parchment); color: var(--slate); }

  /* Hotel & Transport Cards */
  .hotel-card { border: 1px solid var(--parchment); border-radius: 10px; padding: 1.2rem; margin: 0.75rem 0 1.5rem 0; background: var(--white); box-shadow: 0 1px 4px rgba(0,0,0,0.05); }
  .transport-card { background: rgba(61,74,92,0.05); border: 1px solid rgba(61,74,92,0.12); border-radius: 10px; padding: 1rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 15px; }
  
  /* Alertas */
  .alert { background: rgba(196,105,58,0.08); border: 1px solid rgba(196,105,58,0.25); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.85rem; color: var(--terracotta-dark); margin-bottom: 1.5rem; }
  .alert-green { background: rgba(107,122,62,0.08); border-color: rgba(107,122,62,0.25); color: var(--olive); }

  #MainMenu {visibility: hidden;} footer {visibility: hidden;}
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

# ─── DATA COMPLETA (Extraída 100% del HTML) ───────────────────────────────────

# 1. RESERVAS
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

# 2. TRANSPORTES
TRANSPORTES_DATA = [
    {"ico": "✈️→🚄", "r": "MXP → Milano Centrale", "d": "Malpensa Express · 52 min · Sale cada 30 min", "p": "€13/p", "u": "https://www.trenord.it"},
    {"ico": "🚄", "r": "Milano → La Spezia", "d": "Intercity · ~3h · Salida 08:10", "p": "€25–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "La Spezia ↔ Cinque Terre", "d": "Tren regional · 5–12 min entre pueblos · Incluido en Cinque Terre Card", "p": "Incluido", "u": "https://www.cinqueterre.eu.com"},
    {"ico": "🚄", "r": "La Spezia → Firenze SMN", "d": "Intercity · ~2h · Salida 08:30", "p": "€15–20", "u": "https://www.trenitalia.com"},
    {"ico": "🚌", "r": "Firenze ↔ Siena", "d": "Bus SENA · 1h30 · Sale cada hora desde Autostazione", "p": "€9", "u": "https://www.tiemmespa.it"},
    {"ico": "🚄", "r": "Firenze → Roma Termini", "d": "Frecciarossa · 1h30 · Sale cada 30 min", "p": "€25–45", "u": "https://www.trenitalia.com"},
    {"ico": "🚄", "r": "Roma → Napoli", "d": "Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00", "p": "€20–35", "u": "https://www.trenitalia.com"},
    {"ico": "🚂", "r": "Napoli → Pompei Scavi", "d": "Circumvesuviana · 40 min · Andén -1 de Napoli Centrale", "p": "€3", "u": "https://www.eavsrl.it"},
    {"ico": "⛵", "r": "Napoli → Positano (ferry)", "d": "SNAV o Alilauro · Molo Beverello · 65 min · Solo mayo–oct", "p": "€20/p", "u": "https://www.alilauro.it"},
    {"ico": "🚌", "r": "Costa Amalfi (bus SITA)", "d": "Positano ↔ Amalfi ↔ Ravello · Ticket en tabacchi", "p": "€2.50/tramo", "u": "https://www.sitasudtrasporti.it"},
    {"ico": "🚄", "r": "Napoli → Venezia S. Lucia", "d": "Frecciarossa directo · 4h50 · Salida 07:30–08:00", "p": "€35–60", "u": "https://www.trenitalia.com"},
    {"ico": "🚤", "r": "Vaporetto Venecia (24h)", "d": "Línea 1 = Gran Canal completo · Línea 2 = rápida", "p": "€25 · 24h", "u": "https://actv.avmspa.it"},
    {"ico": "🚄", "r": "Venezia → Zurich HB (Alpes)", "d": "EuroCity directo · 4h45 · Paisaje alpino · SBB.ch", "p": "€40–60", "u": "https://www.sbb.ch"},
    {"ico": "🚄", "r": "Zurich HB → Aeropuerto ZRH", "d": "SBB · 10 min · Sale cada 10 min · Andén S-Bahn", "p": "€4", "u": "https://www.sbb.ch"}
]

# 3. TIPS
TIPS_DATA = [
    ("☕ Café en la barra", "Parado en la barra = €1.20. Sentado en mesa = €3–5. La ley lo establece — tienen que mostrar ambos precios en la carta."),
    ("💧 Agua del grifo", "Potable en toda Italia. Pedir 'acqua del rubinetto' en restaurantes — gratis. El agua mineral embotellada en mesa = €3–5."),
    ("🍽️ Menú del giorno", "Primer plato + segundo + bebida + pan = €12–15. Solo al almuerzo. La cena siempre es más cara. Buscar el menú escrito en pizarra afuera."),
    ("💳 Revolut o Wise", "Para no pagar comisiones de cambio. En Suiza: cambiar a CHF francos suizos al llegar. 1 CHF ≈ €1.05. No todos aceptan euros en Zurich."),
    ("👟 Zapatos (fundamental)", "10–15 km por día en adoquines. Amalfi y Cinque Terre requieren suela firme. Zapatillas de running funcionan bien."),
    ("🕌 Ropa para iglesias", "Hombros y rodillas cubiertos. Llevar una bufanda liviana — sirve para ambos. En verano hace calor pero las iglesias lo exigen."),
    ("🚌 Bus SITA Amalfi", "Comprar ticket en tabacchi (estanco) ANTES de subir. €2.50 el tramo. Sentarse del lado derecho mirando al mar Positano→Amalfi."),
    ("🍦 Gelato auténtico", "Colores apagados (no fluo), tapado con espátula, no en montañas. Si está en la vitrina brillante como plástico: es industrial."),
    ("📱 Apps esenciales", "Trenitalia + Italo (trenes) · Maps.me offline · TheFork para restaurantes · Revolut para pagos · SBB para Suiza."),
    ("🎾 Pádel — Padel Nuestro Roma", "La mejor tienda en la ruta. Centro de Roma. Bullpadel, Siux, Babolat, Head, Star Vie. Pista interior para probar palas. Día 12 por la tarde."),
    ("🛍️ Ropa barata — Corso Buenos Aires", "La calle comercial más larga de Italia. Milán. Zara, H&M, Bershka, marcas italianas accesibles. 2km de tiendas. Día 2 por la tarde."),
    ("🧀 Suiza — Fondue y chocolate", "Sprüngli (desde 1836) para chocolates en Zurich. Fondue en Swiss Chuchi. En Suiza todo es más caro que Italia — presupuestar €80–100/día para comidas.")
]

# 4. ITINERARIO (20 DÍAS COMPLETOS)
ITINERARIO_FULL = {
    "Milán": {
        "meta": "Días 1–3 · 25, 26 y 27 mayo · 3 noches",
        "hotel": {"n": "Hotel Ariston ★★★ (o similar zona Centrale/Navigli)", "m": "Central para metro · Desayuno incluido · Habitación doble<br>Alternativa premium: Hotel Dei Cavalieri (junto al Duomo, ~€110/noche)", "p": "~€70–90", "book": "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28", "air": "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28", "maps": "https://maps.google.com/?q=Hotel+Ariston+Milan"},
        "days": [
            {"d": "Día 1", "date": "Lunes 25 mayo — Llegada y primer paseo", "events": [
                {"t": "10:15", "hi": True, "ttl": "Llegada MXP — Inmigración y aduana", "desc": "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta."},
                {"t": "11:30", "hi": False, "ttl": "Malpensa Express → Milano Centrale", "desc": "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station"},
                {"t": "13:30", "hi": False, "ttl": "Check-in + almuerzo tranquilo", "desc": "Pedir risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones."},
                {"t": "15:00", "hi": False, "ttl": "Siesta obligatoria", "desc": "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes."},
                {"t": "18:00", "hi": False, "ttl": "Paseo Navigli + Aperitivo", "desc": "Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.", "maps": "https://maps.google.com/?q=Navigli+Milan"}
            ]},
            {"d": "Día 2", "date": "Martes 26 mayo — Duomo, Última Cena, Shopping y Pádel", "events": [
                {"t": "08:00", "hi": False, "ttl": "Desayuno italiano", "desc": "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía."},
                {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA — Santa Maria delle Grazie", "desc": "El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.", "tip": "⚠️ CRÍTICO: Reservar hoy mismo. Los cupos de mayo se agotan meses antes.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
                {"t": "10:00", "hi": True, "ttl": "★ Duomo di Milano", "desc": "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán.", "maps": "https://maps.google.com/?q=Duomo+di+Milano"},
                {"t": "11:30", "hi": False, "ttl": "Galleria Vittorio Emanuele II + Scala", "desc": "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).", "maps": "https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II+Milan"},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo en Brera", "desc": "Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15.", "maps": "https://maps.google.com/?q=Brera+Milan"},
                {"t": "15:00", "hi": True, "ttl": "★ Shopping — Corso Buenos Aires", "desc": "La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas accesibles. 2km de tiendas.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan"},
                {"t": "17:30", "hi": True, "ttl": "★ Padel Nuestro Milano (opcional)", "desc": "La mayor tienda de pádel del norte de Italia. Tienen pista interior para probar palas.", "tip": "Más conveniente visitar Padel Nuestro Roma (centro) que ésta (40 min del centro).", "maps": "https://maps.google.com/?q=Via+Papa+Giovanni+XXIII+9a+Rodano+Millepini+Milan"},
                {"t": "20:00", "hi": False, "ttl": "Cena en Navigli", "desc": "Evitar restaurantes con foto en el menú en la puerta — señal de trampa turística."}
            ]},
            {"d": "Día 3", "date": "Miércoles 27 mayo — Brera, Isola y preparación", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Pinacoteca di Brera", "desc": "Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia. Calcular 2h.", "maps": "https://maps.google.com/?q=Pinacoteca+di+Brera+Milan"},
                {"t": "11:30", "hi": False, "ttl": "Barrio Isola + Bosco Verticale", "desc": "El famoso 'bosque vertical' de Stefano Boeri. El barrio Isola tiene cafés y mercaditos locales.", "maps": "https://maps.google.com/?q=Bosco+Verticale+Milan"},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo + tarde libre", "desc": "Zona Sant'Ambrogio. Tarde para compras adicionales o descanso."},
                {"t": "19:00", "hi": False, "ttl": "Preparar maletas — mañana viajan a Cinque Terre", "desc": "Tren 08:10 desde Milano Centrale. Poner alarma."}
            ]}
        ]
    },
    "Cinque Terre": {
        "meta": "Días 4–5 · 28–29 mayo · Base: La Spezia · 2 noches",
        "alert": "Estrategia: Alojarse en La Spezia (más económico, más opciones) y usar el tren local incluido en la Cinque Terre Card.",
        "hotel": {"n": "Hotel Firenze ★★★ (La Spezia)", "m": "5 min a pie de la estación · Habitación doble", "p": "~€70–80", "book": "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28", "air": "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28", "maps": "https://maps.google.com/?q=La+Spezia+train+station"},
        "days": [
            {"d": "Día 4", "date": "Jueves 28 mayo — Riomaggiore, Manarola, Corniglia", "events": [
                {"t": "11:30", "hi": False, "ttl": "Llegada La Spezia — Check-in + Cinque Terre Card", "desc": "Comprar la Card 2 días en InfoParco (~€29.50/persona). Incluye todos los trenes locales."},
                {"t": "12:30", "hi": True, "ttl": "★ Riomaggiore — el más fotogénico", "desc": "Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
                {"t": "15:30", "hi": True, "ttl": "★ Manarola — el mirador icónico", "desc": "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"},
                {"t": "17:30", "hi": False, "ttl": "Corniglia — vista 360°", "desc": "El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.", "maps": "https://maps.google.com/?q=Corniglia+Cinque+Terre"}
            ]},
            {"d": "Día 5", "date": "Viernes 29 mayo — Vernazza, senderismo y Monterosso", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Vernazza — el más medieval", "desc": "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.", "maps": "https://maps.google.com/?q=Vernazza+Cinque+Terre"},
                {"t": "11:00", "hi": True, "ttl": "★ Senderismo Vernazza → Monterosso (3.5 km · 2h)", "desc": "El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir.", "tip": "Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.", "maps": "https://maps.google.com/?q=Sentiero+Vernazza+Monterosso"},
                {"t": "14:00", "hi": False, "ttl": "Monterosso — playa y anchoas", "desc": "El único pueblo con playa de arena real. Probar acciughe. Agua ~22°C en junio.", "maps": "https://maps.google.com/?q=Monterosso+al+Mare"}
            ]}
        ]
    },
    "Florencia": {
        "meta": "Días 6–9 · 30 mayo – 2 junio · 4 noches",
        "hotel": {"n": "Hotel Davanzati ★★★ (recomendado)", "m": "2 min del Duomo y Uffizi · Desayuno excelente<br>Alternativa: B&B en Oltrarno (€70–80, más auténtico)", "p": "~€95–110", "book": "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30", "air": "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30", "maps": "https://maps.google.com/?q=Hotel+Davanzati+Florence"},
        "days": [
            {"d": "Día 6", "date": "Sábado 30 mayo — Duomo + Oltrarno + Piazzale", "events": [
                {"t": "11:00", "hi": True, "ttl": "★ Duomo + Cúpula de Brunelleschi", "desc": "463 escalones. Reservar turno online — sin reserva la fila es 2h+.", "maps": "https://maps.google.com/?q=Duomo+Florence"},
                {"t": "13:00", "hi": False, "ttl": "Mercato Centrale — almuerzo", "desc": "Piso superior con puestos de comida. Probar lampredotto o pasta fresca.", "maps": "https://maps.google.com/?q=Mercato+Centrale+Florence"},
                {"t": "16:30", "hi": False, "ttl": "Ponte Vecchio → Oltrarno", "desc": "El puente con joyerías del siglo XVI. Al cruzar: el Florencia auténtico.", "maps": "https://maps.google.com/?q=Ponte+Vecchio+Florence"},
                {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo — atardecer", "desc": "EL punto de Florencia al atardecer. Vista panorámica de toda la ciudad.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence"}
            ]},
            {"d": "Día 7", "date": "Domingo 31 mayo — Uffizi + David + San Miniato", "events": [
                {"t": "08:30", "hi": True, "ttl": "★ Galería degli Uffizi", "desc": "El museo renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence"},
                {"t": "14:00", "hi": True, "ttl": "★ David de Michelangelo — Accademia", "desc": "5.17 metros de mármol perfecto. El original. 1.5h.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence"},
                {"t": "17:30", "hi": False, "ttl": "San Miniato al Monte", "desc": "La iglesia más bella de Florencia. Gratis. Canto gregoriano a las 17:30.", "maps": "https://maps.google.com/?q=San+Miniato+al+Monte+Florence"}
            ]},
            {"d": "Día 8", "date": "Lunes 1 junio — Pitti + Boboli + Cappelle Medicee", "events": [
                {"t": "09:00", "hi": False, "ttl": "Palazzo Pitti + Jardines de Boboli", "desc": "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina.", "maps": "https://maps.google.com/?q=Palazzo+Pitti+Florence"},
                {"t": "16:00", "hi": True, "ttl": "★ Cappelle Medicee — Michelangelo", "desc": "Aurora, Crepúsculo, Día y Noche. Igual de impactantes que el David.", "maps": "https://maps.google.com/?q=Cappelle+Medicee+Florence"}
            ]},
            {"d": "Día 9", "date": "Martes 2 junio — Siena y Val d'Orcia", "events": [
                {"t": "07:30", "hi": False, "ttl": "Bus SENA a Siena", "desc": "Desde Autostazione di Firenze. 1.5h · €9.", "maps": "https://maps.google.com/?q=Autostazione+Firenze"},
                {"t": "09:00", "hi": True, "ttl": "★ Piazza del Campo + Torre del Mangia", "desc": "La plaza más bella de Italia. La Torre tiene 400 escalones.", "maps": "https://maps.google.com/?q=Piazza+del+Campo+Siena"},
                {"t": "17:00", "hi": False, "ttl": "Bus de regreso a Florencia", "desc": "Hay buses frecuentes hasta las 21:00. Cena en Florencia."}
            ]}
        ]
    },
    "Roma": {
        "meta": "Días 10–13 · 3–6 junio · 4 noches",
        "alert": "🎾 Padel Nuestro Roma: La tienda está en el centro de Roma — mucho más conveniente que la de Milán. Permiten probar palas.",
        "hotel": {"n": "Hotel Arco del Lauro ★★★ (Trastevere)", "m": "Zona auténtica · B&B familiar · A pie del centro", "p": "~€80–95", "book": "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03", "air": "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03", "maps": "https://maps.google.com/?q=Trastevere+Rome"},
        "days": [
            {"d": "Día 10", "date": "Miércoles 3 junio — Vaticano completo", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos + Capilla Sixtina", "desc": "3–4h. RESERVA OBLIGATORIA con semanas de anticipación.", "tip": "⚠️ En la Capilla Sixtina: prohibido fotografiar y hacer ruido.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome"},
                {"t": "14:00", "hi": False, "ttl": "Basílica de San Pedro + Cúpula", "desc": "Cúpula: 551 escalones o ascensor parcial (€8).", "maps": "https://maps.google.com/?q=St+Peters+Basilica+Rome"}
            ]},
            {"d": "Día 11", "date": "Jueves 4 junio — Roma clásica imperial", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Coliseo + Foro Romano + Palatino", "desc": "Combo obligatorio. 3–4h. Reservar online para evitar 2h de fila.", "maps": "https://maps.google.com/?q=Colosseum+Rome"},
                {"t": "17:30", "hi": False, "ttl": "Trastevere — paseo y cena", "desc": "El barrio medieval más pintoresco. Cena: Da Enzo al 29.", "maps": "https://maps.google.com/?q=Trastevere+Rome"}
            ]},
            {"d": "Día 12", "date": "Viernes 5 junio — Roma barroca + Borghese + Pádel", "events": [
                {"t": "09:00", "hi": False, "ttl": "Pantheon → Piazza Navona → Fontana di Trevi", "desc": "Pantheon requiere ticket (€5). Trevi: lanzar moneda de espaldas.", "maps": "https://maps.google.com/?q=Pantheon+Rome"},
                {"t": "15:00", "hi": True, "ttl": "★ Galería Borghese — Bernini", "desc": "Solo 360 personas cada 2h. Apolo y Dafne, El rapto de Proserpina.", "maps": "https://maps.google.com/?q=Galleria+Borghese+Rome"},
                {"t": "18:00", "hi": True, "ttl": "★ Padel Nuestro Roma", "desc": "La tienda más completa de pádel en Roma. Pista interior para probar palas.", "maps": "https://maps.google.com/?q=Padel+Nuestro+Roma+Italy"}
            ]},
            {"d": "Día 13", "date": "Sábado 6 junio — Castel Sant'Angelo + día libre", "events": [
                {"t": "09:00", "hi": False, "ttl": "Castel Sant'Angelo", "desc": "Mausoleo de Adriano. Vista del Tiber y San Pedro.", "maps": "https://maps.google.com/?q=Castel+Sant'Angelo+Rome"},
                {"t": "14:00", "hi": False, "ttl": "Tarde libre + preparación", "desc": "Compras en Via del Corso. Mañana temprano: tren a Nápoles."}
            ]}
        ]
    },
    "Nápoles": {
        "meta": "Día 14 · 7 junio · 1 noche",
        "hotel": {"n": "Hotel Piazza Bellini ★★★", "m": "En el corazón de Spaccanapoli · 7–8 junio", "p": "~€75–90", "book": "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07", "air": "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07", "maps": "https://maps.google.com/?q=Piazza+Bellini+Naples"},
        "days": [
            {"d": "Día 14", "date": "Domingo 7 junio — Pompeya + Nápoles", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Circumvesuviana → Pompeya Scavi", "desc": "Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento.", "maps": "https://maps.google.com/?q=Pompei+Scavi+station"},
                {"t": "10:00", "hi": True, "ttl": "★ Pompeya — ciudad del 79 d.C.", "desc": "3h mínimo. Llevar agua y sombrero — hace calor y hay poca sombra.", "maps": "https://maps.google.com/?q=Pompeii+Archaeological+Park"},
                {"t": "15:00", "hi": False, "ttl": "Spaccanapoli + Museo Arqueológico", "desc": "El mejor museo de arqueología romana del mundo.", "maps": "https://maps.google.com/?q=National+Archaeological+Museum+Naples"},
                {"t": "19:30", "hi": True, "ttl": "★ La pizza napolitana original", "desc": "Da Michele (solo Margherita y Marinara) o Sorbillo (favorita local).", "maps": "https://maps.google.com/?q=L'Antica+Pizzeria+da+Michele+Naples"}
            ]}
        ]
    },
    "Amalfi": {
        "meta": "Días 15–16 · 8–9 junio · Base: Praiano · 2 noches",
        "alert": "Tip de presupuesto: Alojarse en Praiano mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200.",
        "hotel": {"n": "Albergo California (Praiano) ★★★", "m": "Vista al mar · Desayuno incluido · 10 min de Positano en ferry", "p": "~€85–100", "book": "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08", "air": "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08", "maps": "https://maps.google.com/?q=Praiano+Amalfi+Coast"},
        "days": [
            {"d": "Día 15", "date": "Lunes 8 junio — Positano + Amalfi", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Positano — las casas en cascada", "desc": "Playa Grande. Playa de guijarros, reposeras ~€20 el par.", "maps": "https://maps.google.com/?q=Positano+Amalfi+Coast"},
                {"t": "15:00", "hi": True, "ttl": "★ Bus SITA → Amalfi ciudad", "desc": "La carretera más espectacular. Sentarse del lado DERECHO mirando al mar.", "tip": "Comprar ticket en tabacchi antes de subir.", "maps": "https://maps.google.com/?q=Amalfi+Cathedral"},
                {"t": "19:30", "hi": False, "ttl": "Cena con vista al mar", "desc": "El atardecer sobre el Tirreno desde la Costa Amalfi."}
            ]},
            {"d": "Día 16", "date": "Martes 9 junio — Ravello + Sentiero degli Dei", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Ravello — Villa Cimbrone", "desc": "La Terraza del Infinito. Jardines sobre el precipicio a 350m sobre el mar.", "maps": "https://maps.google.com/?q=Villa+Cimbrone+Ravello"},
                {"t": "11:00", "hi": True, "ttl": "★ Sentiero degli Dei — Camino de los Dioses", "desc": "7.8km · 3h · Desde Bomerano bajando a Positano. Vista de toda la costa.", "tip": "Baja (no sube) — el cansancio es manejable.", "maps": "https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast"},
                {"t": "15:00", "hi": False, "ttl": "Llegada Positano + playa merecida", "desc": "Baño en el Tirreno. Mañana tren largo a Venecia."}
            ]}
        ]
    },
    "Venecia": {
        "meta": "Día 17 · 10 junio · 1 noche",
        "hotel": {"n": "Hotel Dalla Mora ★★★ (Santa Croce)", "m": "Zona auténtica · 10 min a pie de la estación · No en Mestre (tierra firme)", "p": "~€90–110", "book": "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10", "air": "", "maps": "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice"},
        "days": [
            {"d": "Día 17", "date": "Miércoles 10 junio — Venecia completa", "events": [
                {"t": "13:00", "hi": True, "ttl": "★ Gran Canal en Vaporetto línea 1", "desc": "45 minutos de palacios del siglo XIV. El paseo más cinematográfico.", "maps": "https://maps.google.com/?q=Grand+Canal+Venice"},
                {"t": "15:00", "hi": True, "ttl": "★ Plaza San Marcos + Campanile", "desc": "Basílica siglo XI. Campanile €10 con la mejor vista de Venecia.", "maps": "https://maps.google.com/?q=St+Marks+Basilica+Venice"},
                {"t": "17:00", "hi": True, "ttl": "★ Perderse sin mapa", "desc": "Apagar Google Maps. 118 islas, 400 puentes."},
                {"t": "19:30", "hi": False, "ttl": "Spritz veneziano en bacaro + Rialto", "desc": "Cicchetti (tapas de €1–2). Zona Cannaregio para los más auténticos.", "maps": "https://maps.google.com/?q=Rialto+Bridge+Venice"},
                {"t": "21:00", "hi": False, "ttl": "Góndola nocturna (opcional)", "desc": "Precio fijo oficial: €80 para 30 min. De noche los canales son mágicos."}
            ]}
        ]
    },
    "Zurich": {
        "meta": "Días 18–20 · 11–13 junio · 3 noches · Vuelo 14/6 a las 08:55",
        "alert": "⚠️ Vuelo el 14/6 a las 08:55: Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min.",
        "hotel": {"n": "Hotel Otter ★★ (Langstrasse)", "m": "Zona cool y multicultural · A pie del casco histórico", "p": "~€90–110", "book": "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11", "air": "", "maps": "https://maps.google.com/?q=Langstrasse+Zurich"},
        "days": [
            {"d": "Día 18", "date": "Jueves 11 junio — Llegada + Altstadt", "events": [
                {"t": "14:00", "hi": False, "ttl": "Bahnhofstrasse + Lago de Zurich", "desc": "La calle más cara del mundo. El lago al final es perfecto para una pausa.", "maps": "https://maps.google.com/?q=Bahnhofstrasse+Zurich"},
                {"t": "15:30", "hi": True, "ttl": "★ Altstadt + Grossmünster", "desc": "Donde Zwinglio inició la Reforma. Subir las torres (€5) para la vista.", "maps": "https://maps.google.com/?q=Grossmunster+Zurich"},
                {"t": "18:00", "hi": False, "ttl": "Fraumünster — vitrales de Chagall", "desc": "5 vitrales de Marc Chagall en un edificio del siglo XIII. Entrada €5.", "maps": "https://maps.google.com/?q=Fraumunster+Zurich"}
            ]},
            {"d": "Día 19", "date": "Viernes 12 junio — Lago + ETH + Fondue", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Crucero Lago de Zurich", "desc": "ZSG opera cruceros. Recorrido corto 1h o largo 4h. Los Alpes de fondo.", "maps": "https://maps.google.com/?q=Lake+Zurich+boat+tours"},
                {"t": "16:00", "hi": False, "ttl": "Polybahn → terraza ETH (vista gratis)", "desc": "El funicular sube a la ETH de Einstein. Vista de Zurich y los Alpes.", "maps": "https://maps.google.com/?q=ETH+Zurich+terrace"},
                {"t": "20:00", "hi": True, "ttl": "★ Fondue suiza — Swiss Chuchi", "desc": "El plato nacional. Swiss Chuchi en el Altstadt. ~€35–45/persona.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich"}
            ]},
            {"d": "Día 20", "date": "Sábado 13 junio — Uetliberg + Chocolates + Última noche", "events": [
                {"t": "09:00", "hi": False, "ttl": "Uetliberg — la montaña de Zurich", "desc": "Tren S10 desde HB, 20 min. 870m. Vista de Zurich, el lago y los Alpes.", "maps": "https://maps.google.com/?q=Uetliberg+Zurich"},
                {"t": "13:00", "hi": True, "ttl": "★ Chocolates Sprüngli + Mercado", "desc": "Sprüngli (desde 1836) — los mejores truffes de Zurich.", "maps": "https://maps.google.com/?q=Confiserie+Sprungli+Zurich"},
                {"t": "19:00", "hi": True, "ttl": "★ Última cena del viaje 🥂", "desc": "Brindar por el viaje. Hacer check-in online del vuelo LA8799."},
                {"t": "22:00", "hi": False, "ttl": "A dormir — vuelo 08:55 mañana", "desc": "Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración."}
            ]}
        ]
    }
}

# ─── NAVEGACIÓN (Sidebar) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✈️ NAVEGACIÓN")
    seccion = st.radio("Ir a:", ["🌍 Resumen", "🎟️ Reservas", "💰 Presupuesto", "🚄 Transportes", "💡 Tips", "📝 Notas"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 🏛️ ITALIA")
    it_sel = st.selectbox("Destino IT:", ["Milán", "Cinque Terre", "Florencia", "Roma", "Nápoles", "Amalfi", "Venecia"], label_visibility="collapsed")
    
    st.markdown("### 🇨🇭 SUIZA")
    ch_sel = st.selectbox("Destino CH:", ["Zurich"], label_visibility="collapsed")

# ─── HEADER COMÚN ─────────────────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
    <div class="hero">
      <div class="hero-content">
        <div class="hero-flag">🇮🇹 🇨🇭</div>
        <h1 class="hero-title">Italia & <em>Zurich</em></h1>
        <p class="hero-sub">Luna de Miel · Adilson & Mirtha · Mayo – Junio 2026</p>
        <div class="hero-dates"><span>✈ Sale 24 mayo · Foz de Iguazú</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
      </div>
    </div>
    <div class="stats-bar">
      <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
      <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
      <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div>
      <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
      <div class="stat-item"><span class="stat-num">~€85</span><span class="stat-lbl">Promedio hotel</span></div>
    </div>
"""), unsafe_allow_html=True)

# ─── RENDERIZADO DE VISTAS ESTÁTICAS (Resumen, Reservas, Tips, etc.) ─────────
if seccion == "🌍 Resumen":
    st.markdown('<div class="section-header"><div class="section-title">Ruta en U — Vista general</div><div class="section-meta">Norte → Sur → Norte → Suiza</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>⚠️ Reservas urgentes:</strong> La Última Cena (Da Vinci), Galería Borghese, Museos Vaticanos y Uffizi se agotan con meses de anticipación. Ir a la sección <strong>Reservas</strong> y gestionar hoy.</div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div class="card">
          <div class="card-header"><span class="day-badge">Vuelos</span><span style="font-size:0.9rem;margin-left:10px;font-weight:600;">Itinerario confirmado</span></div>
          <div class="t-row"><div class="t-time">24/5</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Foz de Iguazú → Milán Malpensa</div><div class="t-desc">LA3879 (14:50 IGU) → São Paulo GRU 16:30 · Conexión 1h30 · LA8072 (18:00) → MXP 10:15+1</div></div></div>
          <div class="t-row"><div class="t-time">14/6</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Zurich → Milán → São Paulo → Foz</div><div class="t-desc">LA8799 op. Swiss (08:55 ZRH) → MXP 09:50 · Conexión 3h10 · LA8073 (13:00) → GRU 20:00 · LA3206 (22:20) → IGU 00:05+1</div></div></div>
        </div>
    """), unsafe_allow_html=True)

elif seccion == "🎟️ Reservas":
    st.markdown('<div class="section-header"><div class="section-title">Tracker de Reservas</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>Prioridad máxima:</strong> La Última Cena y Galería Borghese se agotan con meses de anticipación. Gestionar primero.</div>', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, r in enumerate(RESERVAS_DATA):
        with cols[i % 2]:
            st.markdown(f'<div class="hotel-card"><div style="font-weight:600;font-size:1.05rem;">{r["tit"]}</div><div style="font-size:0.8rem;color:var(--slate-light);margin-bottom:8px;">{r["urg"]} · {r["det"]}</div><a href="{r["url"]}" target="_blank" class="btn btn-maps">🔗 Ir a reservar →</a></div>', unsafe_allow_html=True)

elif seccion == "💰 Presupuesto":
    st.markdown('<div class="section-header"><div class="section-title">Presupuesto estimado</div><div class="section-meta">Para 2 personas · 20 días</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:15px; margin-bottom:20px;">
          <div class="card" style="padding:1.5rem;"><div class="stat-lbl">Alojamiento (20 noches)</div><div class="stat-num" style="color:var(--terracotta-dark)">~€1.900</div></div>
          <div class="card" style="padding:1.5rem;"><div class="stat-lbl">Transportes internos</div><div class="stat-num" style="color:var(--terracotta-dark)">~€500</div></div>
          <div class="card" style="padding:1.5rem;"><div class="stat-lbl">Entradas museos</div><div class="stat-num" style="color:var(--terracotta-dark)">~€350</div></div>
          <div class="card" style="padding:1.5rem;"><div class="stat-lbl">Comidas (€60/día)</div><div class="stat-num" style="color:var(--terracotta-dark)">~€1.200</div></div>
          <div class="card" style="padding:1.5rem;"><div class="stat-lbl">Imprevistos (10%)</div><div class="stat-num" style="color:var(--terracotta-dark)">~€400</div></div>
          <div class="card" style="padding:1.5rem; background:rgba(196,105,58,0.1); border-color:var(--terracotta);"><div class="stat-lbl">TOTAL ESTIMADO</div><div class="stat-num" style="color:var(--terracotta-dark)">~€4.350</div></div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">Desglose</span><span style="font-size:0.9rem;margin-left:10px;font-weight:600;">Alojamiento por ciudad</span></div>
          <table class="budget-table">
            <thead><tr><th>Ciudad</th><th>Noches</th><th>€/Noche</th><th>Total</th></tr></thead>
            <tbody>
              <tr><td>Milán</td><td>3</td><td>€80</td><td>€240</td></tr>
              <tr><td>La Spezia</td><td>2</td><td>€75</td><td>€150</td></tr>
              <tr><td>Florencia</td><td>4</td><td>€100</td><td>€400</td></tr>
              <tr><td>Roma</td><td>4</td><td>€88</td><td>€350</td></tr>
              <tr><td>Nápoles</td><td>1</td><td>€80</td><td>€80</td></tr>
              <tr><td>Costa Amalfi</td><td>2</td><td>€92</td><td>€185</td></tr>
              <tr><td>Venecia</td><td>1</td><td>€100</td><td>€100</td></tr>
              <tr><td>Zurich</td><td>3</td><td>€100</td><td>€300</td></tr>
              <tr style="border-top:2px solid var(--terracotta-light);font-weight:600;color:var(--terracotta-dark);"><td>Total alojamiento</td><td>20</td><td>~€95</td><td>~€1.805</td></tr>
            </tbody>
          </table>
        </div>
    """), unsafe_allow_html=True)

elif seccion == "🚄 Transportes":
    st.markdown('<div class="section-header"><div class="section-title">Todos los transportes</div><div class="section-meta">En orden cronológico · Con links de compra</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-green"><strong>Truco de precio:</strong> Comprar trenes con 60 días de anticipación puede costar 4x menos que el día del viaje. Frecciarossa Roma→Nápoles: €9 anticipado vs €55 último momento.</div>', unsafe_allow_html=True)
    for t in TRANSPORTES_DATA:
        st.markdown(f"""
        <div class="transport-card">
          <div style="font-size:1.6rem; min-width:40px; text-align:center;">{t['ico']}</div>
          <div style="flex:1;">
            <div style="font-size:0.95rem; font-weight:600; color:var(--slate);">{t['r']}</div>
            <div style="font-size:0.8rem; color:var(--slate-light);">{t['d']}</div>
          </div>
          <div style="font-size:0.9rem; font-weight:600; color:var(--terracotta); padding:0 15px;">{t['p']}</div>
          <a href="{t['u']}" target="_blank" class="btn btn-maps">Comprar</a>
        </div>
        """, unsafe_allow_html=True)

elif seccion == "💡 Tips":
    st.markdown('<div class="section-header"><div class="section-title">Tips esenciales</div><div class="section-meta">Lo que marca la diferencia</div></div>', unsafe_allow_html=True)
    
    # Creamos un grid de columnas para los tips
    cols = st.columns(3)
    for i, (tit, txt) in enumerate(TIPS_DATA):
        with cols[i % 3]:
            st.markdown(f'<div class="hotel-card" style="height:90%;"><strong>{tit}</strong><br><span style="font-size:0.8rem;color:var(--slate-light);display:block;margin-top:5px;">{txt}</span></div>', unsafe_allow_html=True)

elif seccion == "📝 Notas":
    st.markdown('<div class="section-header"><div class="section-title">Notas Compartidas</div></div>', unsafe_allow_html=True)
    df_n = load_sheet_data("viaje_notas")
    with st.form("new_note", clear_on_submit=True):
        n_txt = st.text_area("Nueva nota:", placeholder="Ej: No olvidar llevar adaptador de enchufe suizo (es distinto al de Italia)...")
        n_aut = st.selectbox("Quién escribe:", ["Adilson", "Mirtha"])
        if st.form_submit_button("📤 Publicar nota en Sheets"):
            if n_txt:
                if add_nota(n_txt, n_aut): st.success("Nota publicada correctamente ✓")
    
    if not df_n.empty and 'texto' in df_n.columns:
        for _, r in df_n.iloc[::-1].iterrows():
            st.markdown(f'<div class="hotel-card" style="border-left: 4px solid var(--gold);"><strong>{r.get("autor","")}</strong><div style="margin:8px 0;font-size:0.9rem;">{r.get("texto","")}</div><small style="color:var(--slate-light);">🕐 {r.get("fecha","")}</small></div>', unsafe_allow_html=True)

# ─── RENDERIZADO DINÁMICO DE CIUDADES (El Itinerario Real) ────────────────────
# Si el usuario NO seleccionó las pestañas estáticas, renderizamos la ciudad elegida
else:
    # Verificamos si se hizo click en Suiza, de lo contrario usamos Italia
    ciudad_final = ch_sel if st.session_state.get('last_click') == 'ch' else it_sel
    
    # El selectbox puede tener texto extra como "Milán (D1-3)", extraemos solo el nombre de la key
    ciudad_key = ciudad_final.split(" (")[0]
    
    if ciudad_key in ITINERARIO_FULL:
        data = ITINERARIO_FULL[ciudad_key]
        
        st.markdown(f'<div class="section-header"><div class="section-title">{ciudad_key}</div><div class="section-meta">{data["meta"]}</div></div>', unsafe_allow_html=True)
        
        if "alert" in data:
            st.markdown(f'<div class="alert"><strong>💡 Tip estratégico:</strong> {data["alert"]}</div>', unsafe_allow_html=True)
            
        h = data["hotel"]
        # Ficha del hotel idéntica al HTML
        btn_booking = f'<a href="{h["book"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if h.get("book") else ""
        btn_airbnb = f'<a href="{h["air"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if h.get("air") else ""
        
        st.markdown(f"""
            <div class="hotel-card">
              <div style="font-family:'Playfair Display';font-size:1.2rem;color:var(--slate);font-weight:600;">{h['n']}</div>
              <div style="font-size:0.85rem;color:var(--slate-light);line-height:1.6;margin-bottom:8px;">{h['m']}</div>
              <div style="display:inline-block;background:rgba(107,122,62,0.1);color:var(--olive);padding:3px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-bottom:8px;">{h['p']} / noche</div><br>
              {btn_booking} {btn_airbnb} <a href="{h['maps']}" target="_blank" class="btn btn-maps">📍 Maps</a>
            </div>
        """, unsafe_allow_html=True)

        # Loop por cada uno de los días de esa ciudad
        for day in data["days"]:
            st.markdown(f'<div class="card-header" style="margin-top:1.5rem; border-radius:12px 12px 0 0;"><span class="day-badge">{day["d"]}</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--slate);">{day["date"]} — {day["title"]}</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="card" style="border-top:none; border-radius:0 0 12px 12px; margin-bottom:0;">', unsafe_allow_html=True)
            
            for ev in day["events"]:
                dot_class = "hi" if ev.get("hi") else ""
                star_class = "star" if ev.get("hi") else ""
                tip_html = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
                maps_html = f'<a href="{ev["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if "maps" in ev else ""
                
                st.markdown(f"""
                    <div class="t-row">
                      <div class="t-time">{ev['t']}</div>
                      <div class="t-dot {dot_class}"></div>
                      <div class="t-content">
                        <div class="t-ttl {star_class}">{ev['ttl']}</div>
                        <div class="t-desc">{ev['desc']}</div>
                        {tip_html}
                        {maps_html}
                      </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
