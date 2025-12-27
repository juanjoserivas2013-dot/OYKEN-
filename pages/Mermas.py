import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =========================
# CONFIGURACIÓN
# =========================

st.title("OYKEN · Mermas")
st.markdown("**Registro operativo de pérdidas de producto**")
st.caption("Fase 1 · Control por cantidad. Sin valoración económica.")

DATA_FILE = Path("mermas.csv")

# =========================
# CARGA / ESTADO
# =========================
if DATA_FILE.exists():
    df_mermas = pd.read_csv(DATA_FILE)
else:
    df_mermas = pd.DataFrame(
        columns=[
            "Fecha",
            "Mes",
            "Familia",
            "Producto",
            "Unidad",
            "Cantidad",
            "Motivo"
        ]
    )

# =========================
# CATÁLOGOS
# =========================
FAMILIAS = ["Matería Prima", "Bebidas", "Limpieza", "Otros"]

UNIDADES = ["kg", "uds", "l"]

MOTIVOS = [
    "Caducidad",
    "Sobreproducción",
    "Error de elaboración",
    "Error de pedido",
    "Deterioro",
    "Rotura",
    "Ajuste inventario",
    "Otro"
]

# =========================
# REGISTRO DE MERMA
# =========================
st.subheader("Registrar merma")

with st.form("form_mermas", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            format="DD/MM/YYYY"
        )

    with col2:
        familia = st.selectbox("Familia", FAMILIAS)

    producto = st.text_input(
        "Producto / referencia",
        placeholder="Ej. Patata agria, Merluza fresca, Pan…"
    )

    col3, col4 = st.columns(2)

    with col3:
        unidad = st.selectbox("Unidad", UNIDADES)

    with col4:
        cantidad = st.number_input(
            "Cantidad",
            min_value=0.0,
            step=0.1
        )

    motivo = st.selectbox("Motivo de la merma", MOTIVOS)

    guardar = st.form_submit_button("Registrar merma")

    if guardar:

        if not producto.strip():
            st.warning("Debes indicar el producto.")
            st.stop()

        if cantidad <= 0:
            st.warning("La cantidad debe ser mayor que cero.")
            st.stop()

        nueva = {
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Mes": fecha.strftime("%Y-%m"),
            "Familia": familia,
            "Producto": producto.strip(),
            "Unidad": unidad,
            "Cantidad": round(cantidad, 2),
            "Motivo": motivo
        }

        df_mermas = pd.concat(
            [df_mermas, pd.DataFrame([nueva])],
            ignore_index=True
        )

        df_mermas.to_csv(DATA_FILE, index=False)
        st.success("Merma registrada correctamente.")

# =========================
# VISUALIZACIÓN
# =========================
st.divider()
st.subheader("Mermas registradas")

if df_mermas.empty:
    st.info("No hay mermas registradas.")
else:
    # Selector de mes
    meses = sorted(df_mermas["Mes"].unique(), reverse=True)
    mes_sel = st.selectbox("Selecciona mes", meses)

    df_mes = df_mermas[df_mermas["Mes"] == mes_sel]

    st.dataframe(
        df_mes[
            ["Fecha", "Producto", "Familia", "Motivo", "Cantidad", "Unidad"]
        ],
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # =========================
    # TOTALES (SIN €)
    # =========================
    st.subheader("Totales del mes")

    totales = (
        df_mes
        .groupby("Unidad")["Cantidad"]
        .sum()
        .reset_index()
    )

    for _, row in totales.iterrows():
        st.markdown(
            f"**Total {row['Unidad']} perdidos:** {row['Cantidad']:.2f}"
        )
