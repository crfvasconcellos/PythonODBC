import os
import pyodbc
from django.shortcuts import render, redirect
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente do .env
load_dotenv(find_dotenv(filename=".env", usecwd=True))

def get_db():
    driver = os.getenv("DB_DRIVER", "PostgreSQL Unicode(x64)")
    server = os.getenv("DB_SERVER", "altaria.proxy.rlwy.net")
    port = os.getenv("DB_PORT", "28633")
    database = os.getenv("DB_DATABASE", "railway")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    
    conn_str = f"DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={user};PWD={password};"
    return pyodbc.connect(conn_str)

def index(request):
    conn = get_db()
    cursor = conn.cursor()

    # SALVAR (CRIAR OU ATUALIZAR)
    if request.method == 'POST':
        livro_id = request.POST.get('id')
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        ano = int(request.POST.get('ano') or 0)
        preco = float(request.POST.get('preco') or 0)

        if livro_id:
            cursor.execute(
                "UPDATE livros SET titulo=?, autor=?, ano=?, preco=? WHERE id=?", 
                (titulo, autor, ano, preco, int(livro_id))
            )
        else:
            cursor.execute(
                "INSERT INTO livros (titulo, autor, ano, preco) VALUES (?, ?, ?, ?)", 
                (titulo, autor, ano, preco)
            )
        conn.commit()
        conn.close()
        return redirect('index')

    # EXCLUIR
    delete_id = request.GET.get('delete')
    if delete_id:
        cursor.execute("DELETE FROM livros WHERE id = ?", (int(delete_id),))
        conn.commit()
        conn.close()
        return redirect('index')

    # BUSCAR LIVRO PARA EDICAO (SE SOLICITADO)
    edit_livro = None
    edit_id = request.GET.get('edit')
    if edit_id:
        cursor.execute("SELECT id, titulo, autor, ano, preco FROM livros WHERE id = ?", (int(edit_id),))
        row = cursor.fetchone()
        if row:
            edit_livro = {'id': row[0], 'titulo': row[1], 'autor': row[2], 'ano': row[3], 'preco': float(row[4])}

    # LISTAR TODOS OS LIVROS
    cursor.execute("SELECT id, titulo, autor, ano, preco FROM livros ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    livros = [{'id': r[0], 'titulo': r[1], 'autor': r[2], 'ano': r[3], 'preco': float(r[4])} for r in rows]

    return render(request, 'index.html', {'livros': livros, 'edit_livro': edit_livro})
