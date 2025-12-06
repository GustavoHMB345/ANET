import streamlit as st
import pandas as pd
import backend as bk
import base64

# Configuração da página
st.set_page_config(page_title="Visualizador de Notas", layout="wide")

st.title("🖥️ Inventário & Notas Fiscais")
st.caption("Filtro Automático: CPUs (010110...) e Notebooks (010121...)")

# --- TRATAMENTO DE ERROS GLOBAIS ---
if not hasattr(bk, 'buscar_lista_resumida'):
    st.error("Erro Crítico: O arquivo backend.py parece estar incompleto.")
    st.stop()

# --- COLUNA DA ESQUERDA: LISTA ---
col_lista, col_visualizador = st.columns([1, 1.2])

with col_lista:
    st.subheader("1. Selecione o Equipamento")
    
    # Botão de atualização
    if st.button("🔄 Atualizar Lista"):
        with st.spinner("Conectando ao banco..."):
            try:
                df = bk.buscar_lista_resumida()
                st.session_state['df_equipamentos'] = df
            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")

    # Exibição dos Dados
    if 'df_equipamentos' in st.session_state and not st.session_state['df_equipamentos'].empty:
        df = st.session_state['df_equipamentos']
        
        # --- NOVO: MÉTRICAS DE QUANTIDADE ---
        # Calculamos os totais baseados na coluna 'Tipo' que o backend gera
        total_geral = len(df)
        qtd_notebooks = len(df[df['Tipo'] == 'Notebook'])
        qtd_cpus = len(df[df['Tipo'] == 'CPU/Desktop'])
        
        # Exibe em colunas bonitas
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Geral", total_geral)
        m2.metric("💻 Notebooks", qtd_notebooks)
        m3.metric("🖥️ CPUs", qtd_cpus)
        st.divider()
        # ------------------------------------

        # Tabela
        st.dataframe(
            df[['ID Aparato', 'Tipo', 'Nota Fiscal']], 
            use_container_width=True, 
            height=300
        )
        
        # Selectbox
        lista_ids = df['ID Aparato'].tolist()
        id_selecionado = st.selectbox("Escolha um ID para ver a Nota:", lista_ids)
        
        # Detalhes rápidos
        if id_selecionado:
            item_detalhes = df[df['ID Aparato'] == id_selecionado].iloc[0]
            st.info(f"**Item:** {item_detalhes['Tipo']}\n\n**Valor:** R$ {item_detalhes['Valor']}\n\n**Obs:** {item_detalhes['Obs']}")
    
    elif 'df_equipamentos' in st.session_state and st.session_state['df_equipamentos'].empty:
        st.warning("A busca funcionou, mas nenhum equipamento foi encontrado.")
    else:
        st.info("Clique no botão acima para carregar a lista.")
        id_selecionado = None

# --- COLUNA DA DIREITA: VISUALIZADOR ---
with col_visualizador:
    st.subheader("2. Visualização da Nota (PDF)")
    
    if id_selecionado:
        # Busca o BLOB
        with st.spinner(f"Baixando PDF..."):
            try:
                blob_bytes = bk.buscar_blob_nota(id_selecionado)
            except Exception as e:
                st.error(f"Erro ao baixar BLOB: {e}")
                blob_bytes = None
        
        if blob_bytes:
            try:
                # Converte para Base64 para exibir no navegador
                base64_pdf = base64.b64encode(blob_bytes).decode('utf-8')
                
                # HTML do Iframe
                pdf_display = f'''
                    <iframe 
                        src="data:application/pdf;base64,{base64_pdf}" 
                        width="100%" 
                        height="600px" 
                        type="application/pdf"
                        style="border: 1px solid #ccc; border-radius: 5px;">
                    </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao renderizar PDF: {e}")
        else:
            st.warning("⚠️ Este item não possui arquivo de nota fiscal (BLOB vazio).")
    else:
        st.write("👈 Selecione um item na lista ao lado.")