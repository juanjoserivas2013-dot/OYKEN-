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
# VENTANA SEMANAL ROLLING
# =========================
df_7 = df.tail(7)
df_15 = df.tail(15)
df_30 = df.tail(30)

if len(df_7) < 5:
    st.warning("Se necesitan al menos 5 días para calcular tendencias semanales.")
    st.stop()

# =========================
# 1. DIRECCIÓN DEL NEGOCIO
# =========================
df_7["mm7"] = df_7["ventas_total_eur"].mean()

if len(df) >= 14:
    prev_7 = df.iloc[-14:-7]["ventas_total_eur"].mean()
else:
    prev_7 = np.nan

mm7_actual = df_7["ventas_total_eur"].mean()
mm7_var = ((mm7_actual - prev_7) / prev_7 * 100) if prev_7 > 0 else 0

st.subheader("Dirección del negocio")
st.metric(
    "Media móvil 7 días",
    f"{mm7_actual:,.0f} €",
    f"{mm7_var:+.1f} %"
)

st.line_chart(
    df_30.set_index("fecha")[["ventas_total_eur"]],
    use_container_width=True
)

st.divider()

# =========================
# 2. CONSISTENCIA DEL RESULTADO
# =========================
cv_ventas = df_7["ventas_total_eur"].std() / df_7["ventas_total_eur"].mean()

st.subheader("Consistencia del resultado")
st.metric(
    "Coeficiente de variación semanal",
    f"{cv_ventas*100:.1f} %"
)

st.divider()

# =========================
# 3. DÍAS FUERTES Y DÉBILES
# (requiere patrón semanal → mínimo 15 días)
# =========================
st.subheader("Días fuertes y días débiles")

if len(df_15) < 15:
    st.info("Histórico insuficiente para identificar días fuertes y débiles.")
else:
    df_15["weekday"] = df_15["fecha"].dt.day_name()
    media_dia = df_15.groupby("weekday")["ventas_total_eur"].mean()
    media_global = df_15["ventas_total_eur"].mean()

    dia_fuerte = media_dia.idxmax()
    dia_debil = media_dia.idxmin()

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            "Día más fuerte",
            dia_fuerte,
            f"{(media_dia.max()/media_global - 1)*100:+.0f} %"
        )

    with c2:
        st.metric(
            "Día más débil",
            dia_debil,
            f"{(media_dia.min()/media_global - 1)*100:+.0f} %"
        )

st.divider()

# =========================
# 4. ESTABILIDAD DEL TICKET MEDIO
# =========================
cv_ticket = df_7["ticket_medio"].std() / df_7["ticket_medio"].mean()

st.subheader("Estabilidad del ticket medio")
st.metric(
    "Coeficiente de variación del ticket medio",
    f"{cv_ticket*100:.1f} %"
)

st.line_chart(
    df_30.set_index("fecha")[["ticket_medio"]],
    use_container_width=True
)

st.divider()

# =========================
# 5. VOLATILIDAD POR TURNOS (TABLA)
# =========================
def cv_turno(ventas, tickets):
    tm = np.where(tickets > 0, ventas / tickets, np.nan)
    return np.nanstd(tm) / np.nanmean(tm)

tabla_turnos = pd.DataFrame({
    "Turno": ["Mañana", "Tarde", "Noche"],
    "CV Ticket (%)": [
        round(cv_turno(df_7["ventas_manana_eur"], df_7["tickets_manana"]) * 100, 1),
        round(cv_turno(df_7["ventas_tarde_eur"], df_7["tickets_tarde"]) * 100, 1),
        round(cv_turno(df_7["ventas_noche_eur"], df_7["tickets_noche"]) * 100, 1)
    ]
})

st.subheader("Volatilidad por turnos")
st.table(tabla_turnos)

st.divider()

# =========================
# 6. DEPENDENCIA DE PICOS
# =========================
media = df_7["ventas_total_eur"].mean()
desv = df_7["ventas_total_eur"].std()

picos = df_7[df_7["ventas_total_eur"] > media + 2 * desv]
pct_picos = (
    picos["ventas_total_eur"].sum()
    / df_7["ventas_total_eur"].sum()
    * 100
) if df_7["ventas_total_eur"].sum() > 0 else 0

st.subheader("Dependencia de picos")
st.metric(
    "Ventas concentradas en días excepcionalmente altos",
    f"{pct_picos:.1f} %"
)

st.divider()

# =========================
# 7. SEÑALES DE CALIDAD OPERATIVA
# =========================
st.subheader("Señales de calidad operativa")

if cv_ticket > 0.25:
    st.write("⚠️ Variabilidad elevada en el ticket medio")
else:
    st.write("🟢 Ticket medio bajo control")

if pct_picos > 45:
    st.write("🔴 Alta dependencia de picos de venta")
elif pct_picos > 30:
    st.write("⚠️ Dependencia moderada de picos")
else:
    st.write("🟢 Dependencia de picos baja")

if tabla_turnos.loc[tabla_turnos["Turno"] == "Tarde", "CV Ticket (%)"].values[0] > 30:
    st.write("⚠️ Variabilidad elevada en turno tarde")
else:
    st.write("🟢 Turnos bajo control")

# =========================
# NOTA DE SISTEMA
# =========================
st.caption(
    "Este bloque describe tendencias y estabilidad. "
    "Las decisiones se priorizan en Calidad Operativa."
)
