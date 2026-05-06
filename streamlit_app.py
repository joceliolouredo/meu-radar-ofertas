import streamlit as st
import pandas as pd
import urllib.parse
import random

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE ELITE & DESIGN
# ==============================================================================
st.set_page_config(page_title="SuperRadar Social", layout="wide", page_icon="🏆")

# CSS Profissional para transformar o site em um App de Comunidade
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #16a34a; color: white; font-weight: bold; border: none; }
    .offer-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 8px solid #16a34a; margin-bottom: 15px; box-shadow: 2px 2px 15px rgba(0,0,0,0.1); color: black; }
    .best-price-badge { background-color: #ffd700; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; display: inline-block; margin-bottom: 10px; }
    .marquee { background: #16a34a; color: white; padding: 10px; font-weight: bold; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

URL_SISTEMA = "https://meu-radar-ofertas.streamlit.app"

# ==============================================================================
# 🗄️ BANCO DE DADOS SOCIAL (Lógica de Curtidas e Votos)
# ==============================================================================
if 'db_promocoes' not in st.session_state:
    # Adicionamos a coluna 'curtidas' para criar o ranking social
    st.session_state.db_promocoes = [
        {"produto": "Arroz 5kg", "preco": 21.50, "loja": "Super Hiper", "tipo": "dia", "pagamento": "Pix", "curtidas": 150},
        {"produto": "Feijão 1kg", "preco": 6.90, "loja": "Mercadinho Zé", "tipo": "semana", "pagamento": "Dinheiro", "curtidas": 80},
        {"produto": "Leite 1L", "preco": 4.10, "loja": "EcoPreço", "tipo": "dia", "pagamento": "Cartão", "curtidas": 210},
    ]

# ==============================================================================
# 📱 INTERFACE E NAVEGAÇÃO
# ==============================================================================
st.sidebar.title("💎 SuperRadar Social")
st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Acesse o Painel:", ["👥 Comunidade", "🔍 Comparador", "🏪 Lojista", "🏆 Ranking Social", "💰 Planos"])

# ------------------------------------------------------------------------------
# MÓDULO 1: VISÃO DA COMUNIDADE (SISTEMA DE VITRINE)
# ------------------------------------------------------------------------------
if app_mode == "👥 Comunidade":
    st.title("🛒 Radar de Ofertas")
    
    # --- TARJA DE MELHORES DA SEMANA (MARQUEE) ---
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        melhores = df.sort_values(by='curtidas', ascending=False).head(3)
        texto_marquee = " 🔥 MELHORES DA SEMANA: " + " | ".join([f"{row['produto']} - R${row['preco']:.2f} em {row['loja']}" for _, row in melhores.iterrows()]) + " 🔥 "
        st.markdown(f'<div class="marquee"><marquee>{texto_marquee}</marquee></div>', unsafe_allow_html=True)

    # Filtros
    c1, c2 = st.columns([3, 1])
    with c1: busca = st.text_input("🔍 Buscar produto...")
    with c2: tab = st.selectbox("Período", ["dia", "semana", "mes"])

    # Ordenação: Primeiro as mais curtidas (Vitrine)
    df_sorted = df.sort_values(by='curtidas', ascending=False)
    
    if not df.empty:
        res = df_sorted[(df_sorted['tipo'] == tab) & (df_sorted['produto'].str.contains(busca, case=False))]
        
        for index, row in res.iterrows():
            # Badge de "Mais Curtido"
            badge = '<div class="best-price-badge">⭐ MAIS CURTIDO</div>' if row['curtidas'] > 100 else ""
            
            msg = f"🔥 *OFERTA!* 🔥\n\n📦 {row['produto']}\n💰 R$ {row['preco']:.2f}\n🛒 {row['loja']}\n\n👇 {URL_SISTEMA}"
            link_whats = f"https://wa.me/?text={urllib.parse.quote(msg)}"
            
            st.markdown(f"""<div class="offer-card">
                {badge}
                <small style="color: gray;">{row['loja'].upper()}</small><br>
                <strong style="font-size: 20px;">{row['produto']}</strong><br>
                <span style="font-size: 24px; color: #16a34a; font-weight: bold;">R$ {row['preco']:.2f}</span>
                <span style="font-size: 12px; color: gray;">({row['pagamento']})</span>
                <div style="margin-top:10px; color: #e11d48; font-weight: bold;">❤️ {row['curtidas']} curtidas</div>
                </div>""", unsafe_allow_html=True)
            
            # BOTÃO DE CURTIR (Lógica de Voto)
            if st.button(f"❤️ Curtir {row['produto']}", key=f"like_{index}"):
                st.session_state.db_promocoes[index]['curtidas'] += 1
                st.rerun()
            
            st.link_button("📢 Divulgar no WhatsApp", link_whats, use_container_width=True)
            st.divider()

# ------------------------------------------------------------------------------
# MÓDULO 2: COMPARADOR E GRÁFICOS
# ------------------------------------------------------------------------------
elif app_mode == "🔍 Comparador":
    st.title("🔍 Análise de Economia")
    prod_busca = st.text_input("Produto para comparar (ex: Arroz)")
    
    if prod_busca:
        df = pd.DataFrame(st.session_state.db_promocoes)
        comp = df[df['produto'].str.contains(prod_busca, case=False)].sort_values(by='preco')
        
        if not comp.empty:
            st.markdown(f'<div class="best-price-box">🏆 O MELHOR PREÇO ESTÁ EM: {comp.iloc[0]["loja"]} - R$ {comp.iloc[0]["preco"]:.2f}</div>', unsafe_allow_html=True)
            
            # GRÁFICO DE ECONOMIA
            st.write("### 📊 Comparativo de Preços")
            st.bar_chart(data=comp.set_index('loja')['preco'])
            st.table(comp[['loja', 'preco', 'pagamento']])
        else:
            st.warning("Produto não encontrado.")

# ------------------------------------------------------------------------------
# MÓDULO 3: PAINEL DO LOJISTA
# ------------------------------------------------------------------------------
elif app_mode == "🏪 Lojista":
    st.title("🏪 Gestão de Ofertas")
    loja_nome = st.text_input("Nome do seu Supermercado", value="Minha Loja")
    
    with st.form("form_oferta"):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1: prod = st.text_input("Produto")
        with col2: preco = st.number_input("Preço", min_value=0.0)
        with col3: pag = st.text_input("Pagamento", value="Pix")
        tipo = st.selectbox("Duração", ["dia", "semana", "mes"])
        
        if st.form_submit_button("✅ Publicar Oferta"):
            if prod and preco > 0:
                st.session_state.db_promocoes.append({"produto": prod, "preco": preco, "loja": loja_nome, "tipo": tipo, "pagamento": pag, "curtidas": 0})
                st.success("Oferta publicada na vitrine!")

# ------------------------------------------------------------------------------
# MÓDULO 4: RANKING SOCIAL (SISTEMA DE ESTRELAS)
# ------------------------------------------------------------------------------
elif app_mode == "🏆 Ranking Social":
    st.title("🏆 Ranking dos Mais Amados")
    st.markdown("Lojas com as ofertas mais curtidas pela comunidade.")
    
    df = pd.DataFrame(st.session_state.db_promocoes)
    if not df.empty:
        # Soma todas as curtidas de cada loja
        rank = df.groupby('loja')['curtidas'].sum().sort_values(ascending=False).reset_index()
        rank.columns = ['Supermercado', 'Total de Curtidas']
        
        # Exibição com Medalhas
        for i, row in rank.iterrows():
            medalha = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "⭐"
            st.markdown(f"### {medalha} {row['Supermercado']} - {row['Total de Curtidas']} ❤️")
            st.progress(int(row['Total de Curtidas'] / max(rank['Total de Curtidas']) * 100) / 100)
        
        st.table(rank)
    else:
        st.write("Ainda não há votos.")

elif app_mode == "💰 Planos":
    st.title("💰 Planos para Lojistas")
    st.markdown("SaaS Profissional: Básico R$ 49 | Pro R$ 149 | Enterprise R$ 399")
