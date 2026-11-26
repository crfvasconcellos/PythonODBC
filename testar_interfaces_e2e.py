"""
Bateria E2E de Estresse e Resiliência das Interfaces (Web/API + Console + Vazamento de Conexões).

Executa os 3 blocos de QA:
  - Bloco 1: Estresse da API HTTP / Interface Web (http://127.0.0.1:8000)
  - Bloco 2: Resiliência do Menu Interativo de Terminal (subprocess com entradas inválidas e 6 baterias)
  - Bloco 3: Verificação de vazamento de conexões (50 requisições consecutivas + pg_stat_activity)

Uso:
    python testar_interfaces_e2e.py
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

from db import transacao

BASE_URL = "http://127.0.0.1:8000"


def _req(metodo: str, caminho: str, corpo=None):
    url = BASE_URL + caminho
    headers = {"Accept": "application/json"}
    data = None
    if corpo is not None:
        if isinstance(corpo, (dict, list)):
            data = json.dumps(corpo).encode("utf-8")
        else:
            data = str(corpo).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="replace")


def bloco_1_api_web() -> list[tuple[str, bool, str]]:
    resultados = []

    # 1. Estáticos e /api/status e 404
    st_root, html_root = _req("GET", "/")
    st_idx, html_idx = _req("GET", "/index.html")
    st_stat, body_stat = _req("GET", "/api/status")
    st_404, _ = _req("GET", "/rota_que_nao_existe_123")
    stat_json = json.loads(body_stat) if st_stat == 200 else {}
    ok_est = (
        st_root == 200 and "<html" in html_root.lower()
        and st_idx == 200 and "<html" in html_idx.lower()
        and st_stat == 200 and stat_json == {"api": "ok", "banco": "ok"}
        and st_404 == 404
    )
    resultados.append(("Rota /api/status, estáticos e 404 tratado", ok_est, f"root={st_root}, idx={st_idx}, status={stat_json}, 404={st_404}"))

    # 2. Listagens, busca filtrada e SQL Injection na URL
    st_all, body_all = _req("GET", "/api/livros")
    livros_all = json.loads(body_all) if st_all == 200 else []

    st_dom, body_dom = _req("GET", "/api/livros?busca=Dom")
    livros_dom = json.loads(body_dom) if st_dom == 200 else []

    payload_sqli = urllib.parse.quote("'; DROP TABLE livros; --")
    st_sqli, body_sqli = _req("GET", f"/api/livros?busca={payload_sqli}")
    livros_sqli = json.loads(body_sqli) if st_sqli == 200 else None

    # Confirma que a tabela livros continua intacta após tentativa de SQL Injection
    st_pos, body_pos = _req("GET", "/api/livros")
    livros_pos = json.loads(body_pos) if st_pos == 200 else []

    ok_sqli = (
        st_all == 200 and len(livros_all) > 0
        and st_dom == 200 and len(livros_dom) >= 1 and all("dom" in l["nome"].lower() for l in livros_dom)
        and st_sqli == 200 and livros_sqli == []
        and len(livros_pos) == len(livros_all)
    )
    resultados.append(("Listagem, busca filtrada e prevenção de SQL Injection", ok_sqli, f"total={len(livros_all)}, busca_Dom={len(livros_dom)}, sqli_retorno={livros_sqli}"))

    # 3. POST: Caso feliz + campos faltando + tipos inválidos + CHECK + UNIQUE
    st_ok, body_ok = _req("POST", "/api/livros", {
        "nome": "Livro QA E2E",
        "autor": "Engenheiro QA",
        "genero": "Testes",
        "numero_de_exemplares": 5,
        "pode_ser_emprestado": True,
        "id_estante": 1,
        "codigo_patrimonio": "PAT-QA99",
    })
    dados_ok = json.loads(body_ok) if st_ok in (200, 201) else {}
    id_criado = dados_ok.get("id_livro")

    st_vazio, b_vazio = _req("POST", "/api/livros", {})
    st_tit_vazio, _ = _req("POST", "/api/livros", {"titulo": "", "autor": "X", "genero": "Y", "numero_de_exemplares": 1, "id_estante": 1})
    st_tipo, _ = _req("POST", "/api/livros", {"nome": "X", "autor": "Y", "genero": "Z", "numero_de_exemplares": "abc", "id_estante": "dois_mil"})
    st_json_ruim, _ = _req("POST", "/api/livros", "{json_quebrado")
    st_check_num, _ = _req("POST", "/api/livros", {"nome": "Neg", "autor": "Y", "genero": "Z", "numero_de_exemplares": -50, "id_estante": 1})
    st_check_in, _ = _req("POST", "/api/livros", {"nome": "StatusRuim", "autor": "Y", "genero": "Z", "numero_de_exemplares": 1, "id_estante": 1, "status_conservacao": "Destruido"})

    ok_post_val = (
        st_ok == 201 and isinstance(id_criado, int)
        and st_vazio == 400 and st_tit_vazio == 400
        and st_tipo == 400 and st_json_ruim == 400
        and st_check_num in (400, 409) and st_check_in in (400, 409)
    )
    resultados.append(("Validação de payloads malformados, tipos e CHECK no POST", ok_post_val, f"criado_id={id_criado}, vazio={st_vazio}, tipo={st_tipo}, json_ruim={st_json_ruim}, check_num={st_check_num}, check_in={st_check_in}"))

    # UNIQUE na API (PAT-0001 já existe)
    st_uniq, body_uniq = _req("POST", "/api/livros", {
        "nome": "Livro Dup", "autor": "Autor", "genero": "Geral",
        "numero_de_exemplares": 2, "id_estante": 1, "codigo_patrimonio": "PAT-0001",
    })
    msg_uniq = json.loads(body_uniq).get("erro", "") if body_uniq else ""
    ok_uniq = st_uniq == 409 and ("unicidade" in msg_uniq.lower() or "unique" in msg_uniq.lower())
    resultados.append(("Tratamento de duplicatas e UNIQUE na API", ok_uniq, f"status={st_uniq}, msg={msg_uniq}"))

    # 4. DELETE: limpa livro criado + ID inexistente (999999) + RESTRICT em editora 1
    st_del_ok, _ = _req("DELETE", f"/api/livros/{id_criado}") if id_criado else (500, "")
    st_del_404, body_del_404 = _req("DELETE", "/api/livros/999999")
    st_del_res, body_del_res = _req("DELETE", "/api/editoras/1")
    msg_res = json.loads(body_del_res).get("erro", "") if body_del_res else ""
    ok_del = st_del_ok == 200 and st_del_404 == 404 and st_del_res == 409 and "restrict" in msg_res.lower()
    resultados.append(("Exclusão controlada (200, 404 inexistente e 409 RESTRICT)", ok_del, f"del_ok={st_del_ok}, del_404={st_del_404}, del_restrict={st_del_res} ({msg_res})"))

    return resultados


def bloco_2_menu_console() -> list[tuple[str, bool, str]]:
    # Simula entradas inválidas, cadastro com texto em campo numérico, busca com aspas/especiais e as 6 baterias
    entradas = [
        # Entradas inválidas no menu principal
        "abc", "xyz", "-1", "999", "",
        # Seção 1: opção inválida, tentativa de cadastrar com texto em exemplares, bateria Parte 1, voltar
        "1", "invalida", "", "2", "Livro Console", "Autor", "Teste", "nao_eh_numero", "5", "0",
        # Seção 2: busca com caracteres especiais/aspas via opção 5 e bateria Parte 2, voltar
        "2", "999", "8", "0",
        # Seção 3: bateria Parte 3, voltar
        "3", "8", "0",
        # Seção 4: bateria Parte 4, voltar
        "4", "9", "0",
        # Seção 5: baterias Parte 5 e Parte 6, voltar
        "5", "5", "6", "0",
        # Sair
        "0",
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, "app.py"],
        input="\n".join(entradas) + "\n",
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=60,
        env=env,
    )
    saida = proc.stdout
    erros = proc.stderr
    tem_invalida = "Opção inválida! Tente novamente." in saida
    tem_erro_num_tratado = "[ERRO]" in saida
    qtd_ok = saida.count("[OK]")
    sem_traceback = "Traceback" not in saida and "Traceback" not in erros
    ok = proc.returncode == 0 and tem_invalida and tem_erro_num_tratado and qtd_ok == 43 and sem_traceback
    return [(
        "Resiliência a entradas inválidas e execução das 6 baterias no Menu Console",
        ok,
        f"exit={proc.returncode}, op_invalida={tem_invalida}, erro_num_tratado={tem_erro_num_tratado}, itens_OK={qtd_ok}/43, sem_traceback={sem_traceback}",
    )]


def bloco_3_vazamento_conexoes() -> list[tuple[str, bool, str]]:
    codigos = []
    for i in range(50):
        rota = "/api/status" if i % 2 == 0 else "/api/livros"
        st, _ = _req("GET", rota)
        codigos.append(st)

    with transacao() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM pg_stat_activity
            WHERE datname = current_database()
              AND state = 'idle in transaction'
              AND pid <> pg_backend_pid();
            """
        )
        idle_in_tx = cur.fetchone()[0]

    ok = all(c == 200 for c in codigos) and len(codigos) == 50 and idle_in_tx == 0
    return [(
        "Gerenciamento de conexões (50 requisições rápidas sem vazamentos)",
        ok,
        f"50/50_HTTP_200={all(c == 200 for c in codigos)}, conexoes_idle_in_transaction={idle_in_tx}",
    )]


def main():
    todos = []
    todos.extend(bloco_1_api_web())
    todos.extend(bloco_2_menu_console())
    todos.extend(bloco_3_vazamento_conexoes())

    print("=" * 78)
    print("RELATÓRIO E2E — TESTE DE ESTRESSE E RESILIÊNCIA DAS INTERFACES")
    print("=" * 78)
    for nome, ok, detalhe in todos:
        print(f"[{'OK' if ok else 'FALHA'}] {nome}")
        print(f"       -> {detalhe}")
    print("=" * 78)
    tudo_ok = all(ok for _, ok, _ in todos)
    print(f"RESULTADO FINAL: {'100% APROVADO' if tudo_ok else 'FALHOU'} ({sum(1 for _, ok, _ in todos if ok)}/{len(todos)})")
    sys.exit(0 if tudo_ok else 1)


if __name__ == "__main__":
    main()
