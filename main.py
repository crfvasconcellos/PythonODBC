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
    """Verifica a tabela 'livros' no schema 'biblioteca'."""
    sql = """
    CREATE SCHEMA IF NOT EXISTS biblioteca;
    CREATE TABLE IF NOT EXISTS biblioteca.livros (
        id_livro SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        numero_de_exemplares INT CHECK (numero_de_exemplares >= 0),
        pode_ser_emprestado BOOLEAN DEFAULT TRUE,
        autor VARCHAR(255),
        genero VARCHAR(100),
        id_estante INT NOT NULL REFERENCES biblioteca.estantes(id_estante) ON DELETE CASCADE
    );
    """
    try:
        with conectar_bd() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
            conn.commit()
        print("-> Tabela 'biblioteca.livros' verificada com sucesso.")
    except Exception:
        pass


# ==========================================
# OPERAÇÕES DE CRUD (Create, Read, Update, Delete)
# ==========================================

def cadastrar_livro(nome, autor, genero="Geral", numero_de_exemplares=1, pode_ser_emprestado=True, id_estante=1):
    """CREATE: Insere um novo livro no schema biblioteca."""
    if isinstance(genero, (int, float)) and isinstance(numero_de_exemplares, (int, float)):
        genero, numero_de_exemplares, id_estante = "Geral", 1, 1

    sql = """
    INSERT INTO biblioteca.livros 
        (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante) 
    VALUES (?, ?, ?, ?, ?, ?)
    """
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, autor, str(genero), int(numero_de_exemplares), bool(pode_ser_emprestado), int(id_estante)))
        conn.commit()
        print("\nLivro cadastrado com sucesso no schema 'biblioteca'!")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao cadastrar livro: {e}")
    finally:
        conn.close()


def listar_livros():
    """READ: Consulta e exibe todos os livros cadastrados no schema biblioteca."""
    sql = """
    SELECT id_livro, nome, autor, genero
    FROM biblioteca.livros 
    ORDER BY id_livro ASC
    """
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        if not rows:
            print("\nNenhum livro encontrado no schema 'biblioteca'.")
            return []

        print("\n" + "=" * 80)
        print(f"{'ID':<5} | {'Título':<35} | {'Autor':<22} | {'Gênero':<15}")
        print("-" * 80)
        for row in rows:
            livro_id, nome, autor, genero = row
            print(f"{livro_id:<5} | {str(nome)[:35]:<35} | {str(autor or '-')[ :22]:<22} | {str(genero or '-')[ :15]:<15}")
        print("=" * 80)
        return rows
    except Exception as e:
        print(f"\nErro ao listar livros do schema 'biblioteca': {e}")
        return []
    finally:
        conn.close()


def atualizar_livro(livro_id, nome, autor, genero="Geral", numero_de_exemplares=1):
    """UPDATE: Atualiza as informações de um livro existente pelo ID (id_livro)."""
    if isinstance(genero, (int, float)) and isinstance(numero_de_exemplares, (int, float)):
        genero, numero_de_exemplares = "Geral", 1

    sql = """
    UPDATE biblioteca.livros 
    SET nome = ?, autor = ?, genero = ?, numero_de_exemplares = ? 
    WHERE id_livro = ?
    """
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, autor, str(genero), int(numero_de_exemplares), livro_id))
            linhas_afetadas = cursor.rowcount
        conn.commit()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} atualizado com sucesso no schema 'biblioteca'!")
        else:
            print(f"\nNenhum livro encontrado com o ID {livro_id}.")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao atualizar livro: {e}")
    finally:
        conn.close()


def excluir_livro(livro_id):
    """DELETE: Remove um livro do banco de dados pelo ID (id_livro)."""
    sql = "DELETE FROM biblioteca.livros WHERE id_livro = ?"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (livro_id,))
            linhas_afetadas = cursor.rowcount
        conn.commit()

        if linhas_afetadas > 0:
            print(f"\nLivro ID {livro_id} excluído com sucesso do schema 'biblioteca'!")
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

SQL_FN_CONTAR_LIVROS_POR_AUTOR = """
CREATE OR REPLACE FUNCTION fn_contar_livros_por_autor(p_autor VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total
    FROM biblioteca.livros
    WHERE autor ILIKE '%' || p_autor || '%';

    RETURN total;
END;
$$ LANGUAGE plpgsql;
"""

