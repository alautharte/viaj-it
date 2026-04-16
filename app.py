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
[data-testid="stSidebar"] { background-color: var(--ink) !important; color: white; }
[data-testid="stSidebar"] * { color: white !important; }
html, body, [class*="css"], .stMarkdown { font-family: 'DM Sans', sans-serif; color: var(--ink); }
.hero-box { background-color: var(--slate); padding: 2rem; border-radius: 16px; text-align: center; color: white; margin-bottom: 1rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; color: #FFFFFF; margin-bottom: 5px; }
.hero-title em { color: #E8C96A; font-style: italic; }
.stats-container { display: flex; justify-content: space-around; background-color: var(--terracotta); padding: 0.8rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
.stat-item { text-align: center; }
.stat-num { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 600; display: block; }
.stat-lbl { font-size: 0.65rem; text-transform: uppercase; opacity: 0.8; }
.t-row { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--parchment); }
.t-time { font-size: 0.75rem; color: #6B7A8D; width: 45px; font-weight: 500; flex-shrink: 0; padding-top: 2px; }
.t-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--terracotta); margin-top: 6px; flex-shrink: 0; }
.t-ttl { font-weight: 500; font-size: 0.9rem; margin-bottom: 2px; }
.t-ttl.star::before { content: '★ '; color: #C9A84C; }
.t-desc { font-size: 0.8rem; color: #555; line-height: 1.4; }
.t-tip { font-size: 0.72rem; color: #8B3E1E; background: rgba(196,105,58,0.08); padding: 4px 10px; border-left: 3px solid var(--terracotta); margin-top: 5px; border-radius: 0 4px 4px 0; }
.btn-maps { text-decoration: none; color: #4285F4; font-size: 0.75rem; font-weight: 500; border: 1px solid #4285F4; padding: 2px 8px; border-radius: 5px; display: inline-block; margin-top: 5px; }
.btn-maps:hover { background: #4285F4; color: white; }
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

# ─── DATOS COMPLETOS 100% PRECISOS AL HTML ─────────────────────────────────────
ITINERARIO = [
    {"city": "🏛️ Milán", "dates": "25–27 Mayo", "n": 3, "days": [
        {"d": "D1", "date": "25 Mayo", "ttl": "Llegada y Navigli", "evs": [
            {"t": "10:15", "ttl": "Llegada MXP", "desc": "Inmigración (30-45 min).", "maps": "https://maps.app.goo.gl/mxp"},
            {"t": "11:30", "ttl": "Malpensa Express → Centrale", "desc": "52 min · €13/p.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station"},
            {"t": "18:00", "ttl": "Aperitivo Navigli", "desc": "Spritz al borde del canal.", "maps": "https://maps.google.com/?q=Navigli+Milan"}
        ]},
        {"d": "D2", "date": "26 Mayo", "ttl": "Duomo y Da Vinci", "evs": [
            {"t": "08:15", "ttl": "★ LA ÚLTIMA CENA", "desc": "Reserva obligatoria.", "tip": "⚠️ Reservar con meses de antelación.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
            {"t": "10:30", "ttl": "Duomo Terrazas", "desc": "Vista de los chapiteles.", "maps": "https://maps.google.com/?q=Duomo+di+Milano"},
            {"t": "15:00", "ttl": "Shopping Corso Buenos Aires", "desc": "2km de tiendas.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan"}
        ]},
        {"d": "D3", "date": "27 Mayo", "ttl": "Brera e Isola", "evs": [
            {"t": "09:00", "ttl": "Pinacoteca di Brera", "desc": "2h recomendadas.", "maps": "https://maps.google.com/?q=Pinacoteca+di+Brera+Milan"},
            {"t": "11:30", "ttl": "Bosco Verticale", "desc": "El bosque vertical.", "maps": "https://maps.google.com/?q=Bosco+Verticale+Milan"}
        ]}
    ]},
    {"city": "🌊 Cinque Terre", "dates": "28–29 Mayo", "n": 2, "days": [
        {"d": "D4", "date": "28 Mayo", "ttl": "Pueblos de la Costa", "evs": [
            {"t": "11:30", "ttl": "Llegada La Spezia", "desc": "Cinque Terre Card €29.50."},
            {"t": "12:30", "ttl": "Riomaggiore", "desc": "Puerto pequeño.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
            {"t": "15:30", "ttl": "Manarola", "desc": "Foto icónica.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"}
        ]},
        {"d": "D5", "date": "29 Mayo", "ttl": "Vernazza y Monterosso", "evs": [
            {"t": "08:00", "ttl": "Vernazza", "desc": "Pueblo medieval.", "maps": "https://maps.google.com/?q=Vernazza+Cinque+Terre"},
            {"t": "11:00", "ttl": "Trekking a Monterosso", "desc": "3.5km · 2h.", "maps": "https://maps.google.com/?q=Sentiero+Vernazza+Monterosso"}
        ]}
    ]},
    {"city": "🌸 Florencia", "dates": "30 Mayo–2 Junio", "n": 4, "days": [
        {"d": "D6", "date": "30 Mayo", "ttl": "Cúpula y Piazzale", "evs": [
            {"t": "11:00", "ttl": "Cúpula Brunelleschi", "desc": "463 escalones.", "maps": "https://maps.google.com/?q=Duomo+Florence"},
            {"t": "18:30", "ttl": "Piazzale Michelangelo", "desc": "Atardecer.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence"}
        ]},
        {"d": "D7", "date": "31 Mayo", "ttl": "Uffizi y David", "evs": [
            {"t": "08:30", "ttl": "★ Galería degli Uffizi", "desc": "3h mínimo.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence"},
            {"t": "14:00", "ttl": "★ David de Michelangelo", "desc": "El original.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence"}
        ]},
        {"d": "D8", "date": "1 Junio", "ttl": "Palazzo Pitti", "evs": [
            {"t": "09:00", "ttl": "Jardines de Boboli", "desc": "Residencia Medici.", "maps": "https://maps.google.com/?q=Palazzo+Pitti+Florence"}
        ]},
        {"d": "D9", "date": "2 Junio", "ttl": "Excursión a Siena", "evs": [
            {"t": "09:00", "ttl": "Piazza del Campo", "desc": "Torre del Mangia.", "maps": "https://maps.google.com/?q=Piazza+del+Campo+Siena"}
        ]}
    ]},
    {"city": "🏟️ Roma", "dates": "3–6 Junio", "n": 4, "days": [
        {"d": "D10", "date": "3 Junio", "ttl": "Vaticano", "evs": [
            {"t": "10:30", "ttl": "★ Museos Vaticanos", "desc": "Capilla Sixtina.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome"}
        ]},
        {"d": "D11", "date": "4 Junio", "ttl": "Roma Imperial", "evs": [
            {"t": "08:00", "ttl": "★ Coliseo + Foro", "desc": "3-4h de visita.", "maps": "https://maps.google.com/?q=Colosseum+Rome"}
        ]},
        {"d": "D12", "date": "5 Junio", "ttl": "Borghese y Pádel", "evs": [
            {"t": "15:00", "ttl": "★ Galería Borghese", "desc": "Reserva crítica.", "maps": "https://maps.google.com/?q=Galleria+Borghese+Rome"},
            {"t": "18:00", "ttl": "★ Padel Nuestro Roma", "desc": "Probar palas.", "maps": "https://maps.google.com/?q=Padel+Nuestro+Roma+Italy"}
        ]},
        {"d": "D13", "date": "6 Junio", "ttl": "Tarde Libre", "evs": [
            {"t": "09:00", "ttl": "Castel Sant'Angelo", "desc": "Vista del Tíber.", "maps": "https://maps.google.com/?q=Castel+Sant'Angelo+Rome"}
        ]}
    ]},
    {"city": "🍕 Nápoles", "dates": "7 Junio", "n": 1, "days": [
        {"d": "D14", "date": "7 Junio", "ttl": "Pompeya y Pizza", "evs": [
            {"t": "10:00", "ttl": "★ Pompeya", "desc": "3h de visita.", "maps": "https://maps.google.com/?q=Pompeii+Archaeological+Park"},
            {"t": "19:30", "ttl": "★ Pizza Da Michele", "desc": "Original.", "maps": "https://maps.google.com/?q=L'Antica+Pizzeria+da+Michele+Naples"}
        ]}
    ]},
    {"city": "🌅 Amalfi", "dates": "8–9 Junio", "n": 2, "days": [
        {"d": "D15", "date": "8 Junio", "ttl": "Positano", "evs": [
            {"t": "10:30", "ttl": "Playa Grande", "desc": "Casas en cascada.", "maps": "https://maps.google.com/?q=Positano+Amalfi+Coast"}
        ]},
        {"d": "D16", "date": "9 Junio", "ttl": "Ravello y Trekking", "evs": [
            {"t": "11:00", "ttl": "★ Sentiero degli Dei", "desc": "7.8km · 3h.", "maps": "https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast"}
        ]}
    ]},
    {"city": "🚤 Venecia", "dates": "10 Junio", "n": 1, "days": [
        {"d": "D17", "date": "10 Junio", "ttl": "Gran Canal", "evs": [
            {"t": "13:00", "ttl": "Vaporetto Línea 1", "desc": "Paseo icónico.", "maps": "https://maps.google.com/?q=Grand+Canal+Venice"},
            {"t": "15:00", "ttl": "Plaza San Marcos", "desc": "Campanile.", "maps": "https://maps.google.com/?q=St+Marks+Basilica+Venice"}
        ]}
    ]},
    {"city": "🇨🇭 Zurich", "dates": "11–13 Junio", "n": 3, "days": [
        {"d": "D18", "date": "11 Junio", "ttl": "Altstadt", "evs": [
            {"t": "15:30", "ttl": "Grossmünster", "desc": "Torres de Zwinglio.", "maps": "https://maps.google.com/?q=Grossmunster+Zurich"}
        ]},
        {"d": "D19", "date": "12 Junio", "ttl": "Lago y Fondue", "evs": [
            {"t": "20:00", "ttl": "Fondue Swiss Chuchi", "desc": "Plato nacional.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich"}
        ]},
        {"d": "D20", "date": "13 Junio", "ttl": "Uetliberg", "evs": [
            {"t": "09:00", "ttl": "Montaña de Zurich", "desc": "Vista Alpes.", "maps": "https://maps.google.com/?q=Uetliberg+Zurich"}
        ]}
    ]}
]

# ─── BARRA LATERAL (NAVEGACIÓN) ────────────────────────────────────────────────
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Sección:", ["🗺️ Itinerario", "🎟️ Reservas", "🚄 Transportes", "💰 Gastos", "📝 Notas", "💡 Tips"])

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f'<div class="hero-box"><div class="hero-title">Italia & <em>Zurich</em></div><div style="opacity:0.8; font-size:0.9rem;">Luna de Miel · Adilson & Mirtha · Mayo-Junio 2026</div></div>', unsafe_allow_html=True)
st.markdown('<div class="stats-container"><div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días Totales</span></div><div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div><div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div><div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div></div>', unsafe_allow_html=True)

# ─── RENDERIZADO POR SECCIÓN ──────────────────────────────────────────────────
if seccion == "🗺️ Itinerario":
    col1, col2 = st.columns([1, 4])
    with col1:
        destino = st.radio("Destino:", [c["city"] for c in ITINERARIO])
    with col2:
        ciudad = next(c for c in ITINERARIO if c["city"] == destino)
        st.markdown(f"<h3 style='font-family:\"Playfair Display\"; color:#8B3E1E;'>{ciudad['city']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:grey; font-size:0.9rem;'>{ciudad['dates']} · {ciudad['n']} noches</p>", unsafe_allow_html=True)
        for day in ciudad["days"]:
            st.markdown(f'<div style="background:#EDE7DC; padding:5px 12px; border-radius:6px; font-weight:500; font-size:0.85rem; margin-top:10px;">{day["d"]} · {day["date"]} — {day["ttl"]}</div>', unsafe_allow_html=True)
            for ev in day["evs"]:
                tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
                maps = f'<a href="{ev["maps"]}" target="_blank" class="btn-maps">📍 Maps</a>' if "maps" in ev else ""
                st.markdown(f'<div class="t-row"><div class="t-time">{ev["t"]}</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl {"star" if "★" in ev["ttl"] else ""}">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip}{maps}</div></div>', unsafe_allow_html=True)

elif seccion == "🎟️ Reservas":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Tracker de Reservas</h3>", unsafe_allow_html=True)
    df_r = load_data("viaje_reservas")
    st.info("⚠️ Crítico: La Última Cena, Borghese y Vaticanos requieren meses de antelación.")
    if not df_r.empty: st.dataframe(df_r, use_container_width=True, hide_index=True)

elif seccion == "🚄 Transportes":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Conexiones Críticas</h3>", unsafe_allow_html=True)
    st.markdown("- **MXP → Centrale**: Malpensa Express (€13/p).")
    st.markdown("- **Venezia → Zurich**: EuroCity (4h45) - Sentarse lado DERECHO.")
    st.markdown("- **Roma → Nápoles**: Frecciarossa (€20-35).")

elif seccion == "💰 Gastos":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Tracker de Gastos</h3>", unsafe_allow_html=True)
    df_g = load_data("viaje_gastos")
    st.metric("Presupuesto Estimado", "€4.350")
    if not df_g.empty: st.dataframe(df_g, use_container_width=True, hide_index=True)

elif seccion == "📝 Notas":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Notas Compartidas</h3>", unsafe_allow_html=True)
    df_n = load_data("viaje_notas")
    if not df_n.empty: st.dataframe(df_n, use_container_width=True, hide_index=True)

elif seccion == "💡 Tips":
    st.markdown("<h3 style='font-family:\"Playfair Display\";'>Tips de Oro</h3>", unsafe_allow_html=True)
    st.markdown("- **Café**: Parado en barra (€1.20) vs Sentado (€4).")
    st.markdown("- **Agua**: Pedir 'rubinetto' (gratis).")
    st.markdown("- **Pádel**: Padel Nuestro Roma tiene pista para probar palas.")
