import mysql.connector
import json
import io
import sys

# Tenta importar a biblioteca de PDF
try:
    from pypdf import PdfReader
except ImportError:
    print("❌ ERRO: Você precisa instalar a biblioteca pypdf.")
    print("Rode no terminal: pip install pypdf")
    sys.exit()

# --- CONFIGURAÇÃO ---
DB_CONFIG = {
    'host': '192.168.1.14', 
    'user': 'gustavo',   
    'password': '@2J5Mi19h', 
    'database': 'dbdeveloperbrightinventory'
}

def espionar_pdf():
    print("--- 🕵️ INICIANDO ESPIONAGEM DE PDF ---")
    print("Detectamos que seus dados são arquivos PDF, não JSON.")
    print("Tentando extrair texto de dentro dos arquivos...\n")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # CORREÇÃO: O nome da coluna chave é 'nNotaAparato'
        query = """
        SELECT nNotaAparato, notaFiscal 
        FROM tablenota 
        WHERE notaFiscal IS NOT NULL 
        LIMIT 3
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        print(f"🔍 Encontrei {len(resultados)} notas.\n")

        for i, linha in enumerate(resultados):
            id_nota = linha[0]
            blob_data = linha[1]
            print(f"--- NOTA ID: {id_nota} ---")
            
            try:
                # 1. Converte o BLOB (bytes) para um arquivo em memória
                arquivo_memoria = io.BytesIO(blob_data)
                
                # 2. Usa o leitor de PDF
                leitor = PdfReader(arquivo_memoria)
                
                # 3. Tenta extrair o texto da primeira página
                if len(leitor.pages) > 0:
                    texto_completo = leitor.pages[0].extract_text()
                    
                    print("✅ TEXTO EXTRAÍDO DO PDF:")
                    print("-" * 40)
                    # Imprime apenas os primeiros 500 caracteres para não poluir
                    if texto_completo:
                        print(texto_completo[:500] + "...") 
                    else:
                        print("(Página em branco ou imagem sem texto)")
                    print("-" * 40)
                    
                    # Teste rápido se tem palavras chave
                    if texto_completo:
                        texto_lower = texto_completo.lower()
                        if "notebook" in texto_lower or "computador" in texto_lower:
                            print("🎉 ACHEI! Encontrei 'notebook' ou 'computador' neste texto!")
                        else:
                            print("⚠️ Não achei palavras-chave de informática nesta primeira página.")
                else:
                    print("⚠️ O PDF não tem páginas.")

            except Exception as e:
                print(f"❌ Erro ao ler PDF: {e}")
            
            print("\n")

        conn.close()

    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    espionar_pdf()