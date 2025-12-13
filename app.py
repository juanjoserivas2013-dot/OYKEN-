import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")

DATA_FILE = Path("ventas.csv")

# --- Cargar datos ---
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=[
        "fecha",
        "ventas_manana_eur",
        "ventas_tarde_eur",
        "ventas_noche_eur",
        "ventas_total_eur",
    ])

# =========================
# REGISTRO / EDICIÓN DIARIA
# =========================
st.subheader("Registro / Edición diaria")

# Selector de fecha a editar o crear
fechas_existentes = sorted(df["fecha"].dt.date.unique()) if not df.empty else []
fecha_sel = st.date_input(
    "Fecha",
    value=date.today(),
    min_value=None,
    max_value=None
)

# Cargar valores si existen
row = df[df["fecha"].dt.date == fecha_sel]
vm0 = float(row["ventas_manana_eur"].iloc[0]) if not row.empty else 0.0
vt0 = float(row["ventas_tarde_eur"].iloc[0]) if not row.empty else 0.0
vn0 = float(row["ventas_noche_eur"].iloc[0]) if not row.empty else 0.0
tot0 = float(row["ventas_total_eur"].iloc[0]) if not row.empty else 0.0

with st.form("form_editar"):
    st.caption("Desglose por franja (opcional)")
    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f", value=vm0)
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f", value=vt0)
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f", value=vn0)

    st.caption("O introduce el total directamente")
    total_manual = st.number_input("Total del día (€)", min_value=0.0, step=10.0, format="%.2f", value=tot0)

    guardar = st.form_submit_button("Guardar cambios")

if guardar:
    total_calc = vm + vt + vn
    ventas_total = total_calc if total_calc > 0 else total_manual

    # eliminar registro previo de ese día (si existe)
    df = df[df["fecha"].dt.date != fecha_sel]

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha_sel),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": ventas_total
    }])

    df = pd.concat([df, nueva], ignore_index=True).sort_values("fecha")
    df.to_csv(DATA_FILE, index=False)
    st.success("Día guardado correctamente")

st.divider()

# =========================
# VISTA MENSUAL
# =========================
st.subheader("Vista mensual")

if not df.empty:
    df["año"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["dia"] = df["fecha"].dt.day
    df["dow"] = df["fecha"].dt.day_name(locale="es_ES")

    col1, col2 = st.columns(2)
    with col1:
        años = sorted(df["año"].unique())
        año_sel = st.selectbox("Año", años, index=len(años)-1)
    with col2:
        mes_sel = st.selectbox(
            "Mes",
            list(range(1,13)),
            format_func=lambda m: ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                                    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1]
        )

    mensual = (
        df[(df["año"] == año_sel) & (df["mes"] == mes_sel)]
        .sort_values("fecha")
        [["fecha","dia","dow","ventas_manana_eur","ventas_tarde_eur","ventas_noche_eur","ventas_total_eur"]]
    )

    st.dataframe(mensual, use_container_width=True, hide_index=True)

    tot_mes = mensual["ventas_total_eur"].sum()
    prom = mensual["ventas_total_eur"].mean() if not mensual.empty else 0
    c1, c2 = st.columns(2)
    c1.metric("Total mes (€)", f"{tot_mes:,.2f}")
    c2.metric("Promedio diario (€)", f"{prom:,.2f}")
else:
    st.info("Aún no hay datos.")

st.divider()

# =========================
# VISTA SEMANAL
# =========================
st.subheader("Vista semanal")

if not df.empty:
    ref = st.date_input("Semana que contiene", value=date.today(), key="week_ref")
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)

    semana = df[(df["fecha"] >= pd.to_datetime(monday)) & (df["fecha"] <= pd.to_datetime(sunday))].copy()
    semana["dow"] = semana["fecha"].dt.day_name(locale="es_ES")
    semana = semana.sort_values("fecha")

    st.caption(f"Semana: {monday} → {sunday}")

    st.dataframe(
        semana[["fecha","dow","ventas_manana_eur","ventas_tarde_eur","ventas_noche_eur","ventas_total_eur"]],
        use_container_width=True,
        hide_index=True
    )

    total_sem = semana["ventas_total_eur"].sum()
    prom_sem = semana["ventas_total_eur"].mean() if not semana.empty else 0

    prev_monday = monday - timedelta(days=7)
    prev_sunday = sunday - timedelta(days=7)
    prev = df[(df["fecha"] >= pd.to_datetime(prev_monday)) & (df["fecha"] <= pd.to_datetime(prev_sunday))]
    total_prev = prev["ventas_total_eur"].sum()
    var = ((total_sem - total_prev) / total_prev * 100) if total_prev > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total semana (€)", f"{total_sem:,.2f}")
    c2.metric("Promedio diario (€)", f"{prom_sem:,.2f}")
    c3.metric("Vs semana anterior", f"{var:+.1f}%")
else:
    st.info("Aún no hay datos.")
