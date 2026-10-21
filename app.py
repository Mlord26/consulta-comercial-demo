
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Consulta Comercial",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Consulta Comercial")
st.caption("Protótipo de consulta de clientes")

clientes = pd.DataFrame([
    {"Cliente": "Mercado Exemplo 1", "Cidade": "Cachoeirinha", "Zona": "FA01", "Volume": 15000},
    {"Cliente": "Mercado Exemplo 2", "Cidade": "Gravataí", "Zona": "FA02", "Volume": 22000},
    {"Cliente": "Comercial Demonstração", "Cidade": "Canoas", "Zona": "FA01", "Volume": 9500},
])

busca = st.text_input("🔎 Buscar cliente ou cidade")

zonas = ["Todas"] + sorted(clientes["Zona"].unique().tolist())
zona = st.selectbox("Filtrar por zona", zonas)

resultado = clientes.copy()

if busca:
    resultado = resultado[
        resultado["Cliente"].str.contains(busca, case=False) |
        resultado["Cidade"].str.contains(busca, case=False)
    ]

if zona != "Todas":
    resultado = resultado[resultado["Zona"] == zona]

st.write(f"Clientes encontrados: {len(resultado)}")
st.dataframe(resultado, hide_index=True, use_container_width=True)

st.info("Demonstração com dados fictícios. A base real será integrada depois.")
