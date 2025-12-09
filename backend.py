# Importa a biblioteca que permite o Python "falar" com o MySQL
import mysql.connector
# Importa apenas o tratamento de erros (para sabermos se a conexão falhou)
from mysql.connector import Error
# Importa o Pandas, usado para criar tabelas estilizadas (DataFrames)
import pandas as pd

# --- CONFIGURAÇÃO ---
# Um dicionário (chave: valor) com as credenciais de acesso.
DB_CONFIG = {
    'host': '192.168.1.14',              # O endereço IP onde o banco está
    'user': 'gustavo',                   # O usuário
    'password': '@2J5Mi19h',             # A senha
    'database': 'dbdeveloperbrightinventory' # O nome do banco de dados
}

def get_connection():
    """Tenta abrir uma porta de conexão com o banco."""
    try:
        # O **DB_CONFIG é um truque do Python (desempacotamento).
        # Ele pega o dicionário acima e espalha os argumentos automaticamente.
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        # Se der errado (senha errada, IP errado), avisa no console.
        print(f"Erro Conexão: {e}")
        return None

def buscar_lista_resumida():
    """
    Função INTELIGENTE: Busca apenas textos e números.
    Ignora os arquivos pesados (PDFs) para a lista carregar rápido.
    """
    # 1. Abre a conexão
    conn = get_connection()
    # Se a conexão falhou, retorna uma tabela vazia para não quebrar o app
    if not conn: return pd.DataFrame()
    
    # 2. Cria o Cursor. O cursor é como um "dedo" que aponta para as linhas do banco.
    cursor = conn.cursor()
    
    # 3. Escreve a pergunta (Query) para o banco:
    query = """
    SELECT 
        A.idAparato,        -- Pega o Código (ex: 010121.500)
        A.nNotaAparato_fk,  -- Pega o número da nota (chave estrangeira)
        A.valorAparato,     -- Pega o valor
        A.observacao,       -- Pega observações
        N.dataEmissaoNota   -- Pega a data (vem da outra tabela 'N')
    FROM tableaparatos A    -- Da tabela de aparatos (apelidada de A)
    INNER JOIN tablenota N  -- Junte com a tabela de notas (apelidada de N)
        ON A.nNotaAparato_fk = N.nNotaAparato -- Onde os números das notas batem
    WHERE 
        A.idAparato LIKE '010110%' -- Traga se começar com 010110 (CPUs)
        OR 
        A.idAparato LIKE '010121%' -- OU se começar com 010121 (Notebooks)
    """
    
    try:
        # 4. Executa a pergunta
        cursor.execute(query)
        # 5. Pega TODAS as respostas que o banco devolveu
        res = cursor.fetchall()
        
        lista = []
        # 6. Loop (Repetição): Para cada linha encontrada
        for r in res:
            # Lógica Python: Se o ID começa com '010121', é Notebook. Senão, é CPU.
            # r[0] é a primeira coluna (idAparato)
            tipo = "Notebook" if str(r[0]).startswith("010121") else "CPU/Desktop"
            
            # Adiciona um dicionário limpo na lista
            lista.append({
                "ID Aparato": r[0],
                "Tipo": tipo,
                "Nota Fiscal": r[1],
                "Valor": r[2],
                "Data": r[4],
                "Obs": r[3]
            })
            
        # 7. Transforma a lista de dicionários em um DataFrame do Pandas
        return pd.DataFrame(lista)
        
    except Error as e:
        print(f"Erro SQL: {e}")
        return pd.DataFrame()
    finally:
        # 8. Fecha a conexão. Muito importante para não travar o banco!
        conn.close()

def buscar_blob_nota(id_aparato):
    """
    Função PESADA: Busca apenas o arquivo PDF (BLOB) de UM item.
    Só é chamada quando o usuário quer ver o documento.
    """
    conn = get_connection()
    if not conn: return None
    
    cursor = conn.cursor()
    
    # Query específica: Traz a coluna 'notaFiscal' (BLOB)
    query = """
    SELECT N.notaFiscal
    FROM tableaparatos A
    INNER JOIN tablenota N ON A.nNotaAparato_fk = N.nNotaAparato
    WHERE A.idAparato = %s 
    """
    # O '%s' acima é um espaço reservado de segurança.
    
    try:
        # Executa a query trocando o %s pelo ID real (id_aparato)
        # A vírgula (id_aparato,) é necessária para o Python entender que é uma tupla
        cursor.execute(query, (id_aparato,))
        
        # fetchone(): Pega APENAS UM resultado (pois o ID é único)
        resultado = cursor.fetchone()
        
        # Se achou algo e não está vazio...
        if resultado and resultado[0]:
            return resultado[0] # Retorna os bytes puros do arquivo
            
    except Error as e:
        print(f"Erro BLOB: {e}")
    finally:
        conn.close()
    return None