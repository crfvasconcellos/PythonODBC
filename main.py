import os
import pyodbc
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de conexão definidas no arquivo .env
load_dotenv(find_dotenv(filename=".env", usecwd=True))

def conectar_bd():
    """Conecta ao banco de dados usando as credenciais do .env via pyodbc."""
    driver = os.getenv("DB_DRIVER", "PostgreSQL Unicode(x64)")
    server = os.getenv("DB_SERVER", "altaria.proxy.rlwy.net")
    port = os.getenv("DB_PORT", "28633")
    database = os.getenv("DB_DATABASE", "railway")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    conn_str = f"DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={password};"
    return pyodbc.connect(conn_str)


def criar_tabela():
    """Cria a tabela 'livros' no banco de dados se ela ainda não existir."""
    sql = """
    CREATE TABLE IF NOT EXISTS livros (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(150) NOT NULL,
        autor VARCHAR(100) NOT NULL,
        ano INT NOT NULL,
        preco NUMERIC(10, 2) NOT NULL
    );
    """
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        conn.close()
        print("-> Tabela 'livros' verificada/criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")


# ==========================================
# OPERAÇÕES DE CRUD (Create, Read, Update, Delete)
# ==========================================

def cadastrar_livro(titulo, autor, ano, preco):
    """CREATE: Insere um novo livro no banco de dados."""
    sql = "INSERT INTO livros (titulo, autor, ano, preco) VALUES (?, ?, ?, ?)"
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(sql, (titulo, autor, ano, preco))
        conn.commit()
        conn.close()
        print("\nLivro cadastrado com sucesso!")
    except Exception as e:
        print(f"\nErro ao cadastrar livro: {e}")


def listar_livros():
    """READ: Consulta e exibe todos os livros cadastrados."""
    sql = "SELECT id, titulo, autor, ano, preco FROM livros ORDER BY id DESC"
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\nNenhum livro encontrado.")
            return []

        print("\n" + "=" * 60)
        print(f"{'ID':<5} | {'Título':<25} | {'Autor':<15} | {'Ano':<6} | {'Preço (R$)':<10}")
        print("-" * 60)
        for row in rows:
            livro_id, titulo, autor, ano, preco = row
            print(f"{livro_id:<5} | {titulo:<25} | {autor:<15} | {ano:<6} | R$ {float(preco):<8.2f}")
        print("=" * 60)
        return rows
    except Exception as e:
        print(f"\nErro ao listar livros: {e}")
        return []


def atualizar_livro(livro_id, titulo, autor, ano, preco):
    """UPDATE: Atualiza as informações de um livro existente pelo ID."""
    sql = "UPDATE livros SET titulo = ?, autor = ?, ano = ?, preco = ? WHERE id = ?"
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(sql, (titulo, autor, ano, preco, livro_id))
        conn.commit()
        linhas_afetadas = cursor.rowcount
        conn.close()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} atualizado com sucesso!")
        else:
            print(f"\nNenhum livro encontrado com o ID {livro_id}.")
    except Exception as e:
        print(f"\nErro ao atualizar livro: {e}")


def excluir_livro(livro_id):
    """DELETE: Remove um livro do banco de dados pelo ID."""
    sql = "DELETE FROM livros WHERE id = ?"
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(sql, (livro_id,))
        conn.commit()
        linhas_afetadas = cursor.rowcount
        conn.close()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} excluído com sucesso!")
        else:
            print(f"\nNenhum livro encontrado com o ID {livro_id}.")
    except Exception as e:
        print(f"\nErro ao excluir livro: {e}")


# ==========================================
# MENU INTERATIVO NO TERMINAL
# ==========================================

def menu():
    """Exibe o menu interativo para o usuário interagir com o CRUD."""
    criar_tabela()

    while True:
        print("\n--- MENU CRUD ODBC (PYTHON) ---")
        print("1. Listar Livros")
        print("2. Cadastrar Novo Livro")
        print("3. Atualizar Livro")
        print("4. Excluir Livro")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            listar_livros()

        elif opcao == "2":
            print("\n--- CADASTRO DE LIVRO ---")
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            try:
                ano = int(input("Ano de publicação: "))
                preco = float(input("Preço (R$): "))
                cadastrar_livro(titulo, autor, ano, preco)
            except ValueError:
                print("Ano ou preço inválidos. Digite valores numéricos.")

        elif opcao == "3":
            print("\n--- ATUALIZAR LIVRO ---")
            try:
                livro_id = int(input("ID do livro que deseja atualizar: "))
                titulo = input("Novo Título: ").strip()
                autor = input("Novo Autor: ").strip()
                ano = int(input("Novo Ano: "))
                preco = float(input("Novo Preço (R$): "))
                atualizar_livro(livro_id, titulo, autor, ano, preco)
            except ValueError:
                print("ID, Ano ou Preço inválidos. Use apenas números.")

        elif opcao == "4":
            print("\n--- EXCLUIR LIVRO ---")
            try:
                livro_id = int(input("ID do livro que deseja excluir: "))
                excluir_livro(livro_id)
            except ValueError:
                print("Digite um ID numérico válido.")

        elif opcao == "0":
            print("\nEncerrando o programa. Até logo!")
            break

        else:
            print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    menu()
