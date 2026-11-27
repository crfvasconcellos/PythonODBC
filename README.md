# 📚 Sistema de Gestão de Biblioteca — Python + ODBC + PostgreSQL

## 📖 Visão Geral do Projeto

Este projeto é uma aplicação completa para gerenciamento e consulta do acervo de uma **Biblioteca**, desenvolvida em **Python puro** conectado diretamente ao **PostgreSQL** via driver **ODBC (`pyodbc`)**, sem o uso de ORMs (como Django ou SQLAlchemy) ou frameworks web externos.

O sistema conta com duas formas de uso integradas:
1. **Interface Web Visual (`Interface-biblioteca/`):** Front-end moderno em HTML, CSS e JavaScript puro que se comunica com o Python via API HTTP nativa.
2. **Menu Interativo no Terminal (`app.py`):** Menu em modo texto dividido pelas 5 seções de conteúdo de Banco de Dados (CRUD, Álgebra Relacional, Subconsultas, Conjuntos, JOINs, Views, Procedures, Triggers e Metadados ODBC).

---

## 🗂️ Estrutura Principal do Projeto

Toda a aplicação funciona a partir dos arquivos Python da **pasta base (raiz)** e da pasta **`Interface-biblioteca/`**:

```text
PythonODBC/
├── .env                       # Credenciais de conexão com o PostgreSQL via ODBC
├── requirements.txt           # Dependências do Python (pyodbc e python-dotenv)
├── db.py                      # Camada de conexão ODBC e controle de transações (ACID)
├── biblioteca.py              # Camada de dados: todas as consultas e comandos SQL puros
├── app.py                     # Ponto de entrada: Menu no Terminal e Servidor Web/API HTTP
├── testar_interfaces_e2e.py   # Script auxiliar de testes automatizados (opcional)
│
└── Interface-biblioteca/      # Front-end visual do sistema (HTML5, CSS3 e JS puro)
    ├── index.html             # Página única (SPA) com todas as telas e formulários
    ├── css/                   # Estilos visuais, animações e layout responsivo
    ├── js/
    │   └── app.js             # Lógica da interface, carrossel e chamadas fetch() para a API
    └── imgs/                  # Imagens de fundo e recursos gráficos da interface
```

*(Observação: a pasta `database/` contém apenas scripts SQL históricos salvos como referência do banco).*

---

## 🔍 Detalhamento de Cada Arquivo

### 1. `db.py` — Conexão ODBC e Transações ACID
É o arquivo mais enxuto e fundamental da comunicação com o PostgreSQL.
* **`conectar()`:** Lê as variáveis do arquivo `.env` (`DB_DRIVER`, `DB_SERVER`, `DB_PORT`, `DB_DATABASE`, `DB_USER`, `DB_PASSWORD`) e abre a conexão com o PostgreSQL através do `pyodbc.connect()` com `autocommit=False`.
* **`transacao()`:** Um gerenciador de contexto (`with transacao() as cursor:`) que entrega um cursor pronto para executar comandos SQL.
  * Se o comando terminar sem erros, ele executa `conn.commit()` automaticamente.
  * Se ocorrer qualquer erro de banco ou validação, ele executa `conn.rollback()` automaticamente (garantindo a atomicidade ACID) e fecha o cursor e a conexão no bloco `finally`.

---

### 2. `biblioteca.py` — Centralizador de Operações SQL
É o "coração" do sistema. Contém todas as funções Python que executam **SQL puro** no PostgreSQL utilizando `db.transacao()`, organizadas em **5 seções temáticas**:

* **Seção 1 — CRUD Básico e Integridade (Cap. 1 a 4):**
  * `listar_livros()`: Consulta `SELECT` ordenada, com suporte a filtro de busca via `ILIKE` e *Prepared Statement* (`?`).
  * `cadastrar_livro()`: `INSERT ... RETURNING id_livro` parametrizado, respeitando regras `NOT NULL`, `UNIQUE`, `CHECK` e `FOREIGN KEY`.
  * `atualizar_livro()`: `UPDATE` parametrizado pelo `id_livro`.
  * `excluir_livro()` e `excluir_editora()`: `DELETE` parametrizado (acionando gatilho de auditoria na exclusão de livros e testando restrição `RESTRICT` em editoras).
* **Seção 2 — Álgebra Relacional e Buscas (Cap. 2 e 3):**
  * Projeções (`DISTINCT` vs `ALL`), atributos calculados, seleção com predicados compostos (`AND`, `OR`, `NOT`), produto cartesiano, junção teta, `SELF JOIN`, buscas com `LIKE` (`%` e `_`), concatenação (`||`), `UPPER`/`LOWER`, faixas com `BETWEEN` e tratamento de nulos (`IS NULL`, `NULLS FIRST/LAST`).
* **Seção 3 — Subconsultas e Operações de Conjunto (Cap. 3):**
  * Subconsultas escalares, `IN` / `NOT IN`, subconsultas correlacionadas com `EXISTS` / `NOT EXISTS`, quantificador `SOME` com `WITH` (CTE) e operações de conjunto (`UNION`, `INTERSECT`, `EXCEPT` e suas variações `ALL`).
