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


def validar_colunas_ddl_alter_table(tabela: str = "livros", colunas_esperadas: tuple = ("codigo_isbn", "valor_seguro")) -> dict:
    """
    [CONCEITO]: ALTER TABLE, METADADOS, CURSOR.COLUMNS, DDL
    [CAPÍTULO]: Cap. 3 e Cap. 5
    [DESCRIÇÃO]: Inspeciona o catálogo via cursor.columns() para comprovar colunas adicionadas via ALTER TABLE.
    """
    with transacao() as cursor:
        encontradas = {c.column_name for c in cursor.columns(table=tabela, schema="biblioteca")}
    presentes = [col for col in colunas_esperadas if col in encontradas]
    return {"tabela": tabela, "esperadas": list(colunas_esperadas), "presentes": presentes, "todas_presentes": len(presentes) == len(colunas_esperadas)}


def testar_parte1_completa() -> list[dict]:
    """
    [CONCEITO]: PRIMARY KEY SIMPLES, PRIMARY KEY COMPOSTA, FOREIGN KEY, ON DELETE CASCADE, ON DELETE SET NULL, ON DELETE RESTRICT, UNIQUE, NOT NULL, CHECK, DEFAULT, ALTER TABLE, CURSOR.COLUMNS
    [CAPÍTULO]: Cap. 1, Cap. 2, Cap. 3 e Cap. 4
    [DESCRIÇÃO]: Executa 1 teste prático para cada um dos 8 itens da Parte 1 (DDL e Restrições de Integridade),
                 capturando pyodbc.IntegrityError com mensagens amigáveis e fazendo rollback ao final de cada teste.
    """
    relatorio = []

    def _executar(item, fn):
        conn = conectar()
        cursor = conn.cursor()
        try:
            detalhes = fn(cursor, conn)
            ok = bool(detalhes.pop("_ok", all(bool(v) for v in detalhes.values())))
            relatorio.append({"item": item, "status": "OK" if ok else "FALHA", "detalhes": detalhes})
        finally:
            conn.rollback()
            cursor.close()
            conn.close()

    # 1. Chave Primária Simples (inserção normal + duplicação forçada)
    def _t1_pk_simples(cur, conn):
        cur.execute("INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);", (901, "Cat Teste PK"))
        bloqueou = False
        try:
            cur.execute("INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);", (901, "Cat Duplicada"))
        except pyodbc.IntegrityError:
            bloqueou = True
            conn.rollback()
        return {"insercao_normal": True, "duplicacao_pk_bloqueada": bloqueou}

    # 2. Chave Primária Composta (tabela N:M livro_tag: mesmo par duas vezes)
    def _t2_pk_composta(cur, conn):
        cur.execute("INSERT INTO biblioteca.livro_tag (id_livro, id_tag) VALUES (?, ?);", (1, 4))
        bloqueou = False
        try:
            cur.execute("INSERT INTO biblioteca.livro_tag (id_livro, id_tag) VALUES (?, ?);", (1, 4))
        except pyodbc.IntegrityError:
            bloqueou = True
            conn.rollback()
        return {"par_inserido_1a_vez": True, "par_duplicado_bloqueado": bloqueou}

    # 3. Chave Estrangeira (tentativa de apontar para ID pai inexistente)
    def _t3_fk_pai_inexistente(cur, conn):
        bloqueou = False
        msg = ""
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, autor, id_estante) VALUES (?, ?, ?);", ("Livro Orfao", "Autor", 999999))
        except pyodbc.IntegrityError:
            bloqueou = True
            msg = "Integridade referencial preservada: estante informada não existe."
            conn.rollback()
        return {"fk_pai_inexistente_bloqueada": bloqueou, "mensagem": msg}

    # 4. Ações Referenciais: ON DELETE CASCADE, ON DELETE SET NULL e ON DELETE RESTRICT
    def _t4_acoes_referenciais(cur, conn):
        # 4a. ON DELETE CASCADE (estantes -> livros)
        cur.execute("INSERT INTO biblioteca.estantes (dominio_lado_1, id_espaco, tipo) VALUES (?, ?, ?) RETURNING id_estante;", ("Dom Cascata", 1, "Acervo Geral de Livros"))
        id_est = cur.fetchone()[0]
        cur.execute("INSERT INTO biblioteca.livros (nome, id_estante) VALUES (?, ?) RETURNING id_livro;", ("Liv Cascata", id_est))
        id_liv = cur.fetchone()[0]
        cur.execute("DELETE FROM biblioteca.estantes WHERE id_estante = ?;", (id_est,))
        cur.execute("SELECT COUNT(*) FROM biblioteca.livros WHERE id_livro = ?;", (id_liv,))
        cascade_ok = cur.fetchone()[0] == 0

        # 4b. ON DELETE SET NULL (bibliotecarios -> edificacoes.id_responsavel)
        cur.execute("INSERT INTO biblioteca.bibliotecarios (nome, email, cpf) VALUES (?, ?, ?) RETURNING id_bibliotecario;", ("Bib Temp", "bib.temp@edu.br", "32132132100"))
        id_bib = cur.fetchone()[0]
        cur.execute("INSERT INTO biblioteca.edificacoes (endereco, telefone, id_biblioteca, id_responsavel) VALUES (?, ?, ?, ?) RETURNING id_endereco;", ("Rua SetNull, 1", "(99) 8888-7777", 1, id_bib))
        id_ed = cur.fetchone()[0]
        cur.execute("DELETE FROM biblioteca.bibliotecarios WHERE id_bibliotecario = ?;", (id_bib,))
        cur.execute("SELECT id_responsavel FROM biblioteca.edificacoes WHERE id_endereco = ?;", (id_ed,))
        set_null_ok = cur.fetchone()[0] is None

        # 4c. ON DELETE RESTRICT (editoras -> livros.id_editora)
        restrict_ok = False
        try:
            cur.execute("DELETE FROM biblioteca.editoras WHERE id_editora = ?;", (1,))
        except pyodbc.IntegrityError:
            restrict_ok = True
            conn.rollback()
        return {"on_delete_cascade": cascade_ok, "on_delete_set_null": set_null_ok, "on_delete_restrict_bloqueou": restrict_ok}

    # 5. Restrição de Unicidade (UNIQUE) com mensagem amigável
    def _t5_unique(cur, conn):
        bloqueou = False
        msg = ""
        try:
            cur.execute(
                "INSERT INTO biblioteca.livros (nome, autor, id_estante, codigo_patrimonio) VALUES (?, ?, ?, ?);",
                ("Livro Duplicado", "Autor", 1, "PAT-0001"),
            )
        except pyodbc.IntegrityError:
            bloqueou = True
            msg = "Erro de unicidade (UNIQUE): o código de patrimônio 'PAT-0001' já está cadastrado."
            conn.rollback()
        return {"unique_bloqueado": bloqueou, "mensagem": msg}

    # 6. Restrição de Não-Nulo (NOT NULL)
    def _t6_not_null(cur, conn):
        bloqueou = False
        msg = ""
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, autor, id_estante) VALUES (?, ?, ?);", (None, "Autor", 1))
        except pyodbc.IntegrityError:
            bloqueou = True
            msg = "Campo obrigatório (NOT NULL): o título do livro não pode ser nulo."
            conn.rollback()
        return {"not_null_bloqueado": bloqueou, "mensagem": msg}

    # 7. Restrições CHECK (faixa numérica >= 0 e lista discreta IN)
    def _t7_check(cur, conn):
        faixa_ok = False
        lista_ok = False
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, numero_de_exemplares, id_estante) VALUES (?, ?, ?);", ("Neg", -10, 1))
        except pyodbc.IntegrityError:
            faixa_ok = True
            conn.rollback()
        try:
            cur.execute("INSERT INTO biblioteca.livros (nome, status_conservacao, id_estante) VALUES (?, ?, ?);", ("Inv", "Destruido", 1))
        except pyodbc.IntegrityError:
            lista_ok = True
            conn.rollback()
        return {"check_faixa_bloqueou": faixa_ok, "check_lista_in_bloqueou": lista_ok}

    # 8. Valores Padrão (DEFAULT) + ALTER TABLE inspecionado via cursor.columns()
    def _t8_default_e_alter(cur, _conn):
        cur.execute("INSERT INTO biblioteca.livros (nome, id_estante) VALUES (?, ?) RETURNING id_livro;", ("Livro Default", 1))
        id_novo = cur.fetchone()[0]
        cur.execute(
            "SELECT numero_de_exemplares, pode_ser_emprestado, status_conservacao, id_categoria, data_cadastro FROM biblioteca.livros WHERE id_livro = ?;",
            (id_novo,),
        )
        ex, emp, st, cat, dt = cur.fetchone()
        default_ok = (ex == 1 and str(emp) in ("True", "1") and st == "Bom" and cat == 1 and dt is not None)

        cur.execute("ALTER TABLE biblioteca.livros ADD COLUMN col_teste_ddl VARCHAR(30);")
        cols_com = {c.column_name for c in cur.columns(table="livros", schema="biblioteca")}
        cur.execute("ALTER TABLE biblioteca.livros DROP COLUMN col_teste_ddl;")
        cols_sem = {c.column_name for c in cur.columns(table="livros", schema="biblioteca")}
        alter_ok = ("col_teste_ddl" in cols_com) and ("col_teste_ddl" not in cols_sem) and ("codigo_isbn" in cols_sem)
        return {"default_preenchido_pelo_sgbd": default_ok, "alter_table_e_cursor_columns": alter_ok}

    _executar("1. Chave Primária Simples (PRIMARY KEY)", _t1_pk_simples)
    _executar("2. Chave Primária Composta (PRIMARY KEY col1, col2)", _t2_pk_composta)
    _executar("3. Chave Estrangeira (FK pai inexistente)", _t3_fk_pai_inexistente)
    _executar("4. Ações Referenciais (CASCADE, SET NULL e RESTRICT)", _t4_acoes_referenciais)
    _executar("5. Restrição de Unicidade (UNIQUE)", _t5_unique)
    _executar("6. Restrição de Não-Nulo (NOT NULL)", _t6_not_null)
    _executar("7. Restrições CHECK (Faixa e Lista IN)", _t7_check)
    _executar("8. Valores DEFAULT e ALTER TABLE + cursor.columns()", _t8_default_e_alter)
    return relatorio


