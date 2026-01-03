import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================
st.title("OYKEN · EBITDA")
st.caption("Lectura consolidada de rentabilidad operativa")
st.divider()

# =========================
# ARCHIVOS
# =========================
VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
GASTOS_FILE = Path("gastos.csv")
RRHH_FILE = Path("rrhh_puestos.csv")

# =========================
# MAPA MESES ESPAÑOL
# =========================
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# =========================
# CARGA DE DATOS
# =========================

# Ventas
df_ventas = pd.read_csv(VENTAS_FILE, parse_dates=["fecha"]) if VENTAS_FILE.exists() else pd.DataFrame()
df_ventas["ventas_total_eur"] = pd.to_numeric(df_ventas.get("ventas_total_eur"), errors="coerce").fillna(0)

# Compras
df_compras = pd.read_csv(COMPRAS_FILE) if COMPRAS_FILE.exists() else pd.DataFrame()
df_compras["Fecha"] = pd.to_datetime(df_compras.get("Fecha"), dayfirst=True, errors="coerce")
df_compras["Coste (€)"] = pd.to_numeric(df_compras.get("Coste (€)"), errors="coerce").fillna(0)

# Gastos
df_gastos = pd.read_csv(GASTOS_FILE) if GASTOS_FILE.exists() else pd.DataFrame()
df_gastos["Fecha"] = pd.to_datetime(df_gastos.get("Fecha"), dayfirst=True, errors="coerce")
df_gastos["Coste (€)"] = pd.to_numeric(df_gastos.get("Coste (€)"), errors="coerce").fillna(0)

# RRHH (coste empresa)
df_rrhh = pd.read_csv(RRHH_FILE) if RRHH_FILE.exists() else pd.DataFrame()

# =========================
# SELECTORES TEMPORALES
# =========================
st.subheader("Periodo de análisis")

c1, c2 = st.columns(2)

with c1:
    anios_disponibles = sorted(
        set(df_ventas["fecha"].dt.year.dropna().unique())
    )
    anio_sel = st.selectbox(
        "Año",
        anios_disponibles,
        index=len(anios_disponibles) - 1,
        key="anio_ebitda"
    )

with c2:
    mes_sel = st.selectbox(
        "Mes",
        options=[0] + list(MESES_ES.keys()),
        format_func=lambda x: "Todos los meses" if x == 0 else MESES_ES[x],
        key="mes_ebitda"
    )

# =========================
# FILTRADO
# =========================

# Ventas
df_v = df_ventas[df_ventas["fecha"].dt.year == anio_sel]
if mes_sel != 0:
    df_v = df_v[df_v["fecha"].dt.month == mes_sel]
ventas_total = df_v["ventas_total_eur"].sum()

# Compras
df_c = df_compras[df_compras["Fecha"].dt.year == anio_sel]
if mes_sel != 0:
    df_c = df_c[df_c["Fecha"].dt.month == mes_sel]
compras_total = df_c["Coste (€)"].sum()

# Gastos
df_g = df_gastos[df_gastos["Fecha"].dt.year == anio_sel]
if mes_sel != 0:
    df_g = df_g[df_g["Fecha"].dt.month == mes_sel]
gastos_total = df_g["Coste (€)"].sum()

# RRHH (por ahora anual completo)
coste_rrhh = 0
if not df_rrhh.empty:
    df_rrhh_anio = df_rrhh[df_rrhh["Año"] == anio_sel]
    for col in df_rrhh_anio.columns:
        if "Coste Empresa" in col:
            coste_rrhh += pd.to_numeric(df_rrhh_anio[col], errors="coerce").sum()

# =========================
# EBITDA
# =========================
ebitda = ventas_total - compras_total - gastos_total - coste_rrhh

# =========================
# TABLA RESUMEN
# =========================
st.subheader("Resumen EBITDA")

tabla = pd.DataFrame([{
    "Ventas (€)": round(ventas_total, 2),
    "Compras (€)": round(compras_total, 2),
    "Gastos (€)": round(gastos_total, 2),
    "RRHH (€)": round(coste_rrhh, 2),
    "EBITDA (€)": round(ebitda, 2)
}])

st.dataframe(tabla, hide_index=True, use_container_width=True)

# =========================
# MÉTRICAS CLAVE
# =========================
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.metric("EBITDA (€)", f"{ebitda:,.2f} €")

with c2:
    margen = (ebitda / ventas_total * 100) if ventas_total > 0 else 0
    st.metric("Margen EBITDA (%)", f"{margen:.1f} %")
