# 📚 Documentação Técnica — Sistema de Gestão de Biblioteca & Banco de Dados

> **Guia Oficial de Entrega e Consulta Rápida para Avaliação**  
> **Avaliador:** Prof. Dr. Ary Henrique  
> **Referência Teórica:** Silberschatz, Korth & Sudarshan — *Sistema de Banco de Dados* (Capítulos 1 a 5 e 14)  
> **Repositório / Arquitetura:** Python 3.10+ · PostgreSQL 14+ · `pyodbc` (ODBC Nativo, sem ORM)

---

## 1. Visão Geral do SGBD e Tecnologias

O sistema implementa a gestão completa de acervo, estantes, localização física e consultas analíticas de uma biblioteca utilizando **SQL puro** via driver ODBC, priorizando transparência didática, segurança contra injeção de SQL e conformidade estrita com as propriedades **ACID**.

| Componente | Especificação Técnica |
| :--- | :--- |
| **SGBD Utilizado** | **PostgreSQL (versão 14+)** — SGBD relacional completo, compatível com ACID, suporte nativo a `MATERIALIZED VIEW`, `PL/pgSQL`, `WITH RECURSIVE`, `WINDOW FUNCTIONS`, `ROLLUP`/`CUBE` e catálogo `pg_indexes`. |
| **Driver de Conexão** | **`pyodbc` (>= 5.0.0)** utilizando o driver oficial **`PostgreSQL Unicode`** (`psqlODBC` 64-bits). |
| **Linguagem / Runtime** | **Python 3.10+** (com *type hints* modernos e biblioteca padrão `http.server` para modo web, sem ORMs ou frameworks externos). |
| **Padrão de Execução** | **Prepared Statements** com placeholders (`?`) em 100% das operações parametrizadas, garantindo imunidade contra ataques de **SQL Injection** e separação estrita entre código SQL e dados do usuário. |
| **Gerenciamento Transacional** | Controle manual explícito em `db.py` (`conn.autocommit = False`) encapsulado no gerenciador de contexto `transacao()`: confirmação via `conn.commit()` em caso de sucesso e reversão atômica via `conn.rollback()` em qualquer exceção (`pyodbc.Error` ou erro de regra de negócio), com encerramento garantido de cursor e conexão no bloco `finally`. |

---

## 2. Configuração de Ambiente e Credenciais (`.env`)

### 2.1. Estrutura do Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto (mesmo diretório de `db.py` e `app.py`). O módulo `db.py` carrega automaticamente essas variáveis via `python-dotenv` (`load_dotenv`).

```env
# Driver ODBC instalado no sistema operacional (db.py adiciona as chaves { } automaticamente)
DB_DRIVER=PostgreSQL Unicode(x64)

# Endereço do servidor PostgreSQL (equivalente conceitual a DB_HOST)
DB_SERVER=localhost

# Porta padrão do PostgreSQL
DB_PORT=5432

# Nome do banco de dados alvo (equivalente conceitual a DB_NAME)
DB_DATABASE=biblioteca

# Usuário e senha de autenticação no PostgreSQL
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
```

#### Referência das Variáveis de Ambiente

| Variável lida por `db.py` | Referência Comum | Valor Padrão (`db.py`) | Descrição |
| :--- | :--- | :--- | :--- |
| `DB_SERVER` | `DB_HOST` | `localhost` (ou `127.0.0.1`) | Host/IP onde o serviço do PostgreSQL está em execução. |
| `DB_PORT` | `DB_PORT` | `5432` | Porta TCP de escuta do servidor PostgreSQL. |
| `DB_DATABASE` | `DB_NAME` | `biblioteca` (ex.: `biblioteca_db`) | Nome do banco de dados contendo o schema `biblioteca`. |
| `DB_USER` | `DB_USER` | `postgres` | Role/usuário com privilégios no banco e para testes DCL. |
| `DB_PASSWORD` | `DB_PASSWORD` | `""` (vazio) | Senha do usuário PostgreSQL informado em `DB_USER`. |
| `DB_DRIVER` | `DB_DRIVER` | `PostgreSQL Unicode(x64)` | Nome do driver ODBC instalado (ex.: `PostgreSQL Unicode` ou `PostgreSQL ODBC Driver(UNICODE)`). No código, `db.py` monta `DRIVER={...}` automaticamente. |

> **Nota de Segurança:** Nunca versione o arquivo `.env` com credenciais reais em repositórios públicos (ele está protegido pelo `.gitignore`).

### 2.2. Instalação das Dependências (`requirements.txt`)

O projeto depende exclusivamente de dois pacotes externos listados em `requirements.txt`:

- `pyodbc>=5.0.0` — Ponte ODBC entre Python e o driver `psqlODBC` do PostgreSQL.
- `python-dotenv>=1.0.0` — Leitura automática das credenciais do arquivo `.env`.

**Pré-requisitos:** Python 3.10+, PostgreSQL 14+ ativo na porta `5432` e driver `psqlODBC` (Unicode 64-bits) instalado.

**Instalação via terminal (na raiz do projeto):**

```powershell
pip install -r requirements.txt
```

---

## 3. Arquitetura do Projeto (Modelo Ultra-Enxuto)

O sistema adota uma arquitetura em camadas mínimas e coesas, eliminando camadas redundantes para facilitar a inspeção de código durante a avaliação acadêmica:

```text
PythonDjangoODBC/
├── database/scripts/          # Scripts SQL sequenciais (01_criacao_banco.sql a 06_consultas_cap3.sql)
├── .env                       # Variáveis de ambiente e credenciais ODBC
├── requirements.txt           # Dependências Python (pyodbc, python-dotenv)
├── db.py                      # Camada de conexão ODBC e gerenciador transacional ACID
├── biblioteca.py              # Centralizador único de todas as operações SQL (6 seções lógicas)
├── app.py                     # Ponto de entrada unificado: Menu Console + Servidor Web/API (--web)
├── Interface-biblioteca/      # Front-end SPA em HTML5, CSS3 e JavaScript puro (fetch API)
└── DOCUMENTACAO_SISTEMA.md    # Esta documentação técnica oficial
```

### Papel de Cada Camada

