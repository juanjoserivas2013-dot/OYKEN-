import streamlit as st
import pandas as pd

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="OYKEN · RRHH",
    layout="centered"
)

st.title("OYKEN · RRHH")
st.caption("Estructura salarial y costes de personal")

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# =========================
# FASE 1 — PERSONAL NECESARIO
# =========================
st.subheader("Fase 1 · Personal necesario")

if "rrhh_personal" not in st.session_state:
    st.session_state.rrhh_personal = pd.DataFrame(
        columns=["Puesto", "Bruto anual (€)"] + MESES
    )

with st.form("form_personal", clear_on_submit=True):

    puesto = st.text_input("Puesto")
    bruto_anual = st.number_input("Bruto anual (€)", min_value=0.0, step=500.0)

    cols = st.columns(6)
    necesidades = {}
    for i, mes in enumerate(MESES):
        with cols[i % 6]:
            necesidades[mes] = st.number_input(
                mes, min_value=0, step=1, key=f"n_{mes}"
            )

    submitted = st.form_submit_button("Añadir puesto")

    if submitted and puesto:
        fila = {"Puesto": puesto, "Bruto anual (€)": bruto_anual}
        fila.update(necesidades)

        st.session_state.rrhh_personal = pd.concat(
            [st.session_state.rrhh_personal, pd.DataFrame([fila])],
            ignore_index=True
        )

if not st.session_state.rrhh_personal.empty:
    st.dataframe(st.session_state.rrhh_personal, hide_index=True)

st.divider()

# =========================
# FASE 2 — COSTE DE PERSONAL
# =========================
st.subheader("Fase 2 · Coste de personal (nómina)")

if st.session_state.rrhh_personal.empty:
    st.info("Introduce personal para calcular el coste.")
    st.stop()

tabla_coste = []

for _, row in st.session_state.rrhh_personal.iterrows():
    bruto_mensual = row["Bruto anual (€)"] / 12

    fila = {"Puesto": row["Puesto"]}
    for mes in MESES:
        fila[mes] = round(bruto_mensual * row[mes], 2)

    tabla_coste.append(fila)

df_coste = pd.DataFrame(tabla_coste)
st.session_state.rrhh_coste_personal = df_coste

st.dataframe(df_coste, hide_index=True, use_container_width=True)

st.divider()

# =========================
# FASE 3 — SEGURIDAD SOCIAL
# =========================
st.subheader("Fase 3 · Seguridad Social y coste salarial")

aplicar_ss = st.checkbox("Aplicar Seguridad Social Empresa (33%)", value=True)

SS_EMPRESA = 0.33
SS_TRABAJADOR = 0.18
RETENCION = 0.02

tabla_final = []

for _, row in df_coste.iterrows():

    fila = {"Puesto": row["Puesto"]}

    for mes in MESES:
        nomina = row[mes]
        ss_empresa = nomina * SS_EMPRESA if aplicar_ss else 0

        fila[f"{mes} · Nómina"] = round(nomina, 2)
        fila[f"{mes} · SS Empresa"] = round(ss_empresa, 2)
        fila[f"{mes} · Coste Empresa"] = round(nomina + ss_empresa, 2)

    tabla_final.append(fila)

df_final = pd.DataFrame(tabla_final)
st.dataframe(df_final, hide_index=True, use_container_width=True)

st.divider()

# =========================
# TOTALES
# =========================
st.subheader("Totales mensuales")

totales = []

for mes in MESES:
    totales.append({
        "Mes": mes,
        "Nómina (€)": round(df_final[f"{mes} · Nómina"].sum(), 2),
        "Seguridad Social (€)": round(df_final[f"{mes} · SS Empresa"].sum(), 2),
        "Coste Empresa (€)": round(df_final[f"{mes} · Coste Empresa"].sum(), 2),
    })

df_totales = pd.DataFrame(totales)
st.dataframe(df_totales, hide_index=True)

st.caption(
    "Este módulo construye el coste salarial completo. "
)
