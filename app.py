
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consulta Comercial", page_icon="📊")
st.title("📊 Consulta Comercial")

arquivo = st.file_uploader("Carregar planilha Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo, header=4)
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")

    st.success(f"Base carregada: {len(df)} registros")

    if "ZONA" in df.columns:
        zonas = sorted(df["ZONA"].dropna().astype(str).unique())
        zona = st.selectbox("📍 Filtrar por zona", ["Todas"] + zonas)
    else:
        zona = "Todas"
        st.warning("Coluna ZONA não encontrada.")

    if st.button("🛒 E-commerce sem compra no mês", use_container_width=True):
        perfil = df["PERFIL DIGITAL"].astype(str).str.strip().str.upper()
        compradores = df["COMPRADORES"].astype(str).str.strip().str.upper()

        pendentes = df[
            (perfil == "E-COMM") &
            (compradores != "OK")
        ].copy()

        if zona != "Todas":
            pendentes = pendentes[
                pendentes["ZONA"].astype(str) == zona
            ]

        st.subheader("E-commerce sem compra no mês")
        st.metric("Clientes pendentes", len(pendentes))
        st.dataframe(pendentes, hide_index=True, use_container_width=True)

        st.download_button(
            "📥 Baixar lista",
            data=pendentes.to_csv(index=False).encode("utf-8-sig"),
            file_name="ecommerce_sem_compra.csv",
            mime="text/csv"
        )
else:
    st.info("Carregue a planilha anonimizada para começar.")
