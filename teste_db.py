import sqlite3
import pandas as pd
import os

# Caminho do banco de dados
db_path = '/Users/denniscanteli/Downloads/Arquivo/dashboard_lavanderia/dstechBD.db'

print(f"Verificando se o arquivo existe: {os.path.exists(db_path)}")

try:
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    print("Conexão com o banco de dados estabelecida com sucesso!")
    
    # Listar tabelas
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tabelas no banco de dados: {tables}")
    
    # Verificar registros na tabela DADOS
    cursor.execute("SELECT COUNT(*) FROM DADOS")
    count = cursor.fetchone()[0]
    print(f"Total de registros na tabela DADOS: {count}")
    
    # Consultar alguns registros
    df = pd.read_sql_query("SELECT * FROM DADOS LIMIT 5", conn)
    print("\nPrimeiros 5 registros:")
    print(df)
    
    # Verificar estrutura da tabela
    cursor.execute("PRAGMA table_info(DADOS)")
    columns = cursor.fetchall()
    print("\nEstrutura da tabela DADOS:")
    for col in columns:
        print(col)
    
    # Fechar conexão
    conn.close()
    print("Conexão fechada com sucesso!")
    
except Exception as e:
    print(f"ERRO: {str(e)}")
    import traceback
    print(traceback.format_exc())
