"""
Módulo de Aplicação e Validação de DDL e Restrições de Integridade (Item 1 da Avaliação).

Todas as demonstrações executam SQL real contra o PostgreSQL via pyodbc
usando Prepared Statements e encerram com rollback() para preservar os dados originais.
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def demonstrar_pk_simples_e_composta() -> dict:
    """
    [CONCEITO AVALIADO] Chaves Primárias (PRIMARY KEY Simples e Composta)
    [SLIDE/CAPÍTULO] Cap. 2 e Cap. 3 (Integridade de Entidade)
    [DESCRIÇÃO] Comprova que o PostgreSQL bloqueia duplicidade tanto na PK simples
                (categorias_acervo.id_categoria) quanto na PK composta (livro_tag(id_livro, id_tag)).
    """
    resultado = {"pk_simples_bloqueou_duplicata": False, "pk_composta_bloqueou_duplicata": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. Teste de PK Simples (tenta duplicar id_categoria = 1)
        try:
            cursor.execute(
                "INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);",
                (1, "Categoria Duplicada"),
            )
        except pyodbc.IntegrityError:
            resultado["pk_simples_bloqueou_duplicata"] = True
            conn.rollback()

        # 2. Teste de PK Composta (tenta duplicar par (1, 1) em livro_tag)
        try:
            cursor.execute(
                "INSERT INTO biblioteca.livro_tag (id_livro, id_tag) VALUES (?, ?);",
                (1, 1),
            )
        except pyodbc.IntegrityError:
            resultado["pk_composta_bloqueou_duplicata"] = True
            conn.rollback()
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_fk_1_1_1_n_n_m() -> dict:
    """
    [CONCEITO AVALIADO] Chaves Estrangeiras e Cardinalidades (1:1, 1:N e N:M)
    [SLIDE/CAPÍTULO] Cap. 2, Cap. 3 e Cap. 4 (Integridade Referencial)
    [DESCRIÇÃO] Consulta os relacionamentos 1:1 (edificacoes <-> ficha_tecnica_edificacao),
                1:N (estantes -> livros) e N:M (livros <-> livro_tag <-> tags), além de testar
                o bloqueio de uma segunda ficha 1:1 para a mesma edificação.
    """
    resultado = {"rel_1_1_bloqueou_segunda_ficha": False, "qtd_1_1": 0, "qtd_1_n": 0, "qtd_n_m": 0}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM biblioteca.ficha_tecnica_edificacao;")
        resultado["qtd_1_1"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM biblioteca.livros;")
        resultado["qtd_1_n"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM biblioteca.livro_tag;")
        resultado["qtd_n_m"] = cursor.fetchone()[0]

        # Valida unicidade do relacionamento 1:1 (edificação 1 já possui ficha técnica)
        try:
            cursor.execute(
                """
                INSERT INTO biblioteca.ficha_tecnica_edificacao
                    (id_endereco, ano_construcao, area_m2)
                VALUES (?, ?, ?);
                """,
                (1, 2020, 500.00),
            )
        except pyodbc.IntegrityError:
            resultado["rel_1_1_bloqueou_segunda_ficha"] = True
            conn.rollback()
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_acoes_cascata() -> dict:
    """
    [CONCEITO AVALIADO] Integridade Referencial em Cascata (ON UPDATE CASCADE e ON DELETE CASCADE)
    [SLIDE/CAPÍTULO] Cap. 4 (Ações Referenciais em Chaves Estrangeiras)
    [DESCRIÇÃO] Em transação temporária com rollback ao final:
                1) Atualiza tipos_de_espaco.tipo e comprova propagação em estantes.tipo (ON UPDATE CASCADE).
                2) Exclui estante temporária e comprova exclusão automática do livro filho (ON DELETE CASCADE).
    """
    resultado = {"on_update_cascade_propagou": False, "on_delete_cascade_removeu_filho": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. ON UPDATE CASCADE: tipos_de_espaco.tipo -> estantes.tipo
        cursor.execute(
            "INSERT INTO biblioteca.tipos_de_espaco (tipo, numero_maximo_de_estantes, eh_privado) VALUES (?, ?, ?);",
            ("Tipo Temporario Original", 10, False),
        )
        cursor.execute(
            """
            INSERT INTO biblioteca.estantes (dominio_lado_1, id_espaco, tipo)
            VALUES (?, ?, ?) RETURNING id_estante;
            """,
            ("Dominio Teste", 1, "Tipo Temporario Original"),
        )
        id_estante_temp = cursor.fetchone()[0]

        cursor.execute(
            "UPDATE biblioteca.tipos_de_espaco SET tipo = ? WHERE tipo = ?;",
            ("Tipo Temporario Renomeado", "Tipo Temporario Original"),
        )
        cursor.execute("SELECT tipo FROM biblioteca.estantes WHERE id_estante = ?;", (id_estante_temp,))
        resultado["on_update_cascade_propagou"] = cursor.fetchone()[0] == "Tipo Temporario Renomeado"

        # 2. ON DELETE CASCADE: estantes -> livros
        cursor.execute(
            """
            INSERT INTO biblioteca.livros (nome, autor, genero, numero_de_exemplares, id_estante)
            VALUES (?, ?, ?, ?, ?) RETURNING id_livro;
            """,
            ("Livro Temporario Cascata", "Autor Teste", "Teste", 2, id_estante_temp),
        )
        id_livro_temp = cursor.fetchone()[0]

        cursor.execute("DELETE FROM biblioteca.estantes WHERE id_estante = ?;", (id_estante_temp,))
        cursor.execute("SELECT COUNT(*) FROM biblioteca.livros WHERE id_livro = ?;", (id_livro_temp,))
        resultado["on_delete_cascade_removeu_filho"] = cursor.fetchone()[0] == 0
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_set_null_e_set_default() -> dict:
    """
    [CONCEITO AVALIADO] Integridade Referencial (ON DELETE SET NULL e ON DELETE SET DEFAULT)
    [SLIDE/CAPÍTULO] Cap. 4 (Ações Referenciais Alternativas ao CASCADE)
    [DESCRIÇÃO] Em transação temporária com rollback ao final:
                1) Exclui um bibliotecário responsável e comprova edificacoes.id_responsavel = NULL.
                2) Exclui uma categoria e comprova livros.id_categoria = 1 (DEFAULT).
    """
    resultado = {"on_delete_set_null_ok": False, "on_delete_set_default_ok": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. ON DELETE SET NULL (bibliotecarios -> edificacoes.id_responsavel)
        cursor.execute(
            """
            INSERT INTO biblioteca.bibliotecarios (nome, email, cpf, status)
            VALUES (?, ?, ?, ?) RETURNING id_bibliotecario;
            """,
            ("Resp Temporario", "resp.temp@biblioteca.edu.br", "12312312312", "Ativo"),
        )
        id_bib = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO biblioteca.edificacoes (endereco, telefone, id_biblioteca, id_responsavel)
            VALUES (?, ?, ?, ?) RETURNING id_endereco;
            """,
            ("Rua Teste Set Null, 99", "(99) 9999-0001", 1, id_bib),
        )
        id_ed = cursor.fetchone()[0]
        cursor.execute("DELETE FROM biblioteca.bibliotecarios WHERE id_bibliotecario = ?;", (id_bib,))
        cursor.execute("SELECT id_responsavel FROM biblioteca.edificacoes WHERE id_endereco = ?;", (id_ed,))
        resultado["on_delete_set_null_ok"] = cursor.fetchone()[0] is None

        # 2. ON DELETE SET DEFAULT (categorias_acervo -> livros.id_categoria DEFAULT 1)
        cursor.execute(
            "INSERT INTO biblioteca.categorias_acervo (id_categoria, nome) VALUES (?, ?);",
            (99, "Categoria Temporaria"),
        )
        cursor.execute(
            """
            INSERT INTO biblioteca.livros (nome, autor, genero, numero_de_exemplares, id_estante, id_categoria)
            VALUES (?, ?, ?, ?, ?, ?) RETURNING id_livro;
            """,
            ("Livro Set Default", "Autor Teste", "Teste", 1, 1, 99),
        )
        id_livro = cursor.fetchone()[0]
        cursor.execute("DELETE FROM biblioteca.categorias_acervo WHERE id_categoria = ?;", (99,))
        cursor.execute("SELECT id_categoria FROM biblioteca.livros WHERE id_livro = ?;", (id_livro,))
        resultado["on_delete_set_default_ok"] = cursor.fetchone()[0] == 1
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_unique_e_not_null() -> dict:
    """
    [CONCEITO AVALIADO] Restrições de Unicidade (UNIQUE) e Não-Nulo (NOT NULL)
    [SLIDE/CAPÍTULO] Cap. 3 e Cap. 4 (Restrições de Integridade em Tabelas)
    [DESCRIÇÃO] Comprova rejeição pelo SGBD ao tentar inserir código de patrimônio duplicado
                (UNIQUE) e livro com nome nulo (NOT NULL).
    """
    resultado = {"unique_bloqueou_duplicata": False, "not_null_bloqueou_vazio": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. UNIQUE (PAT-0001 já existe em livros)
        try:
            cursor.execute(
                """
                INSERT INTO biblioteca.livros (nome, autor, id_estante, codigo_patrimonio)
                VALUES (?, ?, ?, ?);
                """,
                ("Livro Patrimonio Repetido", "Autor", 1, "PAT-0001"),
            )
        except pyodbc.IntegrityError:
            resultado["unique_bloqueou_duplicata"] = True
            conn.rollback()

        # 2. NOT NULL (nome é obrigatório em livros)
        try:
            cursor.execute(
                "INSERT INTO biblioteca.livros (nome, autor, id_estante) VALUES (?, ?, ?);",
                (None, "Autor Sem Titulo", 1),
            )
        except pyodbc.IntegrityError:
            resultado["not_null_bloqueou_vazio"] = True
            conn.rollback()
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_check_faixa_e_lista() -> dict:
    """
    [CONCEITO AVALIADO] Restrições de Checagem (CHECK de Faixa e CHECK com IN)
    [SLIDE/CAPÍTULO] Cap. 4 (Restrições de Domínio / CHECK)
    [DESCRIÇÃO] Comprova rejeição ao tentar inserir numero_de_exemplares negativo (faixa >= 0)
                e status_conservacao fora da lista permitida ('Novo', 'Bom', 'Regular', 'Danificado').
    """
    resultado = {"check_faixa_bloqueou": False, "check_lista_in_bloqueou": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # 1. CHECK de faixa (numero_de_exemplares >= 0)
        try:
            cursor.execute(
                "INSERT INTO biblioteca.livros (nome, numero_de_exemplares, id_estante) VALUES (?, ?, ?);",
                ("Livro Negativo", -5, 1),
            )
        except pyodbc.IntegrityError:
            resultado["check_faixa_bloqueou"] = True
            conn.rollback()

        # 2. CHECK com IN (status_conservacao IN ('Novo', 'Bom', 'Regular', 'Danificado'))
        try:
            cursor.execute(
                """
                INSERT INTO biblioteca.livros (nome, status_conservacao, id_estante)
                VALUES (?, ?, ?);
                """,
                ("Livro Status Invalido", "Destruido", 1),
            )
        except pyodbc.IntegrityError:
            resultado["check_lista_in_bloqueou"] = True
            conn.rollback()
    finally:
        conn.rollback()
        conn.close()
    return resultado


def demonstrar_valores_default() -> dict:
    """
    [CONCEITO AVALIADO] Valores Padrão (DEFAULT)
    [SLIDE/CAPÍTULO] Cap. 4 (Definição de Valores Padrão em DDL)
    [DESCRIÇÃO] Insere um livro informando apenas nome e id_estante, comprovando o
                preenchimento automático de numero_de_exemplares, pode_ser_emprestado,
                status_conservacao, id_categoria e data_cadastro.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO biblioteca.livros (nome, id_estante)
            VALUES (?, ?)
            RETURNING numero_de_exemplares, pode_ser_emprestado, status_conservacao, id_categoria, data_cadastro;
            """,
            ("Livro Teste Default", 1),
        )
        linha = fetch_as_dicts(cursor)[0]
        return {
            "numero_de_exemplares_default": linha["numero_de_exemplares"],
            "pode_ser_emprestado_default": str(linha["pode_ser_emprestado"]) in ("True", "1"),
            "status_conservacao_default": linha["status_conservacao"],
            "id_categoria_default": linha["id_categoria"],
            "data_cadastro_preenchida": linha["data_cadastro"] is not None,
        }
    finally:
        conn.rollback()
        conn.close()


def demonstrar_alter_table_add_drop() -> dict:
    """
    [CONCEITO AVALIADO] Modificação de Esquema (ALTER TABLE ADD COLUMN / DROP COLUMN)
    [SLIDE/CAPÍTULO] Cap. 3 (DDL - Alteração de Esquema)
    [DESCRIÇÃO] Adiciona uma coluna temporária em biblioteca.livros, confirma sua existência
                no catálogo information_schema.columns e a remove em seguida (transação segura).
    """
    resultado = {"coluna_adicionada": False, "coluna_removida": False}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE biblioteca.livros ADD COLUMN coluna_demo_avaliacao VARCHAR(40);")
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'biblioteca'
              AND table_name = 'livros'
              AND column_name = 'coluna_demo_avaliacao';
            """
        )
        resultado["coluna_adicionada"] = cursor.fetchone()[0] == 1

        cursor.execute("ALTER TABLE biblioteca.livros DROP COLUMN coluna_demo_avaliacao;")
        cursor.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'biblioteca'
              AND table_name = 'livros'
              AND column_name = 'coluna_demo_avaliacao';
            """
        )
        resultado["coluna_removida"] = cursor.fetchone()[0] == 0
    finally:
        conn.rollback()
        conn.close()
    return resultado


