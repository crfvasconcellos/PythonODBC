# Documentação do Trabalho Prático Avaliativo Semestral: Visões, Visões Materializadas e CRUD em Python com ODBC

---

## Visão Geral do Projeto

Este projeto consiste na modelagem, consolidação e manipulação de um banco de dados relacional para um **Sistema de Gestão de Acervo, Vendas e Clientes de uma Livraria**, desenvolvido para o SGBD **PostgreSQL** com integração em **Python (pyodbc)**.

O trabalho contempla:
1. **Estrutura de Tabelas (Schema completo)** com chaves primárias, estrangeiras e restrições.
2. **Carga Inicial de Dados de Teste** cobrindo múltiplos cenários reais.
3. **10 Visões Tradicionais (`CREATE VIEW`)** construídas utilizando **Junções Internas (INNER JOIN)** e **Junções Externas (LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN)**.
4. **10 Visões Materializadas (`CREATE MATERIALIZED VIEW`)** utilizando métricas agregadas e junções avançadas.
5. **Mecanismos de Atualização (`REFRESH MATERIALIZED VIEW`)** e instruções passo a passo para consolidação pelo docente.
6. **Aplicação CRUD em Python** nativo via `pyodbc` para manipulação e consulta do acervo de livros.

---

## Tecnologias Utilizadas

- **SGBD**: PostgreSQL
- **Linguagem**: Python 3
- **Conectividade**: `pyodbc` (Driver ODBC do PostgreSQL)
- **Configuração**: `python-dotenv` (Gerenciamento de variáveis de ambiente via `.env`)

---

## Estrutura de Pastas e Arquivos

```text
PythonDjangoODBC/
├── .env                       # Configurações de conexão do banco de dados
├── main.py                    # Script de CRUD interativo em Python via ODBC
├── aplicar_scripts_docente.py  # Script de execução e verificação automatizada
├── README.md                  # Documentação completa do projeto
│
├── atividade_1_banco/          # (Construção e Carga do Banco de Dados)
│   ├── 01_criacao_banco.sql   # Criação do esquema biblioteca
│   ├── 02_criacao_tabelas.sql # Criação das 12 tabelas com restrições
│   ├── 03_insercoes.sql       # Povoamento de dados de exemplo
│   └── banco_biblioteca.sql   # Script consolidado da Atividade 1
│
└── atividade_2_views/          # (Views + Materialized Views)
    └── 04_views.sql           # 10 Visões Tradicionais + 10 Visões Materializadas
```

---

## Configuração do Ambiente e Conexão

1. Certifique-se de configurar o arquivo `.env` na raiz do projeto com as credenciais do seu banco de dados:

```env
DB_DRIVER=PostgreSQL Unicode(x64)
DB_SERVER=localhost
DB_PORT=5432
DB_DATABASE=biblioteca
DB_USER=postgres
DB_PASSWORD=sua_senha
```

2. Instale as dependências necessárias do Python:

```bash
pip install pyodbc python-dotenv
```

---

## Instruções de Execução

### Opção 1: Execução Automatizada via Python (Docente / Acadêmico)

Para consolidar o banco de dados, aplicar todas as visões e executar a verificação automática de contagem:

```bash
python aplicar_scripts_docente.py
```

Para interagir com o menu CRUD de livros no terminal:

```bash
python main.py
```

### Opção 2: Execução via Cliente SQL (psql, DBeaver, pgAdmin)

1. Execute primeiro os scripts da **Atividade 1**:
   ```bash
   psql -U postgres -d biblioteca -f atividade_1_banco/banco_biblioteca.sql
   ```
   *(ou execute individualmente `01_criacao_banco.sql` → `02_criacao_tabelas.sql` → `03_insercoes.sql`)*

2. Em seguida, execute o script da **Atividade 2**:
   ```bash
   psql -U postgres -d biblioteca -f atividade_2_views/04_views.sql
   ```

---

## Relação das 10 Visões (Views Tradicionais)

