import streamlit as st
import pandas as pd
from pathlib import Path

# =========================
# IDENTIDAD DE LA PÁGINA
# =========================

st.title("OYKEN · Totalidades")
st.caption("Ventas mensuales consolidadas")

# =========================
# CARGA DEL CSV DESDE CONTROL OPERATIVO
# =========================

CSV_FILE = Path("ventas_mensuales.csv")

if not CSV_FILE.exists():
    st.warning("No existe el archivo de ventas mensuales generado desde Control Operativo.")
    st.stop()

tabla_meses = pd.read_csv(CSV_FILE)

# =========================
# VISUALIZACIÓN
# =========================

st.divider()
st.subheader("Ventas mensuales")

st.dataframe(
    tabla_meses,
    hide_index=True,
    use_container_width=True
)
