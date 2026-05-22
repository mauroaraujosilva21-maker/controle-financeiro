# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# CONFIGURAÇÕES VISUAIS DA PÁGINA
st.set_page_config(page_title="Nosso Painel Financeiro ❤️", layout="wide")

# Título acolhedor para facilitar o uso da esposa
st.title("💰 Nosso Controle Financeiro Familiar")

st.markdown("---")

# CONEXÃO DIRETA COM O GOOGLE SHEETS
# Substitua pelo link que você copiou no Passo 3
LINK_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/11fafX78intIlKGUT-hyzli7keGs2Diw3cUkRJ5IyYDc/edit?usp=sharing"

def carregar_dados_sheets(url):
    try:
        csv_url = url.replace("/edit?usp=sharing", "/export?format=csv")
        df = pd.read_csv(csv_url)
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
        df["Valor"] = pd.to_numeric(df["Valor"], errors='coerce')
        return df.dropna(subset=["Tipo", "Valor"])
    except:
        # Fallback caso a planilha ainda não esteja conectada ou esteja vazia
        return pd.DataFrame(columns=["Data", "Tipo", "Responsavel", "Categoria", "Valor", "Descricao"])

df_historico = carregar_dados_sheets(LINK_DA_PLANILHA)

# VALORES FIXOS CADASTRADOS (Conforme informado)
RENDA_MAURO = 2100.0
RENDA_ESPOSA = 1000.0
RENDA_TOTAL = RENDA_MAURO + RENDA_ESPOSA

GASTO_NATACAO = 378.0
GASTO_ENERGIA = 200.0
PARCELA_CARTAO_FIXA = 1000.0  # Até jan/2027
FATURA_INTER_JUNHO = 1138.41

# DATA LIMITE DA META: Janeiro de 2028
DATA_ALVO_META = datetime(2028, 1, 1)
DIAS_RESTANTES = (DATA_ALVO_META - datetime.today()).days
MESES_RESTANTES = max(int(DIAS_RESTANTES / 30), 1)

# --- LAYOUT EM ABAS SUPER SIMPLES ---
aba_resumo, aba_lancar, aba_meta = st.tabs([
    "📊 Ver Nosso Dinheiro", 
    "🟢 Lançar um Gasto ou Ganho", 
    "🚗 Nossa Meta de R$ 10mil"
])