# Alias retrocompatível
validar_integridade_ddl = testar_parte1_completa


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


def buscar_livros_por_faixa_exemplares(minimo: int, maximo: int, negar: bool = False) -> list[dict]:
    """
    [CONCEITO]: SELECAO, BETWEEN, NOT BETWEEN, AND, NOT, ORDER BY
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Filtra livros com exemplares dentro (BETWEEN) ou fora (NOT BETWEEN) do intervalo [minimo, maximo].
    """
    if minimo > maximo:
        minimo, maximo = maximo, minimo
    op = "NOT BETWEEN" if negar else "BETWEEN"
    sql = f"""
        SELECT nome, autor, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares {op} ? AND ?
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
    [CONCEITO]: RENOMEACAO, RHO, SELF JOIN, AUTO-JUNCAO, ALIAS, AS
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Encontra pares distintos de livros do mesmo autor dentro de um gênero usando auto-junção com AS.
    """
    sql = """
        SELECT a.nome AS livro_1, b.nome AS livro_2, a.autor AS autor_comum, a.genero
        FROM biblioteca.livros AS a, biblioteca.livros AS b
        WHERE a.genero = ?
          AND a.autor = b.autor
          AND a.genero = b.genero
          AND a.id_livro < b.id_livro;
    """
    with transacao() as cursor:
        cursor.execute(sql, (genero,))
        return _para_dicts(cursor)


