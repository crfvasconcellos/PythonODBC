"""
Módulo de Subconsultas Aninhadas (Escalares, IN, SOME/ALL, EXISTS) e CTEs (WITH).
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def subconsulta_escalar_acima_da_media() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Subconsulta Escalar (na cláusula WHERE e/ou SELECT)
    [SLIDE/CAPÍTULO] Cap. 3 (Subconsultas Escalares)
    [DESCRIÇÃO] Lista livros cuja quantidade de exemplares é superior à média global
                de exemplares de toda a biblioteca.
    """
    sql = """
        SELECT nome, autor, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares > (
            SELECT AVG(numero_de_exemplares) FROM biblioteca.livros
        )
        ORDER BY numero_de_exemplares DESC;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def subconsulta_in_not_in_estantes_por_tipo(tipo_espaco: str) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Associação a Conjuntos - Subconsulta com IN / NOT IN
    [SLIDE/CAPÍTULO] Cap. 3 (Subconsultas Aninhadas - Pertinência a Conjunto)
    [DESCRIÇÃO] Retorna livros armazenados em estantes pertencentes a um determinado
                tipo de espaço informado pelo usuário.
    """
    sql = """
        SELECT id_livro, nome, autor, id_estante
        FROM biblioteca.livros
        WHERE id_estante IN (
            SELECT id_estante
            FROM biblioteca.estantes
            WHERE tipo = ?
        )
        ORDER BY nome;
    """
    # Placeholder com Prepared Statement:
    # cursor.execute(sql, (tipo_espaco,))
    _ = (sql, tipo_espaco)
    return None


def subconsulta_some_all_acervo_critico(dominio_alvo: str, genero_comparacao: str) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Comparação de Conjuntos (SOME / ALL) + CTE (WITH) + Subconsulta no FROM
    [SLIDE/CAPÍTULO] Cap. 3 (Cláusula WITH, Comparação SOME/ALL e Relações Derivadas)
    [DESCRIÇÃO] Encontra livros em estantes de um domínio-alvo que possuem mais exemplares
                do que pelo menos um (> SOME) livro do gênero de comparação.
    """
    sql = """
        WITH Estantes_Alvo AS (
            SELECT id_estante
            FROM biblioteca.estantes
            WHERE dominio_lado_1 = ?
        )
        SELECT sub.nome, sub.numero_de_exemplares
        FROM (
            SELECT id_livro, nome, numero_de_exemplares, id_estante, genero
            FROM biblioteca.livros
        ) AS sub
        WHERE sub.id_estante IN (SELECT id_estante FROM Estantes_Alvo)
          AND sub.numero_de_exemplares > SOME (
              SELECT numero_de_exemplares
              FROM biblioteca.livros
              WHERE genero = ?
          );
    """
    # Placeholder com Prepared Statement:
    # cursor.execute(sql, (dominio_alvo, genero_comparacao))
    _ = (sql, dominio_alvo, genero_comparacao)
    return None


def subconsulta_correlacionada_exists_espacos_com_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Subconsulta Correlacionada - EXISTS / NOT EXISTS
    [SLIDE/CAPÍTULO] Cap. 3 (Teste de Relações Vazias - EXISTS / NOT EXISTS)
    [DESCRIÇÃO] Retorna espaços físicos que possuem (EXISTS) ao menos uma estante
                associada (ou, trocando para NOT EXISTS, espaços completamente vazios).
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos, esp.id_pisos
        FROM biblioteca.espacos esp
        WHERE EXISTS (
            SELECT 1
            FROM biblioteca.estantes est
            WHERE est.id_espaco = esp.id_espaco
        )
        ORDER BY esp.id_espaco;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None
