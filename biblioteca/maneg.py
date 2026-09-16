import os
import pyodbc
from dotenv import load_dotenv, find_dotenv


env_path = find_dotenv(filename=".env", usecwd=True)
if not env_path:
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path=env_path)

driver = os.getenv("DB_DRIVER")
server = os.getenv("DB_SERVER")
port = os.getenv("DB_PORT")
database = os.getenv("DB_DATABASE")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

print("Driver:", repr(driver))
print("Server:", repr(server))

if not driver:
    print("ERRO: Variáveis do .env não foram carregadas.")
else:
    # O nome do driver ODBC exige chaves { } na string de conexão
    conn_str = f"DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={password};"
    
    print("\nConectando ao banco de dados PostgreSQL...")
    try:
        conn = pyodbc.connect(conn_str)
        print("[SUCESSO] Conexao realizada com SUCESSO!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        row = cursor.fetchone()
        print("Versao do banco de dados:", row[0])
        
        conn.close()
    except Exception as e:
        print("[ERRO] Erro ao conectar:", e)