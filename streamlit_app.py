import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(page_title="Radar Encarte PRO", layout="wide", page_icon="📊")

# Criar pasta de uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ==============================================================================
# BANCO DE DADOS
# ==============================================================================
conn = sqlite3.connect("radar.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS encartes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT,
    preco REAL,
    loja TEXT,
    imagem TEXT,
    data TEXT,
    curtidas INTEGER DEFAULT 0
)
""")

conn.commit()

# ==============================================================================
# TEMA CLARO PROFISSIONAL
# ==============================================================================
st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
    color: #1e293b;
}

.offer-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-bottom: 15px;
    transition: 0.3s;
}
.offer-card:hover {
    transform: translateY(-5px);
    border-color: #22c55e;
}

.price-tag {
    font-size: 26px;
    color: #16a34a;
    font-weight: bold;
}

.loja-tag {
    color: #64748b;
    font-size: 13px;
    text-transform: uppercase;
}

.best-price-badge {
    background: #22c55e;
    color: white;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.title("📡 Radar SaaS HUB")
menu = st.sidebar.radio("Navegação", [
    "Dashboard",
    "Enviar Encarte",
    "Análise",
])

usuario_loja = "Minha Loja"

# ==============================================================================
# DASHBOARD
# ==============================================================================
if menu == "Dashboard":
    st.title("🔥 Ofertas em Alta")

    busca = st.text_input("Buscar produto ou loja...")

    df = pd.read_sql("SELECT * FROM encartes ORDER BY curtidas DESC", conn)

    if not df.empty:
        if busca:
            df = df[df["produto"].str.contains(busca, case=False)]

        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="offer-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="loja-tag">{row['loja']}</span>
                    {"<span class='best-price-badge'>🔥 DESTAQUE</span>" if row['curtidas'] > 20 else ""}
                </div>

                <h3>{row['produto']}</h3>

                <div class="price-tag">R$ {row['preco']:.2f}</div>

                <img src="{row['imagem']}" width="100%" style="border-radius:10px; margin-top:10px;">

                <p>❤️ {row['curtidas']} votos</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"👍 Curtir {row['id']}"):
                cursor.execute(
                    "UPDATE encartes SET curtidas = curtidas + 1 WHERE id = ?",
                    (row["id"],)
                )
                conn.commit()
                st.rerun()

# ==============================================================================
# ENVIAR ENCARTE
# ==============================================================================
elif menu == "Enviar Encarte":
    st.title("📤 Publicar Encarte")

    with st.form("form_encarte"):
        nome = st.text_input("Produto")
        preco = st.number_input("Preço", min_value=0.01)
        data = st.date_input("Validade")
        imagem = st.file_uploader("Imagem", type=["png", "jpg", "jpeg"])

        enviar = st.form_submit_button("Publicar")

        if enviar:
            if not imagem:
                st.error("Envie uma imagem!")
            else:
                caminho = f"uploads/{imagem.name}"

                with open(caminho, "wb") as f:
                    f.write(imagem.getbuffer())

                cursor.execute("""
                INSERT INTO encartes (produto, preco, loja, imagem, data)
                VALUES (?, ?, ?, ?, ?)
                """, (nome, preco, usuario_loja, caminho, str(data)))

                conn.commit()

                st.success("Encarte publicado com sucesso!")

# ==============================================================================
# ANÁLISE
# ==============================================================================
elif menu == "Análise":
    st.title("📊 Inteligência de Mercado")

    df = pd.read_sql("SELECT * FROM encartes", conn)

    if not df.empty:
        st.subheader("Ranking por Loja")
        ranking = df.groupby("loja")["curtidas"].sum().sort_values(ascending=False)
        st.bar_chart(ranking)

        st.subheader("Base de Dados")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("Sem dados ainda.")

# ==============================================================================
# FOOTER
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("Radar Encarte PRO © 2026")