1. **`database/scripts/` (Referência SQL — DDL, DML e Objetos de Banco):**
   Scripts SQL sequenciais (`01_criacao_banco.sql` até `06_consultas_cap3.sql`) que definem o schema `biblioteca`, tabelas, chaves primárias simples e compostas, chaves estrangeiras com ações referenciais (`CASCADE`, `SET NULL`, `RESTRICT`), restrições (`UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT`, `ALTER TABLE`), cargas DML, `VIEW`s, `MATERIALIZED VIEW`s, `INDEX`es, `FUNCTION`s, `PROCEDURE`s e `TRIGGER`s.
2. **`db.py` (Conexão ODBC e Controle Transacional):**
   - `conectar()`: Constrói a string de conexão ODBC a partir do `.env`, abre a conexão com `autocommit=False` e `timeout=10`.
   - `transacao()`: Context manager (`@contextmanager`) que fornece um cursor ativo, executa `conn.commit()` ao final do bloco `with` sem erros, reverte via `conn.rollback()` em caso de exceção e sempre libera `cursor.close()` e `conn.close()`.
3. **`biblioteca.py` (Centralizador Único de Operações SQL):**
   Concentra 100% das consultas, comandos DML/DDL/DCL, invocações de objetos de banco e baterias automatizadas de validação. É dividido internamente em **6 seções lógicas**, com docstrings padronizadas contendo as tags `[CONCEITO]`, `[CAPÍTULO]` e `[DESCRIÇÃO]` para localização instantânea via `Ctrl + F`.
4. **`app.py` (Ponto de Entrada Unificado — Console + Web/API):**
   - **Modo Console (`python app.py`):** Menu interativo dividido em 5 menus temáticos que cobrem CRUD, consultas interativas e os 6 atalhos das baterias automatizadas (Partes 1 a 6).
   - **Modo Web (`python app.py --web [porta]`):** Servidor `ThreadingHTTPServer` nativo que serve a SPA em `Interface-biblioteca/` e expõe endpoints REST em `/api/...`, traduzindo códigos de erro SQLSTATE do PostgreSQL (`23505` UNIQUE, `23503` FK/RESTRICT, `23514` CHECK, `23502` NOT NULL) em respostas HTTP `409 Conflict` amigáveis.

---

## 4. Dicionário Completo de Funções do `biblioteca.py`

> **Convenção Transacional:** Todas as funções abaixo utilizam `with transacao() as cursor:` (commit automático no sucesso e rollback automático em qualquer exceção) **ou** conexão manual (`conectar()`) com `conn.rollback()` explícito no bloco `finally` para demonstrações/testes que não devem persistir dados temporários no banco.  
> **Função Auxiliar Global:** `_para_dicts(cursor) -> list[dict]` converte linhas retornadas pelo `pyodbc` em lista de dicionários e normaliza valores booleanos do driver ODBC (`pode_ser_emprestado`).

---

### Seção 1 — CRUD Básico, Gestão de Estantes e Integridade DDL (Cap. 1 a 4)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `listar_livros(busca: str \| None = None) -> list[dict]` | Lista todos os livros ordenados por `id_livro` ou filtra por trecho no título/autor via `ILIKE` parametrizado. | CRUD, `SELECT`, `ORDER BY`, `ILIKE`, Prepared Statement (Cap. 3). | `transacao()`: rollback e fechamento automático em caso de `pyodbc.Error`. |
| `_validar_capacidade_estante(cursor, id_estante: int, novos_exemplares: int, ignorar_id_livro: int \| None = None) -> None` | *(Auxiliar interno)* Verifica se a estante existe e se a soma dos exemplares na estante não excede `numero_de_livros`. | Integridade de domínio/negócio, `COALESCE`, `SUM` (Cap. 3 e 4). | Lança `ValueError` descritivo; aciona rollback da transação chamadora. |
| `cadastrar_livro(nome: str, autor: str, genero: str, numero_de_exemplares: int, pode_ser_emprestado: bool, id_estante: int, codigo_patrimonio: str \| None = None, status_conservacao: str = "Bom") -> int` | Valida capacidade da estante e insere novo livro via `INSERT ... RETURNING id_livro`. | CRUD, `INSERT`, Prepared Statement, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FK` (Cap. 3 e 4). | `transacao()`: reverte inserção em violação de capacidade (`ValueError`) ou integridade (`pyodbc.IntegrityError`). |
| `atualizar_livro(id_livro: int, nome: str, autor: str, genero: str, numero_de_exemplares: int, pode_ser_emprestado: bool) -> bool` | Localiza o livro, revalida a capacidade da estante (desconsiderando o próprio livro) e executa `UPDATE`. | CRUD, `UPDATE`, Prepared Statement, Transação ACID (Cap. 3). | `transacao()`: rollback automático em erro; retorna `False` se `id_livro` não existir. |
| `excluir_livro(id_livro: int) -> bool` | Remove um livro pelo `id_livro`, disparando o trigger `AFTER DELETE` de auditoria. | CRUD, `DELETE`, Prepared Statement, Trigger de Auditoria (Cap. 3 e 5). | `transacao()`: rollback em falha; retorna `cursor.rowcount > 0`. |
| `excluir_editora(id_editora: int) -> bool` | Tenta remover uma editora pelo `id_editora` (bloqueada por `ON DELETE RESTRICT` se houver livros vinculados). | `DELETE`, Integridade Referencial, `ON DELETE RESTRICT` (Cap. 4). | `transacao()`: propaga `pyodbc.IntegrityError` com rollback automático. |
| `_garantir_infraestrutura_base_estantes(cursor) -> tuple[int, str]` | *(Auxiliar interno)* Garante existência mínima de categoria, `tipos_de_espaco` e hierarquia física (`biblioteca` -> `edificacoes` -> `pisos` -> `espacos`). | Integridade Referencial hierárquica, `FOREIGN KEY` (Cap. 4). | Executa dentro da transação chamadora; falha reverte toda a cadeia. |
| `listar_estantes() -> list[dict]` | Lista estantes com domínios, capacidade máxima, quantidade de títulos, exemplares ocupados e vagas restantes. | `LEFT JOIN`, `COUNT`, `SUM`, `COALESCE`, `GREATEST`, `GROUP BY` (Cap. 3 e 4). | `transacao()`: rollback automático em erro ODBC. |
| `cadastrar_estante(dominio_lado_1: str, dominio_lado_2: str = "Geral", numero_de_livros: int = 100) -> int` | Cria nova estante garantindo a infraestrutura física base e retorna o `id_estante` gerado. | CRUD, `INSERT ... RETURNING`, Prepared Statement, `FK` (Cap. 3 e 4). | `transacao()`: rollback atômico em qualquer falha. |
| `excluir_estante(id_estante: int) -> dict` | Conta livros vinculados e exclui a estante, apagando livros filhos via `ON DELETE CASCADE`. | `DELETE`, `ON DELETE CASCADE`, Integridade Referencial (Cap. 3 e 4). | `transacao()`: rollback em falha; retorna `{"excluiu", "livros_removidos"}`. |
| `validar_colunas_ddl_alter_table(tabela: str = "livros", colunas_esperadas: tuple = ("codigo_isbn", "valor_seguro")) -> dict` | Inspeciona metadados via `cursor.columns()` para comprovar colunas adicionadas por `ALTER TABLE`. | `ALTER TABLE`, DDL, Catálogo ODBC `cursor.columns()` (Cap. 3 e 5). | `transacao()`: leitura segura com fechamento automático. |
| `testar_parte1_completa() -> list[dict]` *(alias: `validar_integridade_ddl`)* | Executa 8 testes práticos isolados para todos os itens da Parte 1 (PK simples, PK composta, FK, `CASCADE`/`SET NULL`/`RESTRICT`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT` e `ALTER TABLE`). | DDL e Restrições de Integridade completas (Cap. 1 a 4). | Cada subteste abre conexão própria, captura `pyodbc.IntegrityError` com mensagem amigável e executa `conn.rollback()` obrigatório no `finally`. |

