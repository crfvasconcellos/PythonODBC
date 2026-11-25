"""
API HTTP da Biblioteca - sem frameworks (apenas biblioteca padrão + pyodbc).

Liga o front-end (Interface-biblioteca/) ao PostgreSQL via ODBC.
O mesmo servidor entrega os arquivos estáticos e as rotas /api/...,
então não há problemas de CORS.

Uso:
    python api.py            -> http://127.0.0.1:8000
    python api.py 8080       -> porta personalizada
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import pyodbc
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(filename=".env", usecwd=True))

PASTA_FRONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Interface-biblioteca")
PREFIXO = "/api"


# ==========================================================================
# Banco de dados
# ==========================================================================
def conectar_bd():
    driver = os.getenv("DB_DRIVER", "PostgreSQL Unicode(x64)")
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_DATABASE", "biblioteca")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server};PORT={port};"
        f"DATABASE={database};UID={user};PWD={password};"
    )
    conn = pyodbc.connect(conn_str, timeout=10)
    conn.autocommit = False
    return conn


def consultar(sql, params=()):
    """SELECT -> lista de dicionários."""
    conn = conectar_bd()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        colunas = [c[0] for c in cur.description]
        linhas = [dict(zip(colunas, linha)) for linha in cur.fetchall()]
        # O driver ODBC do PostgreSQL pode devolver BOOLEAN como '1'/'0'.
        for linha in linhas:
            if "pode_ser_emprestado" in linha and linha["pode_ser_emprestado"] is not None:
                linha["pode_ser_emprestado"] = booleano(linha["pode_ser_emprestado"])
        return linhas
    finally:
        conn.close()


def executar(sql, params=()):
    """INSERT/UPDATE/DELETE/CALL com commit -> linhas afetadas."""
    conn = conectar_bd()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        afetadas = cur.rowcount
        conn.commit()
        return afetadas
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def para_json(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return str(valor)


# ==========================================================================
# Erros de validação
# ==========================================================================
class ErroHTTP(Exception):
    def __init__(self, status, mensagem):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


def texto(dados, campo, obrigatorio=True, maximo=255):
    valor = str(dados.get(campo) or "").strip()
    if obrigatorio and not valor:
        raise ErroHTTP(400, f"Campo '{campo}' é obrigatório.")
    if len(valor) > maximo:
        raise ErroHTTP(400, f"Campo '{campo}' excede {maximo} caracteres.")
    return valor


def inteiro(valor, campo, minimo=None):
    try:
        if isinstance(valor, bool):
            raise ValueError
        n = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ErroHTTP(400, f"Campo '{campo}' deve ser um número inteiro.")
    if minimo is not None and n < minimo:
        raise ErroHTTP(400, f"Campo '{campo}' deve ser >= {minimo}.")
    return n


def numero(valor, campo):
    try:
        return float(str(valor).strip())
    except (TypeError, ValueError):
        raise ErroHTTP(400, f"Campo '{campo}' deve ser numérico.")


def booleano(valor):
    if isinstance(valor, bool):
        return valor
    return str(valor).strip().lower() in ("true", "1", "sim", "s")


def dados_livro(corpo, com_estante):
    livro = {
        "nome": texto(corpo, "nome"),
        "autor": texto(corpo, "autor"),
        "genero": texto(corpo, "genero", maximo=100),
        "numero_de_exemplares": inteiro(corpo.get("numero_de_exemplares"), "numero_de_exemplares", 0),
        "pode_ser_emprestado": booleano(corpo.get("pode_ser_emprestado", True)),
    }
    if com_estante:
        livro["id_estante"] = inteiro(corpo.get("id_estante"), "id_estante", 1)
    return livro


def param(qs, nome, obrigatorio=True):
    valor = (qs.get(nome) or [""])[0].strip()
    if obrigatorio and not valor:
        raise ErroHTTP(400, f"Parâmetro '{nome}' é obrigatório.")
    return valor


# ==========================================================================
# Rotas
# ==========================================================================
SQL_JOINS = {
    "natural": """
        SELECT nome, tipo FROM biblioteca.livros
        NATURAL JOIN biblioteca.estantes ORDER BY nome""",
    "inner": """
        SELECT e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo,
               esp.id_espaco, esp.numero_de_espacos
        FROM biblioteca.estantes e
        INNER JOIN biblioteca.espacos esp ON e.id_espaco = esp.id_espaco
        ORDER BY esp.id_espaco, e.id_estante""",
    "left": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        LEFT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco""",
    "right": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        RIGHT OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY e.id_estante""",
    "full": """
        SELECT esp.id_espaco, esp.numero_de_espacos,
               e.id_estante, e.dominio_lado_1, e.dominio_lado_2, e.tipo
        FROM biblioteca.espacos esp
        FULL OUTER JOIN biblioteca.estantes e ON esp.id_espaco = e.id_espaco
        ORDER BY esp.id_espaco, e.id_estante""",
}


def rota_get(partes, qs):
    # GET /livros
    if partes == ["livros"]:
        return 200, consultar("""
            SELECT id_livro, nome, autor, genero, numero_de_exemplares,
                   pode_ser_emprestado, id_estante
            FROM biblioteca.livros ORDER BY id_livro""")

    # GET /livros/por-autor?autor=
    if partes == ["livros", "por-autor"]:
        autor = param(qs, "autor")
        total = consultar("SELECT fn_contar_livros_por_autor(CAST(? AS VARCHAR)) AS total", (autor,))[0]["total"]
        livros = consultar("""
            SELECT id_livro, nome, autor, genero, numero_de_exemplares, pode_ser_emprestado
            FROM biblioteca.livros WHERE autor ILIKE '%' || ? || '%' ORDER BY nome""", (autor,))
        return 200, {"total": total, "livros": livros}

    # GET /livros/por-faixa?minimo=&maximo=
    if partes == ["livros", "por-faixa"]:
        minimo = inteiro(param(qs, "minimo"), "minimo", 0)
        maximo = inteiro(param(qs, "maximo"), "maximo", 0)
        if minimo > maximo:
            minimo, maximo = maximo, minimo
        return 200, {"registros": consultar("""
            SELECT nome, autor, numero_de_exemplares FROM biblioteca.livros
            WHERE numero_de_exemplares BETWEEN ? AND ?
            ORDER BY numero_de_exemplares DESC""", (minimo, maximo))}

    # GET /consultas/joins/{codigo}
    if len(partes) == 3 and partes[:2] == ["consultas", "joins"]:
        sql = SQL_JOINS.get(partes[2])
        if not sql:
            raise ErroHTTP(404, "JOIN desconhecida.")
        return 200, {"registros": consultar(sql)}

    # GET /relatorios/estatisticas-por-genero?media_minima=
    if partes == ["relatorios", "estatisticas-por-genero"]:
        media = numero(param(qs, "media_minima"), "media_minima")
        return 200, {"registros": consultar("""
            SELECT genero,
                   AVG(numero_de_exemplares) AS media_exemplares,
                   MIN(numero_de_exemplares) AS minimo_exemplares,
                   MAX(numero_de_exemplares) AS maximo_exemplares
            FROM biblioteca.livros WHERE genero IS NOT NULL
            GROUP BY genero HAVING AVG(numero_de_exemplares) > ?
            ORDER BY genero""", (media,))}

    # GET /relatorios/autores-multigenero?genero1=&genero2=
    if partes == ["relatorios", "autores-multigenero"]:
        g1, g2 = param(qs, "genero1"), param(qs, "genero2")
        return 200, {"registros": consultar("""
            SELECT autor FROM biblioteca.livros WHERE genero = ?
            INTERSECT
            SELECT autor FROM biblioteca.livros WHERE genero = ?""", (g1, g2))}

    # GET /catalogo/busca?termo=
    if partes == ["catalogo", "busca"]:
        like = f"%{param(qs, 'termo')}%"
        return 200, {"registros": consultar("""
            SELECT UPPER(nome) AS titulo_destaque,
                   nome || ' (Autor: ' || COALESCE(autor, '-') || ')' AS catalogo_completo,
                   SUBSTRING(genero FROM 1 FOR 15) AS genero_curto,
                   LENGTH(nome) AS tamanho_titulo
            FROM biblioteca.livros
            WHERE nome ILIKE ? OR autor ILIKE ?
            ORDER BY autor ASC, numero_de_exemplares DESC""", (like, like))}

    # GET /auditoria/estantes-vazias
    if partes == ["auditoria", "estantes-vazias"]:
        return 200, {"registros": consultar("""
            SELECT id_estante, dominio_lado_1 FROM biblioteca.estantes
            EXCEPT
            SELECT e.id_estante, e.dominio_lado_1 FROM biblioteca.estantes e
            INNER JOIN biblioteca.livros l ON e.id_estante = l.id_estante
            ORDER BY id_estante""")}

    # GET /analises/acervo-critico?genero_alvo=&genero_comparacao=
    if partes == ["analises", "acervo-critico"]:
        alvo, comp = param(qs, "genero_alvo"), param(qs, "genero_comparacao")
        return 200, {"registros": consultar("""
            WITH Estantes_Alvo AS (
                SELECT id_estante FROM biblioteca.estantes WHERE dominio_lado_1 = ?
            )
            SELECT sub.nome, sub.numero_de_exemplares
            FROM (SELECT id_livro, nome, numero_de_exemplares, id_estante, genero
                  FROM biblioteca.livros) AS sub
            WHERE sub.id_estante IN (SELECT id_estante FROM Estantes_Alvo)
              AND sub.numero_de_exemplares > SOME (
                  SELECT numero_de_exemplares FROM biblioteca.livros WHERE genero = ?)
              AND EXISTS (SELECT 1 FROM biblioteca.estantes e WHERE e.id_estante = sub.id_estante)""",
            (alvo, comp))}

    # GET /autores/unicos
    if partes == ["autores", "unicos"]:
        return 200, {"registros": consultar("""
            SELECT DISTINCT autor FROM biblioteca.livros
            WHERE autor IS NOT NULL ORDER BY autor ASC""")}

    # GET /status (saúde da API + banco)
    if partes == ["status"]:
        consultar("SELECT 1 AS ok")
        return 200, {"api": "ok", "banco": "ok"}

    raise ErroHTTP(404, "Rota não encontrada.")


def rota_post(partes, corpo):
    # POST /livros
    if partes == ["livros"]:
        l = dados_livro(corpo, True)
        executar("""
            INSERT INTO biblioteca.livros
                (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (l["nome"], l["autor"], l["genero"], l["numero_de_exemplares"],
             l["pode_ser_emprestado"], l["id_estante"]))
        return 201, {"mensagem": "Livro cadastrado."}

    # POST /livros/procedure
    if partes == ["livros", "procedure"]:
        l = dados_livro(corpo, True)
        executar("CALL sp_cadastrar_livro(CAST(? AS VARCHAR), CAST(? AS VARCHAR), CAST(? AS VARCHAR), "
                 "CAST(? AS INT), CAST(? AS BOOLEAN), CAST(? AS INT))",
                 (l["nome"], l["autor"], l["genero"], l["numero_de_exemplares"],
                  l["pode_ser_emprestado"], l["id_estante"]))
        return 201, {"mensagem": "Livro cadastrado via PROCEDURE."}

    raise ErroHTTP(404, "Rota não encontrada.")


