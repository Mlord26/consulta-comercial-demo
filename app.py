import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consulta Comercial", page_icon="📊", layout="centered")
st.title("📊 Consulta Comercial")
st.caption("Consulta por zona, dia, marcas, e-commerce e volume mensal de tabaco")

arquivo = st.file_uploader("Carregar planilha anonimizada (.xlsx)", type=["xlsx"])
if arquivo is None:
    st.info("Carrega a planilha para começar.")
    st.stop()
try:
    df = pd.read_excel(arquivo, header=4)
except Exception as e:
    st.error(f"Não consegui ler a planilha: {e}")
    st.stop()

df.columns = [str(c).strip().upper() for c in df.columns]
df = df.loc[:, ~pd.Index(df.columns).str.match(r"^UNNAMED", case=False)].dropna(how="all")

def achar(fragmento):
    return next((c for c in df.columns if fragmento in str(c).upper()), None)

codigo_col = achar("COD CLIENTE")
zona_col = next((c for c in df.columns if str(c).strip().upper() == "ZONA"), None)
dia_col = next((c for c in df.columns if str(c).strip().upper() == "DIA"), None)
perfil_col = next((c for c in df.columns if str(c).strip().upper() == "PERFIL DIGITAL"), None)
compradores_col = next((c for c in df.columns if str(c).strip().upper() == "COMPRADORES"), None)
if not codigo_col:
    st.error("Não encontrei a coluna de código do cliente (COD CLIENTE).")
    st.stop()
c1, c2 = st.columns(2)
with c1:
    zonas = sorted(df[zona_col].dropna().astype(str).str.strip().unique()) if zona_col else []
    zona_escolhida = st.selectbox("📍 Zona", ["Todas"] + list(zonas))
with c2:
    dias = sorted(df[dia_col].dropna().astype(str).str.strip().unique()) if dia_col else []
    dia_escolhido = st.selectbox("📅 Dia", ["Todos"] + list(dias))

base = df.copy()
if zona_col and zona_escolhida != "Todas":
    base = base[base[zona_col].astype(str).str.strip() == zona_escolhida]
if dia_col and dia_escolhido != "Todos":
    base = base[base[dia_col].astype(str).str.strip() == dia_escolhido]
st.caption(f"Registros na seleção: {len(base)}")

def limpar_codigo(s):
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

def mostrar_codigos(titulo, resultado):
    st.subheader(titulo)
    saida = resultado[[codigo_col]].copy()
    saida.columns = ["CÓDIGO DO CLIENTE"]
    saida["CÓDIGO DO CLIENTE"] = limpar_codigo(saida["CÓDIGO DO CLIENTE"])
    saida = saida.drop_duplicates().sort_values("CÓDIGO DO CLIENTE")
    st.metric("Quantidade de clientes", len(saida))
    st.dataframe(saida, hide_index=True, use_container_width=True)
    st.download_button("📥 Baixar códigos (CSV)", saida.to_csv(index=False).encode("utf-8-sig"),
        file_name="codigos_clientes.csv", mime="text/csv",
        key="csv_" + "".join(ch if ch.isalnum() else "_" for ch in titulo))

st.divider()
st.subheader("🛒 E-commerce")
if st.button("NÃO COMPRADORES E-COMMERCE", use_container_width=True):
    if not perfil_col or not compradores_col:
        st.error("Não encontrei as colunas PERFIL DIGITAL e/ou COMPRADORES.")
    else:
        perfil = base[perfil_col].fillna("").astype(str).str.strip().str.upper()
        compradores = base[compradores_col].fillna("").astype(str).str.strip().str.upper()
        mostrar_codigos("E-commerce sem compra", base[(perfil == "E-COMM") & (compradores != "OK")])

