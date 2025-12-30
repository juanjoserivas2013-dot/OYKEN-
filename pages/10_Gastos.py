import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CABECERA
# =====================================================
st.subheader("OYKEN · Gastos")
st.markdown("**Registro de gastos operativos no ligados a compras de producto.**")
st.caption("Aquí se captura la estructura fija y variable del negocio.")

# =====================================================
# ARCHIVO DE DATOS
# =====================================================
DATA_FILE = Path("gastos.csv")

# =====================================================
# ESTADO
# =====================================================
if "gastos" not in st.session_state:
    if DATA_FILE.exists():
        st.session_state.gastos = pd.read_csv(DATA_FILE)
    else:
        st.session_state.gastos = pd.DataFrame(
            columns=["Fecha", "Mes", "Concepto", "Categoria", "Coste (€)"]
        )

# =====================================================
# CATEGORÍAS BASE OYKEN
# =====================================================
CATEGORIAS = [
    "Alquiler",
    "Suministros",
    "Mantenimiento",
    "Servicios profesionales",
    "Bancos y Medios de pago",
    "Tecnología y Plataformas",
    "Marqueting y Comunicación",
    "Limpieza y Lavandería",
    "Uniformes y utensilios",
    "Vigilancia y Seguridad",
    "otros Gastos operativos"
    
]

# =====================================================
# FORMULARIO
# =====================================================
with st.form("registro_gastos", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        fecha = st.date_input(
            "Fecha",
            value=date.today(),
            format="DD/MM/YYYY"
        )

    with col2:
        categoria = st.selectbox("Categoría", CATEGORIAS)

    concepto = st.text_input(
        "Concepto / Descripción",
        placeholder="Ej: Alquiler local, gestoría, electricidad..."
    )

    coste = st.number_input(
        "Coste (€)",
        min_value=0.00,
        step=0.01,
        format="%.2f"
    )

    submitted = st.form_submit_button("Registrar gasto")

    if submitted:

        if not concepto:
            st.warning("Debes introducir un concepto.")
            st.stop()

        if coste <= 0:
            st.warning("El coste debe ser mayor que cero.")
            st.stop()

        nuevo = {
            "Fecha": fecha.strftime("%d/%m/%Y"),
            "Mes": fecha.strftime("%Y-%m"),
            "Concepto": concepto,
            "Categoria": categoria,
            "Coste (€)": round(coste, 2)
        }

        st.session_state.gastos = pd.concat(
            [st.session_state.gastos, pd.DataFrame([nuevo])],
            ignore_index=True
        )

        st.session_state.gastos.to_csv(DATA_FILE, index=False)
        st.success("Gasto registrado correctamente.")

# =====================================================
# VISUALIZACIÓN
# =====================================================
st.divider()

if st.session_state.gastos.empty:
    st.info("No hay gastos registrados todavía.")
else:
    st.dataframe(
        st.session_state.gastos,
        hide_index=True,
        use_container_width=True
    )

    total = st.session_state.gastos["Coste (€)"].sum()
    st.markdown(f"### Total acumulado: **{total:.2f} €**")

# =====================================================
# ELIMINAR REGISTRO
# =====================================================
st.subheader("Eliminar gasto")

idx = st.selectbox(
    "Selecciona un registro",
    st.session_state.gastos.index,
    format_func=lambda i: (
        f'{st.session_state.gastos.loc[i,"Fecha"]} | '
        f'{st.session_state.gastos.loc[i,"Concepto"]} | '
        f'{st.session_state.gastos.loc[i,"Coste (€)"]:.2f} €'
    )
)

if st.button("Eliminar gasto"):
    st.session_state.gastos = (
        st.session_state.gastos
        .drop(idx)
        .reset_index(drop=True)
    )
    st.session_state.gastos.to_csv(DATA_FILE, index=False)
    st.success("Gasto eliminado correctamente.")
    
# ===============================
# BASE CUENTA DE RESULTADOS
# Resumen mensual de gastos
# ===============================
st.markdown("---")
st.subheader("Base Cuenta de Resultados — Gastos mensuales")

# Aseguramos fecha en formato datetime
df_gastos["fecha"] = pd.to_datetime(df_gastos["fecha"])

# Selector de año (solo con años existentes)
años_disponibles = sorted(df_gastos["fecha"].dt.year.unique())
año_base = st.selectbox(
    "Año base para Cuenta de Resultados (Gastos)",
    años_disponibles,
    index=len(años_disponibles) - 1
)

# Diccionario de meses legibles
MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Filtrado por año
df_año = df_gastos[df_gastos["fecha"].dt.year == año_base]

# Construcción del resumen mensual
resumen = []

for mes_num in range(1, 13):
    total_mes = df_año[df_año["fecha"].dt.month == mes_num]["coste"].sum()

    resumen.append({
        "Mes": MESES[mes_num],
        "Gastos (€)": round(total_mes, 2)
    })

df_base_gastos = pd.DataFrame(resumen)

# Mostrar tabla
st.dataframe(df_base_gastos, use_container_width=True)

# Total anual
total_anual = df_base_gastos["Gastos (€)"].sum()

st.markdown(
    f"### Total anual de gastos\n**{total_anual:,.2f} €**"
)
