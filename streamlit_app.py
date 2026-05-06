import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import urllib.parse

# ==============================================================================
# CONFIGURAÇÕES INICIAIS
# ==============================================================================
st.set_page_config(page_title="SaaS Radar de Ofertas", layout="wide", page_icon="🛒")

# CONFIGURAÇÃO DA IA (Busca a chave nos Secrets do Streamlit Cloud)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("❌ Erro: Configure a GOOGLE_API_KEY nos Secrets do Streamlit!")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Simulando Banco de Dados na memória do navegador
if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Feijão 1kg", "preco": 6.90, "loja": "Mercadinho Zé", "tipo": "semana", "pagamento": "Dinheiro"},
    ]

# URL DO SEU SITE (Substitua pelo link que o Streamlit te deu)
URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app" 

# ==============================================================================
# MENU LATERAL
# ==============================================================================
st.sidebar.title("🚀 Painel de Controle")
menu = st.sidebar.radio("Navegação:", ["🛒 Visão do Cliente", "📸 Leitor de Encartes (IA)", "🏆 Ranking de Lojas", "💰 Monetização"])

# ==============================================================================
# PÁGINA 1: VISÃO DO CLIENTE + DIVULGAÇÃO WHATSAPP
# ==============================================================================
if menu == "🛒 Visão do Cliente":
    st.title("🛒 Radar de Ofertas da Comunidade")
    st.markdown("Encontre os melhores preços e compartilhe com a galera!")

    # Barra de Busca e Filtros
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Buscar produto (ex: Arroz, Leite, Carne)...")
    with col_filter:
        tab = st.selectbox("Período", ["dia", "semana", "mes"])

    df = pd.DataFrame(st.session_state.db_promocoes)
    
    if not df.empty:
        # Filtragem
        filtered_df = df[(df['tipo'] == tab) & (df['produto'].str.contains(search, case=False))]
        
        if filtered_df.empty:
            st.info("Nenhuma oferta encontrada para esses filtros.")
        else:
            # Exibição dos Cards
            for index, row in filtered_df.iterrows():
                # --- LÓGICA DO WHATSAPP (NÍVEL 1) ---
                mensagem = (
                    f"🔥 *OFERTA IMPERDÍVEL!* 🔥\n\n"
                    f"📦 *Produto:* {row['produto']}\n"
                    f"💰 *Preço:* R$ {row['preco']:.2f}\n"
                    f"🛒 *Loja:* {row['loja']}\n"
                    f"💳 *Pagamento:* {row['pagamento']}\n\n"
                    f"👇 Veja todas as ofertas aqui:\n{URL_SISTEMA}"
                )
                texto_url = urllib.parse.quote(mensagem)
                link_whatsapp = f"https://wa.me/?text={texto_url}"

                # Card Visual
                st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); color: black;">
                    <small style="color: gray; font-weight: bold;">{row['loja'].upper()}</small><br>
                    <strong style="font-size: 20px;">{row['produto']}</strong><br>
                    <span style="font-size: 26px; color: #16a34a; font-weight: bold;">R$ {row['preco']:.2f}</span> 
                    <span style="font-size: 14px; color: gray;">({row['pagamento']})</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Botão de ação rápida
                st.link_button("📢 Enviar Oferta no Grupo do Whats", link_whatsapp, use_container_width=True)
                st.divider()
    else:
        st.warning("O sistema está vazio. Use o Leitor de IA para adicionar ofertas!")

# ==============================================================================
# PÁGINA 2: LEITOR de ENCARTES (IA)
# ==============================================================================
elif menu == "📸 Leitor de Encartes (IA)":
    st.title("📸 Extrator Automático de Ofertas")
    st.info("Suba a foto do encarte e a IA cadastrará tudo no sistema automaticamente.")

    uploaded_file = st.file_uploader("Escolha a foto do encarte", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Encarte Analisado", width=400)
        
        if st.button("🚀 Processar com IA"):
            with st.spinner("A IA está lendo os preços..."):
                try:
                    prompt = "Extraia as promoções desta imagem. Retorne APENAS um JSON no formato: [{\"produto\": \"nome\", \"preco\": 0.00, \"unidade\": \"kg\", \"validade\": \"data\"}]"
                    response = model.generate_content([prompt, image])
                    json_string = response.text.replace('```json', '').replace('```', '').strip()
                    dados_novos = json.loads(json_string)
                    
                    # Adicionando ao Banco de Dados
                    for item in dados_novos:
                        item['loja'] = "Nova Loja (IA)" # Aqui você pode criar um campo para escolher a loja
                        item['tipo'] = "dia"
                        item['pagamento'] = "Pix/Cartão"
                        st.session_state.db_promocoes.append(item)
                    
                    st.success(f"✅ {len(dados_novos)} produtos cadastrados com sucesso!")
                    st.table(dados_novos)
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

# ==============================================================================
# PÁGINA 3: RANKING
# ==============================================================================
elif menu == "🏆 Ranking de Lojas":
    st.title("🏆 Ranking de Supermercados")
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        rank = df['loja'].value_counts().reset_index()
        rank.columns = ['Supermercado', 'Quantidade de Ofertas']
        st.table(rank)
        st.info("💡 Dica: Lojas com mais ofertas ganham mais visibilidade no app!")
    else:
        st.write("Sem dados para gerar ranking.")

# ==============================================================================
# PÁGINA 4: MONETIZAÇÃO
# ==============================================================================
elif menu == "💰 Monetização":
    st.title("💰 Modelo de Negócio SaaS")
    st.markdown("""
    ### 📈 Como faturar com este sistema:
    
    **1. Plano Básico (R$ 49/mês):**
       - Lojista pode cadastrar ofertas manualmente.
       
    **2. Plano Pro (R$ 149/mês):**
       - **Uso do Leitor de IA de Encartes (Automatizado).**
       - Destaque no topo do ranking.
       
    **3. Plano Enterprise (R$ 399/mês):**
       - Relatórios de quais produtos são mais buscados.
       - Gestão de cupons de desconto.
    """)