categorias = {
    "💰 Baixo preço": ["FIRST CUT BLUE", "FIRST CUT SILVER", "L&M FC SILVER BOX", "MLB BLUE SELECTION"],
    "🚬 Handling": ["PARLIAMENT", "SAMPOERNA MENTHOL", "SAMPOERNA CRAVO", "MLB GOLD BOX",
        "MLB RED BOX", "MLB BLUE ICE BURST BOX", "MLB FOREST FUSION BOX",
        "MLB TROPICAL FUSION BOX", "MLB FILTER PLUS BOX"],
    "🆕 Lançamento": ["MLB KRETEK MINT BOX"],
}
st.divider()
st.subheader("Não compradores por marca")
for i, (categoria, marcas) in enumerate(categorias.items()):
    with st.expander(categoria):
        existentes = [m for m in marcas if m in base.columns]
        faltantes = [m for m in marcas if m not in base.columns]
        if faltantes:
            st.caption("Colunas não encontradas: " + ", ".join(faltantes))
        if not existentes:
            st.warning("Não encontrei colunas de marcas desta categoria.")
            continue
        selecionadas = st.multiselect("Seleciona uma ou mais marcas:", existentes, key=f"marcas_{i}")
        if st.button("Mostrar não compradores", key=f"buscar_{i}", use_container_width=True):
            if not selecionadas:
                st.warning("Seleciona pelo menos uma marca.")
            else:
                mascara = pd.Series(True, index=base.index)
                for marca in selecionadas:
                    comprou = base[marca].fillna("").astype(str).str.strip().str.upper().eq("OK")
                    mascara &= ~comprou
                mostrar_codigos(f"{categoria} — não compradores", base[mascara])

st.divider()
st.subheader("🚬 Classificação de volume mensal de tabaco")
st.write("Escolhe o mês e depois P, M ou G. A lista mostra o código e o volume daquele mês.")
colunas_volume = [c for c in df.columns if "VOLUME COMPRADO" in str(c).upper()]
if not colunas_volume:
    st.warning("Não encontrei colunas com 'VOLUME COMPRADO' no nome. Confere os títulos dos meses na planilha.")
else:
    meses = {str(c).upper().replace("VOLUME COMPRADO", "").strip(" _-:"): c for c in colunas_volume}
    mes = st.selectbox("📅 Mês do volume", list(meses.keys()), key="mes_volume")
    coluna_volume = meses[mes]
    p, m, g = st.columns(3)
    with p: ver_p = st.button("P", use_container_width=True, key="volume_p")
    with m: ver_m = st.button("M", use_container_width=True, key="volume_m")
    with g: ver_g = st.button("G", use_container_width=True, key="volume_g")
    if ver_p or ver_m or ver_g:
        volumes = pd.to_numeric(base[coluna_volume], errors="coerce").fillna(0)
        if ver_p:
            faixa, grupo = volumes <= 2.0, "P"
            descricao = "P — até 2,0"
        elif ver_m:
            faixa, grupo = (volumes > 2.0) & (volumes <= 10.0), "M"
            descricao = "M — acima de 2,0 até 10,0"
        else:
            faixa, grupo = volumes > 10.0, "G"
            descricao = "G — acima de 10,0"
        resultado = base.loc[faixa, [codigo_col]].copy()
        resultado["VOLUME DO MÊS"] = volumes.loc[faixa].round(2)
        resultado.columns = ["CÓDIGO DO CLIENTE", "VOLUME DO MÊS"]
        resultado["CÓDIGO DO CLIENTE"] = limpar_codigo(resultado["CÓDIGO DO CLIENTE"])
        resultado = resultado.drop_duplicates().sort_values("VOLUME DO MÊS", ascending=(grupo == "P"))
        st.markdown(f"### {descricao}")
        st.metric("Clientes nesta faixa", len(resultado))
        if grupo == "M":
            st.markdown("<style>[data-testid='stDataFrame'] {border: 2px solid #168BFF; border-radius: 8px;}</style>", unsafe_allow_html=True)
            st.dataframe(resultado.style.set_properties(**{"background-color": "#DCEEFF", "color": "#123A66"}),
                         hide_index=True, use_container_width=True)
        else:
            st.dataframe(resultado, hide_index=True, use_container_width=True)
        st.download_button(f"📥 Baixar lista {grupo} — {mes} (CSV)",
            resultado.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"clientes_{grupo}_{mes.replace(' ', '_')}.csv",
            mime="text/csv", key=f"baixar_volume_{grupo}")
