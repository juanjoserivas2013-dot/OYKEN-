import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# IDENTIDAD DE LA PÁGINA
# =========================

st.title("OYKEN · Totalidades")
st.caption("Ventas mensuales consolidadas")

# =========================
# CARGA DEL CSV
# =========================

CSV_FILE = Path("ventas_mensuales.csv")

if not CSV_FILE.exists():
    st.warning("No existe el archivo de ventas mensuales generado desde Control Operativo.")
    st.stop()

tabla_meses = pd.read_csv(CSV_FILE)

# 👈 CLAVE ABSOLUTA
tabla_meses["Mes"] = tabla_meses["Mes"].astype(str).str.strip()

# =========================
# FILTRO POR MES
# =========================

if mes_sel != "Todos":
    tabla_filtrada = tabla_meses[tabla_meses["Mes"] == mes_sel]
else:
    tabla_filtrada = tabla_meses.copy()

# =========================
# VISUALIZACIÓN
# =========================

st.divider()
st.subheader("Ventas mensuales")

st.dataframe(
    tabla_filtrada,
    hide_index=True,
    use_container_width=True
)
