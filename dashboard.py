import streamlit as st
import pandas as pd
import plotly.express as px
from database import listar_faturas, deletar_fatura, buscar_fatura_por_id, atualizar_fatura, get_estatisticas

st.set_page_config(page_title="FinTrack Dashboard", layout="wide")

st.title("💰 FinTrack - Dashboard Financeiro")
st.markdown("---")

# Sidebar com estatisticas
with st.sidebar:
    st.header("📊 Estatísticas")
    stats = get_estatisticas()
    st.metric("Total de Faturas", stats['total_faturas'])
    st.metric("Total Gasto", f"R$ {stats['total_gasto']:,.2f}")
    
    st.markdown("---")
    st.header("📈 Gastos por Categoria")
    if stats['por_categoria']:
        for cat, valor in stats['por_categoria'].items():
            st.write(f"- {cat}: R$ {valor:,.2f}")

# Abas principais
tab1, tab2, tab3 = st.tabs(["📋 Lista de Faturas", "✏️ Editar Fatura", "📊 Gráficos"])

# TAB 1: Lista de Faturas
with tab1:
    st.header("Todas as Faturas")
    
    faturas = listar_faturas()
    
    if faturas:
        # Converter para DataFrame
        df = pd.DataFrame(faturas)
        df['data_exibicao'] = pd.to_datetime(df['data'])
        df = df.sort_values('data_exibicao', ascending=False)
        
        # Selecionar colunas para exibir
        colunas_exibir = ['id', 'estabelecimento', 'data', 'valor_total', 'categoria']
        df_exibir = df[colunas_exibir].copy()
        df_exibir['valor_total'] = df_exibir['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_exibir, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ Remover Fatura")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            fatura_para_remover = st.selectbox(
                "Selecione a fatura para remover:",
                options=df['id'].tolist(),
                format_func=lambda x: f"#{x} - {df[df['id']==x]['estabelecimento'].iloc[0]} - R$ {df[df['id']==x]['valor_total'].iloc[0]:,.2f}"
            )
        with col2:
            if st.button("🗑️ Remover", type="primary"):
                deletar_fatura(fatura_para_remover)
                st.success(f"Fatura #{fatura_para_remover} removida com sucesso!")
                st.rerun()
    else:
        st.info("Nenhuma fatura encontrada. Faça upload de documentos no app principal.")

# TAB 2: Editar Fatura
with tab2:
    st.header("✏️ Editar Fatura")
    
    faturas = listar_faturas()
    
    if faturas:
        df = pd.DataFrame(faturas)
        
        fatura_id = st.selectbox(
            "Selecione a fatura para editar:",
            options=df['id'].tolist(),
            format_func=lambda x: f"#{x} - {df[df['id']==x]['estabelecimento'].iloc[0]} - R$ {df[df['id']==x]['valor_total'].iloc[0]:,.2f}",
            key="editar_select"
        )
        
        if fatura_id:
            fatura = buscar_fatura_por_id(fatura_id)
            
            if fatura:
                with st.form("editar_fatura_form"):
                    st.subheader(f"Editando Fatura #{fatura_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_estabelecimento = st.text_input("Estabelecimento", fatura['estabelecimento'])
                        nova_data = st.date_input("Data", pd.to_datetime(fatura['data']) if fatura['data'] else None)
                        novo_valor = st.number_input("Valor Total", value=float(fatura['valor_total']), step=10.0)
                    
                    with col2:
                        nova_categoria = st.selectbox(
                            "Categoria",
                            options=['Financeiro', 'Alimentacao', 'Transporte', 'Compras', 'Servicos', 'Educacao', 'Saude', 'Lazer', 'Outros'],
                            index=['Financeiro', 'Alimentacao', 'Transporte', 'Compras', 'Servicos', 'Educacao', 'Saude', 'Lazer', 'Outros'].index(fatura['categoria']) if fatura['categoria'] in ['Financeiro', 'Alimentacao', 'Transporte', 'Compras', 'Servicos', 'Educacao', 'Saude', 'Lazer', 'Outros'] else 8
                        )
                        novo_cnpj = st.text_input("CNPJ (opcional)", fatura['cnpj'])
                    
                    col3, col4, col5 = st.columns([1,1,2])
                    with col3:
                        submitted = st.form_submit_button("💾 Salvar Alterações", type="primary")
                    with col4:
                        if st.form_submit_button("❌ Cancelar"):
                            st.rerun()
                    
                    if submitted:
                        dados_atualizados = {
                            'estabelecimento': novo_estabelecimento,
                            'cnpj': novo_cnpj,
                            'data': nova_data.strftime('%Y-%m-%d') if nova_data else '',
                            'valor_total': novo_valor,
                            'categoria': nova_categoria,
                            'forma_pagamento': fatura.get('forma_pagamento', ''),
                            'itens': fatura.get('itens', []),
                            'arquivo_origem': fatura.get('arquivo_origem', '')
                        }
                        atualizar_fatura(fatura_id, dados_atualizados)
                        st.success(f"Fatura #{fatura_id} atualizada com sucesso!")
                        st.rerun()
    else:
        st.info("Nenhuma fatura para editar.")

# TAB 3: Gráficos
with tab3:
    st.header("📊 Análise de Gastos")
    
    faturas = listar_faturas()
    
    if faturas:
        df = pd.DataFrame(faturas)
        df['data'] = pd.to_datetime(df['data'])
        df['mes'] = df['data'].dt.strftime('%Y-%m')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Gastos por Categoria")
            gastos_categoria = df.groupby('categoria')['valor_total'].sum().reset_index()
            fig_categoria = px.pie(gastos_categoria, values='valor_total', names='categoria', title='Distribuição por Categoria')
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        with col2:
            st.subheader("Gastos por Mês")
            gastos_mes = df.groupby('mes')['valor_total'].sum().reset_index()
            fig_mes = px.bar(gastos_mes, x='mes', y='valor_total', title='Evolução Mensal')
            st.plotly_chart(fig_mes, use_container_width=True)
        
        st.subheader("Top 10 Maiores Gastos")
        top_gastos = df.nlargest(10, 'valor_total')[['estabelecimento', 'data', 'valor_total', 'categoria']]
        top_gastos['valor_total'] = top_gastos['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(top_gastos, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir nos gráficos.")
