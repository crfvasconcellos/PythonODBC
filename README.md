# CRUD em Python com Django e ODBC (pyodbc)

Este é um projeto simples de demonstração de um CRUD (Create, Read, Update, Delete) desenvolvido em **Python** utilizando **Django** e conexão direta via **pyodbc** com um banco de dados PostgreSQL.

O objetivo do projeto é realizar operações SQL nativas diretamente no banco de dados, sem o uso de geradores de DAO ou Django ORM.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Django 6**
- **pyodbc** (Driver ODBC do PostgreSQL)
- **python-dotenv** (Gerenciamento de variáveis de ambiente)
- **HTML5 Puro** (Interface minimalista sem frameworks CSS)

---

## 📁 Estrutura do Projeto

```text
PythonDjangoODBC/
├── .env                # Configurações de conexão do banco de dados
├── manage.py           # Utilitário CLI do Django
├── README.md           # Documentação do projeto
├── main/               # Módulo principal da aplicação Django
│   ├── __init__.py
│   ├── settings.py     # Configurações do Django
│   ├── urls.py         # Mapeamento de rotas
│   ├── views.py        # Lógica do CRUD e consultas SQL via pyodbc
│   └── wsgi.py
└── templates/
    └── index.html      # Página HTML única com formulário e tabela
```

---

## ⚙️ Configuração do Ambiente

1. Crie ou edite o arquivo `.env` na raiz do projeto com as credenciais do seu banco de dados:

```env
DB_DRIVER=PostgreSQL Unicode(x64)
DB_SERVER=seu_servidor.proxy.rlwy.net
DB_PORT=28633
DB_DATABASE=railway
DB_USER=postgres
DB_PASSWORD=sua_senha
```

2. Instale as dependências necessárias:

```bash
pip install django pyodbc python-dotenv
```

---

## 🚀 Como Executar o Projeto

1. Abra o terminal na pasta raiz do projeto.
2. Execute o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

3. Acesse no navegador:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**
