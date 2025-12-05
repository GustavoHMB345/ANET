import mysql.connector
from mysql.connector import Error
import pandas as pd
import json

# --- CONFIGURAÇÕES DO BANCO ---
# CORREÇÃO DO ERRO 111:
# Trocamos 'localhost' por '127.0.0.1' para forçar conexão via rede TCP.
DB_CONFIG = {
    'host': '127.0.0.1',    # <--- MUDANÇA AQUI
    'port': 3306,           # Garantindo a porta padrão
    'user': 'gustavo',         # Se 'root' não funcionar, tente voltar para 'gustavo'
    'password': '@2J5Mi19h',         # <--- SE O ROOT TIVER SENHA, PREENCHA AQUI. 
    'database': 'dbdeveloperbrightinventory'
}


def get_connection():
    try:
        # connection_timeout=10 dá mais tempo para o banco responder
        connection = mysql.connector.connect(**DB_CONFIG, connection_timeout=10)
        return connection
    except Error as e:
        print(f"ERRO CRÍTICO DE CONEXÃO: {e}")
        return None

def validar_conexao():
    conn = None
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            return True, f"Conectado com sucesso em {DB_CONFIG['host']}!"
        return False, "Banco não responde (Connection Refused)."
    except Error as e:
        msg = str(e)
        if "111" in msg or "Connection refused" in msg:
            return False, "ERRO 111: O banco recusou a conexão. Verifique se o MySQL está rodando."
        if "1045" in msg or "Access denied" in msg:
            return False, "ERRO DE SENHA (1045): Usuário ou senha incorretos."
        return False, f"Erro: {msg}"
    finally:
        if conn and conn.is_connected():
            conn.close()

def buscar_dados_aparatos():
    print("--- Iniciando busca de dados ---")
    conn = get_connection()
    if not conn:
        print("Abortando: Sem conexão.")
        return pd.DataFrame()

    cursor = conn.cursor()

    query = """
    SELECT 
        A.idAparato,
        A.valorAparato,
        A.observacao,
        N.notaFiscal,        -- BLOB
        N.dataEmissaoNota    -- Data
    FROM 
        tableaparatos AS A
    INNER JOIN 
        tablenota AS N 
        ON A.nNotaAparato_fk = N.nNotaAparato
    """

    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        print(f"Query executada. Linhas retornadas: {len(resultados)}")
    except Error as e:
        print(f"ERRO DE SQL: {e}")
        conn.close()
        return pd.DataFrame()

    lista_produtos = []

    for linha in resultados:
        # Extração segura
        id_aparato = linha[0]
        blob_data = linha[3]
        
        if blob_data is None:
            continue

        try:
            # Tenta decodificar o BLOB
            if isinstance(blob_data, (bytes, bytearray)):
                json_str = blob_data.decode('utf-8', errors='ignore') 
            else:
                json_str = str(blob_data)

            if not json_str.strip(): 
                continue
                
            dados_nota = json.loads(json_str)

            # Busca flexível
            itens_verificar = []
            if isinstance(dados_nota, list):
                itens_verificar = dados_nota
            elif isinstance(dados_nota, dict):
                itens_verificar = dados_nota.get('itens', dados_nota.get('produtos', [dados_nota]))

            for item in itens_verificar:
                if isinstance(item, dict):
                    nome = item.get('descricao', item.get('nome', item.get('produto', ''))).lower()
                    
                    if any(x in nome for x in ['notebook', 'computador', 'pc', 'desktop', 'dell', 'hp', 'lenovo']):
                        lista_produtos.append({
                            "ID": id_aparato,
                            "Produto": item.get('descricao', item.get('nome')),
                            "Valor Tabela": linha[1],
                            "Data": linha[4],
                            "JSON Bruto": dados_nota
                        })
                        
        except Exception as e:
            # print(f"Erro ao processar linha: {e}") # Comentado para não poluir
            continue

    conn.close()
    print(f"Itens de informática encontrados: {len(lista_produtos)}")
    return pd.DataFrame(lista_produtos)

if __name__ == "__main__":
    ok, msg = validar_conexao()
    print(msg)
    if ok:
        df = buscar_dados_aparatos()
        if not df.empty:
            print(df.head())
        else:
            print("Conectou, mas nenhum notebook/PC foi encontrado nos JSONs.")