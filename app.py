import streamlit as st
import pandas as pd
from datetime import date
import os

# -----------------------------
# Configuración básica
# -----------------------------
st.set_page_config(
    page_title="OYKEN · Ventas",
    page_icon="📊",
    layout="centered"
)

DATA_FILE = "ventas.csv"

# -----------------------------
# Diccionario días en español
# (NO usar locale del sistema)
# -----------------------------
DAYS_ES = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

# -----------------------------
# Funciones de datos
# -----------------------------
def cargar_datos():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
    else:
        df = pd.DataFrame(columns=["fecha", "ventas"])

    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["dia_semana"] = df["fecha"].dt.day_name().map(DAYS_ES)
        df["año"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month
        df["semana"] = df["fecha"].dt.isocalendar().week

    return df


def guardar_venta(fecha, ventas):
    nueva_fila = pd.DataFrame([{
        "fecha": fecha,
        "ventas": ventas
    }])

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["fecha"])
        df = pd.concat([df, nueva_fila], ignore_index=True)
    else:
        df = nueva_fila

    df.to_csv(DATA_FILE, index=False)


# -----------------------------
# UI — CABECERA
# -----------------------------
st.title("OYKEN · Ventas")
st.caption("Prototipo inicial (privado)")

# -----------------------------
# UI — FORMULARIO DE ENTRADA
# -----------------------------
with st.form("form_ventas"):
    fecha = st.date_input(
        "Fecha",
        value=date.today(),
        format="YYYY/MM/DD"
    )

    ventas = st.number_input(
        "Ventas (€)",
        min_value=0.0,
        step=10.0,
        format="%.2f"
    )

    submitted = st.form_submit_button("Guardar")

    if submitted:
        guardar_venta(fecha, ventas)
        st.success("Venta guardada correctamente")

# -----------------------------
# CARGA DE DATOS
# -----------------------------
df = cargar_datos()

# -----------------------------
# UI — LISTADO Y FILTROS
# -----------------------------
st.divider()
st.subheader("Histórico de ventas")

if df.empty:
    st.info("Aún no hay ventas registradas.")
else:
    # Filtros
    col1, col2 = st.columns(2)

    with col1:
        fecha_desde = st.date_input(
            "Desde",
            value=df["fecha"].min().date()
        )

    with col2:
        fecha_hasta = st.date_input(
            "Hasta",
            value=df["fecha"].max().date()
        )

    df_filtrado = df[
        (df["fecha"] >= pd.to_datetime(fecha_desde)) &
        (df["fecha"] <= pd.to_datetime(fecha_hasta))
    ].copy()

    # Recalcular día en español por seguridad
    df_filtrado["dia_semana"] = (
        df_filtrado["fecha"]
        .dt.day_name()
        .map(DAYS_ES)
    )

    df_filtrado = df_filtrado.sort_values("fecha", ascending=False)

    st.dataframe(
        df_filtrado[[
            "fecha",
            "dia_semana",
            "ventas"
        ]],
        use_container_width=True
    )

    st.metric(
        "Total periodo (€)",
        f"{df_filtrado['ventas'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
