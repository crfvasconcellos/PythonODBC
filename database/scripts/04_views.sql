-- ==============================================================================
-- ATIVIDADE 2: 10 VIEWS TRADICIONAIS + 10 MATERIALIZED VIEWS
-- Modelo Físico: Biblioteca, Edificações, Pisos, Espaços, Tipos de Espaço, Estantes e Livros
-- SGBD: PostgreSQL
-- ==============================================================================

SET search_path TO biblioteca, public;

-- Limpeza previa das visões caso existam
DROP MATERIALIZED VIEW IF EXISTS mv_relatorio_completo_hierarquia;
DROP MATERIALIZED VIEW IF EXISTS mv_mapeamento_acervo_biblioteca_diretoria;
DROP MATERIALIZED VIEW IF EXISTS mv_densidade_estantes_por_tipo_espaco;
DROP MATERIALIZED VIEW IF EXISTS mv_ranking_autores_maior_acervo;
DROP MATERIALIZED VIEW IF EXISTS mv_capacidade_pisos_vs_espacos;
DROP MATERIALIZED VIEW IF EXISTS mv_relatorio_acervo_espacos_privados;
DROP MATERIALIZED VIEW IF EXISTS mv_livros_emprestaveis_vs_restritos;
DROP MATERIALIZED VIEW IF EXISTS mv_ocupacao_estantes_livros;
DROP MATERIALIZED VIEW IF EXISTS mv_total_livros_por_genero_e_piso;
DROP MATERIALIZED VIEW IF EXISTS mv_estatisticas_por_edificacao;

-- ==============================================================================
-- PARTE 1: 10 VISÕES TRADICIONAIS (VIEWS)
-- ==============================================================================

-- 1. Localização física completa de cada livro no acervo (INNER JOIN múltiplo)
CREATE OR REPLACE VIEW vw_livros_localizacao_completa AS
SELECT 
    l.id_livro,
    l.nome AS livro,
    l.autor,
    l.genero,
    l.numero_de_exemplares,
    est.id_estante,
    est.dominio_lado_1,
    est.dominio_lado_2,
    est.tipo AS tipo_espaco,
    esp.id_espaco,
    p.id_pisos AS piso,
    ed.endereco,
    b.diretoria
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
INNER JOIN tipos_de_espaco te ON est.tipo = te.tipo
INNER JOIN espacos esp ON est.id_espaco = esp.id_espaco
INNER JOIN pisos p ON esp.id_pisos = p.id_pisos
INNER JOIN edificacoes ed ON p.id_endereco = ed.id_endereco
INNER JOIN biblioteca b ON ed.id_biblioteca = b.id_biblioteca;

-- 2. Espaços cadastrados que ainda não possuem nenhuma estante (LEFT JOIN)
CREATE OR REPLACE VIEW vw_espacos_sem_estantes AS
SELECT 
    esp.id_espaco,
    esp.numero_de_espacos,
    p.id_pisos
FROM espacos esp
INNER JOIN pisos p ON esp.id_pisos = p.id_pisos
LEFT JOIN estantes est ON esp.id_espaco = est.id_espaco
WHERE est.id_estante IS NULL;

-- 3. Livros de consulta local que não podem ser emprestados (INNER JOIN)
CREATE OR REPLACE VIEW vw_livros_nao_emprestaveis AS
SELECT 
    l.id_livro,
    l.nome AS livro,
    l.autor,
    l.genero,
    est.id_estante,
    est.tipo AS tipo_espaco,
    te.eh_privado
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
INNER JOIN tipos_de_espaco te ON est.tipo = te.tipo
WHERE l.pode_ser_emprestado = FALSE;

-- 4. Edificações sem nenhum livro armazenado (LEFT JOIN + INNER JOIN)
CREATE OR REPLACE VIEW vw_edificacoes_sem_livros AS
SELECT 
    ed.id_endereco,
    ed.endereco,
    ed.telefone,
    b.diretoria