def executar_bateria_completa_ddl() -> list[dict]:
    """
    Executa todos os validadores do Item 1 (DDL e Restrições de Integridade)
    e retorna um resumo estruturado pronto para exibição na interface ou terminal.
    """
    testes = [
        ("1. PK Simples e PK Composta", demonstrar_pk_simples_e_composta),
        ("2. FK: Relacionamentos 1:1, 1:N e N:M", demonstrar_fk_1_1_1_n_n_m),
        ("3. FK: ON UPDATE CASCADE e ON DELETE CASCADE", demonstrar_acoes_cascata),
        ("4. FK: ON DELETE SET NULL e ON DELETE SET DEFAULT", demonstrar_set_null_e_set_default),
        ("5. UNIQUE e NOT NULL", demonstrar_unique_e_not_null),
        ("6. CHECK de Faixa e CHECK com Lista (IN)", demonstrar_check_faixa_e_lista),
        ("7. Valores Padrão (DEFAULT)", demonstrar_valores_default),
        ("8. ALTER TABLE ADD / DROP COLUMN", demonstrar_alter_table_add_drop),
    ]
    relatorio = []
    for nome, func in testes:
        detalhes = func()
        ok = all(bool(v) for v in detalhes.values())
        relatorio.append({"conceito": nome, "status": "OK" if ok else "FALHA", "detalhes": detalhes})
    return relatorio
