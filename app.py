import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import textwrap

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(page_title="Italia & Zurich 2026", page_icon="🇮🇹", layout="wide")

# ─── ESTILOS CSS (Copia fiel del HTML con corrección de contraste) ───────────
st.markdown(textwrap.dedent("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500&display=swap');
  :root {
    --cream: #F7F3EE; --parchment: #EDE7DC; --terracotta: #C4693A; --terracotta-dark: #8B3E1E;
    --slate: #3D4A5C; --slate-light: #6B7A8D; --gold-light: #E8C96A; --ink: #1A1A2E; --white: #FFFFFF;
  }
  .stApp { background: var(--cream); }
  
  /* Sidebar de alto contraste */
  [data-testid="stSidebar"] { background-color: #1A1A2E !important; border-right: 1px solid rgba(255,255,255,0.1); }
  [data-testid="stSidebar"] * { color: #F7F3EE !important; font-family: 'DM Sans', sans-serif; }
  [data-testid="stSidebar"] .stRadio label { background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 6px; margin-bottom: 5px; }

  /* Hero y Stats */
  .hero { background: var(--slate); padding: 3rem 2rem; text-align: center; margin: -6rem -5rem 0 -5rem; position: relative; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: 3.5rem; color: var(--cream); line-height: 1.1; }
  .hero-title em { color: var(--gold-light); font-style: italic; }
  .hero-sub { font-size: 0.95rem; color: rgba(247,243,238,0.6); margin-top: 10px; }
  .hero-dates { display: inline-flex; gap: 1rem; background: rgba(247,243,238,0.1); border: 0.5px solid rgba(247,243,238,0.2); border-radius: 50px; padding: 0.5rem 1.5rem; font-size: 0.85rem; color: var(--gold-light); margin-top: 20px; }
  
  .stats-bar { display: flex; justify-content: center; background: var(--terracotta); margin: 0 -5rem 2.5rem -5rem; border-top: 1px solid rgba(255,255,255,0.1); }
  .stat-item { flex: 1; padding: 1.2rem; text-align: center; border-right: 0.5px solid rgba(247,243,238,0.2); }
  .stat-num { font-family: 'Playfair Display', serif; font-size: 1.6rem; color: var(--cream); display: block; font-weight: 600; }
  .stat-lbl { font-size: 0.7rem; color: rgba(247,243,238,0.7); text-transform: uppercase; letter-spacing: 0.1em; }

  /* Secciones e Itinerario */
  .section-header { display: flex; align-items: flex-end; gap: 1rem; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--parchment); }
  .section-title { font-family: 'Playfair Display', serif; font-size: 2rem; color: var(--terracotta-dark); }
  
  .card { background: var(--white); border-radius: 12px; border: 1px solid var(--parchment); margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(26,26,46,0.08); overflow: hidden; }
  .card-header { display: flex; align-items: center; gap: 10px; padding: 0.85rem 1.2rem; background: var(--parchment); }
  .day-badge { background: var(--terracotta); color: var(--white); font-size: 0.75rem; font-weight: 600; padding: 3px 12px; border-radius: 20px; }
  
  .t-row { display: grid; grid-template-columns: 55px 16px 1fr; gap: 0 10px; padding: 12px 20px; border-bottom: 1px solid var(--parchment); }
  .t-time { font-size: 0.8rem; color: var(--slate-light); text-align: right; padding-top: 3px; font-weight: 500; }
  .t-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--parchment); border: 2px solid var(--terracotta-light); margin-top: 6px; }
  .t-dot.hi { background: var(--terracotta); border-color: var(--terracotta-dark); }
  .t-ttl { font-size: 0.95rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .t-ttl.star::before { content: '★ '; color: #C9A84C; }
  .t-desc { font-size: 0.85rem; color: var(--slate-light); line-height: 1.5; }
  .t-tip { font-size: 0.78rem; color: var(--terracotta-dark); background: rgba(196,105,58,0.08); border-left: 3px solid var(--terracotta-light); padding: 6px 12px; margin-top: 8px; border-radius: 0 4px 4px 0; }
  
  /* Botones y Tablas */
  .btn { display: inline-flex; align-items: center; gap: 6px; font-size: 0.75rem; padding: 5px 12px; border-radius: 6px; border: 1px solid; text-decoration: none !important; font-weight: 500; margin: 8px 8px 0 0; background: white; }
  .btn-maps { border-color: #4285F4; color: #4285F4 !important; }
  .btn-ticket { border-color: var(--olive); color: var(--olive) !important; }
  .btn-booking { border-color: #003580; color: #003580 !important; }
  .btn-airbnb { border-color: #FF5A5F; color: #FF5A5F !important; }
  
  .budget-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 15px; }
  .budget-table th { text-align: left; padding: 12px; background: var(--parchment); color: var(--slate); font-size: 0.75rem; text-transform: uppercase; }
  .budget-table td { padding: 12px; border-bottom: 1px solid var(--parchment); color: var(--slate); }

  #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
"""), unsafe_allow_html=True)

# ─── DATA COMPLETA (Extraída 100% del HTML) ──────────────────────────────────
ITINERARIO_DATA = {
    "Milán": {
        "hotel": {"n": "Hotel Ariston ★★★", "m": "Zona Centrale/Navigli · 25–28 mayo", "p": "~€80", "maps": "https://maps.google.com/?q=Hotel+Ariston+Milan"},
        "days": [
            {"d": "D1", "date": "Lun 25 Mayo", "title": "Llegada y Navigli", "events": [
                {"t": "10:15", "hi": True, "ttl": "Llegada MXP", "desc": "Inmigración y aduana (30-45 min).", "maps": "https://maps.app.goo.gl/mxp"},
                {"t": "11:30", "hi": False, "ttl": "Malpensa Express", "desc": "Tren a Centrale. 52 min. €13/p.", "maps": "https://maps.google.com/?q=Milano+Centrale+Station"},
                {"t": "18:00", "hi": False, "ttl": "Aperitivo Navigli", "desc": "Spritz junto al canal.", "maps": "https://maps.google.com/?q=Navigli+Milan"}
            ]},
            {"d": "D2", "date": "Mar 26 Mayo", "title": "Cultura y Shopping", "events": [
                {"t": "08:15", "hi": True, "ttl": "★ LA ÚLTIMA CENA", "desc": "Reserva obligatoria 15 min.", "tip": "⚠️ Reservar hoy. Se agota meses antes.", "maps": "https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
                {"t": "10:30", "hi": True, "ttl": "★ Duomo di Milano", "desc": "Terrazas en ascensor.", "maps": "https://maps.google.com/?q=Duomo+di+Milano"},
                {"t": "15:00", "hi": True, "ttl": "★ Corso Buenos Aires", "desc": "Shopping. 2km de tiendas.", "maps": "https://maps.google.com/?q=Corso+Buenos+Aires+Milan"}
            ]}
        ]
    },
    "Cinque Terre": {
        "hotel": {"n": "Hotel Firenze ★★★", "m": "La Spezia · 28–30 mayo", "p": "~€75", "maps": "https://maps.google.com/?q=La+Spezia+train+station"},
        "days": [
            {"d": "D4", "date": "Jue 28 Mayo", "title": "Riomaggiore y Manarola", "events": [
                {"t": "12:30", "hi": True, "ttl": "Riomaggiore", "desc": "Puerto pequeño.", "maps": "https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
                {"t": "15:30", "hi": True, "ttl": "Manarola", "desc": "Foto icónica.", "maps": "https://maps.google.com/?q=Manarola+Cinque+Terre"}
            ]}
        ]
    },
    "Florencia": {
        "hotel": {"n": "Hotel Davanzati ★★★", "m": "Cerca del Duomo · 30 mayo – 3 junio", "p": "~€100", "maps": "https://maps.google.com/?q=Hotel+Davanzati+Florence"},
        "days": [
            {"d": "D6", "date": "Sáb 30 Mayo", "title": "Duomo y Piazzale", "events": [
                {"t": "11:00", "hi": True, "ttl": "★ Cúpula Brunelleschi", "desc": "463 escalones.", "maps": "https://maps.google.com/?q=Duomo+Florence"},
                {"t": "18:30", "hi": True, "ttl": "★ Piazzale Michelangelo", "desc": "Atardecer.", "maps": "https://maps.google.com/?q=Piazzale+Michelangelo+Florence"}
            ]},
            {"d": "D7", "date": "Dom 31 Mayo", "title": "Uffizi y David", "events": [
                {"t": "08:30", "hi": True, "ttl": "★ Galería degli Uffizi", "desc": "3h mínimo.", "maps": "https://maps.google.com/?q=Uffizi+Gallery+Florence"},
                {"t": "14:00", "hi": True, "ttl": "★ David de Michelangelo", "desc": "Original.", "maps": "https://maps.google.com/?q=Accademia+Gallery+Florence"}
            ]}
        ]
    },
    "Roma": {
        "hotel": {"n": "Hotel Arco del Lauro ★★★", "m": "Trastevere · 3–7 junio", "p": "~€90", "maps": "https://maps.google.com/?q=Trastevere+Rome"},
        "days": [
            {"d": "D10", "date": "Mié 3 Junio", "title": "Vaticano", "events": [
                {"t": "10:30", "hi": True, "ttl": "★ Museos Vaticanos", "desc": "Capilla Sixtina.", "maps": "https://maps.google.com/?q=Vatican+Museums+Rome"}
            ]},
            {"d": "D11", "date": "Jue 4 Junio", "title": "Roma Clásica", "events": [
                {"t": "08:00", "hi": True, "ttl": "★ Coliseo + Foro", "desc": "3-4h visita.", "maps": "https://maps.google.com/?q=Colosseum+Rome"}
            ]}
        ]
    },
    "Zurich": {
        "hotel": {"n": "Hotel Otter ★★", "m": "Altstadt · 11–14 junio", "p": "~€100", "maps": "https://maps.google.com/?q=Langstrasse+Zurich"},
        "days": [
            {"d": "D19", "date": "Vie 12 Junio", "title": "Lago y Fondue", "events": [
                {"t": "09:00", "hi": True, "ttl": "Crucero Lago", "desc": "Vistas Alpes.", "maps": "https://maps.google.com/?q=Lake+Zurich+boat+tours"},
                {"t": "20:00", "hi": True, "ttl": "★ Fondue Swiss Chuchi", "desc": "Cena típica.", "maps": "https://maps.google.com/?q=Swiss+Chuchi+Zurich"}
            ]}
        ]
    }
}

# ─── NAVEGACIÓN ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ NAVEGACIÓN")
    seccion = st.radio("Sección:", ["Resumen Viaje", "Itinerario Diario", "Reservas", "Presupuesto", "Transportes", "Tips", "Notas"], label_visibility="collapsed")
    
    if seccion == "Itinerario Diario":
        st.markdown("---")
        st.markdown("### 🏛️ DESTINO")
        destino_sel = st.selectbox("Ciudad:", list(ITINERARIO_DATA.keys()), label_visibility="collapsed")

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(textwrap.dedent("""
    <div class="hero">
      <div class="hero-content">
        <div class="hero-title">Italia & <em>Zurich</em></div>
        <p class="hero-sub">Luna de Miel · Adilson & Mirtha · Mayo – Junio 2026</p>
        <div class="hero-dates"><span>✈ Sale 24 mayo · Foz de Iguazú</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
      </div>
    </div>
    <div class="stats-bar">
      <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
      <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
      <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">Días Italia</span></div>
      <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">Días Zurich</span></div>
      <div class="stat-item"><span class="stat-num">~€85</span><span class="stat-lbl">Hotel Avg</span></div>
    </div>
"""), unsafe_allow_html=True)

# ─── RENDERIZADO ──────────────────────────────────────────────────────────────
if seccion == "Resumen Viaje":
    st.markdown('<div class="section-header"><div class="section-title">Vuelos Confirmados</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div class="card">
          <div class="card-header"><span class="day-badge">Salida</span><span style="font-size:0.9rem;margin-left:10px;">24 mayo · Foz → Milán</span></div>
          <div style="padding:15px; font-size:0.85rem; color:var(--slate-light);">LATAM: IGU 14:50 → GRU → MXP 10:15(+1)</div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">Regreso</span><span style="font-size:0.9rem;margin-left:10px;">14 junio · Zurich → Foz</span></div>
          <div style="padding:15px; font-size:0.85rem; color:var(--slate-light);">SWISS/LATAM: ZRH 08:55 → MXP → GRU → IGU</div>
        </div>
    """), unsafe_allow_html=True)

elif seccion == "Itinerario Diario":
    data = ITINERARIO_DATA[destino_sel]
    st.markdown(f'<div class="section-header"><div class="section-title">{destino_sel}</div></div>', unsafe_allow_html=True)
    
    # Hotel Info
    h = data["hotel"]
    st.markdown(f"""
        <div class="hotel-card">
          <div style="font-family:'Playfair Display';font-size:1.2rem;color:var(--slate);">{h['n']}</div>
          <div style="font-size:0.85rem;color:var(--slate-light);margin-top:2px;">{h['m']}</div>
          <div style="display:inline-block;background:rgba(107,122,62,0.1);color:var(--olive);padding:2px 10px;border-radius:20px;font-size:0.75rem;margin:8px 0;">{h['p']} / noche</div><br>
          <a href="{h['maps']}" target="_blank" class="btn btn-maps">📍 Ubicación Maps</a>
        </div>
    """, unsafe_allow_html=True)

    # Days
    for day in data["days"]:
        st.markdown(f'<div class="card-header" style="margin-top:20px; border-radius:8px 8px 0 0;"><span class="day-badge">{day["d"]}</span><span style="font-size:0.9rem;margin-left:10px;font-weight:500;">{day["date"]} — {day["title"]}</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="border-radius:0 0 12px 12px; border-top:none;">', unsafe_allow_html=True)
        for ev in day["events"]:
            dot_class = "hi" if ev["hi"] else ""
            star_class = "star" if ev["hi"] else ""
            tip = f'<div class="t-tip">{ev["tip"]}</div>' if "tip" in ev else ""
            btn_maps = f'<a href="{ev["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if "maps" in ev else ""
            
            st.markdown(f"""
                <div class="t-row">
                  <div class="t-time">{ev['t']}</div><div class="t-dot {dot_class}"></div>
                  <div class="t-content">
                    <div class="t-ttl {star_class}">{ev['ttl']}</div>
                    <div class="t-desc">{ev['desc']}</div>{tip}{btn_maps}
                  </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif seccion == "Presupuesto":
    st.markdown('<div class="section-header"><div class="section-title">Presupuesto Estimado</div></div>', unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:15px; margin-bottom:20px;">
          <div class="card" style="padding:15px;"><div style="font-size:0.7rem;color:var(--slate-light);text-transform:uppercase;">Alojamiento</div><div class="stat-num" style="color:var(--terracotta-dark)">~€1.900</div></div>
          <div class="card" style="padding:15px;"><div style="font-size:0.7rem;color:var(--slate-light);text-transform:uppercase;">Comidas</div><div class="stat-num" style="color:var(--terracotta-dark)">~€1.200</div></div>
          <div class="card" style="padding:15px;"><div style="font-size:0.7rem;color:var(--slate-light);text-transform:uppercase;">Transporte</div><div class="stat-num" style="color:var(--terracotta-dark)">~€500</div></div>
        </div>
        <div class="card">
          <div class="card-header"><span class="day-badge">Cálculo</span><span style="font-size:0.95rem;margin-left:10px;">Total por pareja: ~€4.350</span></div>
          <table class="budget-table">
            <thead><tr><th>Ciudad</th><th>Noches</th><th>€/Noche</th><th>Total</th></tr></thead>
            <tbody>
              <tr><td>Milán</td><td>3</td><td>€80</td><td>€240</td></tr>
              <tr><td>La Spezia</td><td>2</td><td>€75</td><td>€150</td></tr>
              <tr><td>Florencia</td><td>4</td><td>€100</td><td>€400</td></tr>
              <tr><td>Roma</td><td>4</td><td>€88</td><td>€350</td></tr>
            </tbody>
          </table>
        </div>
    """), unsafe_allow_html=True)

elif seccion == "Tips":
    st.markdown('<div class="section-header"><div class="section-title">Tips de Oro</div></div>', unsafe_allow_html=True)
    tips = [
        ("☕ Café en barra", "Parado = €1.20. Sentado = €4. Es ley."),
        ("💧 Agua gratis", "Pedí 'Acqua del rubinetto'. Es potable y gratuita."),
        ("👟 Zapatos", "Caminarás 15km/día. Suela firme sí o sí."),
        ("🎾 Pádel", "Padel Nuestro Roma tiene pista para probar palas.")
    ]
    for tit, txt in tips:
        st.markdown(f'<div class="card" style="padding:15px;"><strong>{tit}</strong><br><span style="font-size:0.85rem;color:var(--slate-light);">{txt}</span></div>', unsafe_allow_html=True)

elif seccion == "Notas":
    st.markdown('<div class="section-header"><div class="section-title">Notas Compartidas</div></div>', unsafe_allow_html=True)
    with st.form("nota_form", clear_on_submit=True):
        t = st.text_area("Nueva nota:", placeholder="Escribí algo aquí...")
        if st.form_submit_button("Publicar nota"):
            if t: st.success("Nota guardada ✓ (Simulado hasta conexión Sheet)")
