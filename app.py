import streamlit as st
import backend as bk
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Validador de Banco de Dados", page_icon="🔌")

st.title("🔌 Teste de Conexão MySQL")
st.markdown("Este aplicativo serve apenas para validar se o Python consegue falar com o seu Banco de Dados.")

st.divider()

# --- ÁREA 1: TESTE DE PING (CONEXÃO) ---
st.subheader("1. Teste de Conexão (Ping)")

col1, col2 = st.columns([1, 3])
with col1:
    btn_teste = st.button("Testar Conexão Agora", type="primary")

with col2:
    if btn_teste:
        with st.spinner("Conectando ao 192.168.1.14..."):
            sucesso, mensagem = bk.validar_conexao()
            
        if sucesso:
            st.success(f"**SUCESSO:** {mensagem}")
            st.session_state['conexao_ok'] = True
        else:
            st.error(f"**FALHA:** {mensagem}")
            st.session_state['conexao_ok'] = False

# --- ÁREA 2: TESTE DE DADOS (SELECT) ---
st.divider()
st.subheader("2. Teste de Leitura de Dados")

# Só permite tentar ler dados se a conexão funcionou antes (ou se o usuário insistir)
if st.button("Tentar Ler e Processar Tabela de Aparatos"):
    if 'conexao_ok' in st.session_state and not st.session_state['conexao_ok']:
        st.warning("Atenção: O teste de conexão falhou anteriormente. Isso provavelmente vai dar erro.")
    
    with st.spinner("Lendo tabelas e processando JSONs... (Isso pode demorar)"):
        df_resultado = bk.buscar_dados_aparatos()
    
    if not df_resultado.empty:
        st.balloons()
        st.success(f"Leitura concluída! Foram encontrados **{len(df_resultado)}** registros de informática.")
        
        st.write("### Amostra dos Dados (Primeiras 5 linhas):")
        st.dataframe(df_resultado.head())
        
        st.write("### Estrutura dos Dados:")
        st.json(df_resultado.iloc[0].to_dict()) # Mostra o primeiro registro como JSON para inspeção
    else:
        st.warning("A consulta rodou, mas nenhum dado foi retornado. Verifique se:\n1. Existem dados na tabela.\n2. Se o filtro de 'Notebook/Computador' está funcionando para os seus dados.")