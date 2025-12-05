import mysql.connector
from mysql.connector import Error
import pandas as pd
import json

# --- CONFIGURAÇÕES DO BANCO ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'gustavo',
    'password': '@2J5Mi19h',  
    'database': 'dbdeveloperbrightinventory'
}

def get_connection():
    """Conecta ao banco de dados."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Erro de conexão: {e}")
        return None

def validar_conexao():
    """Testa se o banco está respondendo."""
    conn = None
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            return True, "Banco de Dados Conectado!"
        return False, "Banco não responde."
    except Error as e:
        return False, f"Erro: {str(e)}"
    finally:
        if conn and conn.is_connected():
            conn.close()

def buscar_dados_aparatos():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    cursor = conn.cursor()

    # --- QUERY CORRIGIDA COM BASE NAS IMAGENS ---
    # 1. Tabela 'tablenota'
    # 2. Chave 'nNotaAparato'
    # 3. Coluna BLOB 'notaFiscal'
    
    query = """
    SELECT 
        A.idAparato,
        A.valorAparato,
        A.observacao,
        N.notaFiscal,        -- Nome correto da coluna do BLOB
        N.dataEmissaoNota    -- Aproveitei para pegar a data também
    FROM 
        tableaparatos AS A
    INNER JOIN 
        tablenota AS N 
        ON A.nNotaAparato_fk = N.nNotaAparato -- Ligação correta das chaves
    """

    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
    except Error as e:
        print(f"Erro na Query SQL: {e}")
        conn.close()
        return pd.DataFrame()

    lista_produtos_processados = []

    for linha in resultados:
        id_aparato = linha[0]
        valor_tabela = linha[1]
        observacao = linha[2]
        blob_data = linha[3]     # O conteúdo binário da nota
        data_emissao = linha[4]

        if blob_data is None:
            continue

        try:
            # 1. Decodificar Binário -> Texto
            if isinstance(blob_data, (bytes, bytearray)):
                json_str = blob_data.decode('utf-8')
            else:
                json_str = str(blob_data)

            # 2. Texto -> JSON
            dados_nota = json.loads(json_str)

            # 3. Normalizar estrutura (Lista ou Dict)
            # Verifica se o JSON é uma lista direta ou um dicionário com chave 'itens'
            itens_verificar = []
            if isinstance(dados_nota, list):
                itens_verificar = dados_nota
            elif isinstance(dados_nota, dict):
                # Tenta achar chaves comuns de listas de produtos
                # Adicionei 'detalhes' e 'items' que são comuns também
                itens_verificar = dados_nota.get('itens', 
                                  dados_nota.get('produtos', 
                                  dados_nota.get('detalhes', [dados_nota])))

            # 4. Filtro de Hardware (Notebook/PC)
            for item in itens_verificar:
                if isinstance(item, dict):
                    # Pega descrição ou nome
                    descricao = item.get('descricao', item.get('nome', item.get('produto', ''))).lower()
                    
                    termos = ['notebook', 'computador', 'pc', 'desktop', 'macbook', 'dell', 'lenovo', 'hp', 'samsung']
                    
                    if any(t in descricao for t in termos):
                        lista_produtos_processados.append({
                            "ID Aparato": id_aparato,
                            "Produto (JSON)": item.get('descricao', item.get('nome')),
                            "Valor Nota": item.get('valor', item.get('preco', 0)),
                            "Data Emissão": data_emissao,
                            "Observação": observacao,
                            "Dados Completos": dados_nota # Para exibir o JSON bruto se clicar
                        })

        except Exception as e:
            # Pula silenciosamente erros de JSON inválido para não travar a tela
            continue

    conn.close()
    return pd.DataFrame(lista_produtos_processados)