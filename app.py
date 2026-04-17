import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Italia & Zurich 2026 🇮🇹",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS MODO CLARO COMPLETO ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --cream:#F7F3EE; --parchment:#EDE7DC; --terracotta:#C4693A;
    --terracotta-light:#E8956D; --terracotta-dark:#8B3E1E;
    --olive:#6B7A3E; --olive-light:#9AAD5A;
    --slate:#3D4A5C; --slate-light:#6B7A8D;
    --gold:#C9A84C; --gold-light:#E8C96A;
    --ink:#1A1A2E; --white:#FFFFFF;
}

/* FONDO Y TEXTO BASE */
.stApp { background-color: var(--cream) !important; }
.stApp, .stApp p, .stApp div, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp li {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--ink) !important;
}

/* OCULTAR ELEMENTOS STREAMLIT */
#MainMenu, footer, header, [data-testid="stDecoration"],
[data-testid="collapsedControl"] { visibility:hidden !important; display:none !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap:6px; background:var(--parchment);
    padding:8px 10px; border-radius:12px; margin-bottom:1.5rem;
}
.stTabs [data-baseweb="tab"] {
    padding:8px 18px; border-radius:8px;
    background:rgba(255,255,255,0.5); border:none !important;
}
.stTabs [data-baseweb="tab"] p {
    color:var(--slate) !important; font-weight:600 !important; font-size:0.88rem !important;
}
.stTabs [aria-selected="true"] { background:var(--white) !important; box-shadow:0 2px 6px rgba(0,0,0,0.08) !important; }
.stTabs [aria-selected="true"] p { color:var(--terracotta-dark) !important; }
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }
.stTabs [data-baseweb="tab-border"] { display:none !important; }

/* RADIO */
div[data-testid="stRadio"] > div {
    flex-direction:row !important; flex-wrap:wrap !important; gap:8px !important;
    background:var(--white) !important; padding:12px !important;
    border-radius:12px !important; border:1px solid var(--parchment) !important;
}
div[data-testid="stRadio"] > div > label {
    background-color:var(--parchment) !important; padding:8px 16px !important;
    border-radius:20px !important; cursor:pointer !important; border:1.5px solid transparent !important;
}
div[data-testid="stRadio"] > div > label p {
    color:var(--ink) !important; font-weight:600 !important; font-size:0.85rem !important; margin:0 !important;
}
div[data-testid="stRadio"] > div > label[data-checked="true"] {
    background-color:var(--terracotta) !important; border-color:var(--terracotta-dark) !important;
}
div[data-testid="stRadio"] > div > label[data-checked="true"] p { color:var(--white) !important; }
div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display:none !important; }

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background-color:var(--white) !important; color:var(--ink) !important;
    border:1px solid var(--parchment) !important; border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color:var(--terracotta-light) !important;
    box-shadow:0 0 0 2px rgba(196,105,58,0.15) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label { color:var(--slate) !important; font-size:0.82rem !important; font-weight:500 !important; }
.stSelectbox > div > div { background:var(--white) !important; color:var(--ink) !important; border:1px solid var(--parchment) !important; }
[data-baseweb="select"] { background:var(--white) !important; }
[data-baseweb="select"] * { color:var(--ink) !important; background:var(--white) !important; }

/* BOTONES */
.stButton > button {
    background:var(--terracotta) !important; color:var(--white) !important;
    border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-family:'DM Sans',sans-serif !important;
    padding:8px 20px !important;
}
.stButton > button:hover { background:var(--terracotta-dark) !important; }

/* MÉTRICAS */
[data-testid="stMetric"] {
    background:var(--white); border:1px solid var(--parchment);
    border-radius:10px; padding:1rem !important;
}
[data-testid="stMetricLabel"] p { color:var(--slate-light) !important; font-size:0.78rem !important; }
[data-testid="stMetricValue"] { color:var(--terracotta-dark) !important; font-family:'Playfair Display',serif !important; }
[data-testid="stMetricDelta"] { color:var(--olive) !important; }

/* EXPANDER */
[data-testid="stExpander"] {
    border:1px solid var(--parchment) !important; border-radius:10px !important;
    background:var(--white) !important; margin-bottom:6px !important;
}
[data-testid="stExpander"] summary p { color:var(--ink) !important; font-weight:600 !important; }

/* DATAFRAME */
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }

/* ═══ COMPONENTES HTML CUSTOM ═══ */

