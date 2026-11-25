"""
Módulo de Inspeção de Metadados do Catálogo via Driver ODBC (pyodbc).
"""
import pyodbc
from src.core.connection import get_connection


def inspecionar_tabelas_schema(schema: str = "biblioteca") -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Metadados de Banco de Dados e Catálogo ODBC (cursor.tables)
    [SLIDE/CAPÍTULO] Cap. 5 / Cap. 8 (Acesso a Metadados via API ODBC)
    [DESCRIÇÃO] Lista dinamicamente todas as tabelas e views do schema informado
                usando a interface de metadados nativa do pyodbc.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            tabelas = []
            for row in cursor.tables(schema=schema):
                tabelas.append({
                    "schema": row.table_schem,
                    "tabela": row.table_name,
                    "tipo": row.table_type,
                })
            return tabelas
    except pyodbc.Error as erro:
        print(f"[ERRO METADADOS TABELAS] {erro}")
        return None
    finally:
        if conn:
            conn.close()


def inspecionar_colunas_tabela(tabela: str, schema: str = "biblioteca") -> list[dict] | None:
    """
    [CONCEITO AVALIADO] Metadados de Colunas e Tipos via ODBC (cursor.columns)
    [SLIDE/CAPÍTULO] Cap. 5 / Cap. 8 (Introspecção de Esquema via ODBC)
    [DESCRIÇÃO] Retorna nome, tipo de dado, tamanho e nulabilidade de cada coluna
                de uma tabela específica do schema biblioteca.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            colunas = []
            for col in cursor.columns(table=tabela, schema=schema):
                colunas.append({
                    "coluna": col.column_name,
                    "tipo": col.type_name,
                    "tamanho": col.column_size,
                    "permite_nulo": col.is_nullable,
                })
            return colunas
    except pyodbc.Error as erro:
        print(f"[ERRO METADADOS COLUNAS] {erro}")
        return None
    finally:
        if conn:
            conn.close()
