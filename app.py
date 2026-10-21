
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

    if st.button("🛒 E-commerce sem compra no mês", use_container_width=True):
        perfil = df["PERFIL DIGITAL"].astype(str).str.strip().str.upper()
        compradores = df["COMPRADORES"].astype(str).str.strip().str.upper()

        pendentes = df[
            (perfil == "E-COMM") &
            (compradores != "OK")
        ]

        st.subheader("Clientes E-commerce sem compra no mês")
        st.metric("Clientes pendentes", len(pendentes))
        st.dataframe(pendentes, hide_index=True, use_container_width=True)

        st.download_button(
            "Baixar lista em Excel",
            data=pendentes.to_csv(index=False).encode("utf-8-sig"),
            file_name="ecommerce_sem_compra.csv",
            mime="text/csv"
        )
else:
    st.info("Carregue a planilha anonimizada para começar.")