---

### Seção 2 — Álgebra Relacional, Buscas e Ordenação (Cap. 2 e 3)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `listar_autores_unicos() -> list[dict]` | Retorna autores distintos (não nulos) ordenados alfabeticamente. | Projeção ($\Pi$), `SELECT DISTINCT`, `IS NOT NULL` (Cap. 2 e 3). | `transacao()` com rollback em erro. |
| `listar_autores_todos() -> list[dict]` | Retorna todos os autores mantendo repetições para comparação direta com `DISTINCT`. | Projeção, `SELECT ALL` (Cap. 3). | `transacao()` com rollback em erro. |
| `buscar_catalogo_palavra_chave(termo: str) -> list[dict]` | Busca obras por título/autor formatando saída com `UPPER`, `SUBSTRING`, `LENGTH` e concatenação `\|\|`. | Seleção ($\sigma$), `ILIKE`, `OR`, funções de string, `ORDER BY` (Cap. 3). | `transacao()` com Prepared Statement `(like, like)`. |
| `buscar_livros_por_faixa_exemplares(minimo: int, maximo: int, negar: bool = False) -> list[dict]` | Filtra livros com exemplares dentro (`BETWEEN`) ou fora (`NOT BETWEEN`) do intervalo `[minimo, maximo]`. | Seleção, `BETWEEN` / `NOT BETWEEN`, `AND`, `NOT` (Cap. 3). | Inverte limites se `minimo > maximo`; `transacao()` com rollback em erro. |
| `listar_estantes_sem_dominio_lado2() -> list[dict]` | Identifica estantes cujo `dominio_lado_2` não foi preenchido. | Lógica trivalente, `IS NULL` (Cap. 3). | `transacao()` com rollback em erro. |
| `auto_juncao_livros_mesmo_autor_genero(genero: str) -> list[dict]` | Localiza pares distintos de livros do mesmo autor dentro de um gênero (`a.id_livro < b.id_livro`). | Renomeação ($\rho$ / `AS`), Auto-junção (`SELF JOIN`) (Cap. 2 e 3). | `transacao()` com Prepared Statement `(genero,)`. |
| `projecao_distinct_all_e_calculo(fator_reajuste: float = 1.10) -> dict` | Compara `DISTINCT` vs `ALL` em `status_conservacao` e projeta atributo calculado `ROUND(numero_de_exemplares * fator, 2)`. | Projeção ($\Pi$), `DISTINCT` vs `ALL`, Atributo Calculado, `AS` (Cap. 2 e 3). | `transacao()` com cast seguro e rollback em erro. |
| `selecao_predicados_compostos_e_tupla(status: str = "Bom", emprestavel: bool = True, minimo: int = 5) -> dict` | Executa filtro com operadores (`=`, `<>`, `>`, `<`, `>=`, `<=`), `AND`/`OR`/`NOT` e comparação de tupla `(status_conservacao, pode_ser_emprestado) = (?, ?)`. | Seleção ($\sigma$), Predicados Compostos e Comparação de Tuplas (Cap. 2 e 3). | `transacao()` com Prepared Statements. |
| `produto_cartesiano_e_juncao_teta(min_exemplares: int = 1) -> dict` | Executa `livros × espacos` comprovando cardinalidade $\|R\| \times \|S\|$ e Junção Teta clássica no `WHERE` com `categorias_acervo`. | Produto Cartesiano ($\times$) e Junção Teta ($\bowtie_\theta$) (Cap. 2 e 3). | `transacao()` com rollback em erro. |
| `buscar_strings_like_coringa_posicao(padrao_exato: str = "PAT-____", substring: str = "%a%") -> dict` | Demonstra `LIKE` com `%` (substring) e `_` (posição exata), além de `\|\|`, `UPPER()` e `LOWER()`. | Operações em Strings: `LIKE` (`%`, `_`), `\|\|`, `UPPER`, `LOWER` (Cap. 3). | `transacao()` com Prepared Statements. |
| `consultar_nulos_e_nao_nulos() -> dict` | Separa livros sem código de patrimônio (`IS NULL`) e com código preenchido (`IS NOT NULL`). | Valores Nulos, `IS NULL` e `IS NOT NULL` (Cap. 3). | `transacao()` com rollback em erro. |
| `ordenar_livros_multiatributo_nulos(nulos_primeiro: bool = True) -> list[dict]` | Ordena livros por múltiplos atributos controlando explicitamente `NULLS FIRST` ou `NULLS LAST`. | `ORDER BY` multiatributo (`ASC`/`DESC`), `NULLS FIRST` / `NULLS LAST` (Cap. 3). | `transacao()` com cláusula controlada por booleano (sem entrada crua no SQL). |
| `testar_parte2_completa() -> list[dict]` | Bateria automatizada que valida todos os 8 itens da Parte 2 e retorna relatório estruturado (`OK`/`FALHA`). | Álgebra Relacional e DML completos (Cap. 2 e 3). | Cada subfunção usa `transacao()` (somente leitura). |