SQL_SP_CADASTRAR_LIVRO = """
CREATE OR REPLACE PROCEDURE sp_cadastrar_livro(
    p_nome VARCHAR,
    p_autor VARCHAR,
    p_genero VARCHAR,
    p_exemplares INT,
    p_emprestavel BOOLEAN,
    p_id_estante INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO biblioteca.livros (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante)
    VALUES (p_nome, p_autor, p_genero, p_exemplares, p_emprestavel, p_id_estante);
END;
$$;
"""


def criar_funcoes():
    """Cria a function e a procedure do capítulo 5 se ainda não existirem."""
    scripts = [
        ("Function 'fn_contar_livros_por_autor'", SQL_FN_CONTAR_LIVROS_POR_AUTOR),
        ("Procedure 'sp_cadastrar_livro'", SQL_SP_CADASTRAR_LIVRO),
    ]
    conn = None
    try:
        conn = conectar_bd()
        for nome, sql in scripts:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
            except Exception as e:
                conn.rollback()
    except Exception as e:
        pass
    finally:
        if conn is not None:
            conn.close()


def consultar_total_por_autor(autor):
    """Consulta quantos livros de um autor existem, chamando a function do banco."""
    sql = "SELECT * FROM fn_contar_livros_por_autor(?)"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (autor,))
            total = cursor.fetchone()[0]
        print(f"\nO autor '{autor}' tem {total} livro(s) cadastrado(s) no schema 'biblioteca'.")
    except Exception as e:
        print(f"\nErro ao consultar função: {e}")
    finally:
        conn.close()


def cadastrar_livro_via_procedure(nome, autor, genero="Geral", exemplares=1, pode_emprestar=True, id_estante=1):
    """Cadastra um livro chamando a procedure do banco no schema biblioteca."""
    sql = "CALL sp_cadastrar_livro(?, ?, ?, ?, ?, ?)"
    conn = conectar_bd()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, autor, genero, exemplares, pode_emprestar, id_estante))
        conn.commit()
        print("\nLivro cadastrado com sucesso via PROCEDURE no schema 'biblioteca'!")
    except Exception as e:
        conn.rollback()
        print(f"\nErro ao cadastrar via procedure: {e}")
    finally:
        conn.close()


# ==========================================
# CONSULTAS COM JOIN (Atividade 3)
# ==========================================
# Estas consultas usam as tabelas do schema 'biblioteca' (atividade 1:
# livros, estantes e espacos). Por isso o nome do schema vem escrito em todas
# elas (biblioteca.livros etc.), assim não se confundem com a tabela 'livros'
# simples do schema public usada no CRUD acima. Precisam que o banco já tenha
# sido montado com o banco_biblioteca.sql (ou aplicar_scripts_docente.py);
# se não tiver, o programa avisa em vez de dar erro.

def _fetch_as_dicts(cursor):
    """Converte o resultado do cursor em uma lista de dicionários {coluna: valor}."""
    colunas = [coluna[0] for coluna in cursor.description]
    return [dict(zip(colunas, row)) for row in cursor.fetchall()]


