"""
Centralizador Único de Operações de Banco de Dados — Sistema da Biblioteca.

Use Ctrl + F nas tags [CONCEITO] ou [CAPÍTULO] durante a avaliação:
  - Seção 1: CRUD Básico e Integridade (Cap. 1 a 4)
  - Seção 2: Álgebra Relacional e Buscas (Cap. 2 e 3)
  - Seção 3: Subconsultas e Operações de Conjunto (Cap. 3)
  - Seção 4: Agregações, Junções, Visões e Programação no Banco (Cap. 3, 4 e 5)
  - Seção 5: Metadados via ODBC (Cap. 5)
"""
import pyodbc
from db import conectar, transacao


def _para_dicts(cursor) -> list[dict]:
    """Converte as linhas do cursor em lista de dicionários e normaliza booleanos do ODBC."""
    if not cursor.description:
        return []
    colunas = [c[0] for c in cursor.description]
    linhas = [dict(zip(colunas, row)) for row in cursor.fetchall()]
    for linha in linhas:
        if "pode_ser_emprestado" in linha and linha["pode_ser_emprestado"] is not None:
            v = linha["pode_ser_emprestado"]
            linha["pode_ser_emprestado"] = v if isinstance(v, bool) else str(v).lower() in ("true", "1", "t")
    return linhas


# ==============================================================================
# SEÇÃO 1: CRUD BÁSICO E INTEGRIDADE (Cap. 1 a 4)
# ==============================================================================