---

### Seção 3 — Subconsultas Iniciais, Agregações e Operações de Conjunto (Cap. 3)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `livros_acima_da_media_escalar() -> list[dict]` | Retorna obras com número de exemplares acima da média global do acervo. | Subconsulta Escalar no `WHERE`, `AVG` (Cap. 3). | `transacao()` com rollback em erro. |
| `livros_por_tipo_espaco_in(tipo_espaco: str, negar: bool = False) -> list[dict]` | Lista livros cujas estantes pertencem (`IN`) ou não pertencem (`NOT IN`) a um tipo de espaço. | Subconsulta de pertinência a conjunto: `IN` / `NOT IN` (Cap. 3). | `transacao()` com Prepared Statement `(tipo_espaco,)`. |
| `espacos_com_estantes_exists(negar: bool = False) -> list[dict]` | Lista espaços que possuem (`EXISTS`) ou não possuem (`NOT EXISTS`) estantes vinculadas. | Subconsulta Correlacionada: `EXISTS` / `NOT EXISTS` (Cap. 3). | `transacao()` com rollback em erro. |
| `analise_acervo_critico(genero_alvo: str, genero_comparacao: str) -> list[dict]` | Combina CTE `WITH`, tabela derivada no `FROM`, `IN`, quantificador `> SOME` e `EXISTS`. | CTE (`WITH`), Subconsulta no `FROM`, `IN`, `SOME`, `EXISTS` (Cap. 3). | `transacao()` com Prepared Statement `(genero_alvo, genero_comparacao)`. |
| `uniao_dominios_estantes() -> list[dict]` | Une domínios do lado 1 e lado 2 das estantes removendo duplicatas. | Operação de Conjunto: `UNION` (Cap. 3). | `transacao()` com rollback em erro. |
| `relatorio_autores_multigenero(genero1: str, genero2: str) -> list[dict]` | Identifica autores que possuem obras simultaneamente em `genero1` e `genero2`. | Operação de Conjunto: `INTERSECT` (Cap. 3). | `transacao()` com Prepared Statement `(genero1, genero2)`. |
| `auditoria_estantes_vazias() -> list[dict]` | Lista estantes sem nenhum livro associado via subtração de conjuntos. | Operação de Conjunto: `EXCEPT` (Cap. 3). | `transacao()` com rollback em erro. |
| `estatisticas_agregadas_gerais() -> dict` | Calcula `COUNT(*)`, `COUNT(codigo_patrimonio)`, `COUNT(DISTINCT status_conservacao)`, `SUM`, `AVG`, `MIN` e `MAX`. | Funções de Agregação e tratamento de nulos em `COUNT` (Cap. 3). | `transacao()` com rollback em erro. |
| `agrupamento_simples_por_status() -> list[dict]` | Agrupa livros por `status_conservacao`, somando títulos e exemplares. | Agrupamento Simples (`GROUP BY`), `COUNT`, `SUM` (Cap. 3). | `transacao()` com rollback em erro. |
| `agrupamento_where_e_having(emprestavel: bool = True, min_titulos: int = 2, min_exemplares_grupo: int = 10) -> list[dict]` | Filtra linhas antes do agrupamento (`WHERE`) e grupos consolidados após (`HAVING`). | Diferença `WHERE` vs `HAVING`, `GROUP BY` (Cap. 3). | `transacao()` com Prepared Statement. |
| `comparar_union_vs_union_all() -> dict` | Executa `UNION` (sem duplicatas) e `UNION ALL` (com duplicatas) entre gêneros e domínios. | União de Conjuntos vs Multiconjuntos: `UNION` / `UNION ALL` (Cap. 3). | `transacao()` com rollback em erro. |
| `comparar_intersect_vs_intersect_all(status1: str = "Novo", status2: str = "Bom") -> dict` | Compara `INTERSECT` vs `INTERSECT ALL` sobre categorias presentes em ambos os status. | Interseção de Conjuntos vs Multiconjuntos: `INTERSECT` / `INTERSECT ALL` (Cap. 3). | `transacao()` com Prepared Statements. |
| `comparar_except_vs_except_all(status_excluir: str = "Danificado") -> dict` | Subtrai categorias com livros no `status_excluir`, comparando `EXCEPT` vs `EXCEPT ALL`. | Diferença de Conjuntos vs Multiconjuntos: `EXCEPT` / `EXCEPT ALL` (Cap. 3). | `transacao()` com Prepared Statements. |
| `testar_parte3_completa() -> list[dict]` | Bateria automatizada para todos os 6 itens da Parte 3 (Agregações + Conjuntos). | Agregações, `GROUP BY`/`HAVING` e Operações de Conjunto (Cap. 3). | Somente leitura via `transacao()`. |

---