def projecao_distinct_all_e_calculo(fator_reajuste: float = 1.10) -> dict:
    """
    [CONCEITO]: PROJECAO, PI, DISTINCT, SELECT ALL, ATRIBUTO CALCULADO, EXPRESSAO ARITMETICA, AS
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Projeta atributos específicos com expressão aritmética e compara SELECT DISTINCT vs SELECT ALL.
    """
    with transacao() as cursor:
        cursor.execute("SELECT DISTINCT status_conservacao FROM biblioteca.livros ORDER BY status_conservacao;")
        distintos = _para_dicts(cursor)

        cursor.execute("SELECT ALL status_conservacao FROM biblioteca.livros ORDER BY status_conservacao;")
        todos = _para_dicts(cursor)

        cursor.execute(
            """
            SELECT nome AS titulo,
                   numero_de_exemplares,
                   ROUND(numero_de_exemplares * CAST(? AS NUMERIC), 2) AS meta_exemplares_reajustada
            FROM biblioteca.livros
            ORDER BY id_livro ASC;
            """,
            (float(fator_reajuste),),
        )
        calculados = _para_dicts(cursor)
    return {"distinct": distintos, "all": todos, "calculados": calculados}


def selecao_predicados_compostos_e_tupla(status: str = "Bom", emprestavel: bool = True, minimo: int = 5) -> dict:
    """
    [CONCEITO]: SELECAO, SIGMA, AND, OR, NOT, OPERADORES COMPARACAO, COMPARACAO DE TUPLA
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Combina operadores (=, <>, >, <, >=, <=) com AND/OR/NOT e demonstra predicado com tupla (a, b) = (?, ?).
    """
    sql_composto = """
        SELECT nome, autor, genero, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares >= ?
          AND numero_de_exemplares <= 50
          AND (numero_de_exemplares > 10 OR genero <> ?)
          AND NOT (status_conservacao = 'Danificado')
          AND numero_de_exemplares < 100
        ORDER BY numero_de_exemplares DESC;
    """
    sql_tupla = """
        SELECT nome, status_conservacao, pode_ser_emprestado
        FROM biblioteca.livros
        WHERE (status_conservacao, pode_ser_emprestado) = (?, ?)
        ORDER BY nome ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql_composto, (int(minimo), "Terror"))
        compostos = _para_dicts(cursor)
        cursor.execute(sql_tupla, (status, bool(emprestavel)))
        tuplas = _para_dicts(cursor)
    return {"predicados_compostos": compostos, "comparacao_tupla": tuplas}


def produto_cartesiano_e_juncao_teta(min_exemplares: int = 1) -> dict:
    """
    [CONCEITO]: PRODUTO CARTESIANO, CROSS PRODUCT, JUNCAO TETA, THETA JOIN
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Executa Produto Cartesiano puro (livros × espacos) comprovando |R|*|S| e Junção Teta clássica no WHERE.
    """
    with transacao() as cursor:
        cursor.execute("SELECT COUNT(*) FROM biblioteca.livros;")
        qtd_livros = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM biblioteca.espacos;")
        qtd_espacos = cursor.fetchone()[0]

        cursor.execute("SELECT l.nome AS livro, e.id_espaco FROM biblioteca.livros l, biblioteca.espacos e;")
        cartesiano = _para_dicts(cursor)

        cursor.execute(
            """
            SELECT l.nome AS livro, c.nome AS categoria, l.numero_de_exemplares
            FROM biblioteca.livros l, biblioteca.categorias_acervo c
            WHERE l.id_categoria = c.id_categoria
              AND l.numero_de_exemplares >= ?
            ORDER BY l.nome ASC;
            """,
            (int(min_exemplares),),
        )
        teta = _para_dicts(cursor)
    return {
        "qtd_livros": qtd_livros,
        "qtd_espacos": qtd_espacos,
        "total_cartesiano": len(cartesiano),
        "juncao_teta": teta,
    }


def buscar_strings_like_coringa_posicao(padrao_exato: str = "PAT-____", substring: str = "%a%") -> dict:
    """
    [CONCEITO]: STRINGS, LIKE, CORINGA %, CORINGA _, CONCATENACAO ||, UPPER, LOWER
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Demonstra LIKE com '%' (substring) e '_' (posição exata), além de ||, UPPER() e LOWER().
    """
    sql_sub = """
        SELECT UPPER(nome) AS titulo_upper,
               LOWER(COALESCE(autor, 'desconhecido')) AS autor_lower,
               nome || ' - ' || COALESCE(genero, 'Sem gênero') AS resumo_concatenado
        FROM biblioteca.livros
        WHERE nome LIKE ?
        ORDER BY nome ASC;
    """
    sql_pos = """
        SELECT nome, codigo_patrimonio
        FROM biblioteca.livros
        WHERE codigo_patrimonio LIKE ?
        ORDER BY codigo_patrimonio ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql_sub, (substring,))
        por_substring = _para_dicts(cursor)
        cursor.execute(sql_pos, (padrao_exato,))
        por_posicao = _para_dicts(cursor)
    return {"like_percent": por_substring, "like_underline": por_posicao}


