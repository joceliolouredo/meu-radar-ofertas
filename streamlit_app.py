import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import urllib.parse

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE ELITE
# ==============================================================================
st.set_page_config(page_title="SuperRadar SaaS", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #16a34a; color: white; font-weight: bold; }
    .offer-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); color: black; }
    </style>
    """, unsafe_allow_html=True)

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("❌ API KEY não configurada nos Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

# Usando o modelo de texto mais rápido e estável
MODEL_NAME = 'gemini-1.5-flash' 

URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
    ]

# ==============================================================================
# 🧠 MOTOR de IA (TEXTO PARA JSON)
# ==============================================================================
def processar_texto_ia(texto_ofertas):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"""
        Você é um organizador de ofertas de supermercado.
        Transforme a seguinte lista de ofertas em um JSON estruturado.
        Texto: {texto_ofertas}
        
        Retorne APENAS o JSON no formato:
        [
          {{"produto": "nome do produto", "preco": 0.00, "unidade": "kg/un"}}
        ]
        Se não encontrar o preço, ignore o item. Não escreva nada além do JSON.
        """
        response = model.generate_content(prompt)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        st.error(f"Erro na IA: {e}")
        return None

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("💎 SuperRadar SaaS")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Acesse o Painel:", ["👥 Visão da Comunidade", "🏪 Painel do Lojista", "🏆 Ranking Global", "💰 Planos e Preços"])

if app_mode == "👥 Visão da Comunidade":
    st.title("🛒 Ofertas da Comunidade")
    c1, c2 = st.columns([3, 1])
    with c1:
        busca = st.text_input("🔍 Qual produto você procura?")
    with c2:
        filtro_tempo = st.selectbox("Período", ["dia", "semana", "mes"])

    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        res = df[(df['tipo'] == filtro_tempo) & (df['produto'].str.contains(busca, case=False))]
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

elif app_mode == "🏪 Painel do Lojista":
    st.title("🏪 Painel do Supermercado")
    loja_nome = st.text_input("Nome do Supermercado", value="Minha Loja")
    
    st.subheader("🤖 Cadastro Inteligente")
    st.write("Cole aqui a lista de ofertas (Ex: Arroz 5kg 22,90, Feijão 6,00...)")
    texto_input = st.text_area("Cole as ofertas aqui...", height=200)
    
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
            st.warning("Por favor, cole algum texto de ofertas.")

elif app_mode == "🏆 Ranking Global":
    st.title("🏆 Ranking de Economia")
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        rank = df['loja'].value_counts().reset_index()
        rank.columns = ['Supermercado', 'Qtd de Ofertas']
        st.table(rank)
    else:
        st.write("Sem dados.")

elif app_mode == "💰 Planos e Preços":
    st.title("💰 Planos para Lojistas")
    st.markdown("SaaS Profissional para Supermercados.\n\n- **Básico:** R$ 49/mês\n- **Pro:** R$ 149/mês\n- **Enterprise:** R$ 399/mês")