### Seção 4 — Subconsultas Avançadas, CTEs, Junções, Visões e Programação no Banco (Cap. 3, 4 e 5)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `subconsulta_some_e_all(genero: str = "Tecnologia e Informática") -> dict` | Compara livros com exemplares `> SOME` (maior que pelo menos um) e `> ALL` (maior que todos) de um gênero. | Comparação com Conjuntos: `> SOME` / `> ANY` vs `> ALL` (Cap. 3). | `transacao()` com Prepared Statements. |
| `subconsulta_ausencia_duplicatas_unique() -> list[dict]` | Retorna livros de autores sem duplicidade no acervo (no máximo 1 obra), simulando o predicado `UNIQUE(SELECT ...)` no PostgreSQL. | Teste de Ausência de Duplicatas (`UNIQUE` em subconsulta via `NOT EXISTS` + `HAVING COUNT(*) > 1`) (Cap. 3). | `transacao()` com rollback em erro. |
| `subconsulta_escalar_no_select() -> list[dict]` | Projeta na lista `SELECT` uma subconsulta escalar (1×1) com a média global do acervo ao lado de cada livro. | Subconsulta Escalar na cláusula `SELECT` (Cap. 3). | `transacao()` com rollback em erro. |
| `subconsulta_no_from_media_categoria(media_minima: float = 5.0) -> list[dict]` | Calcula médias por categoria em uma tabela derivada no `FROM` e filtra externamente no `WHERE`. | Subconsulta no `FROM` (Tabela Derivada) (Cap. 3). | `transacao()` com Prepared Statement. |
| `cte_with_resumo_acervo(min_exemplares: int = 10) -> list[dict]` | Isola obras em destaque (`>= min_exemplares`) utilizando uma CTE nomeada (`WITH Acervo_Destaque AS (...)`). | Expressão de Tabela Comum (`WITH` / CTE) (Cap. 3). | `transacao()` com Prepared Statement. |
| `classificacao_case_when_e_dml_subconsulta() -> dict` | Classifica estoque com `CASE WHEN` e executa `INSERT INTO ... SELECT` seguido de `DELETE ... WHERE id_tag IN (SELECT ...)`. | Expressão Condicional `CASE WHEN` e DML com Subconsulta (`INSERT`/`DELETE ... SELECT`) (Cap. 3). | Conexão manual com `conn.rollback()` obrigatório no `finally` (não persiste tags de teste). |
| `testar_parte4_completa() -> list[dict]` | Bateria automatizada para todos os 8 itens da Parte 4 (Subconsultas, CTEs e `CASE WHEN`/DML). | Subconsultas e CTEs completas (Cap. 3). | Seguro: o item 8 faz rollback automático; demais são leitura. |
| `relatorio_estatisticas_genero(media_minima: float) -> list[dict]` | Agrupa livros por gênero exibindo `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` com filtro `HAVING AVG(...) > ?`. | Agregações, `GROUP BY`, `HAVING` (Cap. 3). | `transacao()` com Prepared Statement. |
| `executar_join(codigo: str) -> list[dict]` | Executa uma das cinco junções do dicionário `SQL_JOINS`: `'natural'`, `'inner'`, `'left'`, `'right'`, `'full'`. | `NATURAL JOIN`, `INNER JOIN ... ON`, `LEFT`/`RIGHT`/`FULL OUTER JOIN` (Cap. 4). | Valida `codigo` via whitelist (`SQL_JOINS`); lança `ValueError` se inválido. |
| `consultar_visao_localizacao_completa() -> list[dict]` | Lê a visão convencional `biblioteca.vw_livros_localizacao_completa` (integra 7 tabelas). | Visão Tradicional (`VIEW`) (Cap. 4). | `transacao()` com rollback em erro. |
| `consultar_visao_materializada(nome_mv: str = "mv_ranking_autores_maior_acervo") -> list[dict]` | Lê dados pré-computados de uma das 4 MVs permitidas em `MVS_PERMITIDAS`. | Visão Materializada (`MATERIALIZED VIEW`) (Cap. 4). | Valida `nome_mv` contra whitelist `MVS_PERMITIDAS` (previne SQL Injection); lança `ValueError` se não autorizada. |
| `atualizar_visao_materializada(nome_mv: str = "mv_ranking_autores_maior_acervo") -> bool` | Sincroniza os dados pré-computados executando `REFRESH MATERIALIZED VIEW`. | `REFRESH MATERIALIZED VIEW` (Cap. 4). | Valida whitelist `MVS_PERMITIDAS` e executa via `transacao()`. |
| `consultar_total_por_autor(autor: str) -> dict` | Invoca a Stored Function escalar `fn_contar_livros_por_autor(?)` e lista as obras correspondentes. | Stored Function Escalar (`CREATE FUNCTION`) (Cap. 5). | `transacao()` com Prepared Statements. |
| `cadastrar_livro_via_procedure(nome, autor, genero, numero_de_exemplares, pode_ser_emprestado, id_estante) -> None` | Valida capacidade da estante e invoca `CALL sp_cadastrar_livro(...)`. | Stored Procedure (`CREATE PROCEDURE` / `CALL`) (Cap. 5). | `transacao()`: rollback automático se capacidade exceder ou ocorrer erro no PostgreSQL. |
| `consultar_auditoria_trigger() -> list[dict]` | Consulta os últimos 10 registros gravados em `biblioteca.auditoria_livros_excluidos`. | Gatilho (`TRIGGER AFTER DELETE`) e tabela de auditoria (Cap. 5). | `transacao()` com rollback em erro. |
| `consulta_recursiva_pisos() -> list[dict]` | Percorre hierarquicamente os pisos cadastrados com cláusula `WITH RECURSIVE` (âncora + passo recursivo). | Consulta Recursiva (`WITH RECURSIVE`) (Cap. 5). | `transacao()` com limite de recursão (`nivel < 10`). |

---

