import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================

st.title("OYKEN · Comportamiento del cliente")
st.caption("Cómo compra el cliente · Semana en curso")

DATA_FILE = Path("ventas.csv")

DOW_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

# =========================
# CARGA DE DATOS
# =========================
if not DATA_FILE.exists():
    st.warning("No hay datos suficientes.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
df = df.sort_values("fecha")

# =========================
# PREPARACIÓN TEMPORAL
# =========================
df["weekday"] = df["fecha"].dt.weekday
df["dow"] = df["weekday"].map(DOW_ES)

df["week"] = df["fecha"].dt.isocalendar().week
df["year"] = df["fecha"].dt.isocalendar().year

hoy = pd.to_datetime(date.today())
week_actual = hoy.isocalendar().week
year_actual = hoy.isocalendar().year
dow_hoy = hoy.weekday()

# =========================
# FILTROS DE PERIODO
# =========================
df_semana = df[
    (df["week"] == week_actual) &
    (df["year"] == year_actual)
]

df_patron = df[
    (df["weekday"] == dow_hoy) &
    (df["fecha"] < hoy)
]

if df_semana.empty:
    st.info("Aún no hay datos en la semana actual.")
    st.stop()

# =========================
# AGREGADOS SEMANA
# =========================
ventas_total = df_semana["ventas_total_eur"].sum()
comensales_total = (
    df_semana["comensales_manana"].sum() +
    df_semana["comensales_tarde"].sum() +
    df_semana["comensales_noche"].sum()
)

tickets_total = (
    df_semana["tickets_manana"].sum() +
    df_semana["tickets_tarde"].sum() +
    df_semana["tickets_noche"].sum()
)

# Métricas comportamiento
tickets_por_comensal = tickets_total / comensales_total if comensales_total > 0 else 0
eur_por_comensal = ventas_total / comensales_total if comensales_total > 0 else 0

# =========================
# PESO POR TURNO
# =========================
def peso_turno(col):
    return df_semana[col].sum() / ventas_total * 100 if ventas_total > 0 else 0

peso_manana = peso_turno("ventas_manana_eur")
peso_tarde = peso_turno("ventas_tarde_eur")
peso_noche = peso_turno("ventas_noche_eur")

# =========================
# CABECERA
# =========================
st.markdown("### Semana en curso")
st.caption(
    f"{df_semana['fecha'].min().strftime('%d/%m/%Y')} "
    f"→ {df_semana['fecha'].max().strftime('%d/%m/%Y')}"
)

# =========================
# BLOQUE A · KPIs COMPORTAMIENTO
# =========================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Tickets / comensal",
        f"{tickets_por_comensal:.2f}"
    )

with c2:
    st.metric(
        "€ / comensal",
        f"{eur_por_comensal:,.2f} €"
    )

with c3:
    st.metric(
        "% Mañana",
        f"{peso_manana:.1f} %"
    )

with c4:
    st.metric(
        "% Tarde",
        f"{peso_tarde:.1f} %"
    )

# =========================
# BLOQUE B · POR TURNO
# =========================
st.divider()
st.subheader("Comportamiento por turno")

def bloque_turno(nombre, v_col, c_col, t_col):
    ventas = df_semana[v_col].sum()
    com = df_semana[c_col].sum()
    tic = df_semana[t_col].sum()

    st.markdown(f"**{nombre}**")
    st.write(f"€ / comensal: {(ventas / com) if com > 0 else 0:,.2f} €")
    st.write(f"Tickets / comensal: {(tic / com) if com > 0 else 0:.2f}")
    st.write(f"Peso sobre total: {(ventas / ventas_total * 100) if ventas_total > 0 else 0:.1f} %")

c1, c2, c3 = st.columns(3)

with c1:
    bloque_turno(
        "Mañana",
        "ventas_manana_eur",
        "comensales_manana",
        "tickets_manana"
    )

with c2:
    bloque_turno(
        "Tarde",
        "ventas_tarde_eur",
        "comensales_tarde",
        "tickets_tarde"
    )

with c3:
    bloque_turno(
        "Noche",
        "ventas_noche_eur",
        "comensales_noche",
        "tickets_noche"
    )

# =========================
# BLOQUE C · LECTURA OYKEN
# =========================
st.divider()
st.subheader("Lectura de comportamiento")

lectura = []

if peso_tarde > peso_manana and peso_tarde > peso_noche:
    lectura.append("• La **tarde es el motor principal** de la semana.")

if eur_por_comensal > 0:
    lectura.append("• El valor medio por cliente es estable.")

if tickets_por_comensal > 1.3:
    lectura.append("• Buen nivel de conversión por cliente.")

if not lectura:
    lectura.append("• Sin patrones claros todavía.")

for l in lectura:
    st.write(l)

st.caption("Este bloque describe comportamiento. No anticipa ni recomienda.")
