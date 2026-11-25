"""
Menu Centralizador da Aplicação (Categorizado por Módulos e Capítulos do Silberschatz).
Permite navegar diretamente até o conceito exigido durante a avaliação oral.
"""
from src.services import (
    crud_basico,
    algebra_relacional,
    agregacoes_conjuntos,
    subconsultas,
    juncoes_visoes,
    programacao_banco,
    metadados,
)


def _exibir_tabela(registros: list[dict] | None, titulo: str) -> None:
    print(f"\n=== {titulo} ===")
    if registros is None:
        print("[Aviso] Função ainda em esqueleto (placeholder) ou ocorreu erro na consulta.")
        return
    if not registros:
        print("Nenhum registro retornado.")
        return
    colunas = list(registros[0].keys())
    print(" | ".join(colunas))
    print("-" * 70)
    for linha in registros:
        print(" | ".join(str(linha.get(c, "NULL")) for c in colunas))
    print(f"Total: {len(registros)} registro(s).")


def _menu_crud():
    while True:
        print("\n--- [Módulo 1] CRUD Básico (Cap. 3 - Prepared Statements) ---")
        print("1. [Cap. 3] SELECT - Listar livros")
        print("2. [Cap. 3] INSERT - Cadastrar novo livro")
        print("3. [Cap. 3] UPDATE - Atualizar livro")
        print("4. [Cap. 3] DELETE - Excluir livro")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            _exibir_tabela(crud_basico.listar_livros(), "Livros Cadastrados")
        elif op == "2":
            nome = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Gênero: ").strip() or "Geral"
            exemplares = int(input("Exemplares: ").strip() or "1")
            id_estante = int(input("ID Estante: ").strip() or "1")
            ok = crud_basico.cadastrar_livro(nome, autor, genero, exemplares, True, id_estante)
            print("Cadastrado com sucesso!" if ok else "Falha ao cadastrar.")
        elif op == "3":
            id_livro = int(input("ID do livro: ").strip())
            nome = input("Novo título: ").strip()
            autor = input("Novo autor: ").strip()
            genero = input("Novo gênero: ").strip()
            exemplares = int(input("Novos exemplares: ").strip())
            ok = crud_basico.atualizar_livro(id_livro, nome, autor, genero, exemplares, True)
            print("Atualizado!" if ok else "Livro não encontrado ou erro.")
        elif op == "4":
            id_livro = int(input("ID do livro para excluir: ").strip())
            ok = crud_basico.excluir_livro(id_livro)
            print("Excluído!" if ok else "Livro não encontrado ou erro.")


def _menu_algebra():
    while True:
        print("\n--- [Módulo 2] Álgebra Relacional (Cap. 2 e Cap. 3) ---")
        print("1. [Cap. 2/3] Projeção + DISTINCT + AS (Autores únicos)")
        print("2. [Cap. 3]   Seleção com AND, OR, ILIKE e BETWEEN")
        print("3. [Cap. 3]   Predicado IS NULL (Estantes sem domínio lado 2)")
        print("4. [Cap. 2/3] Produto Cartesiano / Auto-junção (Pares de livros)")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            _exibir_tabela(algebra_relacional.projecao_autores_unicos(), "Projeção + DISTINCT")
        elif op == "2":
            termo = input("Termo: ").strip()
            mi = int(input("Mínimo de exemplares: ").strip() or "0")
            ma = int(input("Máximo de exemplares: ").strip() or "50")
            _exibir_tabela(algebra_relacional.selecao_multiplos_predicados(termo, mi, ma), "Seleção Composta")
        elif op == "3":
            _exibir_tabela(algebra_relacional.selecao_valores_nulos(), "Predicado IS NULL")
        elif op == "4":
            genero = input("Gênero: ").strip()
            _exibir_tabela(algebra_relacional.produto_cartesiano_auto_juncao_mesmo_genero(genero), "Auto-junção")


