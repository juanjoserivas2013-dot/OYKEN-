import streamlit as st
import pandas as pd

st.set_page_config(page_title="OYKEN - Ventas", layout="centered")

st.title("OYKEN · Ventas")

st.write("Prototipo inicial (privado)")

with st.form("ventas"):
    fecha = st.date_input("Fecha")
    ventas = st.number_input("Ventas (€)", min_value=0.0)
    guardar = st.form_submit_button("Guardar")

if guardar:
    st.success("Venta guardada (demo)")