def consultar_nulos_e_nao_nulos() -> dict:
    """
    [CONCEITO]: VALORES NULOS, LOGICA TRIVALENTE, IS NULL, IS NOT NULL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Separa livros sem código de patrimônio (IS NULL) e com código de patrimônio (IS NOT NULL).
    """
    with transacao() as cursor:
        cursor.execute("SELECT id_livro, nome, codigo_patrimonio FROM biblioteca.livros WHERE codigo_patrimonio IS NULL;")
        nulos = _para_dicts(cursor)
        cursor.execute("SELECT id_livro, nome, codigo_patrimonio FROM biblioteca.livros WHERE codigo_patrimonio IS NOT NULL;")
        nao_nulos = _para_dicts(cursor)
    return {"com_nulo": nulos, "sem_nulo": nao_nulos}


def ordenar_livros_multiatributo_nulos(nulos_primeiro: bool = True) -> list[dict]:
    """
    [CONCEITO]: ORDER BY, ORDENACAO MULTIATRIBUTO, ASC, DESC, NULLS FIRST, NULLS LAST
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Ordena livros por múltiplos atributos controlando explicitamente a posição de NULLs.
    """
    pos_nulos = "NULLS FIRST" if nulos_primeiro else "NULLS LAST"
    sql = f"""
        SELECT id_livro, nome, numero_de_exemplares, codigo_patrimonio
        FROM biblioteca.livros
        ORDER BY codigo_patrimonio ASC {pos_nulos}, numero_de_exemplares DESC, nome ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def testar_parte2_completa() -> list[dict]:
    """
    [CONCEITO]: TESTE PARTE 2, ALGEBRA RELACIONAL, PI, SIGMA, PRODUTO CARTESIANO, RHO, SELF JOIN, LIKE, BETWEEN, IS NULL, ORDER BY
    [CAPÍTULO]: Cap. 2 e Cap. 3
    [DESCRIÇÃO]: Executa bateria automatizada para todos os 8 itens da Parte 2 da avaliação.
    """
    r1 = projecao_distinct_all_e_calculo(1.10)
    ok1 = len(r1["distinct"]) <= len(r1["all"]) and len(r1["distinct"]) > 0 and len(r1["calculados"]) > 0

    r2 = selecao_predicados_compostos_e_tupla("Bom", True, 5)
    ok2 = len(r2["predicados_compostos"]) > 0 and len(r2["comparacao_tupla"]) > 0

    r3 = produto_cartesiano_e_juncao_teta(1)
    ok3 = (r3["total_cartesiano"] == r3["qtd_livros"] * r3["qtd_espacos"]) and len(r3["juncao_teta"]) > 0

    r4 = auto_juncao_livros_mesmo_autor_genero("Romance Clássico")
    ok4 = len(r4) > 0

    r5 = buscar_strings_like_coringa_posicao("PAT-____", "%a%")
    ok5 = len(r5["like_percent"]) > 0 and len(r5["like_underline"]) > 0

    r6_in = buscar_livros_por_faixa_exemplares(10, 20, negar=False)
    r6_out = buscar_livros_por_faixa_exemplares(10, 20, negar=True)
    ok6 = len(r6_in) > 0 and len(r6_out) > 0

    r7 = consultar_nulos_e_nao_nulos()
    ok7 = len(r7["com_nulo"]) > 0 and len(r7["sem_nulo"]) > 0

    r8_first = ordenar_livros_multiatributo_nulos(nulos_primeiro=True)
    r8_last = ordenar_livros_multiatributo_nulos(nulos_primeiro=False)
    ok8 = (
        len(r8_first) > 0
        and r8_first[0]["codigo_patrimonio"] is None
        and r8_last[-1]["codigo_patrimonio"] is None
    )

    return [
        {
            "item": "1. Projeção (Pi), DISTINCT vs ALL e Atributo Calculado",
            "status": "OK" if ok1 else "FALHA",
            "detalhes": {"distinct": len(r1["distinct"]), "all": len(r1["all"]), "calculados": len(r1["calculados"])},
        },
        {
            "item": "2. Seleção (Sigma), Predicados Compostos e Tupla",
            "status": "OK" if ok2 else "FALHA",
            "detalhes": {"compostos": len(r2["predicados_compostos"]), "tupla": len(r2["comparacao_tupla"])},
        },
        {
            "item": "3. Produto Cartesiano (|R|x|S|) e Junção Teta",
            "status": "OK" if ok3 else "FALHA",
            "detalhes": {
                "formula": f"{r3['qtd_livros']} x {r3['qtd_espacos']} = {r3['total_cartesiano']}",
                "juncao_teta": len(r3["juncao_teta"]),
            },
        },
        {
            "item": "4. Renomeação (Rho / AS) e Auto-Junção (SELF JOIN)",
            "status": "OK" if ok4 else "FALHA",
            "detalhes": {"pares_encontrados": len(r4), "exemplo": r4[0] if r4 else None},
        },
        {
            "item": "5. Strings: LIKE (% e _), ||, UPPER() e LOWER()",
            "status": "OK" if ok5 else "FALHA",
            "detalhes": {"like_percent": len(r5["like_percent"]), "like_underline_PAT": len(r5["like_underline"])},
        },
        {
            "item": "6. Faixa: BETWEEN e NOT BETWEEN",
            "status": "OK" if ok6 else "FALHA",
            "detalhes": {"between_10_20": len(r6_in), "not_between_10_20": len(r6_out)},
        },
        {
            "item": "7. Valores Nulos: IS NULL e IS NOT NULL",
            "status": "OK" if ok7 else "FALHA",
            "detalhes": {"is_null": len(r7["com_nulo"]), "is_not_null": len(r7["sem_nulo"])},
        },
        {
            "item": "8. Ordenação Multiatributo + NULLS FIRST / NULLS LAST",
            "status": "OK" if ok8 else "FALHA",
            "detalhes": {
                "primeiro_nulls_first": r8_first[0]["codigo_patrimonio"],
                "ultimo_nulls_last": r8_last[-1]["codigo_patrimonio"],
                "total_ordenado": len(r8_first),
            },
        },
    ]


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


def estatisticas_agregadas_gerais() -> dict:
    """
    [CONCEITO]: AGREGACAO, COUNT(*), COUNT(COLUNA), COUNT(DISTINCT), SUM, AVG, MIN, MAX
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Calcula métricas globais do acervo evidenciando COUNT(*) vs COUNT(col sem nulos) vs COUNT(DISTINCT).
    """
    sql = """
        SELECT COUNT(*)                             AS total_tuplas,
               COUNT(codigo_patrimonio)             AS total_com_patrimonio,
               COUNT(DISTINCT status_conservacao)   AS status_distintos,
               SUM(numero_de_exemplares)            AS soma_exemplares,
               ROUND(AVG(numero_de_exemplares), 2)  AS media_exemplares,
               MIN(numero_de_exemplares)            AS minimo_exemplares,
               MAX(numero_de_exemplares)            AS maximo_exemplares
        FROM biblioteca.livros;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)[0]


