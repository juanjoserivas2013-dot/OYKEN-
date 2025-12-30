import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="OYKEN · RRHH",
    layout="centered"
)

st.title("OYKEN · RRHH")
st.caption("Gestión estructural de costes de personal")

# =====================================================
# CONSTANTES
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

SS_EMPRESA = 0.33
EXPORT_FILE = Path("rrhh_coste_mensual.csv")

# =====================================================
# ESTADO BASE (estructura de puestos)
# =====================================================

if "puestos" not in st.session_state:
    st.session_state.puestos = []

# =====================================================
# BLOQUE 1 · ALTA DE PUESTOS
# =====================================================

st.subheader("Alta de puestos")

with st.form("alta_puesto", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input(
        "Salario bruto anual (€)",
        min_value=0.0,
        step=1000.0,
        format="%.2f"
    )

    st.markdown("**Necesidad mensual (personas)**")
    cols = st.columns(6)
    necesidad = {}

    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            necesidad[mes] = st.number_input(
                mes,
                min_value=0,
                step=1,
                key=f"need_{mes}"
            )

    guardar = st.form_submit_button("Guardar puesto")

    if guardar and puesto.strip():
        st.session_state.puestos.append({
            "Puesto": puesto.strip(),
            "Bruto anual (€)": float(bruto_anual),
            **necesidad
        })

# =====================================================
# TABLA · ESTRUCTURA DE PUESTOS
# =====================================================

if st.session_state.puestos:
    df_puestos = pd.DataFrame(st.session_state.puestos)
    st.subheader("Estructura de puestos")
    st.dataframe(df_puestos, hide_index=True, use_container_width=True)
else:
    st.info("Aún no hay puestos definidos.")

st.divider()

# =====================================================
# BLOQUE 2 · COSTE DE PERSONAL (NÓMINA)
# =====================================================

st.subheader("Coste de personal — Nómina")

nominas = []

for _, row in df_puestos.iterrows():
    salario_mensual = row["Bruto anual (€)"] / 12
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        fila[mes] = round(salario_mensual * row[mes], 2)

    nominas.append(fila)

df_nominas = pd.DataFrame(nominas)
st.dataframe(df_nominas, hide_index=True, use_container_width=True)

st.divider()

# =====================================================
# BLOQUE 3 · SEGURIDAD SOCIAL Y COSTE EMPRESA
# =====================================================

st.subheader("Seguridad Social y coste empresarial")
aplicar_ss = st.checkbox("Aplicar Seguridad Social Empresa (33%)", value=True)

costes = []

for _, row in df_nominas.iterrows():
    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss = nomina * SS_EMPRESA if aplicar_ss else 0.0
        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS"] = round(ss, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss, 2)

    costes.append(fila)

df_costes = pd.DataFrame(costes)
st.dataframe(df_costes, hide_index=True, use_container_width=True)

st.divider()

# =====================================================
# BLOQUE 4 · TOTALES MENSUALES RRHH
# =====================================================

st.subheader("Totales mensuales RRHH")

totales = []

for mes in MESES:
    nomina = df_costes[f"{mes} · Nómina"].sum()
    ss = df_costes[f"{mes} · SS"].sum()
    coste = df_costes[f"{mes} · Coste Empresa"].sum()

    totales.append({
        "Mes": mes,
        "Nómina (€)": round(nomina, 2),
        "Seguridad Social (€)": round(ss, 2),
        "Coste Empresa (€)": round(coste, 2)
    })

df_totales = pd.DataFrame(totales)
st.dataframe(df_totales, hide_index=True, use_container_width=True)

st.divider()

# =====================================================
# BLOQUE 5 · PERSISTENCIA
# =====================================================

st.subheader("Guardar coste RRHH mensual")

anio = st.selectbox("Año de referencia", list(range(2022, 2031)), index=3)

df_export = df_totales.copy()
df_export.insert(0, "Año", anio)

df_export.to_csv(EXPORT_FILE, index=False)

st.success("Coste de RRHH mensual guardado correctamente")
st.caption("Este coste se integra directamente en la Cuenta de Resultados.")
