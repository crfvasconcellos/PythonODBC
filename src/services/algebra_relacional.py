"""
Módulo de Álgebra Relacional aplicada ao SQL (Projeção, Seleção, Renomeação e Auto-junção).
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def projecao_autores_unicos() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Álgebra Relacional - Projeção (π), DISTINCT e Renomeação (AS)
    [SLIDE/CAPÍTULO] Cap. 2 e Cap. 3 (Operação de Projeção e Eliminação de Duplicatas)
    [DESCRIÇÃO] Projeta exclusivamente os autores distintos cadastrados no acervo,
                renomeando a coluna de saída e filtrando valores nulos.
    """
    sql = """
        SELECT DISTINCT autor AS nome_autor
        FROM biblioteca.livros
        WHERE autor IS NOT NULL
        ORDER BY autor ASC;
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return fetch_as_dicts(cursor)
    except pyodbc.Error as erro:
        print(f"[ERRO PROJEÇÃO] {erro}")
        return None
    finally:
        if conn:
            conn.close()


def selecao_multiplos_predicados(termo: str, minimo: int, maximo: int) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Álgebra Relacional - Seleção (σ) com AND, OR, LIKE/ILIKE e BETWEEN
    [SLIDE/CAPÍTULO] Cap. 2 e Cap. 3 (Predicados Compostos e Operações de String)
    [DESCRIÇÃO] Filtra livros cujo título ou autor contenham o termo informado E cuja
                quantidade de exemplares esteja dentro do intervalo inclusivo [minimo, maximo].
    """
    sql = """
        SELECT UPPER(nome) AS titulo_destaque,
               autor,
               genero,
               numero_de_exemplares
        FROM biblioteca.livros
        WHERE (nome ILIKE ? OR autor ILIKE ?)
          AND numero_de_exemplares BETWEEN ? AND ?
        ORDER BY autor ASC, numero_de_exemplares DESC;
    """
    like_param = f"%{termo}%"
    # Placeholder pronto para execução com Prepared Statement:
    # cursor.execute(sql, (like_param, like_param, int(minimo), int(maximo)))
    _ = (sql, like_param, minimo, maximo)
    return None


def selecao_valores_nulos() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Predicado de Valor Nulo (IS NULL / IS NOT NULL)
    [SLIDE/CAPÍTULO] Cap. 3 (Valores Nulos e Lógica de Três Valores)
    [DESCRIÇÃO] Identifica estantes que não possuem domínio definido no lado 2 (dominio_lado_2 IS NULL).
    """
    sql = """
        SELECT id_estante, dominio_lado_1, dominio_lado_2, tipo
        FROM biblioteca.estantes
        WHERE dominio_lado_2 IS NULL;
    """
    # TODO: Executar consulta e retornar fetch_as_dicts(cursor)
    _ = sql
    return None


def produto_cartesiano_auto_juncao_mesmo_genero(genero: str) -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Produto Cartesiano (×) e Auto-Junção (Self-Join) com Renomeação (ρ)
    [SLIDE/CAPÍTULO] Cap. 2 e Cap. 3 (Variáveis de Tupla / Alias na cláusula FROM)
    [DESCRIÇÃO] Compara pares distintos de livros (l1, l2) que compartilham o mesmo gênero
                e o mesmo autor, evitando autopareamento (l1.id_livro < l2.id_livro).
    """
    sql = """
        SELECT l1.nome AS livro_1,
               l2.nome AS livro_2,
               l1.autor,
               l1.genero
        FROM biblioteca.livros AS l1,
             biblioteca.livros AS l2
        WHERE l1.genero = ?
          AND l1.genero = l2.genero
          AND l1.autor = l2.autor
          AND l1.id_livro < l2.id_livro;
    """
    # Placeholder com Prepared Statement:
    # cursor.execute(sql, (genero,))
    _ = (sql, genero)
    return None
