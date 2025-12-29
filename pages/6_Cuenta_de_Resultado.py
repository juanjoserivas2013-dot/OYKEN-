import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.title("OYKEN · Cuenta de Resultados")
st.caption("Lectura económica real del negocio")

st.divider()

# =====================================================
# ARCHIVOS
# =====================================================

VENTAS_FILE = Path("ventas.csv")
COMPRAS_FILE = Path("compras.csv")
INVENTARIO_FILE = Path("inventario.csv")
GASTOS_FILE = Path("gastos.csv")

# =====================================================
# SELECTOR PERIODO
# =====================================================

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

c1, c2 = st.columns(2)
with c1:
    mes_sel = st.selectbox("Mes", MESES, index=date.today().month - 1)
with c2:
    año_sel = st.selectbox(
        "Año",
        list(range(date.today().year - 3, date.today().year + 1)),
        index=3
    )

mes_num = MESES.index(mes_sel) + 1
periodo = f"{año_sel}-{mes_num:02d}"

st.divider()

# =====================================================
# VENTAS
# =====================================================

ventas_total = 0.0

if VENTAS_FILE.exists():
    df_v = pd.read_csv(VENTAS_FILE, parse_dates=["fecha"])
    df_v["Mes"] = df_v["fecha"].dt.strftime("%Y-%m")
    ventas_total = df_v[df_v["Mes"] == periodo]["ventas_total_eur"].sum()

# =====================================================
# COMPRAS (COGS)
# =====================================================

compras_producto = 0.0

if COMPRAS_FILE.exists():
    df_c = pd.read_csv(COMPRAS_FILE)
    df_c["Fecha"] = pd.to_datetime(df_c["Fecha"], dayfirst=True, errors="coerce")
    df_c["Mes"] = df_c["Fecha"].dt.strftime("%Y-%m")

    compras_producto = df_c[
        (df_c["Mes"] == periodo) &
        (df_c["Familia"].isin(["Materia prima", "Bebidas"]))
    ]["Coste (€)"].sum()

# =====================================================
# INVENTARIO (VARIACIÓN)
# =====================================================

inventario_var = 0.0

if INVENTARIO_FILE.exists():
    df_i = pd.read_csv(INVENTARIO_FILE)

    actual = df_i[
        (df_i["Mes"] == mes_sel) &
        (df_i["Año"] == año_sel)
    ]

    # Mes anterior
    if mes_num == 1:
        mes_ant = "Diciembre"
        año_ant = año_sel - 1
    else:
        mes_ant = MESES[mes_num - 2]
        año_ant = año_sel

    anterior = df_i[
        (df_i["Mes"] == mes_ant) &
        (df_i["Año"] == año_ant)
    ]

    if not actual.empty and not anterior.empty:
        inventario_var = (
            actual.iloc[0]["Inventario (€)"] -
            anterior.iloc[0]["Inventario (€)"]
        )

# =====================================================
# GASTOS OPERATIVOS
# =====================================================

gastos_total = 0.0
gastos_por_categoria = {}

if GASTOS_FILE.exists():
    df_g = pd.read_csv(GASTOS_FILE)
    gastos_mes = df_g[df_g["Mes"] == periodo]

    gastos_total = gastos_mes["Coste (€)"].sum()
    gastos_por_categoria = (
        gastos_mes.groupby("Categoria")["Coste (€)"].sum().to_dict()
    )

# =====================================================
# RRHH (FASE 1 — NEUTRO)
# =====================================================

coste_personal = 0.0  # Se integrará por CSV en fase siguiente

# =====================================================
# CÁLCULOS
# =====================================================

margen_bruto = ventas_total - compras_producto + inventario_var
ebitda = margen_bruto - coste_personal - gastos_total

# =====================================================
# FUNCIONES UI
# =====================================================

def fila(concepto, importe):
    c1, c2 = st.columns([4, 1])
    with c1:
        st.write(concepto)
    with c2:
        st.write(f"{importe:,.2f} €")

# =====================================================
# RESULTADO EJECUTIVO
# =====================================================

st.subheader("Resultado del periodo")
fila("Ventas netas", ventas_total)
fila("Margen bruto", margen_bruto)
fila("EBITDA", ebitda)

st.divider()

# =====================================================
# ESTRUCTURA CONTABLE
# =====================================================

st.subheader("Estructura contable")

st.markdown("**Ingresos**")
fila("Ventas netas", ventas_total)

st.divider()

st.markdown("**Coste de ventas (COGS)**")
fila("Compras de producto", -compras_producto)
fila("Variación de inventario", inventario_var)
fila("Margen bruto", margen_bruto)

st.divider()

st.markdown("**Gastos de personal**")
fila("Coste de personal", -coste_personal)

st.divider()

st.markdown("**Gastos operativos**")
for cat, imp in gastos_por_categoria.items():
    fila(cat, -imp)

st.divider()

st.subheader("EBITDA")
fila("Resultado operativo", ebitda)

st.divider()

# =====================================================
# LECTURA OYKEN
# =====================================================

st.subheader("Lectura del periodo")

if ventas_total > 0:
    st.write(f"- Margen bruto del {(margen_bruto / ventas_total * 100):.1f} %.")
    st.write(f"- EBITDA del {(ebitda / ventas_total * 100):.1f} %.")
else:
    st.write("- No hay ventas suficientes para análisis.")

st.divider()

st.caption(
    "Datos consolidados desde Ventas · Compras · Inventario · Gastos"
)
