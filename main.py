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
# O texto abaixo é o mesmo do 05_funcoes_cap5.sql. Ele fica aqui para o
# programa criar a function/procedure sozinho (igual faz com a tabela
# 'livros'), então não precisa rodar o .sql antes de usar as opções 5 e 6.
# Trabalham na tabela 'livros' simples do schema public.

SQL_FN_CONTAR_LIVROS_POR_AUTOR = """
CREATE OR REPLACE FUNCTION fn_contar_livros_por_autor(p_autor VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total
    FROM livros
    WHERE autor = p_autor;

    RETURN total;
END;
$$ LANGUAGE plpgsql;
"""

SQL_SP_CADASTRAR_LIVRO = """
CREATE OR REPLACE PROCEDURE sp_cadastrar_livro(
    p_titulo VARCHAR,
    p_autor  VARCHAR,
    p_ano    INT,
    p_preco  NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO livros (titulo, autor, ano, preco)
    VALUES (p_titulo, p_autor, p_ano, p_preco);
END;
$$;
"""


def criar_funcoes():
    """Cria a function e a procedure do capítulo 5 se ainda não existirem.

    Usa CREATE OR REPLACE, então pode rodar toda vez que o programa abre
    sem dar erro (se já existirem, só são recriadas iguais). Se algo falhar
    (ex.: sem permissão), apenas avisa e o resto do programa segue normal.
    """
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
                print(f"-> {nome} verificada/criada com sucesso.")
            except Exception as e:
                conn.rollback()
                print(f"Aviso: não foi possível criar {nome}: {e}")
    except Exception as e:
        print(f"Erro ao criar function/procedure: {e}")
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
        print(f"\nO autor '{autor}' tem {total} livro(s) cadastrado(s).")
    except Exception as e:
        print(f"\nErro ao consultar função: {e}")
    finally:
        conn.close()


def cadastrar_livro_via_procedure(titulo, autor, ano, preco):
    """Cadastra um livro chamando a procedure do banco em vez de fazer o INSERT aqui."""
    # CAST explícito: o driver manda o preço como float (double precision) e o
    # PostgreSQL não converte isso sozinho para NUMERIC na chamada de procedure.
    sql = ("CALL sp_cadastrar_livro("
           "CAST(? AS VARCHAR), CAST(? AS VARCHAR), CAST(? AS INTEGER), CAST(? AS NUMERIC))")
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


def _executar_consulta(sql):
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
                print("Monte o banco da Atividade 1 antes (banco_biblioteca.sql ou "
                      "aplicar_scripts_docente.py).")
                return None
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
            print(f"- {row[0]}")
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
            print(f"| {str(row[0])[:35]:<35} | {str(row[1])[:20]:<20} | {int(row[2]):<10} |")
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
            print(f"- {row[0]}")
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

        elif opcao == '10':
            listar_autores_unicos()

        elif opcao == '11':
            print("\n--- Filtro de Exemplares ---")
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

        elif opcao == '12':
            print("\n--- Busca de Autores Versáteis ---")
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

