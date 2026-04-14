import streamlit as st
import pandas as pd
import plotly.express as px
from database import listar_faturas, deletar_fatura, buscar_fatura_por_id, atualizar_fatura, salvar_fatura, get_estatisticas
from ocr import extract_text
from parser_inteligente import parse_with_rules
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="FinTrack Dashboard", layout="wide")

st.title("💰 FinTrack - Sistema Financeiro Inteligente")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 Estatisticas")
    stats = get_estatisticas()
    st.metric("Total de Faturas", stats['total_faturas'])
    st.metric("Total Gasto", f"R$ {stats['total_gasto']:,.2f}")
    
    st.markdown("---")
    st.header("📈 Gastos por Categoria")
    if stats['por_categoria']:
        for cat, valor in stats['por_categoria'].items():
            st.write(f"- {cat}: R$ {valor:,.2f}")
    
    st.markdown("---")
    st.header("📤 Exportar Dados")
    
    faturas_export = listar_faturas()
    if faturas_export:
        df_export = pd.DataFrame(faturas_export)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fintrack_dados_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    if st.button("🔄 Atualizar Tudo"):
        st.rerun()

# Abas
tab0, tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 Lista", "✏️ Editar", "📊 Graficos"])

# TAB 0: Upload
with tab0:
    st.header("Upload de Nova Fatura")
    
    arquivo = st.file_uploader("Escolha um arquivo (PDF, imagem ou TXT)", type=['pdf', 'png', 'jpg', 'jpeg', 'txt'], key="uploader")
    
    if arquivo:
        with st.spinner("Processando arquivo..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{arquivo.name}") as tmp:
                tmp.write(arquivo.getvalue())
                caminho = tmp.name
            
            texto = extract_text(caminho)
            dados = parse_with_rules(texto)
            dados['arquivo_origem'] = arquivo.name
            salvar_fatura(dados)
            os.unlink(caminho)
        
        st.success(f"✅ Fatura processada e salva!")
        st.json(dados)
        st.info("Clique em 'Atualizar Tudo' no menu lateral para ver as mudancas.")

# TAB 1: Lista
with tab1:
    st.header("Todas as Faturas")
    
    faturas = listar_faturas()
    
    if faturas:
        df = pd.DataFrame(faturas)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            df = df.sort_values('data', ascending=False)
        
        # Filtros
        st.subheader("🔍 Filtros")
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_categoria = st.multiselect("Categoria", options=df['categoria'].unique())
        with col_f2:
            filtro_estabelecimento = st.multiselect("Estabelecimento", options=df['estabelecimento'].unique())
        with col_f3:
            if 'data' in df.columns:
                min_data = df['data'].min()
                max_data = df['data'].max()
                filtro_data = st.date_input("Periodo", value=[min_data, max_data])
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if filtro_categoria:
            df_filtrado = df_filtrado[df_filtrado['categoria'].isin(filtro_categoria)]
        if filtro_estabelecimento:
            df_filtrado = df_filtrado[df_filtrado['estabelecimento'].isin(filtro_estabelecimento)]
        if len(filtro_data) == 2:
            df_filtrado = df_filtrado[(df_filtrado['data'] >= pd.to_datetime(filtro_data[0])) & (df_filtrado['data'] <= pd.to_datetime(filtro_data[1]))]
        
        colunas = ['id', 'estabelecimento', 'data', 'valor_total', 'categoria']
        df_exibir = df_filtrado[colunas].copy()
        df_exibir['valor_total'] = df_exibir['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(df_exibir, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ Remover Fatura")
        
        if 'confirmar_remover' not in st.session_state:
            st.session_state.confirmar_remover = None
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if not df_filtrado.empty:
                fatura_para_remover = st.selectbox(
                    "Selecione a fatura para remover:",
                    options=df_filtrado['id'].tolist(),
                    format_func=lambda x: f"#{x} - {df_filtrado[df_filtrado['id']==x]['estabelecimento'].iloc[0]} - R$ {df_filtrado[df_filtrado['id']==x]['valor_total'].iloc[0]:,.2f}",
                    key="remover_select"
                )
        with col2:
            if st.button("🗑️ Remover", key="remover_btn"):
                st.session_state.confirmar_remover = fatura_para_remover
        
        with col3:
            if st.button("❌ Cancelar", key="cancelar_btn"):
                st.session_state.confirmar_remover = None
                st.success("Operacao cancelada!")
        
        if st.session_state.confirmar_remover:
            st.warning(f"⚠️ Tem certeza que deseja remover a fatura #{st.session_state.confirmar_remover}?")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ Sim, remover", key="confirmar_sim"):
                    deletar_fatura(st.session_state.confirmar_remover)
                    st.success(f"✅ Fatura #{st.session_state.confirmar_remover} removida!")
                    st.session_state.confirmar_remover = None
                    st.rerun()
            with col_cancel:
                if st.button("❌ Nao, cancelar", key="confirmar_nao"):
                    st.session_state.confirmar_remover = None
                    st.rerun()
    else:
        st.info("Nenhuma fatura encontrada. Faca upload na aba Upload.")

# TAB 2: Editar
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
                with st.form(key="editar_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        novo_est = st.text_input("Estabelecimento", fatura['estabelecimento'])
                        nova_data = st.date_input("Data", pd.to_datetime(fatura['data']) if fatura['data'] else pd.Timestamp.now())
                    with col2:
                        novo_valor = st.number_input("Valor Total", value=float(fatura['valor_total']), step=10.0)
                        categorias = ['Financeiro', 'Alimentacao', 'Transporte', 'Compras', 'Servicos', 'Educacao', 'Saude', 'Lazer', 'Internet', 'Energia', 'Outros']
                        idx = categorias.index(fatura['categoria']) if fatura['categoria'] in categorias else 10
                        nova_cat = st.selectbox("Categoria", categorias, index=idx)
                    
                    submitted = st.form_submit_button("💾 Salvar Alteracoes")
                    
                    if submitted:
                        fatura['estabelecimento'] = novo_est
                        fatura['data'] = nova_data.strftime('%Y-%m-%d')
                        fatura['valor_total'] = novo_valor
                        fatura['categoria'] = nova_cat
                        atualizar_fatura(fatura_id, fatura)
                        st.success(f"✅ Fatura #{fatura_id} atualizada!")
                        st.info("Clique em 'Atualizar Tudo' no menu lateral para ver as mudancas.")
    else:
        st.info("Nenhuma fatura para editar.")

# TAB 3: Graficos
with tab3:
    st.header("📊 Analise de Gastos")
    
    faturas = listar_faturas()
    
    if faturas:
        df = pd.DataFrame(faturas)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            df['mes'] = df['data'].dt.strftime('%Y-%m')
        
        col1, col2 = st.columns(2)
        
        with col1:
            gastos_cat = df.groupby('categoria')['valor_total'].sum().reset_index()
            fig = px.pie(gastos_cat, values='valor_total', names='categoria', title="Gastos por Categoria")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'mes' in df.columns and not df['mes'].empty:
                gastos_mes = df.groupby('mes')['valor_total'].sum().reset_index()
                fig2 = px.bar(gastos_mes, x='mes', y='valor_total', title="Gastos por Mes")
                st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Top 10 Maiores Gastos")
        top = df.nlargest(10, 'valor_total')[['estabelecimento', 'data', 'valor_total', 'categoria']]
        top['valor_total'] = top['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        st.dataframe(top, use_container_width=True)
    else:
        st.info("Nenhum dado para exibir nos graficos.")