def listar_livros() -> list[dict]:
    """
    [CONCEITO]: CRUD, SELECT, ORDER BY
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Lista todos os livros cadastrados no schema biblioteca ordenados pelo ID.
    """
    sql = """
        SELECT id_livro, nome, autor, genero, numero_de_exemplares,
               pode_ser_emprestado, status_conservacao, codigo_patrimonio, id_estante
        FROM biblioteca.livros
        ORDER BY id_livro ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def cadastrar_livro(
    nome: str,
    autor: str,
    genero: str,
    numero_de_exemplares: int,
    pode_ser_emprestado: bool,
    id_estante: int,
    codigo_patrimonio: str | None = None,
    status_conservacao: str = "Bom",
) -> None:
    """
    [CONCEITO]: CRUD, INSERT, PREPARED STATEMENT, NOT NULL, UNIQUE, CHECK, DEFAULT
    [CAPÍTULO]: Cap. 3 e Cap. 4
    [DESCRIÇÃO]: Insere novo livro usando Prepared Statement, respeitando restrições de domínio e unicidade.
    """
    sql = """
        INSERT INTO biblioteca.livros
            (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado,
             id_estante, codigo_patrimonio, status_conservacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    with transacao() as cursor:
        cursor.execute(
            sql,
            (
                nome, autor, genero, int(numero_de_exemplares),
                bool(pode_ser_emprestado), int(id_estante),
                codigo_patrimonio, status_conservacao,
            ),
        )


def atualizar_livro(
    id_livro: int,
    nome: str,
    autor: str,
    genero: str,
    numero_de_exemplares: int,
    pode_ser_emprestado: bool,
) -> bool:
    """
    [CONCEITO]: CRUD, UPDATE, PREPARED STATEMENT, TRANSACAO ACID
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Atualiza os dados de um livro existente pelo id_livro.
    """
    sql = """
        UPDATE biblioteca.livros
        SET nome = ?, autor = ?, genero = ?, numero_de_exemplares = ?, pode_ser_emprestado = ?
        WHERE id_livro = ?;
    """
    with transacao() as cursor:
        cursor.execute(
            sql,
            (nome, autor, genero, int(numero_de_exemplares), bool(pode_ser_emprestado), int(id_livro)),
        )
        return cursor.rowcount > 0


def excluir_livro(id_livro: int) -> bool:
    """
    [CONCEITO]: CRUD, DELETE, PREPARED STATEMENT, TRIGGER AUDITORIA
    [CAPÍTULO]: Cap. 3 e Cap. 5
    [DESCRIÇÃO]: Remove um livro pelo id_livro (disparando o gatilho AFTER DELETE de auditoria).
    """
    sql = "DELETE FROM biblioteca.livros WHERE id_livro = ?;"
    with transacao() as cursor:
        cursor.execute(sql, (int(id_livro),))
        return cursor.rowcount > 0


def validar_integridade_ddl() -> list[dict]:
    """
    [CONCEITO]: PRIMARY KEY COMPOSTA, FOREIGN KEY, ON DELETE CASCADE, ON UPDATE CASCADE, SET NULL, SET DEFAULT, UNIQUE, NOT NULL, CHECK, DEFAULT, ALTER TABLE
    [CAPÍTULO]: Cap. 1, Cap. 2, Cap. 3 e Cap. 4
    [DESCRIÇÃO]: Executa testes reais de todas as restrições DDL no PostgreSQL com rollback seguro ao final.
    """
    resultados = []

    def _rodar_teste(nome_teste, fn):
        conn = conectar()
        cursor = conn.cursor()
        try:
            detalhes = fn(cursor, conn)
            ok = all(bool(v) for v in detalhes.values())
            resultados.append({"conceito": nome_teste, "status": "OK" if ok else "FALHA", "detalhes": detalhes})
        finally:
            conn.rollback()
            cursor.close()
            conn.close()

    def _t_pk(cur, conn):
        r = {"pk_simples": False, "pk_composta": False}
        try:
            cur.execute("INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);", (1, "Dup"))
        except pyodbc.IntegrityError:
            r["pk_simples"] = True
            conn.rollback()
        try:
            cur.execute("INSERT INTO biblioteca.livro_tag (id_livro, id_tag) VALUES (?, ?);", (1, 1))
        except pyodbc.IntegrityError:
            r["pk_composta"] = True
            conn.rollback()
        return r

    def _t_unique_not_null(cur, conn):
        r = {"unique": False, "not_null": False}
        try:
            cur.execute(
                "INSERT INTO biblioteca.livros (nome, autor, id_estante, codigo_patrimonio) VALUES (?, ?, ?, ?);",
                ("Dup", "Autor", 1, "PAT-0001"),
            )
        except pyodbc.IntegrityError:
            r["unique"] = True
            conn.rollback()
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, autor, id_estante) VALUES (?, ?, ?);", (None, "Autor", 1))
        except pyodbc.IntegrityError:
            r["not_null"] = True
            conn.rollback()
        return r

    def _t_check(cur, conn):
        r = {"check_faixa": False, "check_in": False}
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, numero_de_exemplares, id_estante) VALUES (?, ?, ?);", ("Neg", -5, 1))
        except pyodbc.IntegrityError:
            r["check_faixa"] = True
            conn.rollback()
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, status_conservacao, id_estante) VALUES (?, ?, ?);", ("Inv", "Destruido", 1))
        except pyodbc.IntegrityError:
            r["check_in"] = True
            conn.rollback()
        return r

    def _t_cascata(cur, _conn):
        cur.execute("INSERT INTO biblioteca.tipos_de_espaco (tipo, numero_maximo_de_estantes, eh_privado) VALUES (?, ?, ?);", ("TmpOrig", 10, False))
        cur.execute("INSERT INTO biblioteca.estantes (dominio_lado_1, id_espaco, tipo) VALUES (?, ?, ?) RETURNING id_estante;", ("Dom", 1, "TmpOrig"))
        id_est = cur.fetchone()[0]
        cur.execute("UPDATE biblioteca.tipos_de_espaco SET tipo = ? WHERE tipo = ?;", ("TmpRenom", "TmpOrig"))
        cur.execute("SELECT tipo FROM biblioteca.estantes WHERE id_estante = ?;", (id_est,))
        upd_ok = cur.fetchone()[0] == "TmpRenom"
        cur.execute("INSERT INTO biblioteca.livros (nome, id_estante) VALUES (?, ?) RETURNING id_livro;", ("LivTmp", id_est))
        id_liv = cur.fetchone()[0]
        cur.execute("DELETE FROM biblioteca.estantes WHERE id_estante = ?;", (id_est,))
        cur.execute("SELECT COUNT(*) FROM biblioteca.livros WHERE id_livro = ?;", (id_liv,))
        del_ok = cur.fetchone()[0] == 0
        return {"on_update_cascade": upd_ok, "on_delete_cascade": del_ok}

    def _t_set_null_default(cur, _conn):
        cur.execute("INSERT INTO biblioteca.bibliotecarios (nome, email, cpf) VALUES (?, ?, ?) RETURNING id_bibliotecario;", ("Tmp", "tmp@bib.edu.br", "12312312312"))
        id_b = cur.fetchone()[0]
        cur.execute("INSERT INTO biblioteca.edificacoes (endereco, telefone, id_biblioteca, id_responsavel) VALUES (?, ?, ?, ?) RETURNING id_endereco;", ("Rua Tmp", "(99) 9999-0001", 1, id_b))
        id_e = cur.fetchone()[0]
        cur.execute("DELETE FROM biblioteca.bibliotecarios WHERE id_bibliotecario = ?;", (id_b,))
        cur.execute("SELECT id_responsavel FROM biblioteca.edificacoes WHERE id_endereco = ?;", (id_e,))
        set_null_ok = cur.fetchone()[0] is None

        cur.execute("INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);", (99, "CatTmp"))
        cur.execute("INSERT INTO biblioteca.livros (nome, id_estante, id_categoria) VALUES (?, ?, ?) RETURNING id_livro;", ("LivDef", 1, 99))
        id_l = cur.fetchone()[0]
        cur.execute("DELETE FROM biblioteca.categorias_acervo WHERE id_categoria = ?;", (99,))
        cur.execute("SELECT id_categoria FROM biblioteca.livros WHERE id_livro = ?;", (id_l,))
        set_def_ok = cur.fetchone()[0] == 1
        return {"on_delete_set_null": set_null_ok, "on_delete_set_default": set_def_ok}

    def _t_default_alter(cur, _conn):
        cur.execute("INSERT INTO biblioteca.livros (nome, id_estante) VALUES (?, ?) RETURNING status_conservacao, id_categoria;", ("Def", 1))
        row = cur.fetchone()
        def_ok = row[0] == "Bom" and row[1] == 1
        cur.execute("ALTER TABLE biblioteca.livros ADD COLUMN col_demo VARCHAR(20);")
        cur.execute("ALTER TABLE biblioteca.livros DROP COLUMN col_demo;")
        return {"valores_default": def_ok, "alter_table_add_drop": True}

    _rodar_teste("PK Simples e Composta", _t_pk)
    _rodar_teste("UNIQUE e NOT NULL", _t_unique_not_null)
    _rodar_teste("CHECK (Faixa e IN)", _t_check)
    _rodar_teste("ON UPDATE / ON DELETE CASCADE", _t_cascata)
    _rodar_teste("ON DELETE SET NULL e SET DEFAULT", _t_set_null_default)
    _rodar_teste("DEFAULT e ALTER TABLE ADD/DROP", _t_default_alter)
    return resultados


