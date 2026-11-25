"""
Módulo de Junções Explícitas (JOINs), Visões Tradicionais (Views)
e Visões Materializadas (Materialized Views + REFRESH).
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def juncao_natural_livros_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Junção Natural (NATURAL JOIN)
    [SLIDE/CAPÍTULO] Cap. 4 (SQL Intermediário - Expressões de Junção)
    [DESCRIÇÃO] Une automaticamente biblioteca.livros e biblioteca.estantes pela coluna
                comum (id_estante), retornando o título do livro e o tipo da estante.
    """
    sql = """
        SELECT nome, tipo
        FROM biblioteca.livros
        NATURAL JOIN biblioteca.estantes
        ORDER BY nome;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def juncao_inner_estantes_espacos() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Junção Interna Explícita (INNER JOIN ... ON)
    [SLIDE/CAPÍTULO] Cap. 4 (SQL Intermediário - INNER JOIN)
    [DESCRIÇÃO] Retorna apenas estantes que possuem um espaço correspondente.
    """
    sql = """
        SELECT e.id_estante, e.dominio_lado_1, e.tipo, esp.id_espaco, esp.numero_de_espacos
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.espacos esp ON e.id_espaco = esp.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def juncao_left_outer_espacos_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Junção Externa à Esquerda (LEFT OUTER JOIN)
    [SLIDE/CAPÍTULO] Cap. 4 (SQL Intermediário - Outer Joins)
    [DESCRIÇÃO] Mantém todos os espaços, inclusive os que não possuem estantes (colunas NULL).
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos, e.id_estante, e.dominio_lado_1, e.tipo
        FROM biblioteca.espacos esp
        LEFT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def juncao_right_outer_espacos_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Junção Externa à Direita (RIGHT OUTER JOIN)
    [SLIDE/CAPÍTULO] Cap. 4 (SQL Intermediário - Outer Joins)
    [DESCRIÇÃO] Mantém todas as estantes, preservando a relação à direita da junção.
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos, e.id_estante, e.dominio_lado_1, e.tipo
        FROM biblioteca.espacos esp
        RIGHT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY e.id_estante;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def juncao_full_outer_espacos_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Junção Externa Completa (FULL OUTER JOIN)
    [SLIDE/CAPÍTULO] Cap. 4 (SQL Intermediário - Outer Joins)
    [DESCRIÇÃO] Preserva todos os espaços e todas as estantes, preenchendo com NULL
                o lado sem correspondência.
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos, e.id_estante, e.dominio_lado_1, e.tipo
        FROM biblioteca.espacos esp
        FULL OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def consultar_visao_localizacao_completa() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Consumo de Visão Tradicional (VIEW)
    [SLIDE/CAPÍTULO] Cap. 4 (Visões / Views)
    [DESCRIÇÃO] Consulta a view biblioteca.vw_livros_localizacao_completa, que encapsula
                7 tabelas (de livros até biblioteca/diretoria).
    """
    sql = "SELECT * FROM biblioteca.vw_livros_localizacao_completa ORDER BY id_livro;"
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def consultar_visao_materializada_ranking_autores() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Consumo de Visão Materializada (MATERIALIZED VIEW)
    [SLIDE/CAPÍTULO] Cap. 4 (Visões Materializadas)
    [DESCRIÇÃO] Lê os dados pré-computados da visão materializada de ranking de autores.
    """
    sql = "SELECT * FROM biblioteca.mv_ranking_autores_maior_acervo;"
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def atualizar_visao_materializada(nome_mv: str = "mv_ranking_autores_maior_acervo") -> bool:
    """
    [CONCEITO AVALIADO] Atualização de Visão Materializada (REFRESH MATERIALIZED VIEW)
    [SLIDE/CAPÍTULO] Cap. 4 (Manutenção de Visões Materializadas)
    [DESCRIÇÃO] Recalcula e atualiza fisicamente uma visão materializada permitida (whitelist),
                com controle manual de transação.
    """
    mvs_permitidas = {
        "mv_ranking_autores_maior_acervo",
        "mv_estatisticas_por_edificacao",
        "mv_ocupacao_estantes_livros",
        "mv_relatorio_completo_hierarquia",
    }
    if nome_mv not in mvs_permitidas:
        raise ValueError(f"Visão materializada não autorizada: {nome_mv}")

    sql = f"REFRESH MATERIALIZED VIEW biblioteca.{nome_mv};"
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
        conn.commit()
        return True
    except pyodbc.Error as erro:
        if conn:
            conn.rollback()
        print(f"[ERRO REFRESH MV] {erro}")
        return False
    finally:
        if conn:
            conn.close()