def agrupamento_simples_por_status() -> list[dict]:
    """
    [CONCEITO]: GROUP BY, AGRUPAMENTO SIMPLES, COUNT, SUM
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Agrupa livros por status_conservacao (todo atributo não agregado do SELECT consta no GROUP BY).
    """
    sql = """
        SELECT status_conservacao,
               COUNT(*) AS total_livros,
               SUM(numero_de_exemplares) AS total_exemplares
        FROM biblioteca.livros
        GROUP BY status_conservacao
        ORDER BY total_livros DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def agrupamento_where_e_having(emprestavel: bool = True, min_titulos: int = 2, min_exemplares_grupo: int = 10) -> list[dict]:
    """
    [CONCEITO]: GROUP BY, HAVING, WHERE vs HAVING, COUNT, SUM
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Filtra tuplas antes do agrupamento (WHERE) e filtra grupos consolidados depois (HAVING).
    """
    sql = """
        SELECT genero,
               COUNT(*) AS qtd_titulos,
               SUM(numero_de_exemplares) AS soma_exemplares
        FROM biblioteca.livros
        WHERE pode_ser_emprestado = ?
          AND genero IS NOT NULL
        GROUP BY genero
        HAVING COUNT(*) >= ?
           AND SUM(numero_de_exemplares) > ?
        ORDER BY soma_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql, (bool(emprestavel), int(min_titulos), int(min_exemplares_grupo)))
        return _para_dicts(cursor)


