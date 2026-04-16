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
    except:
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
        st.error(f"Error: {e}")
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
    except: return False

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
    except: return False

# ─── DATOS ───────────────────────────────────────────────────────────────────
RESERVAS_DEF = [
    {"id":"r01","title":"La Última Cena — Da Vinci","city":"Milán","fecha":"26 mayo · 08:15","urgente":True,"url_book":"https://cenacolodavincimilano.vivaticket.com","url_maps":"https://maps.app.goo.gl/0"},
    {"id":"r02","title":"Galería Borghese","city":"Roma","fecha":"5 junio · tarde","urgente":True,"url_book":"https://www.galleriaborghese.it","url_maps":"https://maps.app.goo.gl/1"},
    {"id":"r03","title":"Museos Vaticanos","city":"Roma","fecha":"3 junio · 08:00","urgente":True,"url_book":"https://www.museivaticani.va","url_maps":"https://maps.app.goo.gl/2"},
    {"id":"r04","title":"Cúpula Brunelleschi","city":"Florencia","fecha":"30 mayo · tarde","urgente":True,"url_book":"https://www.ilgrandemuseodelduomo.it","url_maps":"https://maps.app.goo.gl/3"},
    {"id":"r05","title":"David — Accademia","city":"Florencia","fecha":"31 mayo · 14:00","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.app.goo.gl/4"},
    {"id":"r06","title":"Galería degli Uffizi","city":"Florencia","fecha":"31 mayo · 08:30","urgente":False,"url_book":"https://www.uffizi.it","url_maps":"https://maps.app.goo.gl/5"},
    {"id":"r07","title":"Coliseo + Foro Romano","city":"Roma","fecha":"4 junio · 08:00","urgente":False,"url_book":"https://www.coopculture.it","url_maps":"https://maps.app.goo.gl/6"},
    {"id":"r08","title":"Alojamiento Milán","city":"Milán","fecha":"25–28 mayo","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/7"},
    {"id":"r09","title":"Alojamiento La Spezia","city":"Cinque Terre","fecha":"28–30 mayo","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/8"},
    {"id":"r10","title":"Alojamiento Florencia","city":"Florencia","fecha":"30 mayo–3 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/9"},
    {"id":"r11","title":"Alojamiento Roma","city":"Roma","fecha":"3–7 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/10"},
    {"id":"r12","title":"Alojamiento Nápoles","city":"Nápoles","fecha":"7–8 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/11"},
    {"id":"r13","title":"Alojamiento Praiano","city":"Amalfi","fecha":"8–10 junio","urgente":False,"url_book":"https://www.airbnb.com","url_maps":"https://maps.app.goo.gl/12"},
    {"id":"r14","title":"Alojamiento Venecia","city":"Venecia","fecha":"10–11 junio","urgente":False,"url_book":"https://www.booking.com","url_maps":"https://maps.app.goo.gl/13"},
    {"id":"r15","title":"Alojamiento Zurich","city":"Zurich","fecha":"11–14 junio","urgente":False,"url_book":"https://www.booking.com","url_maps":"https://maps.app.goo.gl/14"},
]

ITINERARIO = [
    {"city":"🏛️ Milán","dates":"D1–3 · 25–27 mayo","days":[
        {"n":"D1","date":"25 mayo","title":"Llegada y Navigli","events":[
            {"t":"10:15","hi":True,"ttl":"Llegada MXP — Inmigración","desc":"Pasaporte argentino. Calcular 30–45 min.","maps":"https://maps.app.goo.gl/15"},
            {"t":"11:30","hi":False,"ttl":"Malpensa Express → Centrale","desc":"52 min · €13/p · Validar antes de subir.","maps":"https://maps.app.goo.gl/16"},
            {"t":"13:30","hi":False,"ttl":"Check-in + almuerzo","desc":"Risotto alla milanese. Evitar cercanías de estaciones."},
            {"t":"18:00","hi":False,"ttl":"Navigli + Aperitivo","desc":"Aperol Spritz junto al canal.","maps":"https://maps.app.goo.gl/17"},
        ]},
        {"n":"D2","date":"26 mayo","title":"Da Vinci y Duomo","events":[
            {"t":"08:15","hi":True,"ttl":"★ LA ÚLTIMA CENA","desc":"Reserva obligatoria. 15 min de visita exacta.","tip":"Vivaticket urgente","maps":"https://maps.app.goo.gl/0"},
            {"t":"10:30","hi":True,"ttl":"Duomo — terrazas","desc":"Ascensor a los chapiteles. Reservar online.","maps":"https://maps.app.goo.gl/18"},
            {"t":"15:00","hi":False,"ttl":"Corso Buenos Aires","desc":"Shopping. La calle comercial más larga.","maps":"https://maps.app.goo.gl/21"},
        ]},
    ]}
]