FROM edificacoes ed
INNER JOIN biblioteca b ON ed.id_biblioteca = b.id_biblioteca
LEFT JOIN pisos p ON ed.id_endereco = p.id_endereco
LEFT JOIN espacos esp ON p.id_pisos = esp.id_pisos
LEFT JOIN estantes est ON esp.id_espaco = est.id_espaco
LEFT JOIN livros l ON est.id_estante = l.id_estante
WHERE l.id_livro IS NULL;

-- 5. Resumo de estantes e o total de títulos/exemplares em cada uma (INNER JOIN)
CREATE OR REPLACE VIEW vw_resumo_estantes_dominio AS
SELECT 
    est.id_estante,
    est.dominio_lado_1,
    est.dominio_lado_2,
    est.tipo AS tipo_espaco,
    esp.id_espaco,
    COUNT(l.id_livro) AS total_titulos,
    SUM(l.numero_de_exemplares) AS total_exemplares
FROM estantes est
INNER JOIN espacos esp ON est.id_espaco = esp.id_espaco
INNER JOIN livros l ON est.id_estante = l.id_estante
GROUP BY est.id_estante, est.dominio_lado_1, est.dominio_lado_2, est.tipo, esp.id_espaco;

-- 6. Livros armazenados exclusivamente em espaços privados (INNER JOIN)
CREATE OR REPLACE VIEW vw_livros_em_espacos_privados AS
SELECT 
    l.id_livro,
    l.nome AS livro,
    l.autor,
    l.genero,
    est.id_estante,
    est.tipo AS tipo_espaco
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
INNER JOIN tipos_de_espaco te ON est.tipo = te.tipo
WHERE te.eh_privado = TRUE;

-- 7. Capacidade física de pisos por edificação e biblioteca (INNER JOIN)
CREATE OR REPLACE VIEW vw_capacidade_pisos_edificacoes AS
SELECT 
    p.id_pisos,
    p.capacidade_maxima,
    p.numero_de_espacos,
    ed.endereco,
    b.diretoria
FROM pisos p
INNER JOIN edificacoes ed ON p.id_endereco = ed.id_endereco
INNER JOIN biblioteca b ON ed.id_biblioteca = b.id_biblioteca;

-- 8. Distribuição de gêneros literários por edificação (INNER JOIN múltiplo)
CREATE OR REPLACE VIEW vw_generos_livros_por_edificacao AS
SELECT 
    ed.id_endereco,
    ed.endereco,
    l.genero,
    COUNT(l.id_livro) AS quantidade_titulos,
    SUM(l.numero_de_exemplares) AS total_exemplares
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
INNER JOIN espacos esp ON est.id_espaco = esp.id_espaco
INNER JOIN pisos p ON esp.id_pisos = p.id_pisos
INNER JOIN edificacoes ed ON p.id_endereco = ed.id_endereco
GROUP BY ed.id_endereco, ed.endereco, l.genero;

-- 9. Cruzamento de edificações e seus pisos cadastrados (FULL OUTER JOIN)
CREATE OR REPLACE VIEW vw_hierarquia_edificacoes_pisos AS
SELECT 
    ed.id_endereco,
    ed.endereco,
    ed.telefone,
    p.id_pisos,
    p.capacidade_maxima,
    p.numero_de_espacos
FROM edificacoes ed
FULL OUTER JOIN pisos p ON ed.id_endereco = p.id_endereco;

-- 10. Autores com suas obras e total de exemplares (INNER JOIN)
CREATE OR REPLACE VIEW vw_autores_obras_cadastradas AS
SELECT 
    l.autor,
    COUNT(l.id_livro) AS total_obras,
    SUM(l.numero_de_exemplares) AS total_exemplares,
    STRING_AGG(DISTINCT l.genero, ', ') AS generos_publicados
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
GROUP BY l.autor;