### Seção 5 — Junções (`USING`), Visões Dinâmicas, Índices, DCL e Metadados ODBC (Cap. 4 e 5)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `juncao_com_using(min_exemplares: int = 1) -> list[dict]` | Une `livros` e `estantes` especificando a coluna comum por `INNER JOIN ... USING (id_estante)`. | Junção Interna com cláusula `USING` (Cap. 4). | `transacao()` com Prepared Statement. |
| `consultar_visoes_convencionais_e_dinamismo() -> dict` | Consome `vw_livros_localizacao_completa` e `vw_resumo_estantes_dominio`, insere um livro temporário e comprova recálculo dinâmico imediato da `VIEW` sem `REFRESH`. | Visão Convencional (`VIEW`) e Recálculo Dinâmico (Cap. 4). | Conexão manual com `conn.rollback()` obrigatório no `finally`. |
| `inspecionar_indices_schema(schema: str = "biblioteca") -> list[dict]` | Lista índices explícitos e de restrições consultando o catálogo `pg_indexes`. | Índices (`CREATE INDEX`) e Catálogo do SGBD `pg_indexes` (Cap. 4 e 14). | `transacao()` com Prepared Statement `(schema,)`. |
| `demonstrar_dcl_grant_revoke(role_temp: str = "leitor_teste_avaliacao") -> dict` | Executa o ciclo completo de controle de acesso: `CREATE ROLE`, `GRANT USAGE/SELECT`, verificação com `has_table_privilege()`, `REVOKE` e `DROP ROLE`. | DCL — Autorização e Controle de Acesso (`CREATE ROLE`, `GRANT`, `REVOKE`, `DROP ROLE`) (Cap. 4). | Conexão manual com `conn.rollback()` obrigatório no `finally` (zero resíduo de roles). |
| `testar_parte5_completa() -> list[dict]` | Bateria automatizada para todos os 7 itens da Parte 5 (Junções, Visões, Índices e DCL). | Junções, Visões, Índices e DCL completos (Cap. 4). | Isolamento seguro: testes de mutação (VIEW dinâmica e DCL) fazem rollback automático. |
| `inspecionar_tabelas_schema(schema: str = "biblioteca") -> list[dict]` | Lista tabelas e visões do schema usando o catálogo nativo ODBC `cursor.tables()`. | Metadados Dinâmicos ODBC (`cursor.tables()`) (Cap. 5). | `transacao()` com rollback em erro. |
| `inspecionar_colunas_tabela(tabela: str, schema: str = "biblioteca") -> list[dict]` | Lista colunas, tipos, tamanhos e nulabilidade de uma tabela via `cursor.columns()`. | Metadados Dinâmicos ODBC (`cursor.columns()`) (Cap. 5). | `transacao()` com rollback em erro. |

---

### Seção 6 — Programação Avançada no Banco, Triggers `BEFORE`/`AFTER`, OLAP e Bateria Parte 6 (Cap. 5)

| Função e Assinatura | Regra de Negócio | Conceito Teórico (Silberschatz) | Tratamento de Erros / Rollback |
| :--- | :--- | :--- | :--- |
| `chamar_table_function_por_genero(genero: str = "Romance Clássico") -> list[dict]` | Invoca a Table Function `biblioteca.fn_listar_livros_por_genero(?)` via `SELECT * FROM ...`. | Table Function (`CREATE FUNCTION ... RETURNS TABLE`) (Cap. 5). | `transacao()` com Prepared Statement. |
| `demonstrar_triggers_before_e_after() -> dict` | Comprova (1) Trigger `BEFORE` ajustando `NEW.nome` e `NEW.codigo_patrimonio` para maiúsculas/trim, (2) Trigger `AFTER DELETE` auditando `OLD` em `auditoria_livros_excluidos`, e (3) Trigger `BEFORE` bloqueando título vazio/espaços. | Gatilhos `BEFORE` (variável `NEW`) e `AFTER` (variável `OLD`) (Cap. 5). | Conexão manual; captura `pyodbc.Error` no bloqueio de título vazio e garante `conn.rollback()` no `finally`. |
| `olap_window_functions_ranking() -> list[dict]` | Ranqueia obras por gênero e calcula soma acumulada por partição usando `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()` e `SUM(...) OVER (PARTITION BY ...)`. | OLAP e Funções de Janela (`WINDOW FUNCTIONS`, `OVER`, `PARTITION BY`) (Cap. 5). | `transacao()` com rollback em erro. |
| `olap_agregacao_rollup_cube() -> dict` | Gera subtotais hierárquicos e total geral em uma única consulta com `GROUP BY ROLLUP (genero, status_conservacao)` e combinações completas com `GROUP BY CUBE (...)`. | OLAP — Agregações Multidimensionais (`ROLLUP` e `CUBE`) (Cap. 5). | `transacao()` com rollback em erro. |
| `testar_parte6_completa() -> list[dict]` | Bateria automatizada para todos os 6 itens da Parte 6 (Functions escalar/tabular, `CALL` procedure, Triggers `BEFORE`/`AFTER`, `WITH RECURSIVE`, OLAP/Window/`ROLLUP`/`CUBE` e Metadados ODBC). | Programação no Banco, Triggers, Recursão, OLAP e ODBC (Cap. 5). | Testes com escrita (`CALL sp_cadastrar_livro` e Triggers) executam em transação isolada com `conn.rollback()` obrigatório no `finally`. |

---

## 5. Mapeamento da Checklist Teórica (Os 43 Itens da Avaliação)

A tabela abaixo mapeia exatamente os **43 itens avaliativos** (divididos em 6 partes) às funções implementadas em `biblioteca.py` e aos caminhos exatos de teste no menu interativo do console (`app.py`).

### Parte 1 — DDL & Integridade (8 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **1.1** | Chave Primária Simples (`PRIMARY KEY`) — inserção válida e bloqueio de duplicata | `testar_parte1_completa()` (`_t1_pk_simples`) | `1 -> 5` (Bateria Parte 1) |
| **1.2** | Chave Primária Composta (`PRIMARY KEY (id_livro, id_tag)` em `livro_tag`) | `testar_parte1_completa()` (`_t2_pk_composta`) | `1 -> 5` (Bateria Parte 1) |
| **1.3** | Chave Estrangeira (`FOREIGN KEY`) — bloqueio de pai inexistente | `testar_parte1_completa()` (`_t3_fk_pai_inexistente`) e `cadastrar_livro()` | `1 -> 5` (Bateria Parte 1) ou `1 -> 2` (ID estante inválido) |
| **1.4** | Ações Referenciais (`ON DELETE CASCADE`, `SET NULL` e `RESTRICT`) | `testar_parte1_completa()` (`_t4_acoes_referenciais`), `excluir_estante()`, `excluir_editora()` | `1 -> 5` (Bateria Parte 1) ou `1 -> 8` (`CASCADE` em estantes) |
| **1.5** | Restrição de Unicidade (`UNIQUE` em `codigo_patrimonio`) | `testar_parte1_completa()` (`_t5_unique`) e `cadastrar_livro()` | `1 -> 5` (Bateria Parte 1) ou `1 -> 2` (patrimônio repetido) |
| **1.6** | Restrição de Não-Nulo (`NOT NULL` em `livros.nome`) | `testar_parte1_completa()` (`_t6_not_null`) | `1 -> 5` (Bateria Parte 1) |
| **1.7** | Restrições `CHECK` (faixa numérica `>= 0` e lista discreta `IN`) | `testar_parte1_completa()` (`_t7_check`) | `1 -> 5` (Bateria Parte 1) |
| **1.8** | Valores Padrão (`DEFAULT`) e evolução de esquema (`ALTER TABLE` + `cursor.columns()`) | `testar_parte1_completa()` (`_t8_default_e_alter`) e `validar_colunas_ddl_alter_table()` | `1 -> 5` (Bateria Parte 1) ou `5 -> 2` (Inspecionar colunas) |