TRANSPORTES = [
    ("✈️→🚄","MXP → Milano Centrale","Malpensa Express · €13/p","€13","https://www.trenord.it"),
    ("🚄","Milano → La Spezia","Intercity · 3h","€25–35","https://www.trenitalia.com"),
    ("🚄","Firenze → Roma","Frecciarossa · 1h30","€25–45","https://www.trenitalia.com"),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def badge_html(estado):
    cls = {"pending":"badge-pending","confirmed":"badge-confirmed","paid":"badge-paid"}.get(estado,"badge-pending")
    lbl = {"pending":"⏳ Pendiente","confirmed":"✅ Confirmado","paid":"💳 Pagado"}.get(estado,"⏳ Pendiente")
    return f'<span class="{cls}">{lbl}</span>'

# ─── CARGA ────────────────────────────────────────────────────────────────────
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

st.markdown(f"""<div class="hero-box">
<div class="hero-title">🇮🇹 Italia & Zurich 2026 🇨🇭</div>
<div class="hero-sub">Luna de Miel · 25 mayo → 14 junio · Tiempo real</div>
<div class="hero-stats">
<div><span class="hstat-n">{ok_count}/{len(RESERVAS_DEF)}</span><span class="hstat-l">Reservas ok</span></div>
<div><span class="hstat-n">€{total_gas:,.0f}</span><span class="hstat-l">Gastado</span></div>
<div><span class="hstat-n">20</span><span class="hstat-l">Días</span></div>
</div>
</div>""", unsafe_allow_html=True)

if sheets_ok: st.markdown('<span class="sync-ok">🟢 Google Sheets conectado</span>', unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
t_res, t_itin, t_trans, t_gas, t_notas = st.tabs(["🎟️ Reservas", "🗺️ Itinerario", "🚄 Transportes", "💰 Gastos", "📝 Notas"])

with t_res:
    for r in RESERVAS_DEF:
        rd = get_reserva_data(r["id"])
        st.markdown(f'<div class="res-card {"res-card-urgente" if r["urgente"] else "res-card-ok"}"><strong>{r["title"]}</strong> {badge_html(rd.get("estado","pending"))}<br><small>{r["city"]} · {r["fecha"]}</small></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nestado = st.selectbox("Estado", ["pending","confirmed","paid"], key=f"s{r['id']}")
        with c2: nmonto = st.number_input("€", value=float(rd.get("monto",0) or 0), key=f"m{r['id']}")
        nurl = st.text_input("URL", value=rd.get("url_reserva",""), key=f"u{r['id']}")
        if st.button("Guardar", key=f"b{r['id']}"):
            if save_reserva(r["id"], nestado, nurl, "", nmonto, ""): st.rerun()

with t_itin:
    selected_city = st.selectbox("Ciudad", [c["city"] for c in ITINERARIO])
    city_data = next(c for c in ITINERARIO if c["city"] == selected_city)
    for day in city_data["days"]:
        with st.expander(f"{day['n']} · {day['date']} — {day['title']}"):
            for ev in day["events"]:
                dot = "🟠" if ev["hi"] else "⚪"
                tip_h = f'<div class="t-tip">⚠️ {ev["tip"]}</div>' if ev.get("tip") else ""
                # HTML en una sola línea para evitar fallos de Markdown
                h_ev = f'<div class="t-row"><span class="t-time">{ev["t"]}</span><span>{dot}</span><div><div class="t-ttl">{ev["ttl"]}</div><div class="t-desc">{ev["desc"]}</div>{tip_h}</div></div>'
                st.markdown(h_ev, unsafe_allow_html=True)
                if ev.get("maps"): st.markdown(f'<a href="{ev["maps"]}" target="_blank" style="font-size:0.8rem;margin-left:60px">📍 Ver en Maps</a>', unsafe_allow_html=True)

with t_trans:
    for icon, route, detail, price, url in TRANSPORTES:
        st.markdown(f'<div class="trans-card"><span>{icon}</span> <strong>{route}</strong> ({detail}) <span style="margin-left:auto">{price}</span></div>', unsafe_allow_html=True)

with t_gas:
    st.metric("Total Gastado", f"€{total_gas:,.0f}")
    with st.form("gasto"):
        d = st.text_input("Descripción")
        c = st.selectbox("Categoría", ["Alojamiento","Transporte","Entradas","Comidas","Otros"])
        m = st.number_input("Monto €", min_value=0.0)
        if st.form_submit_button("Agregar"):
            if add_gasto(d, c, m): st.rerun()
    if not df_gas.empty: st.dataframe(df_gas[["descripcion","categoria","monto","fecha"]], use_container_width=True, hide_index=True)

with t_notas:
    with st.form("nota"):
        txt = st.text_area("Nueva nota")
        aut = st.selectbox("Quién", ["Adilson","Esposa"])
        if st.form_submit_button("Publicar"):
            if add_nota(txt, "General", aut): st.rerun()
    if not df_notas.empty:
        for _, n in df_notas.iloc[::-1].iterrows():
            st.markdown(f'<div class="nota-card"><strong>{n["autor"]}</strong>: {n["texto"]}<div class="nota-meta">{n["fecha"]}</div></div>', unsafe_allow_html=True)