-- ==============================================================================
-- PARTE 2: 10 VISÕES MATERIALIZADAS (MATERIALIZED VIEWS)
-- ==============================================================================

-- 1. Consolidação estatística de acervo por edificação (INNER JOIN)
CREATE MATERIALIZED VIEW mv_estatisticas_por_edificacao AS
SELECT 
    ed.id_endereco,
    ed.endereco,
    COUNT(DISTINCT p.id_pisos) AS total_pisos,
    COUNT(DISTINCT esp.id_espaco) AS total_espacos,
    COUNT(DISTINCT est.id_estante) AS total_estantes,
    COALESCE(SUM(l.numero_de_exemplares), 0) AS total_exemplares_livros
FROM edificacoes ed
INNER JOIN pisos p ON ed.id_endereco = p.id_endereco
INNER JOIN espacos esp ON p.id_pisos = esp.id_pisos
INNER JOIN estantes est ON esp.id_espaco = est.id_espaco
INNER JOIN livros l ON est.id_estante = l.id_estante
GROUP BY ed.id_endereco, ed.endereco
WITH DATA;

-- 2. Total de exemplares por gênero literário e piso (INNER JOIN)
CREATE MATERIALIZED VIEW mv_total_livros_por_genero_e_piso AS
SELECT 
    p.id_pisos,
    l.genero,
    COUNT(l.id_livro) AS quantidade_titulos,
    SUM(l.numero_de_exemplares) AS total_exemplares
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
INNER JOIN espacos esp ON est.id_espaco = esp.id_espaco
INNER JOIN pisos p ON esp.id_pisos = p.id_pisos
GROUP BY p.id_pisos, l.genero
WITH DATA;

-- 3. Comparativo de livros registrados na estante vs livros cadastrados (LEFT JOIN)
CREATE MATERIALIZED VIEW mv_ocupacao_estantes_livros AS
SELECT 
    est.id_estante,
    est.dominio_lado_1,
    est.dominio_lado_2,
    est.numero_de_livros AS capacidade_registrada_estante,
    COALESCE(SUM(l.numero_de_exemplares), 0) AS total_exemplares_fisicos
FROM estantes est
LEFT JOIN livros l ON est.id_estante = l.id_estante
GROUP BY est.id_estante, est.dominio_lado_1, est.dominio_lado_2, est.numero_de_livros
WITH DATA;

-- 4. Acervo emprestável vs acervo restrito por tipo de espaço (INNER JOIN)
CREATE MATERIALIZED VIEW mv_livros_emprestaveis_vs_restritos AS
SELECT 
    te.tipo,
    te.eh_privado,
    SUM(CASE WHEN l.pode_ser_emprestado = TRUE THEN l.numero_de_exemplares ELSE 0 END) AS exemplares_emprestaveis,
    SUM(CASE WHEN l.pode_ser_emprestado = FALSE THEN l.numero_de_exemplares ELSE 0 END) AS exemplares_restritos
FROM tipos_de_espaco te
INNER JOIN estantes est ON te.tipo = est.tipo
INNER JOIN livros l ON est.id_estante = l.id_estante
GROUP BY te.tipo, te.eh_privado
WITH DATA;

-- 5. Relatório patrimonial de livros em salas privadas vs públicas (INNER JOIN)
CREATE MATERIALIZED VIEW mv_relatorio_acervo_espacos_privados AS
SELECT 
    te.eh_privado,
    COUNT(DISTINCT est.id_espaco) AS quantidade_espacos,
    COUNT(DISTINCT l.id_livro) AS total_titulos_armazenados,
    SUM(l.numero_de_exemplares) AS total_exemplares_patrimonio
FROM tipos_de_espaco te
INNER JOIN estantes est ON te.tipo = est.tipo
INNER JOIN livros l ON est.id_estante = l.id_estante
GROUP BY te.eh_privado
WITH DATA;