# ==============================================================================
# SEÇÃO 2: ÁLGEBRA RELACIONAL E BUSCAS (Cap. 2 e 3)
# ==============================================================================

def listar_autores_unicos() -> list[dict]:
    """
    [CONCEITO]: ALGEBRA RELACIONAL, PROJECAO, DISTINCT, IS NOT NULL
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Projeta exclusivamente autores distintos cadastrados no acervo (sem duplicatas).
    """
    sql = """
        SELECT DISTINCT autor
        FROM biblioteca.livros
        WHERE autor IS NOT NULL
        ORDER BY autor ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def listar_autores_todos() -> list[dict]:
    """
    [CONCEITO]: ALGEBRA RELACIONAL, PROJECAO, SELECT ALL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Projeta todos os autores preservando duplicatas (comparativo com DISTINCT).
    """
    sql = "SELECT ALL autor FROM biblioteca.livros WHERE autor IS NOT NULL ORDER BY autor ASC;"
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def buscar_catalogo_palavra_chave(termo: str) -> list[dict]:
    """
    [CONCEITO]: SELECAO, LIKE, ILIKE, OR, UPPER, SUBSTRING, LENGTH, CONCATENACAO, ORDER BY
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Busca obras por palavra-chave no título ou autor com formatação de strings.
    """
    like = f"%{termo}%"
    sql = """
        SELECT UPPER(nome) AS titulo_destaque,
               nome || ' (Autor: ' || COALESCE(autor, '-') || ')' AS catalogo_completo,
               SUBSTRING(genero FROM 1 FOR 15) AS genero_curto,
               LENGTH(nome) AS tamanho_titulo
        FROM biblioteca.livros
        WHERE nome ILIKE ? OR autor ILIKE ?
        ORDER BY autor ASC, numero_de_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql, (like, like))
        return _para_dicts(cursor)


