import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consulta Comercial", page_icon="📊", layout="wide")

st.title("📊 Consulta Comercial")
st.caption("Consulta por zona, e-commerce e marcas de tabaco")

arquivo = st.file_uploader("Carregar planilha anonimizada (.xlsx)", type=["xlsx"])

if arquivo is None:
    st.info("Carrega a planilha para consultar os registros.")
    st.stop()

try:
    # A planilha original tem os títulos das colunas na linha 5 do Excel.
    df = pd.read_excel(arquivo, header=4)
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"Não consegui ler a planilha: {e}")
    st.stop()

# Remove colunas vazias/sem nome, se houver.
df = df.loc[:, ~df.columns.str.match(r"^Unnamed", case=False)]

if "ZONA" not in df.columns:
    st.error("Não encontrei a coluna 'ZONA'. Confere se foi carregada a planilha correta.")
    st.stop()

zonas = sorted(df["ZONA"].dropna().astype(str).str.strip().unique().tolist())
zona_escolhida = st.selectbox("📍 Filtrar por zona", ["Todas"] + zonas)

base = df.copy()
if zona_escolhida != "Todas":
    base = base[base["ZONA"].astype(str).str.strip() == zona_escolhida]

st.caption(f"Registros na zona selecionada: {len(base)}")

def normalizar(coluna):
    if coluna not in base.columns:
        return pd.Series("", index=base.index, dtype=str)
    return base[coluna].fillna("").astype(str).str.strip().str.upper()

def mostrar_resultados(titulo, resultado):
    st.subheader(titulo)
    st.metric("Registros encontrados", len(resultado))
    st.dataframe(resultado, hide_index=True, use_container_width=True)
    if not resultado.empty:
        csv = resultado.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 Baixar esta lista (CSV)",
            data=csv,
            file_name="consulta_comercial.csv",
            mime="text/csv",
            key=f"download_{titulo}"
        )

st.divider()
st.subheader("🛒 E-commerce")
if st.button("E-commerce sem compra no mês", use_container_width=True):
    # Mantém a regra combinada anteriormente: perfil E-COMM e COMPRADORES diferente de OK.
    if "PERFIL DIGITAL" not in base.columns or "COMPRADORES" not in base.columns:
        st.error("Não encontrei a coluna 'PERFIL DIGITAL' ou 'COMPRADORES' na planilha.")
    else:
        perfil = normalizar("PERFIL DIGITAL")
        compradores = normalizar("COMPRADORES")
        pendentes = base[(perfil == "E-COMM") & (compradores != "OK")]
        mostrar_resultados("E-commerce sem compra no mês", pendentes)

categorias = {
    "💰 Marcas de baixo preço": [
        "FIRST CUT BLUE",
        "FIRST CUT SILVER",
        "L&M FC SILVER BOX",
        "MLB BLUE SELECTION",
    ],
    "🚬 Handling Above & Premium": [
        "PARLIAMENT",
        "SAMPOERNA MENTHOL",
        "SAMPOERNA CRAVO",
        "MLB GOLD BOX",
        "MLB RED BOX",
        "MLB BLUE ICE BURST BOX",
        "MLB FOREST FUSION BOX",
        "MLB TROPICAL FUSION BOX",
        "MLB FILTER PLUS BOX",
    ],
    "🆕 Lançamento": [
        "MLB KRETEK MINT BOX",
    ],
}

st.divider()
st.subheader("🚬 Consulta por marca")
st.write("Abre uma categoria, seleciona uma ou mais marcas e toca em **Buscar clientes**. Serão exibidos registros com OK em pelo menos uma das marcas selecionadas.")

for i, (categoria, marcas) in enumerate(categorias.items()):
    with st.expander(categoria, expanded=False):
        marcas_existentes = [m for m in marcas if m in base.columns]
        marcas_faltantes = [m for m in marcas if m not in base.columns]

        if marcas_faltantes:
            st.caption("Colunas não encontradas na planilha: " + ", ".join(marcas_faltantes))
        if not marcas_existentes:
            st.warning("Não encontrei colunas de marcas desta categoria na planilha.")
            continue

        selecionadas = st.multiselect(
            "Seleciona uma ou mais marcas:",
            options=marcas_existentes,
            key=f"marcas_{i}",
        )

        if st.button("Buscar clientes", key=f"buscar_{i}", use_container_width=True):
            if not selecionadas:
                st.warning("Seleciona pelo menos uma marca.")
            else:
                mascara = pd.Series(False, index=base.index)
                for marca in selecionadas:
                    mascara = mascara | (normalizar(marca) == "OK")
                resultado = base[mascara].copy()
                mostrar_resultados(f"{categoria} — clientes com OK", resultado)
