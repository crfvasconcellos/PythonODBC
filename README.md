# CRUD em Python com ODBC (pyodbc)

Este é um projeto simples e didático de um **CRUD** (Create, Read, Update, Delete) desenvolvido em **Python puro** utilizando conexão via **pyodbc** com banco de dados PostgreSQL.

O objetivo deste projeto é demonstrar como realizar operações SQL nativas diretamente no banco de dados sem a complexidade de frameworks web (como Django).

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **pyodbc** (Driver ODBC do PostgreSQL)
- **python-dotenv** (Gerenciamento de variáveis de ambiente)

---

## 📁 Estrutura do Projeto

```text
PythonDjangoODBC/
├── .env        # Configurações de conexão do banco de dados
├── main.py     # Script principal contendo as funções de CRUD e o menu no terminal
└── README.md   # Documentação do projeto
```

---

## ⚙️ Configuração do Ambiente

1. Certifique-se de que possui o arquivo `.env` na raiz do projeto com as credenciais do seu banco de dados:

```env
DB_DRIVER=driver
DB_SERVER=server
DB_PORT=porta
DB_DATABASE=nome_da_base
DB_USER=postgres
DB_PASSWORD=sua_senha
```

2. Instale as dependências necessárias:

```bash
pip install pyodbc python-dotenv
```

---

## 🚀 Como Executar

Execute o script `main.py` direto no terminal:

```bash
python main.py
```

Você verá o menu interativo:

```text
--- MENU CRUD ODBC (PYTHON) ---
1. Listar Livros
2. Cadastrar Novo Livro
3. Atualizar Livro
4. Excluir Livro
0. Sair
```
