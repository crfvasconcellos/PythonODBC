"""
Ponto de Entrada do Sistema da Biblioteca.

Como rodar:
    python app.py              -> Abre o menu interativo no terminal (5 seções)
    python app.py --web        -> Abre o servidor Web + API em http://127.0.0.1:8000
    python app.py --web 8080   -> Abre o servidor Web em outra porta
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import pyodbc
import biblioteca as bib

# Pasta onde ficam os arquivos HTML, CSS e JS da interface visual
PASTA_INTERFACE_WEB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "Interface-biblioteca"
)


# ==============================================================================
# PARTE 1: MENU INTERATIVO NO TERMINAL
# ==============================================================================

def mostrar_tabela(registros, titulo):
    """Imprime uma lista de dicionários em formato de tabela simples no terminal."""
    print(f"\n=== {titulo} ===")
    if not registros:
        print("Nenhum registro retornado.")
        return

    colunas = list(registros[0].keys())
    print(" | ".join(colunas))
    print("-" * 75)

    for linha in registros:
        valores = []
        for col in colunas:
            valor = linha.get(col)
            valores.append("NULL" if valor is None else str(valor))
        print(" | ".join(valores))

    print(f"({len(registros)} registro(s))")


def menu_secao_1():
    """Seção 1: Operações básicas de CRUD (Criar, Ler, Atualizar, Excluir) e testes DDL."""
    while True:
        print("\n--- [Seção 1] CRUD Básico e Integridade (Cap. 1 a 4) ---")
        print("1. Listar livros (SELECT)")
        print("2. Cadastrar livro (INSERT + Prepared Statement)")
        print("3. Atualizar livro (UPDATE)")
        print("4. Excluir livro (DELETE + Trigger Auditoria)")
        print("5. Validar todas as restrições DDL (PK, FK, CASCADE, SET NULL/DEFAULT, UNIQUE, CHECK, ALTER)")
        print("6. Listar estantes disponíveis")
        print("7. Criar nova estante")
        print("8. Excluir estante (ATENÇÃO: apaga todos os livros da estante)")
        print("0. Voltar")

        opcao = input("Opção: ").strip()
        try:
            if opcao == "0":
                break
            elif opcao == "1":
                livros = bib.listar_livros()
                mostrar_tabela(livros, "Livros Cadastrados")
            elif opcao == "2":
                estantes = bib.listar_estantes()
                if estantes:
                    mostrar_tabela(estantes, "Estantes Disponíveis para Cadastro")
                else:
                    print("\n[AVISO] Nenhuma estante cadastrada! Crie uma estante na opção 7 antes de cadastrar livros.")

                nome = input("Título: ").strip()
                autor = input("Autor: ").strip()
                genero = input("Gênero: ").strip() or "Geral"
                exemplares = int(input("Exemplares: ").strip() or "1")
                id_estante = int(input("ID Estante: ").strip() or "1")
                patrimonio = input("Código Patrimônio (opcional, UNIQUE): ").strip() or None

                bib.cadastrar_livro(nome, autor, genero, exemplares, True, id_estante, patrimonio)
                print("Livro cadastrado com sucesso!")
            elif opcao == "3":
                id_livro = int(input("ID do livro: ").strip())
                nome = input("Novo título: ").strip()
                autor = input("Novo autor: ").strip()
                genero = input("Novo gênero: ").strip()
                exemplares = int(input("Novos exemplares: ").strip())

                atualizou = bib.atualizar_livro(id_livro, nome, autor, genero, exemplares, True)
                if atualizou:
                    print("Atualizado!")
                else:
                    print("Livro não encontrado.")
            elif opcao == "4":
                id_livro = int(input("ID do livro para excluir: ").strip())
                excluiu = bib.excluir_livro(id_livro)
                if excluiu:
                    print("Excluído!")
                else:
                    print("Livro não encontrado.")
            elif opcao == "5":
                for item in bib.testar_parte1_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            elif opcao == "6":
                mostrar_tabela(bib.listar_estantes(), "Estantes Cadastradas")
            elif opcao == "7":
                dom1 = input("Domínio Lado 1 (ex: Ficção Científica): ").strip()
                dom2 = input("Domínio Lado 2 (ex: Romance Clássico): ").strip() or "Geral"
                cap = int(input("Capacidade de livros (padrão 100): ").strip() or "100")
                novo_id = bib.cadastrar_estante(dom1, dom2, cap)
                print(f"Estante criada com sucesso! ID da estante: {novo_id}")
            elif opcao == "8":
                mostrar_tabela(bib.listar_estantes(), "Estantes Cadastradas")
                id_est = int(input("ID da estante para excluir: ").strip())
                confirma = input(
                    f"⚠️ ATENÇÃO: Excluir a estante {id_est} apagará TODOS os livros guardados nela! Confirmar? (s/N): "
                ).strip().lower()
                if confirma == "s":
                    res = bib.excluir_estante(id_est)
                    if res["excluiu"]:
                        print(f"Estante {id_est} excluída! ({res['livros_removidos']} livro(s) removido(s) junto com ela).")
                    else:
                        print("Estante não encontrada.")
                else:
                    print("Exclusão cancelada.")
            else:
                print("Opção inválida! Tente novamente.")
        except (ValueError, pyodbc.Error) as erro:
            print(f"[ERRO] {erro}")


def menu_secao_2():
    """Seção 2: Consultas de Álgebra Relacional, filtros LIKE, BETWEEN e valores NULL."""
    while True:
        print("\n--- [Seção 2] Álgebra Relacional e Buscas (Cap. 2 e 3) ---")
        print("1. Projeção DISTINCT vs ALL e Atributo Calculado")
        print("2. Seleção Composta (AND/OR/NOT) e Comparação de Tupla")
        print("3. Produto Cartesiano (|R|x|S|) e Junção Teta")
        print("4. Renomeação (AS) e Auto-junção / SELF JOIN")
        print("5. Strings: LIKE (% e _), ||, UPPER() e LOWER()")
        print("6. Faixa de Exemplares (BETWEEN / NOT BETWEEN)")
        print("7. Valores Nulos (IS NULL / IS NOT NULL) e ORDER BY NULLS FIRST/LAST")
        print("8. Executar bateria completa da Parte 2 (todos os 8 itens)")
        print("0. Voltar")

        opcao = input("Opção: ").strip()
        try:
            if opcao == "0":
                break
            elif opcao == "1":
                resultado = bib.projecao_distinct_all_e_calculo()
                mostrar_tabela(resultado["distinct"], "DISTINCT status_conservacao")
                mostrar_tabela(resultado["calculados"], "Projeção com Atributo Calculado")
            elif opcao == "2":
                resultado = bib.selecao_predicados_compostos_e_tupla()
                mostrar_tabela(resultado["predicados_compostos"], "Seleção com Predicados Compostos")
                mostrar_tabela(resultado["comparacao_tupla"], "Predicado com Tupla")
            elif opcao == "3":
                resultado = bib.produto_cartesiano_e_juncao_teta()
                print(
                    f"\nProduto Cartesiano: {resultado['qtd_livros']} x "
                    f"{resultado['qtd_espacos']} = {resultado['total_cartesiano']} linhas"
                )
                mostrar_tabela(resultado["juncao_teta"], "Junção Teta (WHERE l.id_categoria = c.id_categoria)")
            elif opcao == "4":
                genero = input("Gênero (ex: Romance Clássico): ").strip() or "Romance Clássico"
                mostrar_tabela(bib.auto_juncao_livros_mesmo_autor_genero(genero), f"SELF JOIN ({genero})")
            elif opcao == "5":
                resultado = bib.buscar_strings_like_coringa_posicao()
                mostrar_tabela(resultado["like_percent"], "LIKE com % + UPPER/LOWER/||")
                mostrar_tabela(resultado["like_underline"], "LIKE com _ (PAT-____)")
            elif opcao == "6":
                minimo = int(input("Mínimo: ").strip() or "10")
                maximo = int(input("Máximo: ").strip() or "20")
                usar_not = input("Usar NOT BETWEEN? (s/N): ").strip().lower() == "s"
                livros = bib.buscar_livros_por_faixa_exemplares(minimo, maximo, usar_not)
                mostrar_tabela(livros, f"Faixa {minimo}..{maximo}")
            elif opcao == "7":
                resultado = bib.consultar_nulos_e_nao_nulos()
                mostrar_tabela(resultado["com_nulo"], "IS NULL (sem patrimônio)")
                mostrar_tabela(bib.ordenar_livros_multiatributo_nulos(True), "ORDER BY ... NULLS FIRST")
            elif opcao == "8":
                for item in bib.testar_parte2_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            else:
                print("Opção inválida! Tente novamente.")
        except (ValueError, pyodbc.Error) as erro:
            print(f"[ERRO] {erro}")


def menu_secao_3():
    """Seção 3: Subconsultas (IN, EXISTS, SOME, CTE) e Conjuntos (UNION, INTERSECT, EXCEPT)."""
    while True:
        print("\n--- [Seção 3] Subconsultas e Operações de Conjunto (Cap. 3) ---")
        print("1. Subconsulta Escalar (Livros acima da média)")
        print("2. Subconsulta IN / NOT IN (Livros por tipo de espaço)")
        print("3. Subconsulta Correlacionada EXISTS / NOT EXISTS (Espaços x Estantes)")
        print("4. CTE (WITH) + SOME + Subconsulta no FROM (Acervo crítico)")
        print("5. UNION vs UNION ALL (Temas/Domínios)")
        print("6. INTERSECT vs INTERSECT ALL (Categorias por status)")
        print("7. EXCEPT vs EXCEPT ALL (Subtração de categorias / estantes vazias)")
        print("8. Executar bateria completa da Parte 3 (Agregações + Conjuntos 6/6)")
        print("0. Voltar")

        opcao = input("Opção: ").strip()
        try:
            if opcao == "0":
                break
            elif opcao == "1":
                mostrar_tabela(bib.livros_acima_da_media_escalar(), "Subconsulta Escalar")
            elif opcao == "2":
                tipo = input("Tipo de espaço (ex: Acervo Geral de Livros): ").strip() or "Acervo Geral de Livros"
                usar_not = input("Usar NOT IN? (s/N): ").strip().lower() == "s"
                mostrar_tabela(bib.livros_por_tipo_espaco_in(tipo, usar_not), "Subconsulta IN/NOT IN")
            elif opcao == "3":
                usar_not = input("Usar NOT EXISTS? (s/N): ").strip().lower() == "s"
                mostrar_tabela(bib.espacos_com_estantes_exists(usar_not), "EXISTS / NOT EXISTS")
            elif opcao == "4":
                dominio = input("Domínio das estantes (ex: Ficção Científica): ").strip() or "Ficção Científica"
                genero = input("Gênero de comparação (ex: Romance Clássico): ").strip() or "Romance Clássico"
                mostrar_tabela(bib.analise_acervo_critico(dominio, genero), "CTE + SOME")
            elif opcao == "5":
                resultado = bib.comparar_union_vs_union_all()
                print(f"\nUNION: {len(resultado['union'])} | UNION ALL: {len(resultado['union_all'])}")
                mostrar_tabela(resultado["union"], "UNION Temas")
            elif opcao == "6":
                resultado = bib.comparar_intersect_vs_intersect_all()
                print(f"\nINTERSECT: {len(resultado['intersect'])} | INTERSECT ALL: {len(resultado['intersect_all'])}")
                mostrar_tabela(resultado["intersect"], "INTERSECT Categorias")
            elif opcao == "7":
                resultado = bib.comparar_except_vs_except_all()
                print(f"\nEXCEPT: {len(resultado['except'])} | EXCEPT ALL: {len(resultado['except_all'])}")
                mostrar_tabela(resultado["except"], "EXCEPT Categorias")
            elif opcao == "8":
                for item in bib.testar_parte3_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            else:
                print("Opção inválida! Tente novamente.")
        except (ValueError, pyodbc.Error) as erro:
            print(f"[ERRO] {erro}")


def menu_secao_4():
    """Seção 4: Agregações (GROUP BY/HAVING), JOINs, Views, Functions, Procedures e Triggers."""
    while True:
        print("\n--- [Seção 4] Agregações, Junções, Visões e Banco (Cap. 3, 4 e 5) ---")
        print("1. GROUP BY + HAVING + COUNT/SUM/AVG/MIN/MAX (Estatísticas por gênero)")
        print("2. NATURAL JOIN / INNER / LEFT / RIGHT / FULL OUTER JOIN")
        print("3. Visão Tradicional (VIEW vw_livros_localizacao_completa)")
        print("4. Visão Materializada (Consultar + REFRESH MATERIALIZED VIEW)")
        print("5. Stored Function (fn_contar_livros_por_autor)")
        print("6. Stored Procedure (CALL sp_cadastrar_livro)")
        print("7. Trigger de Auditoria (Consultar biblioteca.auditoria_livros_excluidos)")
        print("8. Consulta Recursiva (WITH RECURSIVE pisos)")
        print("9. Executar bateria completa da Parte 4 (Subconsultas, CTEs e CASE 8/8)")
        print("0. Voltar")

        opcao = input("Opção: ").strip()
        try:
            if opcao == "0":
                break
            elif opcao == "1":
                media = float(input("Média mínima de exemplares: ").strip() or "1")
                mostrar_tabela(bib.relatorio_estatisticas_genero(media), "GROUP BY + HAVING")
            elif opcao == "2":
                tipo_join = input("Tipo (natural | inner | left | right | full): ").strip().lower() or "full"
                mostrar_tabela(bib.executar_join(tipo_join), f"JOIN: {tipo_join.upper()}")
            elif opcao == "3":
                mostrar_tabela(bib.consultar_visao_localizacao_completa(), "VIEW Localização Completa")
            elif opcao == "4":
                atualizar = input("Executar REFRESH antes? (S/n): ").strip().lower() != "n"
                if atualizar:
                    bib.atualizar_visao_materializada()
                    print("REFRESH MATERIALIZED VIEW concluído!")
                mostrar_tabela(bib.consultar_visao_materializada(), "MATERIALIZED VIEW Ranking Autores")
            elif opcao == "5":
                autor = input("Autor: ").strip()
                resultado = bib.consultar_total_por_autor(autor)
                print(f"Total retornado pela FUNCTION: {resultado['total']}")
                mostrar_tabela(resultado["livros"], f"Livros de {autor}")
            elif opcao == "6":
                nome = input("Título: ").strip()
                autor = input("Autor: ").strip()
                genero = input("Gênero: ").strip() or "Geral"
                bib.cadastrar_livro_via_procedure(nome, autor, genero, 1, True, 1)
                print("Cadastrado via PROCEDURE!")
            elif opcao == "7":
                mostrar_tabela(bib.consultar_auditoria_trigger(), "Auditoria do Trigger AFTER DELETE")
            elif opcao == "8":
                mostrar_tabela(bib.consulta_recursiva_pisos(), "WITH RECURSIVE Pisos")
            elif opcao == "9":
                for item in bib.testar_parte4_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            else:
                print("Opção inválida! Tente novamente.")
        except (ValueError, pyodbc.Error) as erro:
            print(f"[ERRO] {erro}")


def menu_secao_5():
    """Seção 5: Inspecionar metadados do banco via ODBC, índices e permissões (DCL)."""
    while True:
        print("\n--- [Seção 5] Junções, Visões, Índices, DCL e Metadados (Cap. 4 e 5) ---")
        print("1. Listar tabelas e views do schema (cursor.tables)")
        print("2. Listar colunas de uma tabela (cursor.columns)")
        print("3. Inspecionar índices do schema (pg_indexes)")
        print("4. Demonstrar DCL (CREATE ROLE, GRANT, REVOKE, DROP com rollback)")
        print("5. Executar bateria completa da Parte 5 (JOINs, Views, Índices e DCL 7/7)")
        print("6. Executar bateria completa da Parte 6 (Functions, Procedures, Triggers, OLAP e ODBC 6/6)")
        print("0. Voltar")

        opcao = input("Opção: ").strip()
        try:
            if opcao == "0":
                break
            elif opcao == "1":
                mostrar_tabela(bib.inspecionar_tabelas_schema(), "Metadados: Tabelas")
            elif opcao == "2":
                tabela = input("Nome da tabela (ex: livros): ").strip() or "livros"
                mostrar_tabela(bib.inspecionar_colunas_tabela(tabela), f"Metadados: Colunas de {tabela}")
            elif opcao == "3":
                mostrar_tabela(bib.inspecionar_indices_schema(), "Índices (pg_indexes)")
            elif opcao == "4":
                print(bib.demonstrar_dcl_grant_revoke())
            elif opcao == "5":
                for item in bib.testar_parte5_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            elif opcao == "6":
                for item in bib.testar_parte6_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
            else:
                print("Opção inválida! Tente novamente.")
        except pyodbc.Error as erro:
            print(f"[ERRO] {erro}")


def menu_console():
    """Menu principal exibido no terminal quando rodamos `python app.py`."""
    while True:
        print("\n============================================================")
        print("   SISTEMA DA BIBLIOTECA — ESTRUTURA MÍNIMA ENXUTA")
        print("============================================================")
        print("1. Seção 1: CRUD Básico e Integridade       [Cap. 1 a 4]")
        print("2. Seção 2: Álgebra Relacional e Buscas     [Cap. 2 e 3]")
        print("3. Seção 3: Subconsultas e Conjuntos        [Cap. 3]")
        print("4. Seção 4: Agregações, JOINs, Views e BD   [Cap. 3, 4 e 5]")
        print("5. Seção 5: Metadados via ODBC              [Cap. 5]")
        print("0. Sair")

        opcao = input("\nEscolha uma seção: ").strip()
        if opcao == "1":
            menu_secao_1()
        elif opcao == "2":
            menu_secao_2()
        elif opcao == "3":
            menu_secao_3()
        elif opcao == "4":
            menu_secao_4()
        elif opcao == "5":
            menu_secao_5()
        elif opcao == "0":
            print("Encerrado.")
            break
        else:
            print("Opção inválida! Tente novamente.")


# ==============================================================================
# PARTE 2: SERVIDOR WEB E API PARA A INTERFACE DO NAVEGADOR (--web)
# ==============================================================================

def converter_para_json(valor):
    """Converte tipos do banco (Decimal e Datas) para formatos que o JSON entende."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return str(valor)