def buscar_livros_por_faixa_exemplares(minimo: int, maximo: int) -> list[dict]:
    """
    [CONCEITO]: SELECAO, BETWEEN, AND, NOT, ORDER BY
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Filtra livros com quantidade de exemplares dentro do intervalo inclusivo [minimo, maximo].
    """
    if minimo > maximo:
        minimo, maximo = maximo, minimo
    sql = """
        SELECT nome, autor, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares BETWEEN ? AND ?
          AND NOT (nome IS NULL)
        ORDER BY numero_de_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql, (int(minimo), int(maximo)))
        return _para_dicts(cursor)


def listar_estantes_sem_dominio_lado2() -> list[dict]:
    """
    [CONCEITO]: VALORES NULOS, IS NULL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Identifica estantes sem domínio definido no lado 2.
    """
    sql = "SELECT id_estante, dominio_lado_1, dominio_lado_2, tipo FROM biblioteca.estantes WHERE dominio_lado_2 IS NULL;"
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def auto_juncao_livros_mesmo_autor_genero(genero: str) -> list[dict]:
    """
    [CONCEITO]: SELF JOIN, AUTO-JUNCAO, PRODUTO CARTESIANO, ALIAS, AS
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Encontra pares distintos de livros do mesmo autor dentro de um gênero usando auto-junção.
    """
    sql = """
        SELECT l1.nome AS livro_1, l2.nome AS livro_2, l1.autor, l1.genero
        FROM biblioteca.livros AS l1
        INNER JOIN biblioteca.livros AS l2
            ON l1.autor = l2.autor AND l1.genero = l2.genero AND l1.id_livro < l2.id_livro
        WHERE l1.genero = ?;
    """
    with transacao() as cursor:
        cursor.execute(sql, (genero,))
        return _para_dicts(cursor)


# ==============================================================================
# SEÇÃO 3: SUBCONSULTAS E OPERAÇÕES DE CONJUNTO (Cap. 3)
# ==============================================================================

def livros_acima_da_media_escalar() -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA ESCALAR, AVG
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Retorna livros cujo número de exemplares supera a média global do acervo.
    """
    sql = """
        SELECT nome, autor, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares > (SELECT AVG(numero_de_exemplares) FROM biblioteca.livros)
        ORDER BY numero_de_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def livros_por_tipo_espaco_in(tipo_espaco: str, negar: bool = False) -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA, IN, NOT IN
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Lista livros cujas estantes pertencem (IN) ou não pertencem (NOT IN) ao tipo de espaço informado.
    """
    op = "NOT IN" if negar else "IN"
    sql = f"""
        SELECT id_livro, nome, autor, id_estante
        FROM biblioteca.livros
        WHERE id_estante {op} (SELECT id_estante FROM biblioteca.estantes WHERE tipo = ?)
        ORDER BY nome;
    """
    with transacao() as cursor:
        cursor.execute(sql, (tipo_espaco,))
        return _para_dicts(cursor)


def espacos_com_estantes_exists(negar: bool = False) -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA CORRELACIONADA, EXISTS, NOT EXISTS
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Lista espaços que possuem (EXISTS) ou não possuem (NOT EXISTS) estantes vinculadas.
    """
    op = "NOT EXISTS" if negar else "EXISTS"
    sql = f"""
        SELECT esp.id_espaco, esp.numero_de_espacos, esp.id_pisos
        FROM biblioteca.espacos esp
        WHERE {op} (SELECT 1 FROM biblioteca.estantes est WHERE est.id_espaco = esp.id_espaco)
        ORDER BY esp.id_espaco;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def analise_acervo_critico(genero_alvo: str, genero_comparacao: str) -> list[dict]:
    """
    [CONCEITO]: CTE, WITH, SUBCONSULTA NO FROM, IN, SOME, EXISTS
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Compara obras em estantes de um domínio-alvo com exemplares superiores a algum (> SOME) livro do gênero comparado.
    """
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
    with transacao() as cursor:
        cursor.execute(sql, (genero_alvo, genero_comparacao))
        return _para_dicts(cursor)


