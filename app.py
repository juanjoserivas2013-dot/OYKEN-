import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="OYKEN · Ventas", layout="centered")
st.title("OYKEN · Ventas")

DATA_FILE = Path("ventas.csv")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# =====================
# CARGA DATOS
# =====================
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

# =====================
# REGISTRO DIARIO
# =====================
st.subheader("Registro diario")

with st.form("form_ventas"):
    fecha = st.date_input("Fecha", value=date.today())

    col1, col2, col3 = st.columns(3)
    with col1:
        vm = st.number_input("Mañana (€)", min_value=0.0, step=10.0, format="%.2f")
    with col2:
        vt = st.number_input("Tarde (€)", min_value=0.0, step=10.0, format="%.2f")
    with col3:
        vn = st.number_input("Noche (€)", min_value=0.0, step=10.0, format="%.2f")

    guardar = st.form_submit_button("Guardar")

if guardar:
    total = vm + vt + vn

    nueva = pd.DataFrame([{
        "fecha": pd.to_datetime(fecha),
        "ventas_manana_eur": vm,
        "ventas_tarde_eur": vt,
        "ventas_noche_eur": vn,
        "ventas_total_eur": total
    }])

    df = pd.concat([df, nueva], ignore_index=True)
    df = df.drop_duplicates(subset=["fecha"], keep="last")
    df.to_csv(DATA_FILE, index=False)

    st.success("Venta guardada correctamente")

st.divider()

# =====================
# VISTA MENSUAL
# =====================
st.subheader("Vista mensual")

if df.empty:
    st.info("No hay datos todavía.")
    st.stop()

df["año"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["dia"] = df["fecha"].dt.day
df["dow"] = df["fecha"].dt.weekday.map(
    {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}
)

col1, col2 = st.columns(2)
with col1:
    año_sel = st.selectbox("Año", sorted(df["año"].unique()), index=-1)
with col2:
    mes_sel = st.selectbox(
        "Mes",
        list(range(1, 13)),
        format_func=lambda m: MESES[m-1]
    )

df_mes = df[(df["año"] == año_sel) & (df["mes"] == mes_sel)].sort_values("fecha")

st.dataframe(
    df_mes[[
        "fecha", "dia", "dow",
        "ventas_manana_eur", "ventas_tarde_eur",
        "ventas_noche_eur", "ventas_total_eur"
    ]],
    hide_index=True,
    use_container_width=True
)

# =====================
# RESUMEN MENSUAL
# =====================
st.divider()
st.subheader("Resumen mensual · Acumulado vs mes anterior")

# --- Mes actual ---
total_actual = df_mes["ventas_total_eur"].sum()
dias_actual = df_mes[df_mes["ventas_total_eur"] > 0].shape[0]
prom_actual = total_actual / dias_actual if dias_actual > 0 else 0

# --- Mes anterior ---
if mes_sel == 1:
    mes_ant = 12
    año_ant = año_sel - 1
else:
    mes_ant = mes_sel - 1
    año_ant = año_sel

df_mes_ant = df[(df["año"] == año_ant) & (df["mes"] == mes_ant)]

total_ant = df_mes_ant["ventas_total_eur"].sum()
dias_ant = df_mes_ant[df_mes_ant["ventas_total_eur"] > 0].shape[0]
prom_ant = total_ant / dias_ant if dias_ant > 0 else 0

# --- Diferencias ---
dif_total = total_actual - total_ant
dif_dias = dias_actual - dias_ant
dif_prom_pct = ((prom_actual / prom_ant) - 1) * 100 if prom_ant > 0 else 0

# --- Labels dinámicos ---
mes_actual_txt = f"{MESES[mes_sel-1]} {año_sel}"
mes_anterior_txt = f"{MESES[mes_ant-1]} {año_ant}"
comparativa_txt = f"{MESES[mes_sel-1]} vs {MESES[mes_ant-1]}"

# =====================
# BLOQUE VISUAL
# =====================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"**Mes actual · {mes_actual_txt}**")
    st.metric("Total acumulado (€)", f"{total_actual:,.2f}")
    st.metric("Días con venta", dias_actual)
    st.metric("Promedio diario (€)", f"{prom_actual:,.2f}")

with c2:
    st.markdown(f"**Mes anterior · {mes_anterior_txt}**")
    st.metric("Total mes (€)", f"{total_ant:,.2f}")
    st.metric("Días con venta", dias_ant)
    st.metric("Promedio diario (€)", f"{prom_ant:,.2f}")

with c3:
    st.markdown(f"**Diferencia vs mes anterior**")
    st.caption(comparativa_txt)
    st.metric("€ vs mes anterior", f"{dif_total:,.2f}")
    st.metric("Diferencia días", f"{dif_dias:+d}")
    st.metric("Variación promedio", f"{dif_prom_pct:+.1f}%")