def rota_put(partes, corpo):
    # PUT /livros/{id}
    if len(partes) == 2 and partes[0] == "livros":
        id_livro = inteiro(partes[1], "id_livro", 1)
        l = dados_livro(corpo, False)
        afetadas = executar("""
            UPDATE biblioteca.livros
            SET nome = ?, autor = ?, genero = ?, numero_de_exemplares = ?, pode_ser_emprestado = ?
            WHERE id_livro = ?""",
            (l["nome"], l["autor"], l["genero"], l["numero_de_exemplares"],
             l["pode_ser_emprestado"], id_livro))
        if afetadas == 0:
            raise ErroHTTP(404, "Livro não encontrado.")
        return 200, {"mensagem": "Livro atualizado."}
    raise ErroHTTP(404, "Rota não encontrada.")


def rota_delete(partes):
    # DELETE /livros/{id}
    if len(partes) == 2 and partes[0] == "livros":
        id_livro = inteiro(partes[1], "id_livro", 1)
        if executar("DELETE FROM biblioteca.livros WHERE id_livro = ?", (id_livro,)) == 0:
            raise ErroHTTP(404, "Livro não encontrado.")
        return 200, {"mensagem": "Livro excluído."}
    raise ErroHTTP(404, "Rota não encontrada.")


# ==========================================================================
# Servidor HTTP
# ==========================================================================
class Manipulador(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PASTA_FRONT, **kwargs)

    def _responder_json(self, status, dados):
        corpo = json.dumps(dados, ensure_ascii=False, default=para_json).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def _ler_corpo(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho == 0:
            return {}
        if tamanho > 1_000_000:
            raise ErroHTTP(413, "Corpo muito grande.")
        try:
            dados = json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise ErroHTTP(400, "JSON inválido.")
        if not isinstance(dados, dict):
            raise ErroHTTP(400, "O corpo deve ser um objeto JSON.")
        return dados

    def _api(self, metodo):
        url = urlparse(self.path)
        partes = [unquote(p) for p in url.path[len(PREFIXO):].split("/") if p]
        qs = parse_qs(url.query)
        try:
            if metodo == "GET":
                status, dados = rota_get(partes, qs)
            elif metodo == "POST":
                status, dados = rota_post(partes, self._ler_corpo())
            elif metodo == "PUT":
                status, dados = rota_put(partes, self._ler_corpo())
            else:
                status, dados = rota_delete(partes)
            self._responder_json(status, dados)
        except ErroHTTP as e:
            self._responder_json(e.status, {"erro": e.mensagem})
        except pyodbc.IntegrityError as e:
            self._responder_json(409, {"erro": "Violação de integridade (ex.: estante inexistente).",
                                       "detalhe": str(e)})
        except pyodbc.Error as e:
            self.log_error("Erro no banco: %s", e)
            self._responder_json(503, {"erro": "Falha ao acessar o banco de dados.", "detalhe": str(e)})
        except Exception as e:
            self.log_error("Erro interno: %s", e)
            self._responder_json(500, {"erro": "Erro interno no servidor."})

    def _eh_api(self):
        caminho = urlparse(self.path).path
        return caminho == PREFIXO or caminho.startswith(PREFIXO + "/")

    def do_GET(self):
        if self._eh_api():
            self._api("GET")
        else:
            super().do_GET()

    def do_POST(self):
        self._api("POST") if self._eh_api() else self._responder_json(404, {"erro": "Não encontrado."})

    def do_PUT(self):
        self._api("PUT") if self._eh_api() else self._responder_json(404, {"erro": "Não encontrado."})

    def do_DELETE(self):
        self._api("DELETE") if self._eh_api() else self._responder_json(404, {"erro": "Não encontrado."})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.end_headers()


def garantir_rotinas():
    """Cria a FUNCTION e a PROCEDURE usadas pela API, caso não existam."""
    scripts = [
        """CREATE OR REPLACE FUNCTION fn_contar_livros_por_autor(p_autor VARCHAR)
        RETURNS INTEGER AS $$
        DECLARE total INTEGER;
        BEGIN
            SELECT COUNT(*) INTO total FROM biblioteca.livros
            WHERE autor ILIKE '%' || p_autor || '%';
            RETURN total;
        END; $$ LANGUAGE plpgsql;""",
        """CREATE OR REPLACE PROCEDURE sp_cadastrar_livro(
            p_nome VARCHAR, p_autor VARCHAR, p_genero VARCHAR,
            p_exemplares INT, p_emprestavel BOOLEAN, p_id_estante INT)
        LANGUAGE plpgsql AS $$
        BEGIN
            INSERT INTO biblioteca.livros
                (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante)
            VALUES (p_nome, p_autor, p_genero, p_exemplares, p_emprestavel, p_id_estante);
        END; $$;""",
    ]
    for sql in scripts:
        try:
            executar(sql)
        except Exception as e:
            print(f"Aviso: não foi possível criar rotina no banco: {e}")


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    garantir_rotinas()
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Manipulador)
    print(f"Biblioteca rodando em http://127.0.0.1:{porta}  (API em {PREFIXO})")
    print("Ctrl+C para encerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
        servidor.server_close()


if __name__ == "__main__":
    main()
