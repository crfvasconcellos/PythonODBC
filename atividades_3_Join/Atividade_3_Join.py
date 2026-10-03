import os
import pyodbc
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(filename=".env", usecwd=True))

# =============================================================================
# 1) NATURAL JOIN
# =============================================================================
def listar_livros_natural_join():
    """
    NATURAL JOIN entre 'livros' e 'estantes'.

    'id_estante' e a unica coluna com o mesmo nome nas duas tabelas,
    entao o NATURAL JOIN une automaticamente por ela (sem precisar de
    ON) e devolve apenas uma copia dessa coluna comum.

    Equivalente a:
        SELECT nome, tipo
        FROM livros, estantes
        WHERE livros.id_estante = estantes.id_estante;
    """
    sql = """
        SELECT nome, tipo
        FROM livros
        NATURAL JOIN estantes
        ORDER BY nome;
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return _fetch_as_dicts(cursor)
    finally:
        conn.close()


# =============================================================================
# 2) INNER JOIN (com ON)
# =============================================================================
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
        FROM estantes e
        INNER JOIN espacos esp ON e.id_espaco = esp.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return _fetch_as_dicts(cursor)
    finally:
        conn.close()


# =============================================================================
# 3) LEFT OUTER JOIN
# =============================================================================
def listar_espacos_left_outer_join():
    """
    LEFT OUTER JOIN: mantem TODAS as linhas de 'espacos', mesmo os
    que ainda nao tem nenhuma estante cadastrada (colunas de
    estantes aparecem como NULL nesse caso).
    """
    sql = """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM espacos esp
        LEFT OUTER JOIN estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco;
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return _fetch_as_dicts(cursor)
    finally:
        conn.close()


# =============================================================================
# 4) RIGHT OUTER JOIN
# =============================================================================
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
        FROM espacos esp
        RIGHT OUTER JOIN estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY e.id_estante;
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return _fetch_as_dicts(cursor)
    finally:
        conn.close()


# =============================================================================
# 5) FULL OUTER JOIN
# =============================================================================
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
        FROM espacos esp
        FULL OUTER JOIN estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return _fetch_as_dicts(cursor)
    finally:
        conn.close()