def _menu_agregacoes_conjuntos():
    while True:
        print("\n--- [Módulo 3] Relatórios: Agregações e Conjuntos (Cap. 3) ---")
        print("1. [Cap. 3] Agregações (COUNT/SUM/AVG) + GROUP BY com HAVING")
        print("2. [Cap. 3] Operação de Conjunto: UNION")
        print("3. [Cap. 3] Operação de Conjunto: INTERSECT (Autores multigênero)")
        print("4. [Cap. 3] Operação de Conjunto: EXCEPT (Estantes vazias)")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            media = float(input("Média mínima de exemplares: ").strip() or "1")
            _exibir_tabela(agregacoes_conjuntos.estatisticas_por_genero_com_having(media), "GROUP BY + HAVING")
        elif op == "2":
            _exibir_tabela(agregacoes_conjuntos.conjunto_union_dominios_estantes(), "UNION")
        elif op == "3":
            g1 = input("Gênero 1: ").strip()
            g2 = input("Gênero 2: ").strip()
            _exibir_tabela(agregacoes_conjuntos.conjunto_intersect_autores_multigenero(g1, g2), "INTERSECT")
        elif op == "4":
            _exibir_tabela(agregacoes_conjuntos.conjunto_except_estantes_vazias(), "EXCEPT")


def _menu_subconsultas():
    while True:
        print("\n--- [Módulo 4] Subconsultas e CTEs (Cap. 3) ---")
        print("1. [Cap. 3] Subconsulta Escalar (Livros acima da média)")
        print("2. [Cap. 3] Subconsulta com IN (Livros por tipo de espaço)")
        print("3. [Cap. 3] Subconsulta SOME/ALL + CTE WITH (Acervo crítico)")
        print("4. [Cap. 3] Subconsulta Correlacionada com EXISTS")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            _exibir_tabela(subconsultas.subconsulta_escalar_acima_da_media(), "Subconsulta Escalar")
        elif op == "2":
            tipo = input("Tipo de espaço: ").strip()
            _exibir_tabela(subconsultas.subconsulta_in_not_in_estantes_por_tipo(tipo), "Subconsulta IN")
        elif op == "3":
            dom = input("Domínio das estantes: ").strip()
            gen = input("Gênero de comparação: ").strip()
            _exibir_tabela(subconsultas.subconsulta_some_all_acervo_critico(dom, gen), "CTE + SOME")
        elif op == "4":
            _exibir_tabela(subconsultas.subconsulta_correlacionada_exists_espacos_com_estantes(), "EXISTS")


def _menu_juncoes_visoes():
    while True:
        print("\n--- [Módulo 5] Consultas Avançadas: Junções e Visões (Cap. 4) ---")
        print("1. [Cap. 4] NATURAL JOIN (Livros × Estantes)")
        print("2. [Cap. 4] INNER JOIN (Estantes × Espaços)")
        print("3. [Cap. 4] LEFT OUTER JOIN (Espaços × Estantes)")
        print("4. [Cap. 4] RIGHT OUTER JOIN (Espaços × Estantes)")
        print("5. [Cap. 4] FULL OUTER JOIN (Espaços × Estantes)")
        print("6. [Cap. 4] Visão Tradicional (VIEW vw_livros_localizacao_completa)")
        print("7. [Cap. 4] Visão Materializada (MATERIALIZED VIEW ranking autores)")
        print("8. [Cap. 4] Atualizar Visão Materializada (REFRESH MATERIALIZED VIEW)")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            _exibir_tabela(juncoes_visoes.juncao_natural_livros_estantes(), "NATURAL JOIN")
        elif op == "2":
            _exibir_tabela(juncoes_visoes.juncao_inner_estantes_espacos(), "INNER JOIN")
        elif op == "3":
            _exibir_tabela(juncoes_visoes.juncao_left_outer_espacos_estantes(), "LEFT OUTER JOIN")
        elif op == "4":
            _exibir_tabela(juncoes_visoes.juncao_right_outer_espacos_estantes(), "RIGHT OUTER JOIN")
        elif op == "5":
            _exibir_tabela(juncoes_visoes.juncao_full_outer_espacos_estantes(), "FULL OUTER JOIN")
        elif op == "6":
            _exibir_tabela(juncoes_visoes.consultar_visao_localizacao_completa(), "VIEW Tradicional")
        elif op == "7":
            _exibir_tabela(juncoes_visoes.consultar_visao_materializada_ranking_autores(), "MATERIALIZED VIEW")
        elif op == "8":
            ok = juncoes_visoes.atualizar_visao_materializada()
            print("REFRESH executado com sucesso!" if ok else "Falha no REFRESH.")