.hero {
    background:linear-gradient(135deg,#3D4A5C 0%,#1A1A2E 100%);
    border-radius:16px 16px 0 0; padding:2.5rem 2rem 2rem; text-align:center;
    position:relative; overflow:hidden;
}
.hero::before {
    content:''; position:absolute; inset:0;
    background:radial-gradient(ellipse at 30% 50%,rgba(196,105,58,0.2) 0%,transparent 60%),
               radial-gradient(ellipse at 70% 30%,rgba(201,168,76,0.12) 0%,transparent 50%);
}
.hero-inner { position:relative; z-index:1; }
.hero-flag { font-size:1.8rem; letter-spacing:8px; margin-bottom:6px; }
.hero-title { font-family:'Playfair Display',serif !important; font-size:clamp(1.8rem,4vw,3rem) !important; color:#F7F3EE !important; line-height:1.1; margin-bottom:6px; }
.hero-title em { color:#E8C96A !important; font-style:italic; }
.hero-sub { font-size:0.9rem !important; color:rgba(247,243,238,0.6) !important; letter-spacing:0.05em; margin-bottom:1.2rem; }
.hero-dates { display:inline-flex; gap:1rem; background:rgba(247,243,238,0.1); border:0.5px solid rgba(247,243,238,0.2); border-radius:50px; padding:0.4rem 1.2rem; font-size:0.82rem !important; color:#E8C96A !important; }

.stats-bar { display:flex; background:var(--terracotta); border-radius:0 0 16px 16px; margin-bottom:1.5rem; flex-wrap:wrap; }
.stat-item { flex:1; min-width:90px; padding:0.85rem 1rem; text-align:center; border-right:0.5px solid rgba(247,243,238,0.2); }
.stat-item:last-child { border-right:none; }
.stat-num { font-family:'Playfair Display',serif !important; font-size:1.5rem !important; color:#F7F3EE !important; display:block; line-height:1; font-weight:600; }
.stat-lbl { font-size:0.67rem !important; color:rgba(247,243,238,0.7) !important; text-transform:uppercase; letter-spacing:0.1em; margin-top:3px; display:block; }

.section-header { border-bottom:2px solid var(--parchment); padding-bottom:0.75rem; margin-bottom:1.25rem; }
.section-title { font-family:'Playfair Display',serif !important; font-size:1.8rem !important; color:var(--terracotta-dark) !important; }
.section-meta { font-size:0.85rem !important; color:var(--slate-light) !important; margin-top:2px; font-weight:500; }

.card { background:var(--white); border-radius:12px; border:1px solid var(--parchment); margin-bottom:1rem; box-shadow:0 2px 8px rgba(26,26,46,0.05); overflow:hidden; }
.card-header { display:flex; align-items:center; gap:10px; padding:0.75rem 1.2rem; background:var(--parchment); border-bottom:1px solid rgba(196,105,58,0.15); }
.day-badge { background:var(--terracotta); color:var(--white) !important; font-size:0.72rem; font-weight:700; padding:3px 12px; border-radius:20px; white-space:nowrap; }
.card-date { font-size:0.9rem !important; font-weight:600; color:var(--slate) !important; }

.t-row { display:grid; grid-template-columns:52px 14px 1fr; gap:0 12px; padding:12px 18px; border-bottom:1px solid var(--parchment); }
.t-row:last-child { border-bottom:none; }
.t-time { font-size:0.78rem !important; color:var(--slate-light) !important; text-align:right; padding-top:3px; font-weight:600; font-variant-numeric:tabular-nums; }
.t-dot { width:10px; height:10px; border-radius:50%; background:var(--parchment); border:2px solid var(--terracotta-light); margin-top:4px; flex-shrink:0; }
.t-dot.hi { background:var(--terracotta); border-color:var(--terracotta-dark); }
.t-content { padding-left:2px; }
.t-ttl { font-size:0.92rem !important; font-weight:700; color:var(--ink) !important; margin-bottom:3px; }
.t-ttl.star::before { content:'★ '; color:var(--gold); }
.t-desc { font-size:0.8rem !important; color:var(--slate-light) !important; line-height:1.5; }
.t-tip { font-size:0.75rem !important; color:var(--terracotta-dark) !important; background:rgba(196,105,58,0.07); border-left:3px solid var(--terracotta-light); padding:5px 10px; margin-top:6px; border-radius:0 4px 4px 0; line-height:1.4; }

.tag { display:inline-flex; align-items:center; font-size:0.7rem; padding:3px 10px; border-radius:20px; font-weight:600; margin-right:5px; margin-top:5px; }
.tag-train { background:#E8F0FB; color:#2A5FAC !important; }
.tag-walk  { background:#EBF5E1; color:#3A6B18 !important; }
.tag-food  { background:#FDE8DE; color:#8B3E1E !important; }
.tag-museum{ background:#F5E8F5; color:#7A3A8C !important; }
.tag-shop  { background:#FFF0E0; color:#8B5010 !important; }
.tag-boat  { background:#E0F4EF; color:#0F6E56 !important; }
.tag-sleep { background:#EEF0FD; color:#4A50B0 !important; }
.tag-bus   { background:#FEF3E2; color:#8B5E10 !important; }
.tag-padel { background:#E8F5E8; color:#2A6B2A !important; }

.btn { display:inline-flex; align-items:center; gap:5px; font-size:0.75rem; padding:5px 12px; border-radius:7px; border:1.5px solid; text-decoration:none !important; font-weight:600; margin:6px 5px 0 0; background:var(--white); transition:all 0.15s; cursor:pointer; }
.btn:hover { filter:brightness(0.9); }
.btn-maps    { border-color:#4285F4; color:#4285F4 !important; }
.btn-booking { border-color:#003580; color:#003580 !important; }
.btn-airbnb  { border-color:#FF5A5F; color:#FF5A5F !important; }
.btn-ticket  { border-color:var(--olive); color:var(--olive) !important; }
.btn-tren    { border-color:#B8000A; color:#B8000A !important; }

.hotel-card { border:1px solid var(--parchment); border-radius:12px; padding:1.1rem 1.25rem; margin:0.5rem 0 1.25rem; background:var(--white); box-shadow:0 2px 6px rgba(0,0,0,0.04); }
.hotel-name { font-family:'Playfair Display',serif !important; font-size:1rem !important; color:var(--slate) !important; margin-bottom:4px; font-weight:600; }
.hotel-meta { font-size:0.8rem !important; color:var(--slate-light) !important; line-height:1.6; margin-bottom:8px; }
.hotel-price { display:inline-block; font-size:0.82rem !important; font-weight:700; background:rgba(107,122,62,0.1); color:var(--olive) !important; padding:3px 12px; border-radius:20px; margin-bottom:8px; }

.res-card { background:var(--white); border:1px solid var(--parchment); border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.5rem; box-shadow:0 2px 6px rgba(0,0,0,0.04); }
.res-urgente { border-left:4px solid var(--terracotta); }
.res-normal  { border-left:4px solid var(--olive); }
.res-title   { font-size:0.95rem !important; font-weight:700; color:var(--ink) !important; }
.res-meta    { font-size:0.78rem !important; color:var(--slate-light) !important; margin:3px 0 6px; }
.b-pending   { background:#FEF3CD; color:#8B6914 !important; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.b-confirmed { background:#D4EDDA; color:#1A6B32 !important; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.b-paid      { background:#CCE5FF; color:#0056B3 !important; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.url-link    { font-size:0.75rem !important; color:#0056B3 !important; word-break:break-all; display:block; margin-top:4px; }

.tc { background:var(--white); border:1px solid var(--parchment); border-radius:10px; padding:10px 14px; margin-bottom:6px; display:flex; align-items:center; gap:14px; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.03); }
.tc-icon   { font-size:1.3rem; width:28px; text-align:center; }
.tc-route  { font-size:0.9rem !important; font-weight:700; color:var(--slate) !important; }
.tc-detail { font-size:0.78rem !important; color:var(--slate-light) !important; margin-top:1px; }
.tc-price  { font-size:0.88rem !important; font-weight:700; color:var(--terracotta) !important; margin-left:auto; }

.alert { background:rgba(196,105,58,0.08); border:1px solid rgba(196,105,58,0.3); border-radius:9px; padding:0.85rem 1rem; font-size:0.82rem !important; color:var(--terracotta-dark) !important; margin-bottom:1rem; line-height:1.6; }
.alert strong { color:var(--terracotta-dark) !important; }
.alert-green { background:rgba(107,122,62,0.08); border-color:rgba(107,122,62,0.3); color:var(--olive) !important; }
.alert-green strong { color:var(--olive) !important; }

.nota-card { background:var(--cream); border-radius:9px; padding:10px 14px; margin-bottom:8px; border-left:3px solid var(--gold); font-size:0.85rem !important; color:var(--ink) !important; }
.nota-meta { font-size:0.72rem !important; color:var(--slate-light) !important; margin-top:5px; }

.tip-card { background:var(--white); border:1px solid var(--parchment); border-radius:10px; padding:1rem; box-shadow:0 1px 4px rgba(0,0,0,0.03); margin-bottom:0.75rem; }
.tip-icon  { font-size:1.4rem; margin-bottom:5px; }
.tip-title { font-size:0.88rem !important; font-weight:700; color:var(--slate) !important; margin-bottom:4px; }
.tip-text  { font-size:0.78rem !important; color:var(--slate-light) !important; line-height:1.6; }

.prog-outer { background:var(--parchment); border-radius:5px; height:8px; overflow:hidden; margin:6px 0; }
.prog-inner { height:100%; border-radius:5px; background:var(--terracotta); }

.budget-table { width:100%; border-collapse:collapse; font-size:0.84rem; }
.budget-table th { text-align:left; padding:10px 12px; background:var(--parchment); color:var(--slate) !important; font-weight:700; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.07em; }
.budget-table td { padding:10px 12px; border-bottom:1px solid var(--parchment); color:var(--ink) !important; font-weight:500; }
.budget-table tr.total-row td { border-bottom:none; font-weight:700; color:var(--terracotta-dark) !important; border-top:2px solid var(--terracotta-light); }

.sync-ok  { background:#D4EDDA; color:#1A6B32 !important; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:600; display:inline-block; margin-bottom:1rem; }
.sync-err { background:#F8D7DA; color:#721C24 !important; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:600; display:inline-block; margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)

# ─── GOOGLE SHEETS ─────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def get_workbook():
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets():
    wb = get_workbook()
    existing = [s.title for s in wb.worksheets()]
    needed = {
        "viaje_reservas":["id","estado","url_reserva","confirmacion","monto","notas_int","updated"],
        "viaje_gastos":  ["id","descripcion","categoria","monto","fecha"],
        "viaje_notas":   ["id","texto","tag","autor","fecha"],
    }
    sheets = {}
    for name, headers in needed.items():
        if name not in existing:
            ws = wb.add_worksheet(title=name, rows=500, cols=len(headers))
            ws.append_row(headers)
        sheets[name] = wb.worksheet(name)
    return sheets

@st.cache_data(ttl=25)
def load_reservas():
    try: return pd.DataFrame(get_workbook().worksheet("viaje_reservas").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=25)
def load_gastos():
    try: return pd.DataFrame(get_workbook().worksheet("viaje_gastos").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=25)
def load_notas():
    try: return pd.DataFrame(get_workbook().worksheet("viaje_notas").get_all_records())
    except: return pd.DataFrame()

def save_reserva(res_id, estado, url, conf, monto, notas_int):
    try:
        sheets = ensure_sheets()
        ws = sheets["viaje_reservas"]
        records = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [res_id, estado, url, conf, monto, notas_int, now]
        for i, r in enumerate(records, start=2):
            if r.get("id") == res_id:
                ws.update(f"A{i}:G{i}", [row]); st.cache_data.clear(); return True
        ws.append_row(row); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def add_gasto(desc, cat, monto):
    try:
        sheets = ensure_sheets()
        gid = f"g{datetime.now().strftime('%m%d%H%M%S')}"
        sheets["viaje_gastos"].append_row([gid, desc, cat, monto, datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_gasto(gid):
    try:
        sheets = ensure_sheets()
        ws = sheets["viaje_gastos"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(gid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

def add_nota(texto, tag, autor):
    try:
        sheets = ensure_sheets()
        nid = f"n{datetime.now().strftime('%m%d%H%M%S')}"
        sheets["viaje_notas"].append_row([nid, texto, tag, autor, datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_nota(nid):
    try:
        sheets = ensure_sheets()
        ws = sheets["viaje_notas"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(nid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

# ─── DATOS ─────────────────────────────────────────────────────────────────────
RESERVAS_DEF = [
    {"id":"r01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_book":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
    {"id":"r02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_book":"https://www.galleriaborghese.it","url_maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
    {"id":"r03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_book":"https://www.museivaticani.va","url_maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
    {"id":"r04","title":"Cúpula Brunelleschi — Duomo Florencia","city":"Florencia","fecha":"30 mayo","urgente":True,"url_book":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.google.com/?q=Duomo+Florence"},
    {"id":"r05","title":"David — Accademia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_book":"https://www.uffizi.it/en/the-accademia-gallery","url_maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
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
    ("🚄","Milano → La Spezia","Intercity · ~3h · Salida 08:10","€25–35","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · Incluido en Cinque Terre Card (€29.50/2 días)","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Firenze SMN","Intercity · ~2h · Salida 08:30","€15–20","https://www.trenitalia.com"),
    ("🚌","Firenze ↔ Siena","Bus SENA · 1h30 · desde Autostazione","€9","https://www.tiemmespa.it"),
    ("🚄","Firenze → Roma Termini","Frecciarossa · 1h30 · cada 30 min","€25–45","https://www.trenitalia.com"),
    ("🚄","Roma → Napoli Centrale","Frecciarossa · 1h10 · desde las 06:00","€20–35","https://www.trenitalia.com"),
    ("🚂","Napoli → Pompei Scavi","Circumvesuviana · 40 min · andén -1","€3/p","https://www.eavsrl.it"),
    ("⛵","Napoli → Positano (ferry)","SNAV/Alilauro · Molo Beverello · 65 min · solo mayo–oct","€20/p","https://www.alilauro.it"),
    ("🚌","Bus SITA Costa Amalfi","Positano ↔ Amalfi ↔ Ravello · ticket en tabacchi","€2.50/tramo","https://www.sitasudtrasporti.it"),
    ("🚄","Napoli → Venezia S. Lucia","Frecciarossa directo · 4h50 · salida 07:30","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia 24h","Línea 1 = Gran Canal completo · Línea 2 = rápida","€25","https://actv.avmspa.it"),
    ("🚄","Venezia → Zurich HB","EuroCity directo · 4h45 · a través de los Alpes","€40–60","https://www.sbb.ch"),
    ("🚄","Zurich HB → Aeropuerto ZRH","SBB · 10 min · sale cada 10 min","€4","https://www.sbb.ch"),
]

TIPS = [
    ("☕","Café en barra","Parado = €1.20. Sentado = €3–5. La ley exige mostrar ambos precios."),
    ("💧","Agua del grifo","'Acqua del rubinetto' — gratis. El agua mineral en mesa = €3–5."),
    ("🍽️","Menú del giorno","Primer + segundo + bebida + pan = €12–15. Solo almuerzo."),
    ("💳","Revolut / Wise","Sin comisiones. En Suiza cambiar a CHF. 1 CHF ≈ €1.05."),
    ("👟","Zapatos (fundamental)","10–15 km/día en adoquines. Suela firme. Zapatillas de running ok."),
    ("🕌","Ropa para iglesias","Hombros y rodillas cubiertos. Bufanda liviana para los dos."),
    ("🚌","Bus SITA Amalfi","Ticket en tabacchi ANTES de subir. Sentarse lado derecho → mar."),
    ("🍦","Gelato auténtico","Colores apagados, tapado, no en montañas brillantes = industrial."),
    ("📱","Apps esenciales","Trenitalia · Italo · Maps.me offline · TheFork · SBB (Suiza)."),
    ("🎾","Pádel Nuestro Roma","Día 12 tarde. Bullpadel, Siux, Babolat, Head. Pista para probar."),
    ("🛍️","Ropa barata — Milán","Corso Buenos Aires. 2km. Zara, H&M, marcas italianas."),
    ("🧀","Fondue — Zurich","Swiss Chuchi (Altstadt). ~€40/p. Sprüngli para chocolates (1836)."),
]

ITIN = {
    "🏛️ Milán":{"meta":"Días 1–3 · 25–27 mayo · 3 noches",
        "hotel":{"n":"Hotel Ariston ★★★","m":"Zona Centrale/Navigli · Desayuno · Central para metro","p":"~€80/noche","b":"https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2","a":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2","maps":"https://maps.google.com/?q=Milan+Italy"},
        "days":[
            {"n":"D1","date":"Lun 25 mayo — Llegada y primer paseo","ev":[
                {"t":"10:15","hi":True,"ttl":"Llegada MXP — Inmigración","desc":"Pasaporte argentino. Calcular 30–45 min en temporada alta.","tags":"","maps":"https://maps.google.com/?q=Malpensa+Airport+Milan"},
                {"t":"11:30","hi":False,"ttl":"Malpensa Express → Centrale","desc":"52 min · €13/persona · Validar antes de subir.","tags":'<span class="tag tag-train">🚄 €13/p</span>',"maps":""},
                {"t":"13:30","hi":False,"ttl":"Check-in + Almuerzo","desc":"Risotto alla milanese o cotoletta. Evitar restaurantes junto a estaciones.","tags":'<span class="tag tag-food">🍝 Risotto</span>',"maps":""},
                {"t":"15:00","hi":False,"ttl":"Siesta obligatoria","desc":"11h de vuelo nocturno. 2–3 horas son fundamentales.","tags":"","maps":""},
                {"t":"18:00","hi":False,"ttl":"Paseo Navigli + Aperitivo","desc":"Aperol Spritz al borde del canal. Alzaia Naviglio Grande.","tags":'<span class="tag tag-walk">🚶 Paseo</span>',"maps":"https://maps.google.com/?q=Navigli+Milan"},
            ]},
            {"n":"D2","date":"Mar 26 mayo — Cultura, Shopping y Pádel","ev":[
                {"t":"08:15","hi":True,"ttl":"★ LA ÚLTIMA CENA","desc":"RESERVA OBLIGATORIA. Solo 25 personas cada 15 min. 15 min exactos de visita.","tip":"⚠️ Reservar YA en cenacolodavincimilano.vivaticket.com","tags":'<span class="tag tag-museum">🎨 €17</span>',"maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
                {"t":"10:00","hi":True,"ttl":"★ Duomo di Milano — terrazas","desc":"Ascensor a los 135 chapiteles. Vista 360° de Milán.","tags":'<span class="tag tag-museum">⛪ €15</span>',"maps":"https://maps.google.com/?q=Duomo+di+Milano"},
                {"t":"11:30","hi":False,"ttl":"Galleria Vittorio Emanuele II","desc":"Pisar el toro y girar el talón — trae suerte.","tags":'<span class="tag tag-walk">🚶 Gratis</span>',"maps":"https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II"},
                {"t":"13:00","hi":False,"ttl":"Almuerzo en Brera","desc":"Menú del giorno: primer + segundo + agua = €12–15.","tags":'<span class="tag tag-food">🍽️ €15</span>',"maps":"https://maps.google.com/?q=Brera+Milan"},
                {"t":"15:00","hi":True,"ttl":"★ Shopping — Corso Buenos Aires","desc":"La calle comercial más larga de Italia. Zara, H&M, Bershka. 2km de tiendas.","tags":'<span class="tag tag-shop">🛍️ Ropa</span>',"maps":"https://maps.google.com/?q=Corso+Buenos+Aires+Milan"},
                {"t":"17:30","hi":False,"ttl":"Padel Nuestro Milano (opcional)","desc":"Bullpadel, Siux, Adidas, Nox. Pista interior. Más conveniente ir en Roma.","tip":"Cierra 19:30. Está en las afueras — evaluar si conviene o ir directo a Roma.","tags":'<span class="tag tag-padel">🎾 Pádel</span>',"maps":"https://maps.google.com/?q=Padel+Nuestro+Milan"},
                {"t":"20:00","hi":False,"ttl":"Cena en Navigli","desc":"Evitar restaurantes con foto en el menú en la puerta.","tags":'<span class="tag tag-food">🍷 Cena</span>',"maps":""},
            ]},
            {"n":"D3","date":"Mié 27 mayo — Brera e Isola","ev":[
                {"t":"09:00","hi":True,"ttl":"★ Pinacoteca di Brera","desc":"Mantegna, Raphael, Caravaggio. 2h recomendadas.","tags":'<span class="tag tag-museum">🎨 €15</span>',"maps":"https://maps.google.com/?q=Pinacoteca+di+Brera+Milan"},
                {"t":"11:30","hi":False,"ttl":"Barrio Isola + Bosco Verticale","desc":"El famoso bosque vertical de Stefano Boeri. Cafés locales.","tags":'<span class="tag tag-walk">🌿 Gratis</span>',"maps":"https://maps.google.com/?q=Bosco+Verticale+Milan"},
                {"t":"19:00","hi":False,"ttl":"Preparar maletas — mañana Cinque Terre","desc":"Tren 08:10 desde Milano Centrale. Poner alarma.","tags":'<span class="tag tag-sleep">🧳 Preparación</span>',"maps":""},
            ]},
        ]},
    "🌊 Cinque Terre":{"meta":"Días 4–5 · 28–29 mayo · 2 noches (La Spezia)",
        "hotel":{"n":"Hotel Firenze ★★★ (La Spezia)","m":"5 min a pie de la estación · 2 noches","p":"~€75/noche","b":"https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2","a":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2","maps":"https://maps.google.com/?q=La+Spezia+Italy"},
        "days":[
            {"n":"D4","date":"Jue 28 mayo — Riomaggiore, Manarola, Corniglia","ev":[
                {"t":"11:30","hi":False,"ttl":"Llegada La Spezia + Cinque Terre Card","desc":"Card 2 días = €29.50/persona. Incluye todos los trenes locales.","tags":'<span class="tag tag-train">🎫 €29.50</span>',"maps":""},
                {"t":"12:30","hi":True,"ttl":"★ Riomaggiore — el más fotogénico","desc":"Bajar al puerto. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà.","tags":'<span class="tag tag-food">🍃 Pesto</span>',"maps":"https://maps.google.com/?q=Riomaggiore+Cinque+Terre"},
                {"t":"15:30","hi":True,"ttl":"★ Manarola — la foto icónica","desc":"Casas pastel sobre las rocas. Muelle de natación en temporada.","tags":'<span class="tag tag-walk">📸 Foto icónica</span>',"maps":"https://maps.google.com/?q=Manarola+Cinque+Terre"},
                {"t":"17:30","hi":False,"ttl":"Corniglia — vista 360°","desc":"El único pueblo en lo alto. 377 escalones o minibus.","tags":'<span class="tag tag-walk">🚶 Vista</span>',"maps":"https://maps.google.com/?q=Corniglia+Cinque+Terre"},
            ]},
            {"n":"D5","date":"Vie 29 mayo — Vernazza, senderismo y Monterosso","ev":[
                {"t":"08:00","hi":True,"ttl":"★ Vernazza — el más medieval","desc":"Castillo Doria (€1.50). Puerto pintoresco.","tags":'<span class="tag tag-museum">🏰 €1.50</span>',"maps":"https://maps.google.com/?q=Vernazza+Cinque+Terre"},
                {"t":"11:00","hi":True,"ttl":"★ Senderismo Vernazza → Monterosso","desc":"3.5 km · 2h · dificultad media. El sendero más espectacular.","tip":"Verificar estado en parconazionale5terre.it antes de ir.","tags":'<span class="tag tag-walk">🥾 Trekking</span>',"maps":"https://maps.google.com/?q=Sentiero+Vernazza+Monterosso"},
                {"t":"14:00","hi":False,"ttl":"Monterosso — playa y anchoas","desc":"La única playa de arena real. Acciughe famosas. Agua ~22°C.","tags":'<span class="tag tag-food">🐟 Anchoas</span>',"maps":"https://maps.google.com/?q=Monterosso+al+Mare"},
            ]},
        ]},
    "🌸 Florencia":{"meta":"Días 6–9 · 30 mayo–2 junio · 4 noches",
        "hotel":{"n":"Hotel Davanzati ★★★","m":"2 min del Duomo · Desayuno incluido","p":"~€100/noche","b":"https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2","a":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2","maps":"https://maps.google.com/?q=Florence+Italy"},
        "days":[
            {"n":"D6","date":"Sáb 30 mayo — Duomo + Cúpula + Piazzale","ev":[
                {"t":"11:00","hi":True,"ttl":"★ Duomo + Cúpula Brunelleschi","desc":"463 escalones. Sin reserva: 2h de fila mínimo.","tags":'<span class="tag tag-museum">⛪ Pase €20</span>',"maps":"https://maps.google.com/?q=Duomo+Florence"},
                {"t":"13:00","hi":False,"ttl":"Mercato Centrale — almuerzo","desc":"Piso superior. Pasta fresca o lampredotto.","tags":'<span class="tag tag-food">🥘 Mercado</span>',"maps":"https://maps.google.com/?q=Mercato+Centrale+Florence"},
                {"t":"16:30","hi":False,"ttl":"Ponte Vecchio → Oltrarno","desc":"Puente con joyerías del siglo XVI.","tags":'<span class="tag tag-walk">🌉 Paseo</span>',"maps":"https://maps.google.com/?q=Ponte+Vecchio+Florence"},
                {"t":"18:30","hi":True,"ttl":"★ Piazzale Michelangelo — atardecer","desc":"EL punto de vista de Florencia. Llegar 30 min antes del sunset.","tags":'<span class="tag tag-walk">🌅 Gratis</span>',"maps":"https://maps.google.com/?q=Piazzale+Michelangelo+Florence"},
            ]},
            {"n":"D7","date":"Dom 31 mayo — Uffizi + David + San Miniato","ev":[
                {"t":"08:30","hi":True,"ttl":"★ Galería degli Uffizi","desc":"Botticelli, Leonardo, Caravaggio. 3h mínimo. RESERVA OBLIGATORIA.","tags":'<span class="tag tag-museum">🎨 €20</span>',"maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
                {"t":"14:00","hi":True,"ttl":"★ David de Michelangelo — Accademia","desc":"5.17 metros. El original. No la copia. 1.5h.","tags":'<span class="tag tag-museum">🗿 €12</span>',"maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
                {"t":"17:30","hi":False,"ttl":"San Miniato al Monte","desc":"La iglesia más bella de Florencia. Gratis. Gregoriano a las 17:30.","tags":'<span class="tag tag-walk">⛪ Gratis</span>',"maps":"https://maps.google.com/?q=San+Miniato+al+Monte+Florence"},
            ]},
            {"n":"D8","date":"Lun 1 junio — Pitti + Boboli + Cappelle Medicee","ev":[
                {"t":"09:00","hi":False,"ttl":"Palazzo Pitti + Jardines Boboli","desc":"Rafael y Tiziano. Gruta de Buontalenti (1583).","tags":'<span class="tag tag-museum">🏰 €16</span>',"maps":"https://maps.google.com/?q=Palazzo+Pitti+Florence"},
                {"t":"16:00","hi":True,"ttl":"★ Cappelle Medicee — Michelangelo","desc":"Aurora, Crepúsculo, Día y Noche. Igual de impactantes que el David.","tags":'<span class="tag tag-museum">🗿 €9</span>',"maps":"https://maps.google.com/?q=Cappelle+Medicee+Florence"},
            ]},
            {"n":"D9","date":"Mar 2 junio — Siena y Val d'Orcia","ev":[
                {"t":"07:30","hi":False,"ttl":"Bus SENA a Siena","desc":"Desde Autostazione frente a SMN · 1.5h · €9.","tags":'<span class="tag tag-bus">🚌 €9</span>',"maps":"https://maps.google.com/?q=Autostazione+Firenze"},
                {"t":"09:00","hi":True,"ttl":"★ Piazza del Campo + Torre del Mangia","desc":"La plaza más bella de Italia. Torre: 400 escalones, vistas espectaculares.","tags":'<span class="tag tag-museum">🏰 Torre €10</span>',"maps":"https://maps.google.com/?q=Piazza+del+Campo+Siena"},
                {"t":"10:30","hi":False,"ttl":"Duomo di Siena","desc":"El pavimento de mármol es único. Interior muy diferente al florentino.","tags":'<span class="tag tag-museum">⛪ €8</span>',"maps":"https://maps.google.com/?q=Siena+Cathedral"},
                {"t":"17:00","hi":False,"ttl":"Bus de regreso a Florencia","desc":"Hay buses hasta las 21:00. Mañana viajan a Roma.","tags":'<span class="tag tag-bus">🚌 Regreso</span>',"maps":""},
            ]},
        ]},
    "🏟️ Roma":{"meta":"Días 10–13 · 3–6 junio · 4 noches",
        "hotel":{"n":"Hotel Arco del Lauro ★★★ (Trastevere)","m":"Zona auténtica · B&B familiar · A pie del centro","p":"~€88/noche","b":"https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2","a":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2","maps":"https://maps.google.com/?q=Trastevere+Rome"},
        "days":[
            {"n":"D10","date":"Mié 3 junio — Vaticano completo","ev":[
                {"t":"10:30","hi":True,"ttl":"★ Museos Vaticanos + Capilla Sixtina","desc":"3–4h. RESERVA OBLIGATORIA con semanas de anticipación.","tip":"⚠️ Silencio absoluto en la Sixtina. Prohibido fotografiar.","tags":'<span class="tag tag-museum">🎨 €17</span>',"maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
                {"t":"14:00","hi":False,"ttl":"Basílica San Pedro + Cúpula","desc":"La basílica más grande del mundo cristiano. Cúpula: 551 escalones o ascensor (€8).","tags":'<span class="tag tag-museum">⛪ Gratis · Cúpula €8</span>',"maps":"https://maps.google.com/?q=St+Peters+Basilica+Rome"},
            ]},
            {"n":"D11","date":"Jue 4 junio — Roma imperial","ev":[
                {"t":"08:00","hi":True,"ttl":"★ Coliseo + Foro Romano + Palatino","desc":"Combo obligatorio. 3–4h. Reservar online para evitar 2h de fila.","tags":'<span class="tag tag-museum">🏛️ €16</span>',"maps":"https://maps.google.com/?q=Colosseum+Rome"},
                {"t":"17:30","hi":False,"ttl":"Trastevere — paseo y cena","desc":"Basílica di Santa Maria in Trastevere (gratis). Cena: Da Enzo al 29.","tags":'<span class="tag tag-walk">🚶 Paseo</span>',"maps":"https://maps.google.com/?q=Trastevere+Rome"},
            ]},
            {"n":"D12","date":"Vie 5 junio — Roma barroca + Borghese + Pádel","ev":[
                {"t":"09:00","hi":False,"ttl":"Pantheon → Piazza Navona → Fontana di Trevi","desc":"Pantheon €5 (desde 2023). Trevi: moneda de espaldas con la derecha.","tags":'<span class="tag tag-museum">🏛️ €5</span>',"maps":"https://maps.google.com/?q=Pantheon+Rome"},
                {"t":"15:00","hi":True,"ttl":"★ Galería Borghese — Bernini","desc":"Solo 360 personas cada 2h. Apolo y Dafne. Lo más impactante de Roma.","tags":'<span class="tag tag-museum">🗿 €15</span>',"maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
                {"t":"18:00","hi":True,"ttl":"★ Padel Nuestro Roma","desc":"Bullpadel, Siux, Babolat, Head, Star Vie. Pista interior para probar palas antes de comprar.","tags":'<span class="tag tag-padel">🎾 Pádel</span>',"maps":"https://maps.google.com/?q=Padel+Nuestro+Roma+Italy"},
            ]},
            {"n":"D13","date":"Sáb 6 junio — Castel Sant'Angelo + libre","ev":[
                {"t":"09:00","hi":False,"ttl":"Castel Sant'Angelo","desc":"Mausoleo de Adriano. Vista del Tiber y San Pedro desde la cima.","tags":'<span class="tag tag-museum">🏰 €14</span>',"maps":"https://maps.google.com/?q=Castel+Sant+Angelo+Rome"},
                {"t":"14:00","hi":False,"ttl":"Tarde libre + preparación","desc":"Compras Via del Corso. Mañana: tren a Nápoles.","tags":'<span class="tag tag-walk">🛍️ Libre</span>',"maps":""},
            ]},
        ]},
    "🍕 Nápoles":{"meta":"Día 14 · 7 junio · 1 noche",
        "hotel":{"n":"Hotel Piazza Bellini ★★★","m":"Centro histórico UNESCO · Spaccanapoli","p":"~€80/noche","b":"https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2","a":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2","maps":"https://maps.google.com/?q=Naples+Italy"},
        "days":[
            {"n":"D14","date":"Dom 7 junio — Pompeya + Nápoles + Pizza","ev":[
                {"t":"09:00","hi":True,"ttl":"★ Circumvesuviana → Pompeya Scavi","desc":"Andén subterráneo -1 de Napoli Centrale. Cada 30 min. €3 cada uno.","tags":'<span class="tag tag-train">🚂 €3 · 40min</span>',"maps":"https://maps.google.com/?q=Pompei+Scavi+station"},
                {"t":"10:00","hi":True,"ttl":"★ Pompeya — ciudad del 79 d.C.","desc":"3h mínimo. Casa dei Vettii, Anfiteatro, moldes humanos. Llevar agua y sombrero.","tags":'<span class="tag tag-museum">🌋 €16</span>',"maps":"https://maps.google.com/?q=Pompeii+Archaeological+Park"},
                {"t":"15:00","hi":False,"ttl":"Spaccanapoli + Museo Arqueológico","desc":"El mejor museo de arqueología romana del mundo. Objetos de Pompeya.","tags":'<span class="tag tag-museum">🏺 €15</span>',"maps":"https://maps.google.com/?q=National+Archaeological+Museum+Naples"},
                {"t":"19:30","hi":True,"ttl":"★ La pizza napolitana ORIGINAL","desc":"Da Michele (solo Margherita/Marinara, fila larga) o Sorbillo (favorita locales).","tags":'<span class="tag tag-food">🍕 €5–8</span>',"maps":"https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples"},
            ]},
        ]},
    "🌅 Costa Amalfi":{"meta":"Días 15–16 · 8–9 junio · 2 noches (Praiano)",
        "hotel":{"n":"Albergo California ★★★ (Praiano)","m":"Vista al mar · Desayuno · 10 min de Positano en ferry","p":"~€92/noche","b":"https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2","a":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2","maps":"https://maps.google.com/?q=Praiano+Italy"},
        "days":[
            {"n":"D15","date":"Lun 8 junio — Positano + Amalfi","ev":[
                {"t":"10:30","hi":True,"ttl":"★ Positano — las casas en cascada","desc":"Playa Grande. Guijarros. Reposeras ~€20 el par. Agua Tirreno ~22°C.","tags":'<span class="tag tag-walk">🏖️ Playa</span>',"maps":"https://maps.google.com/?q=Positano+Amalfi+Coast"},
                {"t":"15:00","hi":True,"ttl":"★ Bus SITA → Amalfi ciudad","desc":"Sentarse del lado DERECHO mirando al mar. Duomo árabe-normando siglo IX.","tip":"Comprar ticket en tabacchi antes de subir. €2.50 el tramo.","tags":'<span class="tag tag-bus">🚌 €2.50 · Lado derecho</span>',"maps":"https://maps.google.com/?q=Amalfi+Cathedral"},
                {"t":"19:30","hi":False,"ttl":"Cena con vista al mar","desc":"Atardecer sobre el Tirreno. Probar: scialatielli ai frutti di mare.","tags":'<span class="tag tag-food">🌅 Cena</span>',"maps":""},
            ]},
            {"n":"D16","date":"Mar 9 junio — Ravello + Sentiero degli Dei","ev":[
                {"t":"08:00","hi":True,"ttl":"★ Ravello — Villa Cimbrone + Terrazza dell'Infinito","desc":"El balcón más bello del mundo según Wagner. Jardines sobre el precipicio. €7.","tags":'<span class="tag tag-museum">🌿 €7</span>',"maps":"https://maps.google.com/?q=Villa+Cimbrone+Ravello"},
                {"t":"11:00","hi":True,"ttl":"★ Sentiero degli Dei — 7.8km · 3h","desc":"El sendero más famoso de Amalfi. Desde Bomerano bajando a Positano desde 600m de altura.","tip":"Llevar agua, sombrero y calzado firme. El mejor día del viaje para muchos viajeros.","tags":'<span class="tag tag-walk">🥾 Trekking</span>',"maps":"https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast"},
                {"t":"15:00","hi":False,"ttl":"Llegada Positano + playa merecida","desc":"Baño en el Tirreno. Mañana: ferry + tren largo a Venecia.","tags":'<span class="tag tag-walk">🏖️ Playa</span>',"maps":""},
            ]},
        ]},
    "🚤 Venecia":{"meta":"Día 17 · 10 junio · 1 noche",
        "hotel":{"n":"Hotel Dalla Mora ★★★ (Santa Croce)","m":"10 min a pie de la estación · Venecia real, no Mestre","p":"~€100/noche","b":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","a":"","maps":"https://maps.google.com/?q=Venice+Italy"},
        "days":[
            {"n":"D17","date":"Mié 10 junio — Venecia completa","ev":[
                {"t":"13:00","hi":True,"ttl":"★ Gran Canal — Vaporetto línea 1 (la lenta)","desc":"45 min de palacios del siglo XIV. Ticket 24h = €25.","tags":'<span class="tag tag-boat">🚤 24h €25</span>',"maps":"https://maps.google.com/?q=Grand+Canal+Venice"},
                {"t":"15:00","hi":True,"ttl":"★ Plaza San Marcos + Basílica + Campanile","desc":"Basílica gratis con espera. Campanile €10 con la mejor vista de Venecia.","tags":'<span class="tag tag-museum">🏛️ Campanile €10</span>',"maps":"https://maps.google.com/?q=St+Marks+Basilica+Venice"},
                {"t":"17:00","hi":True,"ttl":"★ Perderse sin mapa — la mejor actividad","desc":"118 islas, 400 puentes. Apagar Google Maps y caminar. Los callejones angostos llevan a los campos más secretos.","tags":'<span class="tag tag-walk">🗺️ Sin mapa</span>',"maps":""},
                {"t":"19:30","hi":False,"ttl":"Spritz veneziano en bacaro + Rialto","desc":"El Spritz se inventó en Venecia. Cicchetti (tapas €1–2). Zona Cannaregio.","tags":'<span class="tag tag-food">🍹 Bacaro</span>',"maps":"https://maps.google.com/?q=Rialto+Bridge+Venice"},
                {"t":"21:00","hi":False,"ttl":"Góndola nocturna (opcional)","desc":"Precio fijo oficial: €80 para 30 min (hasta 6 personas).","tags":'<span class="tag tag-boat">🎭 €80</span>',"maps":""},
            ]},
        ]},
    "🇨🇭 Zurich":{"meta":"Días 18–20 · 11–13 junio · 3 noches · Vuelo 14/6 a las 08:55",
        "hotel":{"n":"Hotel Otter ★★ (Langstrasse) o IBIS City West","m":"Zona trendy · A pie del Altstadt · 3 noches","p":"~€100/noche","b":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","a":"","maps":"https://maps.google.com/?q=Zurich+Switzerland"},
        "days":[
            {"n":"D18","date":"Jue 11 junio — Llegada + Altstadt","ev":[
                {"t":"14:00","hi":False,"ttl":"Bahnhofstrasse + Lago de Zurich","desc":"La calle más cara del mundo. El lago al final para sentarse.","tags":'<span class="tag tag-walk">⌚ Paseo</span>',"maps":"https://maps.google.com/?q=Bahnhofstrasse+Zurich"},
                {"t":"15:30","hi":True,"ttl":"★ Grossmünster + Altstadt","desc":"Donde Zwinglio inició la Reforma (1519). Torres €5.","tags":'<span class="tag tag-museum">⛪ Torres €5</span>',"maps":"https://maps.google.com/?q=Grossmunster+Zurich"},
                {"t":"18:00","hi":False,"ttl":"Fraumünster — vitrales de Chagall","desc":"5 vitrales de Marc Chagall (1970) en edificio del siglo XIII. €5.","tags":'<span class="tag tag-museum">🎨 €5</span>',"maps":"https://maps.google.com/?q=Fraumunster+Zurich"},
            ]},
            {"n":"D19","date":"Vie 12 junio — Lago + ETH + Fondue","ev":[
                {"t":"09:00","hi":True,"ttl":"★ Crucero Lago de Zurich","desc":"ZSG · recorrido corto 1h o largo 4h hasta Rapperswil. Los Alpes de fondo.","tags":'<span class="tag tag-boat">⛵ €8–30</span>',"maps":"https://maps.google.com/?q=Lake+Zurich"},
                {"t":"16:00","hi":False,"ttl":"Polybahn → terraza ETH (gratis)","desc":"Funicular de 1889. Vista de Zurich y los Alpes. Gratis.","tags":'<span class="tag tag-walk">🔭 Gratis</span>',"maps":"https://maps.google.com/?q=ETH+Zurich"},
                {"t":"20:00","hi":True,"ttl":"★ Fondue suiza — Swiss Chuchi","desc":"El plato nacional suizo. ~€35–45/persona.","tags":'<span class="tag tag-food">🧀 Fondue</span>',"maps":"https://maps.google.com/?q=Swiss+Chuchi+Zurich"},
            ]},
            {"n":"D20","date":"Sáb 13 junio — Uetliberg + Chocolates + Última noche","ev":[
                {"t":"09:00","hi":False,"ttl":"Uetliberg — la montaña de Zurich","desc":"Tren S10 desde HB, 20 min, €5. 870m. Vista de Zurich y los Alpes.","tags":'<span class="tag tag-walk">⛰️ €5</span>',"maps":"https://maps.google.com/?q=Uetliberg+Zurich"},
                {"t":"13:00","hi":True,"ttl":"★ Chocolates Sprüngli + Mercado Bürkliplatz","desc":"Los mejores truffes du jour desde 1836. Mercado de artesanías los sábados.","tags":'<span class="tag tag-food">🍫 Chocolates</span>',"maps":"https://maps.google.com/?q=Confiserie+Sprungli+Zurich"},
                {"t":"19:00","hi":True,"ttl":"★ Última cena del viaje 🥂","desc":"Brindar por el viaje. Hacer check-in online del vuelo LA8799.","tags":'<span class="tag tag-food">🥂 Despedida</span>',"maps":""},
                {"t":"22:00","hi":False,"ttl":"A dormir — vuelo 08:55 mañana","desc":"Tren HB→ZRH: 10 min, sale cada 10 min. Estar en aeropuerto a las 07:00.","tip":"⚠️ ALARMA 06:00. Sin excepciones.","tags":'<span class="tag tag-sleep">✈️ Alarma 06:00</span>',"maps":""},
            ]},
        ]},
}

PRESUPUESTO_FILAS = [
    ("Milán","3","€80","€240"),("La Spezia","2","€75","€150"),
    ("Florencia","4","€100","€400"),("Roma","4","€88","€350"),
    ("Nápoles","1","€80","€80"),("Costa Amalfi","2","€92","€185"),
    ("Venecia","1","€100","€100"),("Zurich","3","€100","€300"),
    ("TOTAL","20","~€95","~€1.805"),
]

# ─── CARGAR DATOS ──────────────────────────────────────────────────────────────
try:
    df_res=load_reservas(); df_gas=load_gastos(); df_notas=load_notas(); sheets_ok=True
except:
    df_res=df_gas=df_notas=pd.DataFrame(); sheets_ok=False

def get_rd(res_id):
    if df_res.empty or "id" not in df_res.columns: return {}
    row = df_res[df_res["id"]==res_id]
    return row.iloc[0].to_dict() if not row.empty else {}

# ─── HERO ──────────────────────────────────────────────────────────────────────
ok_count = sum(1 for r in RESERVAS_DEF if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
total_gas = 0
if not df_gas.empty and "monto" in df_gas.columns:
    total_gas = pd.to_numeric(df_gas["monto"], errors="coerce").fillna(0).sum()

st.markdown(f"""
<div class="hero">
<div class="hero-inner">
  <div class="hero-flag">🇮🇹 🇨🇭</div>
  <div class="hero-title">Italia & <em>Zurich</em></div>
  <div class="hero-sub">Luna de Miel · Mayo–Junio 2026 · Compartido en tiempo real</div>
  <div class="hero-dates"><span>✈ Sale 24 mayo · IGU</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
</div>
</div>
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
    st.markdown('<span class="sync-err">🔴 Sin conexión a Sheets — verificar credenciales en secrets.toml</span>', unsafe_allow_html=True)

st.write("")

# ─── TABS ──────────────────────────────────────────────────────────────────────
tab_vue,tab_itin,tab_res_t,tab_trans,tab_gas_t,tab_pres,tab_tips,tab_notas_t = st.tabs([
    "✈️ Vuelos","🗺️ Itinerario","🎟️ Reservas","🚄 Transportes",
    "💰 Gastos","📊 Presupuesto","💡 Tips","📝 Notas"
])

# ══ VUELOS ═══════════════════════════════════════════════════════════════════
with tab_vue:
    st.markdown('<div class="section-header"><div class="section-title">Vuelos confirmados</div><div class="section-meta">Itinerario LATAM + Swiss · Foz de Iguazú ↔ Zurich</div></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
      <div class="card-header"><span class="day-badge">IDA</span><span class="card-date">Domingo 24 mayo 2026 — Foz de Iguazú → Milán</span></div>
      <div class="t-row"><div class="t-time">14:50</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">IGU → São Paulo GRU</div><div class="t-desc">LA3879 op. LATAM Brasil · Airbus 320 · 1h 40min</div><span class="tag tag-train">✈ LA3879 · A320</span></div></div>
      <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">16:30</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl">Escala São Paulo Guarulhos (GRU)</div><div class="t-desc">Cambio de avión · 1h 30min de conexión</div></div></div>
      <div class="t-row"><div class="t-time">18:00</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">São Paulo GRU → Milán Malpensa MXP</div><div class="t-desc">LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día</div><span class="tag tag-train">✈ LA8072 · B777</span></div></div>
    </div>
    <div class="card">
      <div class="card-header"><span class="day-badge">VUELTA</span><span class="card-date">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>
      <div class="t-row"><div class="t-time">08:55</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Zurich ZRH → Milán Malpensa MXP</div><div class="t-desc">LA8799 op. Swiss · Avión 221 · 55min · Salir al aeropuerto a las 07:00</div><div class="t-tip">⚠️ Tren Zurich HB → ZRH: 10 min, sale cada 10 min. Alarma 06:00.</div><span class="tag tag-train">✈ LA8799 · Swiss</span></div></div>
      <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">09:50</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl">Escala Milán Malpensa (MXP)</div><div class="t-desc">Cambio de avión · 3h 10min de conexión</div></div></div>
      <div class="t-row"><div class="t-time">13:00</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">Milán MXP → São Paulo GRU</div><div class="t-desc">LA8073 op. LATAM Brasil · Boeing 773 · 12h</div><span class="tag tag-train">✈ LA8073 · B777</span></div></div>
      <div class="t-row" style="background:rgba(237,231,220,0.3)"><div class="t-time">20:00</div><div class="t-dot"></div><div class="t-content"><div class="t-ttl">Escala São Paulo Guarulhos (GRU)</div><div class="t-desc">Cambio de avión · 2h 20min de conexión</div></div></div>
      <div class="t-row"><div class="t-time">22:20</div><div class="t-dot hi"></div><div class="t-content"><div class="t-ttl star">São Paulo GRU → Foz de Iguazú IGU</div><div class="t-desc">LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día</div><span class="tag tag-train">✈ LA3206 · A321</span></div></div>
    </div>
    <div class="alert"><strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno. Primer día: siesta obligatoria 2–3h, almuerzo tranquilo y paseo suave al atardecer por Navigli. No planificar actividades intensas.</div>
    """, unsafe_allow_html=True)

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("Ciudad", list(ITIN.keys()), horizontal=True, label_visibility="collapsed")
    d = ITIN[ciudad_sel]; h = d["hotel"]
    st.markdown(f'<div class="section-header" style="margin-top:1rem"><div class="section-title">{ciudad_sel}</div><div class="section-meta">{d["meta"]}</div></div>', unsafe_allow_html=True)
    bb = f'<a href="{h["b"]}" target="_blank" class="btn btn-booking">📅 Booking</a>' if h["b"] else ""
    ba = f'<a href="{h["a"]}" target="_blank" class="btn btn-airbnb">🏠 Airbnb</a>' if h["a"] else ""
    bm = f'<a href="{h["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if h["maps"] else ""
    st.markdown(f'<div class="hotel-card"><div class="hotel-name">{h["n"]}</div><div class="hotel-meta">{h["m"]}</div><span class="hotel-price">{h["p"]}</span><br>{bb}{ba}{bm}</div>', unsafe_allow_html=True)
    for day in d["days"]:
        html = f'<div class="card"><div class="card-header"><span class="day-badge">{day["n"]}</span><span class="card-date">{day["date"]}</span></div>'
        for e in day["ev"]:
            dc="hi" if e["hi"] else ""; sc="star" if e["hi"] else ""
            tip_h = f'<div class="t-tip">{e["tip"]}</div>' if e.get("tip") else ""
            map_b = f'<a href="{e["maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>' if e.get("maps") else ""
            html += f'<div class="t-row"><div class="t-time">{e["t"]}</div><div class="t-dot {dc}"></div><div class="t-content"><div class="t-ttl {sc}">{e["ttl"]}</div><div class="t-desc">{e["desc"]}</div>{tip_h}<div style="margin-top:4px">{e.get("tags","")}{map_b}</div></div></div>'
        st.markdown(html+"</div>", unsafe_allow_html=True)

# ══ RESERVAS ══════════════════════════════════════════════════════════════════
with tab_res_t:
    st.markdown('<div class="section-header"><div class="section-title">Tracker de Reservas</div><div class="section-meta">Cargá la URL reservada — tu pareja lo ve al instante en Google Sheets</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert"><strong>⚠️ Urgente:</strong> La Última Cena, Galería Borghese y Museos Vaticanos se agotan meses antes. Gestionar primero.</div>', unsafe_allow_html=True)
    filtro = st.selectbox("Filtrar por ciudad",["Todas"]+list(dict.fromkeys(r["city"] for r in RESERVAS_DEF)))
    for r in RESERVAS_DEF:
        if filtro!="Todas" and r["city"]!=filtro: continue
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        cc="res-urgente" if r["urgente"] else "res-normal"
        bl={"pending":"b-pending","confirmed":"b-confirmed","paid":"b-paid"}.get(ea,"b-pending")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva",""))
        uh=f'<a href="{us}" target="_blank" class="url-link">🔗 {us[:70]}{"..." if len(us)>70 else ""}</a>' if us else ""
        st.markdown(f'<div class="res-card {cc}"><div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px"><span style="font-size:0.72rem;padding:2px 8px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span><span class="res-title">{"⚠️ " if r["urgente"] else ""}{r["title"]}</span><span class="{bl}">{ll}</span></div><div class="res-meta">📅 {r["fecha"]}</div>{uh}</div>', unsafe_allow_html=True)
        with st.form(key=f"f_{r['id']}"):
            c1,c2,c3=st.columns([2,2,1])
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"s_{r['id']}")
            with c2: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","")),key=f"c_{r['id']}",placeholder="ej. HB-123456")
            with c3: nm=st.number_input("Monto €",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"m_{r['id']}")
            nu=st.text_input("URL reservada (Airbnb / Booking / sitio oficial)",value=us,key=f"u_{r['id']}",placeholder="https://www.airbnb.com/rooms/...")
            nn=st.text_area("Notas internas",value=str(rd.get("notas_int","")),key=f"n_{r['id']}",height=55,placeholder="Ej: Check-in 15hs, habitación alta...")
            cs,cb,cm=st.columns([2,1,1])
            with cs: sub=st.form_submit_button("💾 Guardar — visible para tu pareja al instante",use_container_width=True)
            with cb: st.markdown(f'<a href="{r["url_book"]}" target="_blank" class="btn btn-ticket">🔗 Reservar</a>',unsafe_allow_html=True)
            with cm: st.markdown(f'<a href="{r["url_maps"]}" target="_blank" class="btn btn-maps">📍 Maps</a>',unsafe_allow_html=True)
            if sub:
                if save_reserva(r["id"],ne,nu,nc,nm,nn): st.success("✅ Guardado — tu pareja ya lo puede ver"); st.rerun()
        st.write("")

# ══ TRANSPORTES ═══════════════════════════════════════════════════════════════
with tab_trans:
    st.markdown('<div class="section-header"><div class="section-title">Todos los transportes</div><div class="section-meta">En orden cronológico · Con links de compra</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="alert alert-green"><strong>💡 Truco:</strong> Comprar trenes con 60 días de anticipación puede ser 4x más barato. Frecciarossa Roma→Nápoles: <strong>€9 anticipado</strong> vs €55 último momento.</div>', unsafe_allow_html=True)
    for icon,route,detail,price,url in TRANSPORTES:
        st.markdown(f'<div class="tc"><div class="tc-icon">{icon}</div><div style="flex:1"><div class="tc-route">{route}</div><div class="tc-detail">{detail}</div></div><div class="tc-price">{price}</div><a href="{url}" target="_blank" class="btn btn-tren">🔗 Comprar</a></div>', unsafe_allow_html=True)

# ══ GASTOS ════════════════════════════════════════════════════════════════════
with tab_gas_t:
    st.markdown('<div class="section-header"><div class="section-title">Tracker de Gastos</div><div class="section-meta">Cargá cada gasto — ambos lo ven en tiempo real</div></div>', unsafe_allow_html=True)
    PRESUPUESTO_TOTAL=4350.0
    cats_sum={"Alojamiento":0,"Transporte":0,"Entradas":0,"Comidas":0,"Otros":0}
    if not df_gas.empty and "monto" in df_gas.columns and "categoria" in df_gas.columns:
        for _,row in df_gas.iterrows():
            try: cats_sum[row.get("categoria","Otros")]=cats_sum.get(row.get("categoria","Otros"),0)+float(row["monto"])
            except: pass
    total_g=sum(cats_sum.values()); pct=min(100,int(total_g/PRESUPUESTO_TOTAL*100))
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("💶 Total",f"€{total_g:,.0f}",f"{pct}% del presupuesto")
    c2.metric("🏨 Alojamiento",f"€{cats_sum['Alojamiento']:,.0f}")
    c3.metric("🚄 Transporte",f"€{cats_sum['Transporte']:,.0f}")
    c4.metric("🎟️ Entradas",f"€{cats_sum['Entradas']:,.0f}")
    c5.metric("🍽️ Comidas",f"€{cats_sum['Comidas']:,.0f}")
    st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct}%"></div></div><div style="font-size:0.75rem;color:#6B7A8D;margin-top:4px;font-weight:500">€{total_g:,.0f} gastados de €{PRESUPUESTO_TOTAL:,.0f} presupuestados ({pct}%)</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("**Agregar gasto**")
    with st.form("fg"):
        cd,cc,cm=st.columns([3,2,1])
        with cd: gd=st.text_input("Descripción",placeholder="ej. Airbnb Florencia 4 noches")
        with cc: gc=st.selectbox("Categoría",["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        with cm: gm=st.number_input("€",min_value=0.0,step=1.0)
        if st.form_submit_button("➕ Agregar gasto",use_container_width=True):
            if gd.strip() and gm>0:
                if add_gasto(gd.strip(),gc,gm): st.success("Gasto agregado ✓"); st.rerun()
            else: st.warning("Completá la descripción y el monto")
    st.write("")
    if not df_gas.empty and "descripcion" in df_gas.columns:
        st.markdown("**Historial de gastos**")
        df_show=df_gas[["id","descripcion","categoria","monto","fecha"]].copy()
        df_show["monto"]=pd.to_numeric(df_show["monto"],errors="coerce").map("€{:,.0f}".format)
        st.dataframe(df_show.drop("id",axis=1),use_container_width=True,hide_index=True)
        di=st.text_input("ID de gasto a eliminar",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar gasto") and di:
            if del_gasto(di.strip()): st.success("Eliminado ✓"); st.rerun()
    else: st.info("Aún no hay gastos cargados. ¡Agregá el primero!")

# ══ PRESUPUESTO ═══════════════════════════════════════════════════════════════
with tab_pres:
    st.markdown('<div class="section-header"><div class="section-title">Presupuesto estimado</div><div class="section-meta">Para 2 personas · 20 días · Sin vuelos</div></div>', unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🏨 Alojamiento (20 noches)","~€1.805","Promedio €90/noche")
    c2.metric("🚄 Transportes internos","~€500","Trenes + ferries + buses")
    c3.metric("🎟️ Entradas museos","~€350","Para 2 personas")
    c4.metric("🍽️ Comidas (~€60/día)","~€1.200","Desayuno + almuerzo + cena")
    st.write("")
    c5,c6=st.columns(2)
    c5.metric("🛍️ Imprevistos / extras","~€400","Compras, pádel, chocolates")
    c6.metric("💶 TOTAL ESTIMADO","~€4.350","Para 2 personas sin vuelos")
    st.write("")
    rows=""
    for ciudad,noches,precio,total in PRESUPUESTO_FILAS:
        es_tot = ciudad=="TOTAL"
        cls = 'class="total-row"' if es_tot else ""
        rows+=f"<tr {cls}><td>{ciudad}</td><td style='text-align:center'>{noches}</td><td style='text-align:center'>{precio}</td><td style='text-align:center;font-weight:700'>{total}</td></tr>"
    st.markdown(f'<div class="card" style="padding:0"><table class="budget-table"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th><th style="text-align:center">€/noche</th><th style="text-align:center">Total</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

# ══ TIPS ══════════════════════════════════════════════════════════════════════
with tab_tips:
    st.markdown('<div class="section-header"><div class="section-title">Tips esenciales</div><div class="section-meta">Lo que marca la diferencia entre turista y viajero</div></div>', unsafe_allow_html=True)
    cols=st.columns(3)
    for i,(icon,title,text) in enumerate(TIPS):
        with cols[i%3]:
            st.markdown(f'<div class="tip-card"><div class="tip-icon">{icon}</div><div class="tip-title">{title}</div><div class="tip-text">{text}</div></div>', unsafe_allow_html=True)
            st.write("")

# ══ NOTAS ═════════════════════════════════════════════════════════════════════
with tab_notas_t:
    st.markdown('<div class="section-header"><div class="section-title">Notas compartidas</div><div class="section-meta">Cualquiera puede publicar — el otro lo ve al instante</div></div>', unsafe_allow_html=True)
    with st.form("fn"):
        nt=st.text_area("Nueva nota",height=90,placeholder="Escribí algo — tu pareja lo ve al instante...")
        ct,ca=st.columns(2)
        with ct: ntag=st.selectbox("Categoría",["💡 Idea","⚠️ Importante","🍽️ Restaurante","🏨 Hotel","🎾 Pádel","🛍️ Compras","📝 General"])
        with ca: naut=st.selectbox("Quién escribe",["Adilson","Esposa"])
        if st.form_submit_button("📤 Publicar nota",use_container_width=True):
            if nt.strip():
                if add_nota(nt.strip(),ntag,naut): st.success("Nota publicada ✓"); st.rerun()
            else: st.warning("Escribí algo primero")
    st.write("")
    if not df_notas.empty and "texto" in df_notas.columns:
        for _,row in df_notas.iloc[::-1].iterrows():
            st.markdown(f'<div class="nota-card"><strong>{row.get("tag","📝")}</strong> · <em style="color:#6B7A8D">{row.get("autor","")}</em><br><span style="color:#1A1A2E">{row.get("texto","")}</span><div class="nota-meta">🕐 {row.get("fecha","")}</div></div>', unsafe_allow_html=True)
            if st.button("🗑️ Borrar",key=f"dn_{row.get('id','')}"):
                if del_nota(str(row.get("id",""))): st.rerun()
    else: st.info("Aún no hay notas. ¡Publicá la primera!")
