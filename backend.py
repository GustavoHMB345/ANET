import mysql.connector
from mysql.connector import Error
import pandas as pd
import io
import sys

# Tenta importar a biblioteca de PDF
try:
    from pypdf import PdfReader
except ImportError:
    print("ERRO CRÍTICO: pypdf não instalado.")

# --- CONFIGURAÇÃO ---
DB_CONFIG = {
    'host': '192.168.1.14', # Use o que funcionou anteriormente (127.0.0.1 ou o IP da rede)
    'user': 'gustavo',
    'password': '@2J5Mi19h', 
    'database': 'dbdeveloperbrightinventory'
}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG, connection_timeout=10)
        return connection
    except Error as e:
        print(f"Erro de conexão: {e}")
        return None

def validar_conexao():
    conn = None
    try:
        conn = get_connection()
        if conn and conn.is_connected():
            return True, f"Conectado ao banco em {DB_CONFIG['host']}!"
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

    # --- NOVA ESTRATÉGIA: FILTRO POR ID ---
    # Pegamos apenas IDs que começam com os códigos de TI
    query = """
    SELECT 
        A.idAparato,
        A.valorAparato,
        A.observacao,
        N.notaFiscal,        -- BLOB do PDF
        N.dataEmissaoNota
    FROM 
        tableaparatos AS A
    INNER JOIN 
        tablenota AS N 
        ON A.nNotaAparato_fk = N.nNotaAparato
    WHERE 
        A.idAparato LIKE '010110%'  -- CPUs
        OR 
        A.idAparato LIKE '010121%'  -- Notebooks
    """

    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        print(f"Query executada. Itens de TI encontrados pelo código: {len(resultados)}")
    except Error as e:
        print(f"Erro SQL: {e}")
        conn.close()
        return pd.DataFrame()

    lista_processada = []
    
    for linha in resultados:
        id_aparato = linha[0]
        valor_tab = linha[1]
        obs = linha[2]
        blob_data = linha[3]
        data_emissao = linha[4]

        # 1. Identifica o Tipo pelo Código
        tipo_equipamento = "Desconhecido"
        if str(id_aparato).startswith("010110"):
            tipo_equipamento = "CPU / Desktop"
        elif str(id_aparato).startswith("010121"):
            tipo_equipamento = "Notebook"

        # 2. Tenta extrair texto do PDF (Apenas para exibir detalhes, não para filtrar)
        texto_pdf = "(PDF não legível ou imagem)"
        if blob_data:
            try:
                arquivo_memoria = io.BytesIO(blob_data)
                leitor = PdfReader(arquivo_memoria)
                
                # Tenta pegar texto das primeiras páginas
                texto_extraido = ""
                for i, pagina in enumerate(leitor.pages):
                    if i > 2: break # Lê no máximo 3 páginas para não ficar lento
                    t = pagina.extract_text()
                    if t: texto_extraido += t + "\n"
                
                if texto_extraido.strip():
                    texto_pdf = texto_extraido[:500] + "..." # Guarda um resumo
            except Exception:
                pass # Se der erro no PDF, mantém o texto padrão, mas não perde o item

        # Adiciona à lista final (Garantido, pois o filtro foi pelo ID)
        lista_processada.append({
            "ID Aparato": id_aparato,
            "Tipo": tipo_equipamento,
            "Valor Tabela": valor_tab,
            "Data Emissão": data_emissao,
            "Observação": obs,
            "Resumo da Nota (PDF)": texto_pdf
        })

    conn.close()
    return pd.DataFrame(lista_processada)

if __name__ == "__main__":
    # Teste rápido de terminal
    ok, msg = validar_conexao()
    if ok:
        df = buscar_dados_aparatos()
        if not df.empty:
            print(df[['ID Aparato', 'Tipo', 'Resumo da Nota (PDF)']].head())
        else:
            print("Nenhum item encontrado com os códigos 010110... ou 010121...")
    else:
        print(msg)