def uniao_dominios_estantes() -> list[dict]:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, UNION
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Une todos os domínios do lado 1 e lado 2 das estantes eliminando duplicatas.
    """
    sql = """
        SELECT dominio_lado_1 AS dominio FROM biblioteca.estantes WHERE dominio_lado_1 IS NOT NULL
        UNION
        SELECT dominio_lado_2 AS dominio FROM biblioteca.estantes WHERE dominio_lado_2 IS NOT NULL
        ORDER BY dominio ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def relatorio_autores_multigenero(genero1: str, genero2: str) -> list[dict]:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, INTERSECT
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Retorna autores que possuem livros cadastrados nos dois gêneros simultaneamente.
    """
    sql = """
        SELECT autor FROM biblioteca.livros WHERE genero = ?
        INTERSECT
        SELECT autor FROM biblioteca.livros WHERE genero = ?;
    """
    with transacao() as cursor:
        cursor.execute(sql, (genero1, genero2))
        return _para_dicts(cursor)


def auditoria_estantes_vazias() -> list[dict]:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, EXCEPT
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Retorna estantes que não possuem nenhum livro associado usando diferença de conjuntos.
    """
    sql = """
        SELECT id_estante, dominio_lado_1 FROM biblioteca.estantes
        EXCEPT
        SELECT e.id_estante, e.dominio_lado_1
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.livros l ON e.id_estante = l.id_estante
        ORDER BY id_estante;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


# ==============================================================================
# SEÇÃO 4: AGREGAÇÕES, JUNÇÕES, VISÕES E PROGRAMAÇÃO NO BANCO (Cap. 3, 4 e 5)
# ==============================================================================

def relatorio_estatisticas_genero(media_minima: float) -> list[dict]:
    """
    [CONCEITO]: AGREGACAO, COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Agrupa livros por gênero e filtra grupos cuja média de exemplares seja maior que media_minima.
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
        ORDER BY genero;
    """
    with transacao() as cursor:
        cursor.execute(sql, (float(media_minima),))
        return _para_dicts(cursor)


SQL_JOINS = {
    "natural": """
        SELECT nome, tipo FROM biblioteca.livros
        NATURAL JOIN biblioteca.estantes ORDER BY nome;
    """,
    "inner": """
        SELECT e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo,
               esp.id_espaco, esp.numero_de_espacos
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.espacos esp ON e.id_espaco = esp.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """,
    "left": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        LEFT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco;
    """,
    "right": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        RIGHT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY e.id_estante;
    """,
    "full": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        FULL OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco, e.id_estante;
    """,
}


def executar_join(codigo: str) -> list[dict]:
    """
    [CONCEITO]: JUNCOES, NATURAL JOIN, INNER JOIN, LEFT OUTER JOIN, RIGHT OUTER JOIN, FULL OUTER JOIN
    [CAPÍTULO]: Cap. 4
    [DESCRIÇÃO]: Executa uma das cinco junções SQL explícitas ('natural', 'inner', 'left', 'right', 'full').
    """
    sql = SQL_JOINS.get(codigo)
    if not sql:
        raise ValueError(f"JOIN inválida: {codigo}")
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def consultar_visao_localizacao_completa() -> list[dict]:
    """
    [CONCEITO]: VISAO, VIEW TRADICIONAL
    [CAPÍTULO]: Cap. 4
    [DESCRIÇÃO]: Consome a visão biblioteca.vw_livros_localizacao_completa (7 tabelas integradas).
    """
    sql = "SELECT * FROM biblioteca.vw_livros_localizacao_completa ORDER BY id_livro;"
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


MVS_PERMITIDAS = {
    "mv_ranking_autores_maior_acervo",
    "mv_estatisticas_por_edificacao",
    "mv_ocupacao_estantes_livros",
    "mv_relatorio_completo_hierarquia",
}


def consultar_visao_materializada(nome_mv: str = "mv_ranking_autores_maior_acervo") -> list[dict]:
    """
    [CONCEITO]: VISAO MATERIALIZADA, MATERIALIZED VIEW
    [CAPÍTULO]: Cap. 4
    [DESCRIÇÃO]: Lê dados pré-computados de uma visão materializada autorizada.
    """
    if nome_mv not in MVS_PERMITIDAS:
        raise ValueError(f"Visão materializada não autorizada: {nome_mv}")
    with transacao() as cursor:
        cursor.execute(f"SELECT * FROM biblioteca.{nome_mv};")
        return _para_dicts(cursor)


def atualizar_visao_materializada(nome_mv: str = "mv_ranking_autores_maior_acervo") -> bool:
    """
    [CONCEITO]: REFRESH MATERIALIZED VIEW, VISAO MATERIALIZADA
    [CAPÍTULO]: Cap. 4
    [DESCRIÇÃO]: Executa REFRESH MATERIALIZED VIEW para sincronizar os dados pré-computados.
    """
    if nome_mv not in MVS_PERMITIDAS:
        raise ValueError(f"Visão materializada não autorizada: {nome_mv}")
    with transacao() as cursor:
        cursor.execute(f"REFRESH MATERIALIZED VIEW biblioteca.{nome_mv};")
    return True


