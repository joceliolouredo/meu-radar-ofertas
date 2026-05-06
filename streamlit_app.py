import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import urllib.parse

# ==============================================================================
# ⚙️ CONFIGURAÇÕES
# ==============================================================================
st.set_page_config(page_title="SuperRadar SaaS", layout="wide", page_icon="💰")

st.markdown("""
<style>
.main { background-color: #f5f7f9; }
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #16a34a;
    color: white;
    font-weight: bold;
}
.offer-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    border-left: 8px solid #16a34a;
    margin-bottom: 15px;
    box-shadow: 2px 2px 15px rgba(0,0,0,0.05);
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🔐 API GEMINI
# ==============================================================================
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.warning("Rodando sem IA (modo demo)")

URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

# ==============================================================================
# 🧠 BANCO TEMPORÁRIO (MVP)
# ==============================================================================
if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Arroz 5kg", "preco": 23.90, "loja": "Mercadinho Zé", "tipo": "dia", "pagamento": "Cartão"},
        {"produto": "Feijão 1kg", "preco": 6.90, "loja": "Mercadinho Zé", "tipo": "semana", "pagamento": "Dinheiro"},
    ]

# ==============================================================================
# 🤖 IA
# ==============================================================================
def extrair_dados_ia(imagem):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = """Extraia ofertas de supermercado.
        Retorne JSON:
        [{"produto": "nome", "preco": 0.00, "unidade": "kg/un"}]
        """
        response = model.generate_content([prompt, imagem])
        texto = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(texto)
    except:
        return None

# ==============================================================================
# 📊 FUNÇÃO DE ECONOMIA (SEM CONFLITO)
# ==============================================================================
def calcular_economia(df):
    if df.empty:
        return df

    media = df.groupby('produto')['preco'].transform('mean')
    df['economia'] = media - df['preco']
    return df

# ==============================================================================
# 📱 SIDEBAR
# ==============================================================================
st.sidebar.title("💎 SuperRadar")
modo = st.sidebar.selectbox("Menu", [
    "👥 Comunidade",
    "🏪 Lojista",
    "🏆 Ranking",
    "💰 Planos"
])

# ==============================================================================
# 👥 COMUNIDADE
# ==============================================================================
if modo == "👥 Comunidade":
    st.title("🛒 Ofertas da Comunidade")

    busca = st.text_input("🔍 Buscar produto")
    filtro = st.selectbox("Período", ["dia", "semana", "mes"])

    df = pd.DataFrame(st.session_state.db_promocoes)

    if not df.empty:
        df = df[df['tipo'] == filtro]

        if busca:
            df = df[df['produto'].str.contains(busca, case=False)]

        df = calcular_economia(df)
        df = df.sort_values(by='economia', ascending=False)

        for _, row in df.iterrows():

            # Mensagem WhatsApp
            msg = f"""🔥 OFERTA 🔥

📦 {row['produto']}
💰 R$ {row['preco']:.2f}
🛒 {row['loja']}

Veja mais:
{URL_SISTEMA}
"""
            link = f"https://wa.me/?text={urllib.parse.quote(msg)}"

            st.markdown(f"""
            <div class="offer-card">
                <small>{row['loja'].upper()}</small><br>
                <strong>{row['produto']}</strong><br>
                <span style="font-size:24px; color:#16a34a;">
                R$ {row['preco']:.2f}
                </span><br>
                <span style="font-size:12px;">{row['pagamento']}</span>
            </div>
            """, unsafe_allow_html=True)

            # ECONOMIA (NEUTRO)
            if row['economia'] > 0:
                st.success(f"💰 Economia estimada: R$ {row['economia']:.2f}")
            else:
                st.info("📊 Preço alinhado à média da região")

            st.link_button("📢 Compartilhar", link)
            st.divider()

# ==============================================================================
# 🏪 LOJISTA
# ==============================================================================
elif modo == "🏪 Lojista":
    st.title("🏪 Painel do Lojista")

    loja = st.text_input("Nome da loja")

    tab1, tab2 = st.tabs(["📸 IA", "✍️ Manual"])

    # IA
    with tab1:
        foto = st.file_uploader("Upload encarte", type=["jpg", "png"])

        if foto:
            img = Image.open(foto)
            st.image(img, width=300)

            if st.button("Processar com IA"):
                dados = extrair_dados_ia(img)

                if dados:
                    for item in dados:
                        item.update({
                            "loja": loja,
                            "tipo": "dia",
                            "pagamento": "Pix/Cartão"
                        })
                        st.session_state.db_promocoes.append(item)

                    st.success("Ofertas adicionadas!")
                    st.table(dados)
                else:
                    st.error("Erro na leitura")

    # Manual
    with tab2:
        with st.form("form"):
            p = st.text_input("Produto")
            preco = st.number_input("Preço", min_value=0.0)
            tipo = st.selectbox("Duração", ["dia", "semana", "mes"])
            pag = st.text_input("Pagamento")

            if st.form_submit_button("Salvar"):
                st.session_state.db_promocoes.append({
                    "produto": p,
                    "preco": preco,
                    "loja": loja,
                    "tipo": tipo,
                    "pagamento": pag
                })
                st.success("Salvo!")

# ==============================================================================
# 🏆 RANKING
# ==============================================================================
elif modo == "🏆 Ranking":
    st.title("🏆 Ranking")

    df = pd.DataFrame(st.session_state.db_promocoes)

    if not df.empty:
        rank = df['loja'].value_counts().reset_index()
        rank.columns = ['Loja', 'Ofertas']
        st.table(rank)

# ==============================================================================
# 💰 PLANOS
# ==============================================================================
elif modo == "💰 Planos":
    st.title("💰 Planos")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Básico")
        st.write("R$ 49/mês")

    with c2:
        st.subheader("Pro")
        st.write("R$ 149/mês")

    with c3:
        st.subheader("Enterprise")
        st.write("R$ 399/mês")
