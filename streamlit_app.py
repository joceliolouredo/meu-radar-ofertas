import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(page_title="Radar Encarte PRO", layout="wide", page_icon="📊")

# Criar pasta uploads
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

# Garantir coluna data
cursor.execute("PRAGMA table_info(encartes)")
cols = [col[1] for col in cursor.fetchall()]
if "data" not in cols:
    cursor.execute("ALTER TABLE encartes ADD COLUMN data TEXT")
    conn.commit()

# ==============================================================================
# TEMA CLARO
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
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MENU
# ==============================================================================
st.sidebar.title("📡 Radar SaaS HUB")
menu = st.sidebar.radio("Menu", ["Dashboard", "Enviar Encarte", "Análise"])

# ==============================================================================
# DASHBOARD
# ==============================================================================
if menu == "Dashboard":
    st.title("🔥 Ofertas Disponíveis")

    busca = st.text_input("Buscar produto ou loja")

    df = pd.read_sql("SELECT * FROM encartes ORDER BY curtidas DESC", conn)

    if not df.empty:
        if busca:
            df = df[df["produto"].str.contains(busca, case=False) | df["loja"].str.contains(busca, case=False)]

        for _, row in df.iterrows():
            with st.container():

                # formatar data
                try:
                    data_formatada = datetime.strptime(row['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    data_formatada = row['data']

                st.markdown(f"""
                <div class="offer-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="loja-tag">{row['loja']}</span>
                        <span style="font-size:12px; color:#64748b;">
                            {data_formatada}
                        </span>
                    </div>

                    <h3>{row['produto']}</h3>
                    <div class="price-tag">R$ {row['preco']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                # imagem correta
                if os.path.exists(row["imagem"]):
                    st.image(row["imagem"], use_container_width=True)
                else:
                    st.warning("Imagem não encontrada")

                st.write(f"❤️ {row['curtidas']} votos")

                if st.button(f"👍 Curtir {row['id']}"):
                    cursor.execute(
                        "UPDATE encartes SET curtidas = curtidas + 1 WHERE id = ?",
                        (row["id"],)
                    )
                    conn.commit()
                    st.rerun()

                st.divider()

    else:
        st.info("Nenhum encarte cadastrado ainda.")

# ==============================================================================
# ENVIAR ENCARTE
# ==============================================================================
elif menu == "Enviar Encarte":
    st.title("📤 Publicar Encarte")

    with st.form("form_encarte"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Produto")
            preco = st.number_input("Preço", min_value=0.01)

        with col2:
            loja = st.text_input("Nome da Loja")
            data = st.date_input("Data do Encarte")

        imagem = st.file_uploader("Imagem", type=["png", "jpg", "jpeg"])

        enviar = st.form_submit_button("Publicar")

        if enviar:
            if not nome or not loja:
                st.error("Preencha produto e loja!")
            elif not imagem:
                st.error("Envie uma imagem!")
            else:
                caminho = f"uploads/{imagem.name}"

                with open(caminho, "wb") as f:
                    f.write(imagem.getbuffer())

                cursor.execute("""
                INSERT INTO encartes (produto, preco, loja, imagem, data)
                VALUES (?, ?, ?, ?, ?)
                """, (nome, preco, loja, caminho, str(data)))

                conn.commit()

                st.success(f"Encarte publicado por {loja}!")

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

        st.subheader("Tabela Completa")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Sem dados ainda.")

# ==============================================================================
# FOOTER
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.caption("Radar Encarte PRO © 2026")
