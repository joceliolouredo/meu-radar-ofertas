import streamlit as st
from PIL import Image
import json
import os
import uuid
import time
from datetime import datetime, timedelta
import pandas as pd

# ==============================================================================
# ⚙️ CONFIG
# ==============================================================================
st.set_page_config(page_title="SuperRadar", layout="wide")

ARQUIVO = "encartes.json"
PASTA = "encartes_img"
os.makedirs(PASTA, exist_ok=True)

# ==============================================================================
# 🔐 LOGIN SIMPLES
# ==============================================================================
if "usuario" not in st.session_state:
    nome = st.text_input("Digite seu nome")
    if st.button("Entrar"):
        st.session_state.usuario = nome
        st.session_state.user_id = str(uuid.uuid4())
        st.rerun()
    st.stop()

user_id = st.session_state.user_id

# ==============================================================================
# 💾 BANCO LOCAL
# ==============================================================================
def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            return json.load(f)
    return []

def salvar(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f)

encartes = carregar()

# ==============================================================================
# 📱 MENU
# ==============================================================================
modo = st.sidebar.selectbox("Menu", ["👥 Comunidade", "🏪 Lojista", "🏆 Ranking"])

# ==============================================================================
# 👥 COMUNIDADE
# ==============================================================================
if modo == "👥 Comunidade":
    st.title("🔥 Radar de Encartes")

    # 🔄 CARROSSEL
    if encartes:
        st.subheader("✨ Destaques")

        ordenados = sorted(encartes, key=lambda x: x['timestamp'], reverse=True)

        if "carousel" not in st.session_state:
            st.session_state.carousel = 0

        atual = ordenados[st.session_state.carousel]

        st.image(atual['imagem'], use_column_width=True)
        st.markdown(f"**🏪 {atual['loja']}**")
        st.markdown(f"👍 {atual['likes']} curtidas")

        time.sleep(30)
        st.session_state.carousel = (st.session_state.carousel + 1) % len(ordenados)
        st.rerun()

    # 📰 GRID
    st.subheader("📰 Todos os Encartes")

    cols = st.columns(3)

    for i, encarte in enumerate(encartes):
        with cols[i % 3]:
            st.image(encarte['imagem'], use_column_width=True)
            st.markdown(f"**{encarte['loja']}**")
            st.markdown(f"👍 {encarte['likes']}")

            if user_id not in encarte['liked_users']:
                if st.button("👍 Curtir", key=f"like_{i}"):
                    encartes[i]['likes'] += 1
                    encartes[i]['liked_users'].append(user_id)
                    salvar(encartes)
                    st.rerun()
            else:
                st.caption("✅ Já curtiu")

# ==============================================================================
# 🏪 LOJISTA
# ==============================================================================
elif modo == "🏪 Lojista":
    st.title("🏪 Painel do Lojista")

    loja = st.text_input("Nome da loja")

    arquivos = st.file_uploader(
        "Envie encartes",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    if arquivos and st.button("Salvar Encartes"):
        for arquivo in arquivos:
            nome = f"{datetime.now().timestamp()}_{arquivo.name}"
            caminho = os.path.join(PASTA, nome)

            with open(caminho, "wb") as f:
                f.write(arquivo.getbuffer())

            encartes.append({
                "loja": loja,
                "imagem": caminho,
                "likes": 0,
                "liked_users": [],
                "timestamp": datetime.now().isoformat()
            })

        salvar(encartes)
        st.success("Encartes salvos!")
        st.rerun()

    # 🗂️ GERENCIAR
    st.subheader("Seus Encartes")

    for i, encarte in enumerate(encartes):
        if encarte['loja'] == loja:
            col1, col2 = st.columns([3,1])

            with col1:
                st.image(encarte['imagem'], width=250)

            with col2:
                if st.button("❌ Excluir", key=f"del_{i}"):
                    if os.path.exists(encarte['imagem']):
                        os.remove(encarte['imagem'])

                    encartes.pop(i)
                    salvar(encartes)
                    st.rerun()

# ==============================================================================
# 🏆 RANKING
# ==============================================================================
elif modo == "🏆 Ranking":
    st.title("🏆 Ranking de Curtidas")

    if encartes:
        df = pd.DataFrame(encartes)

        # 🥇 Top geral
        top = df.sort_values(by="likes", ascending=False).head(5)
        st.subheader("🔥 Mais Curtidos")
        st.table(top[['loja', 'likes']])

        # 📅 Hoje
        hoje = datetime.now().date()
        df['data'] = pd.to_datetime(df['timestamp']).dt.date
        hoje_df = df[df['data'] == hoje]

        st.subheader("📅 Hoje")
        st.table(hoje_df.sort_values(by="likes", ascending=False)[['loja','likes']])

        # 📆 Semana
        semana = datetime.now() - timedelta(days=7)
        semana_df = df[pd.to_datetime(df['timestamp']) >= semana]

        st.subheader("📆 Semana")
        st.table(semana_df.sort_values(by="likes", ascending=False)[['loja','likes']])
    else:
        st.info("Sem dados ainda.")
