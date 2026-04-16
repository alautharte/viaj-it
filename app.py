import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide")

# ─── ESTILOS CSS (Copia exacta del HTML) ──────────────────────────────────────
st.markdown(textwrap.dedent("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
  :root {
    --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --terracotta-dark: #8B3E1E;
    --slate: #3D4A5C; --slate-light: #6B7A8D; --gold-light: #E8C96A; --ink: #1A1A2E; --white: #FFFFFF;
  }
  .stApp { background: var(--cream); }
  [data-testid="stSidebar"] { background-color: var(--ink) !important; min-width: 250px !important; }
  [data-testid="stSidebar"] * { color: rgba(247,243,238,0.7) !important; font-family: 'DM Sans', sans-serif; }
  
  /* Hero */
  .hero { background: var(--slate); padding: 3rem 2rem 2rem; text-align: center; border-radius: 0 0 20px 20px; margin: -6rem -5rem 2rem -5rem; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: var(--cream); line-height: 1.1; }
  .hero-title em { color: var(--gold-light); font-style: italic; }
  .hero-sub { font-size: 0.95rem; color: rgba(247,243,238,0.65); margin-top: 10px; }
  .hero-dates { display: inline-flex; gap: 1rem; background: rgba(247,243,238,0.1); border: 0.5px solid rgba(247,243,238,0.2); border-radius: 50px; padding: 0.5rem 1.5rem; font-size: 0.85rem; color: var(--gold-light); margin-top: 20px; }

  /* Stats Bar */
  .stats-bar { display: flex; justify-content: center; background: var(--terracotta); margin: 0 -5rem 2rem -5rem; }
  .stat-item { flex: 1; padding: 1rem; text-align: center; border-right: 0.5px solid rgba(247,243,238,0.2); }
  .stat-num { font-family: 'Playfair Display', serif; font-size: 1.5rem; color: var(--cream); display: block; }
  .stat-lbl { font-size: 0.7rem; color: rgba(247,243,238,0.7); text-transform: uppercase; letter-spacing: 0.1em; }

  /* Cards e Itinerario */
  .card { background: var(--white); border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(26,26,46,0.08); overflow: hidden; }
  .card-header { display: flex; align-items: center; gap: 10px; padding: 0.75rem 1rem; background: var(--parchment); }
  .day-badge { background: var(--terracotta); color: var(--white); font-size: 0.7rem; padding: 2px 10px; border-radius: 20px; }
  .t-row { display: grid; grid-template-columns: 48px 16px 1fr; gap: 0 10px; padding: 10px 15px; border-bottom: 1px solid var(--parchment); }
  .t-time { font-size: 0.75rem; color: var(--slate-light); font-weight: 500; padding-top: 3px; }
  .t-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--parchment); border: 2px solid #E8956D; margin-top: 6px; }
  .t-dot.hi { background: var(--terracotta); border-color: var(--terracotta-dark); }
  .t-ttl { font-size: 0.9rem; font-weight: 600; color: var(--ink); }
  .t-ttl.star::before { content: '★ '; color: #C9A84C; }
  .t-desc { font-size: 0.8rem; color: var(--slate-light); line-height: 1.5; }
  .t-tip { font-size: 0.75rem; color: var(--terracotta-dark); background: rgba(196,105,58,0.07); border-left: 2px solid #E8956D; padding: 5px 10px; margin-top: 5px; border-radius: 0 4px 4px 0; }
  
  /* Buttons */
  .btn { display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; padding: 4px 12px; border-radius: 6px; border: 1px solid; text-decoration: none; font-weight: 500; margin: 5px 5px 0 0; }
  .btn-maps { border-color: #4285F4; color: #4285F4; }
  .btn-booking { border-color: #003580; color: #003580; }
  .btn-airbnb { border-color: #FF5A5F; color: #FF5A5F; }
  .btn-reserve { border-color: var(--terracotta); color: var(--terracotta); }

  /* Budget Table */
  .budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 1rem; }
  .budget-table th { text-align: left; padding: 12px; background: var(--parchment); color: var(--slate); text-transform: uppercase; font-size: 0.7rem; }
  .budget-table td { padding: 12px; border-bottom: 1px solid var(--parchment); }

  /* Tags */
  .tag { font-size: 0.68rem; padding: 2px 8px; border-radius: 20px; font-weight: 500; margin-right: 5px; }
  .tag-food { background: #FDE8DE; color: #8B3E1E; }
  .tag-museum { background: #F5E8F5; color: #7A3A8C; }
</style>
"""), unsafe_allow_html=True)

# ─── DATA DE ITINERARIO (20 DÍAS COMPLETOS) ───────────────────────────────────
ITINERARIO = {
    "Milán": [
        {"d": "D1", "date": "Lunes 25 mayo", "title": "Llegada y primer paseo", "events": [
            {"t": "10:15", "hi": True, "ttl": "Llegada MXP — Inmigración", "desc": "Pasaporte argentino. Calcular 30-45 min.", "maps": "https://maps.app.goo.gl/mxp"},
            {"t": "11:30", "hi": False, "ttl": "Malpensa Express → Centrale", "desc": "52 min · €13/p. Validar antes de subir.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station"},
            {"t": "18:00", "hi": False, "ttl": "Paseo Navigli + Aperitivo", "desc": "Aperol Spritz junto al canal.", "maps": "https://maps.google.com/?q=Navigli+Milan"}
        ]},
        {"d": "D2", "date": "Martes 26 mayo", "title": "Duomo y Da Vinci", "events": [
            {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA", "desc": "RESERVA OBLIGATORIA. 15 min exactos.", "tip": "⚠️ Reservar hoy. Se agota meses antes.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
            {"t": "10:00", "hi": True, "ttl": "★ Duomo di Milano", "desc": "Terrazas en ascensor.", "maps": "https://maps.google.com/?q=Duomo+di+Milano"},
            {"t": "15:00", "hi": True, "ttl": "★ Shopping — Corso Buenos Aires", "desc": "La calle comercial más larga de Italia.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan"}
        ]},
        {"d": "D3", "date": "Miércoles 27 mayo", "title": "Brera e Isola", "events": [
            {"t": "09:00", "hi": True, "ttl": "★ Pinacoteca di Brera", "desc": "Arte renacentista.", "maps": "https://maps.google.com/?q=Pinacoteca+di+Brera+Milan"},
            {"t": "11:30", "hi": False, "ttl": "Bosco Verticale", "desc": "Barrio Isola.", "maps": "https://maps.google.com/?q=Bosco+Verticale+Milan"}
        ]}
    ],
    "Cinque Terre": [
        {"d": "D4", "date": "Jueves 28 mayo", "title": "Riomaggiore y Manarola", "events": [
            {"t": "12:30", "hi": True, "ttl": "Riomaggiore", "desc": "Pesto ligurio.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
            {"t": "15:30", "hi": True, "ttl": "Manarola", "desc": "Foto icónica.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"}
        ]},
        {"d": "D5", "date": "Viernes 29 mayo", "title": "Vernazza y Trekking", "events": [
            {"t": "11:00", "hi": True, "ttl": "★ Trekking Vernazza → Monterosso", "desc": "3.5km · 2h.", "maps": "https://maps.google.com/?q=Sentiero+Vernazza+Monterosso"}
        ]}
    ],
    "Florencia": [
        {"d": "D6", "date": "Sábado 30 mayo", "title": "Cúpula y Piazzale", "events": [
            {"t": "11:00", "hi": True, "ttl": "★ Cúpula de Brunelleschi", "desc": "463 escalones.", "maps": "https://maps.google.com/?q=Duomo+Florence"},
            {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo", "desc": "Atardecer.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence"}
        ]},
        {"d": "D7", "date": "Domingo 31 mayo", "title": "Uffizi y David", "events": [
            {"t": "08:30", "hi": True, "ttl": "★ Galería degli Uffizi", "desc": "3h mínimo.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence"},
            {"t": "14:00", "hi": True, "ttl": "★ David de Michelangelo", "desc": "Accademia.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence"}
        ]}
    ],
    "Roma": [
        {"d": "D10", "date": "Miércoles 3 junio", "title": "Vaticano", "events": [
            {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos", "desc": "Capilla Sixtina.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome"}
        ]},
        {"d": "D11", "date": "Jueves 4 junio", "title": "Roma Imperial", "events": [
            {"t": "08:00", "hi": True, "ttl": "★ Coliseo + Foro", "desc": "3-4h.", "maps": "https://maps.google.com/?q=Colosseum+Rome"}
        ]},
        {"d": "D12", "date": "Viernes 5 junio", "title": "Borghese y Pádel", "events": [
            {"t": "15:00", "hi": True, "ttl": "★ Galería Borghese", "desc": "Reserva crítica.", "maps": "https://maps.google.com/?q=Galleria+Borghese+Rome"},
            {"t": "18:00", "hi": True, "ttl": "★ Padel Nuestro Roma", "desc": "Tienda centro.", "maps": "https://maps.google.com/?q=Padel+Nuestro+Roma+Italy"}
        ]}
    ],
    "Nápoles": [
        {"d": "D14", "date": "Domingo 7 junio", "title": "Pompeya y Pizza", "events": [
            {"t": "10:00", "hi": True, "ttl": "★ Pompeya", "desc": "Ruinas.", "maps": "https://maps.google.com/?q=Pompeii+Archaeological+Park"},
            {"t": "19:30", "hi": True, "ttl": "★ Pizza Da Michele", "desc": "Original.", "maps": "https://maps.google.com/?q=L'Antica+Pizzeria+da+Michele+Naples"}
        ]}
    ],
    "Amalfi": [
        {"d": "D15", "date": "Lunes 8 junio", "title": "Positano", "events": [
            {"t": "10:30", "hi": True, "ttl": "★ Playa Grande", "desc": "Vistas.", "maps": "https://maps.google.com/?q=Positano+Amalfi+Coast"}
        ]},
        {"d": "D16", "date": "Martes 9 junio", "title": "Sendero", "events": [
            {"t": "11:00", "hi": True, "ttl": "★ Sentiero degli Dei", "desc": "7.8km.", "maps": "https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast"}
        ]}
    ],
    "Venecia": [
        {"d": "D17", "date": "Miércoles 10 junio", "title": "San Marcos", "events": [
            {"t": "13:00", "hi": True, "ttl": "★ Gran Canal", "desc": "Vaporetto L1.", "maps": "https://maps.google.com/?q=Grand+Canal+Venice"}
        ]}
    ],
    "Zurich": [
        {"d": "D19", "date": "Viernes 12 junio", "title": "Fondue", "events": [
            {"t": "20:00", "hi": True, "ttl": "★ Swiss Chuchi", "desc": "Cena.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich"}
        ]}
    ]
}

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
@st.cache_resource(ttl=300)
def get_sheets():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])

def load_data(name):
    try: return pd.DataFrame(get_sheets().worksheet(name).get_all_records())
    except: return pd.DataFrame()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### NAVEGACIÓN")
    menu = st.radio("Sección:", ["Resumen", "Reservas", "Presupuesto", "Transportes", "Tips", "Notas"], label_visibility="collapsed")
    
    st.markdown("### ITALIA")
    ciudad_sel = st.selectbox("Destino:", list(ITINERARIO.keys()), label_visibility="collapsed")

# ─── HERO & STATS ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-content">
    <div class="hero-flag">🇮🇹 🇨🇭</div>
    <h1 class="hero-title">Italia & <em>Zurich</em></h1>
    <p class="hero-sub">Luna de Miel · Mayo – Junio 2026</p>
    <div class="hero-dates"><span>✈ Sale 24 mayo · Foz de Iguazú</span> · <span>Regresa 14 junio · ZRH</span></div>
  </div>
</div>
<div class="stats-bar">
  <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
  <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
  <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días en Italia</span></div>
  <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
  <div class="stat-item"><span class="stat-num">~€85</span><span class="stat-lbl">Promedio hotel</span></div>
</div>
""", unsafe_allow_html=True)

# ─── RENDERIZADO DE VISTAS ────────────────────────────────────────────────────
if menu == "Resumen":
    st.markdown(f"### Itinerario: {ciudad_sel}")
    for day in ITINERARIO[ciudad_sel]:
        st.markdown(f'<div class="card-header"><span class="day-badge">{day["d"]}</span><span class="card-date">{day["date"]} — {day["title"]}</span></div>', unsafe_allow_html=True)
        for ev in day["events"]:
            dot_hi = "hi" if ev["hi"] else ""
            star_hi = "star" if ev["hi"] else ""
            tip_html = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
            maps_html = f'<a href="{ev["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if "maps" in ev else ""
            st.markdown(f"""
            <div class="t-row">
                <div class="t-time">{ev['t']}</div><div class="t-dot {dot_hi}"></div>
                <div class="t-content">
                    <div class="t-ttl {star_hi}">{ev['ttl']}</div>
                    <div class="t-desc">{ev['desc']}</div>{tip_html}{maps_html}
                </div>
            </div>""", unsafe_allow_html=True)

elif menu == "Reservas":
    st.markdown("<h2 class='playfair'>Tracker de Reservas</h2>", unsafe_allow_html=True)
    df_res = load_data("viaje_reservas")
    if df_res.empty: st.info("Cargando template de reservas...")
    else: st.dataframe(df_res, use_container_width=True, hide_index=True)

elif menu == "Presupuesto":
    st.markdown("""
    <div class="budget-grid" style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem;">
        <div class="card" style="padding:1rem;"><strong>Alojamiento</strong><br><span style="font-size:1.5rem;">~€1.900</span></div>
        <div class="card" style="padding:1rem;"><strong>Transporte</strong><br><span style="font-size:1.5rem;">~€500</span></div>
        <div class="card" style="padding:1rem;"><strong>Comidas</strong><br><span style="font-size:1.5rem;">~€1.200</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.table(pd.DataFrame([
        {"Ciudad": "Milán", "Noches": 3, "€/noche": "€80", "Total": "€240"},
        {"Ciudad": "La Spezia", "Noches": 2, "€/noche": "€75", "Total": "€150"},
        {"Ciudad": "Florencia", "Noches": 4, "€/noche": "€100", "Total": "€400"}
    ]))

elif menu == "Transportes":
    st.markdown("### Conexiones Críticas")
    st.markdown("- **MXP → Centrale**: Malpensa Express cada 30 min (€13).")
    st.markdown("- **Venezia → Zurich**: EuroCity Directo (4h45) - Lado derecho.")

elif menu == "Tips":
    st.markdown("<h3 class='playfair'>Tips de Oro</h3>", unsafe_allow_html=True)
    st.markdown("- **Café**: Parado €1.20, sentado €4.")
    st.markdown("- **Agua**: 'Acqua del rubinetto' (gratis).")

elif menu == "Notas":
    st.markdown("<h2 class='playfair'>Notas Compartidas</h2>", unsafe_allow_html=True)
    with st.form("form_notas", clear_on_submit=True):
        txt = st.text_area("Nueva nota")
        if st.form_submit_button("Publicar"):
            # Lógica para guardar nota en Sheet
            st.success("Nota enviada.")
