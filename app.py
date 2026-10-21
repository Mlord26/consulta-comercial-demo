
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consulta Comercial", page_icon="📊")
st.title("📊 Consulta Comercial")
st.caption("Base comercial anonimizada")

arquivo = st.file_uploader("Carregar planilha Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo, header=4)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")

    st.success(f"Base carregada: {len(df)} registros")

    if "COD CLIENTE" in df.columns:
        busca = st.text_input("Buscar pelo código")
        if busca:
            df = df[df["COD CLIENTE"].astype(str).str.contains(busca, na=False)]

    if "ZONA" in df.columns:
        zonas = ["Todas"] + sorted(df["ZONA"].dropna().astype(str).unique())
        zona = st.selectbox("Filtrar por zona", zonas)
        if zona != "Todas":
            df = df[df["ZONA"].astype(str) == zona]

    st.write(f"Registros encontrados: {len(df)}")
    st.dataframe(df, hide_index=True, use_container_width=True)

    if len(df) == 1:
        cliente = df.iloc[0]
        st.subheader("Indicadores do registro")
        colunas_volume = [
            c for c in df.columns
            if "VOLUME COMPRADO" in c
        ]
        if colunas_volume:
            volumes = pd.to_numeric(
                cliente[colunas_volume], errors="coerce"
            )
            st.line_chart(pd.DataFrame({
                "Volume": volumes.values
            }, index=colunas_volume))
        if "FATURAMENTO TOTAL ATUAL" in df.columns:
            st.metric(
                "Faturamento atual",
                f"R$ {pd.to_numeric(cliente['FATURAMENTO TOTAL ATUAL'], errors='coerce') or 0:,.2f}"
            )
else:
    st.info("Carregue a planilha anonimizada para começar.")