-- 6. Capacidade de vagas em pisos comparada ao número de espaços (INNER JOIN)
CREATE MATERIALIZED VIEW mv_capacidade_pisos_vs_espacos AS
SELECT 
    p.id_pisos,
    ed.endereco,
    p.capacidade_maxima,
    p.numero_de_espacos AS limite_espacos_piso,
    COUNT(esp.id_espaco) AS espacos_cadastrados
FROM pisos p
INNER JOIN edificacoes ed ON p.id_endereco = ed.id_endereco
INNER JOIN espacos esp ON p.id_pisos = esp.id_pisos
GROUP BY p.id_pisos, ed.endereco, p.capacidade_maxima, p.numero_de_espacos
WITH DATA;

-- 7. Ranking dos autores com maior volume de exemplares (INNER JOIN)
CREATE MATERIALIZED VIEW mv_ranking_autores_maior_acervo AS
SELECT 
    l.autor,
    COUNT(DISTINCT l.id_livro) AS quantidade_obras,
    SUM(l.numero_de_exemplares) AS total_exemplares_acervo
FROM livros l
INNER JOIN estantes est ON l.id_estante = est.id_estante
GROUP BY l.autor
ORDER BY total_exemplares_acervo DESC
WITH DATA;

-- 8. Densidade de estantes ocupadas por tipo de espaço (INNER JOIN / LEFT JOIN)
CREATE MATERIALIZED VIEW mv_densidade_estantes_por_tipo_espaco AS
SELECT 
    te.tipo,
    te.numero_maximo_de_estantes,
    COUNT(est.id_estante) AS estantes_instaladas,
    (te.numero_maximo_de_estantes - COUNT(est.id_estante)) AS capacidade_estantes_restante
FROM tipos_de_espaco te
LEFT JOIN estantes est ON te.tipo = est.tipo
GROUP BY te.tipo, te.numero_maximo_de_estantes
WITH DATA;

-- 9. Mapeamento de acervo agregando por diretoria da biblioteca (INNER JOIN)
CREATE MATERIALIZED VIEW mv_mapeamento_acervo_biblioteca_diretoria AS
SELECT 
    b.id_biblioteca,
    b.diretoria,
    b.numero_edificacoes,
    COUNT(DISTINCT ed.id_endereco) AS edificacoes_vinculadas,
    COALESCE(SUM(l.numero_de_exemplares), 0) AS total_exemplares_geridos
FROM biblioteca b
INNER JOIN edificacoes ed ON b.id_biblioteca = ed.id_biblioteca
INNER JOIN pisos p ON ed.id_endereco = p.id_endereco
INNER JOIN espacos esp ON p.id_pisos = esp.id_pisos
INNER JOIN estantes est ON esp.id_espaco = est.id_espaco
INNER JOIN livros l ON est.id_estante = l.id_estante
GROUP BY b.id_biblioteca, b.diretoria, b.numero_edificacoes
WITH DATA;

-- 10. Relatório de hierarquia física completa (FULL OUTER JOIN)
CREATE MATERIALIZED VIEW mv_relatorio_completo_hierarquia AS
SELECT 
    COALESCE(b.diretoria, 'Sem Diretoria') AS diretoria,
    COALESCE(ed.endereco, 'Sem Edificação') AS endereco,
    p.id_pisos AS piso,
    esp.id_espaco AS espaco,
    est.id_estante AS estante,
    l.nome AS livro
FROM biblioteca b
FULL OUTER JOIN edificacoes ed ON b.id_biblioteca = ed.id_biblioteca
FULL OUTER JOIN pisos p ON ed.id_endereco = p.id_endereco
FULL OUTER JOIN espacos esp ON p.id_pisos = esp.id_pisos
FULL OUTER JOIN estantes est ON esp.id_espaco = est.id_espaco
FULL OUTER JOIN livros l ON est.id_estante = l.id_estante
WITH DATA;
