import os
import sys
import pyodbc
from dotenv import load_dotenv, find_dotenv

sys.stdout.reconfigure(encoding='utf-8')

def aplicar_scripts():
    """Conecta ao banco de dados e executa o script SQL consolidado contendo schema, dados, visões e visões materializadas."""
    load_dotenv(find_dotenv(filename=".env", usecwd=True))
    
    driver = os.getenv("DB_DRIVER", "PostgreSQL Unicode(x64)")
    server = os.getenv("DB_SERVER", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_DATABASE", "biblioteca")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    conn_str = f"DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={password};"
    
    print("=" * 70)
    print("EXECUÇÃO DE CONSOLIDAÇÃO DO BANCO DE DADOS (DOCENTE / ACADÊMICO)")
    print("=" * 70)
    print(f"SGBD: PostgreSQL | Banco: '{database}' | Servidor: '{server}:{port}'")

    script_banco = os.path.join("atividade_1_banco", "banco_biblioteca.sql")
    script_views = os.path.join("atividade_2_views", "04_views.sql")
    
    if not os.path.exists(script_banco) or not os.path.exists(script_views):
        print("Erro: Arquivos SQL não encontrados em atividade_1_banco ou atividade_2_views.")
        return

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("\nLendo e aplicando o script da Atividade 1 (Banco de Dados)...")
        with open(script_banco, "r", encoding="utf-8") as f:
            cursor.execute(f.read())

        print("Aplicando o script da Atividade 2 (10 Views + 10 Materialized Views)...")
        with open(script_views, "r", encoding="utf-8") as f:
            cursor.execute(f.read())

        conn.commit()
        print("Banco de dados e Visões consolidados com SUCESSO!\n")

        # Verificação das Visões Criadas
        views = [
            "vw_livros_localizacao_completa",
            "vw_espacos_sem_estantes",
            "vw_livros_nao_emprestaveis",
            "vw_edificacoes_sem_livros",
            "vw_resumo_estantes_dominio",
            "vw_livros_em_espacos_privados",
            "vw_capacidade_pisos_edificacoes",
            "vw_generos_livros_por_edificacao",
            "vw_hierarquia_edificacoes_pisos",
            "vw_autores_obras_cadastradas"
        ]

        mviews = [
            "mv_estatisticas_por_edificacao",
            "mv_total_livros_por_genero_e_piso",
            "mv_ocupacao_estantes_livros",
            "mv_livros_emprestaveis_vs_restritos",
            "mv_relatorio_acervo_espacos_privados",
            "mv_capacidade_pisos_vs_espacos",
            "mv_ranking_autores_maior_acervo",
            "mv_densidade_estantes_por_tipo_espaco",
            "mv_mapeamento_acervo_biblioteca_diretoria",
            "mv_relatorio_completo_hierarquia"
        ]

        print("-" * 70)
        print("VERIFICAÇÃO DAS 10 VISÕES TRADICIONAIS (VIEWS)")
        print("-" * 70)
        for v in views:
            cursor.execute(f"SELECT COUNT(*) FROM {v}")
            cnt = cursor.fetchone()[0]
            print(f"  • {v:<35}: {cnt} registros retornados")

        print("\n" + "-" * 70)
        print("VERIFICAÇÃO DAS 10 VISÕES MATERIALIZADAS (MATERIALIZED VIEWS)")
        print("-" * 70)
        for mv in mviews:
            cursor.execute(f"SELECT COUNT(*) FROM {mv}")
            cnt = cursor.fetchone()[0]
            print(f"  • {mv:<35}: {cnt} registros armazenados")

        conn.close()
        print("\n" + "=" * 70)
        print("CONSOLIDAÇÃO E VERIFICAÇÃO CONCLUÍDAS COM SUCESSO!")
        print("=" * 70)

    except Exception as e:
        print(f"\nErro ao consolidar banco de dados: {e}")

if __name__ == "__main__":
    aplicar_scripts()
