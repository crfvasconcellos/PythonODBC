"""
Módulo de Programação no Lado do Banco de Dados:
Stored Functions, Stored Procedures, Triggers e Consultas Recursivas (WITH RECURSIVE).
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def chamar_function_total_por_autor(autor: str) -> int | None:
    """
    [CONCEITO AVALIADO] Chamada de Stored Function no PostgreSQL (SELECT func())
    [SLIDE/CAPÍTULO] Cap. 5 (SQL Avançado - Funções)
    [DESCRIÇÃO] Invoca a função fn_contar_livros_por_autor passando o autor via
                Prepared Statement para retornar o total de obras.
    """
    sql = "SELECT fn_contar_livros_por_autor(CAST(? AS VARCHAR)) AS total;"
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (autor,))
            row = cursor.fetchone()
            return int(row[0]) if row else 0
    except pyodbc.Error as erro:
        print(f"[ERRO FUNCTION] {erro}")
        return None
    finally:
        if conn:
            conn.close()


def chamar_procedure_cadastrar_livro(
    nome: str,
    autor: str,
    genero: str,
    exemplares: int,
    pode_emprestar: bool,
    id_estante: int,
) -> bool:
    """
    [CONCEITO AVALIADO] Chamada de Stored Procedure no PostgreSQL (CALL proc())
    [SLIDE/CAPÍTULO] Cap. 5 (SQL Avançado - Procedimentos Armazenados)
    [DESCRIÇÃO] Executa a procedure sp_cadastrar_livro com controle transacional manual.
    """
    sql = """
        CALL sp_cadastrar_livro(
            CAST(? AS VARCHAR), CAST(? AS VARCHAR), CAST(? AS VARCHAR),
            CAST(? AS INT), CAST(? AS BOOLEAN), CAST(? AS INT)
        );
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (nome, autor, genero, int(exemplares), bool(pode_emprestar), int(id_estante)))
        conn.commit()
        return True
    except pyodbc.Error as erro:
        if conn:
            conn.rollback()
        print(f"[ERRO PROCEDURE] {erro}")
        return False
    finally:
        if conn:
            conn.close()


def demonstrar_trigger_auditoria_exclusao(id_livro: int) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Gatilhos (Triggers) - Auditoria Automática em DELETE
    [SLIDE/CAPÍTULO] Cap. 5 (SQL Avançado - Gatilhos / Triggers)
    [DESCRIÇÃO] Exclui um livro (disparando o trigger AFTER DELETE) e consulta a tabela
                biblioteca.auditoria_livros_excluidos para comprovar o registro automático.
    """
    sql_delete = "DELETE FROM biblioteca.livros WHERE id_livro = ?;"
    sql_audit = """
        SELECT id_auditoria, id_livro_apagado, nome_livro, autor, data_exclusao, usuario_banco
        FROM biblioteca.auditoria_livros_excluidos
        ORDER BY id_auditoria DESC
        LIMIT 5;
    """
    # TODO: Executar DELETE + commit() e retornar o SELECT da tabela de auditoria
    _ = (sql_delete, sql_audit, id_livro)
    return None


def consulta_recursiva_hierarquia_biblioteca() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Consultas Recursivas (WITH RECURSIVE)
    [SLIDE/CAPÍTULO] Cap. 5 (SQL Avançado - Consultas Recursivas)
    [DESCRIÇÃO] Demonstra uma CTE recursiva percorrendo níveis hierárquicos ou
                série de capacidade dos pisos/estantes da biblioteca.
    """
    sql = """
        WITH RECURSIVE niveis_piso AS (
            -- Caso base: piso inicial
            SELECT id_pisos, id_endereco, capacidade_maxima, 1 AS nivel
            FROM biblioteca.pisos
            WHERE id_pisos = (SELECT MIN(id_pisos) FROM biblioteca.pisos)

            UNION ALL

            -- Passo recursivo: próximo piso na sequência
            SELECT p.id_pisos, p.id_endereco, p.capacidade_maxima, np.nivel + 1
            FROM biblioteca.pisos p
            INNER JOIN niveis_piso np ON p.id_pisos = np.id_pisos + 1
            WHERE np.nivel < 10
        )
        SELECT * FROM niveis_piso;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None
