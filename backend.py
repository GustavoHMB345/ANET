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
    'database': 'dbbrightinventory'      # O nome do banco de dados (corrigido conforme sua última mensagem)
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
    # ATENÇÃO AQUI: Adicionamos todas as colunas da sua imagem na ordem exata.
    query = """
    SELECT 
        A.idAparato,          -- Índice 0
        A.ordem,              -- Índice 1
        A.idEquipamento_fk,   -- Índice 2
        A.idMarca_fk,         -- Índice 3
        A.dataCompra,         -- Índice 4
        A.idLocalCompra_fk,   -- Índice 5
        A.idPredio_fk,        -- Índice 6
        A.idSetor_fk,         -- Índice 7
        A.idSala_fk,          -- Índice 8
        A.idLocalAlocado_fk,  -- Índice 9
        A.nNotaAparato_fk,    -- Índice 10 (Chave estrangeira da nota)
        A.valorAparato,       -- Índice 11
        A.situacao,           -- Índice 12
        A.observacao,         -- Índice 13
        A.licenca,            -- Índice 14
        A.grupoAdd,           -- Índice 15
        N.dataEmissaoNota     -- Índice 16 (Vem da tabela de notas 'N')
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
            
            # Adiciona um dicionário limpo na lista mapeando os índices numéricos
            # para nomes bonitos que aparecerão no Streamlit
            lista.append({
                "ID Aparato": r[0],
                "Tipo": tipo,
                "Ordem": r[1],
                "ID Equipamento": r[2],
                "ID Marca": r[3],
                "Data da Compra": r[4],
                "ID Local Compra": r[5],
                "ID Prédio": r[6],
                "ID Setor": r[7],
                "ID Sala": r[8],
                "ID Local Alocado": r[9],
                "Nota Fiscal": r[10],
                "Valor": r[11],
                "Situação": r[12],
                "Obs": r[13],
                "Licença": r[14],
                "Grupo Add": r[15],
                "Data Emissão NF": r[16]
            })
            
        # 7. Transforma a lista de dicionários em um DataFrame do Pandas
        return pd.DataFrame(lista)
        
    except Error as e:
        print(f"Erro SQL: {e}")
        return pd.DataFrame()
    finally:
        # 8. Fecha a conexão. Muito importante para não travar o banco!
        if conn and conn.is_connected():
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
        if conn and conn.is_connected():
            conn.close()
    return None