def consultar_total_por_autor(autor: str) -> dict:
    """
    [CONCEITO]: STORED FUNCTION, SELECT FUNCTION
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Invoca a Stored Function fn_contar_livros_por_autor e retorna total + lista de livros.
    """
    with transacao() as cursor:
        cursor.execute("SELECT fn_contar_livros_por_autor(CAST(? AS VARCHAR)) AS total;", (autor,))
        total = int(cursor.fetchone()[0])
        cursor.execute(
            """
            SELECT id_livro, nome, autor, genero, numero_de_exemplares, pode_ser_emprestado
            FROM biblioteca.livros
            WHERE autor ILIKE '%' || ? || '%'
            ORDER BY nome;
            """,
            (autor,),
        )
        return {"total": total, "livros": _para_dicts(cursor)}


def cadastrar_livro_via_procedure(
    nome: str,
    autor: str,
    genero: str,
    numero_de_exemplares: int,
    pode_ser_emprestado: bool,
    id_estante: int,
) -> None:
    """
    [CONCEITO]: STORED PROCEDURE, CALL PROCEDURE
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Executa a Stored Procedure sp_cadastrar_livro via comando CALL.
    """
    sql = """
        CALL sp_cadastrar_livro(
            CAST(? AS VARCHAR), CAST(? AS VARCHAR), CAST(? AS VARCHAR),
            CAST(? AS INT), CAST(? AS BOOLEAN), CAST(? AS INT)
        );
    """
    with transacao() as cursor:
        cursor.execute(
            sql,
            (nome, autor, genero, int(numero_de_exemplares), bool(pode_ser_emprestado), int(id_estante)),
        )


def consultar_auditoria_trigger() -> list[dict]:
    """
    [CONCEITO]: TRIGGER, GATILHO, AUDITORIA AFTER DELETE
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Exibe os registros gravados automaticamente pelo gatilho de exclusão de livros.
    """
    sql = """
        SELECT id_auditoria, id_livro_apagado, nome_livro, autor, data_exclusao, usuario_banco
        FROM biblioteca.auditoria_livros_excluidos
        ORDER BY id_auditoria DESC
        LIMIT 10;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def consulta_recursiva_pisos() -> list[dict]:
    """
    [CONCEITO]: CONSULTA RECURSIVA, WITH RECURSIVE
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Percorre os pisos cadastrados de forma recursiva utilizando CTE WITH RECURSIVE.
    """
    sql = """
        WITH RECURSIVE niveis_piso AS (
            SELECT id_pisos, id_endereco, capacidade_maxima, 1 AS nivel
            FROM biblioteca.pisos
            WHERE id_pisos = (SELECT MIN(id_pisos) FROM biblioteca.pisos)
            UNION ALL
            SELECT p.id_pisos, p.id_endereco, p.capacidade_maxima, np.nivel + 1
            FROM biblioteca.pisos p
            INNER JOIN niveis_piso np ON p.id_pisos = np.id_pisos + 1
            WHERE np.nivel < 10
        )
        SELECT * FROM niveis_piso;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


# ==============================================================================
# SEÇÃO 5: METADADOS VIA ODBC (Cap. 5)
# ==============================================================================

def inspecionar_tabelas_schema(schema: str = "biblioteca") -> list[dict]:
    """
    [CONCEITO]: METADADOS, CATALOGO ODBC, CURSOR.TABLES
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Lista tabelas e visões do schema informado usando cursor.tables() do pyodbc.
    """
    with transacao() as cursor:
        return [
            {"schema": r.table_schem, "tabela": r.table_name, "tipo": r.table_type}
            for r in cursor.tables(schema=schema)
        ]


def inspecionar_colunas_tabela(tabela: str, schema: str = "biblioteca") -> list[dict]:
    """
    [CONCEITO]: METADADOS, CATALOGO ODBC, CURSOR.COLUMNS
    [CAPÍTULO]: Cap. 5
    [DESCRIÇÃO]: Inspeciona colunas, tipos, tamanhos e nulabilidade de uma tabela via cursor.columns().
    """
    with transacao() as cursor:
        return [
            {
                "coluna": c.column_name,
                "tipo": c.type_name,
                "tamanho": c.column_size,
                "permite_nulo": c.is_nullable,
            }
            for c in cursor.columns(table=tabela, schema=schema)
        ]
