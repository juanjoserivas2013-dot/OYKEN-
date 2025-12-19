import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# CONFIG
# =========================
st.title("OIKEN · Tendencias")
st.caption("Calidad operativa · estabilidad · robustez del negocio")

DATA_FILE = Path("ventas.csv")

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.error("No hay datos suficientes para analizar tendencias.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

if len(df) < 7:
    st.warning("Se necesitan al menos 7 días de datos para Tendencias.")
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

# =========================
# PERIODO DE ANÁLISIS
# =========================
df_30 = df.tail(30)

# =========================
# MÉTRICAS DIAGNÓSTICAS
# =========================

# --- Media móvil 7 días ---
df_30["mm7"] = df_30["ventas_total_eur"].rolling(7).mean()
mm7_actual = df_30["mm7"].iloc[-1]
mm7_prev = df_30["mm7"].iloc[-8] if len(df_30) >= 14 else np.nan
mm7_var = ((mm7_actual - mm7_prev) / mm7_prev * 100) if mm7_prev > 0 else 0

# --- CV Ventas ---
cv_ventas = df_30["ventas_total_eur"].std() / df_30["ventas_total_eur"].mean()

# --- CV Ticket medio ---
cv_ticket = df_30["ticket_medio"].std() / df_30["ticket_medio"].mean()

# --- Volatilidad por turno ---
def cv_turno(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm) / np.nanmean(tm)

cv_m = cv_turno(df_30["ventas_manana_eur"], df_30["tickets_manana"])
cv_t = cv_turno(df_30["ventas_tarde_eur"], df_30["tickets_tarde"])
cv_n = cv_turno(df_30["ventas_noche_eur"], df_30["tickets_noche"])

# --- Dependencia de picos ---
media = df_30["ventas_total_eur"].mean()
desv = df_30["ventas_total_eur"].std()
picos = df_30[df_30["ventas_total_eur"] > media + 2 * desv]
pct_picos = picos["ventas_total_eur"].sum() / df_30["ventas_total_eur"].sum() * 100

# =========================
# VISUAL — FILA 1
# =========================
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Dirección del negocio",
        f"{mm7_actual:,.0f} €",
        f"{mm7_var:+.1f} %"
    )
    st.caption("Media móvil 7 días")

with c2:
    st.metric(
        "Consistencia del resultado",
        f"{cv_ventas*100:.1f} %",
        "Estable" if cv_ventas < 0.45 else "Inestable"
    )
    st.caption("Coeficiente de variación ventas")

with c3:
    st.metric(
        "Dependencia de picos",
        f"{pct_picos:.1f} %",
        "Orgánico" if pct_picos < 15 else "Dependiente"
    )

st.divider()

# =========================
# VISUAL — FILA 2
# =========================
c4, c5 = st.columns(2)

with c4:
    st.subheader("Estabilidad del ticket medio")
    st.metric(
        "CV Ticket medio",
        f"{cv_ticket*100:.1f} %",
        "Controlado" if cv_ticket < 0.2 else "Inestable"
    )

with c5:
    st.subheader("Volatilidad por turno")
    st.write(
        pd.DataFrame({
            "Turno": ["Mañana", "Tarde", "Noche"],
            "CV Ticket (%)": [
                round(cv_m*100, 1),
                round(cv_t*100, 1),
                round(cv_n*100, 1)
            ]
        }).set_index("Turno")
    )

st.divider()

# =========================
# VISUAL — FILA 3
# =========================
st.subheader("Señales de calidad operativa")

checks = [
    ("Ticket medio estable", cv_ticket < 0.2),
    ("Ventas consistentes", cv_ventas < 0.45),
    ("Dependencia de picos baja", pct_picos < 15),
    ("Turno noche bajo control", cv_n < 0.25)
]

for label, ok in checks:
    st.write(f"{'✅' if ok else '⚠️'} {label}")

