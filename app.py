"""
Ponto de entrada único — Sistema da Biblioteca.

Uso:
    python app.py              -> Menu interativo no terminal (organizado pelas 5 seções)
    python app.py --web        -> Interface Web + API HTTP nativa em http://127.0.0.1:8000
    python app.py --web 8080   -> Interface Web em porta personalizada
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

PASTA_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Interface-biblioteca")
PREFIXO = "/api"


# ==============================================================================
# 1. MENU INTERATIVO NO TERMINAL (Avaliação Oral)
# ==============================================================================

def _mostrar(registros, titulo):
    print(f"\n=== {titulo} ===")
    if not registros:
        print("Nenhum registro retornado.")
        return
    colunas = list(registros[0].keys())
    print(" | ".join(colunas))
    print("-" * 75)
    for row in registros:
        print(" | ".join("NULL" if row.get(c) is None else str(row.get(c)) for c in colunas))
    print(f"({len(registros)} registro(s))")


def _menu_secao_1():
    while True:
        print("\n--- [Seção 1] CRUD Básico e Integridade (Cap. 1 a 4) ---")
        print("1. Listar livros (SELECT)")
        print("2. Cadastrar livro (INSERT + Prepared Statement)")
        print("3. Atualizar livro (UPDATE)")
        print("4. Excluir livro (DELETE + Trigger Auditoria)")
        print("5. Validar todas as restrições DDL (PK, FK, CASCADE, SET NULL/DEFAULT, UNIQUE, CHECK, ALTER)")
        print("0. Voltar")
        op = input("Opção: ").strip()
        try:
            if op == "0":
                break
            elif op == "1":
                _mostrar(bib.listar_livros(), "Livros Cadastrados")
            elif op == "2":
                nome = input("Título: ").strip()
                autor = input("Autor: ").strip()
                genero = input("Gênero: ").strip() or "Geral"
                ex = int(input("Exemplares: ").strip() or "1")
                est = int(input("ID Estante: ").strip() or "1")
                pat = input("Código Patrimônio (opcional, UNIQUE): ").strip() or None
                bib.cadastrar_livro(nome, autor, genero, ex, True, est, pat)
                print("Livro cadastrado com sucesso!")
            elif op == "3":
                id_l = int(input("ID do livro: ").strip())
                nome = input("Novo título: ").strip()
                autor = input("Novo autor: ").strip()
                genero = input("Novo gênero: ").strip()
                ex = int(input("Novos exemplares: ").strip())
                ok = bib.atualizar_livro(id_l, nome, autor, genero, ex, True)
                print("Atualizado!" if ok else "Livro não encontrado.")
            elif op == "4":
                id_l = int(input("ID do livro para excluir: ").strip())
                ok = bib.excluir_livro(id_l)
                print("Excluído!" if ok else "Livro não encontrado.")
            elif op == "5":
                for item in bib.testar_parte1_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
        except (ValueError, pyodbc.Error) as e:
            print(f"[ERRO] {e}")


def _menu_secao_2():
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
        op = input("Opção: ").strip()
        try:
            if op == "0":
                break
            elif op == "1":
                r = bib.projecao_distinct_all_e_calculo()
                _mostrar(r["distinct"], "DISTINCT status_conservacao")
                _mostrar(r["calculados"], "Projeção com Atributo Calculado")
            elif op == "2":
                r = bib.selecao_predicados_compostos_e_tupla()
                _mostrar(r["predicados_compostos"], "Seleção com Predicados Compostos")
                _mostrar(r["comparacao_tupla"], "Predicado com Tupla")
            elif op == "3":
                r = bib.produto_cartesiano_e_juncao_teta()
                print(f"\nProduto Cartesiano: {r['qtd_livros']} x {r['qtd_espacos']} = {r['total_cartesiano']} linhas")
                _mostrar(r["juncao_teta"], "Junção Teta (WHERE l.id_categoria = c.id_categoria)")
            elif op == "4":
                gen = input("Gênero (ex: Romance Clássico): ").strip() or "Romance Clássico"
                _mostrar(bib.auto_juncao_livros_mesmo_autor_genero(gen), f"SELF JOIN ({gen})")
            elif op == "5":
                r = bib.buscar_strings_like_coringa_posicao()
                _mostrar(r["like_percent"], "LIKE com % + UPPER/LOWER/||")
                _mostrar(r["like_underline"], "LIKE com _ (PAT-____)")
            elif op == "6":
                mi = int(input("Mínimo: ").strip() or "10")
                ma = int(input("Máximo: ").strip() or "20")
                negar = input("Usar NOT BETWEEN? (s/N): ").strip().lower() == "s"
                _mostrar(bib.buscar_livros_por_faixa_exemplares(mi, ma, negar), f"Faixa {mi}..{ma}")
            elif op == "7":
                r = bib.consultar_nulos_e_nao_nulos()
                _mostrar(r["com_nulo"], "IS NULL (sem patrimônio)")
                _mostrar(bib.ordenar_livros_multiatributo_nulos(True), "ORDER BY ... NULLS FIRST")
            elif op == "8":
                for item in bib.testar_parte2_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
        except (ValueError, pyodbc.Error) as e:
            print(f"[ERRO] {e}")


def _menu_secao_3():
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
        op = input("Opção: ").strip()
        try:
            if op == "0":
                break
            elif op == "1":
                _mostrar(bib.livros_acima_da_media_escalar(), "Subconsulta Escalar")
            elif op == "2":
                tipo = input("Tipo de espaço (ex: Acervo Geral de Livros): ").strip() or "Acervo Geral de Livros"
                negar = input("Usar NOT IN? (s/N): ").strip().lower() == "s"
                _mostrar(bib.livros_por_tipo_espaco_in(tipo, negar), "Subconsulta IN/NOT IN")
            elif op == "3":
                negar = input("Usar NOT EXISTS? (s/N): ").strip().lower() == "s"
                _mostrar(bib.espacos_com_estantes_exists(negar), "EXISTS / NOT EXISTS")
            elif op == "4":
                dom = input("Domínio das estantes (ex: Ficção Científica): ").strip() or "Ficção Científica"
                gen = input("Gênero de comparação (ex: Romance Clássico): ").strip() or "Romance Clássico"
                _mostrar(bib.analise_acervo_critico(dom, gen), "CTE + SOME")
            elif op == "5":
                r = bib.comparar_union_vs_union_all()
                print(f"\nUNION: {len(r['union'])} | UNION ALL: {len(r['union_all'])}")
                _mostrar(r["union"], "UNION Temas")
            elif op == "6":
                r = bib.comparar_intersect_vs_intersect_all()
                print(f"\nINTERSECT: {len(r['intersect'])} | INTERSECT ALL: {len(r['intersect_all'])}")
                _mostrar(r["intersect"], "INTERSECT Categorias")
            elif op == "7":
                r = bib.comparar_except_vs_except_all()
                print(f"\nEXCEPT: {len(r['except'])} | EXCEPT ALL: {len(r['except_all'])}")
                _mostrar(r["except"], "EXCEPT Categorias")
            elif op == "8":
                for item in bib.testar_parte3_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
        except (ValueError, pyodbc.Error) as e:
            print(f"[ERRO] {e}")


def _menu_secao_4():
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
        op = input("Opção: ").strip()
        try:
            if op == "0":
                break
            elif op == "1":
                media = float(input("Média mínima de exemplares: ").strip() or "1")
                _mostrar(bib.relatorio_estatisticas_genero(media), "GROUP BY + HAVING")
            elif op == "2":
                cod = input("Tipo (natural | inner | left | right | full): ").strip().lower() or "full"
                _mostrar(bib.executar_join(cod), f"JOIN: {cod.upper()}")
            elif op == "3":
                _mostrar(bib.consultar_visao_localizacao_completa(), "VIEW Localização Completa")
            elif op == "4":
                if input("Executar REFRESH antes? (S/n): ").strip().lower() != "n":
                    bib.atualizar_visao_materializada()
                    print("REFRESH MATERIALIZED VIEW concluído!")
                _mostrar(bib.consultar_visao_materializada(), "MATERIALIZED VIEW Ranking Autores")
            elif op == "5":
                autor = input("Autor: ").strip()
                res = bib.consultar_total_por_autor(autor)
                print(f"Total retornado pela FUNCTION: {res['total']}")
                _mostrar(res["livros"], f"Livros de {autor}")
            elif op == "6":
                nome = input("Título: ").strip()
                autor = input("Autor: ").strip()
                genero = input("Gênero: ").strip() or "Geral"
                bib.cadastrar_livro_via_procedure(nome, autor, genero, 1, True, 1)
                print("Cadastrado via PROCEDURE!")
            elif op == "7":
                _mostrar(bib.consultar_auditoria_trigger(), "Auditoria do Trigger AFTER DELETE")
            elif op == "8":
                _mostrar(bib.consulta_recursiva_pisos(), "WITH RECURSIVE Pisos")
            elif op == "9":
                for item in bib.testar_parte4_completa():
                    print(f"[{item['status']}] {item['item']} -> {item['detalhes']}")
        except (ValueError, pyodbc.Error) as e:
            print(f"[ERRO] {e}")


def _menu_secao_5():
    while True:
        print("\n--- [Seção 5] Metadados via ODBC (Cap. 5) ---")
        print("1. Listar tabelas e views do schema (cursor.tables)")
        print("2. Listar colunas de uma tabela (cursor.columns)")
        print("0. Voltar")
        op = input("Opção: ").strip()
        try:
            if op == "0":
                break
            elif op == "1":
                _mostrar(bib.inspecionar_tabelas_schema(), "Metadados: Tabelas")
            elif op == "2":
                tab = input("Nome da tabela (ex: livros): ").strip() or "livros"
                _mostrar(bib.inspecionar_colunas_tabela(tab), f"Metadados: Colunas de {tab}")
        except pyodbc.Error as e:
            print(f"[ERRO] {e}")


def menu_console():
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
        op = input("\nEscolha uma seção: ").strip()
        if op == "1":
            _menu_secao_1()
        elif op == "2":
            _menu_secao_2()
        elif op == "3":
            _menu_secao_3()
        elif op == "4":
            _menu_secao_4()
        elif op == "5":
            _menu_secao_5()
        elif op == "0":
            print("Encerrado.")
            break
        else:
            print("Opção inválida.")


# ==============================================================================
# 2. MODO WEB (--web): Servidor HTTP Nativo integrado a biblioteca.py
# ==============================================================================

def _para_json(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (date, datetime)):
        return v.isoformat()
    return str(v)


def _bool(v):
    return v if isinstance(v, bool) else str(v).strip().lower() in ("true", "1", "sim", "s")


class _ServidorWeb(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PASTA_WEB, **kwargs)

    def _json(self, status, dados):
        corpo = json.dumps(dados, ensure_ascii=False, default=_para_json).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def _corpo(self):
        tam = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(tam).decode("utf-8")) if tam else {}

    def _api(self, metodo):
        url = urlparse(self.path)
        p = [unquote(x) for x in url.path[len(PREFIXO):].split("/") if x]
        q = lambda k: (parse_qs(url.query).get(k) or [""])[0].strip()
        try:
            if metodo == "GET":
                if p == ["status"]:
                    return self._json(200, {"api": "ok", "banco": "ok"})
                if p == ["livros"]:
                    return self._json(200, bib.listar_livros())
                if p == ["livros", "por-autor"]:
                    return self._json(200, bib.consultar_total_por_autor(q("autor")))
                if p == ["livros", "por-faixa"]:
                    return self._json(200, {"registros": bib.buscar_livros_por_faixa_exemplares(int(q("minimo")), int(q("maximo")))})
                if len(p) == 3 and p[:2] == ["consultas", "joins"]:
                    return self._json(200, {"registros": bib.executar_join(p[2])})
                if p == ["relatorios", "estatisticas-por-genero"]:
                    return self._json(200, {"registros": bib.relatorio_estatisticas_genero(float(q("media_minima")))})
                if p == ["relatorios", "autores-multigenero"]:
                    return self._json(200, {"registros": bib.relatorio_autores_multigenero(q("genero1"), q("genero2"))})
                if p == ["catalogo", "busca"]:
                    return self._json(200, {"registros": bib.buscar_catalogo_palavra_chave(q("termo"))})
                if p == ["auditoria", "estantes-vazias"]:
                    return self._json(200, {"registros": bib.auditoria_estantes_vazias()})
                if p == ["analises", "acervo-critico"]:
                    return self._json(200, {"registros": bib.analise_acervo_critico(q("genero_alvo"), q("genero_comparacao"))})
                if p == ["autores", "unicos"]:
                    return self._json(200, {"registros": bib.listar_autores_unicos()})
            elif metodo == "POST":
                c = self._corpo()
                if p == ["livros"]:
                    bib.cadastrar_livro(c["nome"], c["autor"], c["genero"], c["numero_de_exemplares"], _bool(c.get("pode_ser_emprestado", True)), c["id_estante"])
                    return self._json(201, {"mensagem": "Livro cadastrado."})
                if p == ["livros", "procedure"]:
                    bib.cadastrar_livro_via_procedure(c["nome"], c["autor"], c["genero"], c["numero_de_exemplares"], _bool(c.get("pode_ser_emprestado", True)), c["id_estante"])
                    return self._json(201, {"mensagem": "Livro cadastrado via PROCEDURE."})
            elif metodo == "PUT" and len(p) == 2 and p[0] == "livros":
                c = self._corpo()
                if not bib.atualizar_livro(int(p[1]), c["nome"], c["autor"], c["genero"], c["numero_de_exemplares"], _bool(c.get("pode_ser_emprestado", True))):
                    return self._json(404, {"erro": "Livro não encontrado."})
                return self._json(200, {"mensagem": "Livro atualizado."})
            elif metodo == "DELETE" and len(p) == 2 and p[0] == "livros":
                if not bib.excluir_livro(int(p[1])):
                    return self._json(404, {"erro": "Livro não encontrado."})
                return self._json(200, {"mensagem": "Livro excluído."})
            self._json(404, {"erro": "Rota não encontrada."})
        except (ValueError, KeyError) as e:
            self._json(400, {"erro": str(e)})
        except pyodbc.IntegrityError as e:
            self._json(409, {"erro": "Violação de integridade.", "detalhe": str(e)})
        except pyodbc.Error as e:
            self._json(503, {"erro": "Erro no banco de dados.", "detalhe": str(e)})

    def _eh_api(self):
        c = urlparse(self.path).path
        return c == PREFIXO or c.startswith(PREFIXO + "/")

    def do_GET(self):
        self._api("GET") if self._eh_api() else super().do_GET()

    def do_POST(self):
        self._api("POST") if self._eh_api() else self._json(404, {"erro": "Não encontrado."})

    def do_PUT(self):
        self._api("PUT") if self._eh_api() else self._json(404, {"erro": "Não encontrado."})

    def do_DELETE(self):
        self._api("DELETE") if self._eh_api() else self._json(404, {"erro": "Não encontrado."})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()


def iniciar_web(porta=8000):
    srv = ThreadingHTTPServer(("127.0.0.1", porta), _ServidorWeb)
    print(f"Biblioteca rodando em http://127.0.0.1:{porta}  (API em {PREFIXO})")
    print("Ctrl+C para encerrar.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()


if __name__ == "__main__":
    if "--web" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--web"]
        iniciar_web(int(args[0]) if args and args[0].isdigit() else 8000)
    else:
        menu_console()
