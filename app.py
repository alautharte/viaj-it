import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Italia & Zurich 2026 🇮🇹", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--cream:#F7F3EE;--parchment:#EDE7DC;--terracotta:#C4693A;--tl:#E8956D;--td:#8B3E1E;--olive:#6B7A3E;--ol:#9AAD5A;--slate:#3D4A5C;--sl:#6B7A8D;--gold:#C9A84C;--gl:#E8C96A;--ink:#1A1A2E;--w:#FFFFFF;}
.stApp{background-color:var(--cream)!important;}
.stApp,.stApp p,.stApp div,.stApp span,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp li{font-family:'DM Sans',sans-serif!important;color:var(--ink)!important;}
#MainMenu,footer,header,[data-testid="stDecoration"],[data-testid="collapsedControl"]{visibility:hidden!important;display:none!important;}
.stTabs [data-baseweb="tab-list"]{gap:5px;background:var(--parchment);padding:8px 10px;border-radius:12px;margin-bottom:1.5rem;}
.stTabs [data-baseweb="tab"]{padding:7px 16px;border-radius:8px;background:rgba(255,255,255,0.5);border:none!important;}
.stTabs [data-baseweb="tab"] p{color:var(--slate)!important;font-weight:600!important;font-size:0.85rem!important;}
.stTabs [aria-selected="true"]{background:var(--w)!important;box-shadow:0 2px 6px rgba(0,0,0,0.08)!important;}
.stTabs [aria-selected="true"] p{color:var(--td)!important;}
.stTabs [data-baseweb="tab-highlight"],[data-baseweb="tab-border"]{display:none!important;}
div[data-testid="stRadio"]>div{flex-direction:row!important;flex-wrap:wrap!important;gap:7px!important;background:var(--w)!important;padding:10px!important;border-radius:12px!important;border:1px solid var(--parchment)!important;}
div[data-testid="stRadio"]>div>label{background-color:var(--parchment)!important;padding:7px 14px!important;border-radius:20px!important;cursor:pointer!important;border:1.5px solid transparent!important;}
div[data-testid="stRadio"]>div>label p{color:var(--ink)!important;font-weight:600!important;font-size:0.82rem!important;margin:0!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"]{background-color:var(--terracotta)!important;border-color:var(--td)!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"] p{color:var(--w)!important;}
div[data-testid="stRadio"] div[role="radiogroup"] label>div:first-child{display:none!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background-color:var(--w)!important;color:var(--ink)!important;border:1px solid var(--parchment)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stNumberInput label{color:var(--slate)!important;font-size:0.82rem!important;font-weight:500!important;}
.stSelectbox>div>div,[data-baseweb="select"],[data-baseweb="select"] *{background:var(--w)!important;color:var(--ink)!important;border:1px solid var(--parchment)!important;}
.stButton>button{background:var(--terracotta)!important;color:var(--w)!important;border:none!important;border-radius:8px!important;font-weight:600!important;font-family:'DM Sans',sans-serif!important;padding:8px 20px!important;}
.stButton>button:hover{background:var(--td)!important;}
[data-testid="stMetric"]{background:var(--w);border:1px solid var(--parchment);border-radius:10px;padding:1rem!important;}
[data-testid="stMetricLabel"] p{color:var(--sl)!important;font-size:0.78rem!important;}
[data-testid="stMetricValue"]{color:var(--td)!important;font-family:'Playfair Display',serif!important;}
[data-testid="stMetricDelta"]{color:var(--olive)!important;}
[data-testid="stExpander"]{border:1px solid var(--parchment)!important;border-radius:10px!important;background:var(--w)!important;margin-bottom:6px!important;}
[data-testid="stExpander"] summary p{color:var(--ink)!important;font-weight:600!important;}

/* HERO */
.hero{background:linear-gradient(135deg,#3D4A5C 0%,#1A1A2E 100%);border-radius:16px 16px 0 0;padding:2.5rem 2rem 2rem;text-align:center;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(196,105,58,0.2) 0%,transparent 60%),radial-gradient(ellipse at 70% 30%,rgba(201,168,76,0.12) 0%,transparent 50%);}
.hero-inner{position:relative;z-index:1;}
.hero-flag{font-size:1.8rem;letter-spacing:8px;margin-bottom:6px;}
.hero-title{font-family:'Playfair Display',serif!important;font-size:clamp(1.8rem,4vw,3rem)!important;color:#F7F3EE!important;line-height:1.1;margin-bottom:6px;}
.hero-title em{color:#E8C96A!important;font-style:italic;}
.hero-sub{font-size:0.9rem!important;color:rgba(247,243,238,0.6)!important;margin-bottom:1.2rem;}
.hero-dates{display:inline-flex;gap:1rem;background:rgba(247,243,238,0.1);border:0.5px solid rgba(247,243,238,0.2);border-radius:50px;padding:0.4rem 1.2rem;font-size:0.82rem!important;color:#E8C96A!important;}
.stats-bar{display:flex;background:var(--terracotta);border-radius:0 0 16px 16px;margin-bottom:1.5rem;flex-wrap:wrap;}
.stat-item{flex:1;min-width:90px;padding:0.85rem 1rem;text-align:center;border-right:0.5px solid rgba(247,243,238,0.2);}
.stat-item:last-child{border-right:none;}
.stat-num{font-family:'Playfair Display',serif!important;font-size:1.5rem!important;color:#F7F3EE!important;display:block;line-height:1;font-weight:600;}
.stat-lbl{font-size:0.67rem!important;color:rgba(247,243,238,0.7)!important;text-transform:uppercase;letter-spacing:0.1em;margin-top:3px;display:block;}

/* SECCIONES */
.sec-hdr{border-bottom:2px solid var(--parchment);padding-bottom:0.75rem;margin-bottom:1.25rem;}
.sec-title{font-family:'Playfair Display',serif!important;font-size:1.8rem!important;color:var(--td)!important;}
.sec-meta{font-size:0.85rem!important;color:var(--sl)!important;margin-top:2px;font-weight:500;}

/* CARD */
.card{background:var(--w);border-radius:12px;border:1px solid var(--parchment);margin-bottom:1rem;box-shadow:0 2px 8px rgba(26,26,46,0.05);overflow:hidden;}
.card-header{display:flex;align-items:center;gap:10px;padding:0.75rem 1.2rem;background:var(--parchment);border-bottom:1px solid rgba(196,105,58,0.15);}
.day-badge{background:var(--terracotta);color:var(--w)!important;font-size:0.72rem;font-weight:700;padding:3px 12px;border-radius:20px;white-space:nowrap;}
.card-date{font-size:0.9rem!important;font-weight:600;color:var(--slate)!important;}
.card-city{font-size:0.78rem!important;color:var(--sl)!important;margin-left:auto;}

/* TIMELINE */
.timeline{padding:0 0 4px;}
.t-row{display:grid;grid-template-columns:52px 14px 1fr;gap:0 12px;padding:12px 18px;border-bottom:1px solid var(--parchment);}
.t-row:last-child{border-bottom:none;}
.t-time{font-size:0.78rem!important;color:var(--sl)!important;text-align:right;padding-top:3px;font-weight:600;font-variant-numeric:tabular-nums;}
.t-dot{width:10px;height:10px;border-radius:50%;background:var(--parchment);border:2px solid var(--tl);margin-top:4px;flex-shrink:0;}
.t-dot.hi{background:var(--terracotta);border-color:var(--td);}
.t-title{font-size:0.9rem!important;font-weight:700;color:var(--ink)!important;margin-bottom:3px;}
.t-title.star::before{content:'★ ';color:#C9A84C;}
.t-desc{font-size:0.8rem!important;color:var(--sl)!important;line-height:1.55;}
.t-tip{font-size:0.75rem!important;color:var(--td)!important;background:rgba(196,105,58,0.07);border-left:3px solid var(--tl);padding:5px 10px;margin-top:6px;border-radius:0 4px 4px 0;line-height:1.4;}
.t-actions{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}

/* TAGS */
.tag{display:inline-flex;align-items:center;font-size:0.7rem;padding:2px 9px;border-radius:20px;font-weight:600;}
.tag-train{background:#E8F0FB;color:#2A5FAC!important;}
.tag-walk{background:#EBF5E1;color:#3A6B18!important;}
.tag-food{background:#FDE8DE;color:#8B3E1E!important;}
.tag-museum{background:#F5E8F5;color:#7A3A8C!important;}
.tag-shop{background:#FFF0E0;color:#8B5010!important;}
.tag-boat{background:#E0F4EF;color:#0F6E56!important;}
.tag-sleep{background:#EEF0FD;color:#4A50B0!important;}
.tag-bus{background:#FEF3E2;color:#8B5E10!important;}
.tag-padel{background:#E8F5E8;color:#2A6B2A!important;}
.tag-ticket{background:#FCEBEB;color:#A32D2D!important;}

/* BOTONES LINK */
.btn{display:inline-flex;align-items:center;gap:4px;font-size:0.72rem;padding:4px 10px;border-radius:6px;border:1.5px solid;text-decoration:none!important;font-weight:600;margin-right:4px;background:var(--w);cursor:pointer;}
.btn-maps{border-color:#4285F4;color:#4285F4!important;}
.btn-booking{border-color:#003580;color:#003580!important;}
.btn-airbnb{border-color:#FF5A5F;color:#FF5A5F!important;}
.btn-ticket{border-color:var(--olive);color:var(--olive)!important;}
.btn-tren{border-color:#B8000A;color:#B8000A!important;}

/* HOTEL CARD */
.hotel-card{border:1px solid var(--parchment);border-radius:12px;padding:1.1rem 1.25rem;margin:0.5rem 0 1.25rem;background:var(--w);box-shadow:0 2px 6px rgba(0,0,0,0.04);}
.hotel-name{font-family:'Playfair Display',serif!important;font-size:1rem!important;color:var(--slate)!important;margin-bottom:4px;font-weight:600;}
.hotel-meta{font-size:0.8rem!important;color:var(--sl)!important;line-height:1.6;margin-bottom:6px;}
.hotel-price{display:inline-block;font-size:0.82rem!important;font-weight:700;background:rgba(107,122,62,0.1);color:var(--olive)!important;padding:3px 12px;border-radius:20px;margin-bottom:8px;}
.hotel-actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}

/* TRANSPORT CARD */
.tc{background:var(--w);border:1px solid var(--parchment);border-radius:10px;padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;box-shadow:0 1px 3px rgba(0,0,0,0.03);}
.tc-icon{font-size:1.3rem;width:28px;text-align:center;}
.tc-route{font-size:0.9rem!important;font-weight:700;color:var(--slate)!important;}
.tc-detail{font-size:0.78rem!important;color:var(--sl)!important;margin-top:1px;}
.tc-price{font-size:0.88rem!important;font-weight:700;color:var(--terracotta)!important;margin-left:auto;}

/* ALERTAS */
.alert{background:rgba(196,105,58,0.08);border:1px solid rgba(196,105,58,0.3);border-radius:9px;padding:0.85rem 1rem;font-size:0.82rem!important;color:var(--td)!important;margin-bottom:1rem;line-height:1.6;}
.alert strong{color:var(--td)!important;}
.alert-green{background:rgba(107,122,62,0.08);border-color:rgba(107,122,62,0.3);color:var(--olive)!important;}
.alert-green strong{color:var(--olive)!important;}
.alert-blue{background:#EBF4FF;border-color:#90C4F9;color:#1A4A8A!important;}
.alert-blue strong{color:#1A4A8A!important;}

/* RESERVAS */
.res-card{background:var(--w);border:1px solid var(--parchment);border-radius:12px;padding:1rem 1.25rem;margin-bottom:0.5rem;box-shadow:0 2px 6px rgba(0,0,0,0.04);}
.res-urg{border-left:4px solid var(--terracotta);}
.res-ok{border-left:4px solid var(--olive);}
.res-title{font-size:0.95rem!important;font-weight:700;color:var(--ink)!important;}
.res-meta{font-size:0.78rem!important;color:var(--sl)!important;margin:3px 0 6px;}
.b-pending{background:#FEF3CD;color:#8B6914!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.b-confirmed{background:#D4EDDA;color:#1A6B32!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.b-paid{background:#CCE5FF;color:#0056B3!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.url-saved{font-size:0.75rem!important;color:#0056B3!important;word-break:break-all;display:block;margin-top:4px;}

/* MISC */
.nota-card{background:var(--cream);border-radius:9px;padding:10px 14px;margin-bottom:8px;border-left:3px solid var(--gold);font-size:0.85rem!important;color:var(--ink)!important;}
.nota-meta{font-size:0.72rem!important;color:var(--sl)!important;margin-top:5px;}
.tip-card{background:var(--w);border:1px solid var(--parchment);border-radius:10px;padding:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.03);margin-bottom:0.75rem;}
.tip-icon{font-size:1.4rem;margin-bottom:5px;}
.tip-title{font-size:0.88rem!important;font-weight:700;color:var(--slate)!important;margin-bottom:4px;}
.tip-text{font-size:0.78rem!important;color:var(--sl)!important;line-height:1.6;}
.prog-outer{background:var(--parchment);border-radius:5px;height:8px;overflow:hidden;margin:6px 0;}
.prog-inner{height:100%;border-radius:5px;background:var(--terracotta);}
.budget-table{width:100%;border-collapse:collapse;font-size:0.84rem;}
.budget-table th{text-align:left;padding:10px 12px;background:var(--parchment);color:var(--slate)!important;font-weight:700;font-size:0.72rem;text-transform:uppercase;}
.budget-table td{padding:10px 12px;border-bottom:1px solid var(--parchment);color:var(--ink)!important;font-weight:500;}
.budget-table tr.tot td{font-weight:700;color:var(--td)!important;border-top:2px solid var(--tl);border-bottom:none;}
.sync-ok{background:#D4EDDA;color:#1A6B32!important;padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:600;display:inline-block;margin-bottom:1rem;}
.sync-err{background:#F8D7DA;color:#721C24!important;padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:600;display:inline-block;margin-bottom:1rem;}
</style>
""", unsafe_allow_html=True)

# ─── SHEETS ───────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def get_wb():
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets():
    wb = get_wb()
    ex = [s.title for s in wb.worksheets()]
    needed = {
        "viaje_reservas":["id","estado","tipo_aloj","url_reserva","confirmacion","monto","notas_int","updated"],
        "viaje_gastos":  ["id","descripcion","categoria","monto","fecha"],
        "viaje_notas":   ["id","texto","tag","autor","fecha"],
    }
    sheets = {}
    for name, headers in needed.items():
        if name not in ex:
            ws = wb.add_worksheet(title=name, rows=500, cols=len(headers))
            ws.append_row(headers)
        sheets[name] = wb.worksheet(name)
    return sheets

@st.cache_data(ttl=20)
def load_reservas():
    try: return pd.DataFrame(get_wb().worksheet("viaje_reservas").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=20)
def load_gastos():
    try: return pd.DataFrame(get_wb().worksheet("viaje_gastos").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=20)
def load_notas():
    try: return pd.DataFrame(get_wb().worksheet("viaje_notas").get_all_records())
    except: return pd.DataFrame()

def save_reserva(rid, estado, tipo, url, conf, monto, notas):
    try:
        s = ensure_sheets(); ws = s["viaje_reservas"]
        recs = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [rid, estado, tipo, url, conf, monto, notas, now]
        for i, r in enumerate(recs, start=2):
            if r.get("id") == rid:
                ws.update(f"A{i}:H{i}", [row]); st.cache_data.clear(); return True
        ws.append_row(row); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def add_gasto(desc, cat, monto):
    try:
        s = ensure_sheets()
        gid = f"g{datetime.now().strftime('%m%d%H%M%S')}"
        s["viaje_gastos"].append_row([gid, desc, cat, monto, datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_gasto(gid):
    try:
        s = ensure_sheets(); ws = s["viaje_gastos"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(gid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

def add_nota(texto, tag, autor):
    try:
        s = ensure_sheets()
        nid = f"n{datetime.now().strftime('%m%d%H%M%S')}"
        s["viaje_notas"].append_row([nid, texto, tag, autor, datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_nota(nid):
    try:
        s = ensure_sheets(); ws = s["viaje_notas"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(nid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

# ─── DATOS ITINERARIO COMPLETOS (del HTML) ────────────────────────────────────

ITIN = {
"🏛️ Milán": {
  "meta":"Días 1–3 · 25, 26 y 27 mayo · 3 noches",
  "hotel_nombre":"Hotel Ariston ★★★ (o similar zona Centrale/Navigli)",
  "hotel_meta":"Central para metro · Desayuno incluido · Habitación doble<br>Alternativa premium: Hotel Dei Cavalieri (junto al Duomo, ~€110/noche)",
  "hotel_precio":"~€70–90 / noche · 3 noches",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2&no_rooms=1&nflt=price%3DUSD-min-100-1&order=bayesian_review_score",
  "hotel_airbnb":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2",
  "hotel_maps":"https://maps.google.com/?q=Hotel+Ariston+Milan",
  "transporte": None,
  "alerta": None,
  "dias":[
    {"n":"Día 1","date":"Lunes 25 mayo — Llegada y primer paseo","city":"Milán","ev":[
      {"t":"10:15","hi":True,"title":"Llegada MXP — Inmigración y aduana","desc":"Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta.","tip":None,"tags":[],"btns":[]},
      {"t":"11:30","hi":False,"title":"Malpensa Express → Milano Centrale","desc":"Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.","tip":None,"tags":["🚄 €13/persona|tag-train"],"btns":[("Trenord","https://www.trenord.it/en/tickets/relations/malpensa-express/","btn-tren"),("📍 Maps","https://maps.google.com/?q=Milano+Centrale+Station","btn-maps")]},
      {"t":"13:30","hi":False,"title":"Check-in + almuerzo tranquilo","desc":"Pedir risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones.","tip":None,"tags":["🍝 Risotto|tag-food"],"btns":[]},
      {"t":"15:00","hi":False,"title":"Siesta obligatoria","desc":"Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes.","tip":None,"tags":[],"btns":[]},
      {"t":"18:00","hi":False,"title":"Paseo Navigli + Aperitivo","desc":"Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.","tip":None,"tags":["🚶 Paseo|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Navigli+Milan","btn-maps")]},
    ]},
    {"n":"Día 2","date":"Martes 26 mayo — Última Cena, Duomo, Shopping y Pádel","city":"Milán","ev":[
      {"t":"08:00","hi":False,"title":"Desayuno italiano","desc":"Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.","tip":None,"tags":["☕ €3|tag-food"],"btns":[]},
      {"t":"08:15","hi":True,"title":"LA ÚLTIMA CENA — Santa Maria delle Grazie","desc":"El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.","tip":"⚠️ CRÍTICO: Reservar hoy mismo en cenacolodavincimilano.vivaticket.com — Los cupos de mayo se agotan meses antes.","tags":["🎨 €15 + €2 reserva|tag-museum"],"btns":[("🎟️ Reservar ahora","https://cenacolodavincimilano.vivaticket.com","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan","btn-maps")]},
      {"t":"10:00","hi":True,"title":"Duomo di Milano — terrazas","desc":"Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán. Reservar online — sin reserva hay fila.","tip":None,"tags":["⛪ €15 terraza|tag-museum"],"btns":[("🎟️ Reservar","https://ticket.duomomilano.it","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Duomo+di+Milano","btn-maps")]},
      {"t":"11:30","hi":False,"title":"Galleria Vittorio Emanuele II + Scala","desc":"Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).","tip":None,"tags":["🚶 Gratis|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II+Milan","btn-maps")]},
      {"t":"13:00","hi":False,"title":"Almuerzo en Brera","desc":"Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15. Buscar en callejuelas laterales.","tip":None,"tags":["🍽️ €15|tag-food"],"btns":[("📍 Brera","https://maps.google.com/?q=Brera+Milan","btn-maps")]},
      {"t":"15:00","hi":True,"title":"Shopping — Corso Buenos Aires","desc":"La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas accesibles. 2km de tiendas. Para ropa de calidad a buen precio, es el mejor lugar de Milán.","tip":None,"tags":["🛍️ Ropa|tag-shop"],"btns":[("📍 Maps","https://maps.google.com/?q=Corso+Buenos+Aires+Milan","btn-maps")]},
      {"t":"17:30","hi":True,"title":"Padel Nuestro Milano (opcional — vale si tienen tiempo)","desc":"La mayor tienda de pádel del norte de Italia. Bullpadel, Siux, Adidas, Nox. Tienen pista interior para probar palas. Está en las afueras — evaluar si el tiempo lo permite o dejarlo para Roma.","tip":"Más conveniente visitar Padel Nuestro Roma (centro) que ésta (40 min del centro). Pero si van, abre hasta las 19:30.","tags":["🎾 Pádel|tag-padel"],"btns":[("📍 Maps","https://maps.google.com/?q=Via+Papa+Giovanni+XXIII+9a+Rodano+Millepini+Milan","btn-maps")]},
      {"t":"20:00","hi":False,"title":"Cena en Navigli","desc":"Evitar restaurantes con foto en el menú en la puerta — señal de trampa turística.","tip":None,"tags":["🍷 Cena|tag-food"],"btns":[]},
    ]},
    {"n":"Día 3","date":"Miércoles 27 mayo — Brera e Isola","city":"Milán","ev":[
      {"t":"09:00","hi":True,"title":"Pinacoteca di Brera","desc":"Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia. Calcular 2h.","tip":None,"tags":["🎨 €15|tag-museum"],"btns":[("Reservar","https://pinacotecabrera.org","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Pinacoteca+di+Brera+Milan","btn-maps")]},
      {"t":"11:30","hi":False,"title":"Barrio Isola + Bosco Verticale","desc":"El famoso \"bosque vertical\" de Stefano Boeri. El barrio Isola tiene cafés y mercaditos locales muy cool.","tip":None,"tags":["🌿 Gratis|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Bosco+Verticale+Milan","btn-maps")]},
      {"t":"13:00","hi":False,"title":"Almuerzo + tarde libre","desc":"Zona Sant'Ambrogio (Basílica del siglo IV, gratis). Tarde para compras adicionales o descanso.","tip":None,"tags":[],"btns":[]},
      {"t":"19:00","hi":False,"title":"Preparar maletas — mañana viajan a Cinque Terre","desc":"Tren 08:10 desde Milano Centrale. Poner alarma.","tip":None,"tags":["🧳 Preparación|tag-sleep"],"btns":[]},
    ]},
  ]
},
"🌊 Cinque Terre": {
  "meta":"Días 4–5 · 28 y 29 mayo · Base: La Spezia · 2 noches",
  "hotel_nombre":"Hotel Firenze ★★★ (La Spezia)",
  "hotel_meta":"5 min a pie de la estación · Habitación doble · 2 noches<br>Alternativa: alojarse directamente en Monterosso al Mare",
  "hotel_precio":"~€70–80 / noche · 2 noches",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2",
  "hotel_airbnb":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2",
  "hotel_maps":"https://maps.google.com/?q=La+Spezia+train+station",
  "transporte":("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10 desde Milano Centrale","€25–35","https://www.trenitalia.com"),
  "alerta": None,
  "dias":[
    {"n":"Día 4","date":"Jueves 28 mayo — Riomaggiore, Manarola, Corniglia","city":"Cinque Terre","ev":[
      {"t":"11:30","hi":False,"title":"Llegada La Spezia — Check-in + Cinque Terre Card","desc":"Comprar la Card 2 días en InfoParco o taquilla de la estación (~€29.50/persona). Incluye todos los trenes locales entre los pueblos.","tip":None,"tags":["🎫 €29.50 · 2 días|tag-ticket"],"btns":[("Info Card","https://www.cinqueterre.eu.com/en/cinque-terre-card","btn-ticket")]},
      {"t":"12:30","hi":True,"title":"Riomaggiore — el más fotogénico","desc":"Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà. El pesto se hace con albahaca local, piñones, parmesano y aceite ligur.","tip":None,"tags":["🍃 Pesto original|tag-food"],"btns":[("📍 Maps","https://maps.google.com/?q=Riomaggiore+Cinque+Terre","btn-maps")]},
      {"t":"15:30","hi":True,"title":"Manarola — el mirador icónico","desc":"La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.","tip":None,"tags":["📸 Foto icónica|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Manarola+Cinque+Terre","btn-maps")]},
      {"t":"17:30","hi":False,"title":"Corniglia — vista 360°","desc":"El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.","tip":None,"tags":[],"btns":[("📍 Maps","https://maps.google.com/?q=Corniglia+Cinque+Terre","btn-maps")]},
    ]},
    {"n":"Día 5","date":"Viernes 29 mayo — Vernazza, senderismo y Monterosso","city":"Cinque Terre","ev":[
      {"t":"08:00","hi":True,"title":"Vernazza — el más medieval","desc":"Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.","tip":None,"tags":[],"btns":[("📍 Maps","https://maps.google.com/?q=Vernazza+Cinque+Terre","btn-maps")]},
      {"t":"11:00","hi":True,"title":"Senderismo Vernazza → Monterosso (3.5 km · 2h)","desc":"El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir. Llevar agua y zapatos cerrados.","tip":"Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.","tags":["🥾 Trekking|tag-walk"],"btns":[("Estado senderos","https://www.parconazionale5terre.it","btn-ticket")]},
      {"t":"14:00","hi":False,"title":"Monterosso — playa y anchoas","desc":"El único pueblo con playa de arena real. Probar acciughe (anchoas de Monterosso). Reposeras ~€5. Agua ~22°C en junio.","tip":None,"tags":["🏖️ Playa|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Monterosso+al+Mare","btn-maps")]},
    ]},
  ]
},
"🌸 Florencia": {
  "meta":"Días 6–9 · 30 mayo – 2 junio · 4 noches",
  "hotel_nombre":"Hotel Davanzati ★★★ (recomendado)",
  "hotel_meta":"A 2 min del Duomo y Uffizi · Servicio excelente · Desayuno muy bueno<br>Alternativa económica: B&B Machiavelli (zona Oltrarno, ~€75/noche)",
  "hotel_precio":"~€95–110 / noche · 4 noches",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2",
  "hotel_airbnb":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2",
  "hotel_maps":"https://maps.google.com/?q=Hotel+Davanzati+Florence",
  "transporte":("🚄","La Spezia → Firenze Santa Maria Novella","Intercity · ~2h · Salida 08:30 · Directo o cambio en Pisa","€15–20","https://www.trenitalia.com"),
  "alerta": None,
  "dias":[
    {"n":"Día 6","date":"Sábado 30 mayo — Duomo + Cúpula + Piazzale","city":"Florencia","ev":[
      {"t":"11:00","hi":True,"title":"Duomo + Cúpula de Brunelleschi","desc":"La obra de ingeniería más asombrosa del Renacimiento. 463 escalones. Reservar turno online — sin reserva la fila puede ser 2–3 horas. Incluye Baptisterio y Museo del Duomo.","tip":None,"tags":["⛪ Pase ~€20|tag-museum"],"btns":[("🎟️ Reservar","https://www.ilgrandemuseodelduomo.it","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Duomo+Florence","btn-maps")]},
      {"t":"13:00","hi":False,"title":"Mercato Centrale — almuerzo","desc":"Piso superior con puestos de comida. Probar lampredotto (callos florentinos — para valientes) o pasta fresca.","tip":None,"tags":[],"btns":[("📍 Maps","https://maps.google.com/?q=Mercato+Centrale+Florence","btn-maps")]},
      {"t":"16:30","hi":False,"title":"Ponte Vecchio → Oltrarno","desc":"El puente más antiguo de Florencia con joyerías desde el siglo XVI. Al cruzar: el Florencia auténtico.","tip":None,"tags":["🌉 Paseo|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Ponte+Vecchio+Florence","btn-maps")]},
      {"t":"18:30","hi":True,"title":"Piazzale Michelangelo — atardecer","desc":"EL punto de vista de Florencia al atardecer. Vista panorámica de toda la ciudad. Llegar 30 min antes del sunset para conseguir lugar.","tip":None,"tags":["🌅 Gratis|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Piazzale+Michelangelo+Florence","btn-maps")]},
    ]},
    {"n":"Día 7","date":"Domingo 31 mayo — Uffizi + David + San Miniato","city":"Florencia","ev":[
      {"t":"08:30","hi":True,"title":"Galería degli Uffizi — Botticelli, Leonardo, Caravaggio","desc":"El museo de arte renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA — sin reserva la fila puede ser 2h+. La sala de Botticelli es la más concurrida — visitarla primero.","tip":None,"tags":["🎨 €20 + €4 reserva|tag-museum"],"btns":[("🎟️ Reservar","https://www.uffizi.it","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Uffizi+Gallery+Florence","btn-maps")]},
      {"t":"14:00","hi":True,"title":"David de Michelangelo — Accademia","desc":"5.17 metros de mármol perfecto, tallado entre 1501 y 1504. El original — el de la Piazza es una copia. 1.5h. Hay también los \"Prisioneros\" de Michelangelo.","tip":None,"tags":["🗿 €12 + reserva|tag-museum"],"btns":[("🎟️ Reservar","https://www.uffizi.it/en/the-accademia-gallery","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Accademia+Gallery+Florence","btn-maps")]},
      {"t":"17:30","hi":False,"title":"San Miniato al Monte","desc":"La iglesia más bella de Florencia para muchos — sobre una colina, entrada gratis. Los monjes rezan el Oficio en gregoriano a las 17:30 — experiencia mística si coinciden.","tip":None,"tags":["⛪ Gratis|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=San+Miniato+al+Monte+Florence","btn-maps")]},
    ]},
    {"n":"Día 8","date":"Lunes 1 junio — Palazzo Pitti + Boboli + Cappelle Medicee","city":"Florencia","ev":[
      {"t":"09:00","hi":False,"title":"Palazzo Pitti + Jardines de Boboli","desc":"El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina. Los Jardines de Boboli incluyen una gruta artificial de Buontalenti de 1583.","tip":None,"tags":["🏰 €16|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Palazzo+Pitti+Florence","btn-maps")]},
      {"t":"16:00","hi":True,"title":"Cappelle Medicee — Michelangelo","desc":"Las tumbas de los Medici con las esculturas de Michelangelo: Aurora, Crepúsculo, Día y Noche. Menos conocidas que el David pero igualmente impactantes.","tip":None,"tags":["🗿 €9|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Cappelle+Medicee+Florence","btn-maps")]},
    ]},
    {"n":"Día 9","date":"Martes 2 junio — Siena y Val d'Orcia","city":"Toscana","ev":[
      {"t":"07:30","hi":False,"title":"Bus SENA desde Florencia a Siena","desc":"Desde Autostazione di Firenze (frente a Santa Maria Novella). 1.5h · €9. Alternativa: tren más lento (~2h) con cambio en Empoli.","tip":None,"tags":["🚌 €9|tag-bus"],"btns":[("📍 Bus","https://maps.google.com/?q=Autostazione+Firenze","btn-maps")]},
      {"t":"09:00","hi":True,"title":"Piazza del Campo + Torre del Mangia","desc":"La plaza más bella de Italia en forma de concha. Escenario del Palio (carrera de caballos). La Torre tiene 400 escalones y vista impresionante de los tejados rojizos de Siena.","tip":None,"tags":["🏰 Torre €10|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Piazza+del+Campo+Siena","btn-maps")]},
      {"t":"10:00","hi":False,"title":"Duomo di Siena","desc":"El Duomo de Siena compite con Florencia en belleza. El pavimento de mármol con 56 escenas es único en el mundo.","tip":None,"tags":["⛪ €8|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Siena+Cathedral","btn-maps")]},
      {"t":"13:30","hi":False,"title":"Almuerzo en la ciudad vieja","desc":"Probar: pici all'aglione (pasta gruesa con ajo), cinghiale (jabalí). Siena tiene cocina muy diferente a Florencia.","tip":None,"tags":["🍖 Toscana|tag-food"],"btns":[]},
      {"t":"17:00","hi":False,"title":"Bus de regreso a Florencia","desc":"Hay buses frecuentes hasta las 21:00. Cena en Florencia. Mañana viajan a Roma.","tip":None,"tags":[],"btns":[]},
    ]},
  ]
},
"🏟️ Roma": {
  "meta":"Días 10–13 · 3–6 junio · 4 noches",
  "hotel_nombre":"Hotel Arco del Lauro ★★★ (Trastevere)",
  "hotel_meta":"Zona Trastevere — auténtica y central · B&B familiar · Muy buenas reseñas<br>Alternativa: Hotel Santa Prassede (~€80) o zona Prati (junto al Vaticano)",
  "hotel_precio":"~€80–95 / noche · 4 noches",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2",
  "hotel_airbnb":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2",
  "hotel_maps":"https://maps.google.com/?q=Trastevere+Rome",
  "transporte":("🚄","Firenze SMN → Roma Termini","Frecciarossa (Alta Velocidad) · 1h 30min · Sale cada 30 min · Reservar anticipado","€25–45","https://www.trenitalia.com"),
  "alerta": '<strong>🎾 Padel Nuestro Roma:</strong> La tienda más completa de la ruta. Centro de Roma — mucho más conveniente que la de Milán. Bullpadel, Siux, Babolat, Head, Star Vie. Permiten probar palas antes de comprar. Incorporar en el Día 12.',
  "dias":[
    {"n":"Día 10","date":"Miércoles 3 junio — Vaticano completo","city":"Roma","ev":[
      {"t":"10:30","hi":True,"title":"Museos Vaticanos + Capilla Sixtina","desc":"Los museos más visitados del mundo. 3–4h. El recorrido culmina en la Capilla Sixtina con el fresco de Miguel Ángel (Creación de Adán, Juicio Final). RESERVA OBLIGATORIA con semanas de anticipación.","tip":"⚠️ En la Capilla Sixtina está prohibido fotografiar y hacer ruido — los guardias son estrictos. Silencio absoluto.","tags":["🎨 €17 + €4 reserva|tag-museum"],"btns":[("🎟️ Reservar","https://www.museivaticani.va","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Vatican+Museums+Rome","btn-maps")]},
      {"t":"14:00","hi":False,"title":"Basílica de San Pedro + Cúpula","desc":"La basílica más grande del mundo cristiano. Subir a la cúpula (551 escalones o ascensor parcial €8) para una vista alucinante. La basílica es gratis — la cúpula tiene costo.","tip":None,"tags":["⛪ Gratis · Cúpula €8|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=St+Peters+Basilica+Rome","btn-maps")]},
    ]},
    {"n":"Día 11","date":"Jueves 4 junio — Roma Imperial","city":"Roma","ev":[
      {"t":"08:00","hi":True,"title":"Coliseo + Foro Romano + Palatino","desc":"Combo obligatorio. 3–4h. El Foro Romano es el corazón de la República romana. El Palatino (colina sobre el Foro) tiene las mejores vistas del Coliseo y es el menos visitado del combo — no saltearlo.","tip":None,"tags":["🏛️ €16 + reserva|tag-museum"],"btns":[("🎟️ Reservar","https://www.coopculture.it","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Colosseum+Rome","btn-maps")]},
      {"t":"17:30","hi":False,"title":"Trastevere — paseo y cena","desc":"El barrio medieval más pintoresco de Roma. La Basílica di Santa Maria in Trastevere (siglo XII) es preciosa y gratis. Cena recomendada: Da Enzo al 29.","tip":None,"tags":["🚶 Paseo|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Trastevere+Rome","btn-maps")]},
    ]},
    {"n":"Día 12","date":"Viernes 5 junio — Roma Barroca + Borghese + Pádel","city":"Roma","ev":[
      {"t":"09:00","hi":False,"title":"Pantheon → Piazza Navona → Fontana di Trevi","desc":"El Pantheon (125 d.C.) requiere ticket €5 desde 2023. El óculo deja entrar la lluvia. Trevi: lanzar la moneda de espaldas con la derecha.","tip":None,"tags":["🏛️ Pantheon €5|tag-museum"],"btns":[("📍 Pantheon","https://maps.google.com/?q=Pantheon+Rome","btn-maps"),("📍 Trevi","https://maps.google.com/?q=Trevi+Fountain+Rome","btn-maps")]},
      {"t":"15:00","hi":True,"title":"Galería Borghese — Bernini","desc":"El museo más exclusivo de Roma — solo 360 personas cada 2 horas. Las esculturas de Bernini aquí son lo más impactante de toda Roma: Apolo y Dafne, El rapto de Proserpina.","tip":None,"tags":["🗿 €15 + €2 reserva|tag-museum"],"btns":[("🎟️ Reservar","https://www.galleriaborghese.it","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Galleria+Borghese+Rome","btn-maps")]},
      {"t":"18:00","hi":True,"title":"🎾 Padel Nuestro Roma","desc":"La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Pista interior para probar palas antes de comprar. Mejor opción que la de Milán por ubicación central.","tip":None,"tags":["🎾 Pádel Roma|tag-padel"],"btns":[("📍 Maps","https://maps.google.com/?q=Padel+Nuestro+Roma+Italy","btn-maps"),("Web tienda","https://www.padelnuestro.com","btn-ticket")]},
    ]},
    {"n":"Día 13","date":"Sábado 6 junio — Castel Sant'Angelo + libre","city":"Roma","ev":[
      {"t":"09:00","hi":False,"title":"Castel Sant'Angelo","desc":"Mausoleo de Adriano convertido en fortaleza papal. El \"Passetto\" (corredor secreto al Vaticano) es visible desde afuera. Vista del Tiber y San Pedro desde la cima.","tip":None,"tags":["🏰 €14|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Castel+Sant'Angelo+Rome","btn-maps")]},
      {"t":"14:00","hi":False,"title":"Tarde libre + preparación","desc":"Compras en Via del Corso o zona Spagna. Mañana temprano: tren a Nápoles.","tip":None,"tags":["🛍️ Libre|tag-walk"],"btns":[]},
    ]},
  ]
},
"🍕 Nápoles": {
  "meta":"Día 14 · 7 junio · 1 noche",
  "hotel_nombre":"Hotel Piazza Bellini ★★★ (centro histórico UNESCO)",
  "hotel_meta":"En el corazón de Spaccanapoli · 1 noche (7–8 junio)",
  "hotel_precio":"~€75–90 / noche",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2",
  "hotel_airbnb":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2",
  "hotel_maps":"https://maps.google.com/?q=Piazza+Bellini+Naples",
  "transporte":("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00","€20–35","https://www.trenitalia.com"),
  "alerta": None,
  "dias":[
    {"n":"Día 14","date":"Domingo 7 junio — Pompeya + Nápoles + Pizza","city":"Nápoles","ev":[
      {"t":"09:00","hi":True,"title":"Circumvesuviana → Pompeya Scavi","desc":"Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento. Bajarse en \"Pompei Scavi\". Comprar ticket en máquina automática — evitar vendedores ambulantes.","tip":None,"tags":["🚂 €3 · 40min|tag-train"],"btns":[("📍 Maps","https://maps.google.com/?q=Pompei+Scavi+station","btn-maps")]},
      {"t":"10:00","hi":True,"title":"Pompeya — ciudad sepultada por el Vesubio","desc":"La ciudad romana sepultada en 79 d.C. 3h mínimo. Imprescindible: Casa dei Vettii, Anfiteatro, Thermopolium (bar romano), los moldes humanos en el Granario, el Foro. Llevar agua y sombrero — hace calor y hay poca sombra.","tip":None,"tags":["🌋 €16|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Pompeii+Archaeological+Park","btn-maps")]},
      {"t":"15:00","hi":False,"title":"Spaccanapoli + Museo Arqueológico Nacional","desc":"La calle Spaccanapoli cruza Nápoles histórica. El Museo tiene los mejores objetos de Pompeya y Herculano del mundo — incluyendo la \"Stanza Segreta\" (arte erótico pompeiano).","tip":None,"tags":["🏺 €15|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=National+Archaeological+Museum+Naples","btn-maps")]},
      {"t":"19:30","hi":True,"title":"🍕 La pizza napolitana ORIGINAL","desc":"Nápoles inventó la pizza. Las tres legendarias: L'Antica Pizzeria da Michele (solo Margherita y Marinara, fila larga), Sorbillo (favorita de los napolitanos), Di Matteo (en Spaccanapoli). La margherita original: tomate San Marzano, mozzarella di bufala, albahaca fresca, aceite. Nada más.","tip":None,"tags":["🍕 €5–8|tag-food"],"btns":[("📍 Da Michele","https://maps.google.com/?q=L'Antica+Pizzeria+da+Michele+Naples","btn-maps"),("📍 Sorbillo","https://maps.google.com/?q=Pizzeria+Sorbillo+Naples","btn-maps")]},
    ]},
  ]
},
"🌅 Costa Amalfi": {
  "meta":"Días 15–16 · 8–9 junio · Base: Praiano · 2 noches",
  "hotel_nombre":"Albergo California (Praiano) ★★★",
  "hotel_meta":"Vista al mar · Desayuno incluido · 10 min de Positano en ferry · 2 noches (8–10 junio)",
  "hotel_precio":"~€85–100 / noche",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2",
  "hotel_airbnb":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2",
  "hotel_maps":"https://maps.google.com/?q=Praiano+Amalfi+Coast",
  "transporte":("⛵","Nápoles → Positano (ferry)","SNAV o Alilauro · Desde Molo Beverello · Salidas 08:30 y 09:30 · Solo mayo–oct","~€20/persona","https://www.alilauro.it"),
  "alerta":"<strong>💰 Tip de presupuesto:</strong> Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200 fácilmente. Con ferry desde Praiano se llega a Positano en 10 min.",
  "dias":[
    {"n":"Día 15","date":"Lunes 8 junio — Positano + Amalfi","city":"Costa Amalfi","ev":[
      {"t":"10:30","hi":True,"title":"Positano — las casas en cascada","desc":"El pueblo más fotogénico de la Costa. Las casas de colores en cascada sobre el acantilado. Playa Grande con guijarros (no arena), reposeras ~€20 el par. Agua del Tirreno ~22°C.","tip":None,"tags":["🏖️ Playa|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Positano+Amalfi+Coast","btn-maps")]},
      {"t":"13:00","hi":False,"title":"Almuerzo con vista en Positano","desc":"Muy caro en Positano. Buscar La Zagara (jardín) o Il Ritrovo (más económico, en la colina). Probar: scialatielli ai frutti di mare (pasta fresca con mariscos).","tip":None,"tags":["🦐 Mariscos|tag-food"],"btns":[]},
      {"t":"15:00","hi":True,"title":"Bus SITA → Amalfi ciudad","desc":"El bus azul SITA recorre toda la costa. €2.50 el tramo. Duración 40 min por la carretera más espectacular de Italia. El Duomo de Amalfi (siglo IX, estilo árabe-normando) domina la plaza.","tip":None,"tags":["🚌 €2.50 · Lado derecho|tag-bus"],"btns":[("📍 Maps","https://maps.google.com/?q=Amalfi+Cathedral","btn-maps")]},
      {"t":"19:30","hi":False,"title":"Cena con vista al mar","desc":"El atardecer sobre el Tirreno desde la Costa Amalfi es uno de los espectáculos más bellos de Italia.","tip":None,"tags":["🌅 Scialatielli ai frutti|tag-food"],"btns":[]},
    ]},
    {"n":"Día 16","date":"Martes 9 junio — Ravello + Sentiero degli Dei","city":"Costa Amalfi","ev":[
      {"t":"08:00","hi":True,"title":"Ravello — Villa Cimbrone + Terrazza dell'Infinito","desc":"Ravello está a 350 metros sobre el nivel del mar. La Terraza del Infinito es el mirador más espectacular de toda la Costa. Jardines del siglo XI. Wagner llamó a esta vista \"el balcón más bello del mundo\".","tip":None,"tags":["🌿 €7|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Villa+Cimbrone+Ravello","btn-maps")]},
      {"t":"11:00","hi":True,"title":"Sentiero degli Dei — Camino de los Dioses (7.8km · 3h)","desc":"El sendero más famoso de la Costa Amalfi. Sale desde Bomerano y baja hasta Positano. Vista de toda la costa desde 600m de altura. No necesita guía. Llevar agua, sombrero, calzado firme.","tip":"El trayecto baja (no sube), así que el cansancio es manejable. Es el mejor día del viaje para muchos viajeros.","tags":["🥾 Trekking|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast","btn-maps")]},
      {"t":"15:00","hi":False,"title":"Llegada Positano + playa merecida","desc":"Después del sendero: playa, baño en el mar. Tarde libre. Mañana tren largo a Venecia — preparar maletas.","tip":None,"tags":["🏖️ Playa|tag-walk"],"btns":[]},
    ]},
  ]
},
"🚤 Venecia": {
  "meta":"Día 17 · 10 junio · 1 noche",
  "hotel_nombre":"Hotel Dalla Mora ★★★ (Santa Croce)",
  "hotel_meta":"Zona auténtica · 10 min a pie de la estación · No en Mestre (tierra firme) — en Venecia real<br>Alternativa: B&B en Cannaregio",
  "hotel_precio":"~€90–110 / noche",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2&nflt=di%3D1376",
  "hotel_airbnb":"",
  "hotel_maps":"https://maps.google.com/?q=Hotel+Dalla+Mora+Venice",
  "transporte":("🚄","Nápoles → Venezia Santa Lucia","Frecciarossa directo · 4h50 · Salida 07:30–08:00","€35–60","https://www.trenitalia.com"),
  "alerta":"<strong>Nota Venecia:</strong> Desde junio 2024, Venecia cobra €5 de \"tasa de acceso\" en días pico. Verificar calendario en comune.venezia.it. Airbnb muy regulado en Venecia — hotel es mejor opción.",
  "dias":[
    {"n":"Día 17","date":"Miércoles 10 junio — Venecia completa","city":"Venecia","ev":[
      {"t":"13:00","hi":True,"title":"Gran Canal en Vaporetto línea 1 (la lenta)","desc":"La línea 1 del vaporetto recorre todo el Gran Canal parando en cada estación. 45 minutos de palacios del siglo XIV, puentes, góndolas. El paseo más cinematográfico del viaje. Ticket 24h = €25.","tip":None,"tags":["🚤 24h = €25|tag-boat"],"btns":[]},
      {"t":"15:00","hi":True,"title":"Plaza San Marcos + Basílica + Campanile","desc":"Basílica siglo XI, estilo bizantino, cúpulas doradas — gratuita con espera. El Campanile (99m) ofrece la mejor vista de Venecia. €10.","tip":None,"tags":["🏛️ Gratis + €10 campanile|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=St+Marks+Basilica+Venice","btn-maps")]},
      {"t":"17:00","hi":True,"title":"Perderse sin mapa — la mejor actividad","desc":"Apagar Google Maps. Venecia tiene 118 islas conectadas por 400 puentes. Es imposible no perderse — y eso es exactamente lo que hay que hacer. Los callejones más angostos llevan a los campos (plazas) más secretos.","tip":None,"tags":["🗺️ Sin mapa|tag-walk"],"btns":[]},
      {"t":"19:30","hi":False,"title":"Spritz veneziano en bacaro + Rialto","desc":"El Spritz se inventó en Venecia. Los \"bacari\" son los bares tradicionales con \"cicchetti\" (tapas de €1–2). Zona Cannaregio para los más auténticos.","tip":None,"tags":["🍹 Bacaro|tag-food"],"btns":[("📍 Rialto","https://maps.google.com/?q=Rialto+Bridge+Venice","btn-maps")]},
      {"t":"21:00","hi":False,"title":"Góndola nocturna (opcional)","desc":"Precio fijo oficial: €80 para 30 min (hasta 6 personas). De noche los canales sin turistas son mágicos.","tip":None,"tags":["🎭 €80 / góndola|tag-boat"],"btns":[]},
    ]},
  ]
},
"🇨🇭 Zurich": {
  "meta":"Días 18–20 · 11–13 junio · 3 noches · Vuelo 14/6 a las 08:55",
  "hotel_nombre":"Hotel Otter ★★ (Langstrasse) o IBIS City West",
  "hotel_meta":"Zona cool y multicultural · A pie del casco histórico · 3 noches (11–14 junio)<br>Alternativa con vista: Hotel Limmatblick (~€120, sobre el río Limmat)",
  "hotel_precio":"~€90–110 / noche · 3 noches",
  "hotel_booking":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
  "hotel_airbnb":"",
  "hotel_maps":"https://maps.google.com/?q=Langstrasse+Zurich",
  "transporte":("🚄","Venezia S. Lucia → Zurich HB (a través de los Alpes)","EuroCity directo · 4h45 · Paisaje alpino impresionante · Sentarse del lado derecho mirando norte","€40–60","https://www.sbb.ch"),
  "alerta":"<strong>⚠️ Vuelo el 14/6 a las 08:55:</strong> Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min. El día 13 preparar todo y dormir temprano.",
  "dias":[
    {"n":"Día 18","date":"Jueves 11 junio — Llegada + Altstadt","city":"Zurich","ev":[
      {"t":"14:00","hi":False,"title":"Bahnhofstrasse + Lago de Zurich","desc":"La calle comercial más cara del mundo. Joyerías, Rolex, bancos. El Lago de Zurich al final para sentarse. Cambio mental: de caos italiano a precisión suiza.","tip":None,"tags":["⌚ Paseo|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Bahnhofstrasse+Zurich","btn-maps")]},
      {"t":"15:30","hi":True,"title":"Grossmünster + Altstadt","desc":"La iglesia donde Zwinglio inició la Reforma Protestante en 1519. Subir las torres (€5) para la vista de Zurich. El barrio medieval Niederdorf adyacente: callejuelas adoquinadas, gremios medievales, cafés.","tip":None,"tags":["⛪ Torres €5|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Grossmunster+Zurich","btn-maps")]},
      {"t":"18:00","hi":False,"title":"Fraumünster — vitrales de Chagall (1970)","desc":"5 vitrales de Marc Chagall en un edificio del siglo XIII. Tesoro de arte moderno en arquitectura medieval. €5.","tip":None,"tags":["🎨 €5|tag-museum"],"btns":[("📍 Maps","https://maps.google.com/?q=Fraumunster+Zurich","btn-maps")]},
    ]},
    {"n":"Día 19","date":"Viernes 12 junio — Lago + ETH + Fondue","city":"Zurich","ev":[
      {"t":"09:00","hi":True,"title":"Crucero Lago de Zurich","desc":"ZSG opera cruceros. Recorrido corto 1h o largo 4h hasta Rapperswil. El lago con los Alpes de fondo es icónico.","tip":None,"tags":["⛵ €8–30|tag-boat"],"btns":[("ZSG","https://www.zsg.ch","btn-ticket"),("📍 Maps","https://maps.google.com/?q=Lake+Zurich+boat+tours","btn-maps")]},
      {"t":"16:00","hi":False,"title":"Polybahn → terraza ETH (vista gratis)","desc":"El funicular universitario de 1889 sube hasta la ETH (la universidad de Einstein). Vista panorámica de Zurich, el lago y los Alpes desde la terraza — gratis.","tip":None,"tags":["🔭 Gratis|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=ETH+Zurich+terrace","btn-maps")]},
      {"t":"20:00","hi":True,"title":"Fondue suiza — Swiss Chuchi","desc":"La fondue de queso es el plato nacional suizo. Swiss Chuchi en el Altstadt. Experiencia completa ~€35–45/persona.","tip":None,"tags":["🧀 Fondue|tag-food"],"btns":[("📍 Swiss Chuchi","https://maps.google.com/?q=Swiss+Chuchi+Zurich","btn-maps")]},
    ]},
    {"n":"Día 20","date":"Sábado 13 junio — Uetliberg + Chocolates + Última noche","city":"Zurich","ev":[
      {"t":"09:00","hi":False,"title":"Uetliberg — la montaña de Zurich","desc":"La montaña de Zurich — 870m. Tren S10 desde HB, 20 min, €5. Vista de Zurich, el lago y los Alpes.","tip":None,"tags":["⛰️ €5 tren|tag-walk"],"btns":[("📍 Maps","https://maps.google.com/?q=Uetliberg+Zurich","btn-maps")]},
      {"t":"13:00","hi":True,"title":"Chocolates Sprüngli + Mercado Bürkliplatz","desc":"Sprüngli (desde 1836) — los mejores truffes du jour de Zurich. El mercado de Bürkliplatz los sábados tiene artesanías locales.","tip":None,"tags":["🍫 Chocolates|tag-food"],"btns":[("📍 Sprüngli","https://maps.google.com/?q=Confiserie+Sprungli+Zurich","btn-maps")]},
      {"t":"19:00","hi":True,"title":"Última cena del viaje 🥂","desc":"Elegir el restaurante favorito de los días en Zurich. Brindar por el viaje. Hacer check-in online del vuelo LA8799.","tip":None,"tags":["🥂 Despedida|tag-food"],"btns":[]},
      {"t":"22:00","hi":False,"title":"A dormir — vuelo 08:55 mañana","desc":"Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración. Estar en aeropuerto a las 07:00.","tip":"⚠️ ALARMA 06:00. Sin excepciones.","tags":["✈️ Alarma 06:00|tag-sleep"],"btns":[]},
    ]},
  ]
},
}

RESERVAS_DEF = [
    {"id":"r01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_book":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
    {"id":"r02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_book":"https://www.galleriaborghese.it","url_maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
    {"id":"r03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_book":"https://www.museivaticani.va","url_maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
    {"id":"r04","title":"Cúpula Brunelleschi — Duomo Florencia","city":"Florencia","fecha":"30 mayo","urgente":True,"url_book":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.google.com/?q=Duomo+Florence"},
    {"id":"r05","title":"David — Accademia Florencia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_book":"https://www.uffizi.it/en/the-accademia-gallery","url_maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
    {"id":"r06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
    {"id":"r07","title":"Coliseo + Foro Romano + Palatino","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url_book":"https://www.coopculture.it","url_maps":"https://maps.google.com/?q=Colosseum+Rome"},
    {"id":"r08","title":"Alojamiento Milán — 3 noches","city":"Milán","fecha":"25–28 mayo","urgente":False,"url_book":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2","url_maps":"https://maps.google.com/?q=Milan+Italy"},
    {"id":"r09","title":"Alojamiento La Spezia — 2 noches","city":"Cinque Terre","fecha":"28–30 mayo","urgente":False,"url_book":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2","url_maps":"https://maps.google.com/?q=La+Spezia+Italy"},
    {"id":"r10","title":"Alojamiento Florencia — 4 noches","city":"Florencia","fecha":"30 mayo–3 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2","url_maps":"https://maps.google.com/?q=Florence+Italy"},
    {"id":"r11","title":"Alojamiento Roma — 4 noches","city":"Roma","fecha":"3–7 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2","url_maps":"https://maps.google.com/?q=Trastevere+Rome"},
    {"id":"r12","title":"Alojamiento Nápoles — 1 noche","city":"Nápoles","fecha":"7–8 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2","url_maps":"https://maps.google.com/?q=Naples+Italy"},
    {"id":"r13","title":"Alojamiento Praiano/Amalfi — 2 noches","city":"Amalfi","fecha":"8–10 junio","urgente":False,"url_book":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2","url_maps":"https://maps.google.com/?q=Praiano+Italy"},
    {"id":"r14","title":"Alojamiento Venecia — 1 noche","city":"Venecia","fecha":"10–11 junio","urgente":False,"url_book":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","url_maps":"https://maps.google.com/?q=Venice+Italy"},
    {"id":"r15","title":"Alojamiento Zurich — 3 noches","city":"Zurich","fecha":"11–14 junio","urgente":False,"url_book":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","url_maps":"https://maps.google.com/?q=Zurich+Switzerland"},
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · 52 min · cada 30 min","€13/p","https://www.trenord.it"),
    ("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10","€25–35","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · Incluido en Cinque Terre Card (€29.50/2 días)","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Firenze SMN","Intercity · ~2h · Salida 08:30","€15–20","https://www.trenitalia.com"),
    ("🚌","Firenze ↔ Siena","Bus SENA · 1h30 · desde Autostazione frente a SMN","€9","https://www.tiemmespa.it"),
    ("🚄","Firenze → Roma Termini","Frecciarossa · 1h30 · cada 30 min","€25–45","https://www.trenitalia.com"),
    ("🚄","Roma → Napoli Centrale","Frecciarossa · 1h10 · desde las 06:00","€20–35","https://www.trenitalia.com"),
    ("🚂","Napoli → Pompei Scavi","Circumvesuviana · 40 min · andén subterráneo -1","€3/p","https://www.eavsrl.it"),
    ("⛵","Napoli → Positano (ferry)","SNAV/Alilauro · Molo Beverello · 65 min · solo mayo–oct","€20/p","https://www.alilauro.it"),
    ("🚌","Bus SITA Costa Amalfi","Positano ↔ Amalfi ↔ Ravello · ticket en tabacchi antes de subir","€2.50/tramo","https://www.sitasudtrasporti.it"),
    ("🚄","Napoli → Venezia S. Lucia","Frecciarossa directo · 4h50 · salida 07:30","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia 24h","Línea 1 = Gran Canal completo · Línea 2 = rápida","€25","https://actv.avmspa.it"),
    ("🚄","Venezia → Zurich HB (Alpes)","EuroCity directo · 4h45 · Sentarse lado derecho","€40–60","https://www.sbb.ch"),
    ("🚄","Zurich HB → Aeropuerto ZRH","SBB · 10 min · sale cada 10 min","€4","https://www.sbb.ch"),
]

TIPS = [
    ("☕","Café en la barra","Parado = €1.20. Sentado en mesa = €3–5. La ley exige mostrar ambos precios en la carta."),
    ("💧","Agua del grifo","Pedir 'acqua del rubinetto' — gratis. El agua mineral en mesa = €3–5."),
    ("🍽️","Menú del giorno","Primer + segundo + bebida + pan = €12–15. Solo almuerzo. La cena siempre es más cara."),
    ("💳","Revolut / Wise","Sin comisiones de cambio. En Suiza cambiar a CHF francos. 1 CHF ≈ €1.05."),
    ("👟","Zapatos (fundamental)","10–15 km/día en adoquines. Amalfi y Cinque Terre: suela firme. Zapatillas de running funcionan."),
    ("🕌","Ropa para iglesias","Hombros y rodillas cubiertos. Llevar una bufanda liviana — sirve para los dos."),
    ("🚌","Bus SITA Amalfi","Comprar ticket en tabacchi ANTES de subir. Sentarse del lado DERECHO mirando al mar."),
    ("🍦","Gelato auténtico","Colores apagados, tapado con espátula, no en montañas brillantes = artesanal. Si es fluo = industrial."),
    ("📱","Apps esenciales","Trenitalia · Italo · Maps.me offline · TheFork · SBB (Suiza) · Revolut para pagos."),
    ("🎾","Pádel Nuestro Roma","Día 12 tarde. Bullpadel, Siux, Babolat, Head. Pista interior para probar palas. Centro de Roma."),
    ("🛍️","Ropa barata — Milán","Corso Buenos Aires. 2km de tiendas. Zara, H&M, Bershka, marcas italianas."),
    ("🧀","Fondue — Zurich","Swiss Chuchi (Altstadt) ~€40/persona. Sprüngli desde 1836 para chocolates."),
]

PRESUPUESTO_FILAS = [
    ("Milán","3","€80","€240","https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2","https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2"),
    ("La Spezia","2","€75","€150","https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2","https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2"),
    ("Florencia","4","€100","€400","https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2","https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2"),
    ("Roma","4","€88","€350","https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2","https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2"),
    ("Nápoles","1","€80","€80","https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2","https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2"),
    ("Costa Amalfi","2","€92","€185","https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2","https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2"),
    ("Venecia","1","€100","€100","https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","—"),
    ("Zurich","3","€100","€300","https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","—"),
    ("TOTAL","20","~€95","~€1.805","",""),
]

# ─── CARGAR DATOS ─────────────────────────────────────────────────────────────
try:
    df_res=load_reservas(); df_gas=load_gastos(); df_notas=load_notas(); sheets_ok=True
except:
    df_res=df_gas=df_notas=pd.DataFrame(); sheets_ok=False

def get_rd(rid):
    if df_res.empty or "id" not in df_res.columns: return {}
    row=df_res[df_res["id"]==rid]
    return row.iloc[0].to_dict() if not row.empty else {}

def render_ev(ev):
    tags_html="".join(f'<span class="tag {t.split("|")[1]}">{t.split("|")[0]}</span>' for t in ev.get("tags",[]) if "|" in t)
    btns_html="".join(f'<a href="{u}" target="_blank" class="btn {c}">{l}</a>' for l,u,c in ev.get("btns",[]))
    tip_html=f'<div class="t-tip">{ev["tip"]}</div>' if ev.get("tip") else ""
    dc="hi" if ev["hi"] else ""
    sc="star" if ev["hi"] else ""
    return f"""
    <div class="t-row">
      <div class="t-time">{ev['t']}</div>
      <div class="t-dot {dc}"></div>
      <div>
        <div class="t-title {sc}">{ev['title']}</div>
        <div class="t-desc">{ev['desc']}</div>
        {tip_html}
        <div class="t-actions">{tags_html}{btns_html}</div>
      </div>
    </div>"""

# ─── HERO ─────────────────────────────────────────────────────────────────────
ok_count=sum(1 for r in RESERVAS_DEF if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
total_gas=pd.to_numeric(df_gas["monto"],errors="coerce").fillna(0).sum() if not df_gas.empty and "monto" in df_gas.columns else 0

st.markdown(f"""
<div class="hero"><div class="hero-inner">
  <div class="hero-flag">🇮🇹 🇨🇭</div>
  <div class="hero-title">Italia & <em>Zurich</em></div>
  <div class="hero-sub">Luna de Miel · Mayo–Junio 2026 · Compartido en tiempo real</div>
  <div class="hero-dates"><span>✈ Sale 24 mayo · IGU</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
</div></div>
<div class="stats-bar">
  <div class="stat-item"><span class="stat-num">{ok_count}/{len(RESERVAS_DEF)}</span><span class="stat-lbl">Reservas ok</span></div>
  <div class="stat-item"><span class="stat-num">€{total_gas:,.0f}</span><span class="stat-lbl">Gastado</span></div>
  <div class="stat-item"><span class="stat-num">20</span><span class="stat-lbl">Días totales</span></div>
  <div class="stat-item"><span class="stat-num">9</span><span class="stat-lbl">Ciudades</span></div>
  <div class="stat-item"><span class="stat-num">17</span><span class="stat-lbl">En Italia</span></div>
  <div class="stat-item"><span class="stat-num">3</span><span class="stat-lbl">En Zurich</span></div>
</div>
""", unsafe_allow_html=True)

if sheets_ok:
    st.markdown('<span class="sync-ok">🟢 Google Sheets conectado — ambos ven los mismos datos en tiempo real</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="sync-err">🔴 Sin conexión a Sheets — verificar credenciales</span>', unsafe_allow_html=True)

st.write("")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_vue,tab_itin,tab_res_t,tab_trans,tab_gas_t,tab_pres,tab_tips,tab_notas_t = st.tabs([
    "✈️ Vuelos","🗺️ Itinerario","🎟️ Reservas","🚄 Transportes",
    "💰 Gastos","📊 Presupuesto","💡 Tips","📝 Notas"
])

# ══ VUELOS ════════════════════════════════════════════════════════════════════
with tab_vue:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Vuelos confirmados</div><div class="sec-meta">Itinerario LATAM + Swiss · Foz de Iguazú ↔ Zurich</div></div>', unsafe_allow_html=True)
    st.markdown("""
<div class="card">
  <div class="card-header"><span class="day-badge">IDA</span><span class="card-date">Domingo 24 mayo 2026 — Foz de Iguazú → Milán</span></div>
  <div class="timeline">
    <div class="t-row"><div class="t-time">14:50</div><div class="t-dot hi"></div><div><div class="t-title star">IGU → São Paulo GRU</div><div class="t-desc">LA3879 op. LATAM Brasil · Airbus 320 · 1h 40min</div><div class="t-actions"><span class="tag tag-train">✈ LA3879 · A320</span></div></div></div>
    <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">16:30</div><div class="t-dot"></div><div><div class="t-title">Escala São Paulo Guarulhos (GRU)</div><div class="t-desc">Cambio de avión · 1h 30min de conexión · Considerar el traslado si aplica</div></div></div>
    <div class="t-row"><div class="t-time">18:00</div><div class="t-dot hi"></div><div><div class="t-title star">São Paulo GRU → Milán Malpensa MXP</div><div class="t-desc">LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día</div><div class="t-actions"><span class="tag tag-train">✈ LA8072 · B777</span></div></div></div>
  </div>
</div>
<div class="card">
  <div class="card-header"><span class="day-badge">VUELTA</span><span class="card-date">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>
  <div class="timeline">
    <div class="t-row"><div class="t-time">08:55</div><div class="t-dot hi"></div><div><div class="t-title star">Zurich ZRH → Milán Malpensa MXP</div><div class="t-desc">LA8799 op. Swiss · Avión 221 · 55min · Salir al aeropuerto a las 07:00</div><div class="t-tip">⚠️ Tren Zurich HB → ZRH: 10 min, sale cada 10 min. Alarma 06:00 hs.</div></div></div>
    <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">09:50</div><div class="t-dot"></div><div><div class="t-title">Escala Milán Malpensa (MXP)</div><div class="t-desc">Cambio de avión · 3h 10min de conexión · Considerar el traslado si aplica</div></div></div>
    <div class="t-row"><div class="t-time">13:00</div><div class="t-dot hi"></div><div><div class="t-title star">Milán MXP → São Paulo GRU</div><div class="t-desc">LA8073 op. LATAM Brasil · Boeing 773 · 12h</div><div class="t-actions"><span class="tag tag-train">✈ LA8073 · B777</span></div></div></div>
    <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">20:00</div><div class="t-dot"></div><div><div class="t-title">Escala São Paulo Guarulhos (GRU)</div><div class="t-desc">Cambio de avión · 2h 20min de conexión</div></div></div>
    <div class="t-row"><div class="t-time">22:20</div><div class="t-dot hi"></div><div><div class="t-title star">São Paulo GRU → Foz de Iguazú IGU</div><div class="t-desc">LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día</div><div class="t-actions"><span class="tag tag-train">✈ LA3206 · A321</span></div></div></div>
  </div>
</div>
<div class="alert"><strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno. Primer día: siesta obligatoria 2–3h, almuerzo tranquilo y paseo suave al atardecer por Navigli. No planificar actividades intensas.</div>
""", unsafe_allow_html=True)

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("Ciudad", list(ITIN.keys()), horizontal=True, label_visibility="collapsed")
    d = ITIN[ciudad_sel]

    st.markdown(f'<div class="sec-hdr" style="margin-top:1rem"><div class="sec-title">{ciudad_sel}</div><div class="sec-meta">{d["meta"]}</div></div>', unsafe_allow_html=True)

    # Alerta ciudad
    if d.get("alerta"):
        st.markdown(f'<div class="alert">{d["alerta"]}</div>', unsafe_allow_html=True)

    # Hotel con TODA la información del HTML
    bb = f'<a href="{d["hotel_booking"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if d["hotel_booking"] else ""
    ba = f'<a href="{d["hotel_airbnb"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if d["hotel_airbnb"] else ""
    bm = f'<a href="{d["hotel_maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if d["hotel_maps"] else ""
    st.markdown(f"""
    <div class="hotel-card">
      <div class="hotel-name">{d["hotel_nombre"]}</div>
      <div class="hotel-meta">{d["hotel_meta"]}</div>
      <div class="hotel-price">{d["hotel_precio"]}</div>
      <div class="hotel-actions">{bb}{ba}{bm}</div>
    </div>
    """, unsafe_allow_html=True)

    # Transporte hacia esta ciudad
    if d.get("transporte"):
        icon, route, detail, price, url = d["transporte"]
        st.markdown(f'<div class="tc"><div class="tc-icon">{icon}</div><div style="flex:1"><div class="tc-route">{route}</div><div class="tc-detail">{detail}</div></div><div class="tc-price">{price}</div><a href="{url}" target="_blank" class="btn btn-tren">🔗 Comprar</a></div>', unsafe_allow_html=True)

    # Días con TODO el contenido del HTML
    for day in d["dias"]:
        ev_html = "".join(render_ev(e) for e in day["ev"])
        st.markdown(f"""
        <div class="card">
          <div class="card-header">
            <span class="day-badge">{day['n']}</span>
            <span class="card-date">{day['date']}</span>
            <span class="card-city">{day['city']}</span>
          </div>
          <div class="timeline">{ev_html}</div>
        </div>
        """, unsafe_allow_html=True)

# ══ RESERVAS ══════════════════════════════════════════════════════════════════
with tab_res_t:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Tracker de Reservas</div><div class="sec-meta">Cargá la URL de lo que reservaste (Airbnb o Booking) — tu pareja lo ve al instante</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>⚠️ Urgente:</strong> La Última Cena, Galería Borghese y Museos Vaticanos se agotan meses antes. Gestionar primero.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-blue"><strong>💡 Cómo usar:</strong> Cuando reserves en Airbnb o Booking, pegá la URL de la reserva confirmada en el campo correspondiente y guardá. Tu pareja verá la URL, el número de confirmación y el monto al instante desde su teléfono.</div>', unsafe_allow_html=True)

    filtro = st.selectbox("Filtrar por ciudad",["Todas"]+list(dict.fromkeys(r["city"] for r in RESERVAS_DEF)))

    for r in RESERVAS_DEF:
        if filtro!="Todas" and r["city"]!=filtro: continue
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        cc="res-urg" if r["urgente"] else "res-ok"
        bl={"pending":"b-pending","confirmed":"b-confirmed","paid":"b-paid"}.get(ea,"b-pending")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva",""))
        tipo_saved=str(rd.get("tipo_aloj","Airbnb / Booking"))
        uh=f'<a href="{us}" target="_blank" class="url-saved">🔗 URL guardada: {us[:80]}{"..." if len(us)>80 else ""}</a>' if us else ""
        st.markdown(f"""
        <div class="res-card {cc}">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px">
            <span style="font-size:0.72rem;padding:2px 8px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span>
            <span class="res-title">{"⚠️ " if r["urgente"] else ""}{r["title"]}</span>
            <span class="{bl}">{ll}</span>
          </div>
          <div class="res-meta">📅 {r["fecha"]}</div>
          {uh}
        </div>
        """, unsafe_allow_html=True)

        with st.form(key=f"f_{r['id']}"):
            c1,c2 = st.columns([2,1])
            with c1:
                ne=st.selectbox("Estado",["pending","confirmed","paid"],
                    index=["pending","confirmed","paid"].index(ea),
                    format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],
                    key=f"s_{r['id']}")
            with c2:
                tipo=st.selectbox("Tipo alojamiento",["Airbnb","Booking.com","Directo / Otro"],
                    index=["Airbnb","Booking.com","Directo / Otro"].index(tipo_saved) if tipo_saved in ["Airbnb","Booking.com","Directo / Otro"] else 0,
                    key=f"tipo_{r['id']}")

            nu=st.text_input(
                "🔗 URL de la reserva confirmada (Airbnb, Booking o sitio del hotel)",
                value=us, key=f"u_{r['id']}",
                placeholder="Ej: https://www.airbnb.com/trips/v1/XXXXXXX  o  https://www.booking.com/hotel/..."
            )
            c3,c4=st.columns(2)
            with c3: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","")),key=f"c_{r['id']}",placeholder="ej. HB-123456789")
            with c4: nm=st.number_input("Monto pagado €",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"m_{r['id']}")
            nn=st.text_area("Notas internas",value=str(rd.get("notas_int","")),key=f"n_{r['id']}",height=55,placeholder="Ej: Check-in 15hs · Pedir habitación alta · Desayuno incluido...")

            cs,cb,cm=st.columns([2,1,1])
            with cs: sub=st.form_submit_button("💾 Guardar — tu pareja lo ve al instante",use_container_width=True)
            with cb: st.markdown(f'<a href="{r["url_book"]}" target="_blank" class="btn btn-ticket">🔗 Ir a buscar</a>',unsafe_allow_html=True)
            with cm: st.markdown(f'<a href="{r["url_maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>',unsafe_allow_html=True)

            if sub:
                if save_reserva(r["id"],ne,tipo,nu,nc,nm,nn):
                    st.success(f"✅ Guardado como {tipo} — tu pareja ya lo puede ver"); st.rerun()
        st.write("")

# ══ TRANSPORTES ═══════════════════════════════════════════════════════════════
with tab_trans:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Todos los transportes</div><div class="sec-meta">En orden cronológico · Con links de compra</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-green"><strong>💡 Truco:</strong> Comprar trenes con 60 días de anticipación puede ser 4x más barato. Frecciarossa Roma→Nápoles: <strong>€9 anticipado</strong> vs €55 último momento.</div>', unsafe_allow_html=True)
    for icon,route,detail,price,url in TRANSPORTES:
        st.markdown(f'<div class="tc"><div class="tc-icon">{icon}</div><div style="flex:1"><div class="tc-route">{route}</div><div class="tc-detail">{detail}</div></div><div class="tc-price">{price}</div><a href="{url}" target="_blank" class="btn btn-tren">🔗 Comprar</a></div>', unsafe_allow_html=True)

# ══ GASTOS ════════════════════════════════════════════════════════════════════
with tab_gas_t:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Tracker de Gastos</div><div class="sec-meta">Cargá cada gasto — ambos lo ven en tiempo real</div></div>', unsafe_allow_html=True)
    PRES=4350.0
    cats={"Alojamiento":0,"Transporte":0,"Entradas":0,"Comidas":0,"Otros":0}
    if not df_gas.empty and "monto" in df_gas.columns and "categoria" in df_gas.columns:
        for _,row in df_gas.iterrows():
            try: cats[row.get("categoria","Otros")]=cats.get(row.get("categoria","Otros"),0)+float(row["monto"])
            except: pass
    total_g=sum(cats.values()); pct=min(100,int(total_g/PRES*100))
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("💶 Total",f"€{total_g:,.0f}",f"{pct}% del presupuesto")
    c2.metric("🏨 Alojamiento",f"€{cats['Alojamiento']:,.0f}")
    c3.metric("🚄 Transporte",f"€{cats['Transporte']:,.0f}")
    c4.metric("🎟️ Entradas",f"€{cats['Entradas']:,.0f}")
    c5.metric("🍽️ Comidas",f"€{cats['Comidas']:,.0f}")
    st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct}%"></div></div><div style="font-size:0.75rem;color:#6B7A8D;margin-top:4px;font-weight:500">€{total_g:,.0f} gastados de €{PRES:,.0f} presupuestados ({pct}%)</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("fg"):
        cd,cc_sel,cm=st.columns([3,2,1])
        with cd: gd=st.text_input("Descripción",placeholder="ej. Airbnb Florencia 4 noches")
        with cc_sel: gc=st.selectbox("Categoría",["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        with cm: gm=st.number_input("€",min_value=0.0,step=1.0)
        if st.form_submit_button("➕ Agregar gasto",use_container_width=True):
            if gd.strip() and gm>0:
                if add_gasto(gd.strip(),gc,gm): st.success("Gasto agregado ✓"); st.rerun()
            else: st.warning("Completá descripción y monto")
    if not df_gas.empty and "descripcion" in df_gas.columns:
        st.write("")
        st.markdown("**Historial**")
        df_show=df_gas[["id","descripcion","categoria","monto","fecha"]].copy()
        df_show["monto"]=pd.to_numeric(df_show["monto"],errors="coerce").map("€{:,.0f}".format)
        st.dataframe(df_show.drop("id",axis=1),use_container_width=True,hide_index=True)
        di=st.text_input("ID de gasto a eliminar",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar") and di:
            if del_gasto(di.strip()): st.success("Eliminado ✓"); st.rerun()
    else: st.info("Aún no hay gastos. ¡Agregá el primero!")

# ══ PRESUPUESTO ═══════════════════════════════════════════════════════════════
with tab_pres:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Presupuesto estimado</div><div class="sec-meta">Para 2 personas · 20 días · Sin vuelos</div></div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🏨 Alojamiento (20 noches)","~€1.805","Promedio €90/noche")
    c2.metric("🚄 Transportes internos","~€500","Trenes + ferries + buses")
    c3.metric("🎟️ Entradas museos","~€350","Para 2 personas")
    c4.metric("🍽️ Comidas (~€60/día)","~€1.200","Desayuno + almuerzo + cena")
    st.write("")
    c5,c6=st.columns(2)
    c5.metric("🛍️ Imprevistos / extras","~€400","Compras, pádel, chocolates, etc.")
    c6.metric("💶 TOTAL ESTIMADO","~€4.350","Para 2 personas sin vuelos")
    st.write("")
    rows=""
    for ciudad,noches,precio,total,ub,ua in PRESUPUESTO_FILAS:
        es_tot=ciudad=="TOTAL"
        cls='class="tot"' if es_tot else ""
        btn_b=f'<a href="{ub}" target="_blank" class="btn btn-booking" style="padding:2px 7px;font-size:0.68rem">Book</a>' if ub and ub!="—" else "—"
        btn_a=f'<a href="{ua}" target="_blank" class="btn btn-airbnb" style="padding:2px 7px;font-size:0.68rem">Airbnb</a>' if ua and ua!="—" else "—"
        rows+=f"<tr {cls}><td>{ciudad}</td><td style='text-align:center'>{noches}</td><td style='text-align:center'>{precio}</td><td style='text-align:center;font-weight:700'>{total}</td><td style='text-align:center'>{btn_b}</td><td style='text-align:center'>{btn_a}</td></tr>"
    st.markdown(f'<div class="card" style="padding:0"><table class="budget-table"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th><th style="text-align:center">€/noche</th><th style="text-align:center">Total</th><th style="text-align:center">Booking</th><th style="text-align:center">Airbnb</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

# ══ TIPS ══════════════════════════════════════════════════════════════════════
with tab_tips:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Tips esenciales</div><div class="sec-meta">Lo que marca la diferencia entre turista y viajero</div></div>', unsafe_allow_html=True)
    cols=st.columns(3)
    for i,(icon,title,text) in enumerate(TIPS):
        with cols[i%3]:
            st.markdown(f'<div class="tip-card"><div class="tip-icon">{icon}</div><div class="tip-title">{title}</div><div class="tip-text">{text}</div></div>', unsafe_allow_html=True)
            st.write("")

# ══ NOTAS ═════════════════════════════════════════════════════════════════════
with tab_notas_t:
    st.markdown('<div class="sec-hdr"><div class="sec-title">Notas compartidas</div><div class="sec-meta">Cualquiera puede publicar — el otro lo ve al instante</div></div>', unsafe_allow_html=True)
    with st.form("fn"):
        nt=st.text_area("Nueva nota",height=90,placeholder="Escribí algo — tu pareja lo ve al instante...")
        ct,ca=st.columns(2)
        with ct: ntag=st.selectbox("Categoría",["💡 Idea","⚠️ Importante","🍽️ Restaurante","🏨 Hotel","🎾 Pádel","🛍️ Compras","📝 General"])
        with ca: naut=st.selectbox("Quién escribe",["Adilson","Esposa"])
        if st.form_submit_button("📤 Publicar nota",use_container_width=True):
            if nt.strip():
                if add_nota(nt.strip(),ntag,naut): st.success("Publicado ✓"); st.rerun()
            else: st.warning("Escribí algo primero")
    st.write("")
    if not df_notas.empty and "texto" in df_notas.columns:
        for _,row in df_notas.iloc[::-1].iterrows():
            st.markdown(f'<div class="nota-card"><strong>{row.get("tag","📝")}</strong> · <em style="color:#6B7A8D">{row.get("autor","")}</em><br><span style="color:#1A1A2E">{row.get("texto","")}</span><div class="nota-meta">🕐 {row.get("fecha","")}</div></div>', unsafe_allow_html=True)
            if st.button("🗑️ Borrar",key=f"dn_{row.get('id','')}"):
                if del_nota(str(row.get("id",""))): st.rerun()
    else: st.info("Aún no hay notas. ¡Publicá la primera!")
