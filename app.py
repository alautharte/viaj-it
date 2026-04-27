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
div[data-testid="stRadio"]>div>label{background:var(--pa)!important;padding:6px 12px!important;border-radius:20px!important;border:1.5px solid transparent!important;}
div[data-testid="stRadio"]>div>label p{color:var(--ink)!important;font-weight:600!important;font-size:0.8rem!important;margin:0!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"]{background:var(--te)!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"] p{color:var(--w)!important;}
div[data-testid="stRadio"] div[role="radiogroup"] label>div:first-child{display:none!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:#ffffff!important;color:#1A1A2E!important;border:1px solid #EDE7DC!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#ffffff!important;color:#1A1A2E!important;}
[data-baseweb="base-input"]{background:#ffffff!important;}
[data-baseweb="base-input"] input,[data-baseweb="base-input"] textarea{background:#ffffff!important;color:#1A1A2E!important;}
input[type="number"],input[type="text"],textarea{background:#ffffff!important;color:#1A1A2E!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stNumberInput label{color:#3D4A5C!important;font-size:0.82rem!important;font-weight:500!important;}
.stSelectbox>div>div,[data-baseweb="select"],[data-baseweb="select"] *{background:#ffffff!important;color:#1A1A2E!important;}
.stButton>button{background:var(--te)!important;color:var(--w)!important;border:none!important;border-radius:8px!important;font-weight:600!important;}
.stButton>button:hover{background:var(--td)!important;}
[data-testid="stMetric"]{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.75rem!important;}
[data-testid="stMetricLabel"] p{color:var(--sl)!important;font-size:0.75rem!important;}
[data-testid="stMetricValue"]{color:var(--td)!important;}
[data-testid="stMetricDelta"]{color:var(--ol)!important;}
[data-testid="stExpander"]{border:1px solid var(--pa)!important;border-radius:10px!important;background:var(--w)!important;}
[data-testid="stExpander"] summary p{color:var(--ink)!important;font-weight:600!important;}
@media(max-width:640px){[data-testid="block-container"]{padding:0.5rem!important;}}
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
.sh-m{font-size:0.82rem!important;color:var(--sl)!important;margin-top:1px;}
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
.rc.urg{border-left-color:var(--te);}.rc.ok{border-left-color:var(--ol);}
.rc.done{border-left-color:#1A6B32;background:#F8FFF8;}
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

# Mapa de descripciones para sincronización automática de alojamientos → gastos
ALOJ_DESC_MAP = {
    "a01": "Alojamiento Milán",
    "a02": "Alojamiento La Spezia",
    "a03": "Alojamiento Florencia",
    "a04": "Alojamiento Roma",
    "a05": "Alojamiento Nápoles",
    "a06": "Alojamiento Costa Amalfi",
    "a07": "Alojamiento Venecia",
    "a08": "Alojamiento Zurich",
}

def save_res(rid, estado, tipo, url, conf, monto, notas):
    """
    Guarda una reserva en viaje_reservas.
    Si el rid es de alojamiento (a01–a08) y tiene monto > 0,
    sincroniza automáticamente en viaje_gastos con id 'res_{rid}'.
    """
    try:
        ws = ensure_sheets()["viaje_reservas"]
        recs = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = [rid, estado, tipo, url, conf, monto, notas, now]

        # Actualizar o insertar en viaje_reservas
        found = False
        for i, r in enumerate(recs, start=2):
            if r.get("id") == rid:
                ws.update(f"A{i}:H{i}", [row])
                found = True
                break
        if not found:
            ws.append_row(row)

        # ── Sincronización automática con viaje_gastos ──────────────────────
        if rid in ALOJ_DESC_MAP:
            ws_g = ensure_sheets()["viaje_gastos"]
            recs_g = ws_g.get_all_records()
            gid = f"res_{rid}"
            desc = ALOJ_DESC_MAP[rid]
            monto_float = float(monto) if monto else 0.0
            fecha_corta = now[:5]  # dd/mm

            if monto_float > 0:
                # Actualizar si ya existe, insertar si no
                updated = False
                for i, r in enumerate(recs_g, start=2):
                    if str(r.get("id")) == gid:
                        ws_g.update(f"A{i}:E{i}", [[gid, desc, "Alojamiento", monto_float, fecha_corta]])
                        updated = True
                        break
                if not updated:
                    ws_g.append_row([gid, desc, "Alojamiento", monto_float, fecha_corta])
            else:
                # Si el monto es 0, eliminar la fila de gastos si existía
                for i, r in enumerate(recs_g, start=2):
                    if str(r.get("id")) == gid:
                        ws_g.delete_rows(i)
                        break

        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

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
            ("📄 Documentos","Reservas impresas / guardadas offline"),
            ("📄 Documentos","Tarjetas bancarias notificadas para uso internacional"),
            ("📄 Documentos","Contactos de emergencia anotados"),
            ("💳 Dinero","Euros en efectivo para el primer día"),
            ("💳 Dinero","Francos suizos (CHF) para Zurich"),
            ("💳 Dinero","Revolut o Wise configurada"),
            ("🔌 Tecnología","Adaptador de enchufes para Suiza (tipo J — diferente a Italia)"),
            ("🔌 Tecnología","Power bank cargado"),
            ("🔌 Tecnología","Tarjeta SIM europea o eSIM activada"),
            ("🔌 Tecnología","Maps.me con mapas offline descargados"),
            ("🔌 Tecnología","App Trenitalia instalada"),
            ("🔌 Tecnología","App SBB instalada (trenes Suiza)"),
            ("🔌 Tecnología","Fotos de reservas guardadas en el teléfono"),
            ("👗 Ropa","Ropa para iglesias (hombros y rodillas cubiertos)"),
            ("👗 Ropa","Zapatos cómodos con suela firme (para adoquines)"),
            ("👗 Ropa","Ropa de abrigo para Zurich (puede hacer frío en junio)"),
            ("👗 Ropa","Traje de baño (Cinque Terre y Amalfi)"),
            ("👗 Ropa","Ropa para senderismo (Sentiero degli Dei)"),
            ("🏥 Salud","Protector solar FPS 50+ (varias unidades)"),
            ("🏥 Salud","Medicamentos habituales con receta"),
            ("🏥 Salud","Antidiarreico / antiácido (cambio de dieta)"),
            ("🏥 Salud","Repelente de mosquitos"),
            ("🏥 Salud","Botiquín básico (curitas, ibuprofeno)"),
            ("🎒 Equipaje","Candado para maletas"),
            ("🎒 Equipaje","Bolsa impermeable para la playa"),
            ("🎒 Equipaje","Botella de agua reutilizable"),
            ("🎒 Equipaje","Mochila pequeña para excursiones"),
        ]
        rows = [[f"c{str(i+1).zfill(2)}", cat, item, "0", ""] for i,(cat,item) in enumerate(items)]
        ws.append_rows(rows); st.cache_data.clear()
    except Exception as e: st.warning(f"No se pudo inicializar el checklist: {e}")

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
    except: pass; return False

# ── CLIMA ──────────────────────────────────────────────────────────────────────
CIUDADES_CLIMA = {
    "Milán":       {"lat":45.46,"lon":9.19, "fecha":"2026-05-25"},
    "Pisa":        {"lat":43.72,"lon":10.40,"fecha":"2026-05-29"},
    "Florencia":   {"lat":43.77,"lon":11.25,"fecha":"2026-05-30"},
    "Roma":        {"lat":41.90,"lon":12.49,"fecha":"2026-06-02"},
    "Nápoles":     {"lat":40.85,"lon":14.27,"fecha":"2026-06-06"},
    "Amalfi":      {"lat":40.63,"lon":14.60,"fecha":"2026-06-07"},
    "Venecia":     {"lat":45.44,"lon":12.33,"fecha":"2026-06-09"},
    "Zurich":      {"lat":47.37,"lon":8.54, "fecha":"2026-06-11"},
}
WMO_CODES = {
    0:"☀️ Despejado",1:"🌤️ Poco nublado",2:"⛅ Parcialmente nublado",3:"☁️ Nublado",
    45:"🌫️ Niebla",48:"🌫️ Niebla helada",51:"🌦️ Llovizna",53:"🌦️ Llovizna mod.",
    55:"🌧️ Llovizna intensa",61:"🌧️ Lluvia leve",63:"🌧️ Lluvia moderada",
    65:"🌧️ Lluvia intensa",80:"🌦️ Chubascos",81:"🌧️ Chubascos mod.",
    82:"⛈️ Chubascos fuertes",95:"⛈️ Tormenta",99:"⛈️ Tormenta granizo",
}

@st.cache_data(ttl=3600)
def get_clima(lat, lon, fecha):
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?"
               f"latitude={lat}&longitude={lon}"
               f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max"
               f"&timezone=Europe%2FRome&start_date={fecha}&end_date={fecha}")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()["daily"]
            return {"max":round(d["temperature_2m_max"][0]),"min":round(d["temperature_2m_min"][0]),
                    "code":d["weathercode"][0],"rain":d["precipitation_probability_max"][0]}
    except: pass
    return None

# ── MAPA ───────────────────────────────────────────────────────────────────────
RUTA_MAPA = [
    {"city":"Milán",       "lat":45.4654,"lon":9.1859, "dias":"D1–2","emoji":"🏛️","color":"#C4693A"},
    {"city":"Cinque Terre","lat":44.1461,"lon":9.6439, "dias":"D3–4","emoji":"🌊","color":"#6B7A3E"},
    {"city":"Pisa",        "lat":43.7228,"lon":10.4017,"dias":"D5 excursión","emoji":"🗼","color":"#C9A84C"},
    {"city":"Florencia",   "lat":43.7696,"lon":11.2558,"dias":"D5–8","emoji":"🌸","color":"#C4693A"},
    {"city":"Siena",       "lat":43.3188,"lon":11.3307,"dias":"D8 excursión","emoji":"🏰","color":"#C9A84C"},
    {"city":"Roma",        "lat":41.9028,"lon":12.4964,"dias":"D9–12","emoji":"🏟️","color":"#6B7A3E"},
    {"city":"Nápoles",     "lat":40.8518,"lon":14.2681,"dias":"D13","emoji":"🍕","color":"#C4693A"},
    {"city":"Pompeya",     "lat":40.7497,"lon":14.4990,"dias":"D13 excursión","emoji":"🌋","color":"#8B3E1E"},
    {"city":"Positano",    "lat":40.6278,"lon":14.4841,"dias":"D14–15","emoji":"🌅","color":"#6B7A3E"},
    {"city":"Ravello",     "lat":40.6490,"lon":14.6130,"dias":"D15 excursión","emoji":"🌿","color":"#C9A84C"},
    {"city":"Venecia",     "lat":45.4408,"lon":12.3155,"dias":"D16–17","emoji":"🚤","color":"#C4693A"},
    {"city":"Burano",      "lat":45.4847,"lon":12.4175,"dias":"D17 excursión","emoji":"🎨","color":"#C9A84C"},
    {"city":"Zurich",      "lat":47.3769,"lon":8.5417, "dias":"D18–20","emoji":"🇨🇭","color":"#3D4A5C"},
]

# ── RENDER HELPERS ─────────────────────────────────────────────────────────────
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

def _al(html, extra=""):
    M(f'<div class="al {extra}">{html}</div>')

# ── ITINERARIO COMPLETO ────────────────────────────────────────────────────────
def render_milan():
    _hotel("Hotel Ariston ★★★ (o similar zona Centrale/Navigli)",
           "Central para metro · Desayuno incluido · Habitación doble<br>"
           "Alternativa premium: Hotel Dei Cavalieri (~€110/noche, junto al Duomo)",
           "~€70–90 / noche · 2 noches",
           "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-27&group_adults=2",
           "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-27&adults=2",
           "https://maps.google.com/?q=Hotel+Ariston+Milan")

    _card("Día 1","Lunes 25 mayo — Llegada y primer paseo","Milán",
        _ev("10:15",True,"Llegada MXP — Inmigración y aduana",
            "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta.") +
        _ev("11:30",False,"Malpensa Express → Milano Centrale",
            "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.",
            acts='<span class="tag tr2">🚄 €13/persona</span><a href="https://www.trenord.it" target="_blank" class="lb btr">Trenord</a><a href="https://maps.google.com/?q=Milano+Centrale" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:30",False,"Check-in + almuerzo tranquilo",
            "Risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones.",
            acts='<span class="tag tf">🍝 Risotto</span>') +
        _ev("15:00",False,"Siesta obligatoria",
            "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes.") +
        _ev("18:00",False,"Paseo Navigli + Aperitivo",
            "Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.",
            acts='<span class="tag tw">🚶 Paseo</span><a href="https://maps.google.com/?q=Navigli+Milan" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 2","Martes 26 mayo — Última Cena, Duomo, Shopping y Pádel","Milán",
        _ev("08:00",False,"Desayuno italiano",
            "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.",
            acts='<span class="tag tf">☕ €3</span>') +
        _ev("08:15",True,"LA ÚLTIMA CENA — Santa Maria delle Grazie",
            "El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.",
            tip="⚠️ CRÍTICO: Reservar hoy mismo en cenacolodavincimilano.vivaticket.com — Los cupos de mayo se agotan meses antes.",
            acts='<span class="tag tm">🎨 €15 + €2 reserva</span><a href="https://cenacolodavincimilano.vivaticket.com" target="_blank" class="lb bt">🎟️ Reservar ahora</a><a href="https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"Duomo di Milano — terrazas",
            "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán. Reservar online.",
            acts='<span class="tag tm">⛪ €15 terraza</span><a href="https://ticket.duomomilano.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Duomo+di+Milano" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Galleria Vittorio Emanuele II + Scala",
            "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).",
            acts='<span class="tag tw">🚶 Gratis</span><a href="https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Brera",
            "Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15.",
            acts='<span class="tag tf">🍽️ €15</span><a href="https://maps.google.com/?q=Brera+Milan" target="_blank" class="lb bm">📍 Brera</a>') +
        _ev("15:00",True,"Shopping — Corso Buenos Aires",
            "La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas. 2km de tiendas.",
            acts='<span class="tag ts">🛍️ Ropa</span><a href="https://maps.google.com/?q=Corso+Buenos+Aires+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",True,"Padel Nuestro Milano (opcional)",
            "La mayor tienda de pádel del norte de Italia. Bullpadel, Siux, Adidas, Nox. Pista interior para probar palas. Está en las afueras.",
            tip="Más conveniente ir a Padel Nuestro Roma (centro, Día 11). Esta cierra 19:30.",
            acts='<span class="tag tpa">🎾 Pádel</span><a href="https://maps.google.com/?q=Padel+Nuestro+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena en Navigli · Preparar maletas",
            "Cena tranquila. Mañana temprano: tren a Cinque Terre (08:10 desde Milano Centrale).",
            acts='<span class="tag tf">🍷 Cena</span><span class="tag tsl">🧳 Preparación</span>'))


def render_cinque():
    _tcard("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10 desde Milano Centrale","€25–35","https://www.trenitalia.com")
    _hotel("Hotel Firenze ★★★ (La Spezia)",
           "5 min a pie de la estación · Habitación doble · 2 noches<br>"
           "Alternativa: alojarse directamente en Monterosso al Mare",
           "~€70–80 / noche · 2 noches",
           "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-27&checkout=2026-05-29&group_adults=2",
           "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-27&checkout=2026-05-29&adults=2",
           "https://maps.google.com/?q=La+Spezia+train+station")

    _card("Día 3","Miércoles 27 mayo — Riomaggiore, Manarola, Corniglia","Cinque Terre",
        _ev("11:30",False,"Llegada La Spezia — Check-in + Cinque Terre Card",
            "Comprar la Card 2 días en InfoParco o taquilla de la estación (~€29.50/persona). Incluye todos los trenes locales.",
            acts='<span class="tag tkt">🎫 €29.50 · 2 días</span><a href="https://www.cinqueterre.eu.com/en/cinque-terre-card" target="_blank" class="lb bt">Info Card</a>') +
        _ev("12:30",True,"Riomaggiore — el más fotogénico",
            "Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà. El pesto de Liguria es el mejor del mundo.",
            acts='<span class="tag tf">🍃 Pesto original</span><a href="https://maps.google.com/?q=Riomaggiore+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",True,"Manarola — el mirador icónico",
            "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.",
            acts='<span class="tag tw">📸 Foto icónica</span><a href="https://maps.google.com/?q=Manarola+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"Corniglia — vista 360°",
            "El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.",
            acts='<a href="https://maps.google.com/?q=Corniglia+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 4","Jueves 28 mayo — Vernazza, senderismo y Monterosso","Cinque Terre",
        _ev("08:00",True,"Vernazza — el más medieval",
            "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.",
            acts='<a href="https://maps.google.com/?q=Vernazza+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",True,"Senderismo Vernazza → Monterosso (3.5 km · 2h)",
            "El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir. Llevar agua y zapatos cerrados.",
            tip="Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.",
            acts='<span class="tag tw">🥾 Trekking</span><a href="https://www.parconazionale5terre.it" target="_blank" class="lb bt">Estado senderos</a>') +
        _ev("14:00",False,"Monterosso — playa y anchoas",
            "El único pueblo con playa de arena real. Probar acciughe (anchoas de Monterosso). Reposeras ~€5. Agua ~22°C.",
            acts='<span class="tag tw">🏖️ Playa</span><a href="https://maps.google.com/?q=Monterosso+al+Mare" target="_blank" class="lb bm">📍 Maps</a>'))


def render_florencia():
    _tcard("🚄","La Spezia → Firenze Santa Maria Novella","Intercity · ~2h · Salida 08:30 · Directo o cambio en Pisa","€15–20","https://www.trenitalia.com")
    _hotel("Hotel Davanzati ★★★ (recomendado)",
           "A 2 min del Duomo y Uffizi · Servicio excelente · Desayuno muy bueno<br>"
           "Alternativa: B&B Machiavelli (zona Oltrarno, ~€75/noche)",
           "~€95–110 / noche · 4 noches",
           "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-29&checkout=2026-06-02&group_adults=2",
           "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-29&checkout=2026-06-02&adults=2",
           "https://maps.google.com/?q=Hotel+Davanzati+Florence")

    _card("Día 5","Viernes 29 mayo — Pisa","Pisa / Florencia",
        _ev("08:30",True,"Tren Florencia → Pisa Centrale",
            "Tren Regional · 1h · Sale frecuentemente desde SMN. En Pisa tomar el bus LAM Rossa (€1.50) o 20 min a pie hasta la Piazza dei Miracoli.",
            acts='<span class="tag tr2">🚄 1h · ~€10</span><a href="https://www.trenitalia.com" target="_blank" class="lb btr">Trenitalia</a>') +
        _ev("10:00",True,"Piazza dei Miracoli — La Torre de Pisa",
            "La famosa plaza de los milagros con la Torre Inclinada, el Duomo y el Baptisterio. Subir a la Torre: 294 escalones en espiral, 56m de altura. La inclinación se siente al caminar.",
            tip="⚠️ La Torre requiere reserva obligatoria en opapisa.it. Sin reserva puede no quedar cupos. Llegar 15 min antes del horario reservado.",
            acts='<span class="tag tm">🗼 Torre €20</span><a href="https://www.opapisa.it" target="_blank" class="lb bt">🎟️ Reservar Torre</a><a href="https://maps.google.com/?q=Piazza+dei+Miracoli+Pisa" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Duomo di Pisa + Baptisterio",
            "El Duomo de Pisa (siglo XI) es uno de los mejores ejemplos del románico italiano. El Baptisterio tiene una acústica increíble — el guarda suele demostrarla cantando.",
            acts='<span class="tag tm">⛪ Pase €7</span><a href="https://maps.google.com/?q=Duomo+di+Pisa" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo — Borgo Stretto",
            "Alejarse de la Piazza dei Miracoli para comer bien y barato. Probar: cecina (torta de garbanzo, especialidad de Pisa, €2) y schiacciata.",
            acts='<span class="tag tf">🍽️ Cecina €2</span><a href="https://maps.google.com/?q=Borgo+Stretto+Pisa" target="_blank" class="lb bm">📍 Borgo Stretto</a>') +
        _ev("14:30",False,"Camposanto Monumentale + Lungarni",
            "El Camposanto es un cementerio medieval con frescos impresionantes. Luego pasear por los Lungarni (orilla del Arno pisano) — tranquilo y sin turistas.",
            acts='<span class="tag tm">🏛️ €5</span><a href="https://maps.google.com/?q=Camposanto+Monumentale+Pisa" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:30",False,"Tren Pisa → Florencia",
            "Tren Regional de vuelta · 1h · Hay trenes frecuentes.",
            acts='<span class="tag tr2">🚄 1h</span>') +
        _ev("18:30",True,"Piazzale Michelangelo — atardecer",
            "EL punto de vista de Florencia al atardecer. Vista panorámica de toda la ciudad. Llegar 30 min antes del sunset.",
            acts='<span class="tag tw">🌅 Gratis</span><a href="https://maps.google.com/?q=Piazzale+Michelangelo+Florence" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 6","Sábado 30 mayo — Uffizi + David + San Miniato","Florencia",
        _ev("08:30",True,"Galería degli Uffizi — Botticelli, Leonardo, Caravaggio",
            "El museo de arte renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA. La sala de Botticelli — visitarla primero.",
            acts='<span class="tag tm">🎨 €20 + €4 reserva</span><a href="https://www.uffizi.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Uffizi+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",True,"David de Michelangelo — Accademia",
            "5.17 metros de mármol perfecto, tallado entre 1501 y 1504. El original — el de la Piazza es una copia. 1.5h.",
            acts='<span class="tag tm">🗿 €12 + reserva</span><a href="https://www.uffizi.it/en/the-accademia-gallery" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Accademia+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"San Miniato al Monte",
            "La iglesia más bella de Florencia — sobre una colina, entrada gratis. Los monjes rezan el Oficio en gregoriano a las 17:30.",
            acts='<span class="tag tw">⛪ Gratis</span><a href="https://maps.google.com/?q=San+Miniato+al+Monte+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:30",False,"Cena en Oltrarno",
            "Ponte Vecchio al paso. Cena en el barrio más auténtico de Florencia. Probar bistecca fiorentina si el presupuesto lo permite.",
            acts='<span class="tag tf">🥩 Bistecca</span>'))

    _card("Día 7","Domingo 31 mayo — Palazzo Pitti + Boboli + Cappelle Medicee","Florencia",
        _ev("09:00",False,"Palazzo Pitti + Jardines de Boboli",
            "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina. Jardines renacentistas con gruta de Buontalenti (1583).",
            acts='<span class="tag tm">🏰 €16</span><a href="https://maps.google.com/?q=Palazzo+Pitti+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("12:30",False,"Almuerzo en Mercato Centrale",
            "Piso superior con puestos de comida. Probar lampredotto (callos florentinos) o pasta fresca.",
            acts='<a href="https://maps.google.com/?q=Mercato+Centrale+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:30",True,"Cappelle Medicee — Michelangelo",
            "Las tumbas de los Medici con las esculturas: Aurora, Crepúsculo, Día y Noche. Menos conocidas que el David, igual de impactantes.",
            acts='<span class="tag tm">🗿 €9</span><a href="https://maps.google.com/?q=Cappelle+Medicee+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",False,"Ponte Vecchio + Cuero florentino",
            "Cruzar el Ponte Vecchio y explorar el mercado de San Lorenzo. El cuero florentino es el mejor de Italia. Verificar que sea auténtico (encendedor — no huele a plástico).",
            acts='<span class="tag ts">🛍️ Cuero</span><a href="https://maps.google.com/?q=Ponte+Vecchio+Florence" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 8","Lunes 1 junio — Siena y Val d'Orcia","Toscana",
        _ev("07:30",False,"Bus SENA desde Florencia a Siena",
            "Desde Autostazione di Firenze (frente a Santa Maria Novella). 1.5h · €9.",
            acts='<span class="tag tbu">🚌 €9</span><a href="https://maps.google.com/?q=Autostazione+Firenze" target="_blank" class="lb bm">📍 Bus</a>') +
        _ev("09:00",True,"Piazza del Campo + Torre del Mangia",
            "La plaza más bella de Italia en forma de concha, escenario del Palio. La Torre tiene 400 escalones y vistas impresionantes.",
            acts='<span class="tag tm">🏰 Torre €10</span><a href="https://maps.google.com/?q=Piazza+del+Campo+Siena" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:30",False,"Duomo di Siena",
            "El Duomo de Siena compite con Florencia en belleza. El pavimento de mármol con 56 escenas es único en el mundo.",
            acts='<span class="tag tm">⛪ €8</span><a href="https://maps.google.com/?q=Siena+Cathedral" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en la ciudad vieja",
            "Probar: pici all'aglione (pasta gruesa con ajo), cinghiale (jabalí). Siena tiene cocina muy diferente a Florencia.",
            acts='<span class="tag tf">🍖 Toscana</span>') +
        _ev("17:00",False,"Bus de regreso a Florencia",
            "Hay buses frecuentes hasta las 21:00. Cena en Florencia. Mañana viajan a Roma."))


def render_roma():
    _tcard("🚄","Firenze SMN → Roma Termini","Frecciarossa (Alta Velocidad) · 1h 30min · Sale cada 30 min · Reservar anticipado","€25–45","https://www.trenitalia.com")
    _hotel("Hotel Arco del Lauro ★★★ (Trastevere)",
           "Zona Trastevere — auténtica y central · B&B familiar · Muy buenas reseñas<br>"
           "Alternativa: zona Prati (junto al Vaticano) o Hotel Santa Prassede (~€80)",
           "~€80–95 / noche · 4 noches",
           "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-02&checkout=2026-06-06&group_adults=2",
           "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-02&checkout=2026-06-06&adults=2",
           "https://maps.google.com/?q=Trastevere+Rome")
    _al("<strong>🎾 Padel Nuestro Roma:</strong> La tienda más completa de la ruta. Centro de Roma. Bullpadel, Siux, Babolat, Head, Star Vie. Permiten probar palas. Ver Día 11.")

    _card("Día 9","Martes 2 junio — Vaticano completo","Roma",
        _ev("10:30",True,"Museos Vaticanos + Capilla Sixtina",
            "Los museos más visitados del mundo. 3–4h. El recorrido culmina en la Capilla Sixtina con el fresco de Miguel Ángel. RESERVA YA COMPRADA ✓",
            tip="⚠️ En la Capilla Sixtina está prohibido fotografiar y hacer ruido — los guardias son estrictos. Silencio absoluto.",
            acts='<span class="tag bc">✅ Reserva confirmada</span><a href="https://maps.google.com/?q=Vatican+Museums+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",False,"Basílica de San Pedro + Cúpula",
            "La basílica más grande del mundo cristiano. Subir a la cúpula (551 escalones o ascensor parcial €8) para vista alucinante.",
            acts='<span class="tag tm">⛪ Gratis · Cúpula €8</span><a href="https://maps.google.com/?q=St+Peters+Basilica+Rome" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 10","Miércoles 3 junio — Roma Imperial","Roma",
        _ev("08:00",True,"Coliseo + Foro Romano + Palatino",
            "Combo obligatorio. 3–4h. El Palatino tiene las mejores vistas del Coliseo y es el menos visitado — no saltearlo. RESERVA YA COMPRADA ✓",
            acts='<span class="tag bc">✅ Reserva confirmada</span><a href="https://maps.google.com/?q=Colosseum+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Testaccio",
            "El barrio más auténtico de Roma para comer. El Mercato di Testaccio tiene puestos con cocina romana real: supplì, pizza al taglio.",
            acts='<span class="tag tf">🥙 Testaccio</span><a href="https://maps.google.com/?q=Mercato+Testaccio+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Terme di Caracalla + Circo Massimo",
            "Las Termas de Caracalla (216 d.C.) son ruinas espectaculares y poco masificadas. El Circo Massimo (450,000 espectadores) es gratis, hoy un parque.",
            acts='<span class="tag tm">🏛️ Termas €8</span><a href="https://maps.google.com/?q=Terme+di+Caracalla+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Trastevere — paseo y cena",
            "El barrio medieval más pintoresco de Roma. La Basílica di Santa Maria in Trastevere (siglo XII, gratis). Cena: Da Enzo al 29.",
            acts='<span class="tag tw">🚶 Paseo</span><a href="https://maps.google.com/?q=Trastevere+Rome" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 11","Jueves 4 junio — Roma Barroca + Borghese + Pádel","Roma",
        _ev("09:00",False,"Pantheon → Piazza Navona → Fontana di Trevi",
            "El Pantheon (125 d.C.) requiere ticket €5 desde 2023. Trevi: lanzar la moneda de espaldas con la derecha.",
            acts='<span class="tag tm">🏛️ Pantheon €5</span><a href="https://maps.google.com/?q=Pantheon+Rome" target="_blank" class="lb bm">📍 Pantheon</a><a href="https://maps.google.com/?q=Trevi+Fountain+Rome" target="_blank" class="lb bm">📍 Trevi</a>') +
        _ev("15:00",True,"Galería Borghese — Bernini",
            "El museo más exclusivo de Roma — solo 360 personas cada 2 horas. Apolo y Dafne, El rapto de Proserpina — lo más impactante de toda Roma.",
            acts='<span class="tag tm">🗿 €15 + €2 reserva</span><a href="https://www.galleriaborghese.it" target="_blank" class="lb bt">🎟️ Reservar</a><a href="https://maps.google.com/?q=Galleria+Borghese+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",True,"🎾 Padel Nuestro Roma",
            "La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Pista interior para probar palas antes de comprar.",
            acts='<span class="tag tpa">🎾 Pádel Roma</span><a href="https://maps.google.com/?q=Padel+Nuestro+Roma+Italy" target="_blank" class="lb bm">📍 Maps</a><a href="https://www.padelnuestro.com" target="_blank" class="lb bt">Web tienda</a>'))

    _card("Día 12","Viernes 5 junio — Castel Sant'Angelo + Pincio + libre","Roma",
        _ev("09:00",False,"Castel Sant'Angelo",
            "Mausoleo de Adriano convertido en fortaleza papal. Vista del Tiber y San Pedro desde la cima.",
            acts='<span class="tag tm">🏰 €14</span><a href="https://maps.google.com/?q=Castel+Sant+Angelo+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",False,"Piazza del Popolo + Santa Maria del Popolo",
            "La gran plaza de entrada a Roma desde el norte. Las dos capillas Caravaggio dentro de Santa Maria del Popolo (gratis) son joyas escondidas.",
            acts='<span class="tag tw">⛪ Gratis</span><a href="https://maps.google.com/?q=Piazza+del+Popolo+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo + tarde libre · Compras Via del Corso",
            "Via del Corso para shopping. Zona Spagna para marcas. Ghetto judío para caminar. Mañana temprano: tren a Nápoles.",
            acts='<span class="tag ts">🛍️ Libre</span>'))


def render_napoles():
    _tcard("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00","€20–35","https://www.trenitalia.com")
    _hotel("Hotel Piazza Bellini ★★★ (centro histórico UNESCO)",
           "En el corazón de Spaccanapoli · 1 noche (6–7 junio)",
           "~€75–90 / noche",
           "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-06&checkout=2026-06-07&group_adults=2",
           "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-06&checkout=2026-06-07&adults=2",
           "https://maps.google.com/?q=Piazza+Bellini+Naples")

    _card("Día 13","Sábado 6 junio — Pompeya + Nápoles + Pizza","Nápoles",
        _ev("09:00",True,"Circumvesuviana → Pompeya Scavi",
            "Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento. Bajarse en 'Pompei Scavi'. Comprar ticket en máquina automática.",
            acts='<span class="tag tr2">🚂 €3 · 40min</span><a href="https://maps.google.com/?q=Pompei+Scavi+station" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"Pompeya — ciudad sepultada por el Vesubio",
            "La ciudad romana sepultada en 79 d.C. 3h mínimo. Casa dei Vettii, Anfiteatro, Thermopolium (bar romano), moldes humanos en el Granario, el Foro. Llevar agua y sombrero.",
            acts='<span class="tag tm">🌋 €16</span><a href="https://maps.google.com/?q=Pompeii+Archaeological+Park" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Spaccanapoli + Museo Arqueológico Nacional",
            "La calle que cruza Nápoles histórica. El Museo tiene los mejores objetos de Pompeya y Herculano del mundo.",
            acts='<span class="tag tm">🏺 €15</span><a href="https://maps.google.com/?q=National+Archaeological+Museum+Naples" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",True,"🍕 La pizza napolitana ORIGINAL",
            "Nápoles inventó la pizza. Las tres legendarias: L'Antica Pizzeria da Michele (solo Margherita y Marinara, fila larga), Sorbillo (favorita de los napolitanos), Di Matteo.",
            acts='<span class="tag tf">🍕 €5–8</span><a href="https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples" target="_blank" class="lb bm">📍 Da Michele</a><a href="https://maps.google.com/?q=Pizzeria+Sorbillo+Naples" target="_blank" class="lb bm">📍 Sorbillo</a>'))


def render_amalfi():
    _al("<strong>💰 Tip de presupuesto:</strong> Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200 fácilmente. Con ferry desde Praiano se llega a Positano en 10 min.")
    _tcard("⛵","Nápoles → Positano (ferry)","SNAV o Alilauro · Desde Molo Beverello · Salidas 08:30 y 09:30 · Solo mayo–oct","~€20/persona","https://www.alilauro.it")
    _hotel("Albergo California (Praiano) ★★★",
           "Vista al mar · Desayuno incluido · 10 min de Positano en ferry · 2 noches (7–9 junio)",
           "~€85–100 / noche",
           "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-07&checkout=2026-06-09&group_adults=2",
           "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-07&checkout=2026-06-09&adults=2",
           "https://maps.google.com/?q=Praiano+Amalfi+Coast")

    _card("Día 14","Domingo 7 junio — Positano + Amalfi","Costa Amalfi",
        _ev("10:30",True,"Positano — las casas en cascada",
            "El pueblo más fotogénico de la Costa. Playa Grande con guijarros, reposeras ~€20 el par. Agua del Tirreno ~22°C.",
            acts='<a href="https://maps.google.com/?q=Positano+Amalfi+Coast" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo con vista en Positano",
            "Muy caro en Positano. Buscar La Zagara o Il Ritrovo (más económico). Probar: scialatielli ai frutti di mare.",
            acts='<span class="tag tf">🦐 Mariscos</span>') +
        _ev("15:00",True,"Bus SITA → Amalfi ciudad",
            "El bus azul recorre toda la costa. €2.50 el tramo. 40 min por la carretera más espectacular de Italia.",
            tip="Comprar ticket en tabacchi ANTES de subir. Sentarse del lado DERECHO mirando al mar.",
            acts='<span class="tag tbu">🚌 €2.50</span><a href="https://maps.google.com/?q=Amalfi+Cathedral" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",False,"Cena con vista al mar",
            "El atardecer sobre el Tirreno desde la Costa Amalfi es uno de los espectáculos más bellos de Italia.",
            acts='<span class="tag tf">🌅 Scialatielli ai frutti</span>'))

    _card("Día 15","Lunes 8 junio — Ravello + Sentiero degli Dei","Costa Amalfi",
        _ev("08:00",True,"Ravello — Villa Cimbrone + Terrazza dell'Infinito",
            "Ravello a 350m sobre el mar. La Terraza del Infinito — Wagner llamó a esta vista 'el balcón más bello del mundo'.",
            acts='<span class="tag tm">🌿 €7</span><a href="https://maps.google.com/?q=Villa+Cimbrone+Ravello" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",True,"Sentiero degli Dei — Camino de los Dioses (7.8km · 3h)",
            "El sendero más famoso de la Costa Amalfi. Sale desde Bomerano y baja hasta Positano. Vista de toda la costa desde 600m de altura.",
            tip="El trayecto baja (no sube), así que el cansancio es manejable. Es el mejor día del viaje para muchos viajeros.",
            acts='<span class="tag tw">🥾 Trekking</span><a href="https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Llegada Positano + playa merecida",
            "Después del sendero: baño en el mar. Tarde libre. Mañana: ferry + tren largo a Venecia — preparar maletas.",
            acts='<span class="tag tw">🏖️ Playa</span>'))


def render_venecia():
    _tcard("🚄","Nápoles → Venezia Santa Lucia","Frecciarossa directo · 4h50 · Salida 07:30–08:00","€35–60","https://www.trenitalia.com")
    _al("<strong>Nota Venecia:</strong> Desde junio 2024, Venecia cobra €5 de 'tasa de acceso' en días pico. Verificar en comune.venezia.it. Airbnb muy regulado — hotel es la mejor opción.")
    _hotel("Hotel Dalla Mora ★★★ (Santa Croce)",
           "Zona auténtica · 10 min a pie de la estación · Venecia real, NO en Mestre (tierra firme)<br>"
           "Alternativa: B&B en Cannaregio · 2 noches (9–11 junio)",
           "~€90–110 / noche · 2 noches",
           "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-09&checkout=2026-06-11&group_adults=2&nflt=di%3D1376",
           "", "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice")

    _card("Día 16","Martes 9 junio — Venecia clásica","Venecia",
        _ev("13:00",True,"Gran Canal en Vaporetto línea 1 (la lenta)",
            "La línea 1 recorre todo el Gran Canal parando en cada estación. 45 minutos de palacios del siglo XIV, puentes, góndolas. El paseo más cinematográfico del viaje. Ticket 24h = €25.",
            acts='<span class="tag tb">🚤 24h = €25</span>') +
        _ev("15:00",True,"Plaza San Marcos + Basílica + Campanile",
            "Basílica siglo XI, estilo bizantino, cúpulas doradas — gratuita con espera. El Campanile (99m) ofrece la mejor vista de Venecia. €10.",
            acts='<span class="tag tm">🏛️ Gratis + €10 campanile</span><a href="https://maps.google.com/?q=St+Marks+Basilica+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",True,"Perderse sin mapa — la mejor actividad de Venecia",
            "Apagar Google Maps. Venecia tiene 118 islas conectadas por 400 puentes. Los callejones más angostos llevan a los campos (plazas) más secretos.",
            acts='<span class="tag tw">🗺️ Sin mapa</span>') +
        _ev("19:30",False,"Spritz veneziano en bacaro + Rialto",
            "El Spritz se inventó en Venecia. Los 'bacari' son los bares tradicionales con 'cicchetti' (tapas de €1–2). Zona Cannaregio para los más auténticos.",
            acts='<span class="tag tf">🍹 Bacaro</span><a href="https://maps.google.com/?q=Rialto+Bridge+Venice" target="_blank" class="lb bm">📍 Rialto</a>') +
        _ev("21:00",False,"Góndola nocturna (opcional)",
            "Precio fijo oficial: €80 para 30 min (hasta 6 personas). De noche los canales sin turistas son mágicos.",
            acts='<span class="tag tb">🎭 €80 / góndola</span>'))

    _card("Día 17","Miércoles 10 junio — Murano, Burano y Dorsoduro","Venecia",
        _ev("09:00",True,"Vaporetto a Murano — la isla del cristal",
            "Murano está a 15 min de Venecia en vaporetto (incluido en el pase 24h o ticket día). Ver una demostración en una de las fábricas históricas — es gratis y espectacular.",
            tip="Las mejores maestrías: Fornace Mian y Vetreria Artistica Archimede Seguso. Asegurarse de comprar el cristal directamente en Murano.",
            acts='<span class="tag tb">⛴️ 15 min</span><a href="https://maps.google.com/?q=Murano+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",True,"Burano — la isla más colorida del mundo",
            "Burano está a 40 min de Murano. Las casas pintadas de colores vibrantes son únicas en el mundo. La leyenda dice que los pescadores las pintaban para reconocer su casa desde el mar.",
            tip="El paseo principal es Via Baldassarre Galuppi. Ir temprano para ver el pueblo sin turistas.",
            acts='<span class="tag tb">⛴️ 40 min</span><a href="https://maps.google.com/?q=Burano+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Burano — risotto di go",
            "El 'risotto di go' (una especie de gobio local) es la especialidad de Burano. Los restaurantes al borde del canal son caros pero el ambiente lo vale.",
            acts='<span class="tag tf">🦀 Risotto di go</span>') +
        _ev("15:00",False,"Vaporetto de regreso + barrio Dorsoduro",
            "Dorsoduro es el barrio más tranquilo de Venecia. La Gallerie dell'Accademia (€12) o los Zattere al atardecer.",
            acts='<span class="tag tm">🎨 Accademia €12</span><a href="https://maps.google.com/?q=Dorsoduro+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Campo Santa Margherita — aperitivo final en Venecia",
            "La plaza más viva de Venecia, llena de estudiantes locales. El último Spritz veneziano antes de partir.",
            acts='<span class="tag tf">🍹 Último Spritz</span><a href="https://maps.google.com/?q=Campo+Santa+Margherita+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena despedida de Italia · Preparar maletas",
            "Mañana temprano: tren a Zurich (09:00 desde Venezia S. Lucia). Hacer check-in online si aplica.",
            acts='<span class="tag tsl">🧳 Mañana Zurich</span>'))


def render_zurich():
    _tcard("🚄","Venezia S. Lucia → Zurich HB (a través de los Alpes)","EuroCity directo · 4h45 · Paisaje alpino impresionante · Sentarse del lado DERECHO mirando norte","€40–60","https://www.sbb.ch")
    _al("⚠️ <strong>Vuelo el 14/6 a las 08:55:</strong> Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min. El día 13 preparar todo y dormir temprano.")
    _hotel("Hotel Otter ★★ (Langstrasse) o IBIS City West",
           "Zona cool y multicultural · A pie del casco histórico · 3 noches (11–14 junio)<br>"
           "Alternativa con vista: Hotel Limmatblick (~€120, sobre el río Limmat)",
           "~€90–110 / noche · 3 noches",
           "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
           "", "https://maps.google.com/?q=Langstrasse+Zurich")

    _card("Día 18","Jueves 11 junio — Llegada + Altstadt","Zurich",
        _ev("14:00",False,"Bahnhofstrasse + Lago de Zurich",
            "La calle comercial más cara del mundo. Joyerías, Rolex, bancos. El Lago al final para sentarse. Cambio mental: de caos italiano a precisión suiza.",
            acts='<span class="tag tw">⌚ Paseo</span><a href="https://maps.google.com/?q=Bahnhofstrasse+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",True,"Altstadt + Grossmünster",
            "La iglesia donde Zwinglio inició la Reforma Protestante en 1519. Subir las torres (€5). El barrio Niederdorf: callejuelas adoquinadas, gremios medievales, cafés.",
            acts='<a href="https://maps.google.com/?q=Grossmunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Fraumünster — vitrales de Chagall (1970)",
            "5 vitrales de Marc Chagall en un edificio del siglo XIII. Tesoro de arte moderno en arquitectura medieval. €5.",
            acts='<span class="tag tm">🎨 €5</span><a href="https://maps.google.com/?q=Fraumunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 19","Viernes 12 junio — Lago + ETH + Fondue","Zurich",
        _ev("09:00",True,"Crucero Lago de Zurich",
            "ZSG opera cruceros. Recorrido corto 1h o largo 4h hasta Rapperswil. El lago con los Alpes de fondo es icónico.",
            acts='<span class="tag tb">⛵ €8–30</span><a href="https://www.zsg.ch" target="_blank" class="lb bt">ZSG</a><a href="https://maps.google.com/?q=Lake+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:00",False,"Polybahn → terraza ETH (vista gratis)",
            "El funicular universitario de 1889 sube hasta la ETH (la universidad de Einstein). Vista panorámica de Zurich, el lago y los Alpes — gratis.",
            acts='<a href="https://maps.google.com/?q=ETH+Zurich+terrace" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",True,"Fondue suiza — Swiss Chuchi",
            "La fondue de queso es el plato nacional suizo. Swiss Chuchi en el Altstadt. Experiencia completa ~€35–45/persona.",
            acts='<span class="tag tf">🧀 Fondue</span><a href="https://maps.google.com/?q=Swiss+Chuchi+Zurich" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 20","Sábado 13 junio — Uetliberg + Chocolates + Última noche","Zurich",
        _ev("09:00",False,"Uetliberg — la montaña de Zurich",
            "870m. Tren S10 desde HB, 20 min, €5. Vista de Zurich, el lago y los Alpes. Bajada por sendero a Felsenegg.",
            acts='<span class="tag tw">⛰️ €5 tren</span><a href="https://maps.google.com/?q=Uetliberg+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",True,"Chocolates Sprüngli + Mercado Bürkliplatz",
            "Sprüngli (desde 1836) — los mejores truffes du jour de Zurich. El mercado de Bürkliplatz los sábados tiene artesanías locales.",
            acts='<span class="tag tf">🍫 Chocolates</span><a href="https://maps.google.com/?q=Confiserie+Sprungli+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:00",True,"Última cena del viaje 🥂",
            "Elegir el restaurante favorito de los días en Zurich. Brindar por el viaje. Hacer check-in online del vuelo LA8799.",
            acts='<span class="tag tf">🥂 Despedida</span>') +
        _ev("22:00",False,"A dormir — vuelo 08:55 mañana",
            "Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración. Estar en aeropuerto a las 07:00.",
            tip="⚠️ ALARMA 06:00. Sin excepciones.",
            acts='<span class="tag tsl">✈️ Alarma 06:00</span>'))


CIUDAD_FN = {
    "🏛️ Milán":        render_milan,
    "🌊 Cinque Terre":  render_cinque,
    "🌸 Florencia":     render_florencia,
    "🏟️ Roma":          render_roma,
    "🍕 Nápoles":       render_napoles,
    "🌅 Costa Amalfi":  render_amalfi,
    "🚤 Venecia":       render_venecia,
    "🇨🇭 Zurich":       render_zurich,
}

# ── DATOS FIJOS ────────────────────────────────────────────────────────────────
RESERVAS_MUSEOS = [
    {"id":"m01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15",
     "urgente":True,"url":"https://cenacolodavincimilano.vivaticket.com","maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"4 junio · 15:00",
     "urgente":True,"url":"https://www.galleriaborghese.it","maps":"https://maps.google.com/?q=Galleria+Borghese+Rome",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"2 junio · 10:30",
     "urgente":False,"url":"https://www.museivaticani.va","maps":"https://maps.google.com/?q=Vatican+Museums+Rome",
     "default_estado":"paid","default_conf":"YA COMPRADO ✓","default_monto":42},
    {"id":"m04","title":"Torre de Pisa — Subida","city":"Pisa","fecha":"29 mayo",
     "urgente":True,"url":"https://www.opapisa.it","maps":"https://maps.google.com/?q=Torre+di+Pisa",
     "default_estado":"pending","default_conf":"","default_monto":0},
    {"id":"m05","title":"Coliseo + Foro Romano + Palatino","city":"Roma","fecha":"3 junio · 08:00",
     "urgente":False,"url":"https://www.coopculture.it","maps":"https://maps.google.com/?q=Colosseum+Rome",
     "default_estado":"paid","default_conf":"YA COMPRADO ✓","default_monto":32},
    {"id":"m06","title":"David — Accademia Florencia","city":"Florencia","fecha":"30 mayo · 14:00",
     "urgente":False,"url":"https://www.uffizi.it/en/the-accademia-gallery","maps":"https://maps.google.com/?q=Accademia+Gallery+Florence",
     "default_estado":"paid","default_conf":"YA COMPRADO ✓","default_monto":24},
    {"id":"m07","title":"Galería degli Uffizi","city":"Florencia","fecha":"30 mayo · 08:30",
     "urgente":False,"url":"https://www.uffizi.it","maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence",
     "default_estado":"pending","default_conf":"","default_monto":0},
]

RESERVAS_ALOJ = [
    {"id":"a01","city":"Milán","fecha":"25–27 mayo","noches":2,"precio":"€70–90/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-27&group_adults=2",
     "url_a":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-27&adults=2","maps":"https://maps.google.com/?q=Milan+Italy"},
    {"id":"a02","city":"La Spezia","fecha":"27–29 mayo","noches":2,"precio":"€70–80/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-27&checkout=2026-05-29&group_adults=2",
     "url_a":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-27&checkout=2026-05-29&adults=2","maps":"https://maps.google.com/?q=La+Spezia+Italy"},
    {"id":"a03","city":"Florencia","fecha":"29 mayo–2 junio","noches":4,"precio":"€95–110/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-29&checkout=2026-06-02&group_adults=2",
     "url_a":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-29&checkout=2026-06-02&adults=2","maps":"https://maps.google.com/?q=Florence+Italy"},
    {"id":"a04","city":"Roma","fecha":"2–6 junio","noches":4,"precio":"€80–95/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-02&checkout=2026-06-06&group_adults=2",
     "url_a":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-02&checkout=2026-06-06&adults=2","maps":"https://maps.google.com/?q=Trastevere+Rome"},
    {"id":"a05","city":"Nápoles","fecha":"6–7 junio","noches":1,"precio":"€75–90/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-06&checkout=2026-06-07&group_adults=2",
     "url_a":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-06&checkout=2026-06-07&adults=2","maps":"https://maps.google.com/?q=Naples+Italy"},
    {"id":"a06","city":"Praiano / Costa Amalfi","fecha":"7–9 junio","noches":2,"precio":"€85–100/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-07&checkout=2026-06-09&group_adults=2",
     "url_a":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-07&checkout=2026-06-09&adults=2","maps":"https://maps.google.com/?q=Praiano+Italy"},
    {"id":"a07","city":"Venecia","fecha":"9–11 junio","noches":2,"precio":"€90–110/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-09&checkout=2026-06-11&group_adults=2",
     "url_a":"","maps":"https://maps.google.com/?q=Venice+Italy"},
    {"id":"a08","city":"Zurich","fecha":"11–14 junio","noches":3,"precio":"€90–110/noche",
     "url_b":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
     "url_a":"","maps":"https://maps.google.com/?q=Zurich+Switzerland"},
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · 52 min · cada 30 min","€13/p","https://www.trenord.it"),
    ("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10","€25–35","https://www.trenitalia.com"),
    ("🚂","La Spezia ↔ Cinque Terre","Regional · Incluido en Cinque Terre Card (€29.50/2 días)","Incluido","https://www.cinqueterre.eu.com"),
    ("🚄","La Spezia → Firenze SMN","Intercity · ~2h · Salida 08:30","€15–20","https://www.trenitalia.com"),
    ("🚄","Firenze ↔ Pisa Centrale","Regional · 1h · Frecuente todo el día","€9–12","https://www.trenitalia.com"),
    ("🚌","Firenze ↔ Siena","Bus SENA · 1h30 · desde Autostazione frente a SMN","€9","https://www.tiemmespa.it"),
    ("🚄","Firenze → Roma Termini","Frecciarossa · 1h30 · cada 30 min","€25–45","https://www.trenitalia.com"),
    ("🚄","Roma → Napoli Centrale","Frecciarossa · 1h10 · desde las 06:00","€20–35","https://www.trenitalia.com"),
    ("🚂","Napoli → Pompei Scavi","Circumvesuviana · 40 min · andén subterráneo -1","€3/p","https://www.eavsrl.it"),
    ("⛵","Napoli → Positano (ferry)","SNAV/Alilauro · Molo Beverello · 65 min · solo mayo–oct","€20/p","https://www.alilauro.it"),
    ("🚌","Bus SITA Costa Amalfi","Positano ↔ Amalfi ↔ Ravello · ticket en tabacchi","€2.50/tramo","https://www.sitasudtrasporti.it"),
    ("🚄","Napoli → Venezia S. Lucia","Frecciarossa directo · 4h50 · salida 07:30","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia 24h / 48h","24h=€25 · 48h=€35 · Línea 1 = Gran Canal completo","€25–35","https://actv.avmspa.it"),
    ("⛴️","Vaporetto Venecia → Murano → Burano","Línea 12 desde Fondamente Nove · 40 min a Burano","Incluido en pase","https://actv.avmspa.it"),
    ("🚄","Venezia → Zurich HB (Alpes)","EuroCity directo · 4h45 · lado derecho del tren","€40–60","https://www.sbb.ch"),
    ("🚄","Zurich HB → Aeropuerto ZRH","SBB · 10 min · sale cada 10 min","€4","https://www.sbb.ch"),
]

TIPS = [
    ("☕","Café en la barra","Parado = €1.20. Sentado en mesa = €3–5. La ley exige mostrar ambos precios."),
    ("💧","Agua del grifo","Pedir 'acqua del rubinetto' — gratis. El agua mineral en mesa = €3–5."),
    ("🍽️","Menú del giorno","Primer + segundo + bebida + pan = €12–15. Solo almuerzo."),
    ("💳","Revolut / Wise","Sin comisiones. En Suiza cambiar a CHF. 1 CHF ≈ €1.05."),
    ("👟","Zapatos (fundamental)","10–15 km/día en adoquines. Suela firme. Zapatillas de running funcionan."),
    ("🕌","Ropa para iglesias","Hombros y rodillas cubiertos. Bufanda liviana para los dos."),
    ("🚌","Bus SITA Amalfi","Ticket en tabacchi ANTES de subir. Lado DERECHO mirando al mar."),
    ("🍦","Gelato auténtico","Colores apagados, tapado con espátula = artesanal. Fluo = industrial."),
    ("📱","Apps esenciales","Trenitalia · Italo · Maps.me offline · TheFork · SBB · Revolut."),
    ("🎾","Pádel Nuestro Roma","Día 11 tarde. Bullpadel, Siux, Babolat, Head. Pista interior."),
    ("🛍️","Ropa barata — Milán","Corso Buenos Aires. 2km de tiendas. Zara, H&M, marcas italianas."),
    ("🧀","Fondue — Zurich","Swiss Chuchi (Altstadt) ~€40/persona. Sprüngli para chocolates."),
    ("💶","Coperto en Italia","Un cargo de €1–3 por persona que aparece en la cuenta. Es legal. No es una estafa."),
    ("🔌","Enchufe Suiza (TIPO J)","Suiza usa enchufe TIPO J — diferente al italiano. Comprar adaptador en Milán."),
    ("📸","Mejor foto Manarola","Ir al mirador 15 min ANTES del sunset. Llegar temprano para conseguir lugar."),
    ("🎨","Murano vs Burano","En Murano: ver la demostración de cristal soplado (gratis en las fornaci). En Burano: ir temprano para conseguir las fotos sin turistas."),
]

FRASES_ITALIANO = [
    ("Reservación","¿Tengo una reserva a nombre de...","Ho una prenotazione a nome di...","O-una-pre-no-tah-TSYO-ne-a-NO-me-di"),
    ("Restaurante","La cuenta, por favor","Il conto, per favore","Il-KON-to-per-fa-VO-re"),
    ("Restaurante","¿Tienen menú del día?","Avete il menù del giorno?","A-VE-te-il-me-NU-del-JOR-no"),
    ("Restaurante","Agua del grifo, por favor","Acqua del rubinetto, per favore","A-KUA-del-ru-bi-NET-to"),
    ("Restaurante","Sin gluten, por favor","Senza glutine, per favore","SEN-tsa-GLU-ti-ne"),
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
    if df_res.empty or "id" not in df_res.columns:
        return {}
    r = df_res[df_res["id"]==rid]
    return r.iloc[0].to_dict() if not r.empty else {}

def get_estado(rid, default_estado):
    rd = get_rd(rid)
    return rd.get("estado", default_estado) if rd else default_estado

# ── COUNTDOWN ──────────────────────────────────────────────────────────────────
VIAJE_DATE = date(2026, 5, 24)
hoy = date.today()
dias_restantes = (VIAJE_DATE - hoy).days

# ── HERO ───────────────────────────────────────────────────────────────────────
ok_m = sum(1 for r in RESERVAS_MUSEOS if get_estado(r["id"], r["default_estado"]) in ("confirmed","paid"))
ok_a = sum(1 for r in RESERVAS_ALOJ   if get_estado(r["id"], "pending") in ("confirmed","paid"))

# Calcular total gastado incluyendo gastos manuales + alojamientos sincronizados
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
  <div class="si"><span class="sn">20</span><span class="sl2">Días totales</span></div>
  <div class="si"><span class="sn">9</span><span class="sl2">Ciudades</span></div>
</div>""")

if sheets_ok:
    M('<span class="sok">🟢 Google Sheets conectado — ambos ven los mismos datos en tiempo real</span>')
else:
    M('<span class="serr">🔴 Sin conexión — verificar credenciales en secrets.toml</span>')

st.write("")

# ── TABS ───────────────────────────────────────────────────────────────────────
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
      _ev("16:30",False,"Escala São Paulo Guarulhos (GRU)","Cambio de avión · 1h 30min de conexión · Considerar el traslado si aplica",alt=True) +
      _ev("18:00",True,"São Paulo GRU → Milán Malpensa MXP","LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día",acts='<span class="tag tr2">✈ LA8072 · B777</span>') +
      '</div>')
    M('<div class="dc"><div class="dh"><span class="dn">VUELTA</span><span class="dd">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>' +
      _ev("08:55",True,"Zurich ZRH → Milán Malpensa MXP","LA8799 op. Swiss · Avión 221 · 55min · Salir al aeropuerto a las 07:00",tip="⚠️ Tren Zurich HB → ZRH: 10 min, sale cada 10 min. Alarma 06:00.",acts='<span class="tag tr2">✈ LA8799 · Swiss</span>') +
      _ev("09:50",False,"Escala Milán Malpensa (MXP)","Cambio de avión · 3h 10min de conexión",alt=True) +
      _ev("13:00",True,"Milán MXP → São Paulo GRU","LA8073 op. LATAM Brasil · Boeing 773 · 12h",acts='<span class="tag tr2">✈ LA8073 · B777</span>') +
      _ev("20:00",False,"Escala São Paulo Guarulhos (GRU)","Cambio de avión · 2h 20min de conexión",alt=True) +
      _ev("22:20",True,"São Paulo GRU → Foz de Iguazú IGU","LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día",acts='<span class="tag tr2">✈ LA3206 · A321</span>') +
      '</div>')
    _al("<strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno. Primer día: guardar equipaje, almuerzo tranquilo, siesta obligatoria 2–3h, paseo suave al atardecer por Navigli. No planificar actividades intensas.")

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("", list(CIUDAD_FN.keys()), horizontal=True, label_visibility="collapsed")
    M(f'<div class="sh" style="margin-top:0.75rem"><div class="sh-t">{ciudad_sel}</div></div>')
    CIUDAD_FN[ciudad_sel]()

# ══ MAPA ═════════════════════════════════════════════════════════════════════
with tab_mapa:
    M('<div class="sh"><div class="sh-t">🌍 Ruta completa — La U</div><div class="sh-m">Milán → Cinque Terre → Florencia/Pisa → Roma → Nápoles → Amalfi → Venecia → Zurich</div></div>')
    m = folium.Map(location=[44.5, 11.5], zoom_start=5, tiles="CartoDB positron")
    coords = [(c["lat"], c["lon"]) for c in RUTA_MAPA]
    folium.PolyLine(coords, color="#C4693A", weight=3, opacity=0.7, dash_array="8 4").add_to(m)
    for c in RUTA_MAPA:
        color = c["color"]
        popup_html = f'<div style="font-family:DM Sans,sans-serif;min-width:140px"><div style="font-size:1.1rem;margin-bottom:4px">{c["emoji"]} <strong>{c["city"]}</strong></div><div style="font-size:0.78rem;color:#6B7A8D">{c["dias"]}</div></div>'
        folium.CircleMarker(location=[c["lat"],c["lon"]],radius=10 if "excursión" not in c["dias"] else 7,
            color=color,fill=True,fill_color=color,fill_opacity=0.9,
            popup=folium.Popup(popup_html,max_width=180),tooltip=f'{c["emoji"]} {c["city"]} · {c["dias"]}').add_to(m)
        if "excursión" not in c["dias"]:
            folium.Marker(location=[c["lat"]+0.15,c["lon"]],
                icon=folium.DivIcon(html=f'<div style="font-size:0.65rem;font-weight:700;color:{color};white-space:nowrap;background:white;padding:1px 4px;border-radius:4px;border:1px solid {color}">{c["city"]}</div>',
                icon_size=(80,20),icon_anchor=(40,10))).add_to(m)
    st_folium(m, width=None, height=500, returned_objects=[])
    M("""<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem">
    <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem"><span style="width:12px;height:12px;background:#C4693A;border-radius:50%;display:inline-block"></span>Ciudades principales</div>
    <div style="display:flex;align-items:center;gap:6px;font-size:0.78rem"><span style="width:12px;height:12px;background:#C9A84C;border-radius:50%;display:inline-block"></span>Excursiones de día</div>
    </div>""")

# ══ CLIMA ════════════════════════════════════════════════════════════════════
with tab_clima:
    M('<div class="sh"><div class="sh-t">🌤️ Clima durante el viaje</div><div class="sh-m">Pronóstico para la fecha de llegada a cada ciudad · API Open-Meteo</div></div>')
    _al("<strong>ℹ️ Nota:</strong> A medida que se acerque la fecha, los datos serán más precisos. Las temperaturas de mayo/junio en Italia son ideales: 22–28°C.")
    cols = st.columns(4)
    for i,(nombre,datos) in enumerate(CIUDADES_CLIMA.items()):
        with cols[i%4]:
            clima = get_clima(datos["lat"],datos["lon"],datos["fecha"])
            if clima:
                desc = WMO_CODES.get(clima["code"],"🌤️")
                desc_icon = desc.split()[0]
                desc_text = " ".join(desc.split()[1:])
                rain_html = f'<div style="font-size:0.7rem;color:#4285F4;margin-top:3px">Lluvia: {clima["rain"]}%</div>' if clima["rain"] else ""
                M(f'<div class="clima-card"><div style="font-size:1.4rem">{desc_icon}</div><div class="clima-temp">{clima["max"]}°</div><div style="font-size:0.72rem;color:#6B7A8D">Mín {clima["min"]}°C · Máx {clima["max"]}°C</div><div class="clima-city"><strong>{nombre}</strong><br>{datos["fecha"]}</div><div class="clima-desc">{desc_text}</div>{rain_html}</div>')
            else:
                M(f'<div class="clima-card"><div style="font-size:1.4rem">🌤️</div><div class="clima-city"><strong>{nombre}</strong><br>{datos["fecha"]}</div><div style="font-size:0.72rem;color:#6B7A8D;margin-top:4px">Disponible cuando se acerque la fecha</div></div>')
            st.write("")

# ══ MUSEOS ════════════════════════════════════════════════════════════════════
with tab_museos:
    M('<div class="sh"><div class="sh-t">🎟️ Museos y Entradas</div><div class="sh-m">Reservar en el sitio oficial · Los marcados con ✅ ya están comprados y confirmados</div></div>')
    _al("<strong>⚠️ Urgente pendiente:</strong> La Última Cena (Milán), Galería Borghese (Roma) y Torre de Pisa. Gestionar hoy.")
    _al("<strong>✅ Ya comprados:</strong> Museos Vaticanos · Coliseo + Foro Romano · David (Accademia). No hacer nada con estos.", "alg")

    for r in RESERVAS_MUSEOS:
        rd = get_rd(r["id"])
        ea = rd.get("estado", r["default_estado"]) if rd else r["default_estado"]
        conf_saved = rd.get("confirmacion", r["default_conf"]) if rd else r["default_conf"]
        monto_saved = float(rd.get("monto", r["default_monto"]) or r["default_monto"]) if rd else float(r["default_monto"])
        notas_saved = rd.get("notas_int","") if rd else ""

        bl = {"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll = {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        cc = "done" if ea == "paid" else ("urg" if r["urgente"] else "ok")
        conf_html = (f'<div style="font-size:0.72rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:2px 8px;border-radius:8px;margin-top:4px;display:inline-block">✓ {conf_saved}</div>') if conf_saved else ""

        M(f'<div class="rc {cc}"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px"><span style="font-size:0.68rem;padding:1px 7px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span><span class="rtitle">{"⚠️ " if r["urgente"] else ""}{"✅ " if ea=="paid" else ""}{r["title"]}</span><span class="{bl}">{ll}</span></div><div class="rmeta">📅 {r["fecha"]}</div>{conf_html}<div style="margin-top:6px"><a href="{r["url"]}" target="_blank" class="lb bt">🔗 Ir a reservar</a> <a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a></div></div>')

        if ea != "paid":
            with st.form(key=f"fm_{r['id']}"):
                c1,c2,c3 = st.columns([2,2,1])
                with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"se_{r['id']}")
                with c2: nc=st.text_input("N° confirmación",value=conf_saved,key=f"ce_{r['id']}",placeholder="ej. ABC123456")
                with c3: nm=st.number_input("€",value=monto_saved,min_value=0.0,step=1.0,key=f"me_{r['id']}")
                nn=st.text_area("Notas",value=notas_saved,key=f"ne_{r['id']}",height=50,placeholder="Ej: horario 09:15, 2 personas...")
                if st.form_submit_button("💾 Guardar",use_container_width=True):
                    if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn):
                        st.success("✅ Guardado"); st.rerun()
        else:
            with st.expander("✏️ Editar datos si es necesario"):
                with st.form(key=f"fm_edit_{r['id']}"):
                    c1,c2,c3 = st.columns([2,2,1])
                    with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"spe_{r['id']}")
                    with c2: nc=st.text_input("N° confirmación",value=conf_saved,key=f"cpe_{r['id']}")
                    with c3: nm=st.number_input("€",value=monto_saved,min_value=0.0,step=1.0,key=f"mpe_{r['id']}")
                    nn=st.text_area("Notas",value=notas_saved,key=f"npe_{r['id']}",height=50)
                    if st.form_submit_button("💾 Actualizar",use_container_width=True):
                        if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn):
                            st.success("✅ Actualizado"); st.rerun()
        st.write("")

# ══ ALOJAMIENTOS ══════════════════════════════════════════════════════════════
with tab_aloj:
    M('<div class="sh"><div class="sh-t">🏨 Alojamientos</div><div class="sh-m">Reservá en Airbnb o Booking · Cargá la URL confirmada · Tu pareja la ve al instante</div></div>')
    _al("<strong>💡 Cómo usar:</strong> Buscá con los links → cuando confirmes → copiá la URL de la reserva → pegala aquí → Guardar. Tu pareja verá todo al instante.", "alb")
    _al("<strong>💰 Sincronización automática:</strong> Al guardar el monto de un alojamiento, se refleja automáticamente en el Tracker de Gastos. No hace falta cargarlo dos veces.", "alg")

    for r in RESERVAS_ALOJ:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending") if rd else "pending"
        tipo_saved=str(rd.get("tipo","")) if rd else ""
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva","")) if rd else ""
        uh=f'<div class="usaved">🔗 {us[:70]}{"..." if len(us)>70 else ""}</div>' if us else ""
        tipo_html=(f'<span style="font-size:0.68rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:1px 7px;border-radius:20px">{tipo_saved}</span>') if tipo_saved else ""
        ba_html = f'<a href="{r["url_a"]}" target="_blank" class="lb ba">🏠 Airbnb</a>' if r["url_a"] else ""
        
        # Mostrar monto actual si ya fue guardado
        monto_actual = float(rd.get("monto", 0) or 0) if rd else 0
        monto_html = f'<span style="font-size:0.78rem;font-weight:700;color:#1A6B32;background:rgba(107,122,62,0.1);padding:2px 10px;border-radius:20px;margin-left:6px">€{monto_actual:,.0f} pagado</span>' if monto_actual > 0 else ""
        
        M(f'<div class="rc ok"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px"><span class="rtitle">🏨 {r["city"]} — {r["noches"]} noches</span><span class="{bl}">{ll}</span>{tipo_html}{monto_html}</div><div class="rmeta">📅 {r["fecha"]} · ~{r["precio"]}</div>{uh}<div style="margin-top:6px"><a href="{r["url_b"]}" target="_blank" class="lb bk">📅 Booking</a> {ba_html} <a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a></div></div>')
        with st.form(key=f"fa_{r['id']}"):
            c1,c2=st.columns(2)
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"sa_{r['id']}")
            with c2: tipo=st.selectbox("Reservado en",["","Airbnb","Booking.com","Directo / Otro"],index=["","Airbnb","Booking.com","Directo / Otro"].index(tipo_saved) if tipo_saved in ["","Airbnb","Booking.com","Directo / Otro"] else 0,key=f"ta_{r['id']}")
            nu=st.text_input("🔗 URL de la reserva confirmada",value=us,key=f"ua_{r['id']}",placeholder="Ej: https://www.airbnb.com/trips/v1/XXXXXXX")
            c3,c4=st.columns(2)
            with c3: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","") if rd else ""),key=f"ca_{r['id']}",placeholder="ej. HB-123456789")
            with c4: nm=st.number_input("Monto total € (→ se suma a Gastos automáticamente)",value=float(rd.get("monto",0) or 0 if rd else 0),min_value=0.0,step=1.0,key=f"ma_{r['id']}")
            nn=st.text_area("Notas",value=str(rd.get("notas_int","") if rd else ""),key=f"na_{r['id']}",height=50,placeholder="Ej: Check-in 15hs · Pedir habitación alta...")
            if st.form_submit_button("💾 Guardar — tu pareja lo ve al instante",use_container_width=True):
                if save_res(r["id"],ne,tipo,nu,nc,nm,nn):
                    st.success("✅ Guardado — visible ahora y en Gastos"); st.rerun()
        st.write("")

# ══ TRANSPORTES ══════════════════════════════════════════════════════════════
with tab_trans:
    M('<div class="sh"><div class="sh-t">Transportes</div><div class="sh-m">En orden cronológico · Con links de compra</div></div>')
    _al("<strong>💡 Truco:</strong> Comprar con 60 días de anticipación puede ser 4x más barato. Frecciarossa Roma→Nápoles: €9 anticipado vs €55 último momento.", "alg")
    for icon,route,detail,price,url in TRANSPORTES:
        _tcard(icon,route,detail,price,url)

# ══ GASTOS ═══════════════════════════════════════════════════════════════════
with tab_gas_t:
    M('<div class="sh"><div class="sh-t">Tracker de Gastos</div><div class="sh-m">Los alojamientos se sincronizan automáticamente · Agregá gastos adicionales aquí</div></div>')
    PRES=4350.0
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
    _al("<strong>ℹ️ Nota:</strong> Los alojamientos cargados en la pestaña Hoteles aparecen aquí automáticamente con prefijo <code>res_</code>. No hace falta duplicarlos.", "alb")
    with st.form("fg"):
        cd,cc2,cm=st.columns([3,2,1])
        with cd: gd=st.text_input("Descripción",placeholder="ej. Trenes Trenitalia · Entradas Uffizi")
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
        di=st.text_input("ID a eliminar (solo gastos manuales — NO eliminar los res_XXX)",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar") and di:
            if di.strip().startswith("res_"):
                st.warning("⚠️ Los gastos de alojamiento (res_XXX) se gestionan desde la pestaña Hoteles.")
            else:
                if del_g(di.strip()): st.success("Eliminado ✓"); st.rerun()
    else: st.info("Aún no hay gastos. ¡Cargá el primero desde Hoteles o aquí!")

# ══ PRESUPUESTO ══════════════════════════════════════════════════════════════
with tab_pres:
    M('<div class="sh"><div class="sh-t">Presupuesto estimado</div><div class="sh-m">Para 2 personas · 20 días · Sin vuelos</div></div>')
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🏨 Alojamiento","~€1.790","20 noches · €90 prom.")
    c2.metric("🚄 Transportes","~€500","Trenes + ferries")
    c3.metric("🎟️ Entradas","~€350","Para 2 personas")
    c4.metric("🍽️ Comidas","~€1.200","€60/día")
    st.write("")
    c5,c6=st.columns(2)
    c5.metric("🛍️ Extras","~€400","Compras, pádel, etc.")
    c6.metric("💶 TOTAL","~€4.240","Para 2 · sin vuelos")
    st.write("")
    PRES_FILAS=[
        ("Milán","2","€80","€160"),("La Spezia","2","€75","€150"),
        ("Florencia","4","€100","€400"),("Roma","4","€88","€350"),
        ("Nápoles","1","€80","€80"),("Costa Amalfi","2","€92","€185"),
        ("Venecia","2","€100","€200"),("Zurich","3","€100","€300"),
        ("TOTAL","20","~€91","~€1.825"),
    ]
    rows="".join(f'<tr{"class=tot" if c=="TOTAL" else ""}><td>{c}</td><td style="text-align:center">{n}</td><td style="text-align:center">{p}</td><td style="text-align:center;font-weight:700">{t}</td></tr>' for c,n,p,t in PRES_FILAS)
    M(f'<div style="border:1px solid #EDE7DC;border-radius:10px;overflow:hidden"><table class="bta"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th><th style="text-align:center">€/noche</th><th style="text-align:center">Total</th></tr></thead><tbody>{rows}</tbody></table></div>')
    st.write("")
    st.markdown("**Calculadora de coperto**")
    col1,col2,col3=st.columns(3)
    with col1: cuenta=st.number_input("Cuenta €",min_value=0.0,step=0.50,value=40.0)
    with col2: coperto=st.number_input("Coperto €/persona",min_value=0.0,step=0.50,value=2.0)
    with col3: personas=st.number_input("Personas",min_value=1,max_value=10,value=2)
    total_real=cuenta+(coperto*personas)
    M(f'<div class="al alg" style="text-align:center;font-size:1rem"><strong>Total a pagar: €{total_real:.2f}</strong> (cuenta €{cuenta:.2f} + coperto €{coperto*personas:.2f})</div>')

# ══ CHECKLIST ════════════════════════════════════════════════════════════════
with tab_chk_t:
    M('<div class="sh"><div class="sh-t">✅ Checklist Pre-Viaje</div><div class="sh-m">Marcá cada item como completado — ambos ven el progreso en tiempo real</div></div>')
    if not df_chk.empty and "item" in df_chk.columns:
        done_count=len(df_chk[df_chk["done"].astype(str)=="1"])
        total_count=len(df_chk)
        pct_chk=int(done_count/total_count*100) if total_count>0 else 0
        M(f'<div class="prog-o"><div class="prog-i" style="width:{pct_chk}%"></div></div><div style="font-size:0.78rem;color:#6B7A8D;margin:4px 0 1rem">{done_count} de {total_count} items completados ({pct_chk}%)</div>')
        cats_chk=df_chk["categoria"].unique() if "categoria" in df_chk.columns else []
        for cat in cats_chk:
            items=df_chk[df_chk["categoria"]==cat]
            cat_done=len(items[items["done"].astype(str)=="1"])
            M(f'<div style="font-size:0.78rem;font-weight:700;color:#3D4A5C;margin:1rem 0 4px">{cat} ({cat_done}/{len(items)})</div><div class="dc" style="margin-bottom:0.5rem">')
            for _,item in items.iterrows():
                is_done=str(item.get("done","0"))=="1"
                icon="✅" if is_done else "⬜"
                style="opacity:0.5;text-decoration:line-through" if is_done else ""
                item_id=str(item.get("id",""))
                M(f'<div class="check-item" style="{style}">{icon} {item.get("item","")}</div>')
                if st.button(f"{'↩️ Desmarcar' if is_done else '✅ Marcar'}",key=f"chk_{item_id}"):
                    if toggle_check(item_id,item.get("done","0")): st.rerun()
            M('</div>')
    else:
        st.info("Cargando checklist...")
        if st.button("🔄 Inicializar checklist"):
            init_checklist(); st.rerun()

# ══ FRASES ═══════════════════════════════════════════════════════════════════
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
        M('<div style="font-size:1rem;font-weight:700;color:#3D4A5C;margin-bottom:0.75rem">🇨🇭 Alemán suizo (Zurich)</div>')
        for _,es,de,fon in FRASES_SUIZO:
            M(f'<div class="frase-card"><div class="frase-es">{es}</div><div class="frase-it">{de}</div><div class="frase-fn">🔊 {fon}</div></div>')
    _al("<strong>💡 Tip:</strong> Lo que agrada a los italianos es intentar aunque sea 'Grazie' y 'Per favore'. En Zurich la mayoría habla inglés perfectamente.", "alb")

# ══ TIPS ═════════════════════════════════════════════════════════════════════
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
        with ca: naut=st.selectbox("Quién",["Adilson","Esposa"])
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
