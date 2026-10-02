# Documentação do Trabalho Prático Avaliativo Semestral: Visões e Visões Materializadas em Banco de Dados SQL

---

## 📌 Visão Geral do Projeto

Este projeto consiste na modelagem e consolidação de um banco de dados relacional para um **Sistema de Gestão de Acervo, Vendas e Clientes de uma Livraria**, desenvolvido para o SGBD **PostgreSQL**.

O trabalho contempla:
1. **Estrutura de Tabelas (Schema completo)** com chaves primárias, estrangeiras e restrições.
2. **Carga Inicial de Dados de Teste** cobrindo múltiplos cenários reais.
3. **10 Visões Tradicionais (`CREATE VIEW`)** construídas utilizando **Junções Internas (INNER JOIN)** e **Junções Externas (LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN)**.
4. **10 Visões Materializadas (`CREATE MATERIALIZED VIEW`)** utilizando métricas agregadas e junções avançadas.
5. **Mecanismos de Atualização (`REFRESH MATERIALIZED VIEW`)** e instruções passo a passo para consolidação pelo docente.

---

## 🛠️ Estrutura de Pastas e Como Executar

O projeto está dividido rigorosamente em **duas pastas distintas**, atendendo a cada uma das atividades:

📁 **`atividade_1_banco/`** (Construção e Carga do Banco de Dados)
- `01_criacao_banco.sql`: Criação do esquema `biblioteca`.
- `02_criacao_tabelas.sql`: Criação das 12 tabelas com atributos, PRIMARY KEY, FOREIGN KEY e restrições.
- `03_insercoes.sql`: Povoamento de dados de exemplo em todas as tabelas.
- `banco_biblioteca.sql`: Arquivo único consolidado contendo toda a Atividade 1 em ordem sequencial.

📁 **`atividade_2_views/`** (10 Views + 10 Materialized Views com JOINs)
- `04_views.sql`: Contém as 10 Visões Tradicionais (`CREATE VIEW`) + 10 Visões Materializadas (`CREATE MATERIALIZED VIEW`).

---

## 🚀 Instruções de Execução

### Opção 1: Execução via Cliente SQL (DBeaver, pgAdmin, VS Code ou psql)
1. Execute primeiro os scripts da **Atividade 1**:
   ```bash
   psql -U postgres -d biblioteca -f atividade_1_banco/banco_biblioteca.sql
   ```
   *(ou execute individualmente `01_criacao_banco.sql` → `02_criacao_tabelas.sql` → `03_insercoes.sql`)*

2. Em seguida, execute o script da **Atividade 2**:
   ```bash
   psql -U postgres -d biblioteca -f atividade_2_views/04_views.sql
   ```

### Opção 2: Execução Automatizada via Python
Certifique-se de configurar o `.env` e execute:
```bash
python aplicar_scripts_docente.py
```

---

## 📊 Relação das 10 Visões (Views Tradicionais)

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

## ⚡ Relação das 10 Visões Materializadas (`MATERIALIZED VIEWS`)

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

## 🔄 Atualização das Visões Materializadas (`REFRESH`)

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

## 🧪 Script de Teste / Verificação das Visões

Para consultar qualquer visão ou visão materializada:

```sql
-- Consultando uma Visão Tradicional
SELECT * FROM vw_livros_detalhados;
SELECT * FROM vw_clientes_sem_pedidos;
SELECT * FROM vw_clientes_enderecos_cidades;

-- Consultando uma Visão Materializada
SELECT * FROM mv_ranking_autores_mais_vendidos;
SELECT * FROM mv_estoque_vs_demanda;
SELECT * FROM mv_perfil_compras_cliente;
```
