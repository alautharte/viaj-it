import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import textwrap

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Italia & Zurich 2026 🇮🇹🇨🇭",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── ESTILOS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fuente y fondo */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Hero */
.hero-box {
    background: linear-gradient(135deg, #3D4A5C 0%, #1A1A2E 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: #F7F3EE;
}
.hero-title { font-size: 2rem; font-weight: 500; margin-bottom: 4px; }
.hero-sub { font-size: 0.95rem; opacity: 0.65; margin-bottom: 1.5rem; }
.hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
.hstat-n { font-size: 1.8rem; font-weight: 500; display: block; color: #E8C96A; }
.hstat-l { font-size: 0.75rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.08em; }

/* Cards */
.res-card {
    background: #fff;
    border: 1px solid #EDE7DC;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.res-card-urgente { border-left: 4px solid #C4693A; }
.res-card-ok { border-left: 4px solid #6B7A3E; }

/* Badges estado */
.badge-pending  { background:#FEF3CD; color:#8B6914; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }
.badge-confirmed{ background:#D4EDDA; color:#1A6B32; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }
.badge-paid     { background:#CCE5FF; color:#0056B3; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }

/* Timeline */
.t-row { display:flex; gap:12px; padding:6px 0; border-bottom:1px solid #F0EDE8; }
.t-time { font-size:0.75rem; color:#6B7A8D; width:44px; flex-shrink:0; padding-top:3px; font-variant-numeric:tabular-nums; }
.t-dot  { width:10px; height:10px; border-radius:50%; background:#EDE7DC; border:2px solid #C4693A; margin-top:4px; flex-shrink:0; }
.t-dot-hi { background:#C4693A; }
.t-ttl  { font-size:0.88rem; font-weight:500; margin-bottom:2px; }
.t-desc { font-size:0.78rem; color:#6B7A8D; line-height:1.5; }
.t-tip  { font-size:0.75rem; color:#8B3E1E; background:#FDE8DE; border-left:2px solid #C4693A; padding:4px 8px; margin-top:4px; border-radius:0 4px 4px 0; }

/* Transport card */
.trans-card {
    background:#F7F3EE; border:1px solid #EDE7DC;
    border-radius:10px; padding:10px 14px;
    display:flex; align-items:center; gap:12px;
    margin-bottom:6px; flex-wrap:wrap;
}

/* Alerta */
.alert-box {
    background:#FDE8DE; border:1px solid #E8956D;
    border-radius:8px; padding:10px 14px;
    font-size:0.82rem; color:#8B3E1E; margin:8px 0;
}
.alert-green {
    background:#EBF5E1; border-color:#9AAD5A; color:#3A6B18;
}

/* Nota card */
.nota-card {
    background:#F7F3EE; border-radius:8px;
    padding:10px 14px; margin-bottom:6px;
    border-left:3px solid #C9A84C;
    font-size:0.85rem;
}
.nota-meta { font-size:0.72rem; color:#6B7A8D; margin-top:4px; }

/* Progress bar */
.prog-outer { background:#EDE7DC; border-radius:4px; height:8px; overflow:hidden; }
.prog-inner { background:#C4693A; height:100%; border-radius:4px; transition:width 0.3s; }

/* Sync badge */
.sync-ok   { background:#D4EDDA; color:#1A6B32; padding:4px 12px; border-radius:20px; font-size:0.75rem; display:inline-block; }
.sync-err  { background:#F8D7DA; color:#721C24; padding:4px 12px; border-radius:20px; font-size:0.75rem; display:inline-block; }

/* Ocultar menú hamburguesa en móvil */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(ttl=30)
def get_sheets_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_workbook():
    client = get_sheets_client()
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
def load_sheet_data(sheet_key):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets[sheet_key]
        records = ws.get_all_records()
        return pd.DataFrame(records) if records else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def save_reserva(res_id, estado, url, confirmacion, monto, notas_txt):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets["viaje_reservas"]
        records = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        row_data = [res_id, estado, url, confirmacion, monto, notas_txt, now]
        for i, r in enumerate(records, start=2):
            if r.get("id") == res_id:
                ws.update(f"A{i}:G{i}", [row_data])
                st.cache_data.clear()
                return True
        ws.append_row(row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error guardando: {e}")
        return False

def add_gasto(desc, cat, monto):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets["viaje_gastos"]
        gasto_id = f"g{datetime.now().strftime('%Y%m%d%H%M%S')}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws.append_row([gasto_id, desc, cat, monto, now, now])
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def del_gasto(gasto_id):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets["viaje_gastos"]
        records = ws.get_all_records()
        for i, r in enumerate(records, start=2):
            if str(r.get("id")) == str(gasto_id):
                ws.delete_rows(i)
                st.cache_data.clear()
                return True
    except Exception as e:
        st.error(f"Error: {e}")
    return False

def add_nota(texto, tag, autor):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets["viaje_notas"]
        nota_id = f"n{datetime.now().strftime('%Y%m%d%H%M%S')}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        ws.append_row([nota_id, texto, tag, autor, now])
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def del_nota(nota_id):
    try:
        wb = get_workbook()
        sheets = ensure_sheets(wb)
        ws = sheets["viaje_notas"]
        records = ws.get_all_records()
        for i, r in enumerate(records, start=2):
            if str(r.get("id")) == str(nota_id):
                ws.delete_rows(i)
                st.cache_data.clear()
                return True
    except Exception as e:
        st.error(f"Error: {e}")
    return False

# ─── DATOS DEL ITINERARIO ─────────────────────────────────────────────────────
RESERVAS_DEF = [
    {"id":"r01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_book":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
    {"id":"r02","title":"Galería Borghese","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_book":"https://www.galleriaborghese.it","url_maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
    {"id":"r03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_book":"https://www.museivaticani.va","url_maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
    {"id":"r04","title":"Cúpula Brunelleschi (Duomo Florencia)","city":"Florencia","fecha":"30 mayo · tarde","urgente":True,"url_book":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.google.com/?q=Duomo+Florence"},
    {"id":"r05","title":"David — Accademia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_book":"https://www.uffizi.it/en/the-accademia-gallery","url_maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
    {"id":"r06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
    {"id":"r07","title":"Coliseo + Foro Romano + Palatino","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url_book":"https://www.coopculture.it","url_maps":"https://maps.google.com/?q=Colosseum+Rome"},
    {"id":"r08","title":"Alojamiento Milán (3 noches)","city":"Milán","fecha":"25–28 mayo","urgente":False,"url_book":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2","url_maps":"https://maps.google.com/?q=Milan+Italy"},
    {"id":"r09","title":"Alojamiento La Spezia (2 noches)","city":"Cinque Terre","fecha":"28–30 mayo","urgente":False,"url_book":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2","url_maps":"https://maps.google.com/?q=La+Spezia+Italy"},
    {"id":"r10","title":"Alojamiento Florencia (4 noches)","city":"Florencia","fecha":"30 mayo–3 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2","url_maps":"https://maps.google.com/?q=Florence+Italy"},
    {"id":"r11","title":"Alojamiento Roma (4 noches)","city":"Roma","fecha":"3–7 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2","url_maps":"https://maps.google.com/?q=Trastevere+Rome"},
    {"id":"r12","title":"Alojamiento Nápoles (1 noche)","city":"Nápoles","fecha":"7–8 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2","url_maps":"https://maps.google.com/?q=Naples+Italy"},
    {"id":"r13","title":"Alojamiento Costa Amalfi — Praiano (2 noches)","city":"Amalfi","fecha":"8–10 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2","url_maps":"https://maps.google.com/?q=Praiano+Italy"},
    {"id":"r14","title":"Alojamiento Venecia (1 noche)","city":"Venecia","fecha":"10–11 junio","urgente":False,"url_book":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","url_maps":"https://maps.google.com/?q=Venice+Italy"},
    {"id":"r15","title":"Alojamiento Zurich (3 noches)","city":"Zurich","fecha":"11–14 junio","urgente":False,"url_book":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","url_maps":"https://maps.google.com/?q=Zurich+Switzerland"},
]

ITINERARIO = [
    {"city":"🏛️ Milán","dates":"D1–3 · 25–27 mayo","days":[
        {"n":"D1","date":"Lun 25 mayo","title":"Llegada y primer paseo","events":[
            {"t":"10:15","hi":True,"ttl":"Llegada MXP — Inmigración","desc":"Pasaporte argentino. Calcular 30–45 min.","maps":"https://maps.google.com/?q=Malpensa+Airport+Milan"},
            {"t":"11:30","hi":False,"ttl":"Malpensa Express → Centrale","desc":"52 min · €13/persona · Validar antes de subir.","maps":"https://maps.google.com/?q=Milano+Centrale"},
            {"t":"13:30","hi":False,"ttl":"Check-in + almuerzo","desc":"Risotto alla milanese o cotoletta. Evitar restaurantes junto a estaciones."},
            {"t":"15:00","hi":False,"ttl":"Siesta obligatoria","desc":"11h de vuelo nocturno. 2–3 horas son fundamentales."},
            {"t":"18:00","hi":False,"ttl":"Paseo Navigli + Aperitivo","desc":"Aperol Spritz al borde del canal. Alzaia Naviglio Grande.","maps":"https://maps.google.com/?q=Navigli+Milan"},
        ]},
        {"n":"D2","date":"Mar 26 mayo","title":"Última Cena, Duomo y Shopping","events":[
            {"t":"08:15","hi":True,"ttl":"★ LA ÚLTIMA CENA","desc":"RESERVA OBLIGATORIA. 25 personas cada 15 min. 15 min exactos de visita.","tip":"Reservar en cenacolodavincimilano.vivaticket.com — urgente","maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
            {"t":"10:00","hi":True,"ttl":"★ Duomo di Milano — terrazas","desc":"Ascensor a los 135 chapiteles. Reservar online.","maps":"https://maps.google.com/?q=Duomo+di+Milano"},
            {"t":"11:30","hi":False,"ttl":"Galleria Vittorio Enemuele II","desc":"Pisar el toro y girar el talón — trae suerte.","maps":"https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II"},
            {"t":"13:00","hi":False,"ttl":"Almuerzo en Brera","desc":"Menú del giorno: primer + segundo + agua = €12–15.","maps":"https://maps.google.com/?q=Brera+Milan"},
            {"t":"15:00","hi":True,"ttl":"★ Corso Buenos Aires — shopping","desc":"La calle comercial más larga de Italia. Zara, H&M, Bershka, marcas italianas. 2km de tiendas.","maps":"https://maps.google.com/?q=Corso+Buenos+Aires+Milan"},
            {"t":"17:30","hi":False,"ttl":"Padel Nuestro Milano (opcional)","desc":"Bullpadel, Siux, Adidas, Nox. Pista interior para probar palas.","tip":"Más conveniente ir a Padel Nuestro Roma (más central). Esta cierra 19:30.","maps":"https://maps.google.com/?q=Padel+Nuestro+Milan"},
        ]},
        {"n":"D3","date":"Mié 27 mayo","title":"Brera e Isola","events":[
            {"t":"09:00","hi":True,"ttl":"★ Pinacoteca di Brera","desc":"Mantegna, Raphael, Caravaggio. 2h recomendadas.","maps":"https://maps.google.com/?q=Pinacoteca+di+Brera+Milan"},
            {"t":"11:30","hi":False,"ttl":"Barrio Isola + Bosco Verticale","desc":"El bosque vertical de Stefano Boeri. Cafés y mercaditos locales.","maps":"https://maps.google.com/?q=Bosco+Verticale+Milan"},
            {"t":"19:00","hi":False,"ttl":"Preparar maletas — mañana Cinque Terre","desc":"Tren 08:10 desde Milano Centrale. Poner alarma."},
        ]},
    ]},
    {"city":"🌊 Cinque Terre","dates":"D4–5 · 28–29 mayo","days":[
        {"n":"D4","date":"Jue 28 mayo","title":"Riomaggiore, Manarola, Corniglia","events":[
            {"t":"11:30","hi":False,"ttl":"Llegada La Spezia + Cinque Terre Card","desc":"Card 2 días = €29.50/persona. Incluye todos los trenes locales."},
            {"t":"12:30","hi":True,"ttl":"★ Riomaggiore — el más fotogénico","desc":"Puerto pequeño. Pesto ligurio + vino sciacchetrà.","maps":"https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
            {"t":"15:30","hi":True,"ttl":"★ Manarola — la foto icónica","desc":"Casas pastel sobre las rocas. Muelle de natación en temporada.","maps":"https://maps.google.com/?q=Manarola+Cinque+Terre"},
            {"t":"17:30","hi":False,"ttl":"Corniglia — vista 360°","desc":"El único pueblo en lo alto. 377 escalones o minibus.","maps":"https://maps.google.com/?q=Corniglia+Cinque+Terre"},
        ]},
        {"n":"D5","date":"Vie 29 mayo","title":"Vernazza, senderismo y Monterosso","events":[
            {"t":"08:00","hi":True,"ttl":"★ Vernazza — el más medieval","desc":"Castillo Doria (€1.50). Puerto pintoresco.","maps":"https://maps.google.com/?q=Vernazza+Cinque+Terre"},
            {"t":"11:00","hi":True,"ttl":"★ Senderismo Vernazza → Monterosso","desc":"3.5 km · 2h · dificultad media. El sendero más espectacular.","tip":"Verificar estado en parconazionale5terre.it antes de ir.","maps":"https://maps.google.com/?q=Sentiero+Vernazza+Monterosso"},
            {"t":"14:00","hi":False,"ttl":"Monterosso — playa y anchoas","desc":"La única playa de arena real. Agua ~22°C en junio.","maps":"https://maps.google.com/?q=Monterosso+al+Mare"},
        ]},
    ]},
    {"city":"🌸 Florencia","dates":"D6–9 · 30 mayo–2 junio","days":[
        {"n":"D6","date":"Sáb 30 mayo","title":"Duomo + Cúpula + Piazzale","events":[
            {"t":"11:00","hi":True,"ttl":"★ Duomo + Cúpula de Brunelleschi","desc":"463 escalones. Sin reserva: 2h de fila mínimo.","maps":"https://maps.google.com/?q=Duomo+Florence"},
            {"t":"13:00","hi":False,"ttl":"Mercato Centrale — almuerzo","desc":"Piso superior. Pasta fresca o lampredotto.","maps":"https://maps.google.com/?q=Mercato+Centrale+Florence"},
            {"t":"16:30","hi":False,"ttl":"Ponte Vecchio → Oltrarno","desc":"Puente con joyerías del siglo XVI.","maps":"https://maps.google.com/?q=Ponte+Vecchio+Florence"},
            {"t":"18:30","hi":True,"ttl":"★ Piazzale Michelangelo — atardecer","desc":"EL punto de vista de Florencia. Llegar 30 min antes del sunset.","maps":"https://maps.google.com/?q=Piazzale+Michelangelo+Florence"},
        ]},
        {"n":"D7","date":"Dom 31 mayo","title":"Uffizi + David + San Miniato","events":[
            {"t":"08:30","hi":True,"ttl":"★ Galería degli Uffizi","desc":"Botticelli, Leonardo, Caravaggio. 3h mínimo. RESERVA obligatoria.","maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
            {"t":"14:00","hi":True,"ttl":"★ David de Michelangelo — Accademia","desc":"5.17 metros. El original. 1.5h.","maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
            {"t":"17:30","hi":False,"ttl":"San Miniato al Monte","desc":"La iglesia más bella de Florencia. Gratis. Gregoriano a las 17:30.","maps":"https://maps.google.com/?q=San+Miniato+al+Monte+Florence"},
        ]},
        {"n":"D8","date":"Lun 1 junio","title":"Pitti + Boboli + Cappelle Medicee","events":[
            {"t":"09:00","hi":False,"ttl":"Palazzo Pitti + Jardines de Boboli","desc":"Rafael y Tiziano. Gruta de Buontalenti (1583).","maps":"https://maps.google.com/?q=Palazzo+Pitti+Florence"},
            {"t":"16:00","hi":True,"ttl":"★ Cappelle Medicee — Michelangelo","desc":"Aurora, Crepúsculo, Día y Noche. Igual de impactantes que el David.","maps":"https://maps.google.com/?q=Cappelle+Medicee+Florence"},
        ]},
        {"n":"D9","date":"Mar 2 junio","title":"Siena y Val d'Orcia","events":[
            {"t":"07:30","hi":False,"ttl":"Bus SENA a Siena","desc":"Desde Autostazione frente a SMN · 1.5h · €9","maps":"https://maps.google.com/?q=Autostazione+Firenze"},
            {"t":"09:00","hi":True,"ttl":"★ Piazza del Campo + Torre del Mangia","desc":"La plaza más bella de Italia. Torre: 400 escalones, vistas espectaculares.","maps":"https://maps.google.com/?q=Piazza+del+Campo+Siena"},
            {"t":"10:30","hi":False,"ttl":"Duomo di Siena","desc":"Interior diferente al florentino. El pavimento de mármol es único.","maps":"https://maps.google.com/?q=Siena+Cathedral"},
            {"t":"17:00","hi":False,"ttl":"Bus de regreso a Florencia","desc":"Hay buses hasta las 21:00. Mañana viajan a Roma."},
        ]},
    ]},
    {"city":"🏟️ Roma","dates":"D10–13 · 3–6 junio","days":[
        {"n":"D10","date":"Mié 3 junio","title":"Vaticano completo","events":[
            {"t":"10:30","hi":True,"ttl":"★ Museos Vaticanos + Capilla Sixtina","desc":"3–4h. RESERVA OBLIGATORIA. Silencio absoluto en la Sixtina.","maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
            {"t":"14:00","hi":False,"ttl":"Basílica San Pedro + Cúpula","desc":"La basílica más grande. Cúpula: 551 escalones o ascensor (€8).","maps":"https://maps.google.com/?q=St+Peters+Basilica+Rome"},
        ]},
        {"n":"D11","date":"Jue 4 junio","title":"Roma imperial","events":[
            {"t":"08:00","hi":True,"ttl":"★ Coliseo + Foro Romano + Palatino","desc":"Combo obligatorio. 3–4h. Reservar online para evitar filas.","maps":"https://maps.google.com/?q=Colosseum+Rome"},
            {"t":"17:30","hi":False,"ttl":"Trastevere — paseo y cena","desc":"Basílica di Santa Maria in Trastevere (gratis). Cena: Da Enzo al 29.","maps":"https://maps.google.com/?q=Trastevere+Rome"},
        ]},
        {"n":"D12","date":"Vie 5 junio","title":"Roma barroca + Borghese + Pádel","events":[
            {"t":"09:00","hi":False,"ttl":"Pantheon → Navona → Fontana di Trevi","desc":"Pantheon €5. Trevi: moneda de espaldas con la mano derecha.","maps":"https://maps.google.com/?q=Pantheon+Rome"},
            {"t":"15:00","hi":True,"ttl":"★ Galería Borghese — Bernini","desc":"360 personas cada 2h. Apolo y Dafne. Lo más impactante de Roma.","maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
            {"t":"18:00","hi":True,"ttl":"★ Padel Nuestro Roma","desc":"Bullpadel, Siux, Babolat, Head, Star Vie. Pista interior para probar palas.","maps":"https://maps.google.com/?q=Padel+Nuestro+Roma+Italy"},
        ]},
        {"n":"D13","date":"Sáb 6 junio","title":"Castel Sant'Angelo + libre","events":[
            {"t":"09:00","hi":False,"ttl":"Castel Sant'Angelo","desc":"Vista del Tiber y San Pedro desde la cima.","maps":"https://maps.google.com/?q=Castel+Sant+Angelo+Rome"},
            {"t":"14:00","hi":False,"ttl":"Tarde libre + preparación","desc":"Compras Via del Corso. Mañana: tren a Nápoles."},
        ]},
    ]},
    {"city":"🍕 Nápoles","dates":"D14 · 7 junio","days":[
        {"n":"D14","date":"Dom 7 junio","title":"Pompeya + Nápoles + Pizza","events":[
            {"t":"09:00","hi":True,"ttl":"★ Circumvesuviana → Pompeya Scavi","desc":"Andén -1 de Napoli Centrale. Cada 30 min. €3 cada uno.","maps":"https://maps.google.com/?q=Pompei+Scavi+station"},
            {"t":"10:00","hi":True,"ttl":"★ Pompeya — ciudad del 79 d.C.","desc":"3h mínimo. Casa dei Vettii, Anfiteatro, moldes humanos. Llevar agua.","maps":"https://maps.google.com/?q=Pompeii+Archaeological+Park"},
            {"t":"15:00","hi":False,"ttl":"Spaccanapoli + Museo Arqueológico","desc":"El mejor museo de arqueología romana del mundo.","maps":"https://maps.google.com/?q=National+Archaeological+Museum+Naples"},
            {"t":"19:30","hi":True,"ttl":"★ La pizza napolitana original","desc":"Da Michele (solo Margherita/Marinara, fila larga) o Sorbillo.","maps":"https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples"},
        ]},
    ]},
    {"city":"🌅 Costa Amalfi","dates":"D15–16 · 8–9 junio","days":[
        {"n":"D15","date":"Lun 8 junio","title":"Positano + Amalfi","events":[
            {"t":"10:30","hi":True,"ttl":"★ Positano — las casas en cascada","desc":"Playa Grande. Guijarros. Reposeras ~€20 el par. Agua ~22°C.","maps":"https://maps.google.com/?q=Positano+Amalfi+Coast"},
            {"t":"15:00","hi":True,"ttl":"★ Bus SITA → Amalfi ciudad","desc":"Sentarse del lado DERECHO mirando al mar. Duomo árabe-normando siglo IX.","tip":"Comprar ticket en tabacchi antes de subir. €2.50 el tramo.","maps":"https://maps.google.com/?q=Amalfi+Cathedral"},
        ]},
        {"n":"D16","date":"Mar 9 junio","title":"Ravello + Sentiero degli Dei","events":[
            {"t":"08:00","hi":True,"ttl":"★ Ravello — Villa Cimbrone","desc":"La Terraza del Infinito — el balcón más bello del mundo. €7.","maps":"https://maps.google.com/?q=Villa+Cimbrone+Ravello"},
            {"t":"11:00","hi":True,"ttl":"★ Sentiero degli Dei — 7.8km · 3h","desc":"El sendero más famoso de Amalfi. Baja desde Bomerano a Positano desde 600m.","tip":"Llevar agua, sombrero y calzado firme. El mejor día del viaje para muchos.","maps":"https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast"},
            {"t":"15:00","hi":False,"ttl":"Llegada Positano + playa merecida","desc":"Baño en el Tirreno. Mañana: ferry + tren largo a Venecia."},
        ]},
    ]},
    {"city":"🚤 Venecia","dates":"D17 · 10 junio","days":[
        {"n":"D17","date":"Mié 10 junio","title":"Venecia completa","events":[
            {"t":"13:00","hi":True,"ttl":"★ Gran Canal — Vaporetto línea 1","desc":"45 min de palacios del siglo XIV. Ticket 24h = €25. El más lento = el más bonito.","maps":"https://maps.google.com/?q=Grand+Canal+Venice"},
            {"t":"15:00","hi":True,"ttl":"★ Plaza San Marcos + Basílica + Campanile","desc":"Basílica gratis con espera. Campanile €10 con la mejor vista de Venecia.","maps":"https://maps.google.com/?q=St+Marks+Basilica+Venice"},
            {"t":"17:00","hi":True,"ttl":"★ Perderse sin mapa","desc":"118 islas, 400 puentes. Apagar Google Maps y caminar sin rumbo."},
            {"t":"19:30","hi":False,"ttl":"Spritz en bacaro + Rialto","desc":"Cicchetti (tapas €1–2). Zona Cannaregio para los más auténticos.","maps":"https://maps.google.com/?q=Rialto+Bridge+Venice"},
            {"t":"21:00","hi":False,"ttl":"Góndola nocturna (opcional)","desc":"Precio fijo oficial: €80 para 30 min (hasta 6 personas)."},
        ]},
    ]},
    {"city":"🇨🇭 Zurich","dates":"D18–20 · 11–13 junio","days":[
        {"n":"D18","date":"Jue 11 junio","title":"Llegada + Altstadt","events":[
            {"t":"14:00","hi":False,"ttl":"Bahnhofstrasse + Lago de Zurich","desc":"La calle más cara del mundo. El lago al final.","maps":"https://maps.google.com/?q=Bahnhofstrasse+Zurich"},
            {"t":"15:30","hi":True,"ttl":"★ Grossmünster + Altstadt","desc":"Donde Zwinglio inició la Reforma (1519). Torres €5.","maps":"https://maps.google.com/?q=Grossmunster+Zurich"},
            {"t":"18:00","hi":False,"ttl":"Fraumünster — vitrales de Chagall","desc":"5 vitrales de 1970 en edificio del siglo XIII. €5.","maps":"https://maps.google.com/?q=Fraumunster+Zurich"},
        ]},
        {"n":"D19","date":"Vie 12 junio","title":"Lago + ETH + Fondue","events":[
            {"t":"09:00","hi":True,"ttl":"★ Crucero Lago de Zurich","desc":"Recorrido corto 1h o largo 4h hasta Rapperswil. Los Alpes de fondo.","maps":"https://maps.google.com/?q=Lake+Zurich"},
            {"t":"16:00","hi":False,"ttl":"Polybahn → terraza ETH (gratis)","desc":"Funicular de 1889. Vista de Zurich y los Alpes. Gratis.","maps":"https://maps.google.com/?q=ETH+Zurich"},
            {"t":"20:00","hi":True,"ttl":"★ Fondue suiza — Swiss Chuchi","desc":"El plato nacional. ~€35–45/persona.","maps":"https://maps.google.com/?q=Swiss+Chuchi+Zurich"},
        ]},
        {"n":"D20","date":"Sáb 13 junio","title":"Uetliberg + Chocolates + Última noche","events":[
            {"t":"09:00","hi":False,"ttl":"Uetliberg — la montaña de Zurich","desc":"Tren S10 desde HB, 20 min, €5. 870m de altura.","maps":"https://maps.google.com/?q=Uetliberg+Zurich"},
            {"t":"13:00","hi":True,"ttl":"★ Sprüngli + Mercado Bürkliplatz","desc":"El mejor chocolate de Zurich desde 1836. Mercado los sábados.","maps":"https://maps.google.com/?q=Confiserie+Sprungli+Zurich"},
            {"t":"19:00","hi":True,"ttl":"★ Última cena del viaje 🥂","desc":"Brindar. Hacer check-in online del vuelo LA8799."},
            {"t":"22:00","hi":False,"ttl":"A dormir — vuelo 08:55 mañana","desc":"Alarma 06:00. Tren HB→ZRH: 10 min. Aeropuerto a las 07:00.","tip":"⚠️ ALARMA 06:00. No fallar."},
        ]},
    ]},
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · 52 min · cada 30 min","€13/p","https://www.trenord.it"),
    ("🚄","Milano → La Spezia","Intercity · ~3h · Salida 08:10","€25–35","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · 5–12 min · incluido en Cinque Terre Card","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Firenze SMN","Intercity · ~2h · Salida 08:30","€15–20","https://www.trenitalia.com"),
    ("🚌","Firenze ↔ Siena","Bus SENA · 1h30 · sale cada hora","€9","https://www.tiemmespa.it"),
    ("🚄","Firenze → Roma Termini","Frecciarossa · 1h30 · cada 30 min","€25–45","https://www.trenitalia.com"),
    ("🚄","Roma → Napoli Centrale","Frecciarossa · 1h10 · desde las 06:00","€20–35","https://www.trenitalia.com"),
    ("🚂","Napoli → Pompei Scavi","Circumvesuviana · 40 min · andén -1","€3/p","https://www.eavsrl.it"),
    ("⛵","Napoli → Positano (ferry)","SNAV/Alilauro · Molo Beverello · 65 min · mayo–oct","€20/p","https://www.alilauro.it"),
    ("🚌","Costa Amalfi (bus SITA)","Positano ↔ Amalfi ↔ Ravello · ticket en tabacchi","€2.50/tramo","https://www.sitasudtrasporti.it"),
    ("🚄","Napoli → Venezia S. Lucia","Frecciarossa directo · 4h50 · salida 07:30","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia 24h","Línea 1 = Gran Canal · Línea 2 = rápida","€25","https://actv.avmspa.it"),
    ("🚄","Venezia → Zurich HB","EuroCity directo · 4h45 · a través de los Alpes","€40–60","https://www.sbb.ch"),
    ("🚄","Zurich HB → Aeropuerto ZRH","SBB · 10 min · cada 10 min","€4","https://www.sbb.ch"),
]

# ─── HELPERS UI ───────────────────────────────────────────────────────────────
def badge_html(estado):
    cls = {"pending":"badge-pending","confirmed":"badge-confirmed","paid":"badge-paid"}.get(estado,"badge-pending")
    lbl = {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(estado,"⏳ Pendiente")
    return f'<span class="{cls}">{lbl}</span>'

def maps_link(url, label="📍 Maps"):
    return f'<a href="{url}" target="_blank" style="font-size:0.78rem;color:#0056B3;text-decoration:none">{label}</a>'

# ─── CARGAR DATOS ─────────────────────────────────────────────────────────────
try:
    df_res   = load_sheet_data("viaje_reservas")
    df_gas   = load_sheet_data("viaje_gastos")
    df_notas = load_sheet_data("viaje_notas")
    sheets_ok = True
except Exception as e:
    df_res = df_gas = df_notas = pd.DataFrame()
    sheets_ok = False

def get_reserva_data(res_id):
    if df_res.empty or "id" not in df_res.columns:
        return {}
    row = df_res[df_res["id"] == res_id]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()

# ─── HERO ─────────────────────────────────────────────────────────────────────
ok_count = sum(1 for r in RESERVAS_DEF if get_reserva_data(r["id"]).get("estado") in ("confirmed","paid"))
total_gas = df_gas["monto"].astype(float).sum() if not df_gas.empty and "monto" in df_gas.columns else 0

st.markdown(textwrap.dedent(f"""
<div class="hero-box">
    <div class="hero-title">🇮🇹 Italia & Zurich 2026 🇨🇭</div>
    <div class="hero-sub">Luna de Miel · 25 mayo → 14 junio · Compartido en tiempo real</div>
    <div class="hero-stats">
        <div><span class="hstat-n">{ok_count}/{len(RESERVAS_DEF)}</span><span class="hstat-l">Reservas ok</span></div>
        <div><span class="hstat-n">€{total_gas:,.0f}</span><span class="hstat-l">Gastado</span></div>
        <div><span class="hstat-n">20</span><span class="hstat-l">Días totales</span></div>
        <div><span class="hstat-n">9</span><span class="hstat-l">Ciudades</span></div>
    </div>
</div>
"""), unsafe_allow_html=True)

if sheets_ok:
    st.markdown('<span class="sync-ok">🟢 Google Sheets conectado — visible para ambos en tiempo real</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="sync-err">🔴 Error de conexión — verificar credenciales</span>', unsafe_allow_html=True)

st.write("")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_res, tab_itin, tab_trans, tab_gas, tab_notas = st.tabs([
    "🎟️ Reservas", "🗺️ Itinerario", "🚄 Transportes", "💰 Gastos", "📝 Notas"
])

# ════════════════════════════════════════════════════════════════
# TAB RESERVAS
# ════════════════════════════════════════════════════════════════
with tab_res:
    st.markdown("""
    <div class="alert-box">
    <strong>⚠️ Urgente:</strong> La Última Cena, Galería Borghese y Museos Vaticanos se agotan con meses de anticipación.
    Cargá la URL de cada reserva — tu pareja la ve al instante.
    </div>
    """, unsafe_allow_html=True)

    filtro = st.selectbox("Filtrar por ciudad", ["Todas"] + list(dict.fromkeys(r["city"] for r in RESERVAS_DEF)))

    for r in RESERVAS_DEF:
        if filtro != "Todas" and r["city"] != filtro:
            continue

        rd = get_reserva_data(r["id"])
        estado_actual = rd.get("estado", "pending")
        card_class = "res-card-urgente" if r["urgente"] else "res-card-ok"

        with st.container():
            st.markdown(textwrap.dedent(f"""
            <div class="res-card {card_class}">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <span style="font-size:0.75rem;padding:2px 8px;border-radius:20px;
                    background:#F0EDE8;color:#6B7A8D">{r["city"]}</span>
                    <strong>{("⚠️ " if r["urgente"] else "") + r["title"]}</strong>
                    {badge_html(estado_actual)}
                </div>
                <div style="font-size:0.78rem;color:#6B7A8D;margin:4px 0 8px">{r["fecha"]}</div>
            </div>
            """), unsafe_allow_html=True)

            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                nuevo_estado = st.selectbox(
                    "Estado", ["pending","confirmed","paid"],
                    index=["pending","confirmed","paid"].index(estado_actual),
                    key=f"est_{r['id']}",
                    format_func=lambda x: {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x]
                )
            with col2:
                nuevo_conf = st.text_input("N° confirmación", value=rd.get("confirmacion",""), key=f"conf_{r['id']}", placeholder="ej. HB-123456")
            with col3:
                nuevo_monto = st.number_input("Monto €", value=float(rd.get("monto",0) or 0), key=f"monto_{r['id']}", min_value=0.0, step=1.0)

            nueva_url = st.text_input(
                "URL reservada (Airbnb / Booking / sitio oficial)",
                value=rd.get("url_reserva",""), key=f"url_{r['id']}",
                placeholder="https://www.airbnb.com/rooms/..."
            )
            if nueva_url:
                st.markdown(f'🔗 <a href="{nueva_url}" target="_blank">{nueva_url[:80]}{"..." if len(nueva_url)>80 else ""}</a>', unsafe_allow_html=True)

            nuevas_notas = st.text_area("Notas internas", value=rd.get("notas",""), key=f"nt_{r['id']}", height=60, placeholder="Ej: Check-in 15hs, preguntar por parking...")

            col_save, col_maps, col_book = st.columns([2, 1, 1])
            with col_save:
                if st.button(f"💾 Guardar", key=f"save_{r['id']}"):
                    if save_reserva(r["id"], nuevo_estado, nueva_url, nuevo_conf, nuevo_monto, nuevas_notas):
                        st.success("Guardado — tu pareja ya lo puede ver ✓")
                        st.rerun()
            with col_maps:
                st.markdown(f'<a href="{r["url_maps"]}" target="_blank" class="btn">📍 Maps</a>', unsafe_allow_html=True)
            with col_book:
                st.markdown(f'<a href="{r["url_book"]}" target="_blank" class="btn">🔗 Reservar</a>', unsafe_allow_html=True)

            st.divider()

# ════════════════════════════════════════════════════════════════
# TAB ITINERARIO
# ════════════════════════════════════════════════════════════════
with tab_itin:
    city_names = [c["city"] for c in ITINERARIO]
    selected_city = st.selectbox("Ciudad", city_names, label_visibility="collapsed")
    city_data = next(c for c in ITINERARIO if c["city"] == selected_city)

    st.markdown(f"**{city_data['city']}** · {city_data['dates']}")
    st.write("")

    for day in city_data["days"]:
        with st.expander(f"**{day['n']}** · {day['date']} — {day['title']}", expanded=(day == city_data["days"][0])):
            for ev in day["events"]:
                dot = "🟠" if ev["hi"] else "⚪"
                st.markdown(textwrap.dedent(f"""
                <div class="t-row">
                    <span class="t-time">{ev['t']}</span>
                    <span>{dot}</span>
                    <div>
                        <div class="t-ttl">{ev['ttl']}</div>
                        <div class="t-desc">{ev['desc']}</div>
                        {f'<div class="t-tip">⚠️ {ev["tip"]}</div>' if ev.get("tip") else ""}
                    </div>
                </div>
                """), unsafe_allow_html=True)

                if ev.get("maps"):
                    st.markdown(f'       <a href="{ev["maps"]}" target="_blank" style="font-size:0.78rem;color:#0056B3">📍 Abrir en Maps</a>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB TRANSPORTES
# ════════════════════════════════════════════════════════════════
with tab_trans:
    st.markdown("""
    <div class="alert-box alert-green">
    💡 <strong>Truco:</strong> Comprar con 60 días de anticipación puede ser 4x más barato.
    Frecciarossa Roma→Nápoles: €9 anticipado vs €55 al último momento.
    </div>
    """, unsafe_allow_html=True)

    for icon, route, detail, price, url in TRANSPORTES:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(textwrap.dedent(f"""
            <div class="trans-card">
                <span style="font-size:1.2rem">{icon}</span>
                <div>
                    <div style="font-size:0.9rem;font-weight:500">{route}</div>
                    <div style="font-size:0.78rem;color:#6B7A8D">{detail}</div>
                </div>
                <span style="margin-left:auto;font-weight:500;color:#C4693A">{price}</span>
            </div>
            """), unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{url}" target="_blank">🔗 Comprar</a>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB GASTOS
# ════════════════════════════════════════════════════════════════
with tab_gas:
    PRESUPUESTO = 4350.0

    cats_sum = {}
    if not df_gas.empty and "monto" in df_gas.columns and "categoria" in df_gas.columns:
        cats_sum = df_gas.groupby("categoria")["monto"].apply(lambda x: x.astype(float).sum()).to_dict()

    total_g = sum(cats_sum.values())
    pct = min(100, int(total_g / PRESUPUESTO * 100))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💶 Total gastado", f"€{total_g:,.0f}", f"{pct}% del presupuesto")
    c2.metric("🏨 Alojamiento",   f"€{cats_sum.get('Alojamiento',0):,.0f}")
    c3.metric("🚄 Transportes",   f"€{cats_sum.get('Transporte',0):,.0f}")
    c4.metric("🎟️ Entradas",      f"€{cats_sum.get('Entradas',0):,.0f}")

    st.markdown(textwrap.dedent(f"""
    <div class="prog-outer">
        <div class="prog-inner" style="width:{pct}%"></div>
    </div>
    <div style="font-size:0.75rem;color:#6B7A8D;margin-top:4px">
        €{total_g:,.0f} de €{PRESUPUESTO:,.0f} presupuestados
    </div>
    """), unsafe_allow_html=True)

    st.write("")
    st.subheader("Agregar gasto")
    col_d, col_c, col_m, col_b = st.columns([3, 2, 1, 1])
    with col_d: desc  = st.text_input("Descripción", placeholder="ej. Airbnb Florencia", label_visibility="collapsed")
    with col_c: cat   = st.selectbox("Categoría", ["Alojamiento","Transporte","Entradas","Comidas","Otros"], label_visibility="collapsed")
    with col_m: monto = st.number_input("€", min_value=0.0, step=1.0, label_visibility="collapsed")
    with col_b:
        if st.button("➕ Agregar", use_container_width=True):
            if desc and monto > 0:
                if add_gasto(desc, cat, monto):
                    st.success("Gasto guardado ✓")
                    st.rerun()
            else:
                st.warning("Completá descripción y monto")

    st.write("")
    if not df_gas.empty and "descripcion" in df_gas.columns:
        st.subheader("Historial")
        df_show = df_gas[["id","descripcion","categoria","monto","fecha"]].copy()
        df_show["monto"] = df_show["monto"].astype(float).map("€{:,.0f}".format)
        st.dataframe(df_show.drop("id", axis=1), use_container_width=True, hide_index=True)

        st.write("")
        del_id = st.text_input("ID de gasto a eliminar (ver tabla)", placeholder="ej. g20260525143022")
        if st.button("🗑️ Eliminar gasto") and del_id:
            if del_gasto(del_id):
                st.success("Eliminado ✓")
                st.rerun()
    else:
        st.info("Aún no hay gastos registrados.")

# ════════════════════════════════════════════════════════════════
# TAB NOTAS
# ════════════════════════════════════════════════════════════════
with tab_notas:
    st.subheader("Nueva nota")
    col_nt, col_tag, col_aut = st.columns([3, 2, 1])
    with col_nt:  texto  = st.text_area("Nota", height=80, placeholder="Escribí algo — tu pareja lo ve al instante...", label_visibility="collapsed")
    with col_tag: tag    = st.selectbox("Tipo", ["💡 Idea","⚠️ Importante","🍽️ Restaurante","🏨 Hotel","🎾 Pádel","🛍️ Compras","📝 General"], label_visibility="collapsed")
    with col_aut: autor  = st.selectbox("Quién", ["Adilson","Esposa"], label_visibility="collapsed")

    if st.button("📤 Publicar nota", use_container_width=True):
        if texto.strip():
            if add_nota(texto.strip(), tag, autor):
                st.success("Nota publicada ✓")
                st.rerun()
        else:
            st.warning("Escribí algo primero")

    st.write("")
    st.subheader("Notas compartidas")

    if not df_notas.empty and "texto" in df_notas.columns:
        for _, row in df_notas.iloc[::-1].iterrows():
            st.markdown(textwrap.dedent(f"""
            <div class="nota-card">
                <strong>{row.get("tag","📝")}</strong> · <em>{row.get("autor","")}</em><br>
                {row.get("texto","")}
                <div class="nota-meta">🕐 {row.get("fecha","")}</div>
            </div>
            """), unsafe_allow_html=True)
            if st.button("🗑️", key=f"delnota_{row.get('id','')}"):
                if del_nota(row.get("id","")):
                    st.rerun()
    else:
        st.info("Aún no hay notas. ¡Publicá la primera!")
