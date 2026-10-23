
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consulta Comercial", page_icon="📊", layout="centered")
st.title("📊 Consulta Comercial")
st.caption("Lista de não compradores por zona e dia")

arquivo = st.file_uploader("Carregar planilha anonimizada (.xlsx)", type=["xlsx"])

if arquivo is None:
    st.info("Carrega a planilha para começar.")
    st.stop()

try:
    df = pd.read_excel(arquivo, header=4)
except Exception as e:
    st.error(f"Não consegui ler a planilha: {e}")
    st.stop()

# Padroniza nomes das colunas, removendo espaços extras.
df.columns = [str(c).strip().upper() for c in df.columns]
df = df.loc[:, ~pd.Index(df.columns).str.match(r"^UNNAMED", case=False)]
df = df.dropna(how="all")

obrigatorias = ["COD CLIENTE", "ZONA", "DIA"]
faltantes = [c for c in obrigatorias if c not in df.columns]
if faltantes:
    st.error("Não encontrei estas colunas na planilha: " + ", ".join(faltantes))
    st.stop()

def texto(coluna):
    return df[coluna].fillna("").astype(str).str.strip().str.upper()

# Filtros globais: zona e dia de visita/rota.
zonas = sorted(df["ZONA"].dropna().astype(str).str.strip().unique().tolist())
dias = sorted(df["DIA"].dropna().astype(str).str.strip().unique().tolist())

col1, col2 = st.columns(2)
with col1:
    zona_escolhida = st.selectbox("📍 Zona", ["Todas"] + zonas)
with col2:
    dia_escolhido = st.selectbox("📅 Dia", ["Todos"] + dias)

base = df.copy()
if zona_escolhida != "Todas":
    base = base[base["ZONA"].astype(str).str.strip() == zona_escolhida]
if dia_escolhido != "Todos":
    base = base[base["DIA"].astype(str).str.strip() == dia_escolhido]

st.caption(f"Registros na seleção: {len(base)}")

def mostrar_codigos(titulo, resultado):
    st.subheader(titulo)
    codigos = resultado[["COD CLIENTE"]].copy()
    codigos["COD CLIENTE"] = codigos["COD CLIENTE"].astype(str).str.replace(r"\.0$", "", regex=True)
    codigos = codigos.drop_duplicates().sort_values("COD CLIENTE")
    st.metric("Clientes não compradores", len(codigos))
    st.dataframe(codigos, hide_index=True, use_container_width=True)
    st.download_button(
        "📥 Baixar códigos dos clientes (CSV)",
        data=codigos.to_csv(index=False).encode("utf-8-sig"),
        file_name="codigos_nao_compradores.csv",
        mime="text/csv",
        key="download_" + "".join(ch if ch.isalnum() else "_" for ch in titulo)
    )

st.divider()
st.subheader("🛒 E-commerce")
if st.button("NÃO COMPRADORES E-COMMERCE", use_container_width=True):
    if "PERFIL DIGITAL" not in base.columns or "COMPRADORES" not in base.columns:
        st.error("Não encontrei a coluna 'PERFIL DIGITAL' ou 'COMPRADORES'.")
    else:
        perfil = base["PERFIL DIGITAL"].fillna("").astype(str).str.strip().str.upper()
        compradores = base["COMPRADORES"].fillna("").astype(str).str.strip().str.upper()
        # Cliente E-COMM sem OK na coluna COMPRADORES é não comprador.
        pendentes = base[(perfil == "E-COMM") & (compradores != "OK")]
        mostrar_codigos("E-commerce sem compra no mês", pendentes)

categorias = {
    "💰 Baixo preço": [
        "FIRST CUT BLUE",
        "FIRST CUT SILVER",
        "L&M FC SILVER BOX",
        "MLB BLUE SELECTION",
    ],
    "🚬 Handling": [
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
st.subheader("Não compradores por marca")
st.write("Seleciona uma categoria e uma ou mais marcas. O app mostra apenas o código de clientes que **não têm OK** em nenhuma das marcas selecionadas.")

for i, (categoria, marcas) in enumerate(categorias.items()):
    with st.expander(categoria, expanded=False):
        marcas_existentes = [m for m in marcas if m in base.columns]
        marcas_faltantes = [m for m in marcas if m not in base.columns]

        if marcas_faltantes:
            st.caption("Colunas não encontradas: " + ", ".join(marcas_faltantes))
        if not marcas_existentes:
            st.warning("Não encontrei colunas de marcas desta categoria.")
            continue

        selecionadas = st.multiselect(
            "Seleciona uma ou mais marcas:",
            options=marcas_existentes,
            key=f"marcas_{i}",
        )

        if st.button("Mostrar não compradores", key=f"buscar_{i}", use_container_width=True):
            if not selecionadas:
                st.warning("Seleciona pelo menos uma marca.")
            else:
                # Para múltiplas marcas, mostra quem ainda não comprou NENHUMA das selecionadas:
                # todas as marcas selecionadas precisam estar sem OK.
                mascara = pd.Series(True, index=base.index)
                for marca in selecionadas:
                    comprou_marca = base[marca].fillna("").astype(str).str.strip().str.upper().eq("OK")
                    mascara = mascara & (~comprou_marca)
                resultado = base[mascara].copy()
                mostrar_codigos(f"{categoria} — não compradores", resultado)
