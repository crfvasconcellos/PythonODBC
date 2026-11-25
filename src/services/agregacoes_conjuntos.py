"""
Módulo de Funções de Agregação, Agrupamento e Operações de Conjuntos.
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def estatisticas_por_genero_com_having(media_minima: float) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Funções de Agregação (COUNT, SUM, AVG, MIN, MAX), GROUP BY e HAVING
    [SLIDE/CAPÍTULO] Cap. 3 (Funções de Agregação e Cláusula HAVING)
    [DESCRIÇÃO] Agrupa livros por gênero calculando total de títulos, soma, média, mínimo
                e máximo de exemplares, filtrando grupos cuja média supere media_minima.
    """
    sql = """
        SELECT genero,
               COUNT(id_livro)           AS total_titulos,
               SUM(numero_de_exemplares) AS soma_exemplares,
               AVG(numero_de_exemplares) AS media_exemplares,
               MIN(numero_de_exemplares) AS minimo_exemplares,
               MAX(numero_de_exemplares) AS maximo_exemplares
        FROM biblioteca.livros
        WHERE genero IS NOT NULL
        GROUP BY genero
        HAVING AVG(numero_de_exemplares) > ?
        ORDER BY media_exemplares DESC;
    """
    # Placeholder com Prepared Statement:
    # cursor.execute(sql, (float(media_minima),))
    _ = (sql, media_minima)
    return None


def conjunto_union_dominios_estantes() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Operação de Conjunto - UNION (União)
    [SLIDE/CAPÍTULO] Cap. 3 (Operações de Conjunto: UNION)
    [DESCRIÇÃO] Unifica em uma única relação todos os domínios cadastrados tanto
                no lado 1 quanto no lado 2 das estantes, eliminando duplicatas.
    """
    sql = """
        SELECT dominio_lado_1 AS dominio FROM biblioteca.estantes WHERE dominio_lado_1 IS NOT NULL
        UNION
        SELECT dominio_lado_2 AS dominio FROM biblioteca.estantes WHERE dominio_lado_2 IS NOT NULL
        ORDER BY dominio ASC;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def conjunto_intersect_autores_multigenero(genero1: str, genero2: str) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Operação de Conjunto - INTERSECT (Interseção)
    [SLIDE/CAPÍTULO] Cap. 3 (Operações de Conjunto: INTERSECT)
    [DESCRIÇÃO] Retorna autores que possuem obras cadastradas simultaneamente
                nos dois gêneros informados.
    """
    sql = """
        SELECT autor FROM biblioteca.livros WHERE genero = ?
        INTERSECT
        SELECT autor FROM biblioteca.livros WHERE genero = ?;
    """
    # Placeholder com Prepared Statement:
    # cursor.execute(sql, (genero1, genero2))
    _ = (sql, genero1, genero2)
    return None


def conjunto_except_estantes_vazias() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Operação de Conjunto - EXCEPT (Diferença)
    [SLIDE/CAPÍTULO] Cap. 3 (Operações de Conjunto: EXCEPT)
    [DESCRIÇÃO] Lista as estantes cadastradas que não possuem nenhum livro associado.
    """
    sql = """
        SELECT id_estante, dominio_lado_1 FROM biblioteca.estantes
        EXCEPT
        SELECT e.id_estante, e.dominio_lado_1
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.livros l ON e.id_estante = l.id_estante
        ORDER BY id_estante;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None