---

### Parte 2 — Álgebra Relacional & DML (8 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **2.1** | Projeção ($\Pi$) com `DISTINCT` vs `ALL` e Atributo Calculado | `projecao_distinct_all_e_calculo()`, `listar_autores_unicos()`, `listar_autores_todos()` | `2 -> 1` ou `2 -> 8` (Bateria Parte 2) |
| **2.2** | Seleção ($\sigma$) com predicados compostos (`AND`/`OR`/`NOT`) e comparação de tupla | `selecao_predicados_compostos_e_tupla()` | `2 -> 2` ou `2 -> 8` (Bateria Parte 2) |
| **2.3** | Produto Cartesiano ($\|R\| \times \|S\|$) e Junção Teta ($\bowtie_\theta$) | `produto_cartesiano_e_juncao_teta()` | `2 -> 3` ou `2 -> 8` (Bateria Parte 2) |
| **2.4** | Renomeação ($\rho$ / `AS`) e Auto-junção (`SELF JOIN`) com aliases | `auto_juncao_livros_mesmo_autor_genero()` | `2 -> 4` ou `2 -> 8` (Bateria Parte 2) |
| **2.5** | Operações em Strings: `LIKE` (`%` e `_`), concatenação `\|\|`, `UPPER()` e `LOWER()` | `buscar_strings_like_coringa_posicao()` e `buscar_catalogo_palavra_chave()` | `2 -> 5` ou `2 -> 8` (Bateria Parte 2) |
| **2.6** | Predicado de faixa: `BETWEEN` e `NOT BETWEEN` | `buscar_livros_por_faixa_exemplares()` | `2 -> 6` ou `2 -> 8` (Bateria Parte 2) |
| **2.7** | Valores Nulos e lógica trivalente: `IS NULL` e `IS NOT NULL` | `consultar_nulos_e_nao_nulos()` e `listar_estantes_sem_dominio_lado2()` | `2 -> 7` ou `2 -> 8` (Bateria Parte 2) |
| **2.8** | Ordenação multiatributo (`ORDER BY ASC/DESC`) com `NULLS FIRST` / `NULLS LAST` | `ordenar_livros_multiatributo_nulos()` | `2 -> 7` ou `2 -> 8` (Bateria Parte 2) |

---

### Parte 3 — Agrupamento & Operações de Conjunto (6 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **3.1** | Agregações (`COUNT(*)`, `COUNT(col)` ignorando nulos, `COUNT(DISTINCT)`, `SUM`, `AVG`, `MIN`, `MAX`) | `estatisticas_agregadas_gerais()` | `3 -> 8` (Bateria Parte 3) |
| **3.2** | Agrupamento Simples (`GROUP BY`) | `agrupamento_simples_por_status()` | `3 -> 8` (Bateria Parte 3) |
| **3.3** | Filtro pré e pós-agrupamento: `WHERE` vs `HAVING` | `agrupamento_where_e_having()` e `relatorio_estatisticas_genero()` | `3 -> 8` (Bateria Parte 3) ou `4 -> 1` |
| **3.4** | União de Conjuntos: `UNION` vs `UNION ALL` | `comparar_union_vs_union_all()` e `uniao_dominios_estantes()` | `3 -> 5` ou `3 -> 8` (Bateria Parte 3) |
| **3.5** | Interseção de Conjuntos: `INTERSECT` vs `INTERSECT ALL` | `comparar_intersect_vs_intersect_all()` e `relatorio_autores_multigenero()` | `3 -> 6` ou `3 -> 8` (Bateria Parte 3) |
| **3.6** | Diferença de Conjuntos: `EXCEPT` vs `EXCEPT ALL` | `comparar_except_vs_except_all()` e `auditoria_estantes_vazias()` | `3 -> 7` ou `3 -> 8` (Bateria Parte 3) |

---

### Parte 4 — Subconsultas & CTEs (8 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **4.1** | Subconsulta de pertinência a conjunto (`IN` / `NOT IN`) | `livros_por_tipo_espaco_in()` | `3 -> 2` ou `4 -> 9` (Bateria Parte 4) |
| **4.2** | Comparação com conjuntos (`> SOME` vs `> ALL`) | `subconsulta_some_e_all()` e `analise_acervo_critico()` | `3 -> 4` ou `4 -> 9` (Bateria Parte 4) |
| **4.3** | Subconsulta correlacionada (`EXISTS` / `NOT EXISTS`) | `espacos_com_estantes_exists()` | `3 -> 3` ou `4 -> 9` (Bateria Parte 4) |
| **4.4** | Ausência de duplicatas (`UNIQUE` em subconsulta) | `subconsulta_ausencia_duplicatas_unique()` | `4 -> 9` (Bateria Parte 4) |
| **4.5** | Subconsulta escalar na cláusula `SELECT` | `subconsulta_escalar_no_select()` e `livros_acima_da_media_escalar()` | `3 -> 1` ou `4 -> 9` (Bateria Parte 4) |
| **4.6** | Subconsulta na cláusula `FROM` (Tabela Derivada) | `subconsulta_no_from_media_categoria()` | `4 -> 9` (Bateria Parte 4) |
| **4.7** | Expressão de Tabela Comum (CTE com cláusula `WITH`) | `cte_with_resumo_acervo()` e `analise_acervo_critico()` | `3 -> 4` ou `4 -> 9` (Bateria Parte 4) |
| **4.8** | Expressão `CASE WHEN` e DML com subconsulta (`INSERT/DELETE ... SELECT`) | `classificacao_case_when_e_dml_subconsulta()` | `4 -> 9` (Bateria Parte 4) |

---

