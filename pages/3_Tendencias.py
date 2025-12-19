import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# =========================
# CONFIG
# =========================
st.title("📊 OIKEN · Tendencias")
st.caption("Radar de dirección, consistencia y estructura del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.warning("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

if df.empty:
    st.stop()

# =========================
# PREPARACIÓN BASE
# =========================
df["week"] = df["fecha"].dt.isocalendar().week
df["year"] = df["fecha"].dt.isocalendar().year
df["dow"] = df["fecha"].dt.weekday  # 0=lunes
df["ventas"] = df["ventas_total_eur"]

# Semana actual
hoy = pd.to_datetime(date.today())
week_actual = hoy.isocalendar().week
year_actual = hoy.isocalendar().year

df_semana = df[
    (df["week"] == week_actual) &
    (df["year"] == year_actual)
]

# =========================
# BLOQUE 1 · DIRECCIÓN
# =========================
st.subheader("Dirección del negocio")

df_mm = df.copy()
df_mm["mm7"] = df_mm["ventas"].rolling(7).mean()

mm_actual = df_mm["mm7"].iloc[-1]
mm_prev = df_mm["mm7"].iloc[-8] if len(df_mm) >= 8 else mm_actual
var_mm = ((mm_actual - mm_prev) / mm_prev * 100) if mm_prev > 0 else 0

c1, c2 = st.columns([2, 1])
with c1:
    st.metric(
        "Media móvil 7 días",
        f"{mm_actual:,.0f} €",
        f"{var_mm:+.1f} %"
    )

with c2:
    st.line_chart(df_mm.set_index("fecha")["mm7"].tail(21))

# =========================
# BLOQUE 2 · CONSISTENCIA
# =========================
st.divider()
st.subheader("Consistencia del resultado")

ventas_semanales = (
    df.groupby(["year", "week"])["ventas"]
    .sum()
    .tail(6)
)

coef_var = ventas_semanales.std() / ventas_semanales.mean() * 100 if ventas_semanales.mean() > 0 else 0

st.metric(
    "Coeficiente de variación semanal",
    f"{coef_var:.0f} %",
    help="Variabilidad del resultado entre semanas"
)

# =========================
# BLOQUE 3 · RITMO SEMANAL
# =========================
st.divider()
st.subheader("Ritmo semanal (peso por día)")

dow_map = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

peso_dow = (
    df_semana.groupby("dow")["ventas"]
    .sum()
    / df_semana["ventas"].sum() * 100
)

peso_dow = peso_dow.reindex(range(7), fill_value=0)
peso_dow.index = peso_dow.index.map(dow_map)

st.bar_chart(peso_dow)

# =========================
# BLOQUE 4 · DÍAS FUERTES / DÉBILES (DINÁMICO)
# =========================
st.divider()
st.subheader("Días fuertes y débiles")

dia_fuerte = peso_dow.idxmax()
dia_debil = peso_dow.idxmin()

c1, c2 = st.columns(2)
with c1:
    st.metric("Día fuerte actual", dia_fuerte, f"{peso_dow.max():.1f} %")

with c2:
    st.metric("Día débil actual", dia_debil, f"{peso_dow.min():.1f} %")

# =========================
# BLOQUE 5 · CALIDAD DEL INGRESO
# =========================
st.divider()
st.subheader("Calidad del ingreso (comportamiento)")

df["tickets_totales"] = (
    df["tickets_manana"] +
    df["tickets_tarde"] +
    df["tickets_noche"]
)

df["comensales_totales"] = (
    df["comensales_manana"] +
    df["comensales_tarde"] +
    df["comensales_noche"]
)

ratio_tc = (
    df["tickets_totales"] / df["comensales_totales"]
).replace([float("inf"), -float("inf")], 0)

ratio_actual = ratio_tc.iloc[-1]
ratio_prev = ratio_tc.iloc[-8] if len(ratio_tc) >= 8 else ratio_actual
var_ratio = ratio_actual - ratio_prev

st.metric(
    "Tickets por comensal (tendencia)",
    f"{ratio_actual:.2f}",
    f"{var_ratio:+.2f}"
)

# =========================
# BLOQUE 6 · ALERTAS MINIMAS
# =========================
st.divider()
st.subheader("Alertas")

alertas = []

if coef_var > 20:
    alertas.append("⚠️ Alta variabilidad semanal")

if peso_dow.max() > 30:
    alertas.append("⚠️ Alta dependencia de un solo día")

if var_ratio < -0.04:
    alertas.append("⚠️ Aumento del consumo compartido")

if alertas:
    for a in alertas:
        st.write(a)
else:
    st.write("Sin alertas relevantes")
