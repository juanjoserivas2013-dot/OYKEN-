import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")

st.title("OYKEN · Control Operativo")
st.markdown("**Entra en Oyken. En 30 segundos entiendes mejor tu negocio.**")
st.caption("Sistema automático basado en criterio operativo")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

COLUMNAS = [
    "fecha",
    "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur", "ventas_total_eur",
    "comensales_manana", "comensales_tarde", "comensales_noche",
    "tickets_manana", "tickets_tarde", "tickets_noche",
    "observaciones"
]

# =========================
# CARGA DE DATOS
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS)

for col in COLUMNAS:
    if col not in df.columns:
        df[col] = 0 if col not in ["fecha", "observaciones"] else ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas", clear_on_submit=True):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    st.markdown("**Ventas (€)**")
    v1, v2, v3 = st.columns(3)
    with v1:
        vm = st.number_input("Mañana", min_value=0.0, step=10.0)
    with v2:
        vt = st.number_input("Tarde", min_value=0.0, step=10.0)
    with v3:
        vn = st.number_input("Noche", min_value=0.0, step=10.0)

    st.markdown("**Comensales**")
    c1, c2, c3 = st.columns(3)
    with c1:
        cm = st.number_input("Mañana ", min_value=0, step=1)
    with c2:
        ct = st.number_input("Tarde ", min_value=0, step=1)
    with c3:
        cn = st.number_input("Noche ", min_value=0, step=1)

    st.markdown("**Tickets**")
    t1, t2, t3 = st.columns(3)
    with t1:
        tm = st.number_input("Mañana  ", min_value=0, step=1)
    with t2:
        tt = st.number_input("Tarde  ", min_value=0, step=1)
    with t3:
        tn = st.number_input("Noche  ", min_value=0, step=1)

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Clima, eventos, incidencias, promociones, obras, festivos…",
        height=100
    )

    guardar = st.form_submit_button("Guardar venta")

if guardar:
    total = vm + vt + vn

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total,
        "comensales_manana": cm,
        "comensales_tarde": ct,
        "comensales_noche": cn,
        "tickets_manana": tm,
        "tickets_tarde": tt,
        "tickets_noche": tn,
        "observaciones": observaciones.strip()
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)
    st.success("Venta guardada correctamente")
    st.rerun()

if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# PREPARACIÓN ISO (REGLA CORRECTA GRANDES CADENAS)
# =========================
df = df.sort_values("fecha")
iso = df["fecha"].dt.isocalendar()
df["iso_year"] = iso.year
df["iso_week"] = iso.week
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

# =========================
# BLOQUE HOY — DEFINITIVO
# =========================
st.divider()
st.subheader("HOY")

fecha_hoy = pd.to_datetime(date.today())
dow_hoy = DOW_ES[fecha_hoy.weekday()]

# -------------------------
# DATOS HOY
# -------------------------
venta_hoy = df[df["fecha"] == fecha_hoy]

def safe(row, col):
    return row[col] if col in row else 0

if venta_hoy.empty:
    vm_h = vt_h = vn_h = total_h = 0.0
    cm_h = ct_h = cn_h = 0
    tm_h = tt_h = tn_h = 0
else:
    r = venta_hoy.iloc[0]
    vm_h = r["ventas_manana_eur"]
    vt_h = r["ventas_tarde_eur"]
    vn_h = r["ventas_noche_eur"]
    total_h = r["ventas_total_eur"]

    cm_h = safe(r, "comensales_manana")
    ct_h = safe(r, "comensales_tarde")
    cn_h = safe(r, "comensales_noche")

    tm_h = safe(r, "tickets_manana")
    tt_h = safe(r, "tickets_tarde")
    tn_h = safe(r, "tickets_noche")

# -------------------------
# DOW AÑO ANTERIOR (REGLA CORRECTA)
# → mismo weekday, semana equivalente
# -------------------------
fecha_base = fecha_hoy - pd.DateOffset(weeks=52)

cand = df[df["fecha"].dt.weekday == fecha_hoy.weekday()].copy()
cand["dist"] = (cand["fecha"] - fecha_base).abs()

if cand.empty:
    fecha_a_txt = "Sin histórico comparable"
    vm_a = vt_a = vn_a = total_a = 0.0
    cm_a = ct_a = cn_a = 0
    tm_a = tt_a = tn_a = 0
else:
    comp = cand.sort_values("dist").iloc[0]
    fecha_a_txt = f"{DOW_ES[comp['fecha'].weekday()]} · {comp['fecha'].strftime('%d/%m/%Y')}"

    vm_a = comp["ventas_manana_eur"]
    vt_a = comp["ventas_tarde_eur"]
    vn_a = comp["ventas_noche_eur"]
    total_a = comp["ventas_total_eur"]

    cm_a = safe(comp, "comensales_manana")
    ct_a = safe(comp, "comensales_tarde")
    cn_a = safe(comp, "comensales_noche")

    tm_a = safe(comp, "tickets_manana")
    tt_a = safe(comp, "tickets_tarde")
    tn_a = safe(comp, "tickets_noche")

