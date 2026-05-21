import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime, date
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Italia & Zurich 2026 🇮🇹", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;1,400&display=swap');
:root{--cr:#F7F3EE;--pa:#EDE7DC;--te:#C4693A;--td:#8B3E1E;--ol:#6B7A3E;--sl:#6B7A8D;--go:#C9A84C;--ink:#1A1A2E;--w:#fff;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;}
.stApp{background-color:var(--cr)!important;}
.stApp *{color:var(--ink)!important;}
#MainMenu,footer,header,[data-testid="stDecoration"]{display:none!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--pa);border-radius:12px;padding:6px 8px;gap:4px;overflow-x:auto;flex-wrap:nowrap!important;}
.stTabs [data-baseweb="tab"]{padding:6px 14px;border-radius:8px;background:rgba(255,255,255,0.5);border:none!important;white-space:nowrap;}
.stTabs [data-baseweb="tab"] p{color:#3D4A5C!important;font-weight:600!important;font-size:0.82rem!important;}
.stTabs [aria-selected="true"]{background:var(--w)!important;box-shadow:0 2px 6px rgba(0,0,0,0.08)!important;}
.stTabs [aria-selected="true"] p{color:var(--td)!important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none!important;}
div[data-testid="stRadio"]>div{flex-direction:row!important;flex-wrap:wrap!important;gap:6px!important;background:var(--w)!important;padding:10px!important;border-radius:12px!important;border:1px solid var(--pa)!important;}
div[data-testid="stRadio"]>div>label{background:var(--pa)!important;padding:6px 12px!important;border-radius:20px!important;}
div[data-testid="stRadio"]>div>label p{color:var(--ink)!important;font-weight:600!important;font-size:0.8rem!important;margin:0!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"]{background:var(--te)!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"] p{color:var(--w)!important;}
div[data-testid="stRadio"] div[role="radiogroup"] label>div:first-child{display:none!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:#fff!important;color:#1A1A2E!important;border:1px solid #EDE7DC!important;border-radius:8px!important;}
[data-baseweb="base-input"]{background:#fff!important;}
[data-baseweb="base-input"] input,[data-baseweb="base-input"] textarea{background:#fff!important;color:#1A1A2E!important;}
.stSelectbox>div>div,[data-baseweb="select"],[data-baseweb="select"] *{background:#fff!important;color:#1A1A2E!important;}
.stButton>button{background:var(--te)!important;color:var(--w)!important;border:none!important;border-radius:8px!important;font-weight:600!important;}
.stButton>button:hover{background:var(--td)!important;}
[data-testid="stMetric"]{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.75rem!important;}
[data-testid="stMetricLabel"] p{color:var(--sl)!important;font-size:0.75rem!important;}
[data-testid="stMetricValue"]{color:var(--td)!important;}
[data-testid="stExpander"]{border:1px solid var(--pa)!important;border-radius:10px!important;background:var(--w)!important;}
.hero{background:linear-gradient(135deg,#3D4A5C 0%,#1A1A2E 100%);border-radius:14px 14px 0 0;padding:1.75rem 1.25rem 1.5rem;text-align:center;}
.htitle{font-family:'Playfair Display',serif!important;font-size:2.2rem!important;color:#F7F3EE!important;margin-bottom:4px;line-height:1.1;}
.htitle em{color:#E8C96A!important;font-style:italic;}
.hsub{font-size:0.85rem!important;color:rgba(247,243,238,0.6)!important;margin-bottom:1rem;}
.hdates{display:inline-block;background:rgba(247,243,238,0.1);border:0.5px solid rgba(247,243,238,0.2);border-radius:50px;padding:0.35rem 1rem;font-size:0.78rem!important;color:#E8C96A!important;}
.countdown-box{background:rgba(232,198,106,0.15);border:1px solid rgba(232,198,106,0.4);border-radius:10px;padding:0.6rem 1.2rem;margin-top:1rem;display:inline-block;}
.cd-num{font-family:'Playfair Display',serif!important;font-size:2.5rem!important;color:#E8C96A!important;font-weight:600;line-height:1;}
.cd-lbl{font-size:0.7rem!important;color:rgba(247,243,238,0.7)!important;text-transform:uppercase;letter-spacing:0.1em;}
.sbar{display:flex;background:var(--te);border-radius:0 0 14px 14px;margin-bottom:1.25rem;flex-wrap:wrap;}
.si{flex:1;min-width:80px;padding:0.7rem 0.5rem;text-align:center;border-right:0.5px solid rgba(247,243,238,0.2);}
.si:last-child{border-right:none;}
.sn{font-size:1.3rem!important;color:#F7F3EE!important;display:block;font-weight:600;line-height:1;}
.sl2{font-size:0.62rem!important;color:rgba(247,243,238,0.7)!important;text-transform:uppercase;letter-spacing:0.08em;display:block;margin-top:2px;}
.sh{border-bottom:2px solid var(--pa);padding-bottom:0.6rem;margin-bottom:1rem;}
.sh-t{font-family:'Playfair Display',serif!important;font-size:1.5rem!important;color:var(--td)!important;}
.sh-m{font-size:0.82rem!important;color:var(--sl)!important;}
.sok{background:#D4EDDA;color:#1A6B32!important;padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;display:inline-block;margin-bottom:0.75rem;}
.serr{background:#F8D7DA;color:#721C24!important;padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;display:inline-block;margin-bottom:0.75rem;}
.dc{background:var(--w);border-radius:12px;border:1px solid var(--pa);margin-bottom:0.75rem;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.dh{display:flex;align-items:center;gap:8px;padding:0.6rem 1rem;background:var(--pa);flex-wrap:wrap;}
.dn{background:var(--te);color:#fff!important;font-size:0.7rem;font-weight:700;padding:2px 10px;border-radius:20px;white-space:nowrap;}
.dd{font-size:0.85rem!important;font-weight:600;color:#3D4A5C!important;}
.dc2{font-size:0.75rem!important;color:var(--sl)!important;margin-left:auto;}
.ev{display:flex;gap:10px;padding:10px 1rem;border-bottom:1px solid var(--pa);align-items:flex-start;}
.ev:last-child{border-bottom:none;}
.ev.ab{background:rgba(237,231,220,0.3);}
.ev-t{font-size:0.72rem!important;color:var(--sl)!important;font-weight:600;min-width:42px;padding-top:3px;text-align:right;flex-shrink:0;}
.dot{width:10px;height:10px;border-radius:50%;border:2px solid #E8956D;background:var(--pa);margin-top:4px;flex-shrink:0;}
.dot.hi{background:var(--te);border-color:var(--td);}
.eb{flex:1;min-width:0;}
.et{font-size:0.88rem!important;font-weight:700;color:var(--ink)!important;margin-bottom:2px;word-wrap:break-word;}
.et.star::before{content:'★ ';color:#C9A84C;}
.ed{font-size:0.78rem!important;color:var(--sl)!important;line-height:1.5;word-wrap:break-word;}
.etip{font-size:0.73rem!important;color:var(--td)!important;background:rgba(196,105,58,0.07);border-left:3px solid #E8956D;padding:4px 8px;margin-top:5px;border-radius:0 4px 4px 0;line-height:1.4;}
.acts{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px;align-items:center;}
.tag{display:inline-block;font-size:0.68rem;padding:2px 8px;border-radius:20px;font-weight:600;}
.tr2{background:#E8F0FB;color:#2A5FAC!important;}.tw{background:#EBF5E1;color:#3A6B18!important;}
.tf{background:#FDE8DE;color:#8B3E1E!important;}.tm{background:#F5E8F5;color:#7A3A8C!important;}
.ts{background:#FFF0E0;color:#8B5010!important;}.tb{background:#E0F4EF;color:#0F6E56!important;}
.tsl{background:#EEF0FD;color:#4A50B0!important;}.tbu{background:#FEF3E2;color:#8B5E10!important;}
.tpa{background:#E8F5E8;color:#2A6B2A!important;}.tkt{background:#FCEBEB;color:#A32D2D!important;}
.tgr{background:#D4EDDA;color:#1A6B32!important;}
a.lb{display:inline-block;font-size:0.7rem;padding:3px 9px;border-radius:6px;border:1.5px solid;text-decoration:none!important;font-weight:600;background:var(--w);}
a.bm{border-color:#4285F4;color:#4285F4!important;}a.bk{border-color:#003580;color:#003580!important;}
a.ba{border-color:#FF5A5F;color:#FF5A5F!important;}a.bt{border-color:var(--ol);color:var(--ol)!important;}
a.btr{border-color:#B8000A;color:#B8000A!important;}
.hc{border:1px solid var(--pa);border-radius:12px;padding:1rem;margin-bottom:1rem;background:var(--w);}
.hn{font-family:'Playfair Display',serif!important;font-size:0.95rem!important;color:#3D4A5C!important;margin-bottom:3px;font-weight:600;}
.hm{font-size:0.76rem!important;color:var(--sl)!important;line-height:1.55;margin-bottom:5px;}
.hp{display:inline-block;font-size:0.78rem!important;font-weight:700;background:rgba(107,122,62,0.1);color:var(--ol)!important;padding:2px 10px;border-radius:20px;margin-bottom:7px;}
.tc3{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:9px 12px;margin-bottom:5px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.tr3{font-size:0.86rem!important;font-weight:700;color:#3D4A5C!important;}
.td3{font-size:0.74rem!important;color:var(--sl)!important;}
.tp3{font-size:0.84rem!important;font-weight:700;color:var(--te)!important;margin-left:auto;}
.al{background:rgba(196,105,58,0.08);border:1px solid rgba(196,105,58,0.3);border-radius:9px;padding:0.75rem 0.9rem;font-size:0.79rem!important;color:var(--td)!important;margin-bottom:0.75rem;line-height:1.55;}
.al strong{color:var(--td)!important;}
.alg{background:rgba(107,122,62,0.08);border-color:rgba(107,122,62,0.3);color:var(--ol)!important;}
.alg strong{color:var(--ol)!important;}
.alb{background:#EBF4FF;border-color:#90C4F9;color:#1A4A8A!important;}
.alb strong{color:#1A4A8A!important;}
.rc{background:var(--w);border:1px solid var(--pa);border-left:4px solid;border-radius:0 10px 10px 0;padding:0.85rem 1rem;margin-bottom:0.4rem;}
.rc.urg{border-left-color:var(--te);}.rc.ok{border-left-color:var(--ol);}.rc.done{border-left-color:#1A6B32;background:#F8FFF8;}
.rtitle{font-size:0.88rem!important;font-weight:700;color:var(--ink)!important;}
.rmeta{font-size:0.74rem!important;color:var(--sl)!important;margin:2px 0 5px;}
.bp{background:#FEF3CD;color:#8B6914!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.bc{background:#D4EDDA;color:#1A6B32!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.bpa{background:#CCE5FF;color:#0056B3!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.usaved{font-size:0.72rem!important;color:#0056B3!important;word-break:break-all;}
.ncard{background:var(--cr);border-radius:8px;padding:9px 12px;margin-bottom:6px;border-left:3px solid var(--go);font-size:0.82rem!important;}
.nmeta{font-size:0.68rem!important;color:var(--sl)!important;margin-top:4px;}
.prog-o{background:var(--pa);border-radius:4px;height:7px;overflow:hidden;margin:5px 0;}
.prog-i{height:100%;border-radius:4px;background:var(--te);}
.bta{width:100%;border-collapse:collapse;font-size:0.82rem;}
.bta th{text-align:left;padding:8px 10px;background:var(--pa);color:#3D4A5C!important;font-weight:700;font-size:0.68rem;text-transform:uppercase;}
.bta td{padding:8px 10px;border-bottom:1px solid var(--pa);color:var(--ink)!important;}
.bta tr.tot td{font-weight:700;color:var(--td)!important;border-top:2px solid #E8956D;border-bottom:none;}
.frase-card{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.85rem 1rem;margin-bottom:6px;}
.frase-es{font-size:0.82rem!important;color:var(--sl)!important;margin-bottom:2px;}
.frase-it{font-size:0.95rem!important;font-weight:700;color:var(--ink)!important;margin-bottom:2px;}
.frase-fn{font-size:0.78rem!important;color:var(--te)!important;font-style:italic;}
.check-item{display:flex;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid var(--pa);font-size:0.84rem!important;}
.check-item:last-child{border-bottom:none;}
.clima-card{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.9rem;text-align:center;}
.clima-temp{font-family:'Playfair Display',serif!important;font-size:2rem!important;color:var(--te)!important;font-weight:600;}
.clima-city{font-size:0.78rem!important;color:var(--sl)!important;margin-top:2px;}
.clima-desc{font-size:0.75rem!important;color:var(--ink)!important;margin-top:4px;}
</style>""", unsafe_allow_html=True)
# ── SHEETS ─────────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def get_wb():
    c = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(c).open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets():
    wb = get_wb(); ex = [s.title for s in wb.worksheets()]
    needed = {
        "viaje_reservas": ["id","estado","tipo","url_reserva","confirmacion","monto","notas_int","updated"],
        "viaje_gastos":   ["id","descripcion","categoria","monto","fecha"],
        "viaje_notas":    ["id","texto","tag","autor","fecha"],
        "viaje_checklist":["id","categoria","item","done","updated"],
    }
    out = {}
    for n, h in needed.items():
        if n not in ex:
            ws = wb.add_worksheet(title=n, rows=500, cols=len(h)); ws.append_row(h)
        out[n] = wb.worksheet(n)
    return out

@st.cache_data(ttl=20)
def load_r():
    try: return pd.DataFrame(get_wb().worksheet("viaje_reservas").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=20)
def load_g():
    try: return pd.DataFrame(get_wb().worksheet("viaje_gastos").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=20)
def load_n():
    try: return pd.DataFrame(get_wb().worksheet("viaje_notas").get_all_records())
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def load_chk():
    try: return pd.DataFrame(get_wb().worksheet("viaje_checklist").get_all_records())
    except: return pd.DataFrame()

ALOJ_DESC_MAP = {
    "a01":"Alojamiento Milán","a02":"Alojamiento La Spezia","a03":"Alojamiento Florencia",
    "a04":"Alojamiento Roma","a05":"Alojamiento Nápoles","a06":"Alojamiento Bari",
    "a07":"Alojamiento Venecia","a08":"Alojamiento Zurich",
}

def save_res(rid, estado, tipo, url, conf, monto, notas):
    try:
        ws = ensure_sheets()["viaje_reservas"]
        recs = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [rid, estado, tipo, url, conf, monto, notas, now]
        found = False
        for i, r in enumerate(recs, start=2):
            if r.get("id") == rid:
                ws.update(f"A{i}:H{i}", [row]); found = True; break
        if not found: ws.append_row(row)
        if rid in ALOJ_DESC_MAP:
            ws_g = ensure_sheets()["viaje_gastos"]
            recs_g = ws_g.get_all_records()
            gid = f"res_{rid}"; desc = ALOJ_DESC_MAP[rid]
            monto_float = float(monto) if monto else 0.0
            fecha_corta = now[:5]
            if monto_float > 0:
                updated = False
                for i, r in enumerate(recs_g, start=2):
                    if str(r.get("id")) == gid:
                        ws_g.update(f"A{i}:E{i}", [[gid,desc,"Alojamiento",monto_float,fecha_corta]]); updated = True; break
                if not updated: ws_g.append_row([gid,desc,"Alojamiento",monto_float,fecha_corta])
            else:
                for i, r in enumerate(recs_g, start=2):
                    if str(r.get("id")) == gid: ws_g.delete_rows(i); break
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def toggle_check(cid, current_done):
    try:
        ws = ensure_sheets()["viaje_checklist"]; recs = ws.get_all_records()
        new_done = "0" if str(current_done) == "1" else "1"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        for i, r in enumerate(recs, start=2):
            if str(r.get("id")) == str(cid):
                ws.update(f"E{i}:F{i}", [[new_done, now]]); st.cache_data.clear(); return True
    except: pass
    return False

def init_checklist():
    try:
        ws = ensure_sheets()["viaje_checklist"]
        if len(ws.get_all_records()) > 0: return
        items = [
            ("📄 Documentos","Pasaportes vigentes (vence después de dic 2026)"),
            ("📄 Documentos","Fotocopias de pasaportes (guardar separado del original)"),
            ("📄 Documentos","Seguro de viaje contratado"),
            ("📄 Documentos","Reservas impresas / guardadas offline en el teléfono"),
            ("📄 Documentos","Tarjetas bancarias notificadas para uso internacional"),
            ("💳 Dinero","Euros en efectivo para el primer día (MXP → Milán)"),
            ("💳 Dinero","Francos suizos (CHF) — cambiar en Milán o Venecia"),
            ("💳 Dinero","Revolut o Wise configurada y cargada"),
            ("🔌 Tecnología","Adaptador tipo J para Suiza (diferente al europeo — comprar en Milán)"),
            ("🔌 Tecnología","Power bank cargado"),
            ("🔌 Tecnología","Tarjeta SIM europea o eSIM activada"),
            ("🔌 Tecnología","Maps.me con mapas offline descargados (Italia + Suiza)"),
            ("🔌 Tecnología","App Trenitalia instalada y cuenta creada"),
            ("🔌 Tecnología","App Italo instalada"),
            ("🔌 Tecnología","App SBB instalada (trenes Suiza)"),
            ("🔌 Tecnología","Voucher Vaticano guardado (3 jun 08:30 · Código 2L2N0SMT2JVMU3NOU)"),
            ("🔌 Tecnología","Voucher Coliseo guardado (4 jun 09:00 · Ref. 1386136463)"),
            ("🔌 Tecnología","Ticket Accademia guardado (31 mayo 13:45 · Orden 22515345)"),
            ("🔌 Tecnología","Tickets de tren guardados (IC651 · Italo Z9R56L · Italo UL718U)"),
            ("👗 Ropa","Ropa para iglesias (hombros y rodillas cubiertos — llevar bufanda)"),
            ("👗 Ropa","Zapatillas con suela firme (15 km/día en adoquines)"),
            ("👗 Ropa","Ropa de abrigo para Zurich (puede hacer frío en junio)"),
            ("👗 Ropa","Traje de baño (Cinque Terre + Polignano a Mare)"),
            ("🏥 Salud","Protector solar FPS 50+ (varias unidades — en Italia es caro)"),
            ("🏥 Salud","Medicamentos habituales con receta"),
            ("🏥 Salud","Antidiarreico / antiácido (cambio de dieta)"),
            ("🏥 Salud","Botiquín básico (curitas, ibuprofeno)"),
            ("🎒 Equipaje","Mochila pequeña para excursiones del día"),
            ("🎒 Equipaje","Bolsa impermeable para la playa (Polignano)"),
            ("🎒 Equipaje","Snorkel (Polignano a Mare — agua increíble bajo los acantilados)"),
            ("🎒 Equipaje","Botella de agua reutilizable"),
        ]
        rows = [[f"c{str(i+1).zfill(2)}", cat, item, "0", ""] for i,(cat,item) in enumerate(items)]
        ws.append_rows(rows); st.cache_data.clear()
    except Exception as e: st.warning(f"No se pudo inicializar checklist: {e}")

def add_g(desc, cat, monto):
    try:
        gid = f"g{datetime.now().strftime('%m%d%H%M%S')}"
        ensure_sheets()["viaje_gastos"].append_row([gid,desc,cat,monto,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_g(gid):
    try:
        ws = ensure_sheets()["viaje_gastos"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(gid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

def add_nota(texto, tag, autor):
    try:
        nid = f"n{datetime.now().strftime('%m%d%H%M%S')}"
        ensure_sheets()["viaje_notas"].append_row([nid,texto,tag,autor,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_nota(nid):
    try:
        ws = ensure_sheets()["viaje_notas"]
        for i, r in enumerate(ws.get_all_records(), start=2):
            if str(r.get("id")) == str(nid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass
    return False

# ── CLIMA ───────────────────────────────────────────────────────────────────────
CIUDADES_CLIMA = {
    "Milán":       {"lat":45.46,"lon":9.19, "fecha":"2026-05-25"},
    "Cinque Terre":{"lat":44.15,"lon":9.64, "fecha":"2026-05-27"},
    "Florencia":   {"lat":43.77,"lon":11.25,"fecha":"2026-05-29"},
    "Roma":        {"lat":41.90,"lon":12.49,"fecha":"2026-06-02"},
    "Nápoles":     {"lat":40.85,"lon":14.27,"fecha":"2026-06-06"},
    "Bari":        {"lat":41.12,"lon":16.87,"fecha":"2026-06-07"},
    "Venecia":     {"lat":45.44,"lon":12.33,"fecha":"2026-06-09"},
    "Zurich":      {"lat":47.37,"lon":8.54, "fecha":"2026-06-11"},
}
WMO_CODES = {
    0:"☀️ Despejado",1:"🌤️ Poco nublado",2:"⛅ Parcialmente nublado",3:"☁️ Nublado",
    45:"🌫️ Niebla",51:"🌦️ Llovizna",61:"🌧️ Lluvia leve",63:"🌧️ Lluvia moderada",
    65:"🌧️ Lluvia intensa",80:"🌦️ Chubascos",95:"⛈️ Tormenta",
}

@st.cache_data(ttl=3600)
def get_clima(lat, lon, fecha):
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max"
               f"&timezone=Europe%2FRome&start_date={fecha}&end_date={fecha}")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()["daily"]
            return {"max":round(d["temperature_2m_max"][0]),"min":round(d["temperature_2m_min"][0]),
                    "code":d["weathercode"][0],"rain":d["precipitation_probability_max"][0]}
    except: pass
    return None

# ── MAPA ────────────────────────────────────────────────────────────────────────
RUTA_MAPA = [
    {"city":"Milán",            "lat":45.4654,"lon":9.1859, "dias":"D1–2",          "emoji":"🏛️","color":"#C4693A"},
    {"city":"Cinque Terre",     "lat":44.1461,"lon":9.6439, "dias":"D3–4",          "emoji":"🌊","color":"#6B7A3E"},
    {"city":"Pisa",             "lat":43.7228,"lon":10.4017,"dias":"D5 excursión",  "emoji":"🗼","color":"#C9A84C"},
    {"city":"Florencia",        "lat":43.7696,"lon":11.2558,"dias":"D5–8",          "emoji":"🌸","color":"#C4693A"},
    {"city":"Siena",            "lat":43.3188,"lon":11.3307,"dias":"D8 excursión",  "emoji":"🏰","color":"#C9A84C"},
    {"city":"Roma",             "lat":41.9028,"lon":12.4964,"dias":"D9–12",         "emoji":"🏟️","color":"#6B7A3E"},
    {"city":"Nápoles",          "lat":40.8518,"lon":14.2681,"dias":"D13",           "emoji":"🍕","color":"#C4693A"},
    {"city":"Pompeya",          "lat":40.7497,"lon":14.4990,"dias":"D14 excursión", "emoji":"🌋","color":"#8B3E1E"},
    {"city":"Bari",             "lat":41.1171,"lon":16.8719,"dias":"D14–15",        "emoji":"🦔","color":"#6B7A3E"},
    {"city":"Polignano a Mare", "lat":40.9977,"lon":17.2173,"dias":"D15 excursión", "emoji":"🏖️","color":"#C9A84C"},
    {"city":"Alberobello",      "lat":40.7855,"lon":17.2399,"dias":"D15 excursión", "emoji":"🏠","color":"#C9A84C"},
    {"city":"Venecia",          "lat":45.4408,"lon":12.3155,"dias":"D16–17",        "emoji":"🚤","color":"#C4693A"},
    {"city":"Burano",           "lat":45.4847,"lon":12.4175,"dias":"D17 excursión", "emoji":"🎨","color":"#C9A84C"},
    {"city":"Zurich",           "lat":47.3769,"lon":8.5417, "dias":"D18–20",        "emoji":"🇨🇭","color":"#3D4A5C"},
]

# ── HELPERS ─────────────────────────────────────────────────────────────────────
def M(html): st.markdown(html, unsafe_allow_html=True)

def _ev(hora, hi, titulo, desc, tip="", acts="", alt=False):
    dot   = '<div class="dot hi"></div>' if hi else '<div class="dot"></div>'
    tcls  = 'class="et star"' if hi else 'class="et"'
    acls  = ' ab' if alt else ''
    tip_h = f'<div class="etip">{tip}</div>' if tip else ''
    acts_h= f'<div class="acts">{acts}</div>' if acts else ''
    return (f'<div class="ev{acls}"><div class="ev-t">{hora}</div>{dot}'
            f'<div class="eb"><div {tcls}>{titulo}</div>'
            f'<div class="ed">{desc}</div>{tip_h}{acts_h}</div></div>')

def _card(num, fecha, city, rows_html):
    M(f'<div class="dc"><div class="dh"><span class="dn">{num}</span>'
      f'<span class="dd">{fecha}</span><span class="dc2">{city}</span></div>'
      f'{rows_html}</div>')

def _hotel(nombre, meta, precio, url_b, url_a, url_m):
    bb = f'<a href="{url_b}" target="_blank" class="lb bk">📅 Booking</a>' if url_b else ""
    ba = f'<a href="{url_a}" target="_blank" class="lb ba">🏠 Airbnb</a>'  if url_a else ""
    bm = f'<a href="{url_m}" target="_blank" class="lb bm">📍 Maps</a>'    if url_m else ""
    M(f'<div class="hc"><div class="hn">{nombre}</div><div class="hm">{meta}</div>'
      f'<div class="hp">{precio}</div>'
      f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">{bb}{ba}{bm}</div></div>')

def _tcard(icon, route, detail, price, url):
    M(f'<div class="tc3"><div style="font-size:1.2rem;width:24px;flex-shrink:0">{icon}</div>'
      f'<div style="flex:1;min-width:0"><div class="tr3">{route}</div><div class="td3">{detail}</div></div>'
      f'<div class="tp3">{price}</div>'
      f'<a href="{url}" target="_blank" class="lb btr">🔗 Comprar</a></div>')

def _al(html, extra=""):   M(f'<div class="al {extra}">{html}</div>')
def _ticket_ok(texto):     M(f'<div class="al alg"><strong>✅ TICKET COMPRADO:</strong> {texto}</div>')
def _warn(texto):          M(f'<div class="al" style="background:#FEE2E2;border-color:#B91C1C;color:#B91C1C"><strong>⚠️ ATENCIÓN:</strong> {texto}</div>')
# ══ ITINERARIO — RENDER FUNCTIONS ═════════════════════════════════════════════

def render_milan():
    _hotel("Departamento StayEasy — Airbnb ✅","Corso Como, 9 · Milán · Check-in lun 25 mayo 15:00 · Check-out mié 27 mayo 11:00","Airbnb confirmado · 2 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Corso+Como+9+Milan+Italy")
    _warn("Salida 27 mayo muy temprana (tren 06:10 desde Milano Centrale) — preparar maletas la noche anterior.")
    _card("Día 1","Lunes 25 mayo — Llegada","Milán",
        _ev("10:15",False,"Llegada MXP — Inmigración y aduana","Pasaporte argentino. Calcular 30–45 min en temporada alta. Bajar al andén del Malpensa Express (nivel -1 del aeropuerto).",acts='<span class="tag tr2">🛬 Llegada</span>') +
        _ev("11:30",False,"Malpensa Express → Milano Centrale","52 minutos. Sale cada 30 min. Comprar ticket en máquinas Trenord o app. Validar antes de subir.",acts='<span class="tag tr2">🚄 €13/persona</span><a href="https://www.trenord.it" target="_blank" class="lb btr">Trenord</a>') +
        _ev("13:30",False,"Check-in + almuerzo tranquilo","Zona Isola/Porta Garibaldi. Trattoria local: risotto alla milanese (azafrán) o cotoletta. Menú del giorno = €12–15.",acts='<span class="tag tf">🍝 Risotto alla milanese</span>') +
        _ev("15:00",False,"Siesta obligatoria 2–3 horas","Vienen de 11h de vuelo nocturno. Esta siesta es clave para los días siguientes.") +
        _ev("18:00",True,"Navigli — Alzaia Naviglio Grande","Los canales históricos de Milán. El aperitivo milanese (18–20h): con el precio de una copa (€8–10) viene un buffet gratis — institución local. Mejores bares: Upcycle, El Brellin.",tip="La foto más clásica del canal: ir hacia el puente de Via Corsico.",acts='<span class="tag tw">🚶 Aperitivo gratis</span><a href="https://maps.google.com/?q=Navigli+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:30",False,"Cena en Navigli","Alejarse media cuadra del canal para comer mejor y más barato. Probar: ossobuco alla milanese.",acts='<span class="tag tf">🍷 Ossobuco</span>'))
    _card("Día 2","Martes 26 mayo — Última Cena, Duomo, Shopping","Milán",
        _ev("08:15",True,"LA ÚLTIMA CENA — Santa Maria delle Grazie","El fresco de Leonardo da Vinci (1495–1498). Solo 25 personas cada 15 min exactos. Pintado directamente en la pared del refectorio. Detalle: Judas tiene el salero volcado. Zona Magenta.",tip="⚠️ RESERVA URGENTE en cenacolodavincimilano.vivaticket.com — cupos de mayo se agotan meses antes. Presentarse 10 min antes.",acts='<span class="tag tm">🎨 €15+€2</span><a href="https://cenacolodavincimilano.vivaticket.com" target="_blank" class="lb bt">🎟️ Reservar AHORA</a><a href="https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"Duomo di Milano — terrazas","Tercera catedral más grande del mundo. 135 chapiteles y 3.400 estatuas. Ascensor a las terrazas €7. Vista de Milán y los Alpes en días claros.",acts='<span class="tag tm">⛪ €7 terrazas</span><a href="https://ticket.duomomilano.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Duomo+di+Milano" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Galleria Vittorio Emanuele II + Scala","La galería más antigua de Italia (1877). Ritual del toro: talón en el mosaico central, girar 3 veces — trae suerte al amor. Teatro alla Scala exterior gratis.",acts='<span class="tag tw">🚶 Gratis</span><a href="https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Brera","El barrio más bohemio. Menú del giorno visible en la puerta (Via Fiori Chiari, Via Madonnina): primer + segundo + bebida = €12–15.",acts='<span class="tag tf">🍽️ Menú €12–15</span>') +
        _ev("15:00",True,"Shopping — Corso Buenos Aires","La calle comercial más larga de Italia (2km). Zara, H&M, Bershka, Mango, Benetton, marcas italianas.",acts='<span class="tag ts">🛍️ Shopping</span><a href="https://maps.google.com/?q=Corso+Buenos+Aires+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:00",False,"Castello Sforzesco — exterior","La fortaleza medieval del siglo XV. Patio interior gratis hasta el anochecer. Parco Sempione detrás.",acts='<span class="tag tw">🏰 Gratis</span><a href="https://maps.google.com/?q=Castello+Sforzesco+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:30",False,"Cena + preparar maletas 🧳","MAÑANA: tren IC651 a las 06:10 desde Milano Centrale (PNR M9NTBN). Preparar todo. Dormir a las 22:00.",acts='<span class="tag tsl">🧳 Preparar maletas</span>'))


def render_cinque():
    _ticket_ok("Trenitalia IC651 · Milano Centrale 06:10 → La Spezia Centrale 09:26 · 1ª Clase · Adilson: Coche 1 Asiento 7C · Mirtha: Coche 1 Asiento 7D · PNR: M9NTBN")
    _hotel("Departamento Jessica — Airbnb ✅","Via Napoli, 198 · La Spezia · Check-in mié 27 mayo · Check-out vie 29 mayo 10:00","Airbnb confirmado · 2 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Via+Napoli+198+La+Spezia+Italy")
    _al("<strong>🎫 Cinque Terre Card 2 días:</strong> €29.50/persona. Incluye todos los trenes locales entre los 5 pueblos y los senderos oficiales. Comprar en La Spezia al llegar.", "alb")
    _card("Día 3","Miércoles 27 mayo — Riomaggiore, Manarola, Corniglia","Cinque Terre",
        _ev("09:30",False,"Llegada La Spezia — check-in + Cinque Terre Card","Dejar maletas. Comprar la Card 2 días (€29.50/persona) en InfoParco o taquilla. Desayuno rápido.",acts='<span class="tag tkt">🎫 €29.50 · 2 días</span>') +
        _ev("11:00",True,"★ Riomaggiore — el más fotogénico","El pueblo más al sur. Porto piccolo: barquitas de colores sobre el Mediterráneo. Almuerzo: focaccia con pesto ligurio (el mejor del mundo) + trofie al pesto + vino bianco.",acts='<span class="tag tf">🍃 Pesto original</span><a href="https://maps.google.com/?q=Riomaggiore+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",True,"★ Manarola — el mirador más fotografiado","Casas pastel apiladas sobre los acantilados. Mirador famoso a 5 min al este del pueblo. Plataforma para tirarse al agua (mayo: ~18°C).",tip="La tarde ilumina las fachadas de frente. Ir 30 min antes del sunset.",acts='<span class="tag tw">🌅 Mirador</span><a href="https://maps.google.com/?q=Manarola+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:30",False,"Corniglia — el único pueblo en lo alto","377 escalones (o minibus €2.50). Vista 360°. El más tranquilo. Probar sciacchetrà (vino dulce de uvas pasas).",acts='<span class="tag tw">⛰️ 377 escalones</span><a href="https://maps.google.com/?q=Corniglia+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:00",False,"Tren de vuelta a La Spezia","Cena más económica en La Spezia.",acts='<span class="tag tr2">🚄 Regreso</span>'))
    _card("Día 4","Jueves 28 mayo — Vernazza, senderismo y Monterosso","Cinque Terre",
        _ev("08:00",True,"★ Vernazza — el pueblo más completo","Puerto, iglesia, plaza y Castello Doria (€1.50) — la mejor vista del viaje. 2h para explorarlo. Café en Piazza Marconi mirando al mar.",acts='<span class="tag tm">🏰 Castello €1.50</span><a href="https://maps.google.com/?q=Vernazza+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"★ Senderismo Vernazza → Monterosso (3.5km · 2h)","El sendero más espectacular — viñedos sobre el Mediterráneo. Llevar: agua, protector solar, zapatillas cerradas.",tip="Verificar estado en parconazionale5terre.it antes de salir. Si cerrado, tren directo.",acts='<span class="tag tw">🥾 2h · Sendero</span><a href="https://www.parconazionale5terre.it" target="_blank" class="lb bt">Estado senderos</a>') +
        _ev("13:00",True,"🏖️ Monterosso al Mare — playa y anchoas","El único pueblo con playa de arena real. Reposeras ~€5. Junio: agua ~22°C. Acciughe di Monterosso (anchoas marinadas — la especialidad local).",acts='<span class="tag tw">🏖️ Playa de arena</span><a href="https://maps.google.com/?q=Monterosso+al+Mare" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:30",False,"Tren de regreso — preparar maletas 🧳","Mañana: tren a Florencia desde La Spezia. Comprar en app Trenitalia (La Spezia → Firenze SMN ~08:30). Check-out 10:00.",acts='<span class="tag tsl">🧳 Preparar</span><a href="https://www.trenitalia.com" target="_blank" class="lb btr">Comprar tren</a>'))


def render_florencia():
    _tcard("🚄","La Spezia → Firenze Santa Maria Novella","Intercity · ~2h · Salida ~08:30 · Directo o cambio en Pisa","€15–20","https://www.trenitalia.com")
    _hotel("Departamento Liana — Airbnb ✅","Via Nicola Tagliaferri, 5 · Florencia · Check-in vie 29 mayo 15:00 · Check-out mar 2 junio 11:00","Airbnb confirmado · 4 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Via+Nicola+Tagliaferri+5+Florence+Italy")
    _warn("Salida 02/06: tren Italo Z9R56L a las 09:43 desde Firenze SMN. Desayunar antes y dejar maletas en recepción.")
    _card("Día 5","Viernes 29 mayo — Pisa de excursión","Pisa / Florencia",
        _ev("08:30",False,"Tren Florencia → Pisa Centrale","Regional · 1h · frecuente desde SMN. En Pisa bus LAM Rossa (€1.50) o 20 min a pie hasta la Piazza dei Miracoli.",acts='<span class="tag tr2">🚄 1h · ~€10</span><a href="https://www.trenitalia.com" target="_blank" class="lb btr">Trenitalia</a>') +
        _ev("10:00",True,"★ Torre de Pisa — subida","Piazza dei Miracoli (UNESCO). 294 escalones de mármol blanco. 56m de altura. La inclinación se siente físicamente.",tip="⚠️ Reserva OBLIGATORIA en opapisa.it — llegar 15 min antes del turno reservado.",acts='<span class="tag tm">🗼 Torre €20</span><a href="https://www.opapisa.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Piazza+dei+Miracoli+Pisa" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",False,"Duomo di Pisa + Baptisterio","Románico del siglo XI. El Baptisterio tiene acústica extraordinaria: el custodio canta para demostrarla — no perdérselo. Pase combinado €7.",acts='<span class="tag tm">⛪ Pase €7</span>') +
        _ev("13:00",False,"Almuerzo — Borgo Stretto de Pisa","Cecina (torta de garbanzo, especialidad pisana, €2) y schiacciata con embutidos. Mucho más barato que junto a la Torre.",acts='<span class="tag tf">🫘 Cecina €2</span><a href="https://maps.google.com/?q=Borgo+Stretto+Pisa" target="_blank" class="lb bm">📍 Borgo</a>') +
        _ev("14:30",False,"Camposanto + Lungarni de Pisa","Cementerio medieval con frescos del siglo XIV. Los Lungarni (avenidas sobre el Arno pisano) son tranquilos y sin turistas.",acts='<span class="tag tm">🏛️ €5</span>') +
        _ev("16:30",False,"Tren Pisa → Florencia + Piazzale Michelangelo","Al llegar a Florencia, subir al Piazzale para el atardecer (bus 12 o 13 desde la orilla sur del Arno). Vista panorámica completa.",acts='<span class="tag tw">🌅 Atardecer</span><a href="https://maps.google.com/?q=Piazzale+Michelangelo+Florence" target="_blank" class="lb bm">📍 Maps</a>'))
    _card("Día 6","Sábado 30 mayo — Uffizi + Oltrarno + San Miniato","Florencia",
        _ev("08:30",True,"★ Galería degli Uffizi","El museo de arte renacentista más importante del mundo. 3–4h. Sala de Botticelli (Nascita di Venere + Primavera), Annunciazione de Leonardo, Bacco de Caravaggio, Venere di Urbino de Tiziano.",tip="Reserva OBLIGATORIA en uffizi.it. Sin reserva: 2–3 horas de fila.",acts='<span class="tag tm">🎨 €20+€4</span><a href="https://www.uffizi.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Uffizi+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Oltrarno — lampredotto","Cruzar el Ponte Vecchio. Oltrarno es el barrio más auténtico. Lampredotto (callos de ternera en pan, €4 — el street food típico florentino).",acts='<span class="tag tf">🥩 Lampredotto €4</span>') +
        _ev("14:00",False,"Ponte Vecchio + Piazza della Signoria","Puente más antiguo de Florencia (1345). La Loggia dei Lanzi: Perseo con la testa di Medusa de Cellini y El rapto de las Sabinas de Giambologna — gratis.",acts='<span class="tag tw">🚶 Gratis</span><a href="https://maps.google.com/?q=Ponte+Vecchio+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",True,"★ San Miniato al Monte","La iglesia más antigua y bella de Florencia (siglo XI). Los monjes benedictinos rezan el Oficio Divino en canto gregoriano todos los días a las 17:30. Entrada gratis.",acts='<span class="tag tw">⛪ Gratis · Gregoriano 17:30</span><a href="https://maps.google.com/?q=San+Miniato+al+Monte+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena en Oltrarno","Trattoria Buca Mario (la más antigua de Florencia, 1886) o buscar trat con pizarrón en la puerta.",acts='<span class="tag tf">🍷 Cena Oltrarno</span>'))
    _card("Día 7","Domingo 31 mayo — David de Michelangelo + Palazzo Pitti","Florencia",
        _ev("09:00",True,"★ Palazzo Pitti + Jardines de Boboli","El palacio de los Medici. Galleria Palatina: Rafael (La Velata), Tiziano, Caravaggio. Jardines de Boboli con la Gruta de Buontalenti (1583) — una de las primeras obras manieristas del mundo. €16.",acts='<span class="tag tm">🏰 €16</span><a href="https://maps.google.com/?q=Palazzo+Pitti+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("12:30",False,"Almuerzo — Mercato Centrale (piso superior)","Puestos artesanales. Probar: lampredotto, pasta fresca, ribollita. No el piso inferior — es crudo.",acts='<a href="https://maps.google.com/?q=Mercato+Centrale+Florence" target="_blank" class="lb bm">📍 Mercato</a>') +
        _ev("13:45",True,"★ DAVID DE MICHELANGELO — Accademia ✅ RESERVADO 31 MAYO","El David original (5.17m, mármol de Carrara, 1501–1504). El de la Piazza della Signoria es réplica. También los Prigioni de Michelangelo. Vía Ricasoli 58/60.",tip="⚠️ TICKET COMPRADO · Orden 22515345 · Adilson ID:11 · Mirtha ID:10 · Presentar digital o impreso. Llevar documento. No se admiten mochilas grandes.",acts='<span class="tag tgr">✅ 31 mayo 13:45 · €24</span><a href="https://maps.google.com/?q=Accademia+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:00",True,"★ Cappelle Medicee — tumbas de Michelangelo","Las tumbas con Aurora, Crepúsculo, Día y Noche — las esculturas más expresivas del artista. €9.",acts='<span class="tag tm">🗿 €9</span><a href="https://maps.google.com/?q=Cappelle+Medicee+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Mercato di San Lorenzo + cuero florentino","El mejor cuero de Italia. Verificar autenticidad: acercar llama, el cuero real huele a carne no a plástico.",acts='<span class="tag ts">🛍️ Cuero</span>'))
    _card("Día 8","Lunes 1 junio — Siena + Cúpula de Brunelleschi","Toscana / Florencia",
        _ev("07:30",False,"Bus SENA Florencia → Siena","Desde Autostazione di Firenze (frente a SMN). 1.5h · €9/persona. Sale cada hora.",acts='<span class="tag tbu">🚌 €9 · 1.5h</span><a href="https://maps.google.com/?q=Autostazione+Firenze" target="_blank" class="lb bm">📍 Bus</a>') +
        _ev("09:00",True,"★ Piazza del Campo — la más bella de Italia","Forma de concha, 9 sectores. Torre del Mangia (102m, 400 escalones) — una de las mejores vistas de Toscana. Escenario del Palio di Siena.",acts='<span class="tag tm">🏰 Torre €10</span><a href="https://maps.google.com/?q=Piazza+del+Campo+Siena" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:30",True,"★ Duomo di Siena","El pavimento de mármol con 56 escenas narrativas (únicas en el mundo) y los frescos de Pinturicchio en la Biblioteca Piccolomini. €8.",acts='<span class="tag tm">⛪ €8</span><a href="https://maps.google.com/?q=Siena+Cathedral" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("12:00",False,"Museo Civico — frescos de Lorenzetti","El buen y el mal gobierno (1338): los primeros frescos cívicos de la historia del arte occidental. €10.",acts='<span class="tag tm">🏛️ €10</span>') +
        _ev("13:00",False,"Almuerzo en Siena","Pici all'aglione, pappardelle al cinghiale (jabalí), panforte. Restaurantes en Via di Città.",acts='<span class="tag tf">🍖 Pici + cinghiale</span>') +
        _ev("16:00",False,"Bus de regreso a Florencia","Buses cada hora hasta las 21:00. Cena tranquila en Florencia.") +
        _ev("18:30",True,"★ Cúpula de Brunelleschi — Duomo di Firenze","463 escalones sin ascensor. La cúpula de ladrillo más grande del mundo (1436). Frescos del Juicio Final de Vasari. Vista de Florencia desde la linterna.",tip="Reservar el último turno disponible para menos gente y mejor luz.",acts='<span class="tag tm">⛪ ~€20</span><a href="https://www.ilgrandemuseodelduomo.it" target="_blank" class="lb bt">🎟️ Reservar</a>') +
        _ev("20:30",False,"Última cena en Florencia + preparar maletas 🧳","Mañana: tren Italo Z9R56L a las 09:43 desde Firenze SMN. Check-out 11:00.",acts='<span class="tag tsl">🧳 Preparar maletas</span>'))
def render_roma():
    _ticket_ok("Italo Z9R56L · Firenze S.M. 09:43 → Roma Termini 11:19 · Coche 9 · Asientos 35 y 36")
    _hotel("Departamento Domenico — Airbnb ✅","Via Giovanni Aldini, 3 · Roma · Check-in mar 2 junio 15:00 · Check-out sáb 6 junio 11:00","Airbnb confirmado · 4 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Via+Giovanni+Aldini+3+Rome+Italy")
    _al("<strong>🎾 Pádel:</strong> Padel Nuestro Roma — Día 12 tarde. Centro de Roma. Bullpadel, Siux, Babolat, Head, Star Vie. Pista interior para probar palas.")
    _card("Día 9","Martes 2 junio — Llegada + Trastevere","Roma",
        _ev("11:19",False,"Llegada Roma Termini","Metro Línea A (dirección Battistini) para el centro. Taxi oficial blanco: €15–20. Check-in desde las 15:00.",acts='<span class="tag tr2">🚇 Metro Línea A</span>') +
        _ev("13:00",False,"Almuerzo + check-in","Dejar maletas. Caminar 10 min hacia Prati — evitar restaurantes al lado de Termini.") +
        _ev("16:30",True,"★ Trastevere — primer paseo por Roma","El barrio medieval más pintoresco. Callejuelas adoquinadas, hiedra en las fachadas. La Basílica di Santa Maria in Trastevere (siglo II d.C. — la primera iglesia dedicada a la Virgen en Roma, mosaicos del siglo XII, gratis).",acts='<span class="tag tw">⛪ Gratis</span><a href="https://maps.google.com/?q=Trastevere+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Campo de' Fiori + Piazza Farnese","Campo de' Fiori: la única plaza de Roma sin iglesia. Estatua de Giordano Bruno (quemado aquí en 1600). Piazza Farnese: el palazzo renacentista más monumental de Roma.",acts='<a href="https://maps.google.com/?q=Campo+de+Fiori+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena en Trastevere","Las mejores trattorias de Roma. Probar: cacio e pepe, carbonara (sin nata — la real), gricia. Recomendado: Da Enzo al 29.",acts='<span class="tag tf">🍝 Cacio e pepe</span>'))
    _card("Día 10","Miércoles 3 junio — VATICANO COMPLETO ✅","Roma",
        _ev("08:00",True,"Presentarse en la entrada del Vaticano","Llegar a Viale Vaticano a las 08:00 (30 min antes). Fila exclusiva para visitantes con reserva. Mostrar voucher + documento de identidad al Customer Care Staff.",tip="⚠️ TICKET COMPRADO · Código 2L2N0SMT2JVMU3NOU · Tour guiado español · 3 jun 08:30 · Entrada: CORRIDOIO 2 / PASSAGEWAY 2 · Subir escaleras del fondo izquierdo al desk Visite Guidate.",acts='<span class="tag tgr">✅ 3 jun 08:30 · €80 total</span><a href="https://maps.google.com/?q=Vatican+Museums+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("08:30",True,"★ MUSEOS VATICANOS — Tour Guiado Español ✅","54 galerías. Museo Pio-Clementino (Laocoonte, Apollo del Belvedere), Galleria delle Mappe (40 mapas de Italia siglo XVI), Stanze di Raffaello (La Scuola di Atene), Capilla Sixtina.",tip="Capilla Sixtina: SILENCIO ABSOLUTO. Prohibido fotografiar. Techo: Creación de Adán está en el panel 9 de 12. El Juicio Universal en la pared frontal.",acts='<span class="tag tgr">✅ Confirmado</span>') +
        _ev("12:30",True,"★ Basílica di San Pedro + Cúpula","La basílica más grande del mundo cristiano. La Pietà de Michelangelo (1499, 24 años — primera obra firmada por él). Baldaquino de Bernini (29m de bronce). Cúpula: 551 escalones o ascensor parcial (€8). Colonnato de Bernini (284 columnas en forma de abrazo).",acts='<span class="tag tm">⛪ Gratis · Cúpula €8</span><a href="https://maps.google.com/?q=St+Peters+Basilica+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",False,"Castel Sant'Angelo + Ponte Sant'Angelo","Mausoleo de Adriano (139 d.C.) convertido en fortaleza papal. El Ponte Sant'Angelo con los ángeles de Bernini — uno de los puentes más bellos del mundo. Interior: €14.",acts='<span class="tag tm">🏰 €14</span><a href="https://maps.google.com/?q=Castel+Sant+Angelo+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Barrio Prati — cena tranquila","Pizzería al taglio o trattoria local cerca del Vaticano.",acts='<span class="tag tf">🍕 Prati</span>'))
    _card("Día 11","Jueves 4 junio — COLISEO + Roma Antigua ✅","Roma",
        _ev("08:45",False,"Presentarse en Via delle Terme di Tito 93 (Enjoy Rome)","2 min caminando del Coliseo. Mostrar cupón digital (Ref. 1386136463) + documento. El tour incluye Coliseo, Foro Romano y Palatino con audioguía en español.",tip="⚠️ TICKET COMPRADO · Ref. 1386136463 · 4 junio 09:00 · Llegar 15 min antes = 08:45.",acts='<span class="tag tgr">✅ 4 jun 09:00 · Ref. 1386136463</span><a href="https://maps.google.com/?q=Via+delle+Terme+di+Tito+93+Rome" target="_blank" class="lb bm">📍 Punto encuentro</a>') +
        _ev("09:00",True,"★ COLISEO + FORO ROMANO + MONTE PALATINO ✅","Coliseo (70–80 d.C.): 80.000 espectadores. Los tres niveles de arcos. El hipogeo bajo el piso de arena. Foro Romano: Arco de Tito, Via Sacra. Palatino: la colina donde nació Roma — mejores vistas del Foro. Duración: 3h.",acts='<span class="tag tgr">✅ Confirmado</span>') +
        _ev("13:00",False,"Almuerzo en Testaccio","El barrio gastronómico más auténtico de Roma. Mercato di Testaccio: supplì, pizza al taglio, abbacchio alla romana.",acts='<span class="tag tf">🥙 Testaccio</span><a href="https://maps.google.com/?q=Mercato+Testaccio+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Terme di Caracalla + Circo Massimo","Termas de Caracalla (216 d.C.) — ruinas espectaculares y poco masificadas. Circo Massimo (487m, 250.000+ espectadores): el mayor estadio de la historia humana.",acts='<span class="tag tm">🏛️ Termas €8 · Circo gratis</span><a href="https://maps.google.com/?q=Terme+di+Caracalla+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",True,"★ Buco della Serradura — Aventino","Piazza dei Cavalieri di Malta: mirar por el ojo de la cerradura de la Orden de Malta → la cúpula de San Pedro perfectamente enmarcada por dos setos. Una de las vistas más mágicas de Roma. Gratis.",acts='<span class="tag tw">🔑 Gratis · imperdible</span><a href="https://maps.google.com/?q=Keyhole+View+Rome+Aventine" target="_blank" class="lb bm">📍 Maps</a>'))
    _card("Día 12","Viernes 5 junio — Roma Barroca + Pádel","Roma",
        _ev("09:00",True,"★ Pantheon","El edificio más perfecto de la Antigüedad (125 d.C.). La cúpula de 43.3m: cuando llueve el agua cae por el óculo y escapa por el drenaje romano original. Tumbas de Rafael y Víctor Manuel II. €5.",acts='<span class="tag tm">🏛️ €5</span><a href="https://maps.google.com/?q=Pantheon+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"★ Piazza Navona — Fontana dei Quattro Fiumi","La plaza más barroca de Roma. La Fontana de Bernini (1651): Nilo, Ganges, Danubio y RÍO DE LA PLATA — el único monumento de Roma que alude a América del Sur.",tip="Los cuatro gigantes representan los ríos más importantes de los cuatro continentes conocidos en 1651.",acts='<a href="https://maps.google.com/?q=Piazza+Navona+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",True,"★ Fontana di Trevi","La fuente barroca más grande del mundo (26m × 20m). Ritual: moneda lanzada de espaldas con la mano derecha = regreso a Roma garantizado.",tip="Ir entre 07:00 y 08:00 para encontrarla casi vacía. A mediodía puede ser imposible acercarse.",acts='<a href="https://maps.google.com/?q=Trevi+Fountain+Rome" target="_blank" class="lb bm">📍 Trevi</a>') +
        _ev("12:30",False,"Spanish Steps — Piazza di Spagna","135 escalones (1723). Fontana della Barcaccia de Pietro Bernini abajo. Via Condotti al pie: Gucci, Valentino, Bulgari.",acts='<a href="https://maps.google.com/?q=Spanish+Steps+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:30",False,"Almuerzo + Shopping Via del Corso","2km peatonal: Zara, H&M, Mango, marcas italianas. El Ghetto Ebraico al atardecer: carciofo alla giudìa (alcaucil frito — la especialidad judío-romana).",acts='<span class="tag ts">🛍️ Via del Corso</span>') +
        _ev("17:00",False,"Santa Maria del Popolo — Caravaggio","Piazza del Popolo. Dos capillas con Caravaggio: Conversione di Saulo y Crocifissione di Pietro. Bernini y Bramante también trabajaron aquí. Gratis.",acts='<span class="tag tw">⛪ Gratis · Caravaggio</span><a href="https://maps.google.com/?q=Santa+Maria+del+Popolo+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",True,"🎾 Padel Nuestro Roma","La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head, Nox. Pista interior para probar palas.",acts='<span class="tag tpa">🎾 Pádel</span><a href="https://maps.google.com/?q=Padel+Nuestro+Roma+Italy" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:30",False,"Última cena en Roma","El mejor restaurante que hayan descubierto estos días.",acts='<span class="tag tf">🍷 Última cena Roma</span>'))


def render_napoles():
    _tcard("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Sale cada 30 min · Salida ~11:30 tras check-out","€20–35","https://www.trenitalia.com")
    _hotel("Departamento — Airbnb ✅","Via San Agostino alla Zecca, 4 · Nápoles · Check-in sáb 6 junio 14:00 · Check-out dom 7 junio 10:00","Airbnb confirmado · 1 noche","","https://www.airbnb.com/trips","https://maps.google.com/?q=Via+San+Agostino+alla+Zecca+4+Naples+Italy")
    _al("<strong>🧳 Logística 7 jun:</strong> Check-out 10:00 → dejar maletas en guardaequipajes Napoli Centrale (Kipoint, ~€6/bulto) → Circumvesuviana a Pompeya → regreso ~12:30 → recoger maletas → tren a Bari ~14:00.", "alb")
    _warn("Nápoles: cuidado con los carteristas en zonas turísticas. Guardar el teléfono en bolsillo interno.")
    _card("Día 13","Sábado 6 junio — Llegada + Nápoles histórica","Nápoles",
        _ev("13:00",False,"Llegada Napoli Centrale — check-in","Si el departamento no está listo, dejar maletas y salir a explorar de una.",acts='<a href="https://maps.google.com/?q=Naples+Central+Station" target="_blank" class="lb bm">📍 Centrale</a>') +
        _ev("14:30",True,"★ Spaccanapoli — el corazón de Nápoles","Via San Biagio dei Librai / Via Benedetto Croce: la arteria histórica que cruza Nápoles desde hace 2.500 años. Iglesias barrocas en cada esquina: Santa Chiara, Gesù Nuovo, San Domenico Maggiore.",acts='<a href="https://maps.google.com/?q=Spaccanapoli+Naples" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",True,"★ Cappella Sansevero — Cristo Velato","El Cristo Velato de Sanmartino (1753): la escultura de mármol técnicamente más perfecta del mundo — el velo es de mármol sólido y transmite la forma del cuerpo debajo. No existe ninguna otra igual. €8.",tip="No salteársela bajo ningún concepto. Reservar en museosansevero.it.",acts='<span class="tag tm">🗿 €8</span><a href="https://www.museosansevero.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Cappella+Sansevero+Naples" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"Quartieri Spagnoli — altar de Maradona","El laberinto de callejuelas españolas del siglo XVI. El altar a Diego Maradona en Via Emanuele De Deo — literalmente una deidad local.",acts='<a href="https://maps.google.com/?q=Maradona+Shrine+Naples" target="_blank" class="lb bm">📍 Maradona</a>') +
        _ev("18:00",False,"Castel Nuovo + Porto di Napoli","El Maschio Angioino (1279) con el arco triunfal del siglo XV. Vista al golfo de Nápoles y al Vesubio al atardecer.",acts='<span class="tag tm">🏰 Exterior gratis</span>') +
        _ev("19:30",True,"★ LA PIZZA NAPOLITANA ORIGINAL","Las tres legendarias: L'Antica Pizzeria da Michele (solo Margherita y Marinara, €6–8 — la más auténtica), Pizzeria Sorbillo (favorita de los napolitanos, Via Tribunali), Di Matteo. Horno de leña a 485°C, 90 segundos.",acts='<span class="tag tf">🍕 €6–8</span><a href="https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples" target="_blank" class="lb bm">📍 Da Michele</a><a href="https://maps.google.com/?q=Pizzeria+Sorbillo+Naples" target="_blank" class="lb bm">📍 Sorbillo</a>'))
    _card("Día 14","Domingo 7 junio — POMPEYA de mañana → viaje a Bari","Pompeya / Bari",
        _ev("07:00",True,"Circumvesuviana → Pompei Scavi","Andén subterráneo (-1) de Napoli Centrale. Línea hacia Sorrento. Bajarse en 'Pompei Scavi - Villa dei Misteri'. Sale cada 30 min. Ticket en máquina: €3/persona.",acts='<span class="tag tr2">🚂 €3 · 40 min</span><a href="https://maps.google.com/?q=Pompei+Scavi+station" target="_blank" class="lb bm">📍 Estación</a>') +
        _ev("08:00",True,"★ POMPEYA — ciudad sepultada en 79 d.C.","3h. Imperdibles: Casa dei Vettii (frescos mitológicos), Anfiteatro (70 d.C. — el más antiguo del mundo romano en pie), Thermopolium de Vetutius Placidus (el 'bar' romano con el menú pintado en la barra), moldes humanos en el Granario del Foro, Lupanare. €16.",tip="Llevar agua y sombrero — en junio el sol es muy intenso. No hay sombra en el sitio.",acts='<span class="tag tm">🌋 €16</span><a href="https://maps.google.com/?q=Pompeii+Archaeological+Park" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Tren de vuelta a Nápoles — recoger maletas","~40 min de regreso. Recoger maletas del guardaequipajes Kipoint. Almuerzo rápido en la estación.",acts='<span class="tag tr2">🚂 Regreso</span>') +
        _ev("14:00",False,"Tren Napoli → Bari Centrale","Intercity · ~3h30 · Salida ~14:00. Llegada a Bari ~17:30.",acts='<span class="tag tr2">🚄 ~3h30 · €25–40</span><a href="https://www.trenitalia.com" target="_blank" class="lb btr">Trenitalia</a>') +
        _ev("17:30",False,"Llegada Bari — check-in","Via Melo da Bari, 163. Primera exploración de Bari Vecchia.",acts='<a href="https://maps.google.com/?q=Via+Melo+da+Bari+163+Bari+Italy" target="_blank" class="lb bm">📍 Alojamiento</a>'))


def render_bari():
    _hotel("Departamento — Airbnb ✅","Via Melo da Bari, 163 · Bari · Check-in dom 7 junio 15:00 · Check-out mar 9 junio 10:00","€190 total · 2 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Via+Melo+da+Bari+163+Bari+Italy")
    _ticket_ok("Italo UL718U · Bari C.LE 06:50 → Roma Termini 11:30 · Coche 4 Asientos 5/6 · CONEXIÓN Roma Termini 11:55 → Venezia S.L. 15:55 · Coche 7 Asientos 9/10")
    _warn("CONEXIÓN: solo 25 minutos en Roma Termini entre los dos Italo. No salir de la estación. Ir directo a la pantalla de salidas al llegar.")
    _al("<strong>🏖️ Playas Puglia:</strong> Polignano a Mare (acantilados + agua turquesa, tren 25 min) · Cala Lama Monachile · Cala Paura · Monopoli (arena fina, 30 min). Junio: agua ~24°C.", "alg")
    _card("Día 14b","Domingo 7 junio — Bari Vecchia (tarde/noche)","Bari",
        _ev("19:00",True,"★ Bari Vecchia — el laberinto medieval","El casco histórico fue diseñado como laberinto para confundir invasores sarracenos. Callejuelas tan angostas que a veces solo cabe una persona. Mañana temprano (antes de las 12:00) buscar señoras haciendo orecchiette a mano en las puertas (Via dell'Arco Basso).",acts='<a href="https://maps.google.com/?q=Bari+Vecchia+historic+center" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",True,"Basílica di San Nicola","Una de las más importantes basílicas románicas de Italia (1087–1197). San Nicola — el obispo turco que inspiró la figura de Santa Claus — está enterrado en la cripta. Gratis.",acts='<span class="tag tw">⛪ Gratis</span><a href="https://maps.google.com/?q=Basilica+di+San+Nicola+Bari" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:30",False,"Cena — mariscos del Adriático","Crudo di mare, polpo alla pignata (pulpo guisado), frittura di paranza. Vino Primitivo di Manduria.",acts='<span class="tag tf">🦐 Crudo di mare</span>'))
    _card("Día 15","Lunes 8 junio — Polignano a Mare + Alberobello","Puglia",
        _ev("08:30",False,"Tren Bari → Polignano a Mare","Regional · 25 min · frecuente dirección Brindisi. Estación a 10 min caminando del casco histórico.",acts='<span class="tag tr2">🚄 25 min · ~€3</span><a href="https://www.trenitalia.com" target="_blank" class="lb btr">Trenitalia</a>') +
        _ev("09:00",True,"★ 🏖️ Cala Lama Monachile — LA imagen de Puglia","La cala más fotogénica del Adriático: agua turquesa entre acantilados de caliza blanca. El pueblo medieval cuelga 25m sobre el mar. Playa de guijarros. Junio: ~24°C. Snorkel bajo los acantilados.",tip="Llegar antes de las 10:30 — se satura rápido en temporada alta.",acts='<span class="tag tw">🏖️ Playa</span><a href="https://maps.google.com/?q=Lama+Monachile+Polignano+a+Mare" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:30",False,"Cala Paura + Porto Cavallo — calas secundarias","A 5 min a pie de Lama Monachile. Cala Paura tiene plataformas de roca para zambullidas de 2–3m. Porto Cavallo más pequeña y con menos gente.",acts='<span class="tag tw">🤿 Snorkel</span><a href="https://maps.google.com/?q=Cala+Paura+Polignano+a+Mare" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("12:00",True,"Polignano — almuerzo con vista al mar","Pueblo natal de Domenico Modugno (autor de 'Volare'). Estatua en la Piazza Vittorio Emanuele II. Restaurantes sobre los acantilados — el almuerzo más espectacular del viaje.",acts='<span class="tag tf">🌊 Vista al mar</span><a href="https://maps.google.com/?q=Polignano+a+Mare+historic+center" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:30",False,"Monopoli (opcional — 10 min de tren)","Para playa de arena en lugar de guijarros. Castello Carlo V y catedral barroca.",acts='<span class="tag tr2">🚄 10 min</span><a href="https://maps.google.com/?q=Monopoli+Puglia" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",True,"★ Alberobello — los Trulli UNESCO","Las casas de piedra caliza con techos cónicos (siglo XIV–XVII), únicas en el mundo. Más de 1.500 trulli. Para llegar: tren a Bari (25 min) + FSE desde Bari Sur (~1h30). El barrio Aia Piccola es más tranquilo.",tip="Ir en la tarde para mejor luz. Los trulli iluminados al anochecer son mágicos.",acts='<span class="tag tm">🏠 Trulli UNESCO</span><a href="https://maps.google.com/?q=Alberobello+Trulli" target="_blank" class="lb bm">📍 Maps</a><a href="https://www.fseonline.it" target="_blank" class="lb btr">FSE Trenes</a>') +
        _ev("21:00",False,"Regreso a Bari — preparar maletas 🧳","MAÑANA: Italo UL718U a las 06:50 desde Bari C.LE. Preparar TODO esta noche.",acts='<span class="tag tsl">🧳 Preparar maletas — tren 06:50</span>'))


def render_venecia():
    _ticket_ok("Italo UL718U · Bari C.LE 06:50 → Roma Termini 11:30 · Coche 4 · Asientos 5/6 · Conexión Roma 11:55 → Venezia S.L. 15:55 · Coche 7 · Asientos 9/10")
    _warn("Conexión en Roma Termini: solo 25 minutos. No salir de la estación. Verificar andén de salida en la pantalla al llegar.")
    _hotel("Departamento Matteo — Airbnb ✅","Calle Lionpardo, 1954B · Venecia · Check-in mar 9 junio 15:00 · Check-out jue 11 junio 10:00","Airbnb confirmado · 2 noches","","https://www.airbnb.com/trips","https://maps.google.com/?q=Calle+Lionpardo+1954B+Venice+Italy")
    _al("<strong>⚠️ Mapas en Venecia:</strong> En Venecia no hay calles numeradas normales. Usar Maps.me offline descargado ANTES de llegar.")
    _al("<strong>💶 Tasa turística:</strong> Desde 2024 Venecia cobra €5/persona en días pico de junio. Verificar en comune.venezia.it.", "alb")
    _card("Día 16","Martes 9 junio — Llegada + Venecia clásica","Venecia",
        _ev("15:55",False,"Llegada Venezia Santa Lucia","Comprar pase vaporetto 48h (€35) en la taquilla de la estación.",acts='<span class="tag tb">⛴️ Pase 48h = €35</span><a href="https://actv.avmspa.it" target="_blank" class="lb bt">ACTV</a>') +
        _ev("16:15",True,"★ Gran Canal en vaporetto Línea 1","45 min de palacios del siglo XIV: Ca'd'Oro (el más bello gótico veneciano), Palazzo Grimani, Ca'Rezzonico. El Ponte di Rialto (1591) — el punto más fotogénico. Sentarse en la proa.",acts='<span class="tag tb">🚤 Línea 1</span><a href="https://maps.google.com/?q=Grand+Canal+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",True,"★ Piazza San Marco + Basílica + Campanile","La única plaza de Venecia llamada 'piazza'. Basílica di San Marco (1094): mosaicos de oro estilo bizantino. Campanile (99m): €10. Palazzo Ducale con el Ponte dei Sospiri.",acts='<span class="tag tm">🏛️ Basílica gratis · Campanile €10</span><a href="https://maps.google.com/?q=St+Marks+Basilica+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",True,"★ Perderse sin mapa — la mejor actividad de Venecia","Apagar Google Maps. 118 islas, 160 canales, 400 puentes. Cada calle ciega termina en un canal. Los 'campi' escondidos son los espacios más auténticos.",acts='<span class="tag tw">🗺️ Sin mapa</span>') +
        _ev("20:30",False,"Spritz veneziano en bacaro + cicchetti","El Spritz se inventó en el Véneto. Los bacari tienen cicchetti a €1–2: baccalà mantecato, sarde in saor, nervetti. Zona Cannaregio para los más auténticos.",acts='<span class="tag tf">🍹 Spritz veneziano</span><a href="https://maps.google.com/?q=Cannaregio+Venice" target="_blank" class="lb bm">📍 Cannaregio</a>') +
        _ev("22:00",False,"Góndola nocturna (opcional)","€80 fijos por 30 min / hasta 6 personas. De noche los canales sin turistas y los palacios iluminados son mágicos.",acts='<span class="tag tb">🎭 €80 / góndola entera</span>'))
    _card("Día 17","Miércoles 10 junio — Murano, Burano y Dorsoduro","Venecia",
        _ev("09:00",True,"★ Vaporetto a Murano — isla del cristal soplado","Línea 3 o 4.1 desde Ferrovia. 15 min. Producción de cristal desde 1291. Ver demostración de soplado en vivo en una furnace histórica — gratis en muchas.",tip="Comprar directamente en Murano. Pedir certificado de origen.",acts='<span class="tag tb">⛴️ 15 min</span><a href="https://maps.google.com/?q=Murano+Venice" target="_blank" class="lb bm">📍 Murano</a>') +
        _ev("11:00",True,"★ Burano — la isla más colorida del mundo","45 min de Murano en Línea 12 desde Fondamente Nove. Casas pintadas de colores intensos únicas en el mundo. Ir temprano para verla sin grupos.",acts='<span class="tag tw">🌈 Colores únicos</span><a href="https://maps.google.com/?q=Burano+Venice" target="_blank" class="lb bm">📍 Burano</a>') +
        _ev("13:00",False,"Almuerzo en Burano","Risotto di go (pez de laguna, sabor intenso a mar) — la especialidad local.",acts='<span class="tag tf">🐟 Risotto di go</span>') +
        _ev("15:00",False,"Dorsoduro — Gallerie Accademia + Peggy Guggenheim","Accademia (€12): Bellini, Tiziano, Tintoretto. Peggy Guggenheim (€16): Pollock, Dalí, Kandinsky, Picasso.",acts='<span class="tag tm">🎨 Accademia €12 · Guggenheim €16</span><a href="https://maps.google.com/?q=Dorsoduro+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Campo Santa Margherita — último aperitivo en Italia","El campo más grande y vivo de Venecia. Bares económicos. Último Spritz veneziano del viaje.",acts='<span class="tag tf">🍹 Último Spritz</span>') +
        _ev("20:00",False,"Cena despedida de Italia + preparar maletas 🧳","Mañana: tren EuroCity Venezia → Zürich (~09:00). SENTARSE DEL LADO DERECHO mirando norte para ver los Alpes.",acts='<span class="tag tsl">🧳 Preparar maletas</span><a href="https://www.sbb.ch" target="_blank" class="lb bt">SBB Zürich</a>'))


def render_zurich():
    _tcard("🚄","Venezia S. Lucia → Zürich HB","EuroCity directo · ~4h45 · Alpes por la ventana · Sentarse lado DERECHO mirando norte","€40–60","https://www.sbb.ch")
    _hotel("Hotel Zürich — por confirmar","Zona Langstrasse o Altstadt · Check-in jue 11 junio · Check-out dom 14 junio","~€90–110/noche · 3 noches","https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","","https://maps.google.com/?q=Zurich+Switzerland")
    _warn("VUELO 14/06 LA8799 a las 08:55: estar en ZRH a las 07:00. Tren Zürich HB → Aeropuerto: 10 min, sale cada 10 min desde las 05:30. ALARMA 06:00 sin excepciones.")
    _al("<strong>💱 CHF:</strong> 1 CHF ≈ €1.05. Revolut y Wise funcionan. Precios: café €4–5, almuerzo €20–30, cena €40–60. Presupuestar el doble que Italia.", "alb")
    _card("Día 18","Jueves 11 junio — Llegada + Altstadt","Zürich",
        _ev("15:00",False,"Llegada Zürich HB — check-in","La Bahnhofstrasse empieza en la salida de la estación. Cambio mental: caos italiano → precisión suiza.",acts='<a href="https://maps.google.com/?q=Zurich+Hauptbahnhof" target="_blank" class="lb bm">📍 HB</a>') +
        _ev("15:30",True,"★ Bahnhofstrasse + Lago de Zürich","1.4km de boutiques de lujo y bancos privados. Bürkliplatz sobre el lago. El Zürichsee es perfectamente limpio.",acts='<span class="tag ts">⌚ Rolex · Bulgari</span><a href="https://maps.google.com/?q=Bahnhofstrasse+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",True,"★ Altstadt + Grossmünster","Aquí Huldrych Zwingli comenzó la Reforma Protestante en 1519. Subir las torres (€5) para ver los vitrales de Sigmar Polke (2009) y la vista de Zürich. Barrio Niederdorf: callejuelas medievales.",acts='<span class="tag tm">⛪ Torres €5</span><a href="https://maps.google.com/?q=Grossmunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:30",False,"★ Fraumünster — vitrales de Marc Chagall","Cinco vitrales de Chagall (1970) y rosetón de Giacometti (1945) en edificio románico del siglo IX. Una de las mejores fusiones de arte moderno y arquitectura medieval de Europa. €5.",acts='<span class="tag tm">🎨 Chagall €5</span><a href="https://maps.google.com/?q=Fraumunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena en Niederdorf","Zürcher Geschnetzeltes: ternera con champiñones en crema sobre rösti — el plato nacional de Zürich.",acts='<span class="tag tf">🍖 Geschnetzeltes</span>'))
    _card("Día 19","Viernes 12 junio — Lago + ETH + Fondue","Zürich",
        _ev("09:00",True,"★ Crucero Lago de Zürich","ZSG desde Bürkliplatz. Recorrido corto 1h (€8) o largo 4h hasta Rapperswil (€30) con los Alpes reflejados.",acts='<span class="tag tb">⛵ 1h=€8 · 4h=€30</span><a href="https://www.zsg.ch" target="_blank" class="lb bt">ZSG</a>') +
        _ev("13:00",False,"Almuerzo en el Altstadt","Birchermüesli (el muesli original de Zürich, inventado en 1900) o Rösti con huevo.",acts='<span class="tag tf">🥣 Birchermüesli</span>') +
        _ev("15:00",False,"Polybahn → Terraza ETH Zürich (gratis)","El funicular de 1889 sube al campus donde Einstein estudió y enseñó. La terraza tiene la mejor vista de Zürich, el lago y los Alpes — totalmente gratis.",acts='<span class="tag tw">⛰️ Gratis</span><a href="https://maps.google.com/?q=ETH+Zurich" target="_blank" class="lb bm">📍 ETH</a>') +
        _ev("17:00",False,"St. Peter Kirche","La esfera de reloj de iglesia más grande de Europa (8.7m de diámetro). Visible desde casi cualquier punto del Altstadt.",acts='<a href="https://maps.google.com/?q=St+Peter+Church+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",True,"★ Fondue suiza — Swiss Chuchi","Reitergasse 4. Gruyère + Appenzeller en kirsch. Pan para mojar. Vino blanco valaisano (Fendant). ~€35–45/persona. Reservar con anticipación.",acts='<span class="tag tf">🧀 Fondue</span><a href="https://maps.google.com/?q=Swiss+Chuchi+Zurich" target="_blank" class="lb bm">📍 Maps</a>'))
    _card("Día 20","Sábado 13 junio — Uetliberg + Sprüngli + Despedida","Zürich",
        _ev("09:00",True,"★ Uetliberg — la montaña de Zürich","Tren S10 desde Zürich HB, 20 min, €5.60. 869m. Vista 360°: Zürich, el lago, los Alpes (Jungfrau, Eiger, Matterhorn en días claros). Sendero de bajada a Felsenegg (1.5h, fácil) con vista del lago todo el tiempo.",acts='<span class="tag tw">⛰️ Tren €5.60</span><a href="https://maps.google.com/?q=Uetliberg+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:30",True,"★ Confiserie Sprüngli + Mercado Bürkliplatz","Sprüngli (Paradeplatz, desde 1836): Luxemburgerli (macarons suizos) y Truffes du Jour. Mercado de Bürkliplatz los sábados: artesanías, flores, quesos suizos.",acts='<span class="tag tf">🍫 Chocolates</span><a href="https://maps.google.com/?q=Confiserie+Sprungli+Paradeplatz+Zurich" target="_blank" class="lb bm">📍 Sprüngli</a>') +
        _ev("15:30",False,"Shopping final + preparar maletas 🧳","Via Augustinergasse para recuerdos: chocolates, cuchillos suizos (Victorinox), quesos. Check-in online del vuelo LA8799.",acts='<span class="tag tsl">🧳 Preparar maletas + check-in online</span>') +
        _ev("19:00",True,"★ Última cena del viaje 🥂","Brindar por los 21 días y la luna de miel.",acts='<span class="tag tf">🥂 Despedida</span>') +
        _ev("22:00",False,"🛏️ Dormir — vuelo 08:55 mañana ✈️","ALARMA: 06:00. Tren Zürich HB → ZRH: 10 min desde las 05:30. Estar en ZRH a las 07:00.",tip="⚠️ ALARMA 06:00 SIN EXCEPCIONES.",acts='<span class="tag tsl">✈️ LA8799 · ZRH → MXP 08:55</span>'))


CIUDAD_FN = {
    "🏛️ Milán":        render_milan,
    "🌊 Cinque Terre":  render_cinque,
    "🌸 Florencia":     render_florencia,
    "🏟️ Roma":          render_roma,
    "🍕 Nápoles":       render_napoles,
    "🦔 Bari/Puglia":   render_bari,
    "🚤 Venecia":       render_venecia,
    "🇨🇭 Zurich":       render_zurich,
}
# ── DATOS ESTÁTICOS ────────────────────────────────────────────────────────────

RESERVAS_MUSEOS = [
    {"id":"m03","title":"Museos Vaticanos + Capilla Sixtina (Tour Guiado Español)","city":"Roma",
     "fecha":"3 junio · 08:30 · Código: 2L2N0SMT2JVMU3NOU · Llegar 08:00 a Viale Vaticano · Entrada: CORRIDOIO 2",
     "urgente":False,"url":"https://www.museivaticani.va","maps":"https://maps.google.com/?q=Vatican+Museums+Rome",
     "default_estado":"paid","default_conf":"2L2N0SMT2JVMU3NOU","default_monto":80},
    {"id":"m05","title":"Coliseo + Foro Romano + Palatino (Enjoy Rome · audioguía español)","city":"Roma",
     "fecha":"4 junio · 09:00 · Ref. 1386136463 · Punto encuentro: Via delle Terme di Tito 93 · Llegar 08:45",
     "urgente":False,"url":"https://www.booking.com","maps":"https://maps.google.com/?q=Via+delle+Terme+di+Tito+93+Rome",
     "default_estado":"paid","default_conf":"1386136463","default_monto":0},
    {"id":"m06","title":"David — Galleria dell'Accademia","city":"Florencia",
     "fecha":"31 mayo · 13:45 · Orden: 22515345 · Adilson ID:11 · Mirtha ID:10",
     "urgente":False,"url":"https://www.uffizi.it/en/the-accademia-gallery","maps":"https://maps.google.com/?q=Accademia+Gallery+Florence",
     "default_estado":"paid","default_conf":"22515345","default_monto":24},
    {"id":"m01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15",
     "urgente":True,"url":"https://cenacolodavincimilano.vivaticket.com","maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m04","title":"Torre de Pisa — Subida","city":"Pisa","fecha":"29 mayo",
     "urgente":True,"url":"https://www.opapisa.it","maps":"https://maps.google.com/?q=Torre+di+Pisa",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m07","title":"Galería degli Uffizi","city":"Florencia","fecha":"30 mayo · 08:30",
     "urgente":True,"url":"https://www.uffizi.it","maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m08","title":"Cúpula de Brunelleschi — Duomo Florencia","city":"Florencia","fecha":"1 junio · 18:30",
     "urgente":True,"url":"https://www.ilgrandemuseodelduomo.it","maps":"https://maps.google.com/?q=Florence+Cathedral",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m09","title":"Cappella Sansevero — Cristo Velato","city":"Nápoles","fecha":"6 junio",
     "urgente":True,"url":"https://www.museosansevero.it","maps":"https://maps.google.com/?q=Cappella+Sansevero+Naples",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"5 junio · 15:00",
     "urgente":True,"url":"https://www.galleriaborghese.it","maps":"https://maps.google.com/?q=Galleria+Borghese+Rome",
     "default_estado":"pending","default_conf":"","default_monto":0},
]

RESERVAS_ALOJ = [
    {"id":"a01","city":"Milán","fecha":"25–27 mayo","noches":2,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Corso+Como+9+Milan+Italy"},
    {"id":"a02","city":"La Spezia","fecha":"27–29 mayo","noches":2,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Via+Napoli+198+La+Spezia+Italy"},
    {"id":"a03","city":"Florencia","fecha":"29 mayo–2 junio","noches":4,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Via+Nicola+Tagliaferri+5+Florence+Italy"},
    {"id":"a04","city":"Roma","fecha":"2–6 junio","noches":4,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Via+Giovanni+Aldini+3+Rome+Italy"},
    {"id":"a05","city":"Nápoles","fecha":"6–7 junio","noches":1,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Via+San+Agostino+alla+Zecca+4+Naples+Italy"},
    {"id":"a06","city":"Bari","fecha":"7–9 junio","noches":2,"precio":"€190 total",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Via+Melo+da+Bari+163+Bari+Italy"},
    {"id":"a07","city":"Venecia","fecha":"9–11 junio","noches":2,"precio":"Airbnb confirmado",
     "url_b":"","url_a":"https://www.airbnb.com/trips","maps":"https://maps.google.com/?q=Calle+Lionpardo+1954B+Venice+Italy"},
    {"id":"a08","city":"Zürich","fecha":"11–14 junio","noches":3,"precio":"~€90–110/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
     "url_a":"","maps":"https://maps.google.com/?q=Zurich+Switzerland"},
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · 52 min · sale cada 30 min · Andén -1 aeropuerto","€13/p","https://www.trenord.it"),
    ("🚄✅","Milano Centrale → La Spezia Centrale","IC651 · 06:10→09:26 · 1ª Clase · Adilson 7C · Mirtha 7D · PNR M9NTBN · YA COMPRADO","€53.80 pagado","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · Incluido en Cinque Terre Card (€29.50/2 días)","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Firenze SMN","Intercity · ~2h · Salida ~08:30","€15–20","https://www.trenitalia.com"),
    ("🚄","Firenze ↔ Pisa Centrale","Regional · 1h · Excursión día 5","€9–12","https://www.trenitalia.com"),
    ("🚌","Firenze ↔ Siena","Bus SENA · 1h30 · Desde Autostazione frente a SMN","€9","https://www.tiemmespa.it"),
    ("🚄✅","Firenze SMN → Roma Termini","Italo Z9R56L · 09:43→11:19 · Coche 9 · Asientos 35/36 · YA COMPRADO","€39.80 pagado","https://www.italotreno.it"),
    ("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Salida ~11:30","€20–35","https://www.trenitalia.com"),
    ("🚂","Napoli → Pompei Scavi","Circumvesuviana · 40 min · Andén -1 Napoli Centrale · €3/p","€3/p","https://www.eavsrl.it"),
    ("🚄","Napoli Centrale → Bari Centrale","Intercity · ~3h30 · Salida ~14:00 del 7 jun","€25–40","https://www.trenitalia.com"),
    ("🚄","Bari ↔ Polignano a Mare","Regional · 25 min · Frecuente","€3/p","https://www.trenitalia.com"),
    ("🚌","Bari → Alberobello (FSE)","Ferrovie del Sud Est · ~1h30 · Andén SUR de Bari Centrale","€5/p","https://www.fseonline.it"),
    ("🚄✅","Bari C.LE → Roma Termini","Italo UL718U · 06:50→11:30 · Coche 4 · Asientos 5/6 · YA COMPRADO","","https://www.italotreno.it"),
    ("🚄✅","Roma Termini → Venezia S.L.","Italo UL718U · 11:55→15:55 · Coche 7 · Asientos 9/10 · ⚠️ 25min conexión · YA COMPRADO","€123.80 (Bari→VCE)","https://www.italotreno.it"),
    ("🚤","Vaporetto Venecia 48h","48h=€35 · Línea 1=Gran Canal · Murano (3/4.1) · Burano (Línea 12)","€35","https://actv.avmspa.it"),
    ("🚄","Venezia S.L. → Zürich HB","EuroCity directo · ~4h45 · LADO DERECHO mirando norte · ~09:00","€40–60","https://www.sbb.ch"),
    ("🚄","Zürich HB → Aeropuerto ZRH","SBB · 10 min · sale cada 10 min desde las 05:30","€4","https://www.sbb.ch"),
]

TIPS = [
    ("☕","Café en la barra","Parado = €1.20. Sentado = €3–5. NUNCA pedir cappuccino después del mediodía."),
    ("💧","Agua del grifo","Pedir 'acqua del rubinetto' — gratis. Agua mineral en mesa = €3–5 extra."),
    ("🍽️","Menú del giorno","Primer + segundo + bebida = €12–15. Solo almuerzo. Buscar el pizarrón en la puerta."),
    ("💳","Revolut / Wise","Sin comisiones. En Suiza cambiar a CHF. 1 CHF ≈ €1.05."),
    ("👟","Zapatos (fundamental)","15 km/día en adoquines. Zapatillas de running con amortiguación."),
    ("🕌","Ropa para iglesias","Hombros y rodillas cubiertos. Bufanda liviana para los dos."),
    ("📸","Capilla Sixtina","Prohibido fotografiar — los guardias son muy estrictos. Silencio absoluto."),
    ("🚄","Validar el ticket","SIEMPRE validar antes de subir al tren. Multa sin validar: €50–200."),
    ("🧳","Guardaequipajes Nápoles","Kipoint en Napoli Centrale, ~€6/bulto. Clave para el día de Pompeya."),
    ("🌊","Polignano a Mare","Llegar antes de las 10:30. Llevar snorkel."),
    ("🚤","Venecia sin mapa","Apagar Google Maps y perderse es la mejor actividad de Venecia."),
    ("🧀","Fondue en Zürich","Swiss Chuchi (Reitergasse 4) ~€40/persona. Reservar con anticipación."),
    ("🍫","Sprüngli — Zürich","Los Luxemburgerli y Truffes du Jour: el mejor souvenir comestible del viaje."),
    ("🔌","Enchufe Suiza (TIPO J)","Suiza usa enchufe TIPO J — diferente al italiano. Comprar adaptador en Milán."),
    ("🎾","Pádel Nuestro Roma","Día 12 tarde. Bullpadel, Siux, Babolat. Pista interior para probar palas."),
    ("💶","Coperto en Italia","€1–3 por persona que aparece en la cuenta. Es legal. No es una estafa."),
    ("🍦","Gelato auténtico","Colores apagados + tapado con espátula = artesanal. Fluo + expuesto = industrial."),
    ("📱","Apps esenciales","Trenitalia · Italo · Maps.me offline · TheFork · SBB · Revolut · ACTV."),
]

FRASES_ITALIANO = [
    ("Reservación","¿Tengo una reserva a nombre de...","Ho una prenotazione a nome di...","O-una-pre-no-tah-TSYO-ne-a-NO-me-di"),
    ("Restaurante","La cuenta, por favor","Il conto, per favore","Il-KON-to-per-fa-VO-re"),
    ("Restaurante","¿Tienen menú del día?","Avete il menù del giorno?","A-VE-te-il-me-NU-del-JOR-no"),
    ("Restaurante","Agua del grifo, por favor","Acqua del rubinetto, per favore","A-KUA-del-ru-bi-NET-to"),
    ("Transporte","¿Dónde está la estación?","Dov'è la stazione?","Do-VE-la-sta-TSYO-ne"),
    ("Transporte","Un billete para... por favor","Un biglietto per... per favore","Un-bil-YET-to-per..."),
    ("Transporte","¿A qué hora sale el tren?","A che ora parte il treno?","A-ke-O-ra-PAR-te-il-TRE-no"),
    ("Hotel","Check-in, por favor","Vorrei fare il check-in","Vor-REI-FA-re-il-check-in"),
    ("Hotel","¿A qué hora es el check-out?","A che ora è il check-out?","A-ke-O-ra-e-il-check-out"),
    ("Emergencia","Necesito un médico","Ho bisogno di un medico","O-bi-ZON-yo-di-un-ME-di-ko"),
    ("Emergencia","Llame a la policía","Chiami la polizia","KYA-mi-la-po-LI-tsya"),
    ("Compras","¿Cuánto cuesta?","Quanto costa?","KUAN-to-KOS-ta"),
    ("Compras","Es demasiado caro","È troppo caro","E-TROP-po-KA-ro"),
    ("General","Gracias","Grazie","GRA-tsye"),
    ("General","Por favor","Per favore","Per-fa-VO-re"),
    ("General","Perdón / Disculpe","Scusi","SKU-zi"),
    ("General","No entiendo","Non capisco","Non-ka-PIS-ko"),
    ("General","¿Habla español?","Parla spagnolo?","PAR-la-span-YO-lo"),
]

FRASES_SUIZO = [
    ("General","Buenos días (alemán suizo)","Guete Morge","GUE-te-MOR-gue"),
    ("General","Gracias (alemán)","Danke","DAN-ke"),
    ("General","¿Cuánto cuesta?","Wie viel kostet das?","Vi-FIL-KOS-tet-das"),
    ("Restaurante","La cuenta, por favor","Die Rechnung, bitte","Di-REJ-nung-BI-te"),
    ("General","¿Habla inglés?","Sprechen Sie Englisch?","SHPRE-jen-zi-ENG-lish"),
]
# ── CARGA DE DATOS ──────────────────────────────────────────────────────────────
try:
    df_res=load_r(); df_gas=load_g(); df_notas=load_n(); df_chk=load_chk()
    sheets_ok=True
    init_checklist()
    if len(df_chk)==0: df_chk=load_chk()
except:
    df_res=df_gas=df_notas=df_chk=pd.DataFrame(); sheets_ok=False

def get_rd(rid):
    if df_res.empty or "id" not in df_res.columns: return {}
    r = df_res[df_res["id"]==rid]
    return r.iloc[0].to_dict() if not r.empty else {}

def get_estado(rid, default_estado):
    rd = get_rd(rid)
    return rd.get("estado", default_estado) if rd else default_estado

# ── COUNTDOWN + HERO ───────────────────────────────────────────────────────────
VIAJE_DATE = date(2026, 5, 24)
hoy = date.today()
dias_restantes = (VIAJE_DATE - hoy).days
ok_m = sum(1 for r in RESERVAS_MUSEOS if get_estado(r["id"], r["default_estado"]) in ("confirmed","paid"))
ok_a = sum(1 for r in RESERVAS_ALOJ if get_estado(r["id"], "pending") in ("confirmed","paid"))
total_gas = pd.to_numeric(df_gas["monto"],errors="coerce").fillna(0).sum() if not df_gas.empty and "monto" in df_gas.columns else 0
chk_done  = len(df_chk[df_chk["done"].astype(str)=="1"]) if not df_chk.empty and "done" in df_chk.columns else 0
chk_total = len(df_chk) if not df_chk.empty else 0

if dias_restantes > 0:
    cd_msg = f'<div class="countdown-box"><span class="cd-num">{dias_restantes}</span><div class="cd-lbl">días para el viaje ✈️</div></div>'
elif dias_restantes == 0:
    cd_msg = '<div class="countdown-box"><span class="cd-num">¡HOY!</span><div class="cd-lbl">¡Es el día del viaje! 🎉</div></div>'
else:
    cd_msg = '<div class="countdown-box"><span class="cd-num">🌍</span><div class="cd-lbl">¡Viaje en curso o finalizado!</div></div>'

M(f"""<div class="hero">
  <div style="font-size:1.6rem;letter-spacing:6px;margin-bottom:4px">🇮🇹 🇨🇭</div>
  <div class="htitle">Italia & <em>Zurich</em></div>
  <div class="hsub">Luna de Miel · Mayo–Junio 2026 · Compartido en tiempo real</div>
  <div class="hdates">✈ Sale 24 mayo · IGU &nbsp;·&nbsp; Regresa 14 junio · ZRH</div>
  {cd_msg}
</div>
<div class="sbar">
  <div class="si"><span class="sn">{ok_m}/{len(RESERVAS_MUSEOS)}</span><span class="sl2">Museos ok</span></div>
  <div class="si"><span class="sn">{ok_a}/{len(RESERVAS_ALOJ)}</span><span class="sl2">Hoteles ok</span></div>
  <div class="si"><span class="sn">€{total_gas:,.0f}</span><span class="sl2">Gastado</span></div>
  <div class="si"><span class="sn">{chk_done}/{chk_total}</span><span class="sl2">Checklist</span></div>
  <div class="si"><span class="sn">21</span><span class="sl2">Días totales</span></div>
  <div class="si"><span class="sn">8</span><span class="sl2">Ciudades</span></div>
</div>""")

if sheets_ok:
    M('<span class="sok">🟢 Google Sheets conectado — ambos ven los mismos datos en tiempo real</span>')
else:
    M('<span class="serr">🔴 Sin conexión — verificar credenciales en secrets.toml</span>')

st.write("")

# ── TABS ────────────────────────────────────────────────────────────────────────
tab_vue,tab_itin,tab_mapa,tab_clima,tab_museos,tab_aloj,tab_trans,tab_gas_t,tab_pres,tab_chk_t,tab_frases,tab_tips,tab_notas_t = st.tabs([
    "✈️ Vuelos","🗺️ Itinerario","🌍 Mapa","🌤️ Clima",
    "🎟️ Museos","🏨 Hoteles","🚄 Trenes","💰 Gastos",
    "📊 Presup.","✅ Checklist","🇮🇹 Frases","💡 Tips","📝 Notas"
])

# ══ VUELOS ════════════════════════════════════════════════════════════════════
with tab_vue:
    M('<div class="sh"><div class="sh-t">Vuelos confirmados</div><div class="sh-m">LATAM + Swiss · Foz de Iguazú ↔ Zurich</div></div>')
    M('<div class="dc"><div class="dh"><span class="dn">IDA</span><span class="dd">Domingo 24 mayo 2026 — Foz de Iguazú → Milán</span></div>' +
      _ev("14:50",True,"IGU → São Paulo GRU","LA3879 op. LATAM Brasil · Airbus 320 · 1h 40min",acts='<span class="tag tr2">✈ LA3879 · A320</span>') +
      _ev("16:30",False,"Escala São Paulo Guarulhos (GRU)","Cambio de avión · 1h 30min de conexión",alt=True) +
      _ev("18:00",True,"São Paulo GRU → Milán Malpensa MXP","LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día",acts='<span class="tag tr2">✈ LA8072 · B777</span>') +
      '</div>')
    M('<div class="dc"><div class="dh"><span class="dn">VUELTA</span><span class="dd">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>' +
      _ev("08:55",True,"Zurich ZRH → Milán Malpensa MXP","LA8799 op. Swiss · 55min · Salir al aeropuerto a las 07:00",tip="⚠️ ALARMA 06:00. Tren HB → ZRH: 10 min desde las 05:30. Estar en ZRH a las 07:00.",acts='<span class="tag tr2">✈ LA8799 · Swiss</span>') +
      _ev("09:50",False,"Escala Milán Malpensa (MXP)","Cambio de avión · 3h 10min de conexión",alt=True) +
      _ev("13:00",True,"Milán MXP → São Paulo GRU","LA8073 op. LATAM Brasil · Boeing 773 · 12h",acts='<span class="tag tr2">✈ LA8073 · B777</span>') +
      _ev("20:00",False,"Escala São Paulo Guarulhos (GRU)","Cambio de avión · 2h 20min de conexión",alt=True) +
      _ev("22:20",True,"São Paulo GRU → Foz de Iguazú IGU","LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día",acts='<span class="tag tr2">✈ LA3206 · A321</span>') +
      '</div>')
    _al("<strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno. Primer día tranquilo: guardar equipaje, almuerzo, siesta obligatoria 2–3h, paseo suave al atardecer por Navigli.")

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("", list(CIUDAD_FN.keys()), horizontal=True, label_visibility="collapsed")
    M(f'<div class="sh" style="margin-top:0.75rem"><div class="sh-t">{ciudad_sel}</div></div>')
    CIUDAD_FN[ciudad_sel]()

# ══ MAPA ══════════════════════════════════════════════════════════════════════
with tab_mapa:
    M('<div class="sh"><div class="sh-t">🌍 Ruta completa</div><div class="sh-m">Milán → Cinque Terre → Florencia/Pisa → Roma → Nápoles/Pompeya → Bari/Puglia → Venecia → Zurich</div></div>')
    m = folium.Map(location=[44.5, 11.5], zoom_start=5, tiles="CartoDB positron")
    coords = [(c["lat"], c["lon"]) for c in RUTA_MAPA]
    folium.PolyLine(coords, color="#C4693A", weight=3, opacity=0.7, dash_array="8 4").add_to(m)
    for c in RUTA_MAPA:
        popup_html = f'<div style="font-family:sans-serif;min-width:130px"><strong>{c["emoji"]} {c["city"]}</strong><br><span style="color:#6B7A8D;font-size:0.78rem">{c["dias"]}</span></div>'
        folium.CircleMarker(location=[c["lat"],c["lon"]],
            radius=10 if "excursión" not in c["dias"] else 7,
            color=c["color"],fill=True,fill_color=c["color"],fill_opacity=0.9,
            popup=folium.Popup(popup_html,max_width=180),
            tooltip=f'{c["emoji"]} {c["city"]} · {c["dias"]}').add_to(m)
        if "excursión" not in c["dias"]:
            folium.Marker(location=[c["lat"]+0.15,c["lon"]],
                icon=folium.DivIcon(
                    html=f'<div style="font-size:0.62rem;font-weight:700;color:{c["color"]};white-space:nowrap;background:white;padding:1px 4px;border-radius:4px;border:1px solid {c["color"]}">{c["city"]}</div>',
                    icon_size=(80,20),icon_anchor=(40,10))).add_to(m)
    st_folium(m, width=None, height=500, returned_objects=[])

# ══ CLIMA ═════════════════════════════════════════════════════════════════════
with tab_clima:
    M('<div class="sh"><div class="sh-t">🌤️ Clima durante el viaje</div><div class="sh-m">Pronóstico para la fecha de llegada a cada ciudad · API Open-Meteo</div></div>')
    _al("<strong>ℹ️</strong> A medida que se acerque la fecha, los datos serán más precisos. Las temperaturas de mayo/junio en Italia son ideales: 22–28°C.")
    cols = st.columns(4)
    for i,(nombre,datos) in enumerate(CIUDADES_CLIMA.items()):
        with cols[i%4]:
            clima = get_clima(datos["lat"],datos["lon"],datos["fecha"])
            if clima:
                desc = WMO_CODES.get(clima["code"],"🌤️")
                icon = desc.split()[0]; texto = " ".join(desc.split()[1:])
                rain_h = f'<div style="font-size:0.7rem;color:#4285F4;margin-top:3px">Lluvia: {clima["rain"]}%</div>' if clima["rain"] else ""
                M(f'<div class="clima-card"><div style="font-size:1.4rem">{icon}</div><div class="clima-temp">{clima["max"]}°</div><div style="font-size:0.72rem;color:#6B7A8D">Mín {clima["min"]}° · Máx {clima["max"]}°C</div><div class="clima-city"><strong>{nombre}</strong><br>{datos["fecha"]}</div><div class="clima-desc">{texto}</div>{rain_h}</div>')
            else:
                M(f'<div class="clima-card"><div style="font-size:1.4rem">🌤️</div><div class="clima-city"><strong>{nombre}</strong><br>{datos["fecha"]}</div><div style="font-size:0.72rem;color:#6B7A8D;margin-top:4px">Disponible próximamente</div></div>')
            st.write("")

# ══ MUSEOS ════════════════════════════════════════════════════════════════════
with tab_museos:
    M('<div class="sh"><div class="sh-t">🎟️ Museos y Entradas</div><div class="sh-m">✅ Ya comprados · ⚠️ Gestionar URGENTE</div></div>')
    _al("<strong>✅ Ya comprados:</strong> Vaticano (3 jun 08:30) · Coliseo Enjoy Rome (4 jun 09:00) · Accademia/David (31 mayo 13:45).", "alg")
    _al("<strong>⚠️ Urgentes pendientes:</strong> La Última Cena (Milán) · Uffizi · Cúpula Brunelleschi · Sansevero/Cristo Velato · Galería Borghese.")
    for r in RESERVAS_MUSEOS:
        rd = get_rd(r["id"])
        ea = rd.get("estado", r["default_estado"]) if rd else r["default_estado"]
        conf_saved = rd.get("confirmacion", r["default_conf"]) if rd else r["default_conf"]
        monto_saved = float(rd.get("monto", r["default_monto"]) or r["default_monto"]) if rd else float(r["default_monto"])
        notas_saved = rd.get("notas_int","") if rd else ""
        bl = {"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll = {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        cc = "done" if ea=="paid" else ("urg" if r["urgente"] else "ok")
        conf_html = f'<div style="font-size:0.72rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:2px 8px;border-radius:8px;margin-top:4px;display:inline-block">✓ {conf_saved}</div>' if conf_saved else ""
        M(f'<div class="rc {cc}"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px"><span style="font-size:0.68rem;padding:1px 7px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span><span class="rtitle">{"⚠️ " if r["urgente"] else ""}{"✅ " if ea=="paid" else ""}{r["title"]}</span><span class="{bl}">{ll}</span></div><div class="rmeta">📅 {r["fecha"]}</div>{conf_html}<div style="margin-top:6px"><a href="{r["url"]}" target="_blank" class="lb bt">🔗 Ir a reservar</a> <a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a></div></div>')
        if ea != "paid":
            with st.form(key=f"fm_{r['id']}"):
                c1,c2,c3 = st.columns([2,2,1])
                with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"se_{r['id']}")
                with c2: nc=st.text_input("N° confirmación",value=conf_saved,key=f"ce_{r['id']}",placeholder="ej. ABC123456")
                with c3: nm=st.number_input("€",value=monto_saved,min_value=0.0,step=1.0,key=f"me_{r['id']}")
                nn=st.text_area("Notas",value=notas_saved,key=f"ne_{r['id']}",height=50)
                if st.form_submit_button("💾 Guardar",use_container_width=True):
                    if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn): st.success("✅ Guardado"); st.rerun()
        else:
            with st.expander("✏️ Editar si es necesario"):
                with st.form(key=f"fm_edit_{r['id']}"):
                    c1,c2,c3 = st.columns([2,2,1])
                    with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"spe_{r['id']}")
                    with c2: nc=st.text_input("N° confirmación",value=conf_saved,key=f"cpe_{r['id']}")
                    with c3: nm=st.number_input("€",value=monto_saved,min_value=0.0,step=1.0,key=f"mpe_{r['id']}")
                    nn=st.text_area("Notas",value=notas_saved,key=f"npe_{r['id']}",height=50)
                    if st.form_submit_button("💾 Actualizar",use_container_width=True):
                        if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn): st.success("✅ Actualizado"); st.rerun()
        st.write("")

# ══ ALOJAMIENTOS ══════════════════════════════════════════════════════════════
with tab_aloj:
    M('<div class="sh"><div class="sh-t">🏨 Alojamientos</div><div class="sh-m">Airbnb confirmados · Cargá la URL · Tu pareja la ve al instante</div></div>')
    _al("<strong>💰 Sincronización automática:</strong> Al guardar el monto, se refleja en el Tracker de Gastos. No hace falta cargarlo dos veces.", "alg")
    for r in RESERVAS_ALOJ:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending") if rd else "pending"
        tipo_saved=str(rd.get("tipo","")) if rd else ""
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva","")) if rd else ""
        uh=f'<div class="usaved">🔗 {us[:70]}{"..." if len(us)>70 else ""}</div>' if us else ""
        tipo_html=f'<span style="font-size:0.68rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:1px 7px;border-radius:20px">{tipo_saved}</span>' if tipo_saved else ""
        ba_html = f'<a href="{r["url_a"]}" target="_blank" class="lb ba">🏠 Airbnb</a>' if r["url_a"] else ""
        bb_html = f'<a href="{r["url_b"]}" target="_blank" class="lb bk">📅 Booking</a>' if r.get("url_b") else ""
        try: monto_actual = float(rd.get("monto",0) or 0) if rd else 0
        except: monto_actual = 0
        monto_html = f'<span style="font-size:0.78rem;font-weight:700;color:#1A6B32;background:rgba(107,122,62,0.1);padding:2px 10px;border-radius:20px;margin-left:6px">€{monto_actual:,.0f} pagado</span>' if monto_actual > 0 else ""
        M(f'<div class="rc ok"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px"><span class="rtitle">🏨 {r["city"]} — {r["noches"]} noches</span><span class="{bl}">{ll}</span>{tipo_html}{monto_html}</div><div class="rmeta">📅 {r["fecha"]} · ~{r["precio"]}</div>{uh}<div style="margin-top:6px">{bb_html} {ba_html} <a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a></div></div>')
        with st.form(key=f"fa_{r['id']}"):
            c1,c2=st.columns(2)
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"sa_{r['id']}")
            with c2: tipo=st.selectbox("Reservado en",["","Airbnb","Booking.com","Directo / Otro"],index=["","Airbnb","Booking.com","Directo / Otro"].index(tipo_saved) if tipo_saved in ["","Airbnb","Booking.com","Directo / Otro"] else 0,key=f"ta_{r['id']}")
            nu=st.text_input("🔗 URL de la reserva",value=us,key=f"ua_{r['id']}",placeholder="Ej: https://www.airbnb.com/trips/v1/XXXXXXX")
            c3,c4=st.columns(2)
            with c3: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","") if rd else ""),key=f"ca_{r['id']}")
            try: _mv = float(rd.get("monto",0) or 0) if rd else 0.0
            except: _mv = 0.0
            with c4: nm=st.number_input("Monto total €",value=_mv,min_value=0.0,step=1.0,key=f"ma_{r['id']}")
            nn=st.text_area("Notas",value=str(rd.get("notas_int","") if rd else ""),key=f"na_{r['id']}",height=50)
            if st.form_submit_button("💾 Guardar — tu pareja lo ve al instante",use_container_width=True):
                if save_res(r["id"],ne,tipo,nu,nc,nm,nn): st.success("✅ Guardado"); st.rerun()
        st.write("")

# ══ TRANSPORTES ══════════════════════════════════════════════════════════════
with tab_trans:
    M('<div class="sh"><div class="sh-t">🚄 Transportes</div><div class="sh-m">En orden cronológico · ✅ ya comprados · Links de compra</div></div>')
    _al("<strong>💡</strong> Los marcados ✅ ya están pagados. El resto comprar cuanto antes — el precio sube cerca de la fecha.", "alg")
    for icon,route,detail,price,url in TRANSPORTES:
        _tcard(icon,route,detail,price,url)

# ══ GASTOS ════════════════════════════════════════════════════════════════════
with tab_gas_t:
    M('<div class="sh"><div class="sh-t">💰 Tracker de Gastos</div><div class="sh-m">Los alojamientos se sincronizan automáticamente</div></div>')
    PRES=4500.0
    cats={"Alojamiento":0,"Transporte":0,"Entradas":0,"Comidas":0,"Otros":0}
    if not df_gas.empty and "monto" in df_gas.columns and "categoria" in df_gas.columns:
        for _,rg in df_gas.iterrows():
            try: cats[rg.get("categoria","Otros")]=cats.get(rg.get("categoria","Otros"),0)+float(rg["monto"])
            except: pass
    tg=sum(cats.values()); pct=min(100,int(tg/PRES*100))
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("💶 Total",f"€{tg:,.0f}",f"{pct}%")
    c2.metric("🏨 Aloj.",f"€{cats['Alojamiento']:,.0f}")
    c3.metric("🚄 Trans.",f"€{cats['Transporte']:,.0f}")
    c4.metric("🎟️ Entradas",f"€{cats['Entradas']:,.0f}")
    c5.metric("🍽️ Comidas",f"€{cats['Comidas']:,.0f}")
    M(f'<div class="prog-o"><div class="prog-i" style="width:{pct}%"></div></div><div style="font-size:0.72rem;color:#6B7A8D;margin-top:3px">€{tg:,.0f} de €{PRES:,.0f} presupuestados ({pct}%)</div>')
    st.write("")
    with st.form("fg"):
        cd,cc2,cm=st.columns([3,2,1])
        with cd: gd=st.text_input("Descripción",placeholder="ej. Entradas Uffizi")
        with cc2: gc=st.selectbox("Categoría",["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        with cm: gm=st.number_input("€",min_value=0.0,step=1.0)
        if st.form_submit_button("➕ Agregar gasto",use_container_width=True):
            if gd.strip() and gm>0:
                if add_g(gd.strip(),gc,gm): st.success("Agregado ✓"); st.rerun()
            else: st.warning("Completá descripción y monto")
    if not df_gas.empty and "descripcion" in df_gas.columns:
        st.write(""); st.markdown("**Historial completo**")
        df_s=df_gas[["id","descripcion","categoria","monto","fecha"]].copy()
        df_s["monto"]=pd.to_numeric(df_s["monto"],errors="coerce").map("€{:,.0f}".format)
        st.dataframe(df_s.drop("id",axis=1),use_container_width=True,hide_index=True)
        di=st.text_input("ID a eliminar (NO eliminar los res_XXX)",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar") and di:
            if di.strip().startswith("res_"): st.warning("⚠️ Los gastos de alojamiento se gestionan desde la pestaña Hoteles.")
            else:
                if del_g(di.strip()): st.success("Eliminado ✓"); st.rerun()

# ══ PRESUPUESTO ══════════════════════════════════════════════════════════════
with tab_pres:
    M('<div class="sh"><div class="sh-t">📊 Presupuesto estimado</div><div class="sh-m">Para 2 personas · 21 días · Sin vuelos</div></div>')
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🏨 Alojamiento","~€1.790","21 noches · €85 prom.")
    c2.metric("🚄 Transportes","~€600","Trenes · ferries · vaporetti")
    c3.metric("🎟️ Entradas","~€400","Para 2 personas")
    c4.metric("🍽️ Comidas","~€1.300","€62/día para 2")
    st.write("")
    c5,c6=st.columns(2)
    c5.metric("🛍️ Extras","~€450","Compras · pádel · imprevistos")
    c6.metric("💶 TOTAL","~€4.540","Para 2 · sin vuelos")
    st.write("")
    PRES_FILAS=[
        ("Milán","2","€80","€160"),("La Spezia/CT","2","€75","€150"),
        ("Florencia","4","€100","€400"),("Roma","4","€88","€352"),
        ("Nápoles","1","€80","€80"),("Bari","2","€95","€190"),
        ("Venecia","2","€110","€220"),("Zürich","3","€145","€435"),
        ("TOTAL","20","~€100","~€1.987"),
    ]
    rows="".join(f'<tr{"class=tot" if c=="TOTAL" else ""}><td>{c}</td><td style="text-align:center">{n}</td><td style="text-align:center">{p}</td><td style="text-align:center;font-weight:700">{t}</td></tr>' for c,n,p,t in PRES_FILAS)
    M(f'<div style="border:1px solid #EDE7DC;border-radius:10px;overflow:hidden"><table class="bta"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th><th style="text-align:center">€/noche</th><th style="text-align:center">Total</th></tr></thead><tbody>{rows}</tbody></table></div>')
    st.write("")
    st.markdown("**Calculadora de coperto**")
    col1,col2,col3=st.columns(3)
    with col1: cuenta=st.number_input("Cuenta €",min_value=0.0,step=0.50,value=40.0)
    with col2: coperto=st.number_input("Coperto €/persona",min_value=0.0,step=0.50,value=2.0)
    with col3: personas=st.number_input("Personas",min_value=1,max_value=10,value=2)
    M(f'<div class="al alg" style="text-align:center"><strong>Total a pagar: €{cuenta+(coperto*personas):.2f}</strong> (cuenta €{cuenta:.2f} + coperto €{coperto*personas:.2f})</div>')

# ══ CHECKLIST ════════════════════════════════════════════════════════════════
with tab_chk_t:
    M('<div class="sh"><div class="sh-t">✅ Checklist Pre-Viaje</div><div class="sh-m">Marcá cada item — ambos ven el progreso en tiempo real</div></div>')
    if not df_chk.empty and "item" in df_chk.columns:
        done_count=len(df_chk[df_chk["done"].astype(str)=="1"])
        total_count=len(df_chk)
        pct_chk=int(done_count/total_count*100) if total_count>0 else 0
        M(f'<div class="prog-o"><div class="prog-i" style="width:{pct_chk}%"></div></div><div style="font-size:0.78rem;color:#6B7A8D;margin:4px 0 1rem">{done_count} de {total_count} completados ({pct_chk}%)</div>')
        for cat in df_chk["categoria"].unique():
            items=df_chk[df_chk["categoria"]==cat]
            cat_done=len(items[items["done"].astype(str)=="1"])
            M(f'<div style="font-size:0.78rem;font-weight:700;color:#3D4A5C;margin:1rem 0 4px">{cat} ({cat_done}/{len(items)})</div><div class="dc" style="margin-bottom:0.5rem">')
            for _,item in items.iterrows():
                is_done=str(item.get("done","0"))=="1"
                icon="✅" if is_done else "⬜"
                style="opacity:0.5;text-decoration:line-through" if is_done else ""
                M(f'<div class="check-item" style="{style}">{icon} {item.get("item","")}</div>')
                if st.button(f"{'↩️ Desmarcar' if is_done else '✅ Marcar'}",key=f"chk_{item.get('id','')}"):
                    if toggle_check(str(item.get("id","")),item.get("done","0")): st.rerun()
            M('</div>')
    else:
        st.info("Cargando checklist...")
        if st.button("🔄 Inicializar checklist"): init_checklist(); st.rerun()

# ══ FRASES ════════════════════════════════════════════════════════════════════
with tab_frases:
    M('<div class="sh"><div class="sh-t">🇮🇹 Frases esenciales</div><div class="sh-m">Las frases que realmente usarás · Con pronunciación fonética · Funciona sin internet</div></div>')
    col_it,col_ch=st.columns([2,1])
    with col_it:
        M('<div style="font-size:1rem;font-weight:700;color:#C4693A;margin-bottom:0.75rem">🇮🇹 Italiano</div>')
        cats_it=list(dict.fromkeys(f[0] for f in FRASES_ITALIANO))
        cat_sel=st.radio("Categoría",cats_it,horizontal=True,label_visibility="collapsed")
        for cat,es,it,fon in FRASES_ITALIANO:
            if cat==cat_sel:
                M(f'<div class="frase-card"><div class="frase-es">{es}</div><div class="frase-it">{it}</div><div class="frase-fn">🔊 {fon}</div></div>')
    with col_ch:
        M('<div style="font-size:1rem;font-weight:700;color:#3D4A5C;margin-bottom:0.75rem">🇨🇭 Alemán suizo</div>')
        for _,es,de,fon in FRASES_SUIZO:
            M(f'<div class="frase-card"><div class="frase-es">{es}</div><div class="frase-it">{de}</div><div class="frase-fn">🔊 {fon}</div></div>')

# ══ TIPS ══════════════════════════════════════════════════════════════════════
with tab_tips:
    M('<div class="sh"><div class="sh-t">💡 Tips esenciales</div><div class="sh-m">Lo que marca la diferencia entre turista y viajero</div></div>')
    cols=st.columns(3)
    for i,(icon,title,text) in enumerate(TIPS):
        with cols[i%3]:
            M(f'<div style="background:#fff;border:1px solid #EDE7DC;border-radius:10px;padding:0.85rem;margin-bottom:0.6rem"><div style="font-size:1.3rem;margin-bottom:4px">{icon}</div><div style="font-size:0.84rem;font-weight:700;color:#3D4A5C;margin-bottom:3px">{title}</div><div style="font-size:0.75rem;color:#6B7A8D;line-height:1.55">{text}</div></div>')
            st.write("")

# ══ NOTAS ════════════════════════════════════════════════════════════════════
with tab_notas_t:
    M('<div class="sh"><div class="sh-t">📝 Notas compartidas</div><div class="sh-m">Cualquiera puede publicar — el otro lo ve al instante</div></div>')
    with st.form("fn"):
        nt=st.text_area("Nueva nota",height=80,placeholder="Escribí algo — tu pareja lo ve al instante...")
        ct,ca=st.columns(2)
        with ct: ntag=st.selectbox("Categoría",["💡 Idea","⚠️ Importante","🍽️ Restaurante","🏨 Hotel","🎾 Pádel","🛍️ Compras","📝 General"])
        with ca: naut=st.selectbox("Quién",["Adilson","Mirtha"])
        if st.form_submit_button("📤 Publicar nota",use_container_width=True):
            if nt.strip():
                if add_nota(nt.strip(),ntag,naut): st.success("Publicado ✓"); st.rerun()
            else: st.warning("Escribí algo primero")
    st.write("")
    if not df_notas.empty and "texto" in df_notas.columns:
        for _,rn in df_notas.iloc[::-1].iterrows():
            M(f'<div class="ncard"><strong>{rn.get("tag","📝")}</strong> · <em style="color:#6B7A8D">{rn.get("autor","")}</em><br>{rn.get("texto","")}<div class="nmeta">🕐 {rn.get("fecha","")}</div></div>')
            if st.button("🗑️ Borrar",key=f"dn_{rn.get('id','')}"):
                if del_nota(str(rn.get("id",""))): st.rerun()
    else: st.info("Aún no hay notas. ¡Publicá la primera!")
