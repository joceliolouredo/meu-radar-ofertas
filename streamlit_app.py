import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import urllib.parse

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE ELITE (UI/UX)
# ==============================================================================
st.set_page_config(page_title="SuperRadar SaaS", layout="wide", page_icon="💰")

# CSS para transformar a página em um Aplicativo Profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #16a34a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #12853c; color: white; }
    .offer-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); color: black; }
    .best-price-box { background-color: #dcfce7; border: 2px solid #16a34a; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; color: #16a34a; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# SEGURANÇA: Busca a chave no cofre de Secrets
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("❌ API KEY não configurada nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=API_KEY)

# MODELO ULTRA ESTÁVEL (Para evitar erro 404)
MODEL_NAME = 'gemini-pro' 

# URL do seu site (Lembre-se de trocar pelo seu link real do Streamlit)
URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

# BANCO DE DADOS EM SESSÃO
if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Arroz 5kg", "preco": 23.00, "loja": "Mercadinho Zé", "tipo": "dia", "pagamento": "Pix"},
    ]

# ==============================================================================
# 🧠 MOTOR DE IA COM LIMPEZA AVANÇADA DE JSON
# ==============================================================================
def processar_texto_ia(texto_ofertas):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
        Você é um extrator de dados de supermercado. Transforme a lista abaixo em JSON.
        REGRAS:
        1. Retorne APENAS o JSON. Não escreva frases como 'Aqui está o resultado'.
        2. Formato: [ {{"produto": "nome", "preco": 0.00}} ]
        3. Use ponto para decimais (Ex: 10.50).
        TEXTO: {texto_ofertas}
        """
        response = model.generate_content(prompt)
        texto_bruto = response.text.strip()
        
        # LIMPEZA AVANÇADA: Localiza o início [ e o fim ] do JSON para ignorar conversas da IA
        if "[" in texto_bruto and "]" in texto_bruto:
            inicio = texto_bruto.find("[")
            fim = texto_bruto.rfind("]") + 1
            json_limpo = texto_bruto[inicio:fim]
            return json.loads(json_limpo)
        return None
    except Exception as e:
        st.error(f"Erro técnico na IA: {e}")
        return None

# ==============================================================================
# 📱 INTERFACE DO SISTEMA
# ==============================================================================
st.sidebar.title("💎 SuperRadar SaaS")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Acesse o Painel:", ["👥 Visão da Comunidade", "🔍 Comparador de Preços", "🏪 Painel do Lojista", "🏆 Ranking Global", "💰 Planos"])

# ------------------------------------------------------------------------------
# MÓDULO 1: VISÃO DA COMUNIDADE
# ------------------------------------------------------------------------------
if app_mode == "👥 Visão da Comunidade":
    st.title("🛒 Ofertas da Comunidade")
    st.markdown("As melhores promoções da região em tempo real.")

    col1, col2 = st.columns([3, 1])
    with col1:
        busca = st.text_input("🔍 Qual produto você procura?")
    with col2:
        filtro_tempo = st.selectbox("Período", ["dia", "semana", "mes"])

    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        res = df[(df['tipo'] == filtro_tempo) & (df['produto'].str.contains(busca, case=False))]
        if res.empty:
            st.info("Nenhuma oferta encontrada.")
        else:
            for _, row in res.iterrows():
                msg = f"🔥 *OFERTA!* 🔥\n\n📦 {row['produto']}\n💰 R$ {row['preco']:.2f}\n🛒 {row['loja']}\n\n👇 {URL_SISTEMA}"
                link_whats = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f"""<div class="offer-card">
                    <small style="color: gray;">{row['loja'].upper()}</small><br>
                    <strong style="font-size: 20px;">{row['produto']}</strong><br>
                    <span style="font-size: 24px; color: #16a34a; font-weight: bold;">R$ {row['preco']:.2f}</span>
                    <span style="font-size: 12px; color: gray;">({row['pagamento']})</span>
                    </div>""", unsafe_allow_html=True)
                st.link_button("📢 Divulgar no WhatsApp", link_whats, use_container_width=True)
                st.divider()

# ------------------------------------------------------------------------------
# MÓDULO 2: COMPARADOR de PREÇOS
# ------------------------------------------------------------------------------
elif app_mode == "🔍 Comparador de Preços":
    st.title("🔍 Quem tem o melhor preço?")
    prod_busca = st.text_input("Digite o produto para comparar (ex: Arroz)")
    
    if prod_busca:
        df = pd.DataFrame(st.session_state.db_promocoes)
        comparativo = df[df['produto'].str.contains(prod_busca, case=False)].sort_values(by='preco')
        
        if not comparativo.empty:
            vencedor = comparativo.iloc[0]
            st.markdown(f"""<div class="best-price-box">
                🏆 O MELHOR PREÇO DE {prod_busca.upper()} ESTÁ NO: <br>
                <span style="font-size: 22px;">{vencedor['loja']} - R$ {vencedor['preco']:.2f}</span>
                </div>""", unsafe_allow_html=True)
            st.table(comparativo[['loja', 'preco', 'pagamento']])
        else:
            st.warning("Nenhum mercado cadastrou este produto.")

# ------------------------------------------------------------------------------
# MÓDULO 3: PAINEL DO LOJISTA
# ------------------------------------------------------------------------------
elif app_mode == "🏪 Painel do Lojista":
    st.title("🏪 Painel do Supermercado")
    loja_nome = st.text_input("Nome do seu Supermercado", value="Minha Loja")
    
    st.subheader("🤖 Cadastro Inteligente")
    st.write("Cole a lista de ofertas (Ex: Arroz 5kg 22.90, Feijão 6.50...)")
    texto_input = st.text_area("Cole as ofertas aqui...", height=150)
    
    if st.button("🚀 Transformar Texto em Cards"):
        if texto_input:
            with st.spinner("IA organizando as ofertas..."):
                dados = processar_texto_ia(texto_input)
                if dados:
                    for item in dados:
                        item.update({'loja': loja_nome, 'tipo': 'dia', 'pagamento': 'Pix/Cartão'})
                        st.session_state.db_promocoes.append(item)
                    st.success(f"✅ {len(dados)} ofertas cadastradas!")
                    st.table(dados)
                else:
                    st.error("A IA não conseguiu processar. Tente escrever: 'Produto Preço' (ex: Arroz 22.90)")
        else:
            st.warning("Por favor, cole algum texto.")

# ------------------------------------------------------------------------------
# MÓDULO 4: RANKING E PLANOS
# ------------------------------------------------------------------------------
elif app_mode == "🏆 Ranking Global":
    st.title("🏆 Ranking de Economia")
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        rank = df['loja'].value_counts().reset_index()
        rank.columns = ['Supermercado', 'Quantidade de Ofertas']
        st.table(rank)
    else:
        st.write("Sem dados disponíveis.")

elif app_mode == "💰 Planos":
    st.title("💰 Planos para Lojistas")
    st.markdown("SaaS Profissional para Supermercados.\n\n- **Básico:** R$ 49/mês\n- **Pro:** R$ 149/mês\n- **Enterprise:** R$ 399/mês")
