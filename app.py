import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Italia & Zurich 2026 🇮🇹🇨🇭",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── ESTILOS (Optimizados para evitar indentación Markdown) ──────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.hero-box { background: linear-gradient(135deg, #3D4A5C 0%, #1A1A2E 100%); border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; color: #F7F3EE; }
.hero-title { font-size: 2rem; font-weight: 500; margin-bottom: 4px; }
.hero-sub { font-size: 0.95rem; opacity: 0.65; margin-bottom: 1.5rem; }
.hero-stats { display: flex; gap: 2rem; flex-wrap: wrap; }
.hstat-n { font-size: 1.8rem; font-weight: 500; display: block; color: #E8C96A; }
.hstat-l { font-size: 0.75rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.08em; }
.res-card { background: #fff; border: 1px solid #EDE7DC; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }
.res-card-urgente { border-left: 4px solid #C4693A; }
.res-card-ok { border-left: 4px solid #6B7A3E; }
.badge-pending { background:#FEF3CD; color:#8B6914; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }
.badge-confirmed { background:#D4EDDA; color:#1A6B32; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }
.badge-paid { background:#CCE5FF; color:#0056B3; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:500; }
.t-row { display:flex; gap:12px; padding:6px 0; border-bottom:1px solid #F0EDE8; }
.t-time { font-size:0.75rem; color:#6B7A8D; width:44px; flex-shrink:0; padding-top:3px; font-variant-numeric:tabular-nums; }
.t-ttl { font-size:0.88rem; font-weight:500; margin-bottom:2px; }
.t-desc { font-size:0.78rem; color:#6B7A8D; line-height:1.5; }
.t-tip { font-size:0.75rem; color:#8B3E1E; background:#FDE8DE; border-left:2px solid #C4693A; padding:4px 8px; margin-top:4px; border-radius:0 4px 4px 0; }
.trans-card { background:#F7F3EE; border:1px solid #EDE7DC; border-radius:10px; padding:10px 14px; display:flex; align-items:center; gap:12px; margin-bottom:6px; flex-wrap:wrap; }
.sync-ok { background:#D4EDDA; color:#1A6B32; padding:4px 12px; border-radius:20px; font-size:0.75rem; display:inline-block; }
.nota-card { background:#F7F3EE; border-radius:8px; padding:10px 14px; margin-bottom:6px; border-left:3px solid #C9A84C; font-size:0.85rem; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

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
    except: return pd.DataFrame()

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
    except: return False

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
    except: return False

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
    except: return False

# ─── DATOS COMPLETOS ──────────────────────────────────────────────────────────
RESERVAS_DEF = [
    {"id":"r01","title":"La Última Cena","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_book":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.app.goo.gl/da-vinci"},
    {"id":"r02","title":"Galería Borghese","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_book":"https://www.galleriaborghese.it","url_maps":"https://maps.app.goo.gl/borghese"},
    {"id":"r03","title":"Museos Vaticanos","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_book":"https://www.museivaticani.va","url_maps":"https://maps.app.goo.gl/vaticano"},
    {"id":"r04","title":"Cúpula Brunelleschi","city":"Florencia","fecha":"30 mayo · tarde","urgente":True,"url_book":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.app.goo.gl/duomo-fl"},
    {"id":"r05","title":"David — Accademia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.app.goo.gl/accademia"},
    {"id":"r06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.app.goo.gl/uffizi"},
    {"id":"r07","title":"Coliseo + Foro Romano","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url_book":"https://www.coopculture.it","url_maps":"https://maps.app.goo.gl/coliseo"},
    {"id":"r08","title":"Alojamiento Milán","city":"Milán","fecha":"25–28 mayo","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/milan-host"},
    {"id":"r09","title":"Alojamiento La Spezia","city":"Cinque Terre","fecha":"28–30 mayo","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/spezia-host"},
    {"id":"r10","title":"Alojamiento Florencia","city":"Florencia","fecha":"30 mayo–3 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/fl-host"},
    {"id":"r11","title":"Alojamiento Roma","city":"Roma","fecha":"3–7 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/roma-host"},
    {"id":"r12","title":"Alojamiento Nápoles","city":"Nápoles","fecha":"7–8 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/nap-host"},
    {"id":"r13","title":"Alojamiento Praiano","city":"Amalfi","fecha":"8–10 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/amalfi-host"},
    {"id":"r14","title":"Alojamiento Venecia","city":"Venecia","fecha":"10–11 junio","urgente":False,"url_book":"https://www.booking.com","url_maps":"https://maps.app.goo.gl/ven-host"},
    {"id":"r15","title":"Alojamiento Zurich","city":"Zurich","fecha":"11–14 junio","urgente":False,"url_book":"https://www.booking.com","url_maps":"https://maps.app.goo.gl/zrh-host"},
]

ITINERARIO = [
    {"city":"🏛️ Milán","dates":"D1–3 · 25–27 mayo","days":[
        {"n":"D1","date":"25 mayo","title":"Llegada y Navigli","events":[
            {"t":"10:15","hi":True,"ttl":"Llegada MXP — Inmigración","desc":"Pasaporte argentino. Calcular 30–45 min.","maps":"https://maps.app.goo.gl/mxp"},
            {"t":"11:30","hi":False,"ttl":"Malpensa Express → Centrale","desc":"52 min · €13/p · Validar antes de subir.","maps":"https://maps.app.goo.gl/centrale"},
            {"t":"13:30","hi":False,"ttl":"Check-in + almuerzo","desc":"Risotto alla milanese."},
            {"t":"18:00","hi":False,"ttl":"Navigli + Aperitivo","desc":"Aperol Spritz junto al canal.","maps":"https://maps.app.goo.gl/navigli"},
        ]},
        {"n":"D2","date":"26 mayo","title":"Da Vinci y Duomo","events":[
            {"t":"08:15","hi":True,"ttl":"★ LA ÚLTIMA CENA","desc":"15 min de visita exacta.","tip":"Vivaticket urgente","maps":"https://maps.app.goo.gl/da-vinci"},
            {"t":"10:30","hi":True,"ttl":"Duomo — terrazas","desc":"Ascensor a los chapiteles.","maps":"https://maps.app.goo.gl/duomo-mi"},
            {"t":"15:00","hi":False,"ttl":"Corso Buenos Aires","desc":"Shopping. La calle comercial más larga.","maps":"https://maps.app.goo.gl/shopping-mi"},
        ]},
        {"n":"D3","date":"27 mayo","title":"Brera e Isola","events":[
            {"t":"09:00","hi":True,"ttl":"Pinacoteca di Brera","desc":"Mantegna y Raphael.","maps":"https://maps.app.goo.gl/brera"},
            {"t":"11:30","hi":False,"ttl":"Bosco Verticale","desc":"Bosque vertical de Boeri.","maps":"https://maps.app.goo.gl/bosco"},
        ]},
    ]},
    {"city":"🌊 Cinque Terre","dates":"D4–5 · 28–29 mayo","days":[
        {"n":"D4","date":"28 mayo","title":"Riomaggiore y Manarola","events":[
            {"t":"11:30","hi":False,"ttl":"Llegada La Spezia","desc":"Cinque Terre Card €29.50/2 días."},
            {"t":"12:30","hi":True,"ttl":"Riomaggiore","desc":"Puerto pequeño fotogénico.","maps":"https://maps.app.goo.gl/rio"},
            {"t":"15:30","hi":True,"ttl":"Manarola","desc":"La foto icónica de las casas pastel.","maps":"https://maps.app.goo.gl/mana"},
        ]},
        {"n":"D5","date":"29 mayo","title":"Vernazza y Monterosso","events":[
            {"t":"08:00","hi":True,"ttl":"Vernazza","desc":"Pueblo medieval.","maps":"https://maps.app.goo.gl/ver"},
            {"t":"11:00","hi":True,"ttl":"Senderismo a Monterosso","desc":"3.5km · 2h · Vistas brutales.","tip":"Llevar calzado firme","maps":"https://maps.app.goo.gl/hike"},
        ]},
    ]},
    {"city":"🌸 Florencia","dates":"D6–9 · 30 mayo–2 junio","days":[
        {"n":"D6","date":"30 mayo","title":"Cúpula y Piazzale","events":[
            {"t":"11:00","hi":True,"ttl":"Duomo + Cúpula","desc":"463 escalones. Reserva obligatoria.","maps":"https://maps.app.goo.gl/cupula"},
            {"t":"18:30","hi":True,"ttl":"Piazzale Michelangelo","desc":"Atardecer sobre Florencia.","maps":"https://maps.app.goo.gl/piazzale"},
        ]},
        {"n":"D7","date":"31 mayo","title":"Uffizi y David","events":[
            {"t":"08:30","hi":True,"ttl":"Galería degli Uffizi","desc":"Botticelli y Leonardo.","maps":"https://maps.app.goo.gl/uffizi"},
            {"t":"14:00","hi":True,"ttl":"David de Michelangelo","desc":"El original en la Accademia.","maps":"https://maps.app.goo.gl/david"},
        ]},
        {"n":"D8","date":"1 junio","title":"Pitti y Boboli","events":[
            {"t":"09:00","hi":False,"ttl":"Palazzo Pitti","desc":"Residencia de los Medici."},
            {"t":"16:00","hi":True,"ttl":"Cappelle Medicee","desc":"Esculturas de Michelangelo.","maps":"https://maps.app.goo.gl/medici"},
        ]},
        {"n":"D9","date":"2 junio","title":"Siena","events":[
            {"t":"09:00","hi":True,"ttl":"Piazza del Campo","desc":"La plaza más bella de Italia.","maps":"https://maps.app.goo.gl/siena"},
            {"t":"10:30","hi":False,"ttl":"Duomo di Siena","desc":"Pavimento de mármol único."},
        ]},
    ]},
    {"city":"🏟️ Roma","dates":"D10–13 · 3–6 junio","days":[
        {"n":"D10","date":"3 junio","title":"Vaticano","events":[
            {"t":"10:30","hi":True,"ttl":"Museos Vaticanos","desc":"Capilla Sixtina. Reserva obligatoria.","maps":"https://maps.app.goo.gl/vaticano"},
            {"t":"14:00","hi":False,"ttl":"Basílica San Pedro","desc":"Cúpula: vistas de la plaza.","maps":"https://maps.app.goo.gl/basilica"},
        ]},
        {"n":"D11","date":"4 junio","title":"Roma Imperial","events":[
            {"t":"08:00","hi":True,"ttl":"Coliseo + Foro","desc":"Historia viva. 4h de visita.","maps":"https://maps.app.goo.gl/coliseo"},
            {"t":"17:30","hi":False,"ttl":"Trastevere","desc":"Cena típica en el barrio bohemio.","maps":"https://maps.app.goo.gl/trastevere"},
        ]},
        {"n":"D12","date":"5 junio","title":"Borghese y Pádel","events":[
            {"t":"09:00","hi":False,"ttl":"Pantheon + Trevi","desc":"Tirar la moneda de espaldas.","maps":"https://maps.app.goo.gl/trevi"},
            {"t":"15:00","hi":True,"ttl":"Galería Borghese","desc":"Apolo y Dafne de Bernini.","maps":"https://maps.app.goo.gl/borghese"},
            {"t":"18:00","hi":True,"ttl":"★ Padel Nuestro Roma","desc":"Shopping de palas.","maps":"https://maps.app.goo.gl/padel-roma"},
        ]},
        {"n":"D13","date":"6 junio","title":"Sant'Angelo","events":[
            {"t":"09:00","hi":False,"ttl":"Castel Sant'Angelo","desc":"Vistas del Tíber."},
            {"t":"14:00","hi":False,"ttl":"Tarde libre","desc":"Compras en Via del Corso."},
        ]},
    ]},
    {"city":"🍕 Nápoles","dates":"D14 · 7 junio","days":[
        {"n":"D14","date":"7 junio","title":"Pompeya y Pizza","events":[
            {"t":"10:00","hi":True,"ttl":"Pompeya","desc":"Ciudad detenida en el tiempo.","maps":"https://maps.app.goo.gl/pompeya"},
            {"t":"19:30","hi":True,"ttl":"L'Antica Pizza Da Michele","desc":"La verdadera pizza napolitana.","maps":"https://maps.app.goo.gl/pizza"},
        ]},
    ]},
    {"city":"🌅 Costa Amalfi","dates":"D15–16 · 8–9 junio","days":[
        {"n":"D15","date":"8 junio","title":"Positano","events":[
            {"t":"10:30","hi":True,"ttl":"Playa Grande","desc":"Vistas de las casas en cascada.","maps":"https://maps.app.goo.gl/positano"},
            {"t":"15:00","hi":False,"ttl":"Amalfi ciudad","desc":"Duomo árabe-normando.","maps":"https://maps.app.goo.gl/amalfi"},
        ]},
        {"n":"D16","date":"9 junio","title":"Sentiero degli Dei","events":[
            {"t":"08:00","hi":True,"ttl":"Villa Cimbrone","desc":"Terraza del Infinito en Ravello.","maps":"https://maps.app.goo.gl/ravello"},
            {"t":"11:00","hi":True,"ttl":"Sentiero degli Dei","desc":"7.8km de caminata sobre el mar.","tip":"Día espectacular","maps":"https://maps.app.goo.gl/gods"},
        ]},
    ]},
    {"city":"🚤 Venecia","dates":"D17 · 10 junio","days":[
        {"n":"D17","date":"10 junio","title":"Gran Canal","events":[
            {"t":"13:00","hi":True,"ttl":"Vaporetto Línea 1","desc":"Paseo por el Gran Canal.","maps":"https://maps.app.goo.gl/venecia"},
            {"t":"15:00","hi":True,"ttl":"San Marcos","desc":"Basílica y Campanile.","maps":"https://maps.app.goo.gl/marcos"},
            {"t":"19:30","hi":False,"ttl":"Cena en Cannaregio","desc":"Zona menos turística y auténtica."},
        ]},
    ]},
    {"city":"🇨🇭 Zurich","dates":"D18–20 · 11–13 junio","days":[
        {"n":"D18","date":"11 junio","title":"Altstadt","events":[
            {"t":"14:00","hi":False,"ttl":"Bahnhofstrasse","desc":"Shopping de lujo y lago."},
            {"t":"15:30","hi":True,"ttl":"Grossmünster","desc":"Vistas desde las torres.","maps":"https://maps.app.goo.gl/zrh"},
        ]},
        {"n":"D19","date":"12 junio","title":"Lago y Fondue","events":[
            {"t":"10:00","hi":True,"ttl":"Crucero por el lago","desc":"Vistas de los Alpes."},
            {"t":"20:00","hi":True,"ttl":"Cena Fondue","desc":"Swiss Chuchi en el centro.","maps":"https://maps.app.goo.gl/fondue"},
        ]},
        {"n":"D20","date":"13 junio","title":"Uetliberg","events":[
            {"t":"09:00","hi":False,"ttl":"Uetliberg","desc":"Vistas de toda la ciudad.","maps":"https://maps.app.goo.gl/uetliberg"},
            {"t":"19:00","hi":True,"ttl":"Última cena 🥂","desc":"Cierre de viaje."},
        ]},
    ]},
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · €13/p","€13","https://www.trenord.it"),
    ("🚄","Milano → La Spezia","Intercity · 3h","€25–35","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · Card incluida","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Florencia","Intercity · 2h","€15–20","https://www.trenitalia.com"),
    ("🚌","Florencia ↔ Siena","Bus SENA · 1.5h","€9","https://www.tiemmespa.it"),
    ("🚄","Florencia → Roma","Frecciarossa · 1h30","€25–45","https://www.trenitalia.com"),
    ("🚄","Roma → Nápoles","Frecciarossa · 1h10","€20–35","https://www.trenitalia.com"),
    ("🚂","Nápoles → Pompeya","Circumvesuviana · 40 min","€3/p","https://www.eavsrl.it"),
    ("⛵","Nápoles → Positano","Ferry · 65 min","€20/p","https://www.alilauro.it"),
    ("🚌","Costa Amalfi (Bus)","Positano ↔ Amalfi ↔ Ravello","€2.50","https://www.sitasudtrasporti.it"),
    ("🚄","Nápoles → Venecia","Frecciarossa · 5h","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia","Pase 24h","€25","https://actv.avmspa.it"),
    ("🚄","Venecia → Zurich","EuroCity directo · 4h45","€40–60","https://www.sbb.ch"),
    ("🚄","Zurich HB → Aeropuerto","SBB · 10 min","€4","https://www.sbb.ch"),
]

# ─── HELPERS UI ───────────────────────────────────────────────────────────────
def badge_html(estado):
    cls = {"pending":"badge-pending","confirmed":"badge-confirmed","paid":"badge-paid"}.get(estado,"badge-pending")
    lbl = {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(estado,"⏳ Pendiente")
    return f'<span class="{cls}">{lbl}</span>'

# ─── CARGAR DATOS ─────────────────────────────────────────────────────────────
try:
    df_res = load_sheet_data("viaje_reservas")
    df_gas = load_sheet_data("viaje_gastos")
    df_notas = load_sheet_data("viaje_notas")
    sheets_ok = True
except:
    df_res = df_gas = df_notas = pd.DataFrame()
    sheets_ok = False

def get_reserva_data(res_id):
    if df_res.empty or "id" not in df_res.columns: return {}
    row = df_res[df_res["id"] == res_id]
    return row.iloc[0].to_dict() if not row.empty else {}

# ─── HERO ─────────────────────────────────────────────────────────────────────
ok_count = sum(1 for r in RESERVAS_DEF if get_reserva_data(r["id"]).get("estado") in ("confirmed","paid"))
total_gas = df_gas["monto"].astype(float).sum() if not df_gas.empty and "monto" in df_gas.columns else 0

st.markdown(f"""<div class="hero-box"><div class="hero-title">🇮🇹 Italia & Zurich 2026 🇨🇭</div><div class="hero-sub">Luna de Miel · 25 mayo → 14 junio · Compartido en tiempo real</div><div class="hero-stats"><div><span class="hstat-n">{ok_count}/{len(RESERVAS_DEF)}</span><span class="hstat-l">Reservas ok</span></div><div><span class="hstat-n">€{total_gas:,.0f}</span><span class="hstat-l">Gastado</span></div><div><span class="hstat-n">20</span><span class="hstat-l">Días totales</span></div></div></div>""", unsafe_allow_html=True)
if sheets_ok: st.markdown('<span class="sync-ok">🟢 Google Sheets conectado</span>', unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_res, tab_itin, tab_trans, tab_gas, tab_notas = st.tabs(["🎟️ Reservas", "🗺️ Itinerario", "🚄 Transportes", "💰 Gastos", "📝 Notas"])

with tab_res:
    filtro = st.selectbox("Filtrar por ciudad", ["Todas"] + list(dict.fromkeys(r["city"] for r in RESERVAS_DEF)))
    for r in RESERVAS_DEF:
        if filtro != "Todas" and r["city"] != filtro: continue
        rd = get_reserva_data(r["id"])
        st.markdown(f'<div class="res-card {"res-card-urgente" if r["urgente"] else "res-card-ok"}"><strong>{r["title"]}</strong> {badge_html(rd.get("estado","pending"))}<br><small>{r["city"]} · {r["fecha"]}</small></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nestado = st.selectbox("Estado", ["pending","confirmed","paid"], key=f"s{r['id']}", index=["pending","confirmed","paid"].index(rd.get("estado","pending")))
        with c2: nmonto = st.number_input("€", value=float(rd.get("monto",0) or 0), key=f"m{r['id']}", step=1.0)
        nurl = st.text_input("URL Reserva", value=rd.get("url_reserva",""), key=f"u{r['id']}")
        if st.button("Guardar", key=f"b{r['id']}"):
            if save_reserva(r["id"], nestado, nurl, "", nmonto, ""): st.rerun()

with tab_itin:
    selected_city = st.selectbox("Ciudad", [c["city"] for c in ITINERARIO])
    city_data = next(c for c in ITINERARIO if c["city"] == selected_city)
    for day in city_data["days"]:
        with st.expander(f"{day['n']} · {day['date']} — {day['title']}", expanded=(day == city_data["days"][0])):
            for ev in day["events"]:
                dot = "🟠" if ev["hi"] else "⚪"
                tip_h = f'<div class="t-tip">⚠️ {ev["tip"]}</div>' if ev.get("tip") else ""
                # Renderizado HTML en una línea para evitar el bloque de código Markdown
                h_ev = f'<div class="t-row"><span class="t-time">{ev["t"]}</span><span>{dot}</span><div><div class="t-ttl">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip_h}</div></div>'
                st.markdown(h_ev, unsafe_allow_html=True)
                if ev.get("maps"): st.markdown(f'<a href="{ev["maps"]}" target="_blank" style="font-size:0.75rem;margin-left:60px;color:#0056B3">📍 Abrir en Maps</a>', unsafe_allow_html=True)

with tab_trans:
    for icon, route, detail, price, url in TRANSPORTES:
        st.markdown(f'<div class="trans-card"><span>{icon}</span> <strong>{route}</strong> ({detail}) <span style="margin-left:auto;color:#C4693A">{price}</span> <a href="{url}" target="_blank" style="margin-left:10px;font-size:0.75rem">🔗 Comprar</a></div>', unsafe_allow_html=True)

with tab_gas:
    st.metric("Total Gastado", f"€{total_gas:,.0f}")
    with st.form("gasto"):
        d = st.text_input("Descripción")
        c = st.selectbox("Categoría", ["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        m = st.number_input("Monto €", min_value=0.0)
        if st.form_submit_button("➕ Agregar Gasto"):
            if d and m > 0:
                if add_gasto(d, c, m): st.rerun()
    if not df_gas.empty: st.dataframe(df_gas[["descripcion","categoria","monto","fecha"]], use_container_width=True, hide_index=True)

with tab_notas:
    with st.form("nota"):
        txt = st.text_area("Nueva nota")
        aut = st.selectbox("Autor", ["Adilson","Esposa"])
        if st.form_submit_button("📤 Publicar"):
            if txt.strip():
                if add_nota(txt, "General", aut): st.rerun()
    if not df_notas.empty:
        for _, n in df_notas.iloc[::-1].iterrows():
            st.markdown(f'<div class="nota-card"><strong>{n["autor"]}</strong>: {n["texto"]}<div style="font-size:0.7rem;color:#6B7A8D;margin-top:4px">🕐 {n["fecha"]}</div></div>', unsafe_allow_html=True)