def comparar_union_vs_union_all() -> dict:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, UNION, UNION ALL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Compara UNION (elimina duplicatas) e UNION ALL (retém duplicatas) entre gêneros de livros e domínios de estantes.
    """
    sql_base = """
        SELECT genero AS tema FROM biblioteca.livros WHERE genero IS NOT NULL
        {op}
        SELECT dominio_lado_1 AS tema FROM biblioteca.estantes WHERE dominio_lado_1 IS NOT NULL
        ORDER BY tema ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql_base.format(op="UNION"))
        uniao = _para_dicts(cursor)
        cursor.execute(sql_base.format(op="UNION ALL"))
        uniao_all = _para_dicts(cursor)
    return {"union": uniao, "union_all": uniao_all}


def comparar_intersect_vs_intersect_all(status1: str = "Novo", status2: str = "Bom") -> dict:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, INTERSECT, INTERSECT ALL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Encontra categorias com livros no status1 E no status2, comparando INTERSECT vs INTERSECT ALL.
    """
    sql_base = """
        SELECT id_categoria FROM biblioteca.livros WHERE status_conservacao = ?
        {op}
        SELECT id_categoria FROM biblioteca.livros WHERE status_conservacao = ?
        ORDER BY id_categoria ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql_base.format(op="INTERSECT"), (status1, status2))
        inter = _para_dicts(cursor)
        cursor.execute(sql_base.format(op="INTERSECT ALL"), (status1, status2))
        inter_all = _para_dicts(cursor)
    return {"intersect": inter, "intersect_all": inter_all}


def comparar_except_vs_except_all(status_excluir: str = "Danificado") -> dict:
    """
    [CONCEITO]: OPERACAO DE CONJUNTO, EXCEPT, EXCEPT ALL
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Subtrai categorias que possuem livros no status_excluir, comparando EXCEPT (conjunto) vs EXCEPT ALL (multiconjunto).
    """
    sql_base = """
        SELECT id_categoria FROM biblioteca.livros WHERE id_categoria IS NOT NULL
        {op}
        SELECT id_categoria FROM biblioteca.livros WHERE status_conservacao = ?
        ORDER BY id_categoria ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql_base.format(op="EXCEPT"), (status_excluir,))
        exc = _para_dicts(cursor)
        cursor.execute(sql_base.format(op="EXCEPT ALL"), (status_excluir,))
        exc_all = _para_dicts(cursor)
    return {"except": exc, "except_all": exc_all}


def testar_parte3_completa() -> list[dict]:
    """
    [CONCEITO]: TESTE PARTE 3, AGREGACAO, COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING, UNION, INTERSECT, EXCEPT
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Executa bateria automatizada para todos os 6 itens da Parte 3 da avaliação.
    """
    r1 = estatisticas_agregadas_gerais()
    ok1 = (
        r1["total_tuplas"] > r1["total_com_patrimonio"] > 0
        and r1["status_distintos"] > 0
        and r1["soma_exemplares"] > 0
        and r1["maximo_exemplares"] >= r1["minimo_exemplares"]
    )

    r2 = agrupamento_simples_por_status()
    ok2 = len(r2) == r1["status_distintos"] and sum(x["total_livros"] for x in r2) == r1["total_tuplas"]

    r3 = agrupamento_where_e_having(True, 2, 10)
    ok3 = len(r3) > 0 and all(x["qtd_titulos"] >= 2 and x["soma_exemplares"] > 10 for x in r3)

    r4 = comparar_union_vs_union_all()
    ok4 = len(r4["union_all"]) > len(r4["union"]) > 0

    r5 = comparar_intersect_vs_intersect_all("Novo", "Bom")
    ok5 = len(r5["intersect_all"]) >= len(r5["intersect"]) > 0

    r6 = comparar_except_vs_except_all("Danificado")
    ok6 = len(r6["except_all"]) > len(r6["except"]) > 0

    return [
        {
            "item": "1. Funções Agregadas (COUNT(*)/col/DISTINCT, SUM, AVG, MIN, MAX)",
            "status": "OK" if ok1 else "FALHA",
            "detalhes": {
                "count_star": r1["total_tuplas"],
                "count_patrimonio": r1["total_com_patrimonio"],
                "count_distinct_status": r1["status_distintos"],
                "sum": r1["soma_exemplares"],
                "avg": float(r1["media_exemplares"]),
                "min": r1["minimo_exemplares"],
                "max": r1["maximo_exemplares"],
            },
        },
        {
            "item": "2. Agrupamento Simples (GROUP BY status_conservacao)",
            "status": "OK" if ok2 else "FALHA",
            "detalhes": {"grupos": len(r2), "resumo": r2},
        },
        {
            "item": "3. Filtro Pré e Pós-Agrupamento (WHERE + GROUP BY + HAVING)",
            "status": "OK" if ok3 else "FALHA",
            "detalhes": {"grupos_aprovados": len(r3), "resumo": r3},
        },
        {
            "item": "4. União de Conjuntos (UNION vs UNION ALL)",
            "status": "OK" if ok4 else "FALHA",
            "detalhes": {"union": len(r4["union"]), "union_all": len(r4["union_all"])},
        },
        {
            "item": "5. Interseção de Conjuntos (INTERSECT vs INTERSECT ALL)",
            "status": "OK" if ok5 else "FALHA",
            "detalhes": {"intersect": len(r5["intersect"]), "intersect_all": len(r5["intersect_all"])},
        },
        {
            "item": "6. Diferença de Conjuntos (EXCEPT vs EXCEPT ALL)",
            "status": "OK" if ok6 else "FALHA",
            "detalhes": {"except": len(r6["except"]), "except_all": len(r6["except_all"])},
        },
    ]


# ==============================================================================
# SEÇÃO 4: SUBCONSULTAS AVANÇADAS, CTEs, AGREGAÇÕES, JUNÇÕES E VISÕES (Cap. 3, 4 e 5)
# ==============================================================================

def subconsulta_some_e_all(genero: str = "Tecnologia e Informática") -> dict:
    """
    [CONCEITO]: SUBCONSULTA, SOME, ANY, ALL, COMPARACAO DE CONJUNTOS
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Compara > SOME (maior que ao menos um) e > ALL (estritamente maior que todos) do gênero informado.
    """
    sql_some = """
        SELECT nome, genero, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares > SOME (
            SELECT numero_de_exemplares FROM biblioteca.livros WHERE genero = ?
        )
        ORDER BY numero_de_exemplares DESC;
    """
    sql_all = """
        SELECT nome, genero, numero_de_exemplares
        FROM biblioteca.livros
        WHERE numero_de_exemplares > ALL (
            SELECT numero_de_exemplares FROM biblioteca.livros WHERE genero = ?
        )
        ORDER BY numero_de_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql_some, (genero,))
        maior_que_some = _para_dicts(cursor)
        cursor.execute(sql_all, (genero,))
        maior_que_all = _para_dicts(cursor)
    return {"maior_que_some": maior_que_some, "maior_que_all": maior_que_all}