def _executar_consulta(sql, params=None):
    """Executa um SELECT do schema 'biblioteca' e devolve a lista de dicionários.

    Devolve None se não for possível executar (banco fora do ar, tabelas do
    schema 'biblioteca' inexistentes, erro de SQL), já avisando o motivo.
    """
    sql_verifica = (
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = 'biblioteca' "
        "AND table_name IN ('livros', 'estantes', 'espacos')"
    )
    conn = None
    try:
        conn = conectar_bd()
        with conn.cursor() as cursor:
            cursor.execute(sql_verifica)
            if cursor.fetchone()[0] < 3:
                print("\nAs tabelas do schema 'biblioteca' (livros, estantes, espacos) "
                      "não foram encontradas neste banco.")
                print("Execute primeiro 'python aplicar_scripts_docente.py' para inicializar a base da biblioteca.")
                return None
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return _fetch_as_dicts(cursor)
    except Exception as e:
        print(f"\nErro ao executar a consulta: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()


def _formatar_valor(valor):
    """Texto de uma célula; mostra NULL quando o valor é None (útil nos OUTER JOINs)."""
    return "NULL" if valor is None else str(valor)


def exibir_resultado_join(titulo, linhas):
    """Mostra no terminal, em forma de tabela, o resultado de uma consulta JOIN."""
    print(f"\n--- {titulo} ---")
    if not linhas:
        print("Nenhum registro retornado.")
        return

    colunas = list(linhas[0].keys())
    larguras = [
        max([len(coluna)] + [len(_formatar_valor(linha[coluna])) for linha in linhas])
        for coluna in colunas
    ]

    cabecalho = " | ".join(c.ljust(w) for c, w in zip(colunas, larguras))
    print(cabecalho)
    print("-" * len(cabecalho))
    for linha in linhas:
        print(" | ".join(_formatar_valor(linha[c]).ljust(w) for c, w in zip(colunas, larguras)))
    print(f"({len(linhas)} registro(s))")


def listar_livros_natural_join():
    """
    NATURAL JOIN entre 'livros' e 'estantes' (schema biblioteca).

    'id_estante' e a unica coluna com o mesmo nome nas duas tabelas,
    entao o NATURAL JOIN une automaticamente por ela (sem precisar de
    ON) e devolve apenas uma copia dessa coluna comum.

    Equivalente a:
        SELECT nome, tipo
        FROM biblioteca.livros, biblioteca.estantes
        WHERE livros.id_estante = estantes.id_estante;
    """
    sql = """
        SELECT nome, tipo
        FROM biblioteca.livros
        NATURAL JOIN biblioteca.estantes
        ORDER BY nome;
    """
    return _executar_consulta(sql)


def listar_estantes_inner_join_espacos():
    """
    INNER JOIN entre 'estantes' e 'espacos' usando ON.

    Diferente do NATURAL JOIN, aqui a condicao de igualdade e escrita
    explicitamente, o que deixa claro qual coluna liga as duas
    tabelas (aqui, id_espaco). So retorna estantes que possuem um
    espaco correspondente.
    """
    sql = """
        SELECT e.id_estante, e.dominio_lado_1, e.dominio_lado_2,
               e.tipo, esp.id_espaco, esp.numero_de_espacos
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.espacos esp ON e.id_espaco = esp.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    return _executar_consulta(sql)


def listar_espacos_left_outer_join():
    """
    LEFT OUTER JOIN: mantem TODAS as linhas de 'espacos', mesmo os
    que ainda nao tem nenhuma estante cadastrada (colunas de
    estantes aparecem como NULL nesse caso).
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        LEFT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco;
    """
    return _executar_consulta(sql)


def listar_espacos_right_outer_join():
    """
    RIGHT OUTER JOIN: mantem TODAS as linhas de 'estantes', mesmo que
    exista alguma sem 'espaco' correspondente (nao deveria acontecer,
    ja que id_espaco e NOT NULL em estantes, mas a consulta continua
    valida e serve de comparacao com o LEFT JOIN).
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        RIGHT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY e.id_estante;
    """
    return _executar_consulta(sql)


def listar_espacos_full_outer_join():
    """
    FULL OUTER JOIN: uniao do resultado do LEFT com o do RIGHT --
    mantem todas as linhas de 'espacos' E todas as linhas de
    'estantes', preenchendo com NULL o lado que nao tiver
    correspondencia.
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        FULL OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    return _executar_consulta(sql)


def menu_joins():
    """Submenu com as consultas JOIN da Atividade 3."""
    consultas = {
        "1": ("NATURAL JOIN (livros x estantes)", listar_livros_natural_join),
        "2": ("INNER JOIN (estantes x espaços)", listar_estantes_inner_join_espacos),
        "3": ("LEFT OUTER JOIN (espaços x estantes)", listar_espacos_left_outer_join),
        "4": ("RIGHT OUTER JOIN (espaços x estantes)", listar_espacos_right_outer_join),
        "5": ("FULL OUTER JOIN (espaços x estantes)", listar_espacos_full_outer_join),
    }

    while True:
        print("\n--- CONSULTAS COM JOIN (schema biblioteca) ---")
        for chave, (titulo, _) in consultas.items():
            print(f"{chave}. {titulo}")
        print("0. Voltar ao menu principal")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "0":
            break
        elif opcao in consultas:
            titulo, consulta = consultas[opcao]
            linhas = consulta()
            if linhas is not None:  # None = já avisou o erro, não mostra tabela
                exibir_resultado_join(titulo, linhas)
        else:
            print("\nOpção inválida, tente novamente.")

# ==========================================
# CONSULTAS COM CAP 3
# ==========================================

def relatorio_estatisticas_genero(media_minima):
    """(Cap. 3: AVG, MIN, MAX, HAVING, GROUP BY)"""
    sql = """
        SELECT genero, 
               AVG(numero_de_exemplares) AS media_exemplares,
               MIN(numero_de_exemplares) AS minimo_exemplares,
               MAX(numero_de_exemplares) AS maximo_exemplares
        FROM biblioteca.livros
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
        FROM biblioteca.livros
        WHERE nome ILIKE ? OR autor ILIKE ?
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
        SELECT id_estante, dominio_lado_1 FROM biblioteca.estantes
        EXCEPT
        SELECT e.id_estante, e.dominio_lado_1
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.livros l ON e.id_estante = l.id_estante;
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
            SELECT id_estante FROM biblioteca.estantes WHERE dominio_lado_1 = ?
        )
        SELECT sub.nome, sub.numero_de_exemplares
        FROM (SELECT id_livro, nome, numero_de_exemplares, id_estante, genero FROM biblioteca.livros) AS sub
        WHERE sub.id_estante IN (SELECT id_estante FROM Estantes_Alvo)
          AND sub.numero_de_exemplares > SOME (SELECT numero_de_exemplares FROM biblioteca.livros WHERE genero = ?)
          AND EXISTS (SELECT 1 FROM biblioteca.estantes e WHERE e.id_estante = sub.id_estante);
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

def listar_autores_unicos():
    """Demonstração do DISTINCT (Capítulo 3)"""
    print("\n--- Lista de Autores Únicos (DISTINCT) ---")
    sql = """
        SELECT DISTINCT autor 
        FROM biblioteca.livros 
        WHERE autor IS NOT NULL
        ORDER BY autor ASC;
    """
    rows = _executar_consulta(sql)
    if rows:
        for row in rows:
            print(f"- {row.get('autor')}")
    else:
        print("Nenhum autor encontrado.")


def buscar_livros_por_faixa_exemplares(minimo, maximo):
    """Demonstração do BETWEEN (Capítulo 3)"""
    print(f"\n--- Livros com exemplares entre {minimo} e {maximo} (BETWEEN) ---")
    sql = """
        SELECT nome, autor, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares BETWEEN ? AND ?
        ORDER BY numero_de_exemplares DESC;
    """
    rows = _executar_consulta(sql, (minimo, maximo))
    if rows:
        print(f"| {'Título':<35} | {'Autor':<20} | {'Exemplares':<10} |")
        print("-" * 75)
        for row in rows:
            print(f"| {str(row.get('nome', ''))[:35]:<35} | {str(row.get('autor', ''))[:20]:<20} | {int(row.get('numero_de_exemplares', 0)):<10} |")
    else:
        print("Nenhum livro encontrado nesta faixa de exemplares.")


def relatorio_autores_multigenero(genero1, genero2):
    """Demonstração do INTERSECT (Capítulo 3)"""
    print(f"\n--- Autores que escrevem '{genero1}' e também '{genero2}' (INTERSECT) ---")
    sql = """
        SELECT autor FROM biblioteca.livros WHERE genero = ?
        INTERSECT
        SELECT autor FROM biblioteca.livros WHERE genero = ?;
    """
    rows = _executar_consulta(sql, (genero1, genero2))
    if rows:
        for row in rows:
            print(f"- {row.get('autor')}")
    else:
        print(f"Nenhum autor transita entre os gêneros {genero1} e {genero2}.")

# ==========================================
# MENU INTERATIVO NO TERMINAL
# ==========================================

def menu():
    """Exibe o menu interativo para o usuário interagir com o CRUD."""
    criar_tabela()
    criar_funcoes()

    while True:
        print("\n--- MENU CRUD ODBC (PYTHON) ---")
        print("1. Listar Livros")
        print("2. Cadastrar Novo Livro")
        print("3. Atualizar Livro")
        print("4. Excluir Livro")
        print("5. Consultar total de livros por autor (FUNCTION)")
        print("6. Cadastrar livro via PROCEDURE")
        print("7. Consultas com JOIN (Atividade 3 - schema biblioteca)")
        print("8. Relatório Gerencial: Estatísticas por Gênero")
        print("9. Buscar no Catálogo Completo (Palavra-chave)")
        print("10. Auditoria: Listar Estantes Vazias")
        print("11. Análise de Acervo Crítico")
        print("12. Listar Autores Únicos")
        print("13. Buscar Livros por Faixa de Exemplares")
        print("14. Relatório de Autores Multigênero")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            listar_livros()

        elif opcao == "2":
            print("\n--- CADASTRO DE LIVRO ---")
            nome = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Gênero: ").strip() or "Geral"
            cadastrar_livro(nome, autor, genero)

        elif opcao == "3":
            print("\n--- ATUALIZAR LIVRO ---")
            try:
                livro_id = int(input("ID do livro que deseja atualizar: "))
                nome = input("Novo Título: ").strip()
                autor = input("Novo Autor: ").strip()
                genero = input("Novo Gênero: ").strip() or "Geral"
                atualizar_livro(livro_id, nome, autor, genero)
            except ValueError:
                print("ID numérico inválido.")

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
            nome = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Gênero: ").strip() or "Geral"
            cadastrar_livro_via_procedure(nome, autor, genero)

        elif opcao == "7":
            menu_joins()

        elif opcao == "8":
            print("\n--- RELATÓRIO: ESTATÍSTICAS POR GÊNERO ---")
            try:
                media_min = float(input("Filtrar gêneros com média de exemplares maior que: "))
                relatorio_estatisticas_genero(media_min)
            except ValueError:
                print("Valor inválido. Digite um número.")

        elif opcao == "9":
            print("\n--- BUSCA NO CATÁLOGO COMPLETO ---")
            termo = input("Digite a palavra-chave (título ou autor): ").strip()
            buscar_catalogo_palavra_chave(termo)

        elif opcao == "10":
            print("\n--- AUDITORIA: ESTANTES VAZIAS (SEM LIVROS) ---")
            print("Iniciando varredura no acervo...")
            auditoria_estantes_vazias()

        elif opcao == "11":
            print("\n--- ANÁLISE DE ACERVO CRÍTICO ---")
            print("Dica: Compara se as obras de um gênero superam os exemplares de outro.")
            gen_alvo = input("Gênero alvo da análise (ex: Ficção Científica): ").strip()
            gen_comp = input("Gênero para comparar (ex: Romance Clássico): ").strip()
            analise_acervo_critico(gen_alvo, gen_comp)

        elif opcao == "12":
            listar_autores_unicos()

        elif opcao == "13":
            print("\n--- Filtro de Exemplares (BETWEEN) ---")
            try:
                minimo = int(input("Digite a quantidade MÍNIMA de exemplares: "))
                maximo = int(input("Digite a quantidade MÁXIMA de exemplares: "))
                
                if minimo > maximo:
                    print("Aviso: O valor mínimo não pode ser maior que o máximo. Invertendo a busca...")
                    buscar_livros_por_faixa_exemplares(maximo, minimo)
                else:
                    buscar_livros_por_faixa_exemplares(minimo, maximo)
            except ValueError:
                print("Erro: Entrada inválida. Por favor, digite apenas números inteiros.")

        elif opcao == "14":
            print("\n--- Busca de Autores Versáteis (INTERSECT) ---")
            genero1 = input("Digite o 1º Gênero (ex: Ficção, Romance, etc.): ").strip()
            genero2 = input("Digite o 2º Gênero (ex: Ficção, Romance, etc.): ").strip()
            
            if genero1 and genero2:
                relatorio_autores_multigenero(genero1, genero2)
            else:
                print("Erro: Os gêneros não podem ser vazios.")

        elif opcao == "0":
            print("\nEncerrando o programa. Até logo!")
            break

        else:
            print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    menu()
else:
    print("\nOpção inválida, tente novamente.")

