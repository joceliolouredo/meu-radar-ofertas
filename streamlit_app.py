import streamlit as st
from PIL import Image
import pandas as pd
import json
import os
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIG
# ==============================================================================
st.set_page_config(page_title="SuperRadar", layout="wide")

ARQUIVO_ENCARTES = "encartes.json"
PASTA_IMAGENS = "encartes_img"

os.makedirs(PASTA_IMAGENS, exist_ok=True)

# ==============================================================================
# 💾 FUNÇÕES DE BANCO LOCAL
# ==============================================================================
def carregar_encartes():
    if os.path.exists(ARQUIVO_ENCARTES):
        with open(ARQUIVO_ENCARTES, "r") as f:
            return json.load(f)
    return []

def salvar_encartes(encartes):
    with open(ARQUIVO_ENCARTES, "w") as f:
        json.dump(encartes, f)

# Carregar dados
encartes = carregar_encartes()

# ==============================================================================
# 📱 MENU
# ==============================================================================
modo = st.sidebar.selectbox("Menu", ["👥 Comunidade", "🏪 Lojista"])

# ==============================================================================
# 👥 COMUNIDADE
# ==============================================================================
if modo == "👥 Comunidade":
    st.title("📰 Encartes das Lojas")

    if not encartes:
        st.info("Nenhum encarte ainda.")
    else:
        cols = st.columns(3)  # 3 lado a lado

        for i, encarte in enumerate(encartes):
            with cols[i % 3]:
                st.markdown(f"**{encarte['loja']}**")
                st.image(encarte['imagem_path'], use_column_width=True)

# ==============================================================================
# 🏪 LOJISTA
# ==============================================================================
elif modo == "🏪 Lojista":
    st.title("🏪 Painel do Lojista")

    loja = st.text_input("Nome da loja")

    st.subheader("📸 Enviar Encartes")

    arquivos = st.file_uploader(
        "Envie um ou mais encartes",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    if arquivos and st.button("💾 Salvar Encartes"):
        for arquivo in arquivos:
            nome_arquivo = f"{datetime.now().timestamp()}_{arquivo.name}"
            caminho = os.path.join(PASTA_IMAGENS, nome_arquivo)

            with open(caminho, "wb") as f:
                f.write(arquivo.getbuffer())

            encartes.append({
                "loja": loja,
                "imagem_path": caminho
            })

        salvar_encartes(encartes)
        st.success("✅ Encartes salvos com sucesso!")
        st.rerun()

    # 🔥 GERENCIAR ENCARTE
    st.subheader("🗂️ Seus Encartes")

    if encartes:
        for i, encarte in enumerate(encartes):
            if encarte['loja'] == loja:
                col1, col2 = st.columns([3,1])

                with col1:
                    st.image(encarte['imagem_path'], width=250)

                with col2:
                    if st.button(f"❌ Excluir {i}", key=f"del_{i}"):
                        # Remove imagem
                        if os.path.exists(encarte['imagem_path']):
                            os.remove(encarte['imagem_path'])

                        # Remove do banco
                        encartes.pop(i)
                        salvar_encartes(encartes)

                        st.success("Encartes excluído!")
                        st.rerun()
    else:
        st.info("Nenhum encarte cadastrado.")