def converter_para_booleano(valor):
    """Transforma textos como 'true', '1', 'sim' em True ou False."""
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ("true", "1", "sim", "s")


class ServidorBiblioteca(SimpleHTTPRequestHandler):
    """
    Servidor HTTP simples do Python:
    1) Entrega os arquivos da pasta 'Interface-biblioteca' (index.html, css, js).
    2) Responde aos pedidos da interface que começam com '/api/...' chamando o biblioteca.py.
    """

    def __init__(self, *args, **kwargs):
        # Configura o servidor para entregar os arquivos da pasta Interface-biblioteca
        super().__init__(*args, directory=PASTA_INTERFACE_WEB, **kwargs)

    def responder_json(self, codigo_http, dados):
        """Envia uma resposta em formato JSON para o navegador."""
        texto_json = json.dumps(dados, ensure_ascii=False, default=converter_para_json)
        bytes_json = texto_json.encode("utf-8")

        self.send_response(codigo_http)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(bytes_json)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(bytes_json)

    def ler_json_recebido(self):
        """Lê os dados em JSON enviados pelo navegador (no cadastro ou atualização)."""
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho == 0:
            return {}
        texto = self.rfile.read(tamanho).decode("utf-8")
        dados = json.loads(texto)
        if not isinstance(dados, dict):
            raise ValueError("Os dados enviados devem ser um objeto JSON.")
        return dados

    def validar_dados_do_livro(self, dados, exigir_estante=True):
        """Verifica se os campos do livro enviados pela tela estão preenchidos corretamente."""
        nome = str(dados.get("nome") or dados.get("titulo") or "").strip()
        autor = str(dados.get("autor") or "").strip()
        genero = str(dados.get("genero") or "").strip()

        if not nome or not autor or not genero:
            raise ValueError("Preencha todos os campos obrigatórios: nome, autor e gênero.")

        try:
            exemplares = int(dados.get("numero_de_exemplares"))
        except (TypeError, ValueError):
            raise ValueError("O número de exemplares deve ser um número inteiro válido.")

        if exemplares < 0:
            raise ValueError("Violação de CHECK: o número de exemplares não pode ser negativo.")

        id_estante = None
        if exigir_estante:
            try:
                id_estante = int(dados.get("id_estante"))
            except (TypeError, ValueError):
                raise ValueError("O ID da estante deve ser um número inteiro válido.")
            if id_estante < 1:
                raise ValueError("O ID da estante deve ser maior que zero.")

        patrimonio = dados.get("codigo_patrimonio")
        if patrimonio is not None and str(patrimonio).strip():
            patrimonio = str(patrimonio).strip()
        else:
            patrimonio = None

        status = str(dados.get("status_conservacao") or "Bom").strip()
        emprestavel = converter_para_booleano(dados.get("pode_ser_emprestado", True))

        return nome, autor, genero, exemplares, emprestavel, id_estante, patrimonio, status

    def processar_rota_api(self, metodo_http):
        """Recebe uma chamada em '/api/...', chama a função SQL do biblioteca.py e devolve JSON."""
        url_separada = urlparse(self.path)
        caminho = unquote(url_separada.path)
        parametros_url = parse_qs(url_separada.query)

        # Função auxiliar simples para pegar um parâmetro da URL (ex: ?busca=Dom)
        def pegar_parametro(nome_parametro):
            lista_valores = parametros_url.get(nome_parametro)
            if lista_valores:
                return lista_valores[0].strip()
            return ""

        try:
            # ------------------------------------------------------------------
            # ROTAS GET (Consultas e Listagens)
            # ------------------------------------------------------------------
            if metodo_http == "GET":
                if caminho == "/api/status":
                    return self.responder_json(200, {"api": "ok", "banco": "ok"})

                if caminho == "/api/livros":
                    termo_busca = pegar_parametro("busca") or None
                    return self.responder_json(200, bib.listar_livros(termo_busca))

                if caminho == "/api/livros/por-autor":
                    autor = pegar_parametro("autor")
                    return self.responder_json(200, bib.consultar_total_por_autor(autor))

                if caminho == "/api/livros/por-faixa":
                    minimo = int(pegar_parametro("minimo"))
                    maximo = int(pegar_parametro("maximo"))
                    livros = bib.buscar_livros_por_faixa_exemplares(minimo, maximo)
                    return self.responder_json(200, {"registros": livros})

                if caminho.startswith("/api/consultas/joins/"):
                    tipo_join = caminho.replace("/api/consultas/joins/", "").strip("/")
                    return self.responder_json(200, {"registros": bib.executar_join(tipo_join)})

                if caminho == "/api/relatorios/estatisticas-por-genero":
                    media_minima = float(pegar_parametro("media_minima"))
                    relatorio = bib.relatorio_estatisticas_genero(media_minima)
                    return self.responder_json(200, {"registros": relatorio})

                if caminho == "/api/relatorios/autores-multigenero":
                    genero1 = pegar_parametro("genero1")
                    genero2 = pegar_parametro("genero2")
                    autores = bib.relatorio_autores_multigenero(genero1, genero2)
                    return self.responder_json(200, {"registros": autores})

                if caminho == "/api/catalogo/busca":
                    termo = pegar_parametro("termo")
                    resultado = bib.buscar_catalogo_palavra_chave(termo)
                    return self.responder_json(200, {"registros": resultado})

                if caminho == "/api/auditoria/estantes-vazias":
                    return self.responder_json(200, {"registros": bib.auditoria_estantes_vazias()})

                if caminho == "/api/analises/acervo-critico":
                    genero_alvo = pegar_parametro("genero_alvo")
                    genero_comp = pegar_parametro("genero_comparacao")
                    resultado = bib.analise_acervo_critico(genero_alvo, genero_comp)
                    return self.responder_json(200, {"registros": resultado})

                if caminho == "/api/autores/unicos":
                    return self.responder_json(200, {"registros": bib.listar_autores_unicos()})

                if caminho == "/api/estantes":
                    return self.responder_json(200, bib.listar_estantes())

            # ------------------------------------------------------------------
            # ROTAS POST (Cadastro de Livros e Estantes)
            # ------------------------------------------------------------------
            elif metodo_http == "POST":
                dados = self.ler_json_recebido()

                if caminho == "/api/livros":
                    nome, autor, genero, ex, emp, est, pat, status = self.validar_dados_do_livro(dados, True)
                    id_novo = bib.cadastrar_livro(nome, autor, genero, ex, emp, est, pat, status)
                    return self.responder_json(201, {"mensagem": "Livro cadastrado.", "id_livro": id_novo})

                if caminho == "/api/livros/procedure":
                    nome, autor, genero, ex, emp, est, _, _ = self.validar_dados_do_livro(dados, True)
                    bib.cadastrar_livro_via_procedure(nome, autor, genero, ex, emp, est)
                    return self.responder_json(201, {"mensagem": "Livro cadastrado via PROCEDURE."})

                if caminho == "/api/estantes":
                    dom1 = str(dados.get("dominio_lado_1") or "").strip()
                    dom2 = str(dados.get("dominio_lado_2") or "Geral").strip() or "Geral"
                    if not dom1:
                        raise ValueError("Informe o tema/domínio principal da estante (Domínio Lado 1).")
                    try:
                        capacidade = int(dados.get("numero_de_livros") or 100)
                    except (TypeError, ValueError):
                        raise ValueError("A capacidade de livros deve ser um número inteiro válido.")
                    if capacidade < 0:
                        raise ValueError("A capacidade de livros não pode ser negativa.")
                    id_estante = bib.cadastrar_estante(dom1, dom2, capacidade)
                    return self.responder_json(201, {"mensagem": "Estante criada com sucesso.", "id_estante": id_estante})

            # ------------------------------------------------------------------
            # ROTAS PUT (Atualização de Livro existente)
            # ------------------------------------------------------------------
            elif metodo_http == "PUT" and caminho.startswith("/api/livros/"):
                id_livro = int(caminho.replace("/api/livros/", "").strip("/"))
                dados = self.ler_json_recebido()
                nome, autor, genero, ex, emp, _, _, _ = self.validar_dados_do_livro(dados, False)

                if not bib.atualizar_livro(id_livro, nome, autor, genero, ex, emp):
                    return self.responder_json(404, {"erro": "Livro não encontrado."})
                return self.responder_json(200, {"mensagem": "Livro atualizado."})

            # ------------------------------------------------------------------
            # ROTAS DELETE (Exclusão de Livro, Estante ou Editora)
            # ------------------------------------------------------------------
            elif metodo_http == "DELETE" and caminho.startswith("/api/livros/"):
                id_livro = int(caminho.replace("/api/livros/", "").strip("/"))
                if not bib.excluir_livro(id_livro):
                    return self.responder_json(404, {"erro": "Livro não encontrado."})
                return self.responder_json(200, {"mensagem": "Livro excluído."})

            elif metodo_http == "DELETE" and caminho.startswith("/api/estantes/"):
                id_estante = int(caminho.replace("/api/estantes/", "").strip("/"))
                resultado = bib.excluir_estante(id_estante)
                if not resultado["excluiu"]:
                    return self.responder_json(404, {"erro": "Estante não encontrada."})
                return self.responder_json(
                    200,
                    {
                        "mensagem": "Estante excluída com sucesso.",
                        "livros_removidos": resultado["livros_removidos"],
                    },
                )

            elif metodo_http == "DELETE" and caminho.startswith("/api/editoras/"):
                id_editora = int(caminho.replace("/api/editoras/", "").strip("/"))
                if not bib.excluir_editora(id_editora):
                    return self.responder_json(404, {"erro": "Editora não encontrada."})
                return self.responder_json(200, {"mensagem": "Editora excluída."})

            # Se nenhuma rota acima combinou, devolve erro 404 (Não encontrado)
            self.responder_json(404, {"erro": "Rota não encontrada."})

        except (ValueError, KeyError, TypeError) as erro_validacao:
            self.responder_json(400, {"erro": str(erro_validacao)})

        except pyodbc.IntegrityError as erro_integridade:
            # Traduz os códigos de erro do PostgreSQL para mensagens fáceis de entender
            texto_erro = str(erro_integridade).lower()
            if "23505" in texto_erro or "unicidade" in texto_erro or "unique" in texto_erro:
                mensagem = "Violação de unicidade (UNIQUE): o código/valor informado já está em uso."
            elif "23503" in texto_erro or "chave estrangeira" in texto_erro or "foreign key" in texto_erro:
                mensagem = "Violação de integridade referencial (FK / RESTRICT): registro protegido ou pai inexistente."
            elif "23514" in texto_erro or "checagem" in texto_erro or "check" in texto_erro:
                mensagem = "Violação de regra de domínio (CHECK): valor fora dos permitidos."
            elif "23502" in texto_erro or "not-null" in texto_erro or "não-nulo" in texto_erro:
                mensagem = "Campo obrigatório (NOT NULL) não informado."
            else:
                mensagem = "Violação de integridade no banco de dados."
            self.responder_json(409, {"erro": mensagem})

        except pyodbc.Error as erro_banco:
            self.responder_json(503, {"erro": "Erro ao acessar o banco de dados.", "detalhe": str(erro_banco)})

    def eh_rota_da_api(self):
        """Verifica se o endereço pedido pelo navegador começa com '/api'."""
        caminho = urlparse(self.path).path
        return caminho == "/api" or caminho.startswith("/api/")

    def do_GET(self):
        # Se for '/api/...', busca no banco de dados. Senão, entrega os arquivos HTML/CSS/JS.
        if self.eh_rota_da_api():
            self.processar_rota_api("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.eh_rota_da_api():
            self.processar_rota_api("POST")
        else:
            self.responder_json(404, {"erro": "Não encontrado."})

    def do_PUT(self):
        if self.eh_rota_da_api():
            self.processar_rota_api("PUT")
        else:
            self.responder_json(404, {"erro": "Não encontrado."})

    def do_DELETE(self):
        if self.eh_rota_da_api():
            self.processar_rota_api("DELETE")
        else:
            self.responder_json(404, {"erro": "Não encontrado."})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()


def iniciar_servidor_web(porta=8000):
    """Liga o servidor HTTP local na porta 8000."""
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), ServidorBiblioteca)
    print(f"Biblioteca rodando em http://127.0.0.1:{porta}  (API em /api)")
    print("Pressione Ctrl+C para encerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()


if __name__ == "__main__":
    # Se o usuário digitou `python app.py --web`, inicia a Interface Web.
    # Caso contrário (`python app.py`), inicia o Menu no Terminal.
    if "--web" in sys.argv:
        argumentos = [arg for arg in sys.argv[1:] if arg != "--web"]
        porta_escolhida = int(argumentos[0]) if argumentos and argumentos[0].isdigit() else 8000
        iniciar_servidor_web(porta_escolhida)
    else:
        menu_console()
