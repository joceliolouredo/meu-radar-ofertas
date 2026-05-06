import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import urllib.parse

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE ELITE
# ==============================================================================
st.set_page_config(page_title="SuperRadar SaaS", layout="wide", page_icon="💰")

# Estilização CSS para parecer um App Profissional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #16a34a; color: white; font-weight: bold; }
    .offer-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); color: black; }
    </style>
    """, unsafe_allow_html=True)

# SEGURANÇA DOS SECRETS
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("❌ API KEY não configurada nos Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

# URL do seu sistema (Troque pelo seu link real)
URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

# BANCO DE DADOS EM SESSÃO (SaaS Mode)
if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Feijão 1kg", "preco": 6.90, "loja": "Mercadinho Zé", "tipo": "semana", "pagamento": "Dinheiro"},
    ]

# ==============================================================================
# 🧠 MOTOR DE IA (COM AUTO-CORREÇÃO DE MODELO)
# ==============================================================================
def extrair_dados_ia(imagem):
    # Lista de modelos do mais moderno para o mais estável
    modelos_tentativa = ['gemini-1.5-flash-latest', 'gemini-pro-vision', 'gemini-1.5-pro']
    
    for modelo_nome in modelos_tentativa:
        try:
            model = genai.GenerativeModel(modelo_nome)
            prompt = "Analise este encarte de supermercado. Extraia as ofertas. Retorne APENAS um JSON: [{\"produto\": \"nome\", \"preco\": 0.00, \"unidade\": \"kg/un\"}]"
            response = model.generate_content([prompt, imagem])
            
            # Limpeza de JSON
            texto = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto), modelo_nome
        except Exception as e:
            continue # Se deu erro 404 ou qualquer outro, tenta o próximo modelo da lista
    
    return None, None

# ==============================================================================
# 📱 INTERFACE DO USUÁRIO (UI)
# ==============================================================================
st.sidebar.title("💎 SuperRadar SaaS")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Acesse o Painel:", ["👥 Visão da Comunidade", "🏪 Painel do Lojista", "🏆 Ranking Global", "💰 Planos e Preços"])

# ------------------------------------------------------------------------------
# MÓDULO 1: VISÃO DA COMUNIDADE (B2C)
# ------------------------------------------------------------------------------
if app_mode == "👥 Visão da Comunidade":
    st.title("🛒 Ofertas da Comunidade")
    st.markdown("As melhores promoções da região em tempo real.")

    # Filtros Profissionais
    c1, c2 = st.columns([3, 1])
    with c1:
        busca = st.text_input("🔍 Qual produto você procura?")
    with c2:
        filtro_tempo = st.selectbox("Período", ["dia", "semana", "mes"])

    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        res = df[(df['tipo'] == filtro_tempo) & (df['produto'].str.contains(busca, case=False))]
        if res.empty:
            st.info("Nenhuma oferta encontrada no momento.")
        else:
            for _, row in res.iterrows():
                msg = f"🔥 *OFERTA!* 🔥\n\n📦 {row['produto']}\n💰 R$ {row['preco']:.2f}\n🛒 {row['loja']}\n\n👇 Veja mais:\n{URL_SISTEMA}"
                link_whats = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                
                st.markdown(f"""
                <div class="offer-card">
                    <small style="color: gray;">{row['loja'].upper()}</small><br>
                    <strong style="font-size: 20px;">{row['produto']}</strong><br>
                    <span style="font-size: 24px; color: #16a34a; font-weight: bold;">R$ {row['preco']:.2f}</span>
                    <span style="font-size: 12px; color: gray;">({row['pagamento']})</span>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("📢 Divulgar no WhatsApp", link_whats, use_container_width=True)
                st.divider()

# ------------------------------------------------------------------------------
# MÓDULO 2: PAINEL DO LOJISTA (B2B)
# ------------------------------------------------------------------------------
elif app_mode == "🏪 Painel do Lojista":
    st.title("🏪 Painel do Supermercado")
    st.markdown("Cadastre suas ofertas e suba no ranking de economia!")

    # Cadastro de Loja
    loja_nome = st.text_input("Nome do Supermercado", value="Minha Loja")
    
    tab_cad = st.tabs(["📸 Upload de Encarte (IA)", "✍️ Cadastro Manual"])
    
    with tab_cad[0]:
        st.subheader("Automação com IA")
        foto = st.file_uploader("Suba a foto do encarte", type=["jpg", "png", "jpeg"])
        if foto:
            img = Image.open(foto)
            st.image(img, width=300)
            if st.button("🚀 Processar Encarte"):
                with st.spinner("IA analisando preços..."):
                    dados, modelo_usado = extrair_dados_ia(img)
                    if dados:
                        for item in dados:
                            item.update({'loja': loja_nome, 'tipo': 'dia', 'pagamento': 'Pix/Cartão'})
                            st.session_state.db_promocoes.append(item)
                        st.success(f"✅ {len(dados)} ofertas extraídas com {modelo_usado}!")
                        st.table(dados)
                    else:
                        st.error("A IA não conseguiu ler este encarte. Tente uma foto mais nítida.")

    with tab_cad[1]:
        st.subheader("Cadastro Manual")
        with st.form("form_manual"):
            p_nome = st.text_input("Produto")
            p_preco = st.number_input("Preço", min_value=0.0)
            p_tipo = st.selectbox("Duração", ["dia", "semana", "mes"])
            p_pag = st.text_input("Forma de Pagamento (ex: Pix, Cartão)")
            if st.form_submit_button("Salvar Oferta"):
                st.session_state.db_promocoes.append({"produto": p_nome, "preco": p_preco, "loja": loja_nome, "tipo": p_tipo, "pagamento": p_pag})
                st.success("Oferta salva!")

# ------------------------------------------------------------------------------
# MÓDULO 3: RANKING GLOBAL
# ------------------------------------------------------------------------------
elif app_mode == "🏆 Ranking Global":
    st.title("🏆 Ranking de Economia")
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        rank = df['loja'].value_counts().reset_index()
        rank.columns = ['Supermercado', 'Qtd de Ofertas']
        st.markdown("Lojas com mais ofertas ganham destaque no app!")
        st.table(rank)
    else:
        st.write("Ainda não há dados para o ranking.")

# ------------------------------------------------------------------------------
# MÓDULO 4: PLANOS E PREÇOS
# ------------------------------------------------------------------------------
elif app_mode == "💰 Planos e Preços":
    st.title("💰 Planos para Lojistas")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Básico")
        st.write("R$ 49/mês")
        st.write("- Cadastro Manual\n- Ranking Básico")
    with c2:
        st.subheader("Pro")
        st.write("R$ 149/mês")
        st.write("- **Leitor de IA**\n- Destaque no Ranking\n- Selo de Confiança")
    with c3:
        st.subheader("Enterprise")
        st.write("R$ 399/mês")
        st.write("- Relatórios de Busca\n- Gestão de Cupons\n- Suporte VIP")
