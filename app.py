import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

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
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--w)!important;color:var(--ink)!important;border:1px solid var(--pa)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stNumberInput label{color:#3D4A5C!important;font-size:0.82rem!important;font-weight:500!important;}
.stSelectbox>div>div,[data-baseweb="select"],[data-baseweb="select"] *{background:var(--w)!important;color:var(--ink)!important;}
.stButton>button{background:var(--te)!important;color:var(--w)!important;border:none!important;border-radius:8px!important;font-weight:600!important;}
.stButton>button:hover{background:var(--td)!important;}
[data-testid="stMetric"]{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.75rem!important;}
[data-testid="stMetricLabel"] p{color:var(--sl)!important;font-size:0.75rem!important;}
[data-testid="stMetricValue"]{color:var(--td)!important;}
[data-testid="stMetricDelta"]{color:var(--ol)!important;}
@media(max-width:640px){[data-testid="block-container"]{padding:0.5rem!important;}}

.hero{background:linear-gradient(135deg,#3D4A5C 0%,#1A1A2E 100%);border-radius:14px 14px 0 0;padding:1.75rem 1.25rem 1.5rem;text-align:center;}
.htitle{font-family:'Playfair Display',serif!important;font-size:2.2rem!important;color:#F7F3EE!important;margin-bottom:4px;line-height:1.1;}
.htitle em{color:#E8C96A!important;font-style:italic;}
.hsub{font-size:0.85rem!important;color:rgba(247,243,238,0.6)!important;margin-bottom:1rem;}
.hdates{display:inline-block;background:rgba(247,243,238,0.1);border:0.5px solid rgba(247,243,238,0.2);border-radius:50px;padding:0.35rem 1rem;font-size:0.78rem!important;color:#E8C96A!important;}
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

/* ITINERARIO */
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
.tr2{background:#E8F0FB;color:#2A5FAC!important;}
.tw{background:#EBF5E1;color:#3A6B18!important;}
.tf{background:#FDE8DE;color:#8B3E1E!important;}
.tm{background:#F5E8F5;color:#7A3A8C!important;}
.ts{background:#FFF0E0;color:#8B5010!important;}
.tb{background:#E0F4EF;color:#0F6E56!important;}
.tsl{background:#EEF0FD;color:#4A50B0!important;}
.tbu{background:#FEF3E2;color:#8B5E10!important;}
.tpa{background:#E8F5E8;color:#2A6B2A!important;}
.tkt{background:#FCEBEB;color:#A32D2D!important;}
a.lb{display:inline-block;font-size:0.7rem;padding:3px 9px;border-radius:6px;border:1.5px solid;text-decoration:none!important;font-weight:600;background:var(--w);}
a.bm{border-color:#4285F4;color:#4285F4!important;}
a.bk{border-color:#003580;color:#003580!important;}
a.ba{border-color:#FF5A5F;color:#FF5A5F!important;}
a.bt{border-color:var(--ol);color:var(--ol)!important;}
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
.rc.urg{border-left-color:var(--te);}
.rc.ok{border-left-color:var(--ol);}
.rtitle{font-size:0.88rem!important;font-weight:700;color:var(--ink)!important;}
.rmeta{font-size:0.74rem!important;color:var(--sl)!important;margin:2px 0 5px;}
.bp{background:#FEF3CD;color:#8B6914!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.bc{background:#D4EDDA;color:#1A6B32!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.bpa{background:#CCE5FF;color:#0056B3!important;padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:700;}
.usaved{font-size:0.72rem!important;color:#0056B3!important;word-break:break-all;}
.ncard{background:var(--cr);border-radius:8px;padding:9px 12px;margin-bottom:6px;border-left:3px solid var(--go);font-size:0.82rem!important;}
.nmeta{font-size:0.68rem!important;color:var(--sl)!important;margin-top:4px;}
.tipcard{background:var(--w);border:1px solid var(--pa);border-radius:10px;padding:0.85rem;margin-bottom:0.6rem;}
.prog-o{background:var(--pa);border-radius:4px;height:7px;overflow:hidden;margin:5px 0;}
.prog-i{height:100%;border-radius:4px;background:var(--te);}
.bt{width:100%;border-collapse:collapse;font-size:0.82rem;}
.bt th{text-align:left;padding:8px 10px;background:var(--pa);color:#3D4A5C!important;font-weight:700;font-size:0.68rem;text-transform:uppercase;}
.bt td{padding:8px 10px;border-bottom:1px solid var(--pa);color:var(--ink)!important;}
.bt tr.tot td{font-weight:700;color:var(--td)!important;border-top:2px solid #E8956D;border-bottom:none;}
</style>""", unsafe_allow_html=True)

# ── SHEETS ────────────────────────────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def get_wb():
    c = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(c).open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets():
    wb = get_wb(); ex = [s.title for s in wb.worksheets()]
    needed = {
        "viaje_reservas":["id","estado","tipo","url_reserva","confirmacion","monto","notas_int","updated"],
        "viaje_gastos":["id","descripcion","categoria","monto","fecha"],
        "viaje_notas":["id","texto","tag","autor","fecha"],
    }
    out = {}
    for n,h in needed.items():
        if n not in ex:
            ws = wb.add_worksheet(title=n,rows=500,cols=len(h)); ws.append_row(h)
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

def save_res(rid,estado,tipo,url,conf,monto,notas):
    try:
        ws = ensure_sheets()["viaje_reservas"]; recs = ws.get_all_records()
        now = datetime.now().strftime("%Y-%m-%d %H:%M"); row = [rid,estado,tipo,url,conf,monto,notas,now]
        for i,r in enumerate(recs,start=2):
            if r.get("id")==rid:
                ws.update(f"A{i}:H{i}",[row]); st.cache_data.clear(); return True
        ws.append_row(row); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def add_g(desc,cat,monto):
    try:
        gid = f"g{datetime.now().strftime('%m%d%H%M%S')}"
        ensure_sheets()["viaje_gastos"].append_row([gid,desc,cat,monto,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_g(gid):
    try:
        ws = ensure_sheets()["viaje_gastos"]
        for i,r in enumerate(ws.get_all_records(),start=2):
            if str(r.get("id"))==str(gid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass; return False

def add_nota(texto,tag,autor):
    try:
        nid = f"n{datetime.now().strftime('%m%d%H%M%S')}"
        ensure_sheets()["viaje_notas"].append_row([nid,texto,tag,autor,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_nota(nid):
    try:
        ws = ensure_sheets()["viaje_notas"]
        for i,r in enumerate(ws.get_all_records(),start=2):
            if str(r.get("id"))==str(nid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass; return False

# ── RENDER: cada evento es HTML COMPLETO y LITERAL ───────────────────────────
# Ninguna variable Python se interpola dentro de la parte de tags/btns.
# Todo el HTML de cada evento se escribe directamente como string.

def M(html):
    """Wrapper de st.markdown con unsafe_allow_html siempre True."""
    st.markdown(html, unsafe_allow_html=True)

# Constantes de HTML para no repetir
_DOT  = '<div class="dot"></div>'
_DOTH = '<div class="dot hi"></div>'

def _ev(hora, hi, titulo, desc, tip="", acts="", alt=False):
    """Construye HTML de una fila. acts ya es HTML literal COMPLETO."""
    dot   = _DOTH if hi else _DOT
    tcls  = 'class="et star"' if hi else 'class="et"'
    acls  = ' ab' if alt else ''
    tip_h = f'<div class="etip">{tip}</div>' if tip else ''
    acts_h= f'<div class="acts">{acts}</div>' if acts else ''
    return (
        f'<div class="ev{acls}">'
        f'<div class="ev-t">{hora}</div>{dot}'
        f'<div class="eb"><div {tcls}>{titulo}</div>'
        f'<div class="ed">{desc}</div>{tip_h}{acts_h}</div></div>'
    )

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

# ── ITINERARIO: HTML 100% HARDCODEADO ─────────────────────────────────────────
# Cada evento tiene sus tags y botones escritos como HTML literal,
# NO como variables Python. Esto garantiza que Streamlit nunca escape nada.

def render_milan():
    _hotel("Hotel Ariston ★★★ (o similar zona Centrale/Navigli)",
           "Central para metro · Desayuno incluido · Habitación doble<br>Alternativa premium: Hotel Dei Cavalieri (~€110/noche, junto al Duomo)",
           "~€70–90 / noche · 3 noches",
           "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2",
           "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2",
           "https://maps.google.com/?q=Hotel+Ariston+Milan")

    _card("Día 1","Lunes 25 mayo — Llegada y primer paseo","Milán",
        _ev("10:15",True,"Llegada MXP — Inmigración y aduana",
            "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta.") +
        _ev("11:30",False,"Malpensa Express → Milano Centrale",
            "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.",
            acts='<span class="tag tr2">🚄 €13/persona</span>'
                 '<a href="https://www.trenord.it" target="_blank" class="lb btr">Trenord</a>'
                 '<a href="https://maps.google.com/?q=Milano+Centrale" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:30",False,"Check-in + almuerzo tranquilo",
            "Risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones.",
            acts='<span class="tag tf">🍝 Risotto</span>') +
        _ev("15:00",False,"Siesta obligatoria",
            "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes.") +
        _ev("18:00",False,"Paseo Navigli + Aperitivo",
            "Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.",
            acts='<span class="tag tw">🚶 Paseo</span>'
                 '<a href="https://maps.google.com/?q=Navigli+Milan" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 2","Martes 26 mayo — Última Cena, Duomo, Shopping y Pádel","Milán",
        _ev("08:00",False,"Desayuno italiano",
            "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.",
            acts='<span class="tag tf">☕ €3</span>') +
        _ev("08:15",True,"LA ÚLTIMA CENA — Santa Maria delle Grazie",
            "El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.",
            tip="⚠️ CRÍTICO: Reservar hoy mismo. Los cupos de mayo se agotan meses antes.",
            acts='<span class="tag tm">🎨 €15 + €2 reserva</span>'
                 '<a href="https://cenacolodavincimilano.vivaticket.com" target="_blank" class="lb bt">🎟️ Reservar ahora</a>'
                 '<a href="https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"Duomo di Milano — terrazas",
            "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán. Reservar online.",
            acts='<span class="tag tm">⛪ €15 terraza</span>'
                 '<a href="https://ticket.duomomilano.it" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Duomo+di+Milano" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Galleria Vittorio Emanuele II + Scala",
            "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).",
            acts='<span class="tag tw">🚶 Gratis</span>'
                 '<a href="https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo en Brera",
            "Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15.",
            acts='<span class="tag tf">🍽️ €15</span>'
                 '<a href="https://maps.google.com/?q=Brera+Milan" target="_blank" class="lb bm">📍 Brera</a>') +
        _ev("15:00",True,"Shopping — Corso Buenos Aires",
            "La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas accesibles. 2km de tiendas.",
            acts='<span class="tag ts">🛍️ Ropa</span>'
                 '<a href="https://maps.google.com/?q=Corso+Buenos+Aires+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",True,"Padel Nuestro Milano (opcional)",
            "La mayor tienda de pádel del norte de Italia. Bullpadel, Siux, Adidas, Nox. Pista interior para probar palas. Está en las afueras.",
            tip="Más conveniente ir a Padel Nuestro Roma (centro, Día 12). Esta cierra 19:30.",
            acts='<span class="tag tpa">🎾 Pádel</span>'
                 '<a href="https://maps.google.com/?q=Padel+Nuestro+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",False,"Cena en Navigli",
            "Evitar restaurantes con foto en el menú en la puerta — señal de trampa turística.",
            acts='<span class="tag tf">🍷 Cena</span>'))

    _card("Día 3","Miércoles 27 mayo — Brera e Isola","Milán",
        _ev("09:00",True,"Pinacoteca di Brera",
            "Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia. Calcular 2h.",
            acts='<span class="tag tm">🎨 €15</span>'
                 '<a href="https://pinacotecabrera.org" target="_blank" class="lb bt">Reservar</a>'
                 '<a href="https://maps.google.com/?q=Pinacoteca+di+Brera+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:30",False,"Barrio Isola + Bosco Verticale",
            "El famoso bosque vertical de Stefano Boeri. El barrio Isola tiene cafés y mercaditos locales muy cool.",
            acts='<span class="tag tw">🌿 Gratis</span>'
                 '<a href="https://maps.google.com/?q=Bosco+Verticale+Milan" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo + tarde libre",
            "Zona Sant'Ambrogio (Basílica del siglo IV, gratis). Tarde para compras adicionales o descanso.") +
        _ev("19:00",False,"Preparar maletas — mañana viajan a Cinque Terre",
            "Tren 08:10 desde Milano Centrale. Poner alarma.",
            acts='<span class="tag tsl">🧳 Preparación</span>'))

def render_cinque():
    _tcard("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10 desde Milano Centrale","€25–35","https://www.trenitalia.com")
    _hotel("Hotel Firenze ★★★ (La Spezia)",
           "5 min a pie de la estación · Habitación doble · 2 noches<br>Alternativa: alojarse directamente en Monterosso al Mare",
           "~€70–80 / noche · 2 noches",
           "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2",
           "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2",
           "https://maps.google.com/?q=La+Spezia+train+station")

    _card("Día 4","Jueves 28 mayo — Riomaggiore, Manarola, Corniglia","Cinque Terre",
        _ev("11:30",False,"Llegada La Spezia — Check-in + Cinque Terre Card",
            "Comprar la Card 2 días en InfoParco o taquilla de la estación (~€29.50/persona). Incluye todos los trenes locales entre los pueblos.",
            acts='<span class="tag tkt">🎫 €29.50 · 2 días</span>'
                 '<a href="https://www.cinqueterre.eu.com/en/cinque-terre-card" target="_blank" class="lb bt">Info Card</a>') +
        _ev("12:30",True,"Riomaggiore — el más fotogénico",
            "Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà. El pesto se hace con albahaca local, piñones, parmesano y aceite ligur.",
            acts='<span class="tag tf">🍃 Pesto original</span>'
                 '<a href="https://maps.google.com/?q=Riomaggiore+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",True,"Manarola — el mirador icónico",
            "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.",
            acts='<span class="tag tw">📸 Foto icónica</span>'
                 '<a href="https://maps.google.com/?q=Manarola+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"Corniglia — vista 360°",
            "El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.",
            acts='<a href="https://maps.google.com/?q=Corniglia+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 5","Viernes 29 mayo — Vernazza, senderismo y Monterosso","Cinque Terre",
        _ev("08:00",True,"Vernazza — el más medieval",
            "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.",
            acts='<a href="https://maps.google.com/?q=Vernazza+Cinque+Terre" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",True,"Senderismo Vernazza → Monterosso (3.5 km · 2h)",
            "El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir. Llevar agua y zapatos cerrados.",
            tip="Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.",
            acts='<span class="tag tw">🥾 Trekking</span>'
                 '<a href="https://www.parconazionale5terre.it" target="_blank" class="lb bt">Estado senderos</a>') +
        _ev("14:00",False,"Monterosso — playa y anchoas",
            "El único pueblo con playa de arena real. Probar acciughe (anchoas de Monterosso). Reposeras ~€5. Agua ~22°C en junio.",
            acts='<span class="tag tw">🏖️ Playa</span>'
                 '<a href="https://maps.google.com/?q=Monterosso+al+Mare" target="_blank" class="lb bm">📍 Maps</a>'))

def render_florencia():
    _tcard("🚄","La Spezia → Firenze Santa Maria Novella","Intercity · ~2h · Salida 08:30 · Directo o cambio en Pisa","€15–20","https://www.trenitalia.com")
    _hotel("Hotel Davanzati ★★★ (recomendado)",
           "A 2 min del Duomo y Uffizi · Servicio excelente · Desayuno muy bueno<br>Alternativa: B&B Machiavelli (zona Oltrarno, ~€75/noche)",
           "~€95–110 / noche · 4 noches",
           "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2",
           "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2",
           "https://maps.google.com/?q=Hotel+Davanzati+Florence")

    _card("Día 6","Sábado 30 mayo — Duomo + Cúpula + Piazzale","Florencia",
        _ev("11:00",True,"Duomo + Cúpula de Brunelleschi",
            "463 escalones. Reservar turno online — sin reserva la fila puede ser 2–3 horas. Incluye Baptisterio y Museo del Duomo.",
            acts='<span class="tag tm">⛪ Pase ~€20</span>'
                 '<a href="https://www.ilgrandemuseodelduomo.it" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Duomo+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Mercato Centrale — almuerzo",
            "Piso superior con puestos de comida. Probar lampredotto (callos florentinos) o pasta fresca.",
            acts='<a href="https://maps.google.com/?q=Mercato+Centrale+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:30",False,"Ponte Vecchio → Oltrarno",
            "El puente más antiguo de Florencia con joyerías desde el siglo XVI. Al cruzar: el Florencia auténtico.",
            acts='<span class="tag tw">🌉 Paseo</span>'
                 '<a href="https://maps.google.com/?q=Ponte+Vecchio+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:30",True,"Piazzale Michelangelo — atardecer",
            "EL punto de vista de Florencia al atardecer. Vista panorámica de toda la ciudad. Llegar 30 min antes del sunset.",
            acts='<span class="tag tw">🌅 Gratis</span>'
                 '<a href="https://maps.google.com/?q=Piazzale+Michelangelo+Florence" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 7","Domingo 31 mayo — Uffizi + David + San Miniato","Florencia",
        _ev("08:30",True,"Galería degli Uffizi — Botticelli, Leonardo, Caravaggio",
            "El museo de arte renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA. La sala de Botticelli — visitarla primero.",
            acts='<span class="tag tm">🎨 €20 + €4 reserva</span>'
                 '<a href="https://www.uffizi.it" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Uffizi+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",True,"David de Michelangelo — Accademia",
            "5.17 metros de mármol perfecto, tallado entre 1501 y 1504. El original — el de la Piazza es una copia. 1.5h.",
            acts='<span class="tag tm">🗿 €12 + reserva</span>'
                 '<a href="https://www.uffizi.it/en/the-accademia-gallery" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Accademia+Gallery+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"San Miniato al Monte",
            "La iglesia más bella de Florencia — sobre una colina, entrada gratis. Los monjes rezan el Oficio en gregoriano a las 17:30.",
            acts='<span class="tag tw">⛪ Gratis</span>'
                 '<a href="https://maps.google.com/?q=San+Miniato+al+Monte+Florence" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 8","Lunes 1 junio — Palazzo Pitti + Boboli + Cappelle Medicee","Florencia",
        _ev("09:00",False,"Palazzo Pitti + Jardines de Boboli",
            "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina. Jardines renacentistas con gruta de Buontalenti (1583).",
            acts='<span class="tag tm">🏰 €16</span>'
                 '<a href="https://maps.google.com/?q=Palazzo+Pitti+Florence" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:00",True,"Cappelle Medicee — Michelangelo",
            "Las tumbas de los Medici con las esculturas: Aurora, Crepúsculo, Día y Noche. Menos conocidas que el David, igual de impactantes.",
            acts='<span class="tag tm">🗿 €9</span>'
                 '<a href="https://maps.google.com/?q=Cappelle+Medicee+Florence" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 9","Martes 2 junio — Siena y Val d'Orcia","Toscana",
        _ev("07:30",False,"Bus SENA desde Florencia a Siena",
            "Desde Autostazione di Firenze (frente a Santa Maria Novella). 1.5h · €9.",
            acts='<span class="tag tbu">🚌 €9</span>'
                 '<a href="https://maps.google.com/?q=Autostazione+Firenze" target="_blank" class="lb bm">📍 Bus</a>') +
        _ev("09:00",True,"Piazza del Campo + Torre del Mangia",
            "La plaza más bella de Italia en forma de concha, escenario del Palio. La Torre tiene 400 escalones y vistas impresionantes.",
            acts='<span class="tag tm">🏰 Torre €10</span>'
                 '<a href="https://maps.google.com/?q=Piazza+del+Campo+Siena" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",False,"Duomo di Siena",
            "El Duomo de Siena compite con Florencia en belleza. El pavimento de mármol con 56 escenas es único en el mundo.",
            acts='<span class="tag tm">⛪ €8</span>'
                 '<a href="https://maps.google.com/?q=Siena+Cathedral" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:30",False,"Almuerzo en la ciudad vieja",
            "Probar: pici all'aglione (pasta gruesa con ajo), cinghiale (jabalí). Siena tiene cocina muy diferente a Florencia.",
            acts='<span class="tag tf">🍖 Toscana</span>') +
        _ev("17:00",False,"Bus de regreso a Florencia",
            "Hay buses frecuentes hasta las 21:00. Cena en Florencia. Mañana viajan a Roma."))

def render_roma():
    _tcard("🚄","Firenze SMN → Roma Termini","Frecciarossa (Alta Velocidad) · 1h 30min · Sale cada 30 min · Reservar anticipado","€25–45","https://www.trenitalia.com")
    _hotel("Hotel Arco del Lauro ★★★ (Trastevere)",
           "Zona Trastevere — auténtica y central · B&B familiar · Muy buenas reseñas<br>Alternativa: zona Prati (junto al Vaticano) o Hotel Santa Prassede (~€80)",
           "~€80–95 / noche · 4 noches",
           "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2",
           "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2",
           "https://maps.google.com/?q=Trastevere+Rome")
    _al("<strong>🎾 Padel Nuestro Roma:</strong> La tienda más completa de la ruta. Centro de Roma. Bullpadel, Siux, Babolat, Head, Star Vie. Permiten probar palas. Ver Día 12.")

    _card("Día 10","Miércoles 3 junio — Vaticano completo","Roma",
        _ev("10:30",True,"Museos Vaticanos + Capilla Sixtina",
            "Los museos más visitados del mundo. 3–4h. El recorrido culmina en la Capilla Sixtina con el fresco de Miguel Ángel. RESERVA OBLIGATORIA.",
            tip="⚠️ En la Capilla Sixtina está prohibido fotografiar y hacer ruido — los guardias son estrictos. Silencio absoluto.",
            acts='<span class="tag tm">🎨 €17 + €4 reserva</span>'
                 '<a href="https://www.museivaticani.va" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Vatican+Museums+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",False,"Basílica de San Pedro + Cúpula",
            "La basílica más grande del mundo cristiano. Subir a la cúpula (551 escalones o ascensor parcial €8) para vista alucinante.",
            acts='<span class="tag tm">⛪ Gratis · Cúpula €8</span>'
                 '<a href="https://maps.google.com/?q=St+Peters+Basilica+Rome" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 11","Jueves 4 junio — Roma Imperial","Roma",
        _ev("08:00",True,"Coliseo + Foro Romano + Palatino",
            "Combo obligatorio. 3–4h. El Palatino (colina sobre el Foro) tiene las mejores vistas del Coliseo y es el menos visitado del combo — no saltearlo.",
            acts='<span class="tag tm">🏛️ €16 + reserva</span>'
                 '<a href="https://www.coopculture.it" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Colosseum+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:30",False,"Trastevere — paseo y cena",
            "El barrio medieval más pintoresco de Roma. La Basílica di Santa Maria in Trastevere (siglo XII, gratis). Cena: Da Enzo al 29.",
            acts='<span class="tag tw">🚶 Paseo</span>'
                 '<a href="https://maps.google.com/?q=Trastevere+Rome" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 12","Viernes 5 junio — Roma Barroca + Borghese + Pádel","Roma",
        _ev("09:00",False,"Pantheon → Piazza Navona → Fontana di Trevi",
            "El Pantheon (125 d.C.) requiere ticket €5 desde 2023. El óculo deja entrar la lluvia. Trevi: lanzar la moneda de espaldas con la derecha.",
            acts='<span class="tag tm">🏛️ Pantheon €5</span>'
                 '<a href="https://maps.google.com/?q=Pantheon+Rome" target="_blank" class="lb bm">📍 Pantheon</a>'
                 '<a href="https://maps.google.com/?q=Trevi+Fountain+Rome" target="_blank" class="lb bm">📍 Trevi</a>') +
        _ev("15:00",True,"Galería Borghese — Bernini",
            "El museo más exclusivo de Roma — solo 360 personas cada 2 horas. Apolo y Dafne, El rapto de Proserpina — lo más impactante de toda Roma.",
            acts='<span class="tag tm">🗿 €15 + €2 reserva</span>'
                 '<a href="https://www.galleriaborghese.it" target="_blank" class="lb bt">🎟️ Reservar</a>'
                 '<a href="https://maps.google.com/?q=Galleria+Borghese+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",True,"🎾 Padel Nuestro Roma",
            "La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Pista interior para probar palas antes de comprar.",
            acts='<span class="tag tpa">🎾 Pádel Roma</span>'
                 '<a href="https://maps.google.com/?q=Padel+Nuestro+Roma+Italy" target="_blank" class="lb bm">📍 Maps</a>'
                 '<a href="https://www.padelnuestro.com" target="_blank" class="lb bt">Web tienda</a>'))

    _card("Día 13","Sábado 6 junio — Castel Sant'Angelo + tarde libre","Roma",
        _ev("09:00",False,"Castel Sant'Angelo",
            "Mausoleo de Adriano convertido en fortaleza papal. Vista del Tiber y San Pedro desde la cima.",
            acts='<span class="tag tm">🏰 €14</span>'
                 '<a href="https://maps.google.com/?q=Castel+Sant+Angelo+Rome" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("14:00",False,"Tarde libre + preparación",
            "Compras en Via del Corso o zona Spagna. Mañana temprano: tren a Nápoles.",
            acts='<span class="tag tw">🛍️ Libre</span>'))

def render_napoles():
    _tcard("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00","€20–35","https://www.trenitalia.com")
    _hotel("Hotel Piazza Bellini ★★★ (centro histórico UNESCO)",
           "En el corazón de Spaccanapoli · 1 noche (7–8 junio)",
           "~€75–90 / noche",
           "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2",
           "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2",
           "https://maps.google.com/?q=Piazza+Bellini+Naples")

    _card("Día 14","Domingo 7 junio — Pompeya + Nápoles + Pizza","Nápoles",
        _ev("09:00",True,"Circumvesuviana → Pompeya Scavi",
            "Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento. Bajarse en 'Pompei Scavi'. Comprar ticket en máquina automática.",
            acts='<span class="tag tr2">🚂 €3 · 40min</span>'
                 '<a href="https://maps.google.com/?q=Pompei+Scavi+station" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("10:00",True,"Pompeya — ciudad sepultada por el Vesubio",
            "La ciudad romana sepultada en 79 d.C. 3h mínimo. Casa dei Vettii, Anfiteatro, Thermopolium, moldes humanos en el Granario, el Foro. Llevar agua y sombrero.",
            acts='<span class="tag tm">🌋 €16</span>'
                 '<a href="https://maps.google.com/?q=Pompeii+Archaeological+Park" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Spaccanapoli + Museo Arqueológico Nacional",
            "La calle que cruza Nápoles histórica. El Museo tiene los mejores objetos de Pompeya y Herculano del mundo — incluyendo la 'Stanza Segreta'.",
            acts='<span class="tag tm">🏺 €15</span>'
                 '<a href="https://maps.google.com/?q=National+Archaeological+Museum+Naples" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",True,"🍕 La pizza napolitana ORIGINAL",
            "Nápoles inventó la pizza. Las tres legendarias: L'Antica Pizzeria da Michele (solo Margherita y Marinara, fila larga), Sorbillo (favorita de los napolitanos), Di Matteo (en Spaccanapoli).",
            acts='<span class="tag tf">🍕 €5–8</span>'
                 '<a href="https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples" target="_blank" class="lb bm">📍 Da Michele</a>'
                 '<a href="https://maps.google.com/?q=Pizzeria+Sorbillo+Naples" target="_blank" class="lb bm">📍 Sorbillo</a>'))

def render_amalfi():
    _al("<strong>💰 Tip de presupuesto:</strong> Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200 fácilmente. Con ferry desde Praiano se llega a Positano en 10 min.")
    _tcard("⛵","Nápoles → Positano (ferry)","SNAV o Alilauro · Desde Molo Beverello · Salidas 08:30 y 09:30 · Solo mayo–oct","~€20/persona","https://www.alilauro.it")
    _hotel("Albergo California (Praiano) ★★★",
           "Vista al mar · Desayuno incluido · 10 min de Positano en ferry · 2 noches (8–10 junio)",
           "~€85–100 / noche",
           "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2",
           "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2",
           "https://maps.google.com/?q=Praiano+Amalfi+Coast")

    _card("Día 15","Lunes 8 junio — Positano + Amalfi","Costa Amalfi",
        _ev("10:30",True,"Positano — las casas en cascada",
            "El pueblo más fotogénico de la Costa. Casas de colores sobre el acantilado. Playa Grande con guijarros, reposeras ~€20 el par. Agua del Tirreno ~22°C.",
            acts='<a href="https://maps.google.com/?q=Positano+Amalfi+Coast" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",False,"Almuerzo con vista en Positano",
            "Muy caro en Positano. Buscar La Zagara o Il Ritrovo (más económico, en la colina). Probar: scialatielli ai frutti di mare (pasta fresca con mariscos).",
            acts='<span class="tag tf">🦐 Mariscos</span>') +
        _ev("15:00",True,"Bus SITA → Amalfi ciudad",
            "El bus azul recorre toda la costa. €2.50 el tramo. 40 min por la carretera más espectacular de Italia. Duomo de Amalfi (siglo IX, estilo árabe-normando).",
            tip="Comprar ticket en tabacchi ANTES de subir. Sentarse del lado DERECHO mirando al mar.",
            acts='<span class="tag tbu">🚌 €2.50</span>'
                 '<a href="https://maps.google.com/?q=Amalfi+Cathedral" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:30",False,"Cena con vista al mar",
            "El atardecer sobre el Tirreno desde la Costa Amalfi es uno de los espectáculos más bellos de Italia.",
            acts='<span class="tag tf">🌅 Scialatielli ai frutti</span>'))

    _card("Día 16","Martes 9 junio — Ravello + Sentiero degli Dei","Costa Amalfi",
        _ev("08:00",True,"Ravello — Villa Cimbrone + Terrazza dell'Infinito",
            "Ravello a 350m sobre el mar. La Terraza del Infinito es el mirador más espectacular de toda la Costa. Wagner llamó a esta vista 'el balcón más bello del mundo'.",
            acts='<span class="tag tm">🌿 €7</span>'
                 '<a href="https://maps.google.com/?q=Villa+Cimbrone+Ravello" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("11:00",True,"Sentiero degli Dei — Camino de los Dioses (7.8km · 3h)",
            "El sendero más famoso de la Costa Amalfi. Sale desde Bomerano y baja hasta Positano. Vista de toda la costa desde 600m de altura. No necesita guía.",
            tip="El trayecto baja (no sube), así que el cansancio es manejable. Es el mejor día del viaje para muchos viajeros.",
            acts='<span class="tag tw">🥾 Trekking</span>'
                 '<a href="https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:00",False,"Llegada Positano + playa merecida",
            "Después del sendero: baño en el mar, playa. Tarde libre. Mañana: ferry + tren largo a Venecia — preparar maletas.",
            acts='<span class="tag tw">🏖️ Playa</span>'))

def render_venecia():
    _tcard("🚄","Nápoles → Venezia Santa Lucia","Frecciarossa directo · 4h50 · Salida 07:30–08:00","€35–60","https://www.trenitalia.com")
    _al("<strong>Nota Venecia:</strong> Desde junio 2024, Venecia cobra €5 de 'tasa de acceso' en días pico. Verificar en comune.venezia.it. Airbnb muy regulado — hotel es la mejor opción.")
    _hotel("Hotel Dalla Mora ★★★ (Santa Croce)",
           "Zona auténtica · 10 min a pie de la estación · Venecia real, NO en Mestre (tierra firme)<br>Alternativa: B&B en Cannaregio",
           "~€90–110 / noche",
           "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2&nflt=di%3D1376",
           "", "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice")

    _card("Día 17","Miércoles 10 junio — Venecia completa","Venecia",
        _ev("13:00",True,"Gran Canal en Vaporetto línea 1 (la lenta)",
            "La línea 1 recorre todo el Gran Canal parando en cada estación. 45 minutos de palacios del siglo XIV, puentes, góndolas. El paseo más cinematográfico del viaje. Ticket 24h = €25.",
            acts='<span class="tag tb">🚤 24h = €25</span>') +
        _ev("15:00",True,"Plaza San Marcos + Basílica + Campanile",
            "Basílica siglo XI, estilo bizantino, cúpulas doradas — gratuita con espera. El Campanile (99m) ofrece la mejor vista de Venecia. €10.",
            acts='<span class="tag tm">🏛️ Gratis + €10 campanile</span>'
                 '<a href="https://maps.google.com/?q=St+Marks+Basilica+Venice" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("17:00",True,"Perderse sin mapa — la mejor actividad de Venecia",
            "Apagar Google Maps. Venecia tiene 118 islas conectadas por 400 puentes. Los callejones más angostos llevan a los campos más secretos.",
            acts='<span class="tag tw">🗺️ Sin mapa</span>') +
        _ev("19:30",False,"Spritz veneziano en bacaro + Rialto",
            "El Spritz se inventó en Venecia. Los 'bacari' son los bares tradicionales con 'cicchetti' (tapas de €1–2). Zona Cannaregio para los más auténticos.",
            acts='<span class="tag tf">🍹 Bacaro</span>'
                 '<a href="https://maps.google.com/?q=Rialto+Bridge+Venice" target="_blank" class="lb bm">📍 Rialto</a>') +
        _ev("21:00",False,"Góndola nocturna (opcional)",
            "Precio fijo oficial: €80 para 30 min (hasta 6 personas). De noche los canales sin turistas son mágicos.",
            acts='<span class="tag tb">🎭 €80 / góndola</span>'))

def render_zurich():
    _tcard("🚄","Venezia S. Lucia → Zurich HB (a través de los Alpes)","EuroCity directo · 4h45 · Paisaje alpino impresionante · Sentarse del lado DERECHO mirando norte","€40–60","https://www.sbb.ch")
    _al("⚠️ <strong>Vuelo el 14/6 a las 08:55:</strong> Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min. El día 13 preparar todo y dormir temprano.")
    _hotel("Hotel Otter ★★ (Langstrasse) o IBIS City West",
           "Zona cool y multicultural · A pie del casco histórico · 3 noches (11–14 junio)<br>Alternativa con vista: Hotel Limmatblick (~€120, sobre el río Limmat)",
           "~€90–110 / noche · 3 noches",
           "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
           "", "https://maps.google.com/?q=Langstrasse+Zurich")

    _card("Día 18","Jueves 11 junio — Llegada + Altstadt","Zurich",
        _ev("14:00",False,"Bahnhofstrasse + Lago de Zurich",
            "La calle comercial más cara del mundo. Joyerías, Rolex, bancos. El Lago al final para sentarse. Cambio mental: de caos italiano a precisión suiza.",
            acts='<span class="tag tw">⌚ Paseo</span>'
                 '<a href="https://maps.google.com/?q=Bahnhofstrasse+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("15:30",True,"Altstadt + Grossmünster",
            "La iglesia donde Zwinglio inició la Reforma Protestante en 1519. Subir las torres (€5). El barrio Niederdorf: callejuelas adoquinadas, gremios medievales, cafés.",
            acts='<a href="https://maps.google.com/?q=Grossmunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("18:00",False,"Fraumünster — vitrales de Chagall (1970)",
            "5 vitrales de Marc Chagall en un edificio del siglo XIII. Tesoro de arte moderno en arquitectura medieval. €5.",
            acts='<span class="tag tm">🎨 €5</span>'
                 '<a href="https://maps.google.com/?q=Fraumunster+Zurich" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 19","Viernes 12 junio — Lago + ETH + Fondue","Zurich",
        _ev("09:00",True,"Crucero Lago de Zurich",
            "ZSG opera cruceros. Recorrido corto 1h o largo 4h hasta Rapperswil. El lago con los Alpes de fondo es icónico.",
            acts='<span class="tag tb">⛵ €8–30</span>'
                 '<a href="https://www.zsg.ch" target="_blank" class="lb bt">ZSG</a>'
                 '<a href="https://maps.google.com/?q=Lake+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("16:00",False,"Polybahn → terraza ETH (vista gratis)",
            "El funicular universitario de 1889 sube hasta la ETH (la universidad de Einstein). Vista panorámica de Zurich, el lago y los Alpes — gratis.",
            acts='<a href="https://maps.google.com/?q=ETH+Zurich+terrace" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("20:00",True,"Fondue suiza — Swiss Chuchi",
            "La fondue de queso es el plato nacional suizo. Swiss Chuchi en el Altstadt. Experiencia completa ~€35–45/persona.",
            acts='<span class="tag tf">🧀 Fondue</span>'
                 '<a href="https://maps.google.com/?q=Swiss+Chuchi+Zurich" target="_blank" class="lb bm">📍 Maps</a>'))

    _card("Día 20","Sábado 13 junio — Uetliberg + Chocolates + Última noche","Zurich",
        _ev("09:00",False,"Uetliberg — la montaña de Zurich",
            "870m. Tren S10 desde HB, 20 min, €5. Vista de Zurich, el lago y los Alpes. Bajada por sendero a Felsenegg.",
            acts='<span class="tag tw">⛰️ €5 tren</span>'
                 '<a href="https://maps.google.com/?q=Uetliberg+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("13:00",True,"Chocolates Sprüngli + Mercado Bürkliplatz",
            "Sprüngli (desde 1836) — los mejores truffes du jour de Zurich. El mercado de Bürkliplatz los sábados tiene artesanías locales.",
            acts='<span class="tag tf">🍫 Chocolates</span>'
                 '<a href="https://maps.google.com/?q=Confiserie+Sprungli+Zurich" target="_blank" class="lb bm">📍 Maps</a>') +
        _ev("19:00",True,"Última cena del viaje 🥂",
            "Elegir el restaurante favorito de los días en Zurich. Brindar por el viaje. Hacer check-in online del vuelo LA8799.",
            acts='<span class="tag tf">🥂 Despedida</span>') +
        _ev("22:00",False,"A dormir — vuelo 08:55 mañana",
            "Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración. Estar en aeropuerto a las 07:00.",
            tip="⚠️ ALARMA 06:00. Sin excepciones.",
            acts='<span class="tag tsl">✈️ Alarma 06:00</span>'))

CIUDAD_FN = {
    "🏛️ Milán": render_milan,
    "🌊 Cinque Terre": render_cinque,
    "🌸 Florencia": render_florencia,
    "🏟️ Roma": render_roma,
    "🍕 Nápoles": render_napoles,
    "🌅 Costa Amalfi": render_amalfi,
    "🚤 Venecia": render_venecia,
    "🇨🇭 Zurich": render_zurich,
}

RESERVAS_MUSEOS = [
    {"id":"m01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url":"https://cenacolodavincimilano.vivaticket.com","maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
    {"id":"m02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url":"https://www.galleriaborghese.it","maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
    {"id":"m03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url":"https://www.museivaticani.va","maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
    {"id":"m04","title":"Cúpula Brunelleschi — Duomo Florencia","city":"Florencia","fecha":"30 mayo","urgente":True,"url":"https://www.ilgrandemuseodelduomo.it","maps":"https://maps.google.com/?q=Duomo+Florence"},
    {"id":"m05","title":"David — Accademia Florencia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url":"https://www.uffizi.it/en/the-accademia-gallery","maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
    {"id":"m06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url":"https://www.uffizi.it","maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
    {"id":"m07","title":"Coliseo + Foro Romano + Palatino","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url":"https://www.coopculture.it","maps":"https://maps.google.com/?q=Colosseum+Rome"},
]

RESERVAS_ALOJ = [
    {"id":"a01","city":"Milán","fecha":"25–28 mayo","noches":3,"precio":"€70–90/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2","url_a":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2","maps":"https://maps.google.com/?q=Milan+Italy"},
    {"id":"a02","city":"La Spezia","fecha":"28–30 mayo","noches":2,"precio":"€70–80/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2","url_a":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2","maps":"https://maps.google.com/?q=La+Spezia+Italy"},
    {"id":"a03","city":"Florencia","fecha":"30 mayo–3 junio","noches":4,"precio":"€95–110/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2","url_a":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2","maps":"https://maps.google.com/?q=Florence+Italy"},
    {"id":"a04","city":"Roma","fecha":"3–7 junio","noches":4,"precio":"€80–95/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2","url_a":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2","maps":"https://maps.google.com/?q=Trastevere+Rome"},
    {"id":"a05","city":"Nápoles","fecha":"7–8 junio","noches":1,"precio":"€75–90/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2","url_a":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2","maps":"https://maps.google.com/?q=Naples+Italy"},
    {"id":"a06","city":"Praiano / Costa Amalfi","fecha":"8–10 junio","noches":2,"precio":"€85–100/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2","url_a":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2","maps":"https://maps.google.com/?q=Praiano+Italy"},
    {"id":"a07","city":"Venecia","fecha":"10–11 junio","noches":1,"precio":"€90–110/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","url_a":"","maps":"https://maps.google.com/?q=Venice+Italy"},
    {"id":"a08","city":"Zurich","fecha":"11–14 junio","noches":3,"precio":"€90–110/noche","url_b":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","url_a":"","maps":"https://maps.google.com/?q=Zurich+Switzerland"},
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
    ("🚌","Bus SITA Costa Amalfi","Positano ↔ Amalfi ↔ Ravello · ticket en tabacchi","€2.50/tramo","https://www.sitasudtrasporti.it"),
    ("🚄","Napoli → Venezia S. Lucia","Frecciarossa directo · 4h50 · salida 07:30","€35–60","https://www.trenitalia.com"),
    ("🚤","Vaporetto Venecia 24h","Línea 1 = Gran Canal completo · Línea 2 = rápida","€25","https://actv.avmspa.it"),
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
    ("🎾","Pádel Nuestro Roma","Día 12 tarde. Bullpadel, Siux, Babolat, Head. Pista interior."),
    ("🛍️","Ropa barata — Milán","Corso Buenos Aires. 2km de tiendas. Zara, H&M, marcas italianas."),
    ("🧀","Fondue — Zurich","Swiss Chuchi (Altstadt) ~€40/persona. Sprüngli para chocolates."),
]

# ── CARGA ─────────────────────────────────────────────────────────────────────
try:
    df_res=load_r(); df_gas=load_g(); df_notas=load_n(); sheets_ok=True
except:
    df_res=df_gas=df_notas=pd.DataFrame(); sheets_ok=False

def get_rd(rid):
    if df_res.empty or "id" not in df_res.columns: return {}
    r = df_res[df_res["id"]==rid]
    return r.iloc[0].to_dict() if not r.empty else {}

# ── HERO ─────────────────────────────────────────────────────────────────────
ok_m = sum(1 for r in RESERVAS_MUSEOS if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
ok_a = sum(1 for r in RESERVAS_ALOJ   if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
total_gas = pd.to_numeric(df_gas["monto"],errors="coerce").fillna(0).sum() if not df_gas.empty and "monto" in df_gas.columns else 0

M(f"""<div class="hero">
  <div style="font-size:1.6rem;letter-spacing:6px;margin-bottom:4px">🇮🇹 🇨🇭</div>
  <div class="htitle">Italia & <em>Zurich</em></div>
  <div class="hsub">Luna de Miel · Mayo–Junio 2026 · Compartido en tiempo real</div>
  <div class="hdates">✈ Sale 24 mayo · IGU &nbsp;·&nbsp; Regresa 14 junio · ZRH</div>
</div>
<div class="sbar">
  <div class="si"><span class="sn">{ok_m}/{len(RESERVAS_MUSEOS)}</span><span class="sl2">Museos ok</span></div>
  <div class="si"><span class="sn">{ok_a}/{len(RESERVAS_ALOJ)}</span><span class="sl2">Hoteles ok</span></div>
  <div class="si"><span class="sn">€{total_gas:,.0f}</span><span class="sl2">Gastado</span></div>
  <div class="si"><span class="sn">20</span><span class="sl2">Días totales</span></div>
  <div class="si"><span class="sn">9</span><span class="sl2">Ciudades</span></div>
</div>""")

if sheets_ok:
    M('<span class="sok">🟢 Google Sheets conectado — ambos ven los mismos datos en tiempo real</span>')
else:
    M('<span class="serr">🔴 Sin conexión — verificar credenciales en secrets.toml</span>')

st.write("")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_vue,tab_itin,tab_museos,tab_aloj,tab_trans,tab_gas_t,tab_pres,tab_tips,tab_notas_t = st.tabs([
    "✈️ Vuelos","🗺️ Itinerario","🎟️ Museos","🏨 Hoteles",
    "🚄 Trenes","💰 Gastos","📊 Presup.","💡 Tips","📝 Notas"
])

# ══ VUELOS ════════════════════════════════════════════════════════════════════
with tab_vue:
    M('<div class="sh"><div class="sh-t">Vuelos confirmados</div>'
      '<div class="sh-m">LATAM + Swiss · Foz de Iguazú ↔ Zurich</div></div>')

    M('<div class="dc"><div class="dh"><span class="dn">IDA</span>'
      '<span class="dd">Domingo 24 mayo 2026 — Foz de Iguazú → Milán</span></div>' +
      _ev("14:50",True,"IGU → São Paulo GRU",
          "LA3879 op. LATAM Brasil · Airbus 320 · 1h 40min",
          acts='<span class="tag tr2">✈ LA3879 · A320</span>') +
      _ev("16:30",False,"Escala São Paulo Guarulhos (GRU)",
          "Cambio de avión · 1h 30min de conexión · Considerar el traslado si aplica", alt=True) +
      _ev("18:00",True,"São Paulo GRU → Milán Malpensa MXP",
          "LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día",
          acts='<span class="tag tr2">✈ LA8072 · B777</span>') +
      '</div>')

    M('<div class="dc"><div class="dh"><span class="dn">VUELTA</span>'
      '<span class="dd">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>' +
      _ev("08:55",True,"Zurich ZRH → Milán Malpensa MXP",
          "LA8799 op. Swiss · Avión 221 · 55min · Salir al aeropuerto a las 07:00",
          tip="⚠️ Tren Zurich HB → ZRH: 10 min, sale cada 10 min. Alarma 06:00.",
          acts='<span class="tag tr2">✈ LA8799 · Swiss</span>') +
      _ev("09:50",False,"Escala Milán Malpensa (MXP)",
          "Cambio de avión · 3h 10min de conexión", alt=True) +
      _ev("13:00",True,"Milán MXP → São Paulo GRU",
          "LA8073 op. LATAM Brasil · Boeing 773 · 12h",
          acts='<span class="tag tr2">✈ LA8073 · B777</span>') +
      _ev("20:00",False,"Escala São Paulo Guarulhos (GRU)",
          "Cambio de avión · 2h 20min de conexión", alt=True) +
      _ev("22:20",True,"São Paulo GRU → Foz de Iguazú IGU",
          "LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día",
          acts='<span class="tag tr2">✈ LA3206 · A321</span>') +
      '</div>')

    _al("<strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno desde São Paulo. Primer día: guardar equipaje, almuerzo tranquilo, siesta obligatoria 2–3h, paseo suave al atardecer por Navigli. No planificar actividades intensas.")

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("", list(CIUDAD_FN.keys()), horizontal=True, label_visibility="collapsed")
    M(f'<div class="sh" style="margin-top:0.75rem"><div class="sh-t">{ciudad_sel}</div></div>')
    CIUDAD_FN[ciudad_sel]()

# ══ MUSEOS ════════════════════════════════════════════════════════════════════
with tab_museos:
    M('<div class="sh"><div class="sh-t">🎟️ Museos y Entradas</div>'
      '<div class="sh-m">Reservar en el sitio oficial · Cargar N° de confirmación cuando esté hecho</div></div>')
    _al("<strong>⚠️ Urgente:</strong> La Última Cena, Galería Borghese y Museos Vaticanos se agotan con meses de anticipación. Gestionar hoy.")

    for r in RESERVAS_MUSEOS:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        cc="urg" if r["urgente"] else "ok"
        conf_saved=str(rd.get("confirmacion",""))
        conf_html=(f'<div style="font-size:0.72rem;color:#1A6B32;font-weight:600;background:#D4EDDA;'
                   f'padding:2px 8px;border-radius:8px;margin-top:4px;display:inline-block">✓ {conf_saved}</div>') if conf_saved else ""
        M(f'<div class="rc {cc}">'
          f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px">'
          f'<span style="font-size:0.68rem;padding:1px 7px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span>'
          f'<span class="rtitle">{"⚠️ " if r["urgente"] else ""}{r["title"]}</span>'
          f'<span class="{bl}">{ll}</span></div>'
          f'<div class="rmeta">📅 {r["fecha"]}</div>'
          f'{conf_html}'
          f'<div style="margin-top:6px">'
          f'<a href="{r["url"]}" target="_blank" class="lb bt">🔗 Ir a reservar</a> '
          f'<a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a>'
          f'</div></div>')
        with st.form(key=f"fm_{r['id']}"):
            c1,c2,c3=st.columns([2,2,1])
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"se_{r['id']}")
            with c2: nc=st.text_input("N° confirmación",value=conf_saved,key=f"ce_{r['id']}",placeholder="ej. ABC123456")
            with c3: nm=st.number_input("€",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"me_{r['id']}")
            nn=st.text_area("Notas",value=str(rd.get("notas_int","")),key=f"ne_{r['id']}",height=50,placeholder="Ej: horario 09:15, 2 personas...")
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn):
                    st.success("✅ Guardado"); st.rerun()
        st.write("")

# ══ ALOJAMIENTOS ══════════════════════════════════════════════════════════════
with tab_aloj:
    M('<div class="sh"><div class="sh-t">🏨 Alojamientos</div>'
      '<div class="sh-m">Reservá en Airbnb o Booking · Cargá la URL confirmada · Tu pareja la ve al instante</div></div>')
    _al("<strong>💡 Cómo usar:</strong> Buscá con los links → cuando confirmes → copiá la URL de la reserva → pegala aquí → Guardar. Tu pareja verá todo al instante.", "alb")

    for r in RESERVAS_ALOJ:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        tipo_saved=str(rd.get("tipo",""))
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva",""))
        uh=f'<div class="usaved">🔗 {us[:70]}{"..." if len(us)>70 else ""}</div>' if us else ""
        tipo_html=(f'<span style="font-size:0.68rem;color:#1A6B32;font-weight:600;background:#D4EDDA;'
                   f'padding:1px 7px;border-radius:20px">{tipo_saved}</span>') if tipo_saved else ""
        ba_html = f'<a href="{r["url_a"]}" target="_blank" class="lb ba">🏠 Airbnb</a>' if r["url_a"] else ""
        M(f'<div class="rc ok">'
          f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px">'
          f'<span class="rtitle">🏨 {r["city"]} — {r["noches"]} noches</span>'
          f'<span class="{bl}">{ll}</span>{tipo_html}</div>'
          f'<div class="rmeta">📅 {r["fecha"]} · ~{r["precio"]}</div>'
          f'{uh}'
          f'<div style="margin-top:6px">'
          f'<a href="{r["url_b"]}" target="_blank" class="lb bk">📅 Booking</a> '
          f'{ba_html}'
          f'<a href="{r["maps"]}" target="_blank" class="lb bm">📍 Maps</a>'
          f'</div></div>')
        with st.form(key=f"fa_{r['id']}"):
            c1,c2=st.columns(2)
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],index=["pending","confirmed","paid"].index(ea),format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],key=f"sa_{r['id']}")
            with c2: tipo=st.selectbox("Reservado en",["","Airbnb","Booking.com","Directo / Otro"],index=["","Airbnb","Booking.com","Directo / Otro"].index(tipo_saved) if tipo_saved in ["","Airbnb","Booking.com","Directo / Otro"] else 0,key=f"ta_{r['id']}")
            nu=st.text_input("🔗 URL de la reserva confirmada",value=us,key=f"ua_{r['id']}",placeholder="Ej: https://www.airbnb.com/trips/v1/XXXXXXX")
            c3,c4=st.columns(2)
            with c3: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","")),key=f"ca_{r['id']}",placeholder="ej. HB-123456789")
            with c4: nm=st.number_input("Monto total €",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"ma_{r['id']}")
            nn=st.text_area("Notas",value=str(rd.get("notas_int","")),key=f"na_{r['id']}",height=50,placeholder="Ej: Check-in 15hs · Pedir habitación alta · Desayuno incluido...")
            if st.form_submit_button("💾 Guardar — tu pareja lo ve al instante",use_container_width=True):
                if save_res(r["id"],ne,tipo,nu,nc,nm,nn):
                    st.success("✅ Guardado — visible ahora"); st.rerun()
        st.write("")

# ══ TRANSPORTES ═══════════════════════════════════════════════════════════════
with tab_trans:
    M('<div class="sh"><div class="sh-t">Transportes</div>'
      '<div class="sh-m">En orden cronológico · Con links de compra</div></div>')
    _al("<strong>💡 Truco:</strong> Comprar con 60 días de anticipación puede ser 4x más barato. Frecciarossa Roma→Nápoles: €9 anticipado vs €55 último momento.", "alg")
    for icon,route,detail,price,url in TRANSPORTES:
        _tcard(icon,route,detail,price,url)

# ══ GASTOS ════════════════════════════════════════════════════════════════════
with tab_gas_t:
    M('<div class="sh"><div class="sh-t">Tracker de Gastos</div>'
      '<div class="sh-m">Cargá cada gasto — ambos lo ven en tiempo real</div></div>')
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
    M(f'<div class="prog-o"><div class="prog-i" style="width:{pct}%"></div></div>'
      f'<div style="font-size:0.72rem;color:#6B7A8D;margin-top:3px">€{tg:,.0f} de €{PRES:,.0f} presupuestados ({pct}%)</div>')
    st.write("")
    with st.form("fg"):
        cd,cc2,cm=st.columns([3,2,1])
        with cd: gd=st.text_input("Descripción",placeholder="ej. Airbnb Florencia 4 noches")
        with cc2: gc=st.selectbox("Categoría",["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        with cm: gm=st.number_input("€",min_value=0.0,step=1.0)
        if st.form_submit_button("➕ Agregar",use_container_width=True):
            if gd.strip() and gm>0:
                if add_g(gd.strip(),gc,gm): st.success("Agregado ✓"); st.rerun()
            else: st.warning("Completá descripción y monto")
    if not df_gas.empty and "descripcion" in df_gas.columns:
        st.write(""); st.markdown("**Historial**")
        df_s=df_gas[["id","descripcion","categoria","monto","fecha"]].copy()
        df_s["monto"]=pd.to_numeric(df_s["monto"],errors="coerce").map("€{:,.0f}".format)
        st.dataframe(df_s.drop("id",axis=1),use_container_width=True,hide_index=True)
        di=st.text_input("ID a eliminar",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar") and di:
            if del_g(di.strip()): st.success("Eliminado ✓"); st.rerun()
    else: st.info("Aún no hay gastos. ¡Agregá el primero!")

# ══ PRESUPUESTO ═══════════════════════════════════════════════════════════════
with tab_pres:
    M('<div class="sh"><div class="sh-t">Presupuesto estimado</div>'
      '<div class="sh-m">Para 2 personas · 20 días · Sin vuelos</div></div>')
    c1,c2,c3,c4=st.columns(4)
    c1.metric("🏨 Alojamiento","~€1.805","20 noches · €90 prom.")
    c2.metric("🚄 Transportes","~€500","Trenes + ferries")
    c3.metric("🎟️ Entradas","~€350","Para 2 personas")
    c4.metric("🍽️ Comidas","~€1.200","€60/día")
    st.write("")
    c5,c6=st.columns(2)
    c5.metric("🛍️ Extras","~€400","Compras, pádel, etc.")
    c6.metric("💶 TOTAL","~€4.350","Para 2 · sin vuelos")
    st.write("")
    PRES_FILAS=[("Milán","3","€80","€240"),("La Spezia","2","€75","€150"),("Florencia","4","€100","€400"),
                ("Roma","4","€88","€350"),("Nápoles","1","€80","€80"),("Costa Amalfi","2","€92","€185"),
                ("Venecia","1","€100","€100"),("Zurich","3","€100","€300"),("TOTAL","20","~€95","~€1.805")]
    rows="".join(f'<tr{"class=tot" if c=="TOTAL" else ""}><td>{c}</td><td style="text-align:center">{n}</td><td style="text-align:center">{p}</td><td style="text-align:center;font-weight:700">{t}</td></tr>'
                 for c,n,p,t in PRES_FILAS)
    M(f'<div style="border:1px solid #EDE7DC;border-radius:10px;overflow:hidden">'
      f'<table class="bt"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th>'
      f'<th style="text-align:center">€/noche</th><th style="text-align:center">Total</th></tr></thead>'
      f'<tbody>{rows}</tbody></table></div>')

# ══ TIPS ══════════════════════════════════════════════════════════════════════
with tab_tips:
    M('<div class="sh"><div class="sh-t">Tips esenciales</div>'
      '<div class="sh-m">Lo que marca la diferencia entre turista y viajero</div></div>')
    cols=st.columns(3)
    for i,(icon,title,text) in enumerate(TIPS):
        with cols[i%3]:
            M(f'<div class="tipcard"><div style="font-size:1.3rem;margin-bottom:4px">{icon}</div>'
              f'<div style="font-size:0.84rem;font-weight:700;color:#3D4A5C;margin-bottom:3px">{title}</div>'
              f'<div style="font-size:0.75rem;color:#6B7A8D;line-height:1.55">{text}</div></div>')
            st.write("")

# ══ NOTAS ═════════════════════════════════════════════════════════════════════
with tab_notas_t:
    M('<div class="sh"><div class="sh-t">Notas compartidas</div>'
      '<div class="sh-m">Cualquiera puede publicar — el otro lo ve al instante</div></div>')
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
            M(f'<div class="ncard"><strong>{rn.get("tag","📝")}</strong> · '
              f'<em style="color:#6B7A8D">{rn.get("autor","")}</em><br>'
              f'{rn.get("texto","")}'
              f'<div class="nmeta">🕐 {rn.get("fecha","")}</div></div>')
            if st.button("🗑️ Borrar",key=f"dn_{rn.get('id','')}"):
                if del_nota(str(rn.get("id",""))): st.rerun()
    else: st.info("Aún no hay notas. ¡Publicá la primera!")