# -------------------------
# FUNCIONES DE VARIACIÓN (REGLA OIKEN)
# -------------------------
def variacion(actual, base):
    diff = actual - base

    if base > 0:
        pct = diff / base * 100
    else:
        pct = 100.0 if actual > 0 else 0.0

    if diff > 0:
        s_diff = f"+{diff}"
        s_pct = f"+{pct:.1f}%"
    elif diff < 0:
        s_diff = f"{diff}"
        s_pct = f"{pct:.1f}%"
    else:
        s_diff = "0"
        s_pct = "0%"

    return s_diff, s_pct

def color_eur(v):
    if v > 0:
        return "green"
    if v < 0:
        return "red"
    return "gray"

def icono_pct(pct):
    if pct >= 30:
        return "👁️"
    elif pct >= 1:
        return "↑"
    elif pct <= -30:
        return "⚠️"
    elif pct <= -1:
        return "↓"
    return ""

# -------------------------
# CÁLCULOS €
# -------------------------
d_vm, p_vm = variacion(vm_h, vm_a)
d_vt, p_vt = variacion(vt_h, vt_a)
d_vn, p_vn = variacion(vn_h, vn_a)
d_tot, p_tot = variacion(total_h, total_a)

# -------------------------
# CÁLCULOS COMENSALES / TICKETS
# -------------------------
cm_d, cm_p = variacion(cm_h, cm_a)
ct_d, ct_p = variacion(ct_h, ct_a)
cn_d, cn_p = variacion(cn_h, cn_a)

tm_d, tm_p = variacion(tm_h, tm_a)
tt_d, tt_p = variacion(tt_h, tt_a)
tn_d, tn_p = variacion(tn_h, tn_a)

# -------------------------
# DISPOSICIÓN VISUAL
# -------------------------
c1, c2, c3 = st.columns(3)

# --- HOY ---
with c1:
    st.markdown("**HOY**")
    st.caption(f"{dow_hoy} · {fecha_hoy.strftime('%d/%m/%Y')}")

    st.write("**Mañana**")
    st.write(f"{vm_h:,.2f} € · {cm_h} com · {tm_h} tickets")

    st.write("**Tarde**")
    st.write(f"{vt_h:,.2f} € · {ct_h} com · {tt_h} tickets")

    st.write("**Noche**")
    st.write(f"{vn_h:,.2f} € · {cn_h} com · {tn_h} tickets")

    st.markdown("---")
    st.markdown(f"### TOTAL HOY\n{total_h:,.2f} €")

# --- DOW ---
with c2:
    st.markdown("**DOW (Año anterior)**")
    st.caption(fecha_a_txt)

    st.write(f"**Mañana**  {vm_a:,.2f} € · {cm_a} com · {tm_a} tickets")
    st.write(f"**Tarde**   {vt_a:,.2f} € · {ct_a} com · {tt_a} tickets")
    st.write(f"**Noche**   {vn_a:,.2f} € · {cn_a} com · {tn_a} tickets")

    st.markdown("---")
    st.markdown(f"### TOTAL DOW\n{total_a:,.2f} €")

# --- VARIACIÓN ---
with c3:
    st.markdown("**VARIACIÓN**")
    st.caption("Vs. DOW año anterior")

    st.markdown(
        f"**Mañana** "
        f"<span style='color:{color_eur(vm_h - vm_a)}'>"
        f"{d_vm} € ({p_vm}) {icono_pct(float(p_vm.replace('%','').replace('+','')))}"
        f"</span><br>"
        f"<span style='color:gray;font-size:0.85em'>"
        f"Comensales: {cm_d} ({cm_p}) · Tickets: {tm_d} ({tm_p})"
        f"</span>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Tarde** "
        f"<span style='color:{color_eur(vt_h - vt_a)}'>"
        f"{d_vt} € ({p_vt}) {icono_pct(float(p_vt.replace('%','').replace('+','')))}"
        f"</span><br>"
        f"<span style='color:gray;font-size:0.85em'>"
        f"Comensales: {ct_d} ({ct_p}) · Tickets: {tt_d} ({tt_p})"
        f"</span>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Noche** "
        f"<span style='color:{color_eur(vn_h - vn_a)}'>"
        f"{d_vn} € ({p_vn}) {icono_pct(float(p_vn.replace('%','').replace('+','')))}"
        f"</span><br>"
        f"<span style='color:gray;font-size:0.85em'>"
        f"Comensales: {cn_d} ({cn_p}) · Tickets: {tn_d} ({tn_p})"
        f"</span>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown(
        f"### TOTAL "
        f"<span style='color:{color_eur(total_h - total_a)}'>"
        f"{d_tot} € ({p_tot})"
        f"</span>",
        unsafe_allow_html=True
    )

# =========================
# BITÁCORA DEL MES
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

df_mes = df[
    (df["fecha"].dt.month == fecha_hoy.month) &
    (df["fecha"].dt.year == fecha_hoy.year)
].copy()

df_mes["fecha_display"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")
df_mes["fecha_display"] = df_mes.apply(
    lambda r: f"{r['fecha_display']} 👁️" if r["observaciones"].strip() else r["fecha_display"],
    axis=1
)

st.dataframe(
    df_mes[[
        "fecha_display", "dow",
        "ventas_manana_eur", "ventas_tarde_eur", "ventas_noche_eur",
        "ventas_total_eur",
        "comensales_manana", "comensales_tarde", "comensales_noche",
        "tickets_manana", "tickets_tarde", "tickets_noche",
        "observaciones"
    ]].rename(columns={"fecha_display": "fecha"}),
    hide_index=True,
    use_container_width=True
  )
