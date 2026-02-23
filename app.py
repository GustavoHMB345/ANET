# Importa a biblioteca principal de interface
import streamlit as st
# Importa o Pandas para manipular tabelas de dados
import pandas as pd
# Importa o nosso arquivo 'backend.py' (a Cozinha) para podermos chamar as funções de lá
import backend as bk
# Importa biblioteca para transformar arquivos binários em texto (necessário para o PDF)
import base64

# 1. CONFIGURAÇÃO INICIAL
# Define o título da aba do navegador e diz para usar a tela cheia (layout="wide")
# IMPORTANTE: Este comando deve ser sempre a primeira coisa do Streamlit no código.
st.set_page_config(page_title="Visualizador de Notas", layout="wide")

# Títulos visuais na página
st.title("🖥️ Inventário & Notas Fiscais")
st.caption("Filtro Automático: CPUs (010110...) e Notebooks (010121...)")

# 2. SEGURANÇA (Checagem de Backend)
# Verifica se a função 'buscar_lista_resumida' existe dentro do arquivo backend.
# Isso evita que o site mostre uma tela de erro feia se o backend estiver quebrado.
if not hasattr(bk, 'buscar_lista_resumida'):
    st.error("Erro Crítico: O arquivo backend.py parece estar incompleto.")
    st.stop() # Para a execução do código aqui.

# 3. LAYOUT (Dividindo a tela)
# Cria duas colunas invisíveis.
# A da esquerda (lista) tem tamanho 1, a da direita (visualizador) é 20% maior (1.2).
col_lista, col_visualizador = st.columns([1, 1.2])

# --- LÓGICA DA COLUNA ESQUERDA ---
with col_lista:
    st.subheader("1. Selecione o Equipamento")
    
    # 4. BOTÃO DE CARREGAMENTO
    # Se clicar no botão, entra neste bloco.
    if st.button("🔄 Atualizar Lista"):
        with st.spinner("Conectando ao banco..."): # Mostra rodinha de carregamento
            try:
                # Chama a Cozinha (Backend) para pegar os dados leves
                df = bk.buscar_lista_resumida()
                
                # 5. MEMÓRIA DE SESSÃO (Session State)
                # Salva os dados na memória do navegador. Sem isso, ao clicar em qualquer
                # outra coisa, a tabela sumiria, pois o Streamlit recarrega o código todo.
                st.session_state['df_equipamentos'] = df
            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")

    # 6. EXIBIÇÃO CONDICIONAL
    # "Se existe uma tabela salva na memória E ela não está vazia..."
    if 'df_equipamentos' in st.session_state and not st.session_state['df_equipamentos'].empty:
        # Recupera a tabela da memória
        df = st.session_state['df_equipamentos']
        
        # --- CÁLCULO DE MÉTRICAS (KPIs) ---
        # Usa o Pandas para filtrar e contar linhas rapidamente
        total_geral = len(df)
        qtd_notebooks = len(df[df['Tipo'] == 'Notebook'])
        qtd_cpus = len(df[df['Tipo'] == 'CPU/Desktop'])
        
        # Cria 3 colunas pequenas uma ao lado da outra para os números
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Geral", total_geral)
        m2.metric("💻 Notebooks", qtd_notebooks)
        m3.metric("🖥️ CPUs", qtd_cpus)
        
        st.divider() # Desenha uma linha horizontal cinza
        
        # --- TABELA INTERATIVA ---
        # Mostra apenas as colunas que interessam.
        # width='stretch' faz a tabela ocupar toda a largura disponível.
        st.dataframe(
            df[['ID Aparato', 'Tipo', 'Nota Fiscal']], 
            width='stretch', 
            height=300
        )
        
        # --- SELETOR (Dropdown) ---
        # Cria uma lista simples com todos os IDs para o usuário escolher
        lista_ids = df['ID Aparato'].tolist()
        id_selecionado = st.selectbox("Escolha um ID para ver a Nota:", lista_ids)
        
        # --- DETALHES RÁPIDOS ---
        # Se escolheu alguém, mostra um box azul (st.info) com o resumo
        if id_selecionado:
            # Filtra o DataFrame para pegar a linha daquele ID
            item_detalhes = df[df['ID Aparato'] == id_selecionado].iloc[0]
            st.info(f"**Item:** {item_detalhes['Tipo']}\n\n**Valor:** R$ {item_detalhes['Valor']}\n\n**Obs:** {item_detalhes['Obs']}")
    
    # Tratamento de tabela vazia
    elif 'df_equipamentos' in st.session_state and st.session_state['df_equipamentos'].empty:
        st.warning("A busca funcionou, mas nenhum equipamento foi encontrado.")
    else:
        # Estado inicial (antes de clicar no botão)
        st.info("Clique no botão acima para carregar a lista.")
        id_selecionado = None

# --- LÓGICA DA COLUNA DIREITA ---
with col_visualizador:
    st.subheader("2. Visualização da Nota (PDF)")
    
    # Se algum ID foi escolhido na coluna da esquerda...
    if id_selecionado:
        # Chama o backend para buscar o ARQUIVO PESADO (BLOB)
        with st.spinner(f"Baixando PDF..."):
            try:
                blob_bytes = bk.buscar_blob_nota(id_selecionado)
            except Exception as e:
                st.error(f"Erro ao baixar BLOB: {e}")
                blob_bytes = None
        
        # Se o backend retornou um arquivo...
        if blob_bytes:
            try:
                # 7. TRUQUE DO BASE64
                # Navegadores não leem binário de banco de dados.
                # Transformamos o binário em um "textão" código (base64) que o HTML entende.
                base64_pdf = base64.b64encode(blob_bytes).decode('utf-8')
                
                # 8. INJEÇÃO DE HTML (IFRAME)
                # Criamos um visualizador de PDF usando HTML puro dentro do Python
                pdf_display = f'''
                    <iframe 
                        src="data:application/pdf;base64,{base64_pdf}" 
                        width="100%" 
                        height="600px" 
                        type="application/pdf"
                        style="border: 1px solid #ccc; border-radius: 5px;">
                    </iframe>
                '''
                # Renderiza esse HTML na tela
                st.markdown(pdf_display, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao renderizar PDF: {e}")
        else:
            st.warning("⚠️ Este item não possui arquivo de nota fiscal (BLOB vazio).")
    else:
        st.write("👈 Selecione um item na lista ao lado.")