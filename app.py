import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN DE PÁGINA (Sin sidebar) ────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide", initial_sidebar_state="collapsed")

# ─── ESTILOS CSS (Copia exacta del HTML) ──────────────────────────────────────
st.markdown(textwrap.dedent("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
  
  :root {
    --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --terracotta-light: #E8956D;
    --terracotta-dark: #8B3E1E; --olive: #6B7A3E; --slate: #3D4A5C;
    --slate-light: #6B7A8D; --gold: #C9A84C; --gold-light: #E8C96A; --ink: #1A1A2E; --white: #FFFFFF;
  }

  .stApp { background: var(--cream); }
  
  /* ELIMINAR SIDEBAR POR COMPLETO */
  [data-testid="collapsedControl"] { display: none !important; }
  [data-testid="stSidebar"] { display: none !important; }
  header { visibility: hidden !important; }
  #MainMenu {visibility: hidden;} footer {visibility: hidden;}

  /* Tipografía General */
  html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }

  /* Hero Section */
  .hero { background: var(--slate); padding: 3rem 2rem 2rem; text-align: center; border-radius: 16px; margin-bottom: 0; position: relative; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: var(--cream); line-height: 1.1; margin-bottom: 0.5rem; }
  .hero-title em { color: var(--gold-light); font-style: italic; }
  .hero-sub { font-size: 0.95rem; color: rgba(247,243,238,0.65); letter-spacing: 0.05em; margin-bottom: 1.5rem; }
  .hero-dates { display: inline-flex; gap: 1rem; background: rgba(247,243,238,0.1); border: 0.5px solid rgba(247,243,238,0.2); border-radius: 50px; padding: 0.5rem 1.5rem; font-size: 0.85rem; color: var(--gold-light); }
  
  /* Stats Bar */
  .stats-bar { display: flex; justify-content: center; background: var(--terracotta); margin-top: -10px; margin-bottom: 2rem; border-radius: 0 0 16px 16px; flex-wrap: wrap; }
  .stat-item { flex: 1; padding: 1rem; text-align: center; border-right: 0.5px solid rgba(247,243,238,0.2); min-width: 120px; }
  .stat-item:last-child { border-right: none; }
  .stat-num { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--cream); display: block; font-weight: 600; line-height: 1; }
  .stat-lbl { font-size: 0.7rem; color: rgba(247,243,238,0.8); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; display: block; }

  /* Tabs de Streamlit (Para que se vean como menú horizontal superior) */
  .stTabs [data-baseweb="tab-list"] { gap: 8px; background: var(--parchment); padding: 5px 10px; border-radius: 12px; }
  .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; border: none; background: transparent; font-weight: 600; color: var(--slate); }
  .stTabs [aria-selected="true"] { background: var(--white) !important; color: var(--terracotta-dark) !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
  .stTabs [data-baseweb="tab-highlight"] { display: none; }

  /* Radio Buttons Horizontales (Para las ciudades, simulando menú de HTML) */
  div.row-widget.stRadio > div { flex-direction: row; flex-wrap: wrap; gap: 8px; background: white; padding: 10px; border-radius: 12px; border: 1px solid var(--parchment); box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
  div.row-widget.stRadio > div > label { background-color: var(--parchment); padding: 8px 16px; border-radius: 20px; border: 1px solid transparent; cursor: pointer; transition: 0.2s; }
  div.row-widget.stRadio > div > label[data-checked="true"] { background-color: var(--terracotta); border-color: var(--terracotta-dark); }
  div.row-widget.stRadio > div > label p { color: var(--slate) !important; font-weight: 600; font-size: 0.85rem; margin: 0; }
  div.row-widget.stRadio > div > label[data-checked="true"] p { color: white !important; }
  div.row-widget.stRadio div[role="radiogroup"] label > div:first-child { display: none; /* Oculta el circulito del radio */ }

  /* Section Headers */
  .section-header { display: flex; flex-direction: column; margin: 1.5rem 0; padding-bottom: 1rem; border-bottom: 1px solid var(--parchment); }
  .section-title { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: var(--terracotta-dark); line-height: 1.2; }
  .section-meta { font-size: 0.9rem; color: var(--slate-light); margin-top: 4px; font-weight: 500; }
  
  /* Cards & Timeline */
  .card { background: var(--white); border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(26,26,46,0.05); overflow: hidden; }
  .card-header { display: flex; align-items: center; gap: 10px; padding: 0.85rem 1.2rem; background: var(--parchment); border-bottom: 1px solid rgba(196,105,58,0.15); }
  .day-badge { background: var(--terracotta); color: var(--white); font-size: 0.75rem; font-weight: 600; padding: 4px 12px; border-radius: 20px; }
  
  .t-row { display: grid; grid-template-columns: 55px 16px 1fr; gap: 0 12px; padding: 15px 20px; border-bottom: 1px solid var(--parchment); }
  .t-time { font-size: 0.85rem; color: var(--slate-light); text-align: right; padding-top: 2px; font-weight: 600; font-variant-numeric: tabular-nums; }
  .t-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--parchment); border: 2px solid var(--terracotta-light); margin-top: 5px; }
  .t-dot.hi { background: var(--terracotta); border-color: var(--terracotta-dark); }
  .t-ttl { font-size: 1rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .t-ttl.star::before { content: '★ '; color: #C9A84C; }
  .t-desc { font-size: 0.85rem; color: var(--slate-light); line-height: 1.5; }
  .t-tip { font-size: 0.75rem; color: var(--terracotta-dark); background: rgba(196,105,58,0.07); border-left: 3px solid var(--terracotta-light); padding: 6px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; }
  
  /* Buttons & Tags */
  .btn { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; padding: 5px 12px; border-radius: 6px; border: 1px solid; text-decoration: none !important; font-weight: 600; margin: 8px 8px 0 0; background: white; transition: all 0.2s; }
  .btn-maps { border-color: #4285F4; color: #4285F4 !important; }
  .btn-booking { border-color: #003580; color: #003580 !important; }
  .btn-airbnb { border-color: #FF5A5F; color: #FF5A5F !important; }
  .btn-ticket { border-color: var(--olive); color: var(--olive) !important; }
  .btn:hover { background: #f8f9fa; transform: translateY(-1px); }
  
  .tag { display: inline-flex; align-items: center; font-size: 0.7rem; padding: 3px 10px; border-radius: 20px; font-weight: 600; margin-right: 6px; margin-top: 6px; }
  .tag-train { background: #E8F0FB; color: #2A5FAC; }
  .tag-walk { background: #EBF5E1; color: #3A6B18; }
  .tag-food { background: #FDE8DE; color: #8B3E1E; }
  .tag-museum { background: #F5E8F5; color: #7A3A8C; }
  .tag-shop { background: #FFF0E0; color: #8B5010; }

  /* Hotel & Transport Cards */
  .hotel-card { border: 1px solid var(--parchment); border-radius: 12px; padding: 1.2rem; margin: 0.75rem 0 1.5rem 0; background: var(--white); box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
  .transport-card { background: rgba(61,74,92,0.03); border: 1px solid rgba(61,74,92,0.08); border-radius: 10px; padding: 1rem 1.2rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 15px; transition: 0.2s; }
  .transport-card:hover { background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
  
  .budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 5px; }
  .budget-table th { text-align: left; padding: 12px; background: var(--parchment); color: var(--slate); font-size: 0.75rem; text-transform: uppercase; }
  .budget-table td { padding: 12px; border-bottom: 1px solid var(--parchment); color: var(--slate); font-weight: 500; }
  
  .alert { background: rgba(196,105,58,0.08); border: 1px solid rgba(196,105,58,0.25); border-radius: 8px; padding: 1rem; font-size: 0.85rem; color: var(--terracotta-dark); margin-bottom: 1.5rem; }
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

# ─── DATA COMPLETA Y EXACTA: ITINERARIO DE 20 DÍAS ────────────────────────────
ITINERARIO_FULL = {
    "🏛️ Milán (Días 1-3)": {
        "meta": "25, 26 y 27 mayo · 3 noches",
        "hotel": {"n": "Hotel Ariston ★★★ (o similar zona Centrale/Navigli)", "m": "Central para metro · Desayuno incluido · Habitación doble", "p": "~€80 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=Hotel+Ariston+Milan"},
        "days": [
            {"d": "Día 1", "date": "Lunes 25 mayo — Llegada y primer paseo", "events": [
                {"t": "10:15", "hi": True, "ttl": "Llegada MXP — Inmigración y aduana", "desc": "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta.", "tags": ""},
                {"t": "11:30", "hi": False, "ttl": "Malpensa Express → Milano Centrale", "desc": "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station", "tags": '<span class="tag tag-train">🚄 €13/p</span>'},
                {"t": "13:30", "hi": False, "ttl": "Check-in + almuerzo tranquilo", "desc": "Pedir risotto alla milanese o cotoletta. Evitar restaurantes junto a estaciones.", "tags": '<span class="tag tag-food">🍝 Risotto</span>'},
                {"t": "15:00", "hi": False, "ttl": "Siesta obligatoria", "desc": "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes."},
                {"t": "18:00", "hi": False, "ttl": "Paseo Navigli + Aperitivo", "desc": "Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.", "maps": "https://maps.google.com/?q=Navigli+Milan", "tags": '<span class="tag tag-walk">🚶 Paseo</span>'}
            ]},
            {"d": "Día 2", "date": "Martes 26 mayo — Duomo, Última Cena, Shopping y Pádel", "events": [
                {"t": "08:00", "hi": False, "ttl": "Desayuno italiano", "desc": "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.", "tags": '<span class="tag tag-food">☕ €3</span>'},
                {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA — Da Vinci", "desc": "RESERVA OBLIGATORIA. Solo 25 personas cada 15 min. Duración: 15 min exactos.", "tip": "⚠️ CRÍTICO: Reservar hoy mismo.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan", "tags": '<span class="tag tag-museum">🎨 €17</span>'},
                {"t": "10:00", "hi": True, "ttl": "★ Duomo di Milano", "desc": "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360°.", "maps": "https://maps.google.com/?q=Duomo+di+Milano", "tags": '<span class="tag tag-museum">⛪ €15</span>'},
                {"t": "11:30", "hi": False, "ttl": "Galleria Vittorio Emanuele II + Scala", "desc": "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior).", "maps": "https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II+Milan"},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo en Brera", "desc": "Menú del giorno: primer plato + segundo + agua = €12–15.", "maps": "https://maps.google.com/?q=Brera+Milan"},
                {"t": "15:00", "hi": True, "ttl": "★ Shopping — Corso Buenos Aires", "desc": "La calle comercial más larga de Italia. Ropa de calidad a buen precio. 2km de tiendas.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan", "tags": '<span class="tag tag-shop">🛍️ Shopping</span>'},
                {"t": "17:30", "hi": True, "ttl": "★ Padel Nuestro Milano (opcional)", "desc": "Tienen pista interior para probar palas Bullpadel, Siux, Adidas, Nox.", "tip": "Más conveniente visitar Padel Nuestro Roma (centro) que ésta (afueras).", "maps": "https://maps.google.com/?q=Via+Papa+Giovanni+XXIII+9a+Rodano+Millepini+Milan"},
                {"t": "20:00", "hi": False, "ttl": "Cena en Navigli", "desc": "Evitar restaurantes con foto en el menú en la puerta."}
            ]},
            {"d": "Día 3", "date": "Miércoles 27 mayo — Brera, Isola y preparación", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Pinacoteca di Brera", "desc": "Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia.", "maps": "https://maps.google.com/?q=Pinacoteca+di+Brera+Milan", "tags": '<span class="tag tag-museum">🎨 €15</span>'},
                {"t": "11:30", "hi": False, "ttl": "Barrio Isola + Bosco Verticale", "desc": "El famoso 'bosque vertical' de Stefano Boeri. Cafés y mercaditos locales.", "maps": "https://maps.google.com/?q=Bosco+Verticale+Milan"},
                {"t": "13:00", "hi": False, "ttl": "Almuerzo + tarde libre", "desc": "Zona Sant'Ambrogio. Tarde para descanso."},
                {"t": "19:00", "hi": False, "ttl": "Preparar maletas", "desc": "Tren 08:10 desde Milano Centrale mañana hacia Cinque Terre. Poner alarma."}
            ]}
        ]
    },
    "🌊 C. Terre (D4-5)": {
        "meta": "28 y 29 mayo · Base: La Spezia · 2 noches",
        "alert": "💡 Estrategia: Alojarse en La Spezia es más económico. Usar el tren local de la Cinque Terre Card para moverse entre los 5 pueblos.",
        "hotel": {"n": "Hotel Firenze ★★★ (La Spezia)", "m": "5 min a pie de la estación · Habitación doble", "p": "~€75 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=La+Spezia+train+station"},
        "days": [
            {"d": "Día 4", "date": "Jueves 28 mayo — Riomaggiore, Manarola, Corniglia", "events": [
                {"t": "11:30", "hi": False, "ttl": "Llegada La Spezia — Cinque Terre Card", "desc": "Comprar la Card 2 días (~€29.50/persona). Incluye todos los trenes locales.", "tags": '<span class="tag tag-train">🎫 Card €29.50</span>'},
                {"t": "12:30", "hi": True, "ttl": "★ Riomaggiore — el más fotogénico", "desc": "Bajar al puerto. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre", "tags": '<span class="tag tag-food">🍃 Pesto original</span>'},
                {"t": "15:30", "hi": True, "ttl": "★ Manarola — el mirador icónico", "desc": "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"},
                {"t": "17:30", "hi": False, "ttl": "Corniglia — vista 360°", "desc": "El único pueblo en lo alto. 377 escalones o minibus. Vista impresionante.", "maps": "https://maps.google.com/?q=Corniglia+Cinque+Terre"}
            ]},
            {"d": "Día 5", "date": "Viernes 29 mayo — Vernazza, senderismo y Monterosso", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Vernazza — el más medieval", "desc": "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.", "maps": "https://maps.google.com/?q=Vernazza+Cinque+Terre"},
                {"t": "11:00", "hi": True, "ttl": "★ Senderismo Vernazza → Monterosso", "desc": "3.5 km · 2h. El sendero más espectacular. Llevar agua y zapatos cerrados.", "tip": "Si el sendero está cerrado, tomar tren y disfrutar playa en Monterosso.", "maps": "https://maps.google.com/?q=Sentiero+Vernazza+Monterosso", "tags": '<span class="tag tag-walk">🥾 Trekking</span>'},
                {"t": "14:00", "hi": False, "ttl": "Monterosso — playa y anchoas", "desc": "Playa de arena. Probar acciughe (anchoas). Reposeras ~€5. Agua ~22°C.", "maps": "https://maps.google.com/?q=Monterosso+al+Mare", "tags": '<span class="tag tag-food">🐟 Acciughe</span>'}
            ]}
        ]
    },
    "🌸 Florencia (D6-9)": {
        "meta": "30 mayo – 2 junio · 4 noches",
        "hotel": {"n": "Hotel Davanzati ★★★ (Recomendado)", "m": "2 min del Duomo y Uffizi · Desayuno excelente", "p": "~€100 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=Hotel+Davanzati+Florence"},
        "days": [
            {"d": "Día 6", "date": "Sábado 30 mayo — Duomo + Oltrarno + Piazzale", "events": [
                {"t": "11:00", "hi": True, "ttl": "★ Cúpula de Brunelleschi", "desc": "463 escalones. Reservar turno online — sin reserva la fila es 2h+.", "maps": "https://maps.google.com/?q=Duomo+Florence", "tags": '<span class="tag tag-museum">⛪ Pase €20</span>'},
                {"t": "13:00", "hi": False, "ttl": "Mercato Centrale — almuerzo", "desc": "Piso superior. Probar lampredotto (para valientes) o pasta fresca.", "maps": "https://maps.google.com/?q=Mercato+Centrale+Florence"},
                {"t": "16:30", "hi": False, "ttl": "Ponte Vecchio → Oltrarno", "desc": "Joyerías del siglo XVI. Al cruzar: el Florencia auténtico.", "maps": "https://maps.google.com/?q=Ponte+Vecchio+Florence"},
                {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo", "desc": "EL punto de Florencia al atardecer. Llegar 30 min antes del sunset.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence", "tags": '<span class="tag tag-walk">🌅 Atardecer</span>'}
            ]},
            {"d": "Día 7", "date": "Domingo 31 mayo — Uffizi + David + San Miniato", "events": [
                {"t": "08:30", "hi": True, "ttl": "★ Galería degli Uffizi", "desc": "Botticelli, Leonardo, Caravaggio. 3h mínimo. RESERVA OBLIGATORIA.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence", "tags": '<span class="tag tag-museum">🎨 €24</span>'},
                {"t": "14:00", "hi": True, "ttl": "★ David de Michelangelo — Accademia", "desc": "5.17 metros de mármol perfecto. El original. 1.5h.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence", "tags": '<span class="tag tag-museum">🗿 €16</span>'},
                {"t": "17:30", "hi": False, "ttl": "San Miniato al Monte", "desc": "La iglesia más bella de Florencia. Canto gregoriano a las 17:30.", "maps": "https://maps.google.com/?q=San+Miniato+al+Monte+Florence"}
            ]},
            {"d": "Día 8", "date": "Lunes 1 junio — Pitti + Boboli + Cappelle Medicee", "events": [
                {"t": "09:00", "hi": False, "ttl": "Palazzo Pitti + Jardines de Boboli", "desc": "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina.", "maps": "https://maps.google.com/?q=Palazzo+Pitti+Florence", "tags": '<span class="tag tag-museum">🏰 €16</span>'},
                {"t": "16:00", "hi": True, "ttl": "★ Cappelle Medicee — Michelangelo", "desc": "Esculturas: Aurora, Crepúsculo, Día y Noche. Impactantes.", "maps": "https://maps.google.com/?q=Cappelle+Medicee+Florence", "tags": '<span class="tag tag-museum">🗿 €9</span>'}
            ]},
            {"d": "Día 9", "date": "Martes 2 junio — Siena y Val d'Orcia", "events": [
                {"t": "07:30", "hi": False, "ttl": "Bus SENA a Siena", "desc": "Desde Autostazione di Firenze. 1.5h · €9.", "maps": "https://maps.google.com/?q=Autostazione+Firenze", "tags": '<span class="tag tag-bus">🚌 €9</span>'},
                {"t": "09:00", "hi": True, "ttl": "★ Piazza del Campo + Torre del Mangia", "desc": "La plaza más bella de Italia. La Torre tiene 400 escalones.", "maps": "https://maps.google.com/?q=Piazza+del+Campo+Siena"},
                {"t": "10:30", "hi": False, "ttl": "Duomo di Siena", "desc": "Interior diferente al florentino. Pavimento de mármol único.", "maps": "https://maps.google.com/?q=Siena+Cathedral"},
                {"t": "17:00", "hi": False, "ttl": "Bus de regreso a Florencia", "desc": "Hay buses frecuentes hasta las 21:00. Mañana viajan a Roma."}
            ]}
        ]
    },
    "🏟️ Roma (D10-13)": {
        "meta": "3–6 junio · 4 noches",
        "alert": "🎾 Padel Nuestro Roma: Ubicada en el centro, mucho más conveniente que la de Milán. Bullpadel, Siux, Adidas. Tienen pista para probar.",
        "hotel": {"n": "Hotel Arco del Lauro ★★★ (Trastevere)", "m": "Zona auténtica · B&B familiar · A pie del centro", "p": "~€88 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=Trastevere+Rome"},
        "days": [
            {"d": "Día 10", "date": "Miércoles 3 junio — Vaticano completo", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos + Capilla Sixtina", "desc": "Los museos más visitados del mundo. 3–4h. RESERVA OBLIGATORIA.", "tip": "⚠️ En la Capilla Sixtina: prohibido fotografiar. Silencio absoluto.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome", "tags": '<span class="tag tag-museum">🎨 €21</span>'},
                {"t": "14:00", "hi": False, "ttl": "Basílica de San Pedro + Cúpula", "desc": "La basílica más grande. Cúpula: 551 escalones o ascensor parcial (€8).", "maps": "https://maps.google.com/?q=St+Peters+Basilica+Rome", "tags": '<span class="tag tag-museum">⛪ Gratis (Cúpula €8)</span>'}
            ]},
            {"d": "Día 11", "date": "Jueves 4 junio — Roma clásica imperial", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Coliseo + Foro Romano + Palatino", "desc": "Combo obligatorio. 3–4h. Reservar online para evitar 2h de fila.", "maps": "https://maps.google.com/?q=Colosseum+Rome", "tags": '<span class="tag tag-museum">🏛️ €16</span>'},
                {"t": "17:30", "hi": False, "ttl": "Trastevere — paseo y cena", "desc": "El barrio medieval más pintoresco. Cena recomendada: Da Enzo al 29.", "maps": "https://maps.google.com/?q=Trastevere+Rome"}
            ]},
            {"d": "Día 12", "date": "Viernes 5 junio — Roma barroca + Borghese + Pádel", "events": [
                {"t": "09:00", "hi": False, "ttl": "Pantheon → Piazza Navona → Fontana di Trevi", "desc": "Pantheon requiere ticket (€5). Trevi: lanzar la moneda de espaldas.", "maps": "https://maps.google.com/?q=Pantheon+Rome"},
                {"t": "15:00", "hi": True, "ttl": "★ Galería Borghese — Bernini", "desc": "Solo 360 personas cada 2h. Apolo y Dafne. Lo más impactante de Roma.", "maps": "https://maps.google.com/?q=Galleria+Borghese+Rome", "tags": '<span class="tag tag-museum">🗿 €17</span>'},
                {"t": "18:00", "hi": True, "ttl": "★ Padel Nuestro Roma", "desc": "La tienda más completa de pádel. Pista interior para probar palas.", "maps": "https://maps.google.com/?q=Padel+Nuestro+Roma+Italy", "tags": '<span class="tag tag-padel">🎾 Compras Pádel</span>'}
            ]},
            {"d": "Día 13", "date": "Sábado 6 junio — Castel Sant'Angelo + día libre", "events": [
                {"t": "09:00", "hi": False, "ttl": "Castel Sant'Angelo", "desc": "Mausoleo de Adriano. Vista del Tiber y San Pedro desde la cima.", "maps": "https://maps.google.com/?q=Castel+Sant'Angelo+Rome"},
                {"t": "14:00", "hi": False, "ttl": "Tarde libre + preparación", "desc": "Compras en Via del Corso. Mañana temprano: tren a Nápoles."}
            ]}
        ]
    },
    "🍕 Nápoles (D14)": {
        "meta": "7 junio · 1 noche",
        "hotel": {"n": "Hotel Piazza Bellini ★★★", "m": "En el corazón de Spaccanapoli", "p": "~€80 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=Piazza+Bellini+Naples"},
        "days": [
            {"d": "Día 14", "date": "Domingo 7 junio — Pompeya + Nápoles", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Circumvesuviana → Pompeya", "desc": "Andén subterráneo de Napoli Centrale. Sale cada 30 min. 40min de viaje.", "maps": "https://maps.google.com/?q=Pompei+Scavi+station", "tags": '<span class="tag tag-train">🚂 €3</span>'},
                {"t": "10:00", "hi": True, "ttl": "★ Pompeya Scavi", "desc": "3h mínimo. Casa dei Vettii, Anfiteatro. Llevar agua y sombrero.", "maps": "https://maps.google.com/?q=Pompeii+Archaeological+Park", "tags": '<span class="tag tag-museum">🌋 €16</span>'},
                {"t": "15:00", "hi": False, "ttl": "Spaccanapoli + Museo Arqueológico", "desc": "El mejor museo de arqueología romana del mundo. Artefactos de Pompeya.", "maps": "https://maps.google.com/?q=National+Archaeological+Museum+Naples"},
                {"t": "19:30", "hi": True, "ttl": "★ La pizza napolitana original", "desc": "Da Michele (solo Margherita y Marinara) o Sorbillo.", "maps": "https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples", "tags": '<span class="tag tag-food">🍕 €5–8</span>'}
            ]}
        ]
    },
    "🌅 Amalfi (D15-16)": {
        "meta": "8–9 junio · Base: Praiano · 2 noches",
        "alert": "💰 Tip: Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto ~€90/noche con vista al mar. Positano supera los €200.",
        "hotel": {"n": "Albergo California (Praiano) ★★★", "m": "Vista al mar · Desayuno incluido · 10 min de Positano en ferry", "p": "~€92 / noche", "book": "https://www.booking.com", "air": "https://www.airbnb.com", "maps": "https://maps.google.com/?q=Praiano+Amalfi+Coast"},
        "days": [
            {"d": "Día 15", "date": "Lunes 8 junio — Positano + Amalfi", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Positano — Playa Grande", "desc": "Las casas en cascada. Playa de guijarros, reposeras ~€20 el par.", "maps": "https://maps.google.com/?q=Positano+Amalfi+Coast"},
                {"t": "15:00", "hi": True, "ttl": "★ Bus SITA → Amalfi ciudad", "desc": "Sentarse del lado DERECHO mirando al mar. Duomo árabe-normando.", "tip": "Comprar ticket en tabacchi antes de subir.", "maps": "https://maps.google.com/?q=Amalfi+Cathedral", "tags": '<span class="tag tag-bus">🚌 €2.50</span>'},
                {"t": "19:30", "hi": False, "ttl": "Cena con vista al mar", "desc": "El atardecer sobre el Tirreno desde la Costa Amalfi."}
            ]},
            {"d": "Día 16", "date": "Martes 9 junio — Ravello + Sentiero", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Ravello — Villa Cimbrone", "desc": "La Terraza del Infinito. Jardines sobre el precipicio a 350m.", "maps": "https://maps.google.com/?q=Villa+Cimbrone+Ravello"},
                {"t": "11:00", "hi": True, "ttl": "★ Sentiero degli Dei", "desc": "El Camino de los Dioses. 7.8km · 3h · Desde Bomerano bajando a Positano.", "tip": "El mejor día del viaje para muchos. Baja (no sube).", "maps": "https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast", "tags": '<span class="tag tag-walk">🥾 Trekking</span>'},
                {"t": "15:00", "hi": False, "ttl": "Positano + playa", "desc": "Baño en el Tirreno. Mañana tren largo a Venecia — preparar maletas."}
            ]}
        ]
    },
    "🚤 Venecia (D17)": {
        "meta": "10 junio · 1 noche",
        "hotel": {"n": "Hotel Dalla Mora ★★★ (Santa Croce)", "m": "Zona auténtica · 10 min a pie de la estación · En Venecia real, no en Mestre", "p": "~€100 / noche", "book": "https://www.booking.com", "air": "", "maps": "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice"},
        "days": [
            {"d": "Día 17", "date": "Miércoles 10 junio — Venecia completa", "events": [
                {"t": "13:00", "hi": True, "ttl": "★ Gran Canal en Vaporetto línea 1", "desc": "45 min de palacios del siglo XIV. El paseo más cinematográfico.", "maps": "https://maps.google.com/?q=Grand+Canal+Venice", "tags": '<span class="tag tag-boat">🚤 24h = €25</span>'},
                {"t": "15:00", "hi": True, "ttl": "★ Plaza San Marcos + Campanile", "desc": "Basílica bizantina. Campanile €10 con la mejor vista de Venecia.", "maps": "https://maps.google.com/?q=St+Marks+Basilica+Venice"},
                {"t": "17:00", "hi": True, "ttl": "★ Perderse sin mapa", "desc": "Apagar Google Maps. 118 islas, 400 puentes."},
                {"t": "19:30", "hi": False, "ttl": "Spritz veneziano + Rialto", "desc": "Cicchetti (tapas €1–2). Zona Cannaregio para los más auténticos.", "maps": "https://maps.google.com/?q=Rialto+Bridge+Venice"},
                {"t": "21:00", "hi": False, "ttl": "Góndola nocturna (opcional)", "desc": "Precio fijo oficial: €80 para 30 min. De noche es mágico.", "tags": '<span class="tag tag-boat">🎭 €80</span>'}
            ]}
        ]
    },
    "🇨🇭 Zurich (D18-20)": {
        "meta": "11–13 junio · 3 noches · Vuelo 14/6 a las 08:55",
        "alert": "⚠️ Vuelo de regreso el 14/6 a las 08:55 AM: Estar en ZRH a las 07:00. El tren desde Zurich HB al aeropuerto tarda 10 min y sale cada 10 min.",
        "hotel": {"n": "Hotel Otter ★★ (Langstrasse)", "m": "Zona cool y multicultural · A pie del casco histórico", "p": "~€100 / noche", "book": "https://www.booking.com", "air": "", "maps": "https://maps.google.com/?q=Langstrasse+Zurich"},
        "days": [
            {"d": "Día 18", "date": "Jueves 11 junio — Llegada + Altstadt", "events": [
                {"t": "14:00", "hi": False, "ttl": "Bahnhofstrasse + Lago de Zurich", "desc": "La calle más cara del mundo. El lago al final es perfecto para una pausa.", "maps": "https://maps.google.com/?q=Bahnhofstrasse+Zurich"},
                {"t": "15:30", "hi": True, "ttl": "★ Altstadt + Grossmünster", "desc": "Donde inició la Reforma Protestante. Subir las torres (€5) para la vista.", "maps": "https://maps.google.com/?q=Grossmunster+Zurich"},
                {"t": "18:00", "hi": False, "ttl": "Fraumünster", "desc": "5 vitrales de Marc Chagall. Entrada €5.", "maps": "https://maps.google.com/?q=Fraumunster+Zurich"}
            ]},
            {"d": "Día 19", "date": "Viernes 12 junio — Lago + ETH + Fondue", "events": [
                {"t": "09:00", "hi": True, "ttl": "★ Crucero Lago de Zurich", "desc": "ZSG opera cruceros. Recorrido corto 1h. Los Alpes de fondo.", "maps": "https://maps.google.com/?q=Lake+Zurich+boat+tours", "tags": '<span class="tag tag-boat">⛵ €8–30</span>'},
                {"t": "16:00", "hi": False, "ttl": "Polybahn → terraza ETH", "desc": "El funicular de 1889 sube a la universidad. Vista de Zurich. Gratis.", "maps": "https://maps.google.com/?q=ETH+Zurich+terrace"},
                {"t": "20:00", "hi": True, "ttl": "★ Fondue suiza — Swiss Chuchi", "desc": "El plato nacional. Swiss Chuchi en el Altstadt. ~€40/persona.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich", "tags": '<span class="tag tag-food">🧀 Fondue</span>'}
            ]},
            {"d": "Día 20", "date": "Sábado 13 junio — Uetliberg + Última noche", "events": [
                {"t": "09:00", "hi": False, "ttl": "Uetliberg — la montaña", "desc": "Tren S10, 20 min, €5. 870m de altura. Vista de Zurich y los Alpes.", "maps": "https://maps.google.com/?q=Uetliberg+Zurich", "tags": '<span class="tag tag-walk">⛰️ Vistas</span>'},
                {"t": "13:00", "hi": True, "ttl": "★ Chocolates Sprüngli", "desc": "Sprüngli (desde 1836) — los mejores truffes de Zurich.", "maps": "https://maps.google.com/?q=Confiserie+Sprungli+Zurich"},
                {"t": "19:00", "hi": True, "ttl": "★ Última cena del viaje 🥂", "desc": "Brindar por el viaje. Hacer check-in online del vuelo LA8799."},
                {"t": "22:00", "hi": False, "ttl": "A dormir — vuelo 08:55", "desc": "Alarma 06:00. Tren HB→ZRH: 10 min.", "tip": "⚠️ ALARMA 06:00. No fallar.", "tags": '<span class="tag tag-sleep">✈️ Alarma</span>'}
            ]}
        ]
    }
}

# ─── HEADER COMÚN DE LA APP ───────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
    <div class="hero">
      <div class="hero-title">Italia & <em>Zurich</em></div>
      <div class="hero-sub">Luna de Miel · Adilson & Mirtha · Mayo – Junio 2026</div>
      <div class="hero-dates"><span>✈ Sale 24 mayo · IGU</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
    </div>
    <div class="stats-bar">
      <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
      <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
      <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div>
      <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
    </div>
"""), unsafe_allow_html=True)

# ─── SISTEMA DE PESTAÑAS (TABS) PARA REEMPLAZAR EL SIDEBAR ────────────────────
tab_res, tab_itin, tab_book, tab_pres, tab_trans, tab_tips, tab_notas = st.tabs([
    "🌍 Vuelos", "📅 Itinerario", "🎟️ Reservas", "💰 Presupuesto", "🚄 Transportes", "💡 Tips", "📝 Notas"
])

# ─── 1. VUELOS Y RESUMEN ──────────────────────────────────────────────────────
with tab_res:
    st.markdown('<div class="section-header"><div class="section-title">Vuelos confirmados</div><div class="section-meta">Norte → Sur → Norte → Suiza</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div class="card">
          <div class="card-header"><span class="day-badge">IDA</span><span style="font-size:0.9rem;margin-left:10px;font-weight:600;color:var(--slate);">24 Mayo — Foz de Iguazú → Milán</span></div>
          <div class="t-row"><div class="t-time">14:50</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Vuelo LA3879 / LA8072</div><div class="t-desc">IGU 14:50 → GRU 16:30 (Conexión 1h30)<br>GRU 18:00 → MXP 10:15 (+1 día)</div><span class="tag tag-train">✈ LATAM Brasil</span></div></div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">VUELTA</span><span style="font-size:0.9rem;margin-left:10px;font-weight:600;color:var(--slate);">14 Junio — Zurich → Foz de Iguazú</span></div>
          <div class="t-row"><div class="t-time">08:55</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Vuelo LA8799 / LA8073 / LA3206</div><div class="t-desc">ZRH 08:55 → MXP 09:50 (Swiss, Conexión 3h10)<br>MXP 13:00 → GRU 20:00 (LATAM, Conexión 2h20)<br>GRU 22:20 → IGU 00:05 (+1 día)</div><span class="tag tag-train">✈ Swiss + LATAM</span></div></div>
        </div>
    """), unsafe_allow_html=True)

# ─── 2. ITINERARIO (RADIO HORIZONTAL SIN SELECTBOX NI SIDEBAR) ────────────────
with tab_itin:
    ciudades = list(ITINERARIO_FULL.keys())
    ciudad_sel = st.radio("Navegación de destinos:", ciudades, horizontal=True, label_visibility="collapsed")
    
    data = ITINERARIO_FULL[ciudad_sel]
    st.markdown(f'<div class="section-header" style="margin-top:1rem;"><div class="section-title">{ciudad_sel.split(" (")[0]}</div><div class="section-meta">{data["meta"]}</div></div>', unsafe_allow_html=True)
    
    if "alert" in data:
        st.markdown(f'<div class="alert"><strong>💡 Tip estratégico:</strong> {data["alert"].split(":")[1] if ":" in data["alert"] else data["alert"]}</div>', unsafe_allow_html=True)
        
    h = data["hotel"]
    bb = f'<a href="{h["book"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if h.get("book") else ""
    ba = f'<a href="{h["air"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if h.get("air") else ""
    st.markdown(f'<div class="hotel-card"><div style="font-family:\'Playfair Display\';font-size:1.15rem;color:var(--slate);font-weight:600;">{h["n"]}</div><div style="font-size:0.85rem;color:var(--slate-light);margin-bottom:8px;">{h["m"]}</div><div style="display:inline-block;background:rgba(107,122,62,0.1);color:var(--olive);padding:3px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-bottom:8px;">{h["p"]}</div><br>{bb} {ba} <a href="{h["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a></div>', unsafe_allow_html=True)
    
    for day in data["days"]:
        st.markdown(f'<div class="card-header" style="margin-top:1.5rem; border-radius:12px 12px 0 0;"><span class="day-badge">{day["d"]}</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--slate);">{day["date"]}</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="border-top:none; border-radius:0 0 12px 12px; margin-bottom:0;">', unsafe_allow_html=True)
        for ev in day["events"]:
            dc = "hi" if ev.get("hi") else ""
            sc = "star" if ev.get("hi") else ""
            tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
            bm = f'<a href="{ev["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if "maps" in ev else ""
            tags = ev.get("tags", "")
            st.markdown(f'<div class="t-row"><div class="t-time">{ev["t"]}</div><div class="t-dot {dc}"></div><div class="t-content"><div class="t-ttl {sc}">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip}<div style="margin-top:8px;">{tags} {bm}</div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─── 3. RESERVAS ──────────────────────────────────────────────────────────────
with tab_book:
    st.markdown('<div class="section-header"><div class="section-title">Tracker de Reservas</div><div class="section-meta">Enlaces oficiales directos</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>Prioridad máxima:</strong> La Última Cena y Galería Borghese se agotan con meses de anticipación.</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, r in enumerate(RESERVAS_DATA):
        with cols[i % 2]:
            st.markdown(f'<div class="card" style="padding:1.2rem;margin-bottom:1rem;"><div style="display:flex;justify-content:space-between;align-items:flex-start;"><div style="font-size:0.95rem;font-weight:600;color:var(--slate);">{r["tit"]}</div><div style="font-size:0.65rem;background:#FEF3CD;color:#8B6914;padding:3px 10px;border-radius:20px;font-weight:600;">⏳ Pendiente</div></div><div style="font-size:0.8rem;color:var(--slate-light);margin-top:6px;margin-bottom:10px;">{r["urg"]} · {r["det"]}</div><a href="{r["url"]}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;font-size:0.75rem;color:var(--terracotta);text-decoration:none;font-weight:600;">🔗 Ir al sitio oficial →</a></div>', unsafe_allow_html=True)

# ─── 4. PRESUPUESTO ───────────────────────────────────────────────────────────
with tab_pres:
    st.markdown('<div class="section-header"><div class="section-title">Presupuesto estimado</div><div class="section-meta">Para 2 personas · 20 días</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; margin-bottom:2rem;">
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Alojamiento (20 noches)</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€1.900</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Transportes internos</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€500</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0;"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--slate-light);margin-bottom:4px;">Comidas (€60/día)</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€1.200</div></div>
          <div class="card" style="padding:1.5rem;margin-bottom:0; background:rgba(196,105,58,0.05); border-color:var(--terracotta);"><div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--terracotta-dark);font-weight:600;margin-bottom:4px;">TOTAL ESTIMADO</div><div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:var(--terracotta-dark);">~€4.350</div></div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">Desglose</span><span style="font-size:0.95rem;margin-left:12px;font-weight:600;color:var(--slate);">Alojamiento por ciudad</span></div>
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
              <tr style="border-top:2px solid var(--terracotta-light);font-weight:700;color:var(--terracotta-dark);font-size:0.9rem;"><td>Total</td><td>20</td><td>~€95</td><td>~€1.805</td></tr>
            </tbody>
          </table>
        </div>
    """), unsafe_allow_html=True)

# ─── 5. TRANSPORTES ───────────────────────────────────────────────────────────
with tab_trans:
    st.markdown('<div class="section-header"><div class="section-title">Todos los transportes</div><div class="section-meta">En orden cronológico · Con links oficiales</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-green"><strong>Truco de precio:</strong> Comprar trenes con 60 días de anticipación puede costar 4 veces menos que el día del viaje. Frecciarossa Roma→Nápoles: €9 anticipado vs €55 último momento.</div>', unsafe_allow_html=True)
    for t in TRANSPORTES_DATA:
        st.markdown(f"""
        <div class="transport-card">
          <div style="font-size:1.8rem; min-width:50px; text-align:center;">{t['ico']}</div>
          <div style="flex:1;">
            <div style="font-size:1rem; font-weight:600; color:var(--slate); margin-bottom:2px;">{t['r']}</div>
            <div style="font-size:0.85rem; color:var(--slate-light);">{t['d']}</div>
          </div>
          <div style="font-size:0.95rem; font-weight:700; color:var(--terracotta); padding:0 15px;">{t['p']}</div>
          <a href="{t['u']}" target="_blank" class="btn btn-maps">Comprar</a>
        </div>
        """, unsafe_allow_html=True)

# ─── 6. TIPS ──────────────────────────────────────────────────────────────────
with tab_tips:
    st.markdown('<div class="section-header"><div class="section-title">12 Tips esenciales</div><div class="section-meta">Para moverse como local</div></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (tit, txt) in enumerate(TIPS_DATA):
        with cols[i % 3]:
            st.markdown(f'<div class="hotel-card" style="height:90%; padding:1.2rem;"><strong style="font-size:0.95rem; color:var(--slate);">{tit}</strong><br><span style="font-size:0.85rem;color:var(--slate-light);display:block;margin-top:8px;line-height:1.5;">{txt}</span></div>', unsafe_allow_html=True)

# ─── 7. NOTAS ─────────────────────────────────────────────────────────────────
with tab_notas:
    st.markdown('<div class="section-header"><div class="section-title">Notas Compartidas</div><div class="section-meta">Sincronizado con Google Sheets</div></div>', unsafe_allow_html=True)
    with st.form("new_note", clear_on_submit=True):
        n_txt = st.text_area("Nueva nota:", placeholder="Ej: No olvidar llevar adaptador de enchufe suizo (es distinto al de Italia)...")
        n_aut = st.selectbox("Quién escribe:", ["Adilson", "Mirtha"])
        if st.form_submit_button("📤 Publicar nota en Sheets"):
            if n_txt:
                if add_nota(n_txt, n_aut): st.success("Nota publicada correctamente ✓")
    df_n = load_sheet_data("viaje_notas")
    if not df_n.empty and 'texto' in df_n.columns:
        for _, r in df_n.iloc[::-1].iterrows():
            st.markdown(f'<div class="card" style="padding:1.2rem; border-left: 4px solid var(--gold);"><strong style="font-size:0.95rem;">{r.get("autor","")}</strong><div style="margin:10px 0;font-size:0.9rem;color:var(--slate);line-height:1.5;">{r.get("texto","")}</div><small style="color:var(--slate-light);font-weight:500;">🕐 {r.get("fecha","")}</small></div>', unsafe_allow_html=True)
