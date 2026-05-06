import streamlit as st
from PIL import Image
import json
import os
import uuid
from datetime import datetime, timedelta
import pandas as pd

# ==============================================================================
# CONFIG
# ==============================================================================
st.set_page_config(page_title="SuperRadar", layout="wide")

ARQUIVO_ENCARTES = "encartes.json"
ARQUIVO_LOJAS = "lojas.json"
PASTA_ENCARTES = "encartes_img"
PASTA_PERFIS = "perfil_img"

os.makedirs(PASTA_ENCARTES, exist_ok=True)
os.makedirs(PASTA_PERFIS, exist_ok=True)

# ==============================================================================
# LOGIN SIMPLES
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
# BANCO
# ==============================================================================
def carregar_json(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return json.load(f)
    return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f)

encartes = carregar_json(ARQUIVO_ENCARTES)
lojas = carregar_json(ARQUIVO_LOJAS)

# corrigir dados antigos
for e in encartes:
    e.setdefault("likes", 0)
    e.setdefault("liked_users", [])
    e.setdefault("reposts", 0)
    e.setdefault("reposted_users", [])
    e.setdefault("timestamp", datetime.now().isoformat())
    if "imagem" not in e and "imagem_path" in e:
        e["imagem"] = e["imagem_path"]

# ==============================================================================
# MENU
# ==============================================================================
modo = st.sidebar.selectbox("Menu", ["👥 Comunidade", "🏪 Lojista", "🏆 Ranking"])

# ==============================================================================
# COMUNIDADE
# ==============================================================================
if modo == "👥 Comunidade":
    st.title("🔥 Radar Social de Ofertas")

    # PERFIS
    st.subheader("🏪 Lojas")

    for loja in lojas:
        col1, col2 = st.columns([1,3])

        with col1:
            if loja.get("foto"):
                st.image(loja["foto"], width=80)

        with col2:
            st.markdown(f"### {loja['nome']}")
            st.write(loja.get("descricao",""))

            if st.button(f"Ver perfil {loja['nome']}", key=loja['nome']):
                st.session_state["perfil_loja"] = loja['nome']

    # PERFIL DETALHADO
    if "perfil_loja" in st.session_state:
        nome = st.session_state["perfil_loja"]
        loja = next((l for l in lojas if l['nome'] == nome), None)

        if loja:
            st.title(loja['nome'])

            if loja.get("foto"):
                st.image(loja["foto"], width=150)

            st.write(loja.get("descricao",""))
            st.write(f"📍 {loja.get('endereco','')}")
            st.write(f"📞 {loja.get('contato','')}")

            st.subheader("📦 Encartes")

            for e in encartes:
                if e['loja'] == nome:
                    st.image(e['imagem'], width=300)

    # GRID
    st.subheader("📰 Encartes")

    cols = st.columns(4)

    for i, e in enumerate(encartes):
        with cols[i % 4]:

            if e.get("imagem"):
                st.image(e["imagem"], use_column_width=True)

            st.markdown(f"**{e['loja']}**")
            st.markdown(f"👍 {e['likes']} | 🔁 {e['reposts']}")

            # CURTIR / DESCURTIR
            if user_id in e['liked_users']:
                if st.button("💔 Descurtir", key=f"unlike_{i}"):
                    e['likes'] -= 1
                    e['liked_users'].remove(user_id)
                    salvar_json(ARQUIVO_ENCARTES, encartes)
                    st.rerun()
            else:
                if st.button("❤️ Curtir", key=f"like_{i}"):
                    e['likes'] += 1
                    e['liked_users'].append(user_id)
                    salvar_json(ARQUIVO_ENCARTES, encartes)
                    st.rerun()

            # REPOST
            if user_id not in e['reposted_users']:
                if st.button("🔁 Repostar", key=f"rep_{i}"):
                    novo = e.copy()
                    novo['likes'] = 0
                    novo['liked_users'] = []
                    novo['reposts'] = 0
                    novo['reposted_users'] = []
                    novo['loja'] = f"{st.session_state.usuario} (repost)"
                    novo['timestamp'] = datetime.now().isoformat()

                    encartes.append(novo)

                    e['reposts'] += 1
                    e['reposted_users'].append(user_id)

                    salvar_json(ARQUIVO_ENCARTES, encartes)
                    st.rerun()

            # ZOOM
            if st.button("🔍", key=f"zoom_{i}"):
                st.session_state["zoom"] = e["imagem"]

    # MODAL
    if "zoom" in st.session_state:
        st.image(st.session_state["zoom"], use_column_width=True)
        if st.button("Fechar"):
            del st.session_state["zoom"]

# ==============================================================================
# LOJISTA
# ==============================================================================
elif modo == "🏪 Lojista":
    st.title("🏪 Painel do Lojista")

    nome = st.text_input("Nome da loja")
    desc = st.text_area("Descrição")
    end = st.text_input("Endereço")
    cont = st.text_input("Contato")

    foto = st.file_uploader("Foto perfil", type=["jpg","png"])

    if st.button("Salvar Perfil"):
        path = ""

        if foto:
            nome_foto = f"{nome}_{foto.name}"
            caminho = os.path.join(PASTA_PERFIS, nome_foto)

            with open(caminho, "wb") as f:
                f.write(foto.getbuffer())

            path = caminho

        existente = next((l for l in lojas if l['nome'] == nome), None)

        if existente:
            existente.update({
                "descricao": desc,
                "endereco": end,
                "contato": cont,
                "foto": path or existente.get("foto","")
            })
        else:
            lojas.append({
                "nome": nome,
                "descricao": desc,
                "endereco": end,
                "contato": cont,
                "foto": path
            })

        salvar_json(ARQUIVO_LOJAS, lojas)
        st.success("Perfil salvo!")

    # ENCARTE
    arquivos = st.file_uploader("Enviar encartes", accept_multiple_files=True)

    if arquivos and st.button("Salvar Encartes"):
        for arq in arquivos:
            nome_img = f"{datetime.now().timestamp()}_{arq.name}"
            caminho = os.path.join(PASTA_ENCARTES, nome_img)

            with open(caminho, "wb") as f:
                f.write(arq.getbuffer())

            encartes.append({
                "loja": nome,
                "imagem": caminho,
                "likes": 0,
                "liked_users": [],
                "reposts": 0,
                "reposted_users": [],
                "timestamp": datetime.now().isoformat()
            })

        salvar_json(ARQUIVO_ENCARTES, encartes)
        st.success("Encartes enviados!")

# ==============================================================================
# RANKING
# ==============================================================================
elif modo == "🏆 Ranking":
    st.title("🏆 Ranking")

    if encartes:
        df = pd.DataFrame(encartes)

        st.subheader("🔥 Mais Curtidos")
        st.table(df.sort_values(by="likes", ascending=False)[['loja','likes']].head(5))

        st.subheader("🔁 Mais Repostados")
        st.table(df.sort_values(by="reposts", ascending=False)[['loja','reposts']].head(5))