def _menu_programacao_metadados():
    while True:
        print("\n--- [Módulo 6] Programação no Banco (Cap. 5) e Metadados (Cap. 8) ---")
        print("1. [Cap. 5] Stored Function (SELECT fn_contar_livros_por_autor)")
        print("2. [Cap. 5] Stored Procedure (CALL sp_cadastrar_livro)")
        print("3. [Cap. 5] Trigger de Auditoria (DELETE + consulta auditoria)")
        print("4. [Cap. 5] Consulta Recursiva (WITH RECURSIVE)")
        print("5. [Cap. 8] Metadados ODBC: Listar tabelas do schema (cursor.tables)")
        print("6. [Cap. 8] Metadados ODBC: Listar colunas de tabela (cursor.columns)")
        print("0. Voltar")
        op = input("Escolha: ").strip()
        if op == "0":
            break
        elif op == "1":
            autor = input("Nome do autor: ").strip()
            total = programacao_banco.chamar_function_total_por_autor(autor)
            print(f"Total encontrado pela FUNCTION: {total}")
        elif op == "2":
            nome = input("Título: ").strip()
            autor = input("Autor: ").strip()
            genero = input("Gênero: ").strip() or "Geral"
            ok = programacao_banco.chamar_procedure_cadastrar_livro(nome, autor, genero, 1, True, 1)
            print("Cadastrado via PROCEDURE!" if ok else "Erro na PROCEDURE.")
        elif op == "3":
            id_livro = int(input("ID do livro para testar trigger de exclusão: ").strip())
            _exibir_tabela(programacao_banco.demonstrar_trigger_auditoria_exclusao(id_livro), "Auditoria Trigger")
        elif op == "4":
            _exibir_tabela(programacao_banco.consulta_recursiva_hierarquia_biblioteca(), "WITH RECURSIVE")
        elif op == "5":
            _exibir_tabela(metadados.inspecionar_tabelas_schema(), "Metadados: Tabelas")
        elif op == "6":
            tabela = input("Nome da tabela (ex: livros): ").strip() or "livros"
            _exibir_tabela(metadados.inspecionar_colunas_tabela(tabela), f"Metadados: Colunas de {tabela}")


def iniciar_menu_console() -> None:
    """Loop principal do centralizador categorizado por capítulos."""
    while True:
        print("\n============================================================")
        print("   SISTEMA DE BIBLIOTECA — AVALIAÇÃO DE BANCO DE DADOS")
        print("============================================================")
        print("1. CRUD Básico                              [Cap. 3]")
        print("2. Álgebra Relacional (Projeção/Seleção)    [Cap. 2 e 3]")
        print("3. Relatórios -> Agregações e Conjuntos     [Cap. 3]")
        print("4. Consultas Avançadas -> Subconsultas/CTE  [Cap. 3]")
        print("5. Consultas Avançadas -> Junções e Visões  [Cap. 4]")
        print("6. Programação no Banco e Metadados ODBC    [Cap. 5 e 8]")
        print("0. Sair")

        opcao = input("\nEscolha uma categoria: ").strip()
        if opcao == "1":
            _menu_crud()
        elif opcao == "2":
            _menu_algebra()
        elif opcao == "3":
            _menu_agregacoes_conjuntos()
        elif opcao == "4":
            _menu_subconsultas()
        elif opcao == "5":
            _menu_juncoes_visoes()
        elif opcao == "6":
            _menu_programacao_metadados()
        elif opcao == "0":
            print("Encerrando aplicação.")
            break
        else:
            print("Opção inválida.")
