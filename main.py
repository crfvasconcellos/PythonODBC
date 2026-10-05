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
    conn = pyodbc.connect(conn_str)
    conn.autocommit = False  # já é False por padrão no pyodbc, mas deixo explícito aqui
    return conn


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
        # with fecha a conexão e o cursor sozinho, mesmo se der erro no meio
        with conectar_bd() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        print("-> Tabela 'livros' verificada/criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")


# ==========================================
# OPERAÇÕES DE CRUD (Create, Read, Update, Delete)
# ==========================================

def cadastrar_livro(titulo, autor, ano, preco):
    """CREATE: Insere um novo livro no banco de dados."""
    sql = "INSERT INTO livros (titulo, autor, ano, preco) VALUES (?, ?, ?, ?)"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (titulo, autor, ano, preco))
        conn.commit()
        print("\nLivro cadastrado com sucesso!")
    except Exception as e:
        conn.rollback()  # desfaz a transação se algo falhar no meio
        print(f"\nErro ao cadastrar livro: {e}")
    finally:
        conn.close()


def listar_livros():
    """READ: Consulta e exibe todos os livros cadastrados."""
    sql = "SELECT id, titulo, autor, ano, preco FROM livros ORDER BY id DESC"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            # cursor.description traz nome/tipo de cada coluna retornada
            print("\nMetadados das colunas retornadas:")
            for coluna in cursor.description:
                print(f"  - {coluna[0]}: {coluna[1]}")
            rows = cursor.fetchall()

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
    finally:
        conn.close()


def atualizar_livro(livro_id, titulo, autor, ano, preco):
    """UPDATE: Atualiza as informações de um livro existente pelo ID."""
    sql = "UPDATE livros SET titulo = ?, autor = ?, ano = ?, preco = ? WHERE id = ?"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (titulo, autor, ano, preco, livro_id))
            linhas_afetadas = cursor.rowcount
        conn.commit()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} atualizado com sucesso!")
        else:
            print(f"\nNenhum livro encontrado com o ID {livro_id}.")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao atualizar livro: {e}")
    finally:
        conn.close()


def excluir_livro(livro_id):
    """DELETE: Remove um livro do banco de dados pelo ID."""
    sql = "DELETE FROM livros WHERE id = ?"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (livro_id,))
            linhas_afetadas = cursor.rowcount
        conn.commit()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} excluído com sucesso!")
        else:
            print(f"\nNenhum livro encontrado com o ID {livro_id}.")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao excluir livro: {e}")
    finally:
        conn.close()


# ==========================================
# FUNCTION E PROCEDURE DO BANCO (ver 05_funcoes_cap5.sql)
# ==========================================

def consultar_total_por_autor(autor):
    """Consulta quantos livros de um autor existem, chamando a function do banco."""
    sql = "SELECT * FROM fn_contar_livros_por_autor(?)"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (autor,))
            total = cursor.fetchone()[0]
        print(f"\nO autor '{autor}' tem {total} livro(s) cadastrado(s).")
    except Exception as e:
        print(f"\nErro ao consultar função: {e}")
    finally:
        conn.close()


def cadastrar_livro_via_procedure(titulo, autor, ano, preco):
    """Cadastra um livro chamando a procedure do banco em vez de fazer o INSERT aqui."""
    sql = "CALL sp_cadastrar_livro(?, ?, ?, ?)"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (titulo, autor, ano, preco))
        conn.commit()
        print("\nLivro cadastrado com sucesso via PROCEDURE!")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao cadastrar via procedure: {e}")
    finally:
        conn.close()

def relatorio_estatisticas_genero(media_minima):
    """(Cap. 3: AVG, MIN, MAX, HAVING, GROUP BY)"""
    sql = """
        SELECT genero, 
               AVG(numero_de_exemplares) AS media_exemplares,
               MIN(numero_de_exemplares) AS minimo_exemplares,
               MAX(numero_de_exemplares) AS maximo_exemplares
        FROM livros
        WHERE genero IS NOT NULL
        GROUP BY genero
        HAVING AVG(numero_de_exemplares) > ?;
    """
    conn = conectar_bd()
    conn.autocommit = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (media_minima,))
            
            if cursor.description:
                colunas = [col[0].upper() for col in cursor.description]
                print("\n" + "=" * 80)
                print(f"| {colunas[0]:<25} | {colunas[1]:<15} | {colunas[2]:<10} | {colunas[3]:<10} |")
                print("-" * 80)
                
            rows = cursor.fetchall()
            if not rows:
                print("Nenhum dado encontrado para este filtro.")
                return

            for row in rows:
                print(f"| {str(row[0]):<25} | {float(row[1]):<15.2f} | {int(row[2]):<10} | {int(row[3]):<10} |")
            print("=" * 80)
            
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao gerar estatísticas por gênero: {e}")
    finally:
        conn.close()