### Parte 5 — Junções, Visões, Índices & DCL (7 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **5.1** | Junções Naturais e Internas (`NATURAL JOIN`, `INNER JOIN ... ON`, `USING`) | `executar_join("natural")`, `executar_join("inner")`, `juncao_com_using()` | `4 -> 2` (`natural`/`inner`) ou `5 -> 5` (Bateria Parte 5) |
| **5.2** | Junções Externas Parciais (`LEFT OUTER JOIN` e `RIGHT OUTER JOIN`) | `executar_join("left")`, `executar_join("right")` | `4 -> 2` (`left`/`right`) ou `5 -> 5` (Bateria Parte 5) |
| **5.3** | Junção Externa Completa (`FULL OUTER JOIN`) | `executar_join("full")` | `4 -> 2` (`full`) ou `5 -> 5` (Bateria Parte 5) |
| **5.4** | Visões Convencionais (`VIEW`) e comprovação de recálculo dinâmico sem `REFRESH` | `consultar_visoes_convencionais_e_dinamismo()`, `consultar_visao_localizacao_completa()` | `4 -> 3` ou `5 -> 5` (Bateria Parte 5) |
| **5.5** | Visões Materializadas (`MATERIALIZED VIEW`) e `REFRESH MATERIALIZED VIEW` | `consultar_visao_materializada()`, `atualizar_visao_materializada()` | `4 -> 4` ou `5 -> 5` (Bateria Parte 5) |
| **5.6** | Inspeção de Índices (`CREATE INDEX`) via catálogo `pg_indexes` | `inspecionar_indices_schema()` | `5 -> 3` ou `5 -> 5` (Bateria Parte 5) |
| **5.7** | Ciclo completo DCL (`CREATE ROLE`, `GRANT`, `REVOKE`, `DROP ROLE` com rollback) | `demonstrar_dcl_grant_revoke()` | `5 -> 4` ou `5 -> 5` (Bateria Parte 5) |

---

### Parte 6 — Programação no Banco, Triggers, OLAP & ODBC (6 itens)

| Parte / Item | Conceito Teórico (Silberschatz) | Função Correspondente em `biblioteca.py` | Como Testar no Menu (`app.py`) |
| :--- | :--- | :--- | :--- |
| **6.1** | Stored Function Escalar e Table Function (`RETURNS TABLE`) | `consultar_total_por_autor()`, `chamar_table_function_por_genero()` | `4 -> 5` ou `5 -> 6` (Bateria Parte 6) |
| **6.2** | Stored Procedure invocada via `CALL` | `cadastrar_livro_via_procedure()` e `testar_parte6_completa()` | `4 -> 6` ou `5 -> 6` (Bateria Parte 6) |
| **6.3** | Triggers `BEFORE` (ajustando `NEW` / validando) e `AFTER` (auditando `OLD`) | `demonstrar_triggers_before_e_after()`, `consultar_auditoria_trigger()` | `4 -> 7` ou `5 -> 6` (Bateria Parte 6) |
| **6.4** | Consulta Recursiva (`WITH RECURSIVE`) | `consulta_recursiva_pisos()` | `4 -> 8` ou `5 -> 6` (Bateria Parte 6) |
| **6.5** | OLAP: Funções de Janela (`RANK`, `DENSE_RANK`, `ROW_NUMBER`, `SUM OVER`) e `ROLLUP`/`CUBE` | `olap_window_functions_ranking()`, `olap_agregacao_rollup_cube()` | `5 -> 6` (Bateria Parte 6) |
| **6.6** | Inspeção de Metadados Dinâmicos ODBC (`cursor.tables()` e `cursor.columns()`) | `inspecionar_tabelas_schema()`, `inspecionar_colunas_tabela()` | `5 -> 1`, `5 -> 2` ou `5 -> 6` (Bateria Parte 6) |

> **Total verificado:** $8 + 8 + 6 + 8 + 7 + 6 = \mathbf{43\text{ itens}}$ 100% implementados e automatizados.

---

## 6. Guia Prático de Execução e Testes

### 6.1. Iniciar o Menu Interativo no Terminal

Na raiz do projeto, execute:

```powershell
python app.py
```

O menu principal exibirá as 5 seções operacionais (`1` a `5`, e `0` para sair).

### 6.2. Iniciar a Interface Web e API REST

Para subir o servidor HTTP integrado e acessar a interface visual no navegador:

```powershell
python app.py --web
```

Acesse: **`http://127.0.0.1:8000`** *(para usar outra porta, informe-a como argumento, ex.: `python app.py --web 8080`)*.  
Para encerrar o servidor com segurança, pressione `Ctrl + C`.

### 6.3. Atalhos Rápidos — Baterias Automáticas da Avaliação (43/43 Itens)

Durante a apresentação ao professor, é possível validar todas as 6 partes da checklist diretamente pelo menu de console (`python app.py`) usando os atalhos abaixo. Todos os testes destrutivos ou de mutação operam com **`ROLLBACK` garantido**, mantendo o banco limpo:

| Parte da Checklist | Quantidade de Itens | Atalho no Menu (`app.py`) | Função Executada em `biblioteca.py` |
| :--- | :---: | :---: | :--- |
| **Parte 1** — DDL & Integridade | 8 itens | `1 -> 5` | `testar_parte1_completa()` |
| **Parte 2** — Álgebra Relacional & DML | 8 itens | `2 -> 8` | `testar_parte2_completa()` |
| **Parte 3** — Agrupamento & Conjuntos | 6 itens | `3 -> 8` | `testar_parte3_completa()` |
| **Parte 4** — Subconsultas & CTEs | 8 itens | `4 -> 9` | `testar_parte4_completa()` |
| **Parte 5** — Junções, Visões, Índices & DCL | 7 itens | `5 -> 5` | `testar_parte5_completa()` |
| **Parte 6** — Functions, Procedures, Triggers, OLAP & ODBC | 6 itens | `5 -> 6` | `testar_parte6_completa()` |

> **Dica de Consulta Rápida no Código:** Abra `biblioteca.py` e pressione `Ctrl + F` pesquisando por `[CONCEITO]` ou `[CAPÍTULO]` para navegar instantaneamente até qualquer conceito solicitado durante a arguição.
