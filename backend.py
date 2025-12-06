import mysql.connector
from mysql.connector import Error
import pandas as pd

# --- CONFIGURAÇÃO ---
DB_CONFIG = {
    'host': '192.168.1.14',
    'user': 'gustavo',
    'password': '@2J5Mi19h',
    'database': 'dbdeveloperbrightinventory'
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erro Conexão: {e}")
        return None

def buscar_lista_resumida():
    """
    Busca apenas os dados leves (Texto) para preencher a tabela rápido.
    NÃO traz o BLOB aqui para não travar a memória.
    """
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    cursor = conn.cursor()
    
    # Filtro: IDs de CPU (010110) e Notebooks (010121)
    query = """
    SELECT 
        A.idAparato,
        A.nNotaAparato_fk,
        A.valorAparato,
        A.observacao,
        N.dataEmissaoNota
    FROM tableaparatos A
    INNER JOIN tablenota N ON A.nNotaAparato_fk = N.nNotaAparato
    WHERE A.idAparato LIKE '010110%' OR A.idAparato LIKE '010121%'
    """
    
    try:
        cursor.execute(query)
        res = cursor.fetchall()
        
        lista = []
        for r in res:
            tipo = "Notebook" if str(r[0]).startswith("010121") else "CPU/Desktop"
            lista.append({
                "ID Aparato": r[0],
                "Tipo": tipo,
                "Nota Fiscal": r[1],
                "Valor": r[2],
                "Data": r[4],
                "Obs": r[3]
            })
            
        return pd.DataFrame(lista)
    except Error as e:
        print(f"Erro SQL: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def buscar_blob_nota(id_aparato):
    """
    Busca o arquivo PDF (BLOB) de UM item específico.
    """
    conn = get_connection()
    if not conn: return None
    
    cursor = conn.cursor()
    query = """
    SELECT N.notaFiscal
    FROM tableaparatos A
    INNER JOIN tablenota N ON A.nNotaAparato_fk = N.nNotaAparato
    WHERE A.idAparato = %s
    """
    
    try:
        cursor.execute(query, (id_aparato,))
        resultado = cursor.fetchone()
        if resultado and resultado[0]:
            return resultado[0] # Retorna os bytes puros
    except Error as e:
        print(f"Erro BLOB: {e}")
    finally:
        conn.close()
    return None