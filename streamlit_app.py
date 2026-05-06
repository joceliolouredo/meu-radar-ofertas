import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE DESIGN DARK & PREMIUM
# ==============================================================================
st.set_page_config(page_title="Radar Encarte Pro", layout="wide", page_icon="📈")

# CSS Customizado para Tema Dark Profissional
st.markdown("""
    <style>
    /* Estilização Geral Dark */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Cartões de Oferta Dark */
    .offer-card {
        background-color: #1d232d;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #343a40;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .offer-card:hover { border-color: #16a34a; transform: translateY(-5px); }
    
    /* Badges e Textos */
    .price-tag { font-size: 28px; color: #10b981; font-weight: 800; }
    .loja-tag { color: #94a3b8; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
    .best-price-badge {
        background: linear-gradient(90deg, #f59e0b, #d97706);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: bold;
    }
    
    /* Botões */
    .stButton>button {
        border-radius: 8px;
        background-color: #16a34a;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #15803d; border-color: #15803d; }
    
    /* Estilo para Inputs */
    input { background-color: #1d232d !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 🗄️ PERSISTÊNCIA DE DADOS (SIMULADA COM SESSION STATE)
# ==============================================================================
# Para salvar "de verdade", você substituiria st.session_state por uma API de DB.
if 'db_encartes' not in st.session_state:
    st.session_state.db_encartes = [
        {"id": 1, "produto": "Cerveja Heineken 330ml", "preco": 6.49, "loja": "Mercado Central", "data": "2026-05-06", "curtidas": 45},
        {"id": 2, "produto": "Picanha Argentina kg", "preco": 89.90, "loja": "Carnes Nobres", "data": "2026-05-06", "curtidas": 120},
        {"id": 3, "produto": "Leite Integral 1L", "preco": 4.29, "loja": "Vila Nova", "data": "2026-05-06", "curtidas": 30},
    ]

if 'usuario_loja' not in st.session_state:
    st.session_state.usuario_loja = "Lojista Master"

# ==============================================================================
# 📱 NAVEGAÇÃO LATERAL
# ==============================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1162/1162499.png", width=100)
st.sidebar.title("Radar SaaS")
menu = st.sidebar.radio("Navegação", ["Dashboard Social", "Enviar Encarte", "Análise de Concorrência", "Meu Perfil"])

# ==============================================================================
# MÓDULO 1: DASHBOARD SOCIAL (VISUALIZAÇÃO & VOTAÇÃO)
# ==============================================================================
if menu == "Dashboard Social":
    st.title("🚀 Inteligência de Mercado")
    st.subheader("Veja os preços que estão dominando a região e vote nos melhores")

    col_a, col_b = st.columns([3, 1])
    busca = col_a.text_input("Filtrar por produto ou concorrente...")
    
    df = pd.DataFrame(st.session_state.db_encartes).sort_values(by="curtidas", ascending=False)
    
    if not df.empty:
        # Filtro de Busca
        res = df[df['produto'].str.contains(busca, case=False)] if busca else df
        
        for index, row in res.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="offer-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span class="loja-tag">{row['loja']}</span>
                        {f'<span class="best-price-badge">🔥 TENDÊNCIA</span>' if row['curtidas'] > 50 else ''}
                    </div>
                    <div style="margin-top: 10px;">
                        <span style="font-size: 20px; font-weight: 500;">{row['produto']}</span><br>
                        <span class="price-tag">R$ {row['preco']:.2f}</span>
                    </div>
                    <div style="color: #ef4444; margin-top: 10px; font-weight: bold;">
                        ❤️ {row['curtidas']} votos da comunidade
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 4])
                if c1.button(f"👍 Votar", key=f"vote_{row['id']}"):
                    # Lógica para incrementar curtida no banco
                    idx_original = next(i for i, item in enumerate(st.session_state.db_encartes) if item["id"] == row['id'])
                    st.session_state.db_encartes[idx_original]['curtidas'] += 1
                    st.rerun()
                st.divider()

# ==============================================================================
# MÓDULO 2: ENVIO DE ENCARTE (SALVAMENTO)
# ==============================================================================
elif menu == "Enviar Encarte":
    st.title("📤 Publicar Novo Encarte")
    st.info("As ofertas publicadas aqui ficarão visíveis para a análise da comunidade de lojistas.")
    
    with st.form("upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_prod = st.text_input("Nome do Produto")
            preco_prod = st.number_input("Preço de Venda (R$)", min_value=0.01)
        with col2:
            categoria = st.selectbox("Categoria", ["Açougue", "Bebidas", "Higiene", "Hortifruti", "Padaria"])
            data_validade = st.date_input("Válido até")
        
        submit = st.form_submit_button("🚀 PUBLICAR NO RADAR")
        
        if submit:
            novo_id = len(st.session_state.db_encartes) + 1
            nova_oferta = {
                "id": novo_id,
                "produto": nome_prod,
                "preco": preco_prod,
                "loja": st.session_state.usuario_loja,
                "data": str(data_validade),
                "curtidas": 0
            }
            st.session_state.db_encartes.append(nova_oferta)
            st.success(f"Sucesso! O produto {nome_prod} já está disponível para votação.")

# ==============================================================================
# MÓDULO 3: ANÁLISE DE CONCORRÊNCIA
# ==============================================================================
elif menu == "Análise de Concorrência":
    st.title("📊 Comparativo de Performance")
    
    df = pd.DataFrame(st.session_state.db_encartes)
    if not df.empty:
        st.write("### Ranking de Preços mais Atrativos (Votos)")
        chart_data = df.groupby("loja")["curtidas"].sum().sort_values(ascending=False)
        st.bar_chart(chart_data)
        
        st.write("### Tabela Detalhada")
        st.dataframe(df, use_container_width=True)

# Footer Profissional
st.sidebar.markdown("---")
st.sidebar.caption("Radar Encarte SaaS v2.0 - 2026")
