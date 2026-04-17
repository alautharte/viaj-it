import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Italia & Zurich 2026 🇮🇹", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--cr:#F7F3EE;--pa:#EDE7DC;--te:#C4693A;--tl:#E8956D;--td:#8B3E1E;--ol:#6B7A3E;--sl:#6B7A8D;--go:#C9A84C;--ink:#1A1A2E;--wh:#FFFFFF;}
.stApp{background-color:var(--cr)!important;}
.stApp,.stApp p,.stApp div,.stApp span,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp li{font-family:'DM Sans',sans-serif!important;color:var(--ink)!important;}
#MainMenu,footer,header,[data-testid="stDecoration"],[data-testid="collapsedControl"]{visibility:hidden!important;display:none!important;}
.stTabs [data-baseweb="tab-list"]{gap:5px;background:var(--pa);padding:8px 10px;border-radius:12px;margin-bottom:1.5rem;}
.stTabs [data-baseweb="tab"]{padding:7px 16px;border-radius:8px;background:rgba(255,255,255,0.5);border:none!important;}
.stTabs [data-baseweb="tab"] p{color:#3D4A5C!important;font-weight:600!important;font-size:0.85rem!important;}
.stTabs [aria-selected="true"]{background:var(--wh)!important;box-shadow:0 2px 6px rgba(0,0,0,0.08)!important;}
.stTabs [aria-selected="true"] p{color:var(--td)!important;}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none!important;}
div[data-testid="stRadio"]>div{flex-direction:row!important;flex-wrap:wrap!important;gap:7px!important;background:var(--wh)!important;padding:10px!important;border-radius:12px!important;border:1px solid var(--pa)!important;}
div[data-testid="stRadio"]>div>label{background-color:var(--pa)!important;padding:7px 14px!important;border-radius:20px!important;cursor:pointer!important;border:1.5px solid transparent!important;}
div[data-testid="stRadio"]>div>label p{color:var(--ink)!important;font-weight:600!important;font-size:0.82rem!important;margin:0!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"]{background-color:var(--te)!important;border-color:var(--td)!important;}
div[data-testid="stRadio"]>div>label[data-checked="true"] p{color:var(--wh)!important;}
div[data-testid="stRadio"] div[role="radiogroup"] label>div:first-child{display:none!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background-color:var(--wh)!important;color:var(--ink)!important;border:1px solid var(--pa)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stNumberInput label{color:#3D4A5C!important;font-size:0.82rem!important;font-weight:500!important;}
.stSelectbox>div>div,[data-baseweb="select"],[data-baseweb="select"] *{background:var(--wh)!important;color:var(--ink)!important;}
.stButton>button{background:var(--te)!important;color:var(--wh)!important;border:none!important;border-radius:8px!important;font-weight:600!important;font-family:'DM Sans',sans-serif!important;padding:8px 20px!important;}
.stButton>button:hover{background:var(--td)!important;}
[data-testid="stMetric"]{background:var(--wh);border:1px solid var(--pa);border-radius:10px;padding:1rem!important;}
[data-testid="stMetricLabel"] p{color:var(--sl)!important;font-size:0.78rem!important;}
[data-testid="stMetricValue"]{color:var(--td)!important;font-family:'Playfair Display',serif!important;}
[data-testid="stMetricDelta"]{color:var(--ol)!important;}
[data-testid="stExpander"]{border:1px solid var(--pa)!important;border-radius:10px!important;background:var(--wh)!important;margin-bottom:6px!important;}
[data-testid="stExpander"] summary p{color:var(--ink)!important;font-weight:600!important;}

/* HERO */
.hero{background:linear-gradient(135deg,#3D4A5C 0%,#1A1A2E 100%);border-radius:16px 16px 0 0;padding:2.5rem 2rem 2rem;text-align:center;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 30% 50%,rgba(196,105,58,0.2) 0%,transparent 60%),radial-gradient(ellipse at 70% 30%,rgba(201,168,76,0.12) 0%,transparent 50%);}
.hi{position:relative;z-index:1;}
.hflag{font-size:1.8rem;letter-spacing:8px;margin-bottom:6px;}
.htitle{font-family:'Playfair Display',serif!important;font-size:clamp(1.8rem,4vw,3rem)!important;color:#F7F3EE!important;line-height:1.1;margin-bottom:6px;}
.htitle em{color:#E8C96A!important;font-style:italic;}
.hsub{font-size:0.9rem!important;color:rgba(247,243,238,0.6)!important;margin-bottom:1.2rem;}
.hdates{display:inline-flex;gap:1rem;background:rgba(247,243,238,0.1);border:0.5px solid rgba(247,243,238,0.2);border-radius:50px;padding:0.4rem 1.2rem;font-size:0.82rem!important;color:#E8C96A!important;}
.sbar{display:flex;background:var(--te);border-radius:0 0 16px 16px;margin-bottom:1.5rem;flex-wrap:wrap;}
.si{flex:1;min-width:90px;padding:0.85rem 1rem;text-align:center;border-right:0.5px solid rgba(247,243,238,0.2);}
.si:last-child{border-right:none;}
.sn{font-family:'Playfair Display',serif!important;font-size:1.5rem!important;color:#F7F3EE!important;display:block;line-height:1;font-weight:600;}
.sl2{font-size:0.67rem!important;color:rgba(247,243,238,0.7)!important;text-transform:uppercase;letter-spacing:0.1em;margin-top:3px;display:block;}

/* SECTION */
.sh{border-bottom:2px solid var(--pa);padding-bottom:0.75rem;margin-bottom:1.25rem;}
.st2{font-family:'Playfair Display',serif!important;font-size:1.8rem!important;color:var(--td)!important;}
.sm{font-size:0.85rem!important;color:var(--sl)!important;margin-top:2px;font-weight:500;}

/* CARD / TIMELINE */
.card{background:var(--wh);border-radius:12px;border:1px solid var(--pa);margin-bottom:1rem;box-shadow:0 2px 8px rgba(26,26,46,0.05);overflow:hidden;}
.ch{display:flex;align-items:center;gap:10px;padding:0.75rem 1.2rem;background:var(--pa);border-bottom:1px solid rgba(196,105,58,0.15);}
.db{background:var(--te);color:var(--wh)!important;font-size:0.72rem;font-weight:700;padding:3px 12px;border-radius:20px;white-space:nowrap;}
.cd{font-size:0.9rem!important;font-weight:600;color:#3D4A5C!important;}
.cc{font-size:0.78rem!important;color:var(--sl)!important;margin-left:auto;}
.tl{padding:0;}
.tr{display:grid;grid-template-columns:52px 14px 1fr;gap:0 12px;padding:12px 18px;border-bottom:1px solid var(--pa);}
.tr:last-child{border-bottom:none;}
.tr.alt{background:rgba(237,231,220,0.3);}
.tt{font-size:0.78rem!important;color:var(--sl)!important;text-align:right;padding-top:3px;font-weight:600;font-variant-numeric:tabular-nums;}
.dot{width:10px;height:10px;border-radius:50%;background:var(--pa);border:2px solid var(--tl);margin-top:4px;flex-shrink:0;}
.dot.hi2{background:var(--te);border-color:var(--td);}
.tc2{}
.tit{font-size:0.9rem!important;font-weight:700;color:var(--ink)!important;margin-bottom:3px;}
.tit.star::before{content:'★ ';color:#C9A84C;}
.tdesc{font-size:0.8rem!important;color:var(--sl)!important;line-height:1.55;}
.tip2{font-size:0.75rem!important;color:var(--td)!important;background:rgba(196,105,58,0.07);border-left:3px solid var(--tl);padding:5px 10px;margin-top:6px;border-radius:0 4px 4px 0;line-height:1.4;}
.acts{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;align-items:center;}

/* TAGS */
.tag{display:inline-flex;align-items:center;font-size:0.7rem;padding:2px 9px;border-radius:20px;font-weight:600;}
.tr2{background:#E8F0FB;color:#2A5FAC!important;}
.tw{background:#EBF5E1;color:#3A6B18!important;}
.tf{background:#FDE8DE;color:#8B3E1E!important;}
.tm{background:#F5E8F5;color:#7A3A8C!important;}
.ts{background:#FFF0E0;color:#8B5010!important;}
.tb{background:#E0F4EF;color:#0F6E56!important;}
.tsl{background:#EEF0FD;color:#4A50B0!important;}
.tbu{background:#FEF3E2;color:#8B5E10!important;}
.tp{background:#E8F5E8;color:#2A6B2A!important;}
.tkt{background:#FCEBEB;color:#A32D2D!important;}

/* LINKS / BUTTONS */
a.bn{display:inline-flex;align-items:center;gap:4px;font-size:0.72rem;padding:4px 10px;border-radius:6px;border:1.5px solid;text-decoration:none!important;font-weight:600;margin-right:3px;background:var(--wh);}
a.bm{border-color:#4285F4;color:#4285F4!important;}
a.bk{border-color:#003580;color:#003580!important;}
a.bab{border-color:#FF5A5F;color:#FF5A5F!important;}
a.bt{border-color:var(--ol);color:var(--ol)!important;}
a.btr{border-color:#B8000A;color:#B8000A!important;}

/* HOTEL CARD */
.hc{border:1px solid var(--pa);border-radius:12px;padding:1.1rem 1.25rem;margin:0.5rem 0 1.25rem;background:var(--wh);box-shadow:0 2px 6px rgba(0,0,0,0.04);}
.hn{font-family:'Playfair Display',serif!important;font-size:1rem!important;color:#3D4A5C!important;margin-bottom:4px;font-weight:600;}
.hm{font-size:0.8rem!important;color:var(--sl)!important;line-height:1.6;margin-bottom:6px;}
.hp{display:inline-block;font-size:0.82rem!important;font-weight:700;background:rgba(107,122,62,0.1);color:var(--ol)!important;padding:3px 12px;border-radius:20px;margin-bottom:8px;}
.ha{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}

/* TRANSPORT CARD */
.tc3{background:var(--wh);border:1px solid var(--pa);border-radius:10px;padding:10px 14px;margin-bottom:6px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;box-shadow:0 1px 3px rgba(0,0,0,0.03);}
.tr3{font-size:0.9rem!important;font-weight:700;color:#3D4A5C!important;}
.td3{font-size:0.78rem!important;color:var(--sl)!important;margin-top:1px;}
.tp3{font-size:0.88rem!important;font-weight:700;color:var(--te)!important;margin-left:auto;}

/* ALERTS */
.al{background:rgba(196,105,58,0.08);border:1px solid rgba(196,105,58,0.3);border-radius:9px;padding:0.85rem 1rem;font-size:0.82rem!important;color:var(--td)!important;margin-bottom:1rem;line-height:1.6;}
.al strong{color:var(--td)!important;}
.alg{background:rgba(107,122,62,0.08);border-color:rgba(107,122,62,0.3);color:var(--ol)!important;}
.alg strong{color:var(--ol)!important;}
.alb{background:#EBF4FF;border-color:#90C4F9;color:#1A4A8A!important;}
.alb strong{color:#1A4A8A!important;}

/* RESERVA CARD */
.rc{background:var(--wh);border:1px solid var(--pa);border-radius:12px;padding:1rem 1.25rem;margin-bottom:0.5rem;box-shadow:0 2px 6px rgba(0,0,0,0.04);}
.ru{border-left:4px solid var(--te);}
.ro{border-left:4px solid var(--ol);}
.rtitle{font-size:0.95rem!important;font-weight:700;color:var(--ink)!important;}
.rmeta{font-size:0.78rem!important;color:var(--sl)!important;margin:3px 0 6px;}
.bp{background:#FEF3CD;color:#8B6914!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.bc{background:#D4EDDA;color:#1A6B32!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.bpa{background:#CCE5FF;color:#0056B3!important;padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;}
.usaved{font-size:0.75rem!important;color:#0056B3!important;word-break:break-all;display:block;margin-top:4px;}
.catbadge{display:inline-block;font-size:0.7rem;padding:2px 8px;border-radius:12px;font-weight:600;margin-right:6px;}
.cat-museo{background:#F5E8F5;color:#7A3A8C!important;}
.cat-aloj{background:#EBF5E1;color:#3A6B18!important;}

/* MISC */
.nota-c{background:var(--cr);border-radius:9px;padding:10px 14px;margin-bottom:8px;border-left:3px solid var(--go);font-size:0.85rem!important;color:var(--ink)!important;}
.nota-m{font-size:0.72rem!important;color:var(--sl)!important;margin-top:5px;}
.tip-c{background:var(--wh);border:1px solid var(--pa);border-radius:10px;padding:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.03);margin-bottom:0.75rem;}
.tip-i{font-size:1.4rem;margin-bottom:5px;}
.tip-t{font-size:0.88rem!important;font-weight:700;color:#3D4A5C!important;margin-bottom:4px;}
.tip-tx{font-size:0.78rem!important;color:var(--sl)!important;line-height:1.6;}
.prog-o{background:var(--pa);border-radius:5px;height:8px;overflow:hidden;margin:6px 0;}
.prog-i{height:100%;border-radius:5px;background:var(--te);}
.bt2{width:100%;border-collapse:collapse;font-size:0.84rem;}
.bt2 th{text-align:left;padding:10px 12px;background:var(--pa);color:#3D4A5C!important;font-weight:700;font-size:0.72rem;text-transform:uppercase;}
.bt2 td{padding:10px 12px;border-bottom:1px solid var(--pa);color:var(--ink)!important;font-weight:500;}
.bt2 tr.tot td{font-weight:700;color:var(--td)!important;border-top:2px solid var(--tl);border-bottom:none;}
.sok{background:#D4EDDA;color:#1A6B32!important;padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:600;display:inline-block;margin-bottom:1rem;}
.serr{background:#F8D7DA;color:#721C24!important;padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:600;display:inline-block;margin-bottom:1rem;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ─── SHEETS ────────────────────────────────────────────────────────────────────
SCOPES=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def get_wb():
    c=Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]),scopes=SCOPES)
    return gspread.authorize(c).open_by_key(st.secrets["spreadsheet_id"])

def ensure_sheets():
    wb=get_wb(); ex=[s.title for s in wb.worksheets()]
    needed={"viaje_reservas":["id","estado","tipo","url_reserva","confirmacion","monto","notas_int","updated"],
            "viaje_gastos":["id","descripcion","categoria","monto","fecha"],
            "viaje_notas":["id","texto","tag","autor","fecha"]}
    out={}
    for n,h in needed.items():
        if n not in ex:
            ws=wb.add_worksheet(title=n,rows=500,cols=len(h)); ws.append_row(h)
        out[n]=wb.worksheet(n)
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
        s=ensure_sheets(); ws=s["viaje_reservas"]; recs=ws.get_all_records()
        now=datetime.now().strftime("%Y-%m-%d %H:%M"); row=[rid,estado,tipo,url,conf,monto,notas,now]
        for i,r in enumerate(recs,start=2):
            if r.get("id")==rid:
                ws.update(f"A{i}:H{i}",[row]); st.cache_data.clear(); return True
        ws.append_row(row); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def add_g(desc,cat,monto):
    try:
        s=ensure_sheets(); gid=f"g{datetime.now().strftime('%m%d%H%M%S')}"
        s["viaje_gastos"].append_row([gid,desc,cat,monto,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_g(gid):
    try:
        s=ensure_sheets(); ws=s["viaje_gastos"]
        for i,r in enumerate(ws.get_all_records(),start=2):
            if str(r.get("id"))==str(gid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass; return False

def add_nota(texto,tag,autor):
    try:
        s=ensure_sheets(); nid=f"n{datetime.now().strftime('%m%d%H%M%S')}"
        s["viaje_notas"].append_row([nid,texto,tag,autor,datetime.now().strftime("%d/%m %H:%M")])
        st.cache_data.clear(); return True
    except Exception as e: st.error(f"Error: {e}"); return False

def del_nota(nid):
    try:
        s=ensure_sheets(); ws=s["viaje_notas"]
        for i,r in enumerate(ws.get_all_records(),start=2):
            if str(r.get("id"))==str(nid):
                ws.delete_rows(i); st.cache_data.clear(); return True
    except: pass; return False

# ─── HTML HELPERS ─────────────────────────────────────────────────────────────
def tag(txt, cls): return f'<span class="tag {cls}">{txt}</span>'
def btn(txt, url, cls): return f'<a href="{url}" target="_blank" class="bn {cls}">{txt}</a>'

def row(hora, titulo, desc, hi=False, tip=None, tags="", btns="", alt=False):
    dot = "dot hi2" if hi else "dot"
    tit = "tit star" if hi else "tit"
    al = " alt" if alt else ""
    tip_h = f'<div class="tip2">{tip}</div>' if tip else ""
    return f"""<div class="tr{al}">
  <div class="tt">{hora}</div><div class="{dot}"></div>
  <div class="tc2">
    <div class="{tit}">{titulo}</div>
    <div class="tdesc">{desc}</div>
    {tip_h}
    <div class="acts">{tags}{btns}</div>
  </div>
</div>"""

def card(day_n, day_date, city, rows_html):
    return f"""<div class="card">
  <div class="ch"><span class="db">{day_n}</span><span class="cd">{day_date}</span><span class="cc">{city}</span></div>
  <div class="tl">{rows_html}</div>
</div>"""

def hotel(nombre, meta, precio, url_b, url_a, url_m):
    bb = btn("📅 Booking", url_b, "bk") if url_b else ""
    ba = btn("🏠 Airbnb", url_a, "bab") if url_a else ""
    bm = btn("📍 Maps", url_m, "bm") if url_m else ""
    return f"""<div class="hc">
  <div class="hn">{nombre}</div>
  <div class="hm">{meta}</div>
  <div class="hp">{precio}</div>
  <div class="ha">{bb}{ba}{bm}</div>
</div>"""

def transporte(icon, route, detail, price, url):
    return f"""<div class="tc3">
  <div style="font-size:1.3rem;width:28px;text-align:center">{icon}</div>
  <div style="flex:1"><div class="tr3">{route}</div><div class="td3">{detail}</div></div>
  <div class="tp3">{price}</div>
  {btn("🔗 Comprar", url, "btr")}
</div>"""

def alerta(html, tipo=""):
    return f'<div class="al {tipo}">{html}</div>'

# ─── CONTENIDO ITINERARIO ─────────────────────────────────────────────────────

def html_milan():
    h = hotel("Hotel Ariston ★★★ (o similar zona Centrale/Navigli)",
              "Central para metro · Desayuno incluido · Habitación doble<br>Alternativa premium: Hotel Dei Cavalieri (junto al Duomo, ~€110/noche)",
              "~€70–90 / noche · 3 noches",
              "https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2",
              "https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2",
              "https://maps.google.com/?q=Hotel+Ariston+Milan")

    d1 = card("Día 1","Lunes 25 mayo — Llegada y primer paseo","Milán",
        row("10:15","Llegada MXP — Inmigración y aduana",
            "Pasaporte argentino. Calcular 30–45 min en inmigración en temporada alta.", hi=True) +
        row("11:30","Malpensa Express → Milano Centrale",
            "Sale cada 30 min. 52 minutos. Comprar en máquinas Trenord o app. Validar antes de subir.",
            tags=tag("🚄 €13/persona","tr2"), btns=btn("Trenord","https://www.trenord.it/en/tickets/relations/malpensa-express/","btr")+btn("📍 Maps","https://maps.google.com/?q=Milano+Centrale+Station","bm")) +
        row("13:30","Check-in + almuerzo tranquilo",
            "Pedir risotto alla milanese o cotoletta en trattoria local. Evitar restaurantes junto a estaciones.",
            tags=tag("🍝 Risotto","tf")) +
        row("15:00","Siesta obligatoria",
            "Vienen de 11h de vuelo nocturno. 2–3 horas de siesta es clave para los días siguientes.") +
        row("18:00","Paseo Navigli + Aperitivo",
            "Los canales al atardecer. Aperol Spritz al borde del canal. Mejor zona: Alzaia Naviglio Grande.",
            tags=tag("🚶 Paseo","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Navigli+Milan","bm")))

    d2 = card("Día 2","Martes 26 mayo — Última Cena, Duomo, Shopping y Pádel","Milán",
        row("08:00","Desayuno italiano",
            "Bar local: cappuccino + cornetto. No pedir cappuccino después del mediodía.",
            tags=tag("☕ €3","tf")) +
        row("08:15","LA ÚLTIMA CENA — Santa Maria delle Grazie",
            "El fresco más famoso del mundo. RESERVA OBLIGATORIA. Solo 25 personas cada 15 minutos. Duración: 15 min exactos.",
            hi=True, tip="⚠️ CRÍTICO: Reservar hoy mismo. Los cupos de mayo se agotan meses antes.",
            tags=tag("🎨 €15 + €2 reserva","tm"),
            btns=btn("🎟️ Reservar ahora","https://cenacolodavincimilano.vivaticket.com","bt")+btn("📍 Maps","https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan","bm")) +
        row("10:00","Duomo di Milano — terrazas",
            "Terrazas en ascensor para ver los 135 chapiteles de cerca. Vista 360° de Milán.",
            hi=True, tags=tag("⛪ €15 terraza","tm"),
            btns=btn("🎟️ Reservar","https://ticket.duomomilano.it","bt")+btn("📍 Maps","https://maps.google.com/?q=Duomo+di+Milano","bm")) +
        row("11:30","Galleria Vittorio Emanuele II + Scala",
            "Pisar el toro y girar el talón — trae suerte. Teatro alla Scala (exterior y museo).",
            tags=tag("🚶 Gratis","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Galleria+Vittorio+Emanuele+II+Milan","bm")) +
        row("13:00","Almuerzo en Brera",
            "Buscar menú del giorno visible en la puerta: primer plato + segundo + agua = €12–15.",
            tags=tag("🍽️ €15","tf"), btns=btn("📍 Brera","https://maps.google.com/?q=Brera+Milan","bm")) +
        row("15:00","Shopping — Corso Buenos Aires",
            "La calle comercial más larga de Italia. Zara, H&M, Bershka, Mango, marcas italianas accesibles. 2km de tiendas. Para ropa de calidad a buen precio, es el mejor lugar de Milán.",
            hi=True, tags=tag("🛍️ Ropa","ts"), btns=btn("📍 Maps","https://maps.google.com/?q=Corso+Buenos+Aires+Milan","bm")) +
        row("17:30","Padel Nuestro Milano (opcional — vale si tienen tiempo)",
            "La mayor tienda de pádel del norte de Italia. Bullpadel, Siux, Adidas, Nox. Pista interior para probar palas. Está en las afueras — evaluar si el tiempo lo permite o dejarlo para Roma.",
            hi=True, tip="Más conveniente visitar Padel Nuestro Roma (centro) que ésta (40 min del centro). Abre hasta las 19:30.",
            tags=tag("🎾 Pádel","tp"), btns=btn("📍 Maps","https://maps.google.com/?q=Via+Papa+Giovanni+XXIII+9a+Rodano+Millepini+Milan","bm")) +
        row("20:00","Cena en Navigli",
            "Evitar restaurantes con foto en el menú en la puerta — señal de trampa turística.",
            tags=tag("🍷 Cena","tf")))

    d3 = card("Día 3","Miércoles 27 mayo — Brera e Isola","Milán",
        row("09:00","Pinacoteca di Brera",
            "Mantegna, Raphael, Caravaggio. Una de las mejores colecciones renacentistas de Italia. Calcular 2h.",
            hi=True, tags=tag("🎨 €15","tm"),
            btns=btn("Reservar","https://pinacotecabrera.org","bt")+btn("📍 Maps","https://maps.google.com/?q=Pinacoteca+di+Brera+Milan","bm")) +
        row("11:30","Barrio Isola + Bosco Verticale",
            "El famoso bosque vertical de Stefano Boeri. El barrio Isola tiene cafés y mercaditos locales muy cool.",
            tags=tag("🌿 Gratis","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Bosco+Verticale+Milan","bm")) +
        row("13:00","Almuerzo + tarde libre",
            "Zona Sant'Ambrogio (Basílica del siglo IV, gratis). Tarde para compras adicionales o descanso.") +
        row("19:00","Preparar maletas — mañana viajan a Cinque Terre",
            "Tren 08:10 desde Milano Centrale. Poner alarma.", tags=tag("🧳 Preparación","tsl")))

    return h + d1 + d2 + d3

def html_cinque():
    h = hotel("Hotel Firenze ★★★ (La Spezia)",
              "5 min a pie de la estación · Habitación doble · 2 noches<br>Alternativa: alojarse directamente en Monterosso al Mare",
              "~€70–80 / noche · 2 noches",
              "https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2",
              "https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2",
              "https://maps.google.com/?q=La+Spezia+train+station")
    tr = transporte("🚄","Milano → La Spezia Centrale","Intercity · ~3h · Salida 08:10 desde Milano Centrale","€25–35","https://www.trenitalia.com")

    d4 = card("Día 4","Jueves 28 mayo — Riomaggiore, Manarola, Corniglia","Cinque Terre",
        row("11:30","Llegada La Spezia — Check-in + Cinque Terre Card",
            "Comprar la Card 2 días en InfoParco o taquilla de la estación (~€29.50/persona). Incluye todos los trenes locales entre los pueblos.",
            tags=tag("🎫 €29.50 · 2 días","tkt"), btns=btn("Info Card","https://www.cinqueterre.eu.com/en/cinque-terre-card","bt")) +
        row("12:30","Riomaggiore — el más fotogénico",
            "Bajar al puerto pequeño. Almuerzo: focaccia con pesto ligurio + vino sciacchetrà. El pesto se hace con albahaca local, piñones, parmesano y aceite ligur.",
            hi=True, tags=tag("🍃 Pesto original","tf"), btns=btn("📍 Maps","https://maps.google.com/?q=Riomaggiore+Cinque+Terre","bm")) +
        row("15:30","Manarola — el mirador icónico",
            "La foto de las casas pastel sobre las rocas. Bajar al muelle de natación. 1.5h.",
            hi=True, tags=tag("📸 Foto icónica","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Manarola+Cinque+Terre","bm")) +
        row("17:30","Corniglia — vista 360°",
            "El único pueblo en lo alto. 377 escalones o minibus desde la estación. Vista impresionante.",
            btns=btn("📍 Maps","https://maps.google.com/?q=Corniglia+Cinque+Terre","bm")))

    d5 = card("Día 5","Viernes 29 mayo — Vernazza, senderismo y Monterosso","Cinque Terre",
        row("08:00","Vernazza — el más medieval",
            "Castillo Doria (€1.50) para la mejor vista. Puerto pintoresco. 2h.",
            hi=True, btns=btn("📍 Maps","https://maps.google.com/?q=Vernazza+Cinque+Terre","bm")) +
        row("11:00","Senderismo Vernazza → Monterosso (3.5 km · 2h)",
            "El sendero más espectacular. Verificar estado en parconazionale5terre.it antes de ir. Llevar agua y zapatos cerrados.",
            hi=True, tip="Si el sendero está cerrado, tomar el tren y usar el tiempo de playa en Monterosso.",
            tags=tag("🥾 Trekking","tw"), btns=btn("Estado senderos","https://www.parconazionale5terre.it","bt")) +
        row("14:00","Monterosso — playa y anchoas",
            "El único pueblo con playa de arena real. Probar acciughe (anchoas de Monterosso). Reposeras ~€5. Agua ~22°C en junio.",
            tags=tag("🏖️ Playa","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Monterosso+al+Mare","bm")))

    return h + tr + d4 + d5

def html_florencia():
    h = hotel("Hotel Davanzati ★★★ (recomendado)",
              "A 2 min del Duomo y Uffizi · Servicio excelente · Desayuno muy bueno<br>Alternativa económica: B&B Machiavelli (zona Oltrarno, ~€75/noche)",
              "~€95–110 / noche · 4 noches",
              "https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2",
              "https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2",
              "https://maps.google.com/?q=Hotel+Davanzati+Florence")
    tr = transporte("🚄","La Spezia → Firenze Santa Maria Novella","Intercity · ~2h · Salida 08:30 · Directo o cambio en Pisa","€15–20","https://www.trenitalia.com")

    d6 = card("Día 6","Sábado 30 mayo — Duomo + Cúpula + Piazzale","Florencia",
        row("11:00","Duomo + Cúpula de Brunelleschi",
            "463 escalones. Reservar turno online — sin reserva la fila puede ser 2–3 horas. Incluye Baptisterio y Museo del Duomo.",
            hi=True, tags=tag("⛪ Pase ~€20","tm"),
            btns=btn("🎟️ Reservar","https://www.ilgrandemuseodelduomo.it","bt")+btn("📍 Maps","https://maps.google.com/?q=Duomo+Florence","bm")) +
        row("13:00","Mercato Centrale — almuerzo",
            "Piso superior con puestos de comida. Probar lampredotto (callos florentinos — para valientes) o pasta fresca.",
            btns=btn("📍 Maps","https://maps.google.com/?q=Mercato+Centrale+Florence","bm")) +
        row("16:30","Ponte Vecchio → Oltrarno",
            "El puente más antiguo de Florencia con joyerías desde el siglo XVI. Al cruzar: el Florencia auténtico.",
            tags=tag("🌉 Paseo","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Ponte+Vecchio+Florence","bm")) +
        row("18:30","Piazzale Michelangelo — atardecer",
            "EL punto de vista de Florencia al atardecer. Vista panorámica de toda la ciudad. Llegar 30 min antes del sunset para conseguir lugar.",
            hi=True, tags=tag("🌅 Gratis","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Piazzale+Michelangelo+Florence","bm")))

    d7 = card("Día 7","Domingo 31 mayo — Uffizi + David + San Miniato","Florencia",
        row("08:30","Galería degli Uffizi — Botticelli, Leonardo, Caravaggio",
            "El museo de arte renacentista más importante del mundo. 3h mínimo. RESERVA OBLIGATORIA. La sala de Botticelli es la más concurrida — visitarla primero.",
            hi=True, tags=tag("🎨 €20 + €4 reserva","tm"),
            btns=btn("🎟️ Reservar","https://www.uffizi.it","bt")+btn("📍 Maps","https://maps.google.com/?q=Uffizi+Gallery+Florence","bm")) +
        row("14:00","David de Michelangelo — Accademia",
            "5.17 metros de mármol perfecto, tallado entre 1501 y 1504. El original — el de la Piazza es una copia. 1.5h. Hay también los 'Prisioneros' de Michelangelo.",
            hi=True, tags=tag("🗿 €12 + reserva","tm"),
            btns=btn("🎟️ Reservar","https://www.uffizi.it/en/the-accademia-gallery","bt")+btn("📍 Maps","https://maps.google.com/?q=Accademia+Gallery+Florence","bm")) +
        row("17:30","San Miniato al Monte",
            "La iglesia más bella de Florencia — sobre una colina, entrada gratis. Los monjes rezan el Oficio en gregoriano a las 17:30.",
            tags=tag("⛪ Gratis","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=San+Miniato+al+Monte+Florence","bm")))

    d8 = card("Día 8","Lunes 1 junio — Palazzo Pitti + Boboli + Cappelle Medicee","Florencia",
        row("09:00","Palazzo Pitti + Jardines de Boboli",
            "El palacio de los Medici. Rafael y Tiziano en la Galleria Palatina. Los Jardines incluyen una gruta artificial de Buontalenti de 1583.",
            tags=tag("🏰 €16","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Palazzo+Pitti+Florence","bm")) +
        row("16:00","Cappelle Medicee — Michelangelo",
            "Las tumbas de los Medici con las esculturas de Michelangelo: Aurora, Crepúsculo, Día y Noche. Menos conocidas que el David, igual de impactantes.",
            hi=True, tags=tag("🗿 €9","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Cappelle+Medicee+Florence","bm")))

    d9 = card("Día 9","Martes 2 junio — Siena y Val d'Orcia","Toscana",
        row("07:30","Bus SENA desde Florencia a Siena",
            "Desde Autostazione di Firenze (frente a Santa Maria Novella). 1.5h · €9.",
            tags=tag("🚌 €9","tbu"), btns=btn("📍 Bus","https://maps.google.com/?q=Autostazione+Firenze","bm")) +
        row("09:00","Piazza del Campo + Torre del Mangia",
            "La plaza más bella de Italia en forma de concha, escenario del Palio. La Torre tiene 400 escalones y vista impresionante de los tejados rojizos.",
            hi=True, tags=tag("🏰 Torre €10","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Piazza+del+Campo+Siena","bm")) +
        row("10:00","Duomo di Siena",
            "El Duomo de Siena compite con Florencia en belleza. El pavimento de mármol con 56 escenas es único en el mundo.",
            tags=tag("⛪ €8","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Siena+Cathedral","bm")) +
        row("13:30","Almuerzo en la ciudad vieja",
            "Probar: pici all'aglione (pasta gruesa con ajo), cinghiale (jabalí). Siena tiene cocina muy diferente a Florencia.",
            tags=tag("🍖 Toscana","tf")) +
        row("17:00","Bus de regreso a Florencia",
            "Hay buses frecuentes hasta las 21:00. Cena en Florencia. Mañana viajan a Roma."))

    return h + tr + d6 + d7 + d8 + d9

def html_roma():
    h = hotel("Hotel Arco del Lauro ★★★ (Trastevere)",
              "Zona Trastevere — auténtica y central · B&B familiar · Muy buenas reseñas<br>Alternativa: Hotel Santa Prassede (~€80) o zona Prati (junto al Vaticano)",
              "~€80–95 / noche · 4 noches",
              "https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2",
              "https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2",
              "https://maps.google.com/?q=Trastevere+Rome")
    tr = transporte("🚄","Firenze SMN → Roma Termini","Frecciarossa (Alta Velocidad) · 1h 30min · Sale cada 30 min · Reservar anticipado","€25–45","https://www.trenitalia.com")
    al = alerta("<strong>🎾 Padel Nuestro Roma:</strong> La tienda más completa de la ruta. Centro de Roma — mucho más conveniente que la de Milán. Bullpadel, Siux, Babolat, Head, Star Vie. Permiten probar palas. Ver Día 12.")

    d10 = card("Día 10","Miércoles 3 junio — Vaticano completo","Roma",
        row("10:30","Museos Vaticanos + Capilla Sixtina",
            "Los museos más visitados del mundo. 3–4h. El recorrido culmina en la Capilla Sixtina con el fresco de Miguel Ángel (Creación de Adán, Juicio Final). RESERVA OBLIGATORIA con semanas de anticipación.",
            hi=True, tip="⚠️ En la Capilla Sixtina está prohibido fotografiar y hacer ruido — los guardias son estrictos. Silencio absoluto.",
            tags=tag("🎨 €17 + €4 reserva","tm"),
            btns=btn("🎟️ Reservar","https://www.museivaticani.va","bt")+btn("📍 Maps","https://maps.google.com/?q=Vatican+Museums+Rome","bm")) +
        row("14:00","Basílica de San Pedro + Cúpula",
            "La basílica más grande del mundo cristiano. Subir a la cúpula (551 escalones o ascensor parcial €8) para una vista alucinante de la Plaza San Pedro y Roma.",
            tags=tag("⛪ Gratis · Cúpula €8","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=St+Peters+Basilica+Rome","bm")))

    d11 = card("Día 11","Jueves 4 junio — Roma Imperial","Roma",
        row("08:00","Coliseo + Foro Romano + Palatino",
            "Combo obligatorio. 3–4h. El Palatino (colina sobre el Foro) tiene las mejores vistas del Coliseo y es el menos visitado del combo — no saltearlo.",
            hi=True, tags=tag("🏛️ €16 + reserva","tm"),
            btns=btn("🎟️ Reservar","https://www.coopculture.it","bt")+btn("📍 Maps","https://maps.google.com/?q=Colosseum+Rome","bm")) +
        row("17:30","Trastevere — paseo y cena",
            "El barrio medieval más pintoresco de Roma. La Basílica di Santa Maria in Trastevere (siglo XII, gratis). Cena recomendada: Da Enzo al 29.",
            tags=tag("🚶 Paseo","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Trastevere+Rome","bm")))

    d12 = card("Día 12","Viernes 5 junio — Roma Barroca + Borghese + Pádel","Roma",
        row("09:00","Pantheon → Piazza Navona → Fontana di Trevi",
            "El Pantheon (125 d.C.) requiere ticket €5 desde 2023. El óculo deja entrar la lluvia y sale por el desagüe central. Trevi: lanzar la moneda de espaldas con la derecha.",
            tags=tag("🏛️ Pantheon €5","tm"), btns=btn("📍 Pantheon","https://maps.google.com/?q=Pantheon+Rome","bm")+btn("📍 Trevi","https://maps.google.com/?q=Trevi+Fountain+Rome","bm")) +
        row("15:00","Galería Borghese — Bernini",
            "El museo más exclusivo de Roma — solo 360 personas cada 2 horas. Las esculturas de Bernini: Apolo y Dafne, El rapto de Proserpina — lo más impactante de toda Roma.",
            hi=True, tags=tag("🗿 €15 + €2 reserva","tm"),
            btns=btn("🎟️ Reservar","https://www.galleriaborghese.it","bt")+btn("📍 Maps","https://maps.google.com/?q=Galleria+Borghese+Rome","bm")) +
        row("18:00","🎾 Padel Nuestro Roma",
            "La tienda más completa de pádel en Roma. Bullpadel, Siux, Adidas, Star Vie, Babolat, Head. Pista interior para probar palas antes de comprar. Mejor opción que la de Milán por ubicación central.",
            hi=True, tags=tag("🎾 Pádel Roma","tp"),
            btns=btn("📍 Maps","https://maps.google.com/?q=Padel+Nuestro+Roma+Italy","bm")+btn("Web tienda","https://www.padelnuestro.com","bt")))

    d13 = card("Día 13","Sábado 6 junio — Castel Sant'Angelo + libre","Roma",
        row("09:00","Castel Sant'Angelo",
            "Mausoleo de Adriano convertido en fortaleza papal. El 'Passetto' (corredor secreto al Vaticano) es visible desde afuera. Vista del Tiber y San Pedro desde la cima.",
            tags=tag("🏰 €14","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Castel+Sant+Angelo+Rome","bm")) +
        row("14:00","Tarde libre + preparación",
            "Compras en Via del Corso o zona Spagna. Mañana temprano: tren a Nápoles.",
            tags=tag("🛍️ Libre","tw")))

    return h + tr + al + d10 + d11 + d12 + d13

def html_napoles():
    h = hotel("Hotel Piazza Bellini ★★★ (centro histórico UNESCO)",
              "En el corazón de Spaccanapoli · 1 noche (7–8 junio)",
              "~€75–90 / noche",
              "https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2",
              "https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2",
              "https://maps.google.com/?q=Piazza+Bellini+Naples")
    tr = transporte("🚄","Roma Termini → Napoli Centrale","Frecciarossa · 1h10 · Sale cada 30 min desde las 06:00","€20–35","https://www.trenitalia.com")

    d14 = card("Día 14","Domingo 7 junio — Pompeya + Nápoles + Pizza","Nápoles",
        row("09:00","Circumvesuviana → Pompeya Scavi",
            "Andén subterráneo (-1) de Napoli Centrale. Sale cada 30 min hacia Sorrento. Bajarse en 'Pompei Scavi'. Comprar ticket en máquina automática — evitar vendedores ambulantes.",
            hi=True, tags=tag("🚂 €3 · 40min","tr2"), btns=btn("📍 Maps","https://maps.google.com/?q=Pompei+Scavi+station","bm")) +
        row("10:00","Pompeya — ciudad sepultada por el Vesubio",
            "La ciudad romana sepultada en 79 d.C. 3h mínimo. Imprescindible: Casa dei Vettii, Anfiteatro, Thermopolium (bar romano), los moldes humanos en el Granario, el Foro. Llevar agua y sombrero — hace calor y hay poca sombra.",
            hi=True, tags=tag("🌋 €16","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Pompeii+Archaeological+Park","bm")) +
        row("15:00","Spaccanapoli + Museo Arqueológico Nacional",
            "La calle Spaccanapoli cruza Nápoles histórica. El Museo tiene los mejores objetos de Pompeya y Herculano del mundo — incluyendo la 'Stanza Segreta' (arte erótico pompeiano).",
            tags=tag("🏺 €15","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=National+Archaeological+Museum+Naples","bm")) +
        row("19:30","🍕 La pizza napolitana ORIGINAL",
            "Nápoles inventó la pizza. Las tres legendarias: L'Antica Pizzeria da Michele (solo Margherita y Marinara, fila larga), Sorbillo (favorita de los napolitanos), Di Matteo (en Spaccanapoli). La margherita original: tomate San Marzano, mozzarella di bufala, albahaca, aceite. Nada más.",
            hi=True, tags=tag("🍕 €5–8","tf"),
            btns=btn("📍 Da Michele","https://maps.google.com/?q=L+Antica+Pizzeria+da+Michele+Naples","bm")+btn("📍 Sorbillo","https://maps.google.com/?q=Pizzeria+Sorbillo+Naples","bm")))

    return h + tr + d14

def html_amalfi():
    al = alerta("<strong>💰 Tip de presupuesto:</strong> Alojarse en Praiano (entre Positano y Amalfi) mantiene el presupuesto de €85–100/noche con vista al mar. Positano mismo supera los €200 fácilmente. Con ferry desde Praiano se llega a Positano en 10 min.")
    h = hotel("Albergo California (Praiano) ★★★",
              "Vista al mar · Desayuno incluido · 10 min de Positano en ferry · 2 noches (8–10 junio)",
              "~€85–100 / noche",
              "https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2",
              "https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2",
              "https://maps.google.com/?q=Praiano+Amalfi+Coast")
    tr = transporte("⛵","Nápoles → Positano (ferry)","SNAV o Alilauro · Desde Molo Beverello · Salidas 08:30 y 09:30 · Solo mayo–oct","~€20/persona","https://www.alilauro.it")

    d15 = card("Día 15","Lunes 8 junio — Positano + Amalfi","Costa Amalfi",
        row("10:30","Positano — las casas en cascada",
            "El pueblo más fotogénico de la Costa. Las casas de colores en cascada sobre el acantilado. Playa Grande con guijarros, reposeras ~€20 el par. Agua del Tirreno ~22°C.",
            hi=True, btns=btn("📍 Maps","https://maps.google.com/?q=Positano+Amalfi+Coast","bm")) +
        row("13:00","Almuerzo con vista en Positano",
            "Muy caro en Positano. Buscar La Zagara (jardín) o Il Ritrovo (más económico, en la colina). Probar: scialatielli ai frutti di mare (pasta fresca con mariscos).",
            tags=tag("🦐 Mariscos","tf")) +
        row("15:00","Bus SITA → Amalfi ciudad",
            "El bus azul SITA recorre toda la costa. €2.50 el tramo. Duración 40 min por la carretera más espectacular de Italia. El Duomo de Amalfi (siglo IX, estilo árabe-normando) domina la plaza. Sentarse del lado DERECHO mirando al mar.",
            hi=True, tip="Comprar ticket en tabacchi antes de subir. Sentarse del lado derecho mirando al mar — la vista es incomparable.",
            tags=tag("🚌 €2.50","tbu"), btns=btn("📍 Maps","https://maps.google.com/?q=Amalfi+Cathedral","bm")) +
        row("19:30","Cena con vista al mar",
            "El atardecer sobre el Tirreno desde la Costa Amalfi es uno de los espectáculos más bellos de Italia.",
            tags=tag("🌅 Scialatielli ai frutti","tf")))

    d16 = card("Día 16","Martes 9 junio — Ravello + Sentiero degli Dei","Costa Amalfi",
        row("08:00","Ravello — Villa Cimbrone + Terrazza dell'Infinito",
            "Ravello está a 350 metros sobre el nivel del mar. La Terraza del Infinito es el mirador más espectacular de toda la Costa. Jardines del siglo XI. Wagner llamó a esta vista 'el balcón más bello del mundo'.",
            hi=True, tags=tag("🌿 €7","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Villa+Cimbrone+Ravello","bm")) +
        row("11:00","Sentiero degli Dei — Camino de los Dioses (7.8km · 3h)",
            "El sendero más famoso de la Costa Amalfi. Sale desde Bomerano y baja hasta Positano. Vista de toda la costa desde 600m de altura. No necesita guía. Llevar agua, sombrero, calzado firme.",
            hi=True, tip="El trayecto baja (no sube), así que el cansancio es manejable. Es el mejor día del viaje para muchos viajeros.",
            tags=tag("🥾 Trekking","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Sentiero+degli+Dei+Amalfi+Coast","bm")) +
        row("15:00","Llegada Positano + playa merecida",
            "Después del sendero: baño en el mar, playa, almuerzo merecido. Tarde libre. Mañana: ferry + tren largo a Venecia — preparar maletas.",
            tags=tag("🏖️ Playa","tw")))

    return al + h + tr + d15 + d16

def html_venecia():
    al = alerta("<strong>Nota Venecia:</strong> Desde junio 2024, Venecia cobra €5 de 'tasa de acceso' en días pico. Verificar calendario en comune.venezia.it. Airbnb muy regulado en Venecia — hotel es la mejor opción.")
    h = hotel("Hotel Dalla Mora ★★★ (Santa Croce)",
              "Zona auténtica · 10 min a pie de la estación · No en Mestre (tierra firme) — en Venecia real<br>Alternativa: B&B en Cannaregio",
              "~€90–110 / noche",
              "https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2&nflt=di%3D1376",
              "", "https://maps.google.com/?q=Hotel+Dalla+Mora+Venice")
    tr = transporte("🚄","Nápoles → Venezia Santa Lucia","Frecciarossa directo · 4h50 · Salida 07:30–08:00","€35–60","https://www.trenitalia.com")

    d17 = card("Día 17","Miércoles 10 junio — Venecia completa","Venecia",
        row("13:00","Gran Canal en Vaporetto línea 1 (la lenta)",
            "La línea 1 recorre todo el Gran Canal parando en cada estación. 45 minutos de palacios del siglo XIV, puentes, góndolas. El paseo más cinematográfico del viaje. Ticket 24h = €25.",
            hi=True, tags=tag("🚤 24h = €25","tb")) +
        row("15:00","Plaza San Marcos + Basílica + Campanile",
            "Basílica siglo XI, estilo bizantino, cúpulas doradas — gratuita con espera. El Campanile (99m) ofrece la mejor vista de Venecia.",
            hi=True, tags=tag("🏛️ Gratis + €10 campanile","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=St+Marks+Basilica+Venice","bm")) +
        row("17:00","Perderse sin mapa — la mejor actividad de Venecia",
            "Apagar Google Maps. Venecia tiene 118 islas conectadas por 400 puentes. Es imposible no perderse — y eso es exactamente lo que hay que hacer. Los callejones más angostos llevan a los campos más secretos.",
            hi=True, tags=tag("🗺️ Sin mapa","tw")) +
        row("19:30","Spritz veneziano en bacaro + Rialto",
            "El Spritz se inventó en Venecia. Los 'bacari' son los bares tradicionales con 'cicchetti' (tapas de €1–2). Zona Cannaregio para los más auténticos.",
            tags=tag("🍹 Bacaro","tf"), btns=btn("📍 Rialto","https://maps.google.com/?q=Rialto+Bridge+Venice","bm")) +
        row("21:00","Góndola nocturna (opcional)",
            "Precio fijo oficial: €80 para 30 min (hasta 6 personas). De noche los canales sin turistas son mágicos.",
            tags=tag("🎭 €80 / góndola","tb")))

    return al + h + tr + d17

def html_zurich():
    al = alerta("⚠️ <strong>Vuelo el 14/6 a las 08:55:</strong> Estar en ZRH a las 07:00. Tren Zurich HB → aeropuerto: 10 min, sale cada 10 min. El día 13 preparar todo y dormir temprano.")
    h = hotel("Hotel Otter ★★ (Langstrasse) o IBIS City West",
              "Zona cool y multicultural · A pie del casco histórico · 3 noches (11–14 junio)<br>Alternativa con vista: Hotel Limmatblick (~€120, sobre el río Limmat)",
              "~€90–110 / noche · 3 noches",
              "https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2",
              "", "https://maps.google.com/?q=Langstrasse+Zurich")
    tr = transporte("🚄","Venezia S. Lucia → Zurich HB (a través de los Alpes)","EuroCity directo · 4h45 · Paisaje alpino impresionante · Sentarse del lado derecho mirando norte","€40–60","https://www.sbb.ch")

    d18 = card("Día 18","Jueves 11 junio — Llegada + Altstadt","Zurich",
        row("14:00","Bahnhofstrasse + Lago de Zurich",
            "La calle comercial más cara del mundo. Joyerías, Rolex, bancos. El Lago de Zurich al final para sentarse. Cambio mental: de caos italiano a precisión suiza.",
            tags=tag("⌚ Paseo","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Bahnhofstrasse+Zurich","bm")) +
        row("15:30","Altstadt + Grossmünster",
            "La iglesia donde Zwinglio inició la Reforma Protestante en 1519. Subir las torres (€5) para la vista de Zurich. El barrio medieval Niederdorf: callejuelas adoquinadas, gremios, cafés.",
            hi=True, btns=btn("📍 Maps","https://maps.google.com/?q=Grossmunster+Zurich","bm")) +
        row("18:00","Fraumünster — vitrales de Chagall (1970)",
            "5 vitrales de Marc Chagall en un edificio del siglo XIII. Tesoro de arte moderno en arquitectura medieval. €5.",
            tags=tag("🎨 €5","tm"), btns=btn("📍 Maps","https://maps.google.com/?q=Fraumunster+Zurich","bm")))

    d19 = card("Día 19","Viernes 12 junio — Lago + ETH + Fondue","Zurich",
        row("09:00","Crucero Lago de Zurich",
            "ZSG opera cruceros. Recorrido corto 1h o largo 4h hasta Rapperswil. El lago con los Alpes de fondo es icónico.",
            hi=True, tags=tag("⛵ €8–30","tb"),
            btns=btn("ZSG","https://www.zsg.ch","bt")+btn("📍 Maps","https://maps.google.com/?q=Lake+Zurich+boat+tours","bm")) +
        row("16:00","Polybahn → terraza ETH (vista gratis)",
            "El funicular universitario de 1889 sube hasta la ETH (la universidad de Einstein). Vista panorámica de Zurich, el lago y los Alpes desde la terraza — gratis.",
            btns=btn("📍 Maps","https://maps.google.com/?q=ETH+Zurich+terrace","bm")) +
        row("20:00","Fondue suiza — Swiss Chuchi",
            "La fondue de queso es el plato nacional suizo. Swiss Chuchi en el Altstadt. Experiencia completa ~€35–45/persona.",
            hi=True, tags=tag("🧀 Fondue","tf"), btns=btn("📍 Swiss Chuchi","https://maps.google.com/?q=Swiss+Chuchi+Zurich","bm")))

    d20 = card("Día 20","Sábado 13 junio — Uetliberg + Chocolates + Última noche","Zurich",
        row("09:00","Uetliberg — la montaña de Zurich",
            "870m. Tren S10 desde HB, 20 min, €5. Vista de Zurich, el lago y los Alpes. Bajada por sendero a Felsenegg.",
            tags=tag("⛰️ €5 tren","tw"), btns=btn("📍 Maps","https://maps.google.com/?q=Uetliberg+Zurich","bm")) +
        row("13:00","Chocolates Sprüngli + Mercado Bürkliplatz",
            "Sprüngli (desde 1836) — los mejores truffes du jour de Zurich. El mercado de Bürkliplatz los sábados tiene artesanías locales.",
            hi=True, tags=tag("🍫 Chocolates","tf"), btns=btn("📍 Sprüngli","https://maps.google.com/?q=Confiserie+Sprungli+Zurich","bm")) +
        row("19:00","Última cena del viaje 🥂",
            "Elegir el restaurante favorito de los días en Zurich. Brindar por el viaje. Hacer check-in online del vuelo LA8799.",
            hi=True, tags=tag("🥂 Despedida","tf")) +
        row("22:00","A dormir — vuelo 08:55 mañana",
            "Alarma: 06:00. Tren HB → ZRH: cada 10 min, 10 min de duración. Estar en aeropuerto a las 07:00.",
            tip="⚠️ ALARMA 06:00. Sin excepciones.", tags=tag("✈️ Alarma 06:00","tsl")))

    return al + h + tr + d18 + d19 + d20

CIUDAD_HTML = {
    "🏛️ Milán":       html_milan,
    "🌊 Cinque Terre": html_cinque,
    "🌸 Florencia":    html_florencia,
    "🏟️ Roma":         html_roma,
    "🍕 Nápoles":      html_napoles,
    "🌅 Costa Amalfi": html_amalfi,
    "🚤 Venecia":      html_venecia,
    "🇨🇭 Zurich":      html_zurich,
}

# ─── RESERVAS (separadas por tipo) ────────────────────────────────────────────
RESERVAS_MUSEOS = [
    {"id":"m01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_reservar":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.google.com/?q=Santa+Maria+delle+Grazie+Milan"},
    {"id":"m02","title":"Galería Borghese — Bernini","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_reservar":"https://www.galleriaborghese.it","url_maps":"https://maps.google.com/?q=Galleria+Borghese+Rome"},
    {"id":"m03","title":"Museos Vaticanos + Capilla Sixtina","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_reservar":"https://www.museivaticani.va","url_maps":"https://maps.google.com/?q=Vatican+Museums+Rome"},
    {"id":"m04","title":"Cúpula Brunelleschi — Duomo Florencia","city":"Florencia","fecha":"30 mayo","urgente":True,"url_reservar":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.google.com/?q=Duomo+Florence"},
    {"id":"m05","title":"David — Accademia Florencia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_reservar":"https://www.uffizi.it/en/the-accademia-gallery","url_maps":"https://maps.google.com/?q=Accademia+Gallery+Florence"},
    {"id":"m06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url_reservar":"https://www.uffizi.it","url_maps":"https://maps.google.com/?q=Uffizi+Gallery+Florence"},
    {"id":"m07","title":"Coliseo + Foro Romano + Palatino","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url_reservar":"https://www.coopculture.it","url_maps":"https://maps.google.com/?q=Colosseum+Rome"},
]

RESERVAS_ALOJ = [
    {"id":"a01","city":"Milán","fecha":"25–28 mayo","noches":3,"precio":"€70–90","url_b":"https://www.booking.com/searchresults.es.html?ss=Milan&checkin=2026-05-25&checkout=2026-05-28&group_adults=2","url_a":"https://www.airbnb.com/s/Milan--Italy/homes?checkin=2026-05-25&checkout=2026-05-28&adults=2","url_maps":"https://maps.google.com/?q=Milan+Italy"},
    {"id":"a02","city":"La Spezia","fecha":"28–30 mayo","noches":2,"precio":"€70–80","url_b":"https://www.booking.com/searchresults.es.html?ss=La+Spezia&checkin=2026-05-28&checkout=2026-05-30&group_adults=2","url_a":"https://www.airbnb.com/s/La-Spezia--Italy/homes?checkin=2026-05-28&checkout=2026-05-30&adults=2","url_maps":"https://maps.google.com/?q=La+Spezia+Italy"},
    {"id":"a03","city":"Florencia","fecha":"30 mayo–3 junio","noches":4,"precio":"€95–110","url_b":"https://www.booking.com/searchresults.es.html?ss=Florence&checkin=2026-05-30&checkout=2026-06-03&group_adults=2","url_a":"https://www.airbnb.com/s/Florence--Italy/homes?checkin=2026-05-30&checkout=2026-06-03&adults=2","url_maps":"https://maps.google.com/?q=Florence+Italy"},
    {"id":"a04","city":"Roma","fecha":"3–7 junio","noches":4,"precio":"€80–95","url_b":"https://www.booking.com/searchresults.es.html?ss=Rome&checkin=2026-06-03&checkout=2026-06-07&group_adults=2","url_a":"https://www.airbnb.com/s/Rome--Italy/homes?checkin=2026-06-03&checkout=2026-06-07&adults=2","url_maps":"https://maps.google.com/?q=Trastevere+Rome"},
    {"id":"a05","city":"Nápoles","fecha":"7–8 junio","noches":1,"precio":"€75–90","url_b":"https://www.booking.com/searchresults.es.html?ss=Naples&checkin=2026-06-07&checkout=2026-06-08&group_adults=2","url_a":"https://www.airbnb.com/s/Naples--Italy/homes?checkin=2026-06-07&checkout=2026-06-08&adults=2","url_maps":"https://maps.google.com/?q=Naples+Italy"},
    {"id":"a06","city":"Costa Amalfi (Praiano)","fecha":"8–10 junio","noches":2,"precio":"€85–100","url_b":"https://www.booking.com/searchresults.es.html?ss=Praiano&checkin=2026-06-08&checkout=2026-06-10&group_adults=2","url_a":"https://www.airbnb.com/s/Praiano--Italy/homes?checkin=2026-06-08&checkout=2026-06-10&adults=2","url_maps":"https://maps.google.com/?q=Praiano+Italy"},
    {"id":"a07","city":"Venecia","fecha":"10–11 junio","noches":1,"precio":"€90–110","url_b":"https://www.booking.com/searchresults.es.html?ss=Venice&checkin=2026-06-10&checkout=2026-06-11&group_adults=2","url_a":"","url_maps":"https://maps.google.com/?q=Venice+Italy"},
    {"id":"a08","city":"Zurich","fecha":"11–14 junio","noches":3,"precio":"€90–110","url_b":"https://www.booking.com/searchresults.es.html?ss=Zurich&checkin=2026-06-11&checkout=2026-06-14&group_adults=2","url_a":"","url_maps":"https://maps.google.com/?q=Zurich+Switzerland"},
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
    ("🍦","Gelato auténtico","Colores apagados, tapado con espátula, no en montañas brillantes = artesanal."),
    ("📱","Apps esenciales","Trenitalia · Italo · Maps.me offline · TheFork · SBB (Suiza) · Revolut para pagos."),
    ("🎾","Pádel Nuestro Roma","Día 12 tarde. Bullpadel, Siux, Babolat, Head. Pista interior para probar palas."),
    ("🛍️","Ropa barata — Milán","Corso Buenos Aires. 2km de tiendas. Zara, H&M, Bershka, marcas italianas."),
    ("🧀","Fondue — Zurich","Swiss Chuchi (Altstadt) ~€40/persona. Sprüngli desde 1836 para chocolates."),
]

PRES_FILAS = [
    ("Milán","3","€80","€240","https://booking.com","https://airbnb.com"),
    ("La Spezia","2","€75","€150","https://booking.com","https://airbnb.com"),
    ("Florencia","4","€100","€400","https://booking.com","https://airbnb.com"),
    ("Roma","4","€88","€350","https://booking.com","https://airbnb.com"),
    ("Nápoles","1","€80","€80","https://booking.com","https://airbnb.com"),
    ("Costa Amalfi","2","€92","€185","https://booking.com","https://airbnb.com"),
    ("Venecia","1","€100","€100","https://booking.com","—"),
    ("Zurich","3","€100","€300","https://booking.com","—"),
    ("TOTAL","20","~€95","~€1.805","",""),
]

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
try:
    df_res=load_r(); df_gas=load_g(); df_notas=load_n(); sheets_ok=True
except:
    df_res=df_gas=df_notas=pd.DataFrame(); sheets_ok=False

def get_rd(rid):
    if df_res.empty or "id" not in df_res.columns: return {}
    row2=df_res[df_res["id"]==rid]
    return row2.iloc[0].to_dict() if not row2.empty else {}

# ─── HERO ─────────────────────────────────────────────────────────────────────
ok_m = sum(1 for r in RESERVAS_MUSEOS if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
ok_a = sum(1 for r in RESERVAS_ALOJ   if get_rd(r["id"]).get("estado") in ("confirmed","paid"))
total_gas = pd.to_numeric(df_gas["monto"],errors="coerce").fillna(0).sum() if not df_gas.empty and "monto" in df_gas.columns else 0

st.markdown(f"""
<div class="hero"><div class="hi">
  <div class="hflag">🇮🇹 🇨🇭</div>
  <div class="htitle">Italia & <em>Zurich</em></div>
  <div class="hsub">Luna de Miel · Mayo–Junio 2026 · Compartido en tiempo real</div>
  <div class="hdates"><span>✈ Sale 24 mayo · IGU</span><span>·</span><span>Regresa 14 junio · ZRH</span></div>
</div></div>
<div class="sbar">
  <div class="si"><span class="sn">{ok_m}/{len(RESERVAS_MUSEOS)}</span><span class="sl2">Museos ok</span></div>
  <div class="si"><span class="sn">{ok_a}/{len(RESERVAS_ALOJ)}</span><span class="sl2">Hoteles ok</span></div>
  <div class="si"><span class="sn">€{total_gas:,.0f}</span><span class="sl2">Gastado</span></div>
  <div class="si"><span class="sn">20</span><span class="sl2">Días totales</span></div>
  <div class="si"><span class="sn">9</span><span class="sl2">Ciudades</span></div>
  <div class="si"><span class="sn">17</span><span class="sl2">En Italia</span></div>
</div>
""", unsafe_allow_html=True)

if sheets_ok:
    st.markdown('<span class="sok">🟢 Google Sheets conectado — ambos ven los mismos datos en tiempo real</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="serr">🔴 Sin conexión a Sheets — verificar credenciales</span>', unsafe_allow_html=True)

st.write("")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_vue,tab_itin,tab_museos,tab_aloj,tab_trans,tab_gas_t,tab_pres,tab_tips,tab_notas_t = st.tabs([
    "✈️ Vuelos","🗺️ Itinerario","🎟️ Museos/Entradas","🏨 Alojamientos",
    "🚄 Transportes","💰 Gastos","📊 Presupuesto","💡 Tips","📝 Notas"
])

# ══ VUELOS ════════════════════════════════════════════════════════════════════
with tab_vue:
    st.markdown('<div class="sh"><div class="st2">Vuelos confirmados</div><div class="sm">Itinerario LATAM + Swiss · Foz de Iguazú ↔ Zurich</div></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="card">
  <div class="ch"><span class="db">IDA</span><span class="cd">Domingo 24 mayo 2026 — Foz de Iguazú → Milán</span></div>
  <div class="tl">
    {row("14:50","IGU → São Paulo GRU","LA3879 op. LATAM Brasil · Airbus 320 · 1h 40min",hi=True,tags=tag("✈ LA3879 · A320","tr2"))}
    {row("16:30","Escala São Paulo Guarulhos (GRU)","Cambio de avión · 1h 30min de conexión · Considerar el traslado si aplica",alt=True)}
    {row("18:00","São Paulo GRU → Milán Malpensa MXP","LA8072 op. LATAM Brasil · Boeing 773 · 11h 15min · Llega 10:15 +1día",hi=True,tags=tag("✈ LA8072 · B777","tr2"))}
  </div>
</div>
<div class="card">
  <div class="ch"><span class="db">VUELTA</span><span class="cd">Domingo 14 junio 2026 — Zurich → Foz de Iguazú</span></div>
  <div class="tl">
    {row("08:55","Zurich ZRH → Milán Malpensa MXP","LA8799 op. Swiss · Avión 221 · 55min · Salir al aeropuerto a las 07:00",hi=True,tip="⚠️ Tren Zurich HB → ZRH: 10 min, sale cada 10 min. Alarma 06:00.",tags=tag("✈ LA8799 · Swiss","tr2"))}
    {row("09:50","Escala Milán Malpensa (MXP)","Cambio de avión · 3h 10min de conexión",alt=True)}
    {row("13:00","Milán MXP → São Paulo GRU","LA8073 op. LATAM Brasil · Boeing 773 · 12h",hi=True,tags=tag("✈ LA8073 · B777","tr2"))}
    {row("20:00","Escala São Paulo Guarulhos (GRU)","Cambio de avión · 2h 20min de conexión",alt=True)}
    {row("22:20","São Paulo GRU → Foz de Iguazú IGU","LA3206 op. LATAM Brasil · Airbus 321 · 1h 45min · Llega 00:05 +1día",hi=True,tags=tag("✈ LA3206 · A321","tr2"))}
  </div>
</div>
<div class="al">
  <strong>⚠️ Día 1 — Llegada 25 mayo:</strong> Llegan a las 10:15hs tras 11h de vuelo nocturno desde São Paulo.
  Primer día: guardar equipaje, almuerzo tranquilo, siesta obligatoria 2–3h, paseo suave al atardecer por Navigli.
  No planificar actividades intensas el primer día.
</div>
""", unsafe_allow_html=True)

# ══ ITINERARIO ════════════════════════════════════════════════════════════════
with tab_itin:
    ciudad_sel = st.radio("", list(CIUDAD_HTML.keys()), horizontal=True, label_visibility="collapsed")
    st.markdown(f'<div class="sh" style="margin-top:1rem"><div class="st2">{ciudad_sel}</div></div>', unsafe_allow_html=True)
    st.markdown(CIUDAD_HTML[ciudad_sel](), unsafe_allow_html=True)

# ══ MUSEOS / ENTRADAS ═════════════════════════════════════════════════════════
with tab_museos:
    st.markdown('<div class="sh"><div class="st2">🎟️ Museos y Entradas</div><div class="sm">Reservar en el sitio oficial — cargar N° de confirmación cuando esté hecho</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="al"><strong>⚠️ Urgente:</strong> La Última Cena, Galería Borghese y Museos Vaticanos se agotan con meses de anticipación. Gestionar hoy.</div>', unsafe_allow_html=True)

    for r in RESERVAS_MUSEOS:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        cc="ru" if r["urgente"] else "ro"
        conf_saved=str(rd.get("confirmacion",""))
        conf_html=f'<span style="font-size:0.78rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:2px 8px;border-radius:8px;margin-top:4px;display:inline-block">✓ Confirmación: {conf_saved}</span>' if conf_saved else ""

        st.markdown(f"""
        <div class="rc {cc}">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px">
            <span class="catbadge cat-museo">🎨 Museo</span>
            <span style="font-size:0.72rem;padding:2px 8px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span>
            <span class="rtitle">{"⚠️ " if r["urgente"] else ""}{r["title"]}</span>
            <span class="{bl}">{ll}</span>
          </div>
          <div class="rmeta">📅 {r["fecha"]}</div>
          {conf_html}
          <div style="margin-top:8px">
            {btn("🔗 Ir a reservar",r["url_reservar"],"bt")}
            {btn("📍 Maps",r["url_maps"],"bm")}
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(key=f"fm_{r['id']}"):
            c1,c2,c3=st.columns([2,2,1])
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],
                index=["pending","confirmed","paid"].index(ea),
                format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],
                key=f"sme_{r['id']}")
            with c2: nc=st.text_input("N° de confirmación",value=conf_saved,key=f"cme_{r['id']}",placeholder="ej. ABC123456")
            with c3: nm=st.number_input("Monto €",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"mme_{r['id']}")
            nn=st.text_area("Notas",value=str(rd.get("notas_int","")),key=f"nme_{r['id']}",height=50,placeholder="Ej: horario 09:15, entrada para 2 personas...")
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                if save_res(r["id"],ne,"Museo/Entrada","",nc,nm,nn):
                    st.success("✅ Guardado"); st.rerun()
        st.write("")

# ══ ALOJAMIENTOS ══════════════════════════════════════════════════════════════
with tab_aloj:
    st.markdown('<div class="sh"><div class="st2">🏨 Alojamientos</div><div class="sm">Cuando reserves en Airbnb o Booking, pegá la URL de la reserva confirmada — tu pareja la ve al instante</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="al alb"><strong>💡 Cómo usar:</strong> Buscá en Booking o Airbnb con los links de abajo → cuando confirmes la reserva → copiá la URL de confirmación → pegala aquí → Guardar. Tu pareja verá la URL, el número de confirmación y el monto al instante desde su teléfono.</div>', unsafe_allow_html=True)

    for r in RESERVAS_ALOJ:
        rd=get_rd(r["id"]); ea=rd.get("estado","pending")
        tipo_saved=str(rd.get("tipo",""))
        bl={"pending":"bp","confirmed":"bc","paid":"bpa"}.get(ea,"bp")
        ll={"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(ea,"⏳ Pendiente")
        us=str(rd.get("url_reserva",""))
        uh=f'<a href="{us}" target="_blank" class="usaved">🔗 {us[:80]}{"..." if len(us)>80 else ""}</a>' if us else ""
        tipo_ico={"Airbnb":"🏠","Booking.com":"📅","Directo / Otro":"🏷️"}.get(tipo_saved,"")
        tipo_html=f'<span style="font-size:0.78rem;color:#1A6B32;font-weight:600;background:#D4EDDA;padding:2px 8px;border-radius:8px;margin-left:8px">{tipo_ico} {tipo_saved}</span>' if tipo_saved else ""

        st.markdown(f"""
        <div class="rc ro">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:4px">
            <span class="catbadge cat-aloj">🏨 Alojamiento</span>
            <span style="font-size:0.72rem;padding:2px 8px;border-radius:20px;background:#F0EDE8;color:#6B7A8D;font-weight:600">{r["city"]}</span>
            <span class="rtitle">{r["city"]} — {r["noches"]} noches</span>
            <span class="{bl}">{ll}</span>{tipo_html}
          </div>
          <div class="rmeta">📅 {r["fecha"]} · Presupuesto: ~{r["precio"]}/noche</div>
          {uh}
          <div style="margin-top:8px">
            {btn("📅 Buscar en Booking",r["url_b"],"bk") if r["url_b"] else ""}
            {btn("🏠 Buscar en Airbnb",r["url_a"],"bab") if r["url_a"] else ""}
            {btn("📍 Maps",r["url_maps"],"bm")}
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(key=f"fa_{r['id']}"):
            c1,c2=st.columns([2,2])
            with c1: ne=st.selectbox("Estado",["pending","confirmed","paid"],
                index=["pending","confirmed","paid"].index(ea),
                format_func=lambda x:{"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}[x],
                key=f"sae_{r['id']}")
            with c2: tipo=st.selectbox("Reservado en",["","Airbnb","Booking.com","Directo / Otro"],
                index=["","Airbnb","Booking.com","Directo / Otro"].index(tipo_saved) if tipo_saved in ["","Airbnb","Booking.com","Directo / Otro"] else 0,
                key=f"tae_{r['id']}")
            nu=st.text_input("🔗 URL de la reserva confirmada",value=us,key=f"uae_{r['id']}",
                placeholder="Ej: https://www.airbnb.com/trips/v1/XXXXXXX  o  https://booking.com/hotel/...")
            c3,c4=st.columns(2)
            with c3: nc=st.text_input("N° confirmación",value=str(rd.get("confirmacion","")),key=f"cae_{r['id']}",placeholder="ej. HB-123456789")
            with c4: nm=st.number_input("Monto total pagado €",value=float(rd.get("monto",0) or 0),min_value=0.0,step=1.0,key=f"mae_{r['id']}")
            nn=st.text_area("Notas internas",value=str(rd.get("notas_int","")),key=f"nae_{r['id']}",height=50,
                placeholder="Ej: Check-in 15hs · Pedir habitación alta · Desayuno incluido · Parking disponible...")
            if st.form_submit_button("💾 Guardar — tu pareja lo ve al instante",use_container_width=True):
                if save_res(r["id"],ne,tipo,nu,nc,nm,nn):
                    st.success(f"✅ Guardado como {tipo or 'reserva'} — visible para tu pareja ahora"); st.rerun()
        st.write("")

# ══ TRANSPORTES ═══════════════════════════════════════════════════════════════
with tab_trans:
    st.markdown('<div class="sh"><div class="st2">Todos los transportes</div><div class="sm">En orden cronológico · Con links de compra</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="al alg"><strong>💡 Truco:</strong> Comprar trenes con 60 días de anticipación puede ser 4x más barato. Frecciarossa Roma→Nápoles: <strong>€9 anticipado</strong> vs €55 último momento.</div>', unsafe_allow_html=True)
    for icon,route,detail,price,url in TRANSPORTES:
        st.markdown(transporte(icon,route,detail,price,url), unsafe_allow_html=True)

# ══ GASTOS ════════════════════════════════════════════════════════════════════
with tab_gas_t:
    st.markdown('<div class="sh"><div class="st2">Tracker de Gastos</div><div class="sm">Cargá cada gasto — ambos lo ven en tiempo real</div></div>', unsafe_allow_html=True)
    PRES=4350.0
    cats={"Alojamiento":0,"Transporte":0,"Entradas":0,"Comidas":0,"Otros":0}
    if not df_gas.empty and "monto" in df_gas.columns and "categoria" in df_gas.columns:
        for _,rg in df_gas.iterrows():
            try: cats[rg.get("categoria","Otros")]=cats.get(rg.get("categoria","Otros"),0)+float(rg["monto"])
            except: pass
    total_g=sum(cats.values()); pct=min(100,int(total_g/PRES*100))
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("💶 Total",f"€{total_g:,.0f}",f"{pct}% del presupuesto")
    c2.metric("🏨 Alojamiento",f"€{cats['Alojamiento']:,.0f}")
    c3.metric("🚄 Transporte",f"€{cats['Transporte']:,.0f}")
    c4.metric("🎟️ Entradas",f"€{cats['Entradas']:,.0f}")
    c5.metric("🍽️ Comidas",f"€{cats['Comidas']:,.0f}")
    st.markdown(f'<div class="prog-o"><div class="prog-i" style="width:{pct}%"></div></div><div style="font-size:0.75rem;color:#6B7A8D;margin-top:4px;font-weight:500">€{total_g:,.0f} gastados de €{PRES:,.0f} presupuestados ({pct}%)</div>', unsafe_allow_html=True)
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
        di=st.text_input("ID de gasto a eliminar",placeholder="ej. g0510143022")
        if st.button("🗑️ Eliminar") and di:
            if del_g(di.strip()): st.success("Eliminado ✓"); st.rerun()
    else: st.info("Aún no hay gastos. ¡Agregá el primero!")

# ══ PRESUPUESTO ═══════════════════════════════════════════════════════════════
with tab_pres:
    st.markdown('<div class="sh"><div class="st2">Presupuesto estimado</div><div class="sm">Para 2 personas · 20 días · Sin vuelos</div></div>', unsafe_allow_html=True)
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
    for ciudad,noches,precio,total,ub,ua in PRES_FILAS:
        es_tot=ciudad=="TOTAL"
        cls='class="tot"' if es_tot else ""
        rows+=f"<tr {cls}><td>{ciudad}</td><td style='text-align:center'>{noches}</td><td style='text-align:center'>{precio}</td><td style='text-align:center;font-weight:700'>{total}</td></tr>"
    st.markdown(f'<div class="card" style="padding:0"><table class="bt2"><thead><tr><th>Ciudad</th><th style="text-align:center">Noches</th><th style="text-align:center">€/noche</th><th style="text-align:center">Total</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

# ══ TIPS ══════════════════════════════════════════════════════════════════════
with tab_tips:
    st.markdown('<div class="sh"><div class="st2">Tips esenciales</div><div class="sm">Lo que marca la diferencia entre turista y viajero</div></div>', unsafe_allow_html=True)
    cols=st.columns(3)
    for i,(icon,title,text) in enumerate(TIPS):
        with cols[i%3]:
            st.markdown(f'<div class="tip-c"><div class="tip-i">{icon}</div><div class="tip-t">{title}</div><div class="tip-tx">{text}</div></div>', unsafe_allow_html=True)
            st.write("")

# ══ NOTAS ═════════════════════════════════════════════════════════════════════
with tab_notas_t:
    st.markdown('<div class="sh"><div class="st2">Notas compartidas</div><div class="sm">Cualquiera puede publicar — el otro lo ve al instante</div></div>', unsafe_allow_html=True)
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
        for _,rn in df_notas.iloc[::-1].iterrows():
            st.markdown(f'<div class="nota-c"><strong>{rn.get("tag","📝")}</strong> · <em style="color:#6B7A8D">{rn.get("autor","")}</em><br><span style="color:#1A1A2E">{rn.get("texto","")}</span><div class="nota-m">🕐 {rn.get("fecha","")}</div></div>', unsafe_allow_html=True)
            if st.button("🗑️ Borrar",key=f"dn_{rn.get('id','')}"):
                if del_nota(str(rn.get("id",""))): st.rerun()
    else: st.info("Aún no hay notas. ¡Publicá la primera!")
