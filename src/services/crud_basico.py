"""
Módulo de Operações CRUD Básicas (DML) com Prepared Statements.
"""
import pyodbc
from src.core.connection import get_connection, fetch_as_dicts


def listar_livros() -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Consulta Básica (SELECT / ORDER BY)
    [SLIDE/CAPÍTULO] Cap. 3 (Introdução ao SQL)
    [DESCRIÇÃO] Retorna todos os livros cadastrados ordenados pelo ID.
    """
    sql = """
        SELECT id_livro, nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante
        FROM biblioteca.livros
        ORDER BY id_livro ASC;
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return fetch_as_dicts(cursor)
    except pyodbc.Error as erro:
        print(f"[ERRO SELECT] {erro}")
        return None
    finally:
        if conn:
            conn.close()


def cadastrar_livro(
    nome: str,
    autor: str,
    genero: str,
    numero_de_exemplares: int,
    pode_ser_emprestado: bool,
    id_estante: int,
) -> bool:
    """
    [CONCEITO AVALIADO] Inserção de Dados (INSERT) com Prepared Statement e Transação
    [SLIDE/CAPÍTULO] Cap. 3 (Modificação do Banco de Dados - INSERT)
    [DESCRIÇÃO] Insere um novo livro na tabela biblioteca.livros usando placeholders (?)
                para prevenir SQL Injection.
    """
    sql = """
        INSERT INTO biblioteca.livros
            (nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante)
        VALUES (?, ?, ?, ?, ?, ?);
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (nome, autor, genero, int(numero_de_exemplares), bool(pode_ser_emprestado), int(id_estante)),
            )
        conn.commit()
        return True
    except pyodbc.Error as erro:
        if conn:
            conn.rollback()
        print(f"[ERRO INSERT] {erro}")
        return False
    finally:
        if conn:
            conn.close()


def atualizar_livro(
    id_livro: int,
    nome: str,
    autor: str,
    genero: str,
    numero_de_exemplares: int,
    pode_ser_emprestado: bool,
) -> bool:
    """
    [CONCEITO AVALIADO] Atualização de Dados (UPDATE) com Prepared Statement e Transação
    [SLIDE/CAPÍTULO] Cap. 3 (Modificação do Banco de Dados - UPDATE)
    [DESCRIÇÃO] Atualiza os atributos de um livro existente identificado por id_livro.
    """
    sql = """
        UPDATE biblioteca.livros
        SET nome = ?, autor = ?, genero = ?, numero_de_exemplares = ?, pode_ser_emprestado = ?
        WHERE id_livro = ?;
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (nome, autor, genero, int(numero_de_exemplares), bool(pode_ser_emprestado), int(id_livro)),
            )
            afetadas = cursor.rowcount
        conn.commit()
        return afetadas > 0
    except pyodbc.Error as erro:
        if conn:
            conn.rollback()
        print(f"[ERRO UPDATE] {erro}")
        return False
    finally:
        if conn:
            conn.close()


def excluir_livro(id_livro: int) -> bool:
    """
    [CONCEITO AVALIADO] Remoção de Dados (DELETE) com Prepared Statement e Transação
    [SLIDE/CAPÍTULO] Cap. 3 (Modificação do Banco de Dados - DELETE)
    [DESCRIÇÃO] Remove um livro pelo seu ID (também dispara o trigger de auditoria, se ativo).
    """
    sql = "DELETE FROM biblioteca.livros WHERE id_livro = ?;"
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (int(id_livro),))
            afetadas = cursor.rowcount
        conn.commit()
        return afetadas > 0
    except pyodbc.Error as erro:
        if conn:
            conn.rollback()
        print(f"[ERRO DELETE] {erro}")
        return False
    finally:
        if conn:
            conn.close()
