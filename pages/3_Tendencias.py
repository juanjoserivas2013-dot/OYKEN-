import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# CABECERA
# =========================
st.title("OIKEN · Tendencias")
st.caption("Estructura, estabilidad y robustez del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

if len(df) < 14:
    st.warning("Se necesitan al menos 14 días de datos para Tendencias.")
    st.stop()

# =========================
# VARIABLES BASE
# =========================
df["tickets_total"] = (
    df["tickets_manana"] +
    df["tickets_tarde"] +
    df["tickets_noche"]
)

df["ticket_medio"] = np.where(
    df["tickets_total"] > 0,
    df["ventas_total_eur"] / df["tickets_total"],
    np.nan
)

# Ventana dinámica desde HOY hacia atrás
df_30 = df.tail(30)

# =========================
# 1. DIRECCIÓN DEL NEGOCIO
# =========================
df_30["mm7"] = df_30["ventas_total_eur"].rolling(7).mean()
mm7_actual = df_30["mm7"].iloc[-1]
mm7_prev = df_30["mm7"].iloc[-8] if len(df_30) >= 14 else np.nan
mm7_var = ((mm7_actual - mm7_prev) / mm7_prev * 100) if mm7_prev > 0 else 0

st.subheader("Dirección del negocio")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Media móvil 7 días",
        f"{mm7_actual:,.0f} €",
        f"{mm7_var:+.1f} %"
    )

# =========================
# 2. CONSISTENCIA DEL RESULTADO
# =========================
cv_ventas = df_30["ventas_total_eur"].std() / df_30["ventas_total_eur"].mean()

with c2:
    st.metric(
        "Consistencia del resultado",
        f"{(1 - cv_ventas)*100:.1f} %",
        "Inestable" if cv_ventas > 0.30 else "Estable"
    )

# =========================
# 3. DEPENDENCIA DE PICOS
# =========================
media = df_30["ventas_total_eur"].mean()
desv = df_30["ventas_total_eur"].std()

picos = df_30[df_30["ventas_total_eur"] > media + 2 * desv]
pct_picos = (
    picos["ventas_total_eur"].sum()
    / df_30["ventas_total_eur"].sum()
    * 100
)

with c3:
    st.metric(
        "Dependencia de picos",
        f"{pct_picos:.1f} %",
        "Dependiente" if pct_picos > 35 else "Controlada"
    )

st.divider()

# =========================
# 4. ESTABILIDAD DEL TICKET MEDIO
# =========================
cv_ticket = df_30["ticket_medio"].std() / df_30["ticket_medio"].mean()

c4, c5 = st.columns(2)

with c4:
    st.subheader("Estabilidad del ticket medio")
    st.metric(
        "CV Ticket medio",
        f"{cv_ticket*100:.1f} %",
        "Inestable" if cv_ticket > 0.25 else "Estable"
    )

# =========================
# 5. VOLATILIDAD POR TURNOS (TABLA)
# =========================
def cv_turno(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm) / np.nanmean(tm)

tabla_turnos = pd.DataFrame({
    "Turno": ["Mañana", "Tarde", "Noche"],
    "CV Ticket (%)": [
        round(cv_turno(df_30["ventas_manana_eur"], df_30["tickets_manana"]) * 100, 1),
        round(cv_turno(df_30["ventas_tarde_eur"], df_30["tickets_tarde"]) * 100, 1),
        round(cv_turno(df_30["ventas_noche_eur"], df_30["tickets_noche"]) * 100, 1)
    ]
})

with c5:
    st.subheader("Volatilidad por turno")
    st.table(tabla_turnos)

st.divider()

# =========================
# 6. SEÑALES DE CALIDAD OPERATIVA
# =========================
st.subheader("Señales de calidad operativa")

if cv_ticket > 0.25:
    st.write("⚠️ Ticket medio inestable")
else:
    st.write("🟢 Ticket medio estable")

if cv_ventas > 0.30:
    st.write("⚠️ Ventas inconsistentes")
else:
    st.write("🟢 Ventas consistentes")

if pct_picos > 35:
    st.write("⚠️ Dependencia elevada de picos")
else:
    st.write("🟢 Dependencia de picos baja")

if tabla_turnos.loc[tabla_turnos["Turno"] == "Noche", "CV Ticket (%)"].values[0] > 30:
    st.write("⚠️ Turno noche volátil")
else:
    st.write("🟢 Turno noche bajo control")

# =========================
# NOTA DE SISTEMA
# =========================
st.caption(
    "Este bloque evalúa estabilidad y robustez. "
    "No interpreta causas ni propone acciones."
)
