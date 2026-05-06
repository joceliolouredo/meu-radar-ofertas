import streamlit as st
import pandas as pd
from datetime import datetime
import os

from database import *
from utils import salvar_imagem

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="Radar Encarte PRO", layout="wide")

conn = conectar()
criar_tabelas(conn)

# ==============================================================================
# CSS LIGHT CLEAN
# ==============================================================================
st.markdown("""
<style>
.stApp { background:#f8fafc; }

.card {
    background:white;
    padding:20px;
    border-radius:12px;
    border:1px solid #e2e8f0;
    margin-bottom:15px;
}

.price { color:#16a34a; font-size:24px; font-weight:bold; }
.loja { color:#64748b; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MENU
# ==============================================================================
menu = st.sidebar.radio("Menu", ["Dashboard", "Novo Encarte", "Análise"])

# ==============================================================================
# DASHBOARD
# ==============================================================================
if menu == "Dashboard":
    st.title("🔥 Radar de Ofertas")

    busca = st.text_input("Buscar produto ou loja")

    dados = listar_encartes(conn)
    df = pd.DataFrame(dados, columns=["id","produto","preco","loja","imagem","data","curtidas"])

    if busca:
        df = df[df["produto"].str.contains(busca, case=False) | df["loja"].str.contains(busca, case=False)]

    for _, row in df.iterrows():
        with st.container():

            data_fmt = ""
            if row["data"]:
                try:
                    data_fmt = datetime.strptime(row["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    data_fmt = row["data"]

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="loja">{row['loja']}</span>
                    <span class="loja">{data_fmt}</span>
                </div>

                <h3>{row['produto']}</h3>
                <div class="price">R$ {row['preco']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            if row["imagem"] and os.path.exists(row["imagem"]):
                st.image(row["imagem"], use_container_width=True)

            st.write(f"❤️ {row['curtidas']}")

            if st.button(f"👍 Curtir {row['id']}"):
                curtir(conn, row["id"])
                st.rerun()

            st.divider()

# ==============================================================================
# NOVO ENCARTE
# ==============================================================================
elif menu == "Novo Encarte":
    st.title("📤 Publicar Encarte")

    with st.form("form"):
        col1, col2 = st.columns(2)

        with col1:
            produto = st.text_input("Produto")
            preco = st.number_input("Preço", min_value=0.01)

        with col2:
            loja = st.text_input("Loja")
            data = st.date_input("Data")

        imagem = st.file_uploader("Imagem")

        submit = st.form_submit_button("Publicar")

        if submit:
            if not produto or not loja:
                st.error("Preencha produto e loja")
            elif not imagem:
                st.error("Envie imagem")
            else:
                caminho = salvar_imagem(imagem)

                inserir_encarte(
                    conn,
                    produto,
                    preco,
                    loja,
                    caminho,
                    str(data)
                )

                st.success("Encarte publicado!")

# ==============================================================================
# ANALISE
# ==============================================================================
elif menu == "Análise":
    st.title("📊 Inteligência")

    df = pd.read_sql("SELECT * FROM encartes", conn)

    if not df.empty:
        ranking = df.groupby("loja")["curtidas"].sum().sort_values(ascending=False)
        st.bar_chart(ranking)

        st.dataframe(df)
    else:
        st.info("Sem dados")