def subconsulta_ausencia_duplicatas_unique() -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA, UNIQUE, AUSENCIA DE DUPLICATAS, NOT EXISTS, HAVING COUNT
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Simulação formal no PostgreSQL do predicado UNIQUE(SELECT ...) do Silberschatz:
                 retorna livros de autores sem duplicidade no acervo (no máximo 1 obra por autor).
    """
    sql = """
        SELECT l1.id_livro, l1.nome, l1.autor
        FROM biblioteca.livros l1
        WHERE l1.autor IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM biblioteca.livros l2
              WHERE l2.autor = l1.autor
              GROUP BY l2.autor
              HAVING COUNT(*) > 1
          )
        ORDER BY l1.autor ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def subconsulta_escalar_no_select() -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA ESCALAR, SELECT SUBQUERY, AVG
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Projeta no SELECT uma subconsulta escalar (1 linha x 1 coluna) com a média global de exemplares.
    """
    sql = """
        SELECT nome,
               numero_de_exemplares,
               (SELECT ROUND(AVG(numero_de_exemplares), 2) FROM biblioteca.livros) AS media_geral_acervo
        FROM biblioteca.livros
        ORDER BY numero_de_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql)
        return _para_dicts(cursor)


def subconsulta_no_from_media_categoria(media_minima: float = 5.0) -> list[dict]:
    """
    [CONCEITO]: SUBCONSULTA NO FROM, TABELA DERIVADA, ALIAS
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Usa uma tabela derivada na cláusula FROM para calcular a média por categoria e filtrar no WHERE externo.
    """
    sql = """
        SELECT sub.id_categoria, sub.total_livros, sub.media_exemplares
        FROM (
            SELECT id_categoria,
                   COUNT(*) AS total_livros,
                   ROUND(AVG(numero_de_exemplares), 2) AS media_exemplares
            FROM biblioteca.livros
            WHERE id_categoria IS NOT NULL
            GROUP BY id_categoria
        ) AS sub
        WHERE sub.media_exemplares > CAST(? AS NUMERIC)
        ORDER BY sub.media_exemplares DESC;
    """
    with transacao() as cursor:
        cursor.execute(sql, (float(media_minima),))
        return _para_dicts(cursor)


def cte_with_resumo_acervo(min_exemplares: int = 10) -> list[dict]:
    """
    [CONCEITO]: CTE, WITH, EXPRESSAO DE TABELA COMUM
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Estrutura uma consulta com cláusula WITH isolando obras em destaque com exemplares >= min_exemplares.
    """
    sql = """
        WITH Acervo_Destaque AS (
            SELECT id_livro, nome, autor, genero, numero_de_exemplares
            FROM biblioteca.livros
            WHERE numero_de_exemplares >= ?
        )
        SELECT nome, autor, genero, numero_de_exemplares
        FROM Acervo_Destaque
        ORDER BY numero_de_exemplares DESC, nome ASC;
    """
    with transacao() as cursor:
        cursor.execute(sql, (int(min_exemplares),))
        return _para_dicts(cursor)


