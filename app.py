import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="OYKEN · Control Operativo", layout="centered")
st.title("OYKEN · Control Operativo")
st.caption("Sistema automático de control diario y memoria operativa")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

MESES_ES = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
]

COLUMNAS_BASE = [
    "fecha",
    "ventas_manana_eur",
    "ventas_tarde_eur",
    "ventas_noche_eur",
    "ventas_total_eur",
    "observaciones"
]

# =========================
# CARGA Y NORMALIZACIÓN
# =========================
if DATA_FILE.exists():
    df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
else:
    df = pd.DataFrame(columns=COLUMNAS_BASE)

# 🔒 BLINDAJE: asegurar columnas siempre
for col in COLUMNAS_BASE:
    if col not in df.columns:
        df[col] = ""

df["observaciones"] = df["observaciones"].fillna("")

# =========================
# REGISTRO DIARIO
# =========================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    c1, c2, c3 = st.columns(3)
    with c1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0)
    with c2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0)
    with c3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0)

    observaciones = st.text_area(
        "Observaciones del día",
        placeholder="Clima, evento, promoción, incidencia, obra, partido…",
        height=80
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
        "observaciones": observaciones.strip()
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Venta guardada correctamente")
    st.rerun()

# =========================
# SI NO HAY DATOS
# =========================
if df.empty:
    st.info("Aún no hay ventas registradas.")
    st.stop()

# =========================
# CAMPOS DERIVADOS
# =========================
df = df.sort_values("fecha")
df["año"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia"] = df["fecha"].dt.day
df["dow"] = df["fecha"].dt.weekday.map(DOW_ES)

# =========================
# BITÁCORA MENSUAL
# =========================
st.divider()
st.subheader("Ventas del mes (bitácora viva)")

hoy = pd.to_datetime(date.today())
df_mes = df[(df["mes"] == hoy.month) & (df["año"] == hoy.year)].copy()

df_mes["fecha"] = df_mes["fecha"].dt.strftime("%d-%m-%Y")

st.dataframe(
    df_mes[
        [
            "fecha",
            "dow",
            "ventas_manana_eur",
            "ventas_tarde_eur",
            "ventas_noche_eur",
            "ventas_total_eur",
            "observaciones"
        ]
    ],
    hide_index=True,
    use_container_width=True
)
