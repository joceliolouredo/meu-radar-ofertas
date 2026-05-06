import streamlit as st
import pandas as pd
import urllib.parse

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE ELITE
# ==============================================================================
st.set_page_config(page_title="SuperRadar - Comparador de Preços", layout="wide", page_icon="💰")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #16a34a; color: white; font-weight: bold; }
    .offer-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.05); color: black; }
    .best-price { background-color: #dcfce7; border: 2px solid #16a34a; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; color: #16a34a; }
    </style>
    """, unsafe_allow_html=True)

# URL do seu sistema
URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

# BANCO DE DADOS EM SESSÃO (SaaS Mode)
if 'db_promocoes' not in st.session_state:
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 25.00, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Mercadinho Zé", "tipo": "dia", "pagamento": "Pix"},
        {"produto": "Feijão 1kg", "preco": 6.90, "loja": "Super Hiper", "tipo": "semana", "pagamento": "Dinheiro"},
        {"produto": "Feijão 1kg", "preco": 7.50, "loja": "Mercadinho Zé", "tipo": "semana", "pagamento": "Dinheiro"},
    ]

# ==============================================================================
# 📱 INTERFACE
# ==============================================================================
st.sidebar.title("💎 SuperRadar SaaS")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Acesse o Painel:", ["👥 Visão da Comunidade", "🔍 Comparador de Preços", "🏪 Painel do Lojista", "🏆 Ranking Global", "💰 Planos"])

# ------------------------------------------------------------------------------
# MÓDULO 1: VISÃO DA COMUNIDADE
# ------------------------------------------------------------------------------
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
        if res.empty:
            st.info("Nenhuma oferta encontrada.")
        else:
            for _, row in res.iterrows():
                msg = f"🔥 *OFERTA!* 🔥\n\n📦 {row['produto']}\n💰 R$ {row['preco']:.2f}\n🛒 {row['loja']}\n\n👇 Veja mais:\n{URL_SISTEMA}"
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
# MÓDULO 2: COMPARADOR DE PREÇOS (A FUNÇÃO MAIS VALIOSA)
# ------------------------------------------------------------------------------
elif app_mode == "🔍 Comparador de Preços":
    st.title("🔍 Quem tem o melhor preço?")
    st.markdown("Analisamos todos os mercados para você economizar.")

    produto_busca = st.text_input("Digite o nome do produto para comparar (ex: Arroz)")
    
    if produto_busca:
        df = pd.DataFrame(st.session_state.db_promocoes)
        # Filtra todos os mercados que tem esse produto
        comparativo = df[df['produto'].str.contains(produto_busca, case=False)].sort_values(by='preco')
        
        if not comparativo.empty:
            melhor_preco = comparativo.iloc[0]
            st.markdown(f"""<div class="best-price">
                🏆 O MELHOR PREÇO DE {produto_busca.upper()} ESTÁ NO: <br>
                <span style="font-size: 24px;">{melhor_preco['loja']} - R$ {melhor_preco['preco']:.2f}</span>
                </div>""", unsafe_allow_html=True)
            
            st.write("### Comparação detalhada:")
            st.table(comparativo[['loja', 'preco', 'pagamento']])
        else:
            st.warning("Nenhum mercado cadastrou esse produto até agora.")

# ------------------------------------------------------------------------------
# MÓDULO 3: PAINEL DO LOJISTA (CADASTRO SIMPLES)
# ------------------------------------------------------------------------------
elif app_mode == "🏪 Painel do Lojista":
    st.title("🏪 Painel do Supermercado")
    loja_nome = st.text_input("Nome do seu Supermercado", value="Minha Loja")
    
    st.subheader("✍️ Cadastro de Ofertas")
    st.write("Adicione seus produtos rapidamente abaixo.")
    
    with st.form("form_oferta"):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1: prod = st.text_input("Produto (ex: Arroz 5kg)")
        with col2: preco = st.number_input("Preço", min_value=0.0)
        with col3: pag = st.text_input("Pagamento", value="Pix")
        
        tipo = st.selectbox("Duração da Oferta", ["dia", "semana", "mes"])
        
        if st.form_submit_button("✅ Salvar Oferta"):
            if prod and preco > 0:
                st.session_state.db_promocoes.append({"produto": prod, "preco": preco, "loja": loja_nome, "tipo": tipo, "pagamento": pag})
                st.success(f"Oferta de {prod} salva com sucesso!")
            else:
                st.error("Preencha o nome do produto e o preço corretamente.")

# ------------------------------------------------------------------------------
# MÓDULO 4: RANKING GLOBAL
# ------------------------------------------------------------------------------
elif app_// la l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l