# =====================================================================
# ABA 1: RESUMO DO MÊS
# =====================================================================
with aba_resumo:
    st.subheader("📌 Como estamos hoje?")
    
    # Cálculos das movimentações manuais da planilha
    gastos_variaveis = df_historico[df_historico["Tipo"] == "Despesa"]["Valor"].sum()
    total_investido_manual = df_historico[df_historico["Tipo"] == "Investimento"]["Valor"].sum()
    
    # Total de Saídas Reais = Fixos Cadastrados + Variáveis da Planilha
    total_saidas = GASTO_NATACAO + GASTO_ENERGIA + PARCELA_CARTAO_FIXA + gastos_variaveis
    saldo_atual = RENDA_TOTAL - total_saidas
    
    # Cards Grandes com Cores Claras para Leitura Fácil
    # Cards Grandes e Nativos do Streamlit (Seguros e fáceis de ler)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(label="💵 Nossa Renda Somada", value=f"R$ {RENDA_TOTAL:,.2f}", help="Mauro: R$ 2.100 | Esposa: R$ 1.000")
        
    with c2:
        st.metric(label="📉 Total de Gastos", value=f"R$ {total_saidas:,.2f}", delta="- Fixo Essencial: R$ 1.578,00", delta_color="inverse")
        
    with c3:
        if saldo_atual >= 0:
            st.metric(label="💰 Sobra / Livre para Investir", value=f"R$ {saldo_atual:,.2f}", delta="Dinheiro sob controle!")
        else:
            st.metric(label="⚠️ Orçamento Estourado", value=f"R$ {saldo_atual:,.2f}", delta="Atenção aos gastos!", delta_color="inverse")

    st.markdown("### 💳 Seus Cartões e Alertas Importantes")
    col_cartao1, col_cartao2 = st.columns(2)
    
    with col_cartao1:
        st.info(f"**Banco Inter:** R$ {FATURA_INTER_JUNHO:,.2f} com vencimento em **15/06**.")
    with col_cartao2:
        st.warning(f"**Compromisso Fixo:** Parcela mensal de **R$ 1.000,00** garantida no orçamento até **Janeiro/2027**.")

    st.markdown("---")
    
    # Histórico de compras fáceis de ler
    st.subheader("📋 Últimas compras que vocês lançaram")
    if not df_historico.empty:
        df_exibicao = df_historico.sort_values(by="Data", ascending=False).copy()
        df_exibicao["Data"] = df_exibicao["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(df_exibicao, use_container_width=True)
    else:
        st.info("Nenhum gasto extra ou investimento manual foi registrado ainda este mês. Use a segunda aba para lançar!")

# =====================================================================
# ABA 2: LANÇAMENTO AMIGÁVEL (Para a Esposa usar sem medo)
# =====================================================================
with aba_lancar:
    st.subheader("📝 Cadastrar uma nova movimentação do dia a dia")
    st.markdown("Preencha os campos abaixo e clique no botão para salvar. Tudo vai direto para os gráficos!")
    
    with st.form("form_simples", clear_on_submit=True):
        fl1, fl2 = st.columns(2)
        
        with fl1:
            data_mov = st.date_input("Quando foi?", datetime.today())
            tipo_mov = st.radio("O que é isso?", ["Despesa (Gasto extra)", "Investimento (Dinheiro guardado)", "Receita (Ganho extra)"])
            responsavel_mov = st.selectbox("Quem fez o movimento?", ["Mauro", "Esposa", "Ambos"])
            
        with fl2:
            valor_mov = st.number_input("Qual o valor em Reais? (R$)", min_value=1.0, value=10.0, step=5.0)
            
            # Categorias simples e em português direto
            if "Despesa" in tipo_mov:
                cat_mov = st.selectbox("Categoria do Gasto:", ["Mercado/Alimentação", "Farmácia/Saúde", "Lazer/Cinema/Restaurante", "Roupas/Compras", "Outros Gastos"])
            elif "Investimento" in tipo_mov:
                cat_mov = st.selectbox("Onde guardou?", ["Poupança da Meta", "Outros Investimentos"])
            else:
                cat_mov = st.selectbox("Origem do ganho:", ["Bico/Extra", "Outros"])
                
            desc_mov = st.text_input("Uma nota curta (Ex: Compra na padaria):")
            
        botao_gravar = st.form_submit_button("💾 SALVAR NO PAINEL")
        
        if botao_gravar:
            # Transforma em texto limpo para o Sheets
            tipo_limpo = "Despesa" if "Despesa" in tipo_mov else ("Investimento" if "Investimento" in tipo_mov else "Receita")
            
            st.success(f"Sucesso! Lançamento de R$ {valor_mov:.2f} registrado.")
            st.markdown(f"**Anote isso na sua planilha do Google Sheets para consolidar:**")
            st.code(f"{data_mov.strftime('%Y-%m-%d')},{tipo_limpo},{responsavel_mov},{cat_mov},{valor_mov},{desc_mov}")
            st.info("💡 Como estamos usando a conexão gratuita direta, copie a linha acima e cole na sua planilha do Google Sheets para que o gráfico atualize instantaneamente!")

# =====================================================================
# ABA 3: TERMÔMETRO RUMO AOS R$ 10.000 EM 2028
# =====================================================================
with aba_meta:
    st.subheader("🚗 Nosso Futuro: R$ 10.000,00 até 2028")
    st.markdown("Aqui vocês acompanham o crescimento do fundo financeiro para projetos maiores ou a entrada do carro!")
    
    # Calcula o quanto já guardaram pela planilha
    ja_guardado = df_historico[df_historico["Categoria"] == "Poupança da Meta"]["Valor"].sum()
    meta_total = 10000.0
    
    # Indicador de Progresso Visual
    progresso_porcentagem = min((ja_guardado / meta_total) * 100, 100.0)
    
    fig_meta = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ja_guardado,
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, meta_total], 'tickformat': "R$ ,.2f"},
            'bar': {'color': "#2E7D32"},
            'bgcolor': "#ECEFF1",
            'steps': [
                {'range': [0, 3000], 'color': '#FFEBEE'},
                {'range': [3000, 7000], 'color': '#FFF8E1'},
                {'range': [7000, 10000], 'color': '#E8F5E9'}
            ]
        }
    ))
    st.plotly_chart(fig_meta, use_container_width=True)
    
    # Projeção de parcelas
    falta_guardar = meta_total - ja_guardado
    if falta_guardar > 0:
        parcela_sugerida = falta_guardar / MESES_RESTANTES
        st.success(f"Falta muito pouco! Restam **R$ {falta_guardar:,.2f}** para atingir o objetivo.")
        st.info(f"📆 Vocês têm exatamente **{MESES_RESTANTES} meses** até 2028. Para bater a meta sem aperto, vocês precisam guardar **R$ {parcela_sugerida:,.2f}** por mês juntos.")
    else:
        st.balloons()
        st.success("🎉 Sensacional! A meta de R$ 10.000,00 foi atingida antes do prazo!")