* **Seção 4 — Agregações, Junções, Visões e Programação no Banco (Cap. 3, 4 e 5):**
  * Agrupamentos com `GROUP BY` e `HAVING` (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`), todos os tipos de junção (`NATURAL JOIN`, `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`), leitura de `VIEW` e `MATERIALIZED VIEW` (com `REFRESH`), chamada de *Stored Function* (`SELECT fn_contar_livros_por_autor(?)`), *Stored Procedure* (`CALL sp_cadastrar_livro(...)`), consulta ao log do *Trigger* de auditoria e CTE recursiva (`WITH RECURSIVE`).
* **Seção 5 — Metadados via ODBC e DCL (Cap. 4 e 5):**
  * Inspeção do catálogo do banco usando métodos nativos do cursor ODBC (`cursor.tables()`, `cursor.columns()`), leitura de índices (`pg_indexes`) e demonstração de comandos DCL (`CREATE ROLE`, `GRANT`, `REVOKE`).

---

### 3. `app.py` — Ponto de Entrada (Terminal + Servidor Web/API)
É o arquivo que você executa para rodar o programa. Ele une o `biblioteca.py` ao usuário final de duas maneiras simples:

* **Parte 1 — Menu de Console (`menu_console()`):**
  * Exibe um menu numérico no terminal dividido nas 5 seções do `biblioteca.py`, lê os dados digitados com `input()` e imprime os resultados formatados em tabela com `mostrar_tabela()`.
* **Parte 2 — Servidor Web e API (`ServidorBiblioteca` e `iniciar_servidor_web()`):**
  * Utiliza o módulo nativo `http.server` do Python (`ThreadingHTTPServer` e `SimpleHTTPRequestHandler`) para:
    1. **Servir a Interface Visual:** Entrega automaticamente o arquivo `Interface-biblioteca/index.html`, além dos arquivos CSS, JS e imagens quando você acessa `http://127.0.0.1:8000`.
    2. **Responder às Rotas da API (`/api/...`):** Recebe chamadas HTTP (`GET`, `POST`, `PUT`, `DELETE`) vindas do JavaScript da interface, chama as funções do `biblioteca.py` e devolve os dados do PostgreSQL convertidos para JSON.
    3. **Tratar Erros do Banco:** Captura violações de integridade do PostgreSQL (`UNIQUE`, `FOREIGN KEY`, `CHECK`, `NOT NULL`) e devolve mensagens amigáveis para a interface exibir ao usuário.

---

### 4. `Interface-biblioteca/` — Interface Gráfica no Navegador
Front-end construído sem dependências externas (HTML + CSS + JavaScript puro):
* **`index.html`:** Estrutura todas as telas do sistema em uma única página (Tela Principal, Listagem do Catálogo, Cadastro de Livro, Atualização, Exclusão e Menu de Consultas Avançadas de Banco de Dados).
* **`css/`:** Estilização moderna com efeito translúcido (*glassmorphism*), tipografia adaptada para leitura e transições suaves.
* **`js/app.js`:**
  * Controla o carrossel de imagens de fundo (`imgs/fundos/`).
  * Faz a navegação entre as telas sem recarregar a página.
  * Conecta todos os formulários e botões às rotas `/api/...` do `app.py` usando `fetch()` assíncrono (`async/await`), exibindo as tabelas e mensagens de retorno do PostgreSQL diretamente na tela.

---

## ⚙️ Configuração e Como Rodar o Programa

### 1. Pré-requisitos
* **Python 3.10+** instalado.
* **PostgreSQL** rodando localmente (porta `5432`) com o banco `biblioteca` criado.
* **Driver ODBC do PostgreSQL (`psqlODBC` 64-bits)** instalado no Windows.

### 2. Instalar as Dependências do Python
No terminal, dentro da pasta raiz do projeto, execute:
```powershell
pip install -r requirements.txt
```

### 3. Configurar o Arquivo `.env`
Crie ou verifique o arquivo `.env` na raiz do projeto com os dados do seu PostgreSQL:
```env
DB_DRIVER=PostgreSQL ODBC Driver(UNICODE)
DB_SERVER=localhost
DB_PORT=5432
DB_DATABASE=biblioteca
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

### 4. Executar o Sistema

#### 🌐 Modo 1: Abrir a Interface Web (Navegador)
No terminal, execute:
```powershell
python app.py --web
```
Depois, abra o navegador e acesse:
👉 **`http://127.0.0.1:8000`**

*(Se quiser usar outra porta, basta informá-la no comando, por exemplo: `python app.py --web 8080`). Para desligar o servidor, pressione `Ctrl + C` no terminal.*

#### 💻 Modo 2: Abrir o Menu Interativo no Terminal
Se preferir usar o sistema em modo texto direto no terminal, execute:
```powershell
python app.py
```
Escolha o número da seção desejada (`1` a `5`), digite o número da operação e pressione `Enter`.