def classificacao_case_when_e_dml_subconsulta() -> dict:
    """
    [CONCEITO]: CASE WHEN, EXPRESSAO CONDICIONAL, INSERT SELECT, DELETE SUBCONSULTA
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Classifica o estoque com CASE WHEN e demonstra INSERT INTO ... SELECT e DELETE ... WHERE IN (SELECT ...) com rollback seguro.
    """
    sql_case = """
        SELECT nome,
               numero_de_exemplares,
               CASE
                   WHEN numero_de_exemplares >= 15 THEN 'Alto Estoque'
                   WHEN numero_de_exemplares >= 5  THEN 'Estoque Regular'
                   ELSE 'Estoque Crítico'
               END AS faixa_estoque
        FROM biblioteca.livros
        ORDER BY numero_de_exemplares DESC;
    """
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_case)
        classificados = _para_dicts(cursor)

        cursor.execute(
            """
            INSERT INTO biblioteca.tags (nome)
            SELECT 'DemoSub-' || nome
            FROM biblioteca.categorias_acervo
            WHERE id_categoria = ?;
            """,
            (1,),
        )
        inseridos = cursor.rowcount

        cursor.execute(
            """
            DELETE FROM biblioteca.tags
            WHERE id_tag IN (
                SELECT id_tag FROM biblioteca.tags WHERE nome LIKE ?
            );
            """,
            ("DemoSub-%",),
        )
        removidos = cursor.rowcount
    finally:
        conn.rollback()
        cursor.close()
        conn.close()
    return {"case_when": classificados, "insert_select_linhas": inseridos, "delete_subconsulta_linhas": removidos}


def testar_parte4_completa() -> list[dict]:
    """
    [CONCEITO]: TESTE PARTE 4, IN, NOT IN, SOME, ALL, EXISTS, NOT EXISTS, UNIQUE SUBQUERY, ESCALAR, FROM SUBQUERY, WITH CTE, CASE WHEN, INSERT SELECT
    [CAPÍTULO]: Cap. 3
    [DESCRIÇÃO]: Executa bateria automatizada para todos os 8 itens da Parte 4 da avaliação.
    """
    r1_in = livros_por_tipo_espaco_in("Acervo Geral de Livros", negar=False)
    r1_not = livros_por_tipo_espaco_in("Acervo Geral de Livros", negar=True)
    ok1 = len(r1_in) > 0 and len(r1_not) > 0

    r2 = subconsulta_some_e_all("Tecnologia e Informática")
    ok2 = len(r2["maior_que_some"]) >= len(r2["maior_que_all"]) > 0

    r3_ex = espacos_com_estantes_exists(negar=False)
    r3_nex = espacos_com_estantes_exists(negar=True)
    ok3 = len(r3_ex) > 0 and len(r3_nex) > 0

    r4 = subconsulta_ausencia_duplicatas_unique()
    ok4 = len(r4) > 0

    r5 = subconsulta_escalar_no_select()
    ok5 = len(r5) > 0 and r5[0]["media_geral_acervo"] is not None

    r6 = subconsulta_no_from_media_categoria(5.0)
    ok6 = len(r6) > 0

    r7 = cte_with_resumo_acervo(10)
    ok7 = len(r7) > 0

    r8 = classificacao_case_when_e_dml_subconsulta()
    ok8 = (
        len(r8["case_when"]) > 0
        and r8["insert_select_linhas"] == 1
        and r8["delete_subconsulta_linhas"] == 1
    )

    return [
        {
            "item": "1. Subconsulta de Conjunto (IN e NOT IN)",
            "status": "OK" if ok1 else "FALHA",
            "detalhes": {"in": len(r1_in), "not_in": len(r1_not)},
        },
        {
            "item": "2. Comparação com Conjuntos (> SOME e > ALL)",
            "status": "OK" if ok2 else "FALHA",
            "detalhes": {"maior_que_some": len(r2["maior_que_some"]), "maior_que_all": len(r2["maior_que_all"])},
        },
        {
            "item": "3. Subconsulta Correlacionada (EXISTS e NOT EXISTS)",
            "status": "OK" if ok3 else "FALHA",
            "detalhes": {"exists": len(r3_ex), "not_exists": len(r3_nex)},
        },
        {
            "item": "4. Ausência de Duplicatas (UNIQUE em Subconsulta)",
            "status": "OK" if ok4 else "FALHA",
            "detalhes": {"autores_sem_duplicata": len(r4)},
        },
        {
            "item": "5. Subconsulta Escalar no SELECT",
            "status": "OK" if ok5 else "FALHA",
            "detalhes": {"linhas": len(r5), "media_geral": float(r5[0]["media_geral_acervo"]) if r5 else None},
        },
        {
            "item": "6. Subconsulta na Cláusula FROM (Tabela Derivada)",
            "status": "OK" if ok6 else "FALHA",
            "detalhes": {"categorias_acima_da_media": len(r6)},
        },
        {
            "item": "7. Expressão de Tabela Comum (WITH - CTE)",
            "status": "OK" if ok7 else "FALHA",
            "detalhes": {"obras_em_destaque_cte": len(r7)},
        },
        {
            "item": "8. CASE WHEN e DML com Subconsulta (INSERT/DELETE SELECT)",
            "status": "OK" if ok8 else "FALHA",
            "detalhes": {
                "case_when_linhas": len(r8["case_when"]),
                "insert_select": r8["insert_select_linhas"],
                "delete_in_select": r8["delete_subconsulta_linhas"],
            },
        },
    ]

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
