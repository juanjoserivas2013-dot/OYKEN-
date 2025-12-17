import streamlit as st

st.set_page_config(page_title="OYKEN · Comportamiento", layout="centered")

st.title("OYKEN · Comportamiento")
st.caption("Cómo se comporta el cliente")

st.divider()

st.subheader("ESTADÍSTICAS DE COMPORTAMIENTO")
st.markdown("_Primer bloque nuevo recomendable_")

st.markdown("""
Estas explican **cómo se comporta el cliente**:

- **Tickets / comensal** (ratio de conversión)
- **€ / comensal**
- **% de ventas por turno**
- **Peso de cada turno sobre el total**
""")

st.info("Aquí empiezas a ver **patrones**, no solo cifras.")