def buscar_catalogo_palavra_chave(termo):
    """(Cap. 3: LIKE, UPPER, LOWER, LENGTH, SUBSTRING, ||, ESCAPE, ORDER BY)"""
    busca_like = f"%{termo}%"
    sql = """
        SELECT UPPER(nome) AS titulo_destaque,
               nome || ' (Autor: ' || autor || ')' AS catalogo_completo,
               SUBSTRING(genero FROM 1 FOR 15) AS genero_curto,
               LENGTH(nome) as tamanho_titulo
        FROM livros
        WHERE nome LIKE ? OR autor LIKE ?
        ORDER BY autor ASC, numero_de_exemplares DESC;
    """
    conn = conectar_bd()
    conn.autocommit = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (busca_like, busca_like))
            rows = cursor.fetchall()
            
            print("\n" + "=" * 90)
            print(f"| {'TÍTULO DESTAQUE':<25} | {'CATÁLOGO COMPLETO':<40} | {'GÊNERO':<15} |")
            print("-" * 90)
            
            if not rows:
                print("| Nenhuma obra encontrada com esse termo. ".ljust(89) + "|")
            
            for row in rows:
                print(f"| {str(row[0])[:25]:<25} | {str(row[1])[:40]:<40} | {str(row[2]):<15} |")
            print("=" * 90)
            
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao buscar no catálogo: {e}")
    finally:
        conn.close()



def auditoria_estantes_vazias():
    """(Cap. 3: EXCEPT / Operações de Conjunto)"""
    sql = """
        SELECT id_estante, dominio_lado_1 FROM estantes
        EXCEPT
        SELECT e.id_estante, e.dominio_lado_1
        FROM estantes e
        INNER JOIN livros l ON e.id_estante = l.id_estante;
    """
    conn = conectar_bd()
    conn.autocommit = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            if not rows:
                print("Resultado: Todas as estantes possuem pelo menos um livro associado!")
            else:
                for row in rows:
                    print(f"ID Estante: {row[0]:<5} | Domínio: {row[1]}")
                    
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao realizar auditoria: {e}")
    finally:
        conn.close()


def analise_acervo_critico(genero_alvo, genero_comparacao):
    """(Cap. 3: WITH/CTE, EXISTS, IN, SOME/ALL, Subconsulta no FROM)"""
    sql = """
        WITH Estantes_Alvo AS (
            SELECT id_estante FROM estantes WHERE dominio_lado_1 = ?
        )
        SELECT sub.nome, sub.numero_de_exemplares
        FROM (SELECT id_livro, nome, numero_de_exemplares, id_estante, genero FROM livros) AS sub
        WHERE sub.id_estante IN (SELECT id_estante FROM Estantes_Alvo)
          AND sub.numero_de_exemplares > SOME (SELECT numero_de_exemplares FROM livros WHERE genero = ?)
          AND EXISTS (SELECT 1 FROM estantes e WHERE e.id_estante = sub.id_estante);
    """
    conn = conectar_bd()
    conn.autocommit = False
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (genero_alvo, genero_comparacao))
            rows = cursor.fetchall()
            
            if not rows:
                print("Nenhum livro crítico encontrado nestes parâmetros.")
            else:
                for row in rows:
                    print(f"Obra: {row[0]:<30} | Exemplares: {row[1]}")
                    
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao processar análise crítica: {e}")
    finally:
        conn.close()


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
        print("5. Consultar total de livros por autor (FUNCTION)")
        print("6. Cadastrar livro via PROCEDURE")
        print("7. Relatório Gerencial: Estatísticas por Gênero")
        print("8. Buscar no Catálogo Completo (Palavra-chave)")
        print("9. Auditoria: Listar Estantes Vazias")
        print("10. Análise de Acervo Crítico")
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

        elif opcao == "5":
            print("\n--- CONSULTAR TOTAL POR AUTOR ---")
            autor = input("Nome do autor: ").strip()
            consultar_total_por_autor(autor)

        elif opcao == "6":
            print("\n--- CADASTRAR LIVRO VIA PROCEDURE ---")
            titulo = input("Título: ").strip()
            autor = input("Autor: ").strip()
            try:
                ano = int(input("Ano de publicação: "))
                preco = float(input("Preço (R$): "))
                cadastrar_livro_via_procedure(titulo, autor, ano, preco)
            except ValueError:
                print("Ano ou preço inválidos. Digite valores numéricos.")

        elif opcao == "7":
            print("\n--- RELATÓRIO: ESTATÍSTICAS POR GÊNERO ---")
            try:
                media_min = float(input("Filtrar gêneros com média de exemplares maior que: "))
                relatorio_estatisticas_genero(media_min)
            except ValueError:
                print("Valor inválido. Digite um número.")

        elif opcao == "8":
            print("\n--- BUSCA NO CATÁLOGO COMPLETO ---")
            termo = input("Digite a palavra-chave (título ou autor): ").strip()
            buscar_catalogo_palavra_chave(termo)

        elif opcao == "9":
            print("\n--- AUDITORIA: ESTANTES VAZIAS (SEM LIVROS) ---")
            print("Iniciando varredura no acervo...")
            auditoria_estantes_vazias()

        elif opcao == "10":
            print("\n--- ANÁLISE DE ACERVO CRÍTICO ---")
            print("Dica: Compara se as obras de um gênero superam os exemplares de outro.")
            gen_alvo = input("Gênero alvo da análise (ex: Ficção Científica): ").strip()
            gen_comp = input("Gênero para comparar (ex: Romance Clássico): ").strip()
            analise_acervo_critico(gen_alvo, gen_comp)
            
        elif opcao == "0":
            print("\nEncerrando o programa. Até logo!")
            break

        else:
            print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    menu()