| # | Nome da Visão | Tipo de Junção Utilizada | Descrição e Raciocínio de Negócio |
|---|---|---|---|
| 1 | `vw_livros_localizacao_completa` | `INNER JOIN` (Múltiplos) | Exibe a localização física exata do livro (estante, número do espaço, piso, endereço da edificação e diretoria). |
| 2 | `vw_espacos_sem_estantes` | `LEFT JOIN` | Identifica salas ou espaços cadastrados que ainda **não possuem nenhuma estante física** alocada. |
| 3 | `vw_livros_nao_emprestaveis` | `INNER JOIN` | Lista obras reservadas apenas para consulta local (`pode_ser_emprestado = FALSE`) com o tipo de espaço e se é privado. |
| 4 | `vw_edificacoes_sem_livros` | `LEFT JOIN` (Múltiplo) | Mapeia endereços ou edifícios cadastrados no sistema que **não possuem nenhum livro** armazenado. |
| 5 | `vw_resumo_estantes_dominio` | `INNER JOIN` | Resumo analítico de cada estante (domínios dos lados 1 e 2) com total de títulos e exemplares físicos. |
| 6 | `vw_livros_em_espacos_privados` | `INNER JOIN` | Filtra livros armazenados em salas e laboratórios restritos (`eh_privado = TRUE`). |
| 7 | `vw_capacidade_pisos_edificacoes` | `INNER JOIN` | Relatório estrutural de capacidade máxima de pessoas e espaços por piso e edificação. |
| 8 | `vw_generos_livros_por_edificacao` | `INNER JOIN` (Múltiplos) | Quantidade de títulos e exemplares agrupados por gênero literário e por prédio. |
| 9 | `vw_hierarquia_edificacoes_pisos` | `FULL OUTER JOIN` | Cruzamento completo entre o cadastro de edificações e pisos, exibindo locais com ou sem pisos alocados. |
| 10 | `vw_autores_obras_cadastradas` | `INNER JOIN` | Agrupamento de autores com a contagem total de suas obras, número de exemplares e gêneros publicados. |

---

## Relação das 10 Visões Materializadas (`MATERIALIZED VIEWS`)

| # | Nome da Visão Materializada | Tipo de Junção Utilizada | Descrição e Raciocínio de Negócio |
|---|---|---|---|
| 1 | `mv_estatisticas_por_edificacao` | `INNER JOIN` (Múltiplos) | Total consolidado de pisos, espaços, estantes e exemplares de livros por prédio. |
| 2 | `mv_total_livros_por_genero_e_piso` | `INNER JOIN` | Volume pré-calculado de acervo por gênero literário e por andar/piso. |
| 3 | `mv_ocupacao_estantes_livros` | `LEFT JOIN` | Comparativo entre a capacidade informada da estante e a contagem real de exemplares armazenados. |
| 4 | `mv_livros_emprestaveis_vs_restritos` | `INNER JOIN` | Totalização de acervo circulante (para empréstimo) versus acervo restrito agrupado por tipo de espaço. |
| 5 | `mv_relatorio_acervo_espacos_privados` | `INNER JOIN` | Patrimônio total de livros armazenados em ambientes privados vs públicos. |
| 6 | `mv_capacidade_pisos_vs_espacos` | `INNER JOIN` | Medição de ocupação física: capacidade máxima do piso versus espaços efetivamente cadastrados. |
| 7 | `mv_ranking_autores_maior_acervo` | `INNER JOIN` | Ranking dos autores com maior número de exemplares físicos disponíveis nas bibliotecas. |
| 8 | `mv_densidade_estantes_por_tipo_espaco` | `LEFT JOIN` | Medição de utilização dos tipos de espaço (estantes instaladas vs limite máximo permitido). |
| 9 | `mv_mapeamento_acervo_biblioteca_diretoria` | `INNER JOIN` (Múltiplos) | Total de edificações e volume total de livros geridos por cada diretoria da biblioteca. |
| 10 | `mv_relatorio_completo_hierarquia` | `FULL OUTER JOIN` (Múltiplo) | Visão analítica completa em árvore da hierarquia física (Diretoria → Edificação → Piso → Espaço → Estante → Livro). |

---

## Atualização das Visões Materializadas (`REFRESH`)

Para atualizar os dados pré-calculados nas visões materializadas, execute:

```sql
REFRESH MATERIALIZED VIEW mv_estatisticas_por_edificacao;
REFRESH MATERIALIZED VIEW mv_total_livros_por_genero_e_piso;
REFRESH MATERIALIZED VIEW mv_ocupacao_estantes_livros;
REFRESH MATERIALIZED VIEW mv_livros_emprestaveis_vs_restritos;
REFRESH MATERIALIZED VIEW mv_relatorio_acervo_espacos_privados;
REFRESH MATERIALIZED VIEW mv_capacidade_pisos_vs_espacos;
REFRESH MATERIALIZED VIEW mv_ranking_autores_maior_acervo;
REFRESH MATERIALIZED VIEW mv_densidade_estantes_por_tipo_espaco;
REFRESH MATERIALIZED VIEW mv_mapeamento_acervo_biblioteca_diretoria;
REFRESH MATERIALIZED VIEW mv_relatorio_completo_hierarquia;
```

---

## Script de Teste / Verificação das Visões

Para consultar qualquer visão ou visão materializada:

```sql
-- Consultando Visões Tradicionais
SELECT * FROM vw_livros_localizacao_completa;
SELECT * FROM vw_espacos_sem_estantes;
SELECT * FROM vw_autores_obras_cadastradas;

-- Consultando Visões Materializadas
SELECT * FROM mv_estatisticas_por_edificacao;
SELECT * FROM mv_ranking_autores_maior_acervo;
SELECT * FROM mv_relatorio_completo_hierarquia;